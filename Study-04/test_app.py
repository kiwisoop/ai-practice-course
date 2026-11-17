from pathlib import Path
import io
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import storage
from api import prepare_image
from test_storage import RECIPE


class AppTests(unittest.TestCase):
    def test_recognition_guidance_tracks_missing_requirements(self):
        with tempfile.TemporaryDirectory() as directory:
            original_database = storage.database
            path = Path(directory) / "test.sqlite3"
            with patch("storage.database", lambda ignored: original_database(path)), \
                    patch("streamlit.file_uploader", return_value=None) as upload, \
                    patch("api.list_models", return_value=["claude-test"]):
                app = AppTest.from_file("app.py", default_timeout=15).run()
                next(b for b in app.button if b.label == "데모 계정").click().run()
                app.session_state["nav"] = "📷 재료 인식"
                app.run()
                guidance = next(c.value for c in app.caption if "시작 전 필요한 항목" in c.value)
                for requirement in ("사진 업로드", "API 키 입력", "사진 인식 모델 선택", "전송 동의"):
                    self.assertIn(requirement, guidance)
                self.assertTrue(next(b for b in app.button if b.label == "🔍 재료 인식 시작").disabled)
                next(t for t in app.text_input if t.label == "새 API 키").input("test-key").run()
                next(b for b in app.button if b.label == "🔌 API 연결 테스트").click().run()
                app.selectbox(key="model").select("claude-test").run()
                guidance = next(c.value for c in app.caption if "시작 전 필요한 항목" in c.value)
                self.assertNotIn("API 키 입력", guidance)
                self.assertNotIn("사진 인식 모델 선택", guidance)
                self.assertIn("전송 동의", guidance)
                upload.return_value = io.BytesIO(Path("assets/fridge-sample.png").read_bytes())
                app.checkbox(key="api_consent").check().run()
                self.assertFalse(any("시작 전 필요한 항목" in c.value for c in app.caption))
                self.assertFalse(next(b for b in app.button if b.label == "🔍 재료 인식 시작").disabled)
                self.assertFalse(app.exception)

    def test_photo_reuses_preview_and_rejects_invalid_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            original_database = storage.database
            path = Path(directory) / "test.sqlite3"
            photo = io.BytesIO(Path("assets/fridge-sample.png").read_bytes())
            with patch("storage.database", lambda ignored: original_database(path)), \
                    patch("streamlit.file_uploader", return_value=photo) as upload, \
                    patch("api.prepare_image", wraps=prepare_image) as prepare:
                app = AppTest.from_file("app.py", default_timeout=15).run()
                next(b for b in app.button if b.label == "데모 계정").click().run()
                app.session_state["nav"] = "📷 재료 인식"
                app.run()
                self.assertIn("photo_preview", app.session_state)
                prepare.assert_called_once()
                app.run()
                prepare.assert_called_once()
                upload.return_value = io.BytesIO(b"invalid image")
                app.run()
                self.assertNotIn("photo_preview", app.session_state)
                self.assertTrue(app.error)
                self.assertTrue(next(b for b in app.button if b.label == "🔍 재료 인식 시작").disabled)
                self.assertFalse(app.exception)

    def test_signup_and_email_login(self):
        with tempfile.TemporaryDirectory() as directory:
            original_database = storage.database
            path = Path(directory) / "test.sqlite3"
            with patch("storage.database", lambda ignored: original_database(path)):
                app = AppTest.from_file("app.py", default_timeout=15).run()
                app.text_input(key="signup_name").input("실습 요리사")
                app.text_input(key="signup_email").input("cook@example.com")
                app.text_input(key="signup_password").input("test-password")
                app.text_input(key="signup_confirmation").input("test-password")
                next(b for b in app.button if b.label == "회원가입").click().run()
                self.assertTrue(app.success)
                app.text_input(key="login_email").input("cook@example.com")
                app.text_input(key="login_password").input("test-password")
                next(b for b in app.button if b.label == "로그인").click().run()
                self.assertEqual(storage.profile(app.session_state["user_id"], path)["name"], "실습 요리사")
                self.assertEqual(app.session_state["nav"], "🏠 대시보드")
                self.assertFalse(app.exception)

    def test_generate_save_cook_delete_and_logout(self):
        with tempfile.TemporaryDirectory() as directory:
            original_database = storage.database
            path = Path(directory) / "test.sqlite3"
            with patch("storage.database", lambda ignored: original_database(path)), \
                    patch("api.list_models", return_value=["claude-test", "deepseek-test"]), \
                    patch("api.generate_recipes", return_value=[RECIPE]):
                app = AppTest.from_file("app.py", default_timeout=15).run()
                self.assertFalse(app.exception)
                next(b for b in app.button if b.label == "데모 계정").click().run()
                self.assertFalse(app.exception)
                self.assertEqual(app.session_state["nav"], "🏠 대시보드")
                next(t for t in app.text_input if t.label == "새 API 키").input("test-key").run()
                next(b for b in app.button if b.label == "🔌 API 연결 테스트").click().run()
                app.selectbox(key="recipe_model").select("deepseek-test").run()
                app.session_state["nav"] = "🍽️ 레시피 생성"
                app.run()
                app.text_area(key="ingredients").input("달걀").run()
                app.checkbox(key="api_consent").check().run()
                next(b for b in app.button if b.label == "🔍 레시피 생성").click().run()
                self.assertFalse(app.exception)
                app.button(key="save_generated_1_0").click().run()
                self.assertEqual(storage.stats("demo1", path)["saved"], 1)
                self.assertEqual(len(app.get("download_button")), 1)
                next(t for t in app.text_input if t.label == "요리명 검색").input("없는 요리").run()
                self.assertFalse(any(b.key == "save_generated_1_0" for b in app.button))
                next(t for t in app.text_input if t.label == "요리명 검색").input("").run()
                next(s for s in app.selectbox if s.label == "요리 종류 필터").select("양식").run()
                self.assertFalse(any(b.key == "save_generated_1_0" for b in app.button))
                next(s for s in app.selectbox if s.label == "요리 종류 필터").select("전체").run()
                app.button(key="save_generated_1_0").click().run()
                self.assertEqual(storage.stats("demo1", path)["saved"], 1)
                app.session_state["nav"] = "📚 나의 레시피"
                app.run()
                self.assertTrue(app.button(key="delete_1").disabled)
                app.button(key="cook_1").click().run()
                app.session_state["nav"] = "🏠 대시보드"
                app.run()
                self.assertEqual(next(m.value for m in app.metric if m.label == "저장한 레시피"), "1개")
                self.assertEqual(next(m.value for m in app.metric if m.label == "요리한 횟수"), "1회")
                app.session_state["nav"] = "🍽️ 레시피 생성"
                app.run()
                self.assertEqual(app.text_area(key="ingredients").value, "달걀")
                app.session_state["nav"] = "📚 나의 레시피"
                app.run()
                app.checkbox(key="confirm_delete_1").check().run()
                app.button(key="delete_1").click().run()
                self.assertEqual(storage.stats("demo1", path)["saved"], 0)
                next(b for b in app.button if b.label == "로그아웃").click().run()
                self.assertNotIn("user_id", app.session_state)
                self.assertNotIn("generated", app.session_state)
                self.assertFalse(app.exception)

    def test_profile_folders_ratings_and_recommendations(self):
        with tempfile.TemporaryDirectory() as directory:
            original_database = storage.database
            path = Path(directory) / "test.sqlite3"
            with patch("storage.database", lambda ignored: original_database(path)):
                app = AppTest.from_file("app.py", default_timeout=15).run()
                next(b for b in app.button if b.label == "데모 계정").click().run()
                app.session_state["nav"] = "👤 프로필"
                app.run()
                next(t for t in app.text_input if t.label == "이름").input("테스트 요리사")
                next(t for t in app.text_area if t.label == "요리 취향·제외할 재료").input("땅콩 제외")
                next(b for b in app.button if b.label == "프로필 저장").click().run()
                self.assertEqual(storage.profile("demo1", path)["preferences"], "땅콩 제외")
                storage.save_recipe("demo1", RECIPE, path=path)
                app.session_state["nav"] = "📚 나의 레시피"
                app.run()
                app.text_input(key="move_folder_1").input("아침").run()
                app.button(key="move_1").click().run()
                next(s for s in app.selectbox if s.label == "폴더 선택").select("아침").run()
                app.select_slider(key="rating_1").set_value(5).run()
                app.button(key="rate_1").click().run()
                self.assertEqual(storage.saved_recipes("demo1", path)[0]["folder"], "아침")
                self.assertEqual(storage.stats("demo1", path)["rating"], 5.0)
                app.session_state["nav"] = "🏠 대시보드"
                app.run()
                self.assertEqual(next(m.value for m in app.metric if m.label == "평균 평점"), "5.0 ⭐")
                self.assertEqual(next(m.value for m in app.metric if m.label == "레시피 폴더"), "2개")
                app.session_state["nav"] = "🎯 추천"
                app.run()
                self.assertTrue(any(e.label == RECIPE["title"] for e in app.expander))
                next(b for b in app.button if b.label == "🍽️ 새 맞춤 레시피 생성").click().run()
                self.assertEqual(app.session_state["nav"], "🍽️ 레시피 생성")
                self.assertFalse(app.exception)


if __name__ == "__main__":
    unittest.main()
