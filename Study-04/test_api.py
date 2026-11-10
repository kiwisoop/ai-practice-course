import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from PIL import Image

from api import MAX_BYTES, generate_recipes, list_models, prepare_image, recognize, request_json
from test_storage import RECIPE


class ApiTests(unittest.TestCase):
    def test_photo_validation_and_resize(self):
        output = io.BytesIO()
        Image.new("RGB", (2000, 1000)).save(output, format="PNG")
        photo = prepare_image(output.getvalue())
        with Image.open(io.BytesIO(photo)) as image:
            self.assertEqual(image.size, (1600, 800))
            self.assertEqual(image.format, "JPEG")
        for raw in (b"not an image", b"", b"x" * (MAX_BYTES + 1)):
            with self.subTest(size=len(raw)), self.assertRaises(ValueError):
                prepare_image(raw)

    @patch("api.request_json")
    def test_models_and_recognition(self, request):
        request.return_value = {"data": [{"id": "claude-test"}, {"id": "other"}, {"id": "claude-test"}]}
        self.assertEqual(list_models("test-key"), ["claude-test"])
        self.assertEqual(list_models("test-key", claude_only=False), ["claude-test", "other"])
        request.return_value = {"choices": [{"message": {"content": "확인된 재료\n- 달걀"}, "finish_reason": "stop"}]}
        self.assertIn("달걀", recognize("test-key", "claude-test", b"photo"))
        payload = request.call_args.args[2]
        self.assertEqual(payload["model"], "claude-test")
        self.assertTrue(payload["messages"][1]["content"][1]["image_url"]["url"].startswith("data:image/jpeg;base64,"))
        for response in ({}, None, {"choices": []}, {"choices": [{"message": {"content": ""}}]}):
            request.return_value = response
            with self.subTest(response=response), self.assertRaises(ValueError):
                recognize("test-key", "claude-test", b"photo")
        request.return_value = {"choices": [{"message": {"content": "partial"}, "finish_reason": "length"}]}
        with self.assertRaisesRegex(ValueError, "잘렸"):
            recognize("test-key", "claude-test", b"photo")

    @patch("api.urlopen")
    def test_auth_and_failures(self, open_url):
        with self.assertRaises(ValueError):
            request_json("", "/models/")
        open_url.assert_not_called()
        open_url.return_value.__enter__.return_value = io.BytesIO(json.dumps({"data": []}).encode())
        self.assertEqual(request_json("test-key", "/models/"), {"data": []})
        self.assertEqual(open_url.call_args.args[0].full_url, "https://api.baze.co/v1/gateway/models/")
        self.assertEqual(open_url.call_args.args[0].get_header("Authorization"), "Bearer test-key")
        for status in (401, 403, 429, 500):
            open_url.side_effect = HTTPError("https://example.test", status, "secret body", {}, None)
            with self.subTest(status=status), self.assertRaises(ValueError) as caught:
                request_json("test-key", "/models/")
            self.assertNotIn("secret body", str(caught.exception))
        open_url.side_effect = URLError("offline")
        with self.assertRaisesRegex(ValueError, "연결"):
            request_json("test-key", "/models/")

    @patch("api.request_json")
    def test_recipe_generation_validation_and_preferences(self, request):
        request.return_value = {"choices": [{"message": {"content": json.dumps([RECIPE])}}]}
        recipes = generate_recipes("test-key", "deepseek-test", "달걀", "한식", "쉬움", "땅콩 제외")
        self.assertEqual(recipes[0]["title"], "달걀볶음")
        self.assertIn("땅콩 제외", request.call_args.args[2]["messages"][1]["content"])
        recipes = generate_recipes("test-key", "deepseek-test", "달걀", "한식", "보통", "", max_minutes=20, servings=2, dietary_restrictions=["저염식"])
        options = json.loads(request.call_args.args[2]["messages"][1]["content"])
        self.assertEqual((options["최대_조리_시간_분"], options["인분"], options["식단_제한"]), (20, 2, ["저염식"]))
        self.assertEqual(recipes[0]["servings"], 2)
        request.reset_mock()
        with self.assertRaises(ValueError):
            generate_recipes("test-key", "deepseek-test", " ", "한식", "쉬움", "")
        request.assert_not_called()
        for content in ("not json", "[]", json.dumps([{**RECIPE, "minutes": -1}]), json.dumps([{**RECIPE, "steps": []}])):
            request.return_value = {"choices": [{"message": {"content": content}}]}
            with self.subTest(content=content), self.assertRaises(ValueError):
                generate_recipes("test-key", "deepseek-test", "달걀", "한식", "쉬움", "")
        request.return_value = {"choices": [{"message": {"content": json.dumps([{**RECIPE, "minutes": 35}])}}]}
        with self.assertRaisesRegex(ValueError, "최대 조리 시간"):
            generate_recipes("test-key", "deepseek-test", "달걀", "한식", "보통", "", max_minutes=30)


if __name__ == "__main__":
    unittest.main()
