import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

import ai


def pdf_bytes(text="A small test document.", pages=1, encrypted=False):
    writer = PdfWriter()
    for _ in range(pages):
        page = writer.add_blank_page(width=300, height=300)
        if text:
            font = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"), NameObject("/BaseFont"): NameObject("/Helvetica")})
            page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
            stream = DecodedStreamObject()
            stream.set_data(f"BT /F1 12 Tf 10 100 Td ({text}) Tj ET".encode())
            page[NameObject("/Contents")] = writer._add_object(stream)
    if encrypted:
        writer.encrypt("test-password")
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def response(content, reason="stop"):
    return {"choices": [{"message": {"content": content}, "finish_reason": reason}]}


class AiTests(unittest.TestCase):
    @patch("ai.urlopen")
    def test_transport_errors_and_key_validation(self, open_url):
        for key in (None, "", "has space", "한글", "key\nsecret"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                ai.request_json(key, "/models/")
        open_url.assert_not_called()
        open_url.return_value.__enter__.return_value = io.BytesIO(b'{"data":[]}')
        self.assertEqual(ai.request_json("test-key", "/models/"), {"data": []})
        for error in (HTTPError("https://example.test", 401, "secret", {}, None), URLError("secret")):
            open_url.side_effect = error
            with self.assertRaises(ValueError) as caught:
                ai.request_json("test-key", "/models/")
            self.assertNotIn("secret", str(caught.exception))

    @patch("ai.request_json")
    def test_models_and_diary(self, request):
        request.return_value = {"data": [{"id": "b"}, {"id": "a"}, {"id": "a"}, None]}
        self.assertEqual(ai.list_models("test-key"), ["a", "b"])
        expected = {"emotion": "뿌듯함", "message": "해낸 일이 자랑스럽겠어요."}
        request.return_value = response("```json\n" + json.dumps(expected) + "\n```")
        self.assertEqual(ai.analyze_diary("test-key", "test-model", "할 일을 끝냈다"), expected)
        ai.analyze_diary("test-key", "test-model", "오늘의 일기", mood="지침")
        self.assertEqual(json.loads(request.call_args.args[2]["messages"][1]["content"])["선택한_기분"], "지침")
        request.reset_mock()
        with self.assertRaises(ValueError):
            ai.analyze_diary("test-key", "test-model", "오늘의 일기", mood="unknown")
        request.assert_not_called()
        for text in (" ", "x" * 2001, None):
            request.reset_mock()
            with self.assertRaises(ValueError):
                ai.analyze_diary("test-key", "test-model", text)
            request.assert_not_called()

    @patch("ai.request_json")
    def test_bad_ai_responses(self, request):
        for data in (None, {}, {"choices": []}, {"choices": [None]}, {"choices": ["bad"]}, response(""), response("{}"), response("null"), response("```"), response('{"emotion":true,"message":"x"}'), response("partial", "length")):
            request.return_value = data
            with self.subTest(data=data), self.assertRaises(ValueError):
                ai.analyze_diary("test-key", "test-model", "오늘의 일기")
        request.reset_mock()
        with self.assertRaises(ValueError):
            ai.analyze_diary("test-key", "", "오늘의 일기")
        request.assert_not_called()

    def test_pdf_extract_and_reject_invalid_files(self):
        text, pages = ai.extract_pdf(pdf_bytes())
        self.assertIn("A small test document.", text)
        self.assertEqual(pages, 1)
        for raw, message in ((b"not pdf", "정상"), (b"%PDF-broken", "읽지"), (pdf_bytes(text=""), "OCR"), (pdf_bytes(encrypted=True), "암호"), (pdf_bytes(pages=101), "100페이지"), (b"x" * (ai.MAX_PDF_BYTES + 1), "10MB")):
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                ai.extract_pdf(raw)
        with patch("ai.MAX_CHARACTERS", 10), self.assertRaisesRegex(ValueError, "60,000"):
            ai.extract_pdf(pdf_bytes())

    @patch("ai.request_json")
    def test_pdf_summary_modes_and_metadata(self, request):
        request.return_value = response("A summary.")
        raw = pdf_bytes()
        prompts = []
        for mode in ("normal", "brief"):
            result = ai.summarize_pdf("test-key", "test-model", raw, mode)
            self.assertEqual(result["summary"], "A summary.")
            self.assertEqual(result["pages"], 1)
            self.assertGreater(result["characters"], 0)
            payload = request.call_args.args[2]
            prompts.append(payload["messages"][0]["content"])
            self.assertIn("A small test document.", payload["messages"][1]["content"])
        self.assertNotEqual(prompts[0], prompts[1])
        request.reset_mock()
        with self.assertRaises(ValueError):
            ai.summarize_pdf("test-key", "test-model", raw, "invalid")
        request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
