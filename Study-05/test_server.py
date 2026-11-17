import base64
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

import server


class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.data = {"api_key": "test-key", "model": "test-model", "consent": True}

    def test_routes_forward_only_the_expected_fields(self):
        with patch("server.ai.list_models", return_value=["test-model"]) as models:
            self.assertEqual(server.dispatch("/api/models", {"api_key": "test-key"}), {"models": ["test-model"]})
            models.assert_called_once_with("test-key")
        with patch("server.ai.analyze_diary", return_value={"emotion": "기쁨", "message": "잘했어요"}) as diary:
            result = server.dispatch("/api/diary", {**self.data, "text": "과제를 마쳤다"})
            self.assertEqual(result["emotion"], "기쁨")
            diary.assert_called_once_with("test-key", "test-model", "과제를 마쳤다", mood="")
            diary.reset_mock()
            server.dispatch("/api/diary", {**self.data, "text": "피곤한 하루", "mood": "지침"})
            diary.assert_called_once_with("test-key", "test-model", "피곤한 하루", mood="지침")
        with patch("server.ai.summarize_pdf", return_value={"summary": "요약"}) as summary:
            result = server.dispatch("/api/pdf-summary", {**self.data, "pdf": base64.b64encode(b"%PDF-test").decode(), "mode": "brief"})
            self.assertEqual(result, {"summary": "요약"})
            summary.assert_called_once_with("test-key", "test-model", b"%PDF-test", "brief")

    def test_consent_must_be_true_before_analysis_or_summary(self):
        with patch("server.ai.analyze_diary") as diary, patch("server.ai.summarize_pdf") as summary:
            for path in ("/api/diary", "/api/pdf-summary"):
                for consent in (None, False, 1, "true"):
                    with self.subTest(path=path, consent=consent), self.assertRaises(ValueError):
                        server.dispatch(path, {**self.data, "consent": consent, "text": "오늘", "pdf": "JVBERg=="})
            diary.assert_not_called()
            summary.assert_not_called()

    def test_invalid_input_types_never_reach_ai(self):
        invalid = [("/api/models", []), ("/api/models", {"api_key": 1})]
        invalid += [("/api/diary", {**self.data, "model": value, "text": "오늘"}) for value in (None, 1, [], "", " ", "x" * 201)]
        invalid += [("/api/diary", {**self.data, "text": value}) for value in (None, 1, [], {})]
        invalid += [("/api/diary", {**self.data, "text": "오늘", "mood": value}) for value in (None, 1, [], "unknown")]
        invalid += [("/api/pdf-summary", {**self.data, "pdf": value}) for value in (None, 1, [], "not base64", "한글")]
        with patch("server.ai.list_models") as models, patch("server.ai.analyze_diary") as diary, patch("server.ai.summarize_pdf") as summary:
            for path, data in invalid:
                with self.subTest(path=path, data=data), self.assertRaises(ValueError):
                    server.dispatch(path, data)
            models.assert_not_called()
            diary.assert_not_called()
            summary.assert_not_called()


class HandlerTests(unittest.TestCase):
    def request(self, method="POST", path="/api/diary", body=b"{}", headers=None):
        handler = object.__new__(server.Handler)
        handler.path = path
        handler.headers = {"Host": f"127.0.0.1:{server.PORT}", "Origin": server.ORIGIN,
                           "Content-Type": "application/json", "Content-Length": str(len(body)), **(headers or {})}
        handler.rfile = io.BytesIO(body)
        handler.reply = Mock()
        getattr(handler, "do_" + method)()
        return handler

    def test_host_and_origin_rejected_before_dispatch(self):
        with patch("server.dispatch") as dispatch:
            for headers in ({"Host": "evil.test:8514"}, {"Host": "localhost:8514"}, {"Origin": "https://evil.test"}, {"Origin": "null"}, {"Origin": ""}):
                with self.subTest(headers=headers):
                    self.assertEqual(self.request(headers=headers).reply.call_args.args[0], 403)
            self.assertEqual(self.request("GET", "/", headers={"Host": "evil.test"}).reply.call_args.args[0], 403)
            dispatch.assert_not_called()

    def test_request_type_size_and_json_validation(self):
        cases = [(415, b"{}", {"Content-Type": "text/plain"}),
                 (413, b"", {}), (413, b"{}", {"Content-Length": "-1"}),
                 (413, b"{}", {"Content-Length": str(server.MAX_BODY + 1)}),
                 (400, b"{}", {"Content-Length": "invalid"}),
                 (400, b"not json", {}), (400, b"\xff", {})]
        with patch("server.dispatch") as dispatch:
            for status, body, headers in cases:
                with self.subTest(status=status, body=body, headers=headers):
                    handler = self.request(body=body, headers=headers)
                    self.assertEqual(handler.reply.call_args.args[0], status)
            dispatch.assert_not_called()

    def test_success_and_errors_do_not_expose_unexpected_exception(self):
        with patch("server.dispatch", return_value={"emotion": "기쁨"}) as dispatch:
            handler = self.request(body=json.dumps({"text": "오늘"}).encode())
            self.assertEqual(handler.reply.call_args.args, (200, {"emotion": "기쁨"}))
            dispatch.assert_called_once_with("/api/diary", {"text": "오늘"})
        with patch("server.dispatch", side_effect=ValueError("동의가 필요합니다.")):
            self.assertEqual(self.request().reply.call_args.args, (400, {"error": "동의가 필요합니다."}))
        with patch("server.dispatch", side_effect=RuntimeError("private-test-data")):
            handler = self.request()
            self.assertEqual(handler.reply.call_args.args[0], 500)
            self.assertNotIn("private-test-data", str(handler.reply.call_args))

    def test_only_allowlisted_static_resources_are_served(self):
        with tempfile.TemporaryDirectory() as directory, patch("server.ROOT", Path(directory)):
            Path(directory, "index.html").write_bytes(b"local app")
            self.assertEqual(self.request("GET", "/").reply.call_args.args, (200, b"local app", "text/html"))
            Path(directory, "assets").mkdir()
            Path(directory, "assets/kiwi-friend.png").write_bytes(b"test image")
            self.assertEqual(self.request("GET", "/assets/kiwi-friend.png").reply.call_args.args, (200, b"test image", "image/png"))
            for path in ("/server.py", "/ai.py", "/.env", "/../index.html", "/index.html?x=1"):
                with self.subTest(path=path):
                    self.assertEqual(self.request("GET", path).reply.call_args.args[0], 404)
            self.assertEqual(self.request("GET", "/index_pdf.html").reply.call_args.args[0], 500)
        with patch("server.dispatch") as dispatch:
            self.assertEqual(self.request(path="/api/unknown").reply.call_args.args[0], 404)
            dispatch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
