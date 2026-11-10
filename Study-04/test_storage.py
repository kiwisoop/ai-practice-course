import tempfile
import json
from pathlib import Path
import unittest

import storage

RECIPE = {
    "title": "달걀볶음", "minutes": 10, "cuisine": "한식", "difficulty": "쉬움",
    "ingredients": [{"name": "달걀", "amount": "2개"}], "extra_ingredients": [],
    "steps": ["달걀을 깨서 충분히 익힌다."],
}


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "recipes.sqlite3"
        storage.init_db(self.path)

    def test_persistence_duplicates_and_user_isolation(self):
        self.assertTrue(storage.save_recipe("demo1", RECIPE, path=self.path))
        self.assertFalse(storage.save_recipe("demo1", RECIPE, path=self.path))
        self.assertEqual(storage.saved_recipes("demo2", self.path), [])
        row = storage.saved_recipes("demo1", self.path)[0]
        for operation in (
            lambda: storage.move_recipe("demo2", row["id"], "침범", self.path),
            lambda: storage.mark_cooked("demo2", row["id"], self.path),
            lambda: storage.delete_recipe("demo2", row["id"], self.path),
        ):
            operation()
        self.assertEqual(storage.saved_recipes("demo1", self.path)[0]["folder"], "기본")
        self.assertEqual(storage.stats("demo1", self.path)["cooked"], 0)
        storage.move_recipe("demo1", row["id"], "아침", self.path)
        storage.mark_cooked("demo1", row["id"], self.path)
        storage.init_db(self.path)
        self.assertEqual(storage.saved_recipes("demo1", self.path)[0]["folder"], "아침")
        stats = storage.stats("demo1", self.path)
        self.assertEqual((stats["saved"], stats["cooked"], stats["ingredients"]), (1, 1, [("달걀", 1)]))
        storage.rate_recipe("demo2", row["id"], 5, self.path)
        self.assertIsNone(storage.stats("demo1", self.path)["rating"])
        storage.rate_recipe("demo1", row["id"], 4, self.path)
        self.assertEqual(storage.stats("demo1", self.path)["rating"], 4.0)
        self.assertTrue(storage.save_recipe("demo2", RECIPE, path=self.path))
        storage.delete_recipe("demo1", row["id"], self.path)
        self.assertEqual(storage.stats("demo1", self.path)["saved"], 0)
        self.assertEqual(storage.stats("demo2", self.path)["saved"], 1)

    def test_profile_and_failed_write_preserve_data(self):
        storage.update_profile("demo1", "요리 실습", "땅콩 제외", self.path)
        self.assertEqual(storage.profile("demo1", self.path)["preferences"], "땅콩 제외")
        self.assertEqual(storage.profile("demo2", self.path)["preferences"], "")
        with self.assertRaises(ValueError):
            storage.update_profile("demo1", "", "", self.path)
        self.assertEqual(storage.profile("demo1", self.path)["name"], "요리 실습")
        with self.assertRaises(ValueError):
            storage.save_recipe("unknown", RECIPE, path=self.path)

    def test_registration_and_login(self):
        self.assertEqual(storage.authenticate("demo@example.com", "demo1234", self.path), "demo1")
        self.assertIsNone(storage.authenticate("demo@example.com", "wrong", self.path))
        user_id = storage.register_user("cook@example.com", "test-password", "요리사", self.path)
        self.assertEqual(storage.authenticate("COOK@example.com", "test-password", self.path), user_id)
        self.assertEqual(storage.profile(user_id, self.path)["name"], "요리사")
        with storage.database(self.path) as db:
            password = db.execute("SELECT password_hash FROM accounts WHERE user_id = ?", (user_id,)).fetchone()[0]
            self.assertNotIn("test-password", password)
        with self.assertRaises(ValueError):
            storage.register_user("cook@example.com", "test-password", "다른 이름", self.path)
        with self.assertRaises(ValueError):
            storage.register_user("invalid", "test-password", "요리사", self.path)
        storage.init_db(self.path)
        self.assertEqual(storage.authenticate("cook@example.com", "test-password", self.path), user_id)

    def test_existing_database_is_migrated_without_losing_recipes(self):
        old_path = Path(self.directory.name) / "old.sqlite3"
        with storage.database(old_path) as db:
            db.execute("CREATE TABLE recipes (id INTEGER PRIMARY KEY, user_id TEXT NOT NULL, fingerprint TEXT NOT NULL, body TEXT NOT NULL, folder TEXT NOT NULL DEFAULT '기본', cooked INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(user_id, fingerprint))")
            db.execute("INSERT INTO recipes (user_id, fingerprint, body) VALUES (?, ?, ?)", ("demo1", "existing", json.dumps(RECIPE)))
        storage.init_db(old_path)
        rows = storage.saved_recipes("demo1", old_path)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["recipe"], RECIPE)
        self.assertEqual(rows[0]["rating"], 0)


if __name__ == "__main__":
    unittest.main()
