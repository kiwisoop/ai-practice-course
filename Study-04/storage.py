"""교재 실습용 로컬 계정, 프로필과 레시피 보관함."""

from collections import Counter
from contextlib import contextmanager
import hashlib
import hmac
import json
from pathlib import Path
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from uuid import uuid4

DB_PATH = Path(__file__).with_name("recipes.sqlite3")
DEMO_USERS = {"demo1": "데모 요리사 1", "demo2": "데모 요리사 2"}


@contextmanager
def database(path):
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def init_db(path=DB_PATH):
    with database(path) as db:
        db.execute("CREATE TABLE IF NOT EXISTS profiles (user_id TEXT PRIMARY KEY, name TEXT NOT NULL, preferences TEXT NOT NULL DEFAULT '')")
        db.execute("""CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY, user_id TEXT NOT NULL, fingerprint TEXT NOT NULL,
            body TEXT NOT NULL, folder TEXT NOT NULL DEFAULT '기본', cooked INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, fingerprint))""")
        db.executemany("INSERT OR IGNORE INTO profiles (user_id, name) VALUES (?, ?)", DEMO_USERS.items())
        columns = {row["name"] for row in db.execute("PRAGMA table_info(recipes)")}
        if "rating" not in columns:
            db.execute("ALTER TABLE recipes ADD COLUMN rating INTEGER NOT NULL DEFAULT 0")
        db.execute("CREATE TABLE IF NOT EXISTS accounts (email TEXT PRIMARY KEY, user_id TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)")
        for user_id in DEMO_USERS:
            if not db.execute("SELECT 1 FROM accounts WHERE user_id = ?", (user_id,)).fetchone():
                email = "demo@example.com" if user_id == "demo1" else "demo2@example.com"
                db.execute("INSERT OR IGNORE INTO accounts VALUES (?, ?, ?)", (email, user_id, password_hash("demo1234")))


def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 600_000).hex()
    return salt + ":" + digest


def register_user(email, password, name, path=DB_PATH):
    email = email.strip().lower()
    if len(email) > 254 or email.count("@") != 1 or not all(email.split("@")) or "." not in email.split("@")[-1] or any(c.isspace() for c in email):
        raise ValueError("올바른 이메일 주소를 입력해 주세요.")
    if not 8 <= len(password) <= 128:
        raise ValueError("비밀번호는 8~128자로 입력해 주세요.")
    if not name.strip() or len(name) > 50:
        raise ValueError("이름은 1~50자로 입력해 주세요.")
    user_id = "user_" + uuid4().hex
    try:
        with database(path) as db:
            db.execute("INSERT INTO accounts VALUES (?, ?, ?)", (email, user_id, password_hash(password)))
            db.execute("INSERT INTO profiles (user_id, name) VALUES (?, ?)", (user_id, name.strip()))
    except sqlite3.IntegrityError:
        raise ValueError("이미 가입된 이메일입니다.") from None
    return user_id


def authenticate(email, password, path=DB_PATH):
    if len(password) > 128:
        return None
    with database(path) as db:
        row = db.execute("SELECT user_id, password_hash FROM accounts WHERE email = ?", (email.strip().lower(),)).fetchone()
    if row is None:
        return None
    salt = row["password_hash"].split(":", 1)[0]
    return row["user_id"] if hmac.compare_digest(row["password_hash"], password_hash(password, salt)) else None


def profile(user_id, path=DB_PATH):
    with database(path) as db:
        row = db.execute("SELECT name, preferences FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
        if row is None:
            raise ValueError("로그인한 프로필을 찾을 수 없습니다.")
        return dict(row)


def update_profile(user_id, name, preferences, path=DB_PATH):
    if not name.strip() or len(name) > 50 or len(preferences) > 1000:
        raise ValueError("이름은 1~50자, 취향은 1,000자 이하로 입력해 주세요.")
    with database(path) as db:
        db.execute("UPDATE profiles SET name = ?, preferences = ? WHERE user_id = ?", (name.strip(), preferences.strip(), user_id))


def save_recipe(user_id, recipe, folder="기본", path=DB_PATH):
    folder = folder.strip() or "기본"
    if len(folder) > 50:
        raise ValueError("폴더 이름은 50자 이하여야 합니다.")
    body = json.dumps(recipe, ensure_ascii=False, sort_keys=True)
    fingerprint = hashlib.sha256(body.encode()).hexdigest()
    with database(path) as db:
        if not db.execute("SELECT 1 FROM profiles WHERE user_id = ?", (user_id,)).fetchone():
            raise ValueError("로그인한 프로필을 찾을 수 없습니다.")
        cursor = db.execute("INSERT OR IGNORE INTO recipes (user_id, fingerprint, body, folder) VALUES (?, ?, ?, ?)", (user_id, fingerprint, body, folder))
        return cursor.rowcount == 1


def saved_recipes(user_id, path=DB_PATH):
    with database(path) as db:
        rows = db.execute("SELECT id, body, folder, cooked, rating, created_at FROM recipes WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    return [{**dict(row), "recipe": json.loads(row["body"])} for row in rows]


def move_recipe(user_id, recipe_id, folder, path=DB_PATH):
    folder = folder.strip() or "기본"
    if len(folder) > 50:
        raise ValueError("폴더 이름은 50자 이하여야 합니다.")
    with database(path) as db:
        db.execute("UPDATE recipes SET folder = ? WHERE id = ? AND user_id = ?", (folder, recipe_id, user_id))


def mark_cooked(user_id, recipe_id, path=DB_PATH):
    with database(path) as db:
        db.execute("UPDATE recipes SET cooked = cooked + 1 WHERE id = ? AND user_id = ?", (recipe_id, user_id))


def delete_recipe(user_id, recipe_id, path=DB_PATH):
    with database(path) as db:
        db.execute("DELETE FROM recipes WHERE id = ? AND user_id = ?", (recipe_id, user_id))


def rate_recipe(user_id, recipe_id, rating, path=DB_PATH):
    if type(rating) is not int or not 0 <= rating <= 5:
        raise ValueError("평점은 0~5 사이로 입력해 주세요.")
    with database(path) as db:
        db.execute("UPDATE recipes SET rating = ? WHERE id = ? AND user_id = ?", (rating, recipe_id, user_id))


def stats(user_id, path=DB_PATH):
    rows = saved_recipes(user_id, path)
    ingredients = Counter()
    for row in rows:
        ingredients.update({item["name"] for item in row["recipe"]["ingredients"]})
    ratings = [row["rating"] for row in rows if row["rating"]]
    week_start = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    return {
        "saved": len(rows), "cooked": sum(row["cooked"] for row in rows), "ingredients": ingredients.most_common(10),
        "rating": round(sum(ratings) / len(ratings), 1) if ratings else None,
        "folders": len({"기본"} | {row["folder"] for row in rows}),
        "weekly_saved": sum(row["created_at"] >= week_start for row in rows),
    }
