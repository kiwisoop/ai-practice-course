import sqlite3
import json
import os
import hashlib
from pathlib import Path
from datetime import datetime, date, timezone, timedelta

KST = timezone(timedelta(hours=9))

class Database:
    def __init__(self):
        data_dir = os.environ.get('DIARY_DATA_DIR', str(Path(__file__).resolve().parent / 'data'))
        Path(data_dir).mkdir(parents=True, exist_ok=True)
        self.db_path = os.path.join(data_dir, 'diary.sqlite3')
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diary (
                date TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                content_hash TEXT,
                image_path TEXT,
                image_content_hash TEXT,
                is_demo INTEGER DEFAULT 0,
                updated_at TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        cursor.execute('CREATE TABLE IF NOT EXISTS videos (id TEXT PRIMARY KEY, metadata TEXT NOT NULL)')
        conn.commit()
        conn.close()
    
    def _validate_date(self, date_str):
        try:
            d = date.fromisoformat(date_str)
            if d.isoformat() != date_str:
                raise ValueError('존재하지 않거나 형식이 올바르지 않은 날짜입니다.')
            return d
        except (ValueError, TypeError):
            raise ValueError('존재하지 않거나 형식이 올바르지 않은 날짜입니다.') from None
    
    def _validate_content(self, content):
        if not isinstance(content, str):
            raise ValueError('Content must be string')
        content = content.strip()
        if len(content) < 1 or len(content) > 10000:
            raise ValueError('Content must be 1-10000 characters')
        return content
    
    def _validate_start_year(self, year):
        if not isinstance(year, int) or isinstance(year, bool):
            raise ValueError('start_year must be integer')
        if year < 1900 or year > 2097:
            raise ValueError('start_year must be 1900-2097')
        return year
    
    @staticmethod
    def is_leap_year(year):
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    
    def save_diary(self, date_str, content):
        d = self._validate_date(date_str)
        content = self._validate_content(content)
        today = datetime.now(KST).date()
        if d > today:
            raise ValueError('Cannot save future dates')
        
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        now = datetime.now(KST).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM diary WHERE date = ?', (date_str,))
        exists = cursor.fetchone() is not None
        
        if exists:
            cursor.execute('UPDATE diary SET content = ?, content_hash = ?, updated_at = ?, is_demo = 0 WHERE date = ?',
                          (content, content_hash, now, date_str))
        else:
            cursor.execute('INSERT INTO diary (date, content, content_hash, is_demo, updated_at) VALUES (?, ?, ?, 0, ?)',
                          (date_str, content, content_hash, now))
        conn.commit()
        
        cursor.execute('SELECT date, content, image_path, image_content_hash, is_demo, updated_at FROM diary WHERE date = ?', (date_str,))
        row = cursor.fetchone()
        conn.close()
        
        image_stale = row[2] is not None and row[3] != content_hash
        return {
            'date': row[0],
            'content': row[1],
            'content_hash': content_hash,
            'image_path': row[2],
            'image_content_hash': row[3],
            'is_demo': bool(row[4]),
            'image_stale': image_stale,
            'updated_at': row[5]
        }
    
    def get_diary(self, date_str):
        self._validate_date(date_str)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT date, content, image_path, image_content_hash, is_demo, updated_at, content_hash FROM diary WHERE date = ?', (date_str,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            image_stale = row[2] is not None and row[3] != row[6]
            return {
                'date': row[0],
                'content': row[1],
                'content_hash': row[6],
                'image_path': row[2],
                'image_content_hash': row[3],
                'is_demo': bool(row[4]),
                'image_stale': image_stale,
                'updated_at': row[5]
            }
        return {
            'date': date_str,
            'content': '',
            'content_hash': None,
            'image_path': None,
            'image_content_hash': None,
            'is_demo': False,
            'image_stale': False,
            'updated_at': None
        }
    
    def delete_diary(self, date_str):
        self._validate_date(date_str)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM diary WHERE date = ?', (date_str,))
        cursor.execute('DELETE FROM settings WHERE key = ?', ('shorts_story:' + date_str,))
        cursor.execute('DELETE FROM settings WHERE key LIKE ?', ('shorts_scene:' + date_str + ':%',))
        conn.commit()
        conn.close()

    def attach_image(self, date_str, content_hash, image_path):
        self._validate_date(date_str)
        conn = sqlite3.connect(self.db_path)
        try:
            with conn:
                cursor = conn.execute(
                    'UPDATE diary SET image_path = ?, image_content_hash = ? WHERE date = ? AND content_hash = ?',
                    (image_path, content_hash, date_str, content_hash))
            return cursor.rowcount == 1
        finally:
            conn.close()

    def has_image(self, image_path):
        conn = sqlite3.connect(self.db_path)
        try:
            return (conn.execute('SELECT 1 FROM diary WHERE image_path = ?', (image_path,)).fetchone() is not None
                    or conn.execute("SELECT 1 FROM settings WHERE key LIKE 'shorts_scene:%' AND value = ?", (image_path,)).fetchone() is not None)
        finally:
            conn.close()

    def save_video(self, video_id, metadata):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('INSERT INTO videos VALUES (?, ?)', (video_id, json.dumps(metadata, ensure_ascii=False)))

    def list_videos(self, date_str):
        self._validate_date(date_str)
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute('SELECT metadata FROM videos ORDER BY rowid DESC').fetchall()
        result = []
        for row in rows:
            item = json.loads(row[0])
            if date_str in item['sources']:
                item['stale'] = any(self.get_diary(d)['content_hash'] != h for d, h in item['sources'].items())
                result.append(item)
        return result
    
    def get_setting(self, key, default=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        if row:
            try:
                return int(row[0])
            except (ValueError, TypeError):
                return row[0]
        return default
    
    def set_setting(self, key, value):
        if key == 'start_year':
            value = self._validate_start_year(value)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, str(value)))
        conn.commit()
        conn.close()
    
    def load_demo_data(self):
        legacy_entries = [
            ('2024-11-17', '오랜만에 친구를 만나 한참을 웃었다.\n함께 걷던 길의 은행잎이 유난히 노랬다.', '/assets/demo-walk.png'),
            ('2025-11-17', '바쁜 하루 끝에 따뜻한 차를 마셨다.\n창밖의 낙엽을 보며 잠시 쉬어갔다.', '/assets/demo-tea.png'),
            ('2026-11-17', '조금씩 만들던 다이어리가 모습을 갖췄다.\n지난 기록을 보니 나도 많이 달라져 있었다.', '/assets/demo-diary.png'),
        ]
        demo_entries = json.loads((Path(__file__).resolve().parent / 'demo_diaries.json').read_text(encoding='utf-8'))
        legacy = {item[0]: item for item in legacy_entries}
        previous = {}
        previous_path = Path(__file__).resolve().parent / 'demo_diaries_previous.json'
        if previous_path.is_file():
            for item in json.loads(previous_path.read_text(encoding='utf-8')):
                previous.setdefault(item['date'], []).append(item['content'])
        now = datetime.now(KST).isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for entry in demo_entries:
            date_str, content, image_path = entry['date'], entry['content'], entry['image_path']
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            cursor.execute('INSERT OR IGNORE INTO diary (date, content, content_hash, image_path, image_content_hash, is_demo, updated_at) VALUES (?, ?, ?, ?, ?, 1, ?)',
                          (date_str, content, content_hash, image_path, None, now))
            _, old_content, old_image = legacy[date_str]
            old_hash = hashlib.sha256(old_content.encode()).hexdigest()
            cursor.execute('UPDATE diary SET content = ?, content_hash = ?, is_demo = 1, updated_at = ? WHERE date = ? AND content = ? AND content_hash = ? AND image_path = ? AND image_content_hash = ?',
                           (content, content_hash, now, date_str, old_content, old_hash, old_image, old_hash))
            # Replace the previous long demo text only while it is still an untouched demo record.
            for previous_content in previous.get(date_str, []):
                cursor.execute('UPDATE diary SET content = ?, content_hash = ?, updated_at = ? WHERE date = ? AND is_demo = 1 AND content_hash = ?',
                               (content, content_hash, now, date_str, hashlib.sha256(previous_content.encode()).hexdigest()))
            self._seed_demo_story(cursor, date_str, content_hash, entry.get('captions'))
        conn.commit()
        conn.close()

    @staticmethod
    def _seed_demo_story(cursor, date_str, content_hash, captions):
        """Store hand-written demo captions so demo shorts need no AI call. Marked demo, never overwrites a story for this text."""
        if not isinstance(captions, list) or not captions:
            return
        row = cursor.execute('SELECT is_demo, content_hash FROM diary WHERE date = ?', (date_str,)).fetchone()
        if not row or row[0] != 1 or row[1] != content_hash:
            return
        key = 'shorts_story:' + date_str
        existing = cursor.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
        try:
            if existing and json.loads(existing[0]).get('content_hash') == content_hash:
                return
        except (ValueError, AttributeError):
            pass
        # version must match server.STORY_VERSION for the cache to be reused.
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
                       (key, json.dumps({'version': 1, 'content_hash': content_hash, 'captions': captions, 'demo': True}, ensure_ascii=False)))

    def list_diaries(self, start_year):
        self._validate_start_year(start_year)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute('SELECT * FROM diary WHERE date BETWEEN ? AND ? ORDER BY date',
                                (f'{start_year}-01-01', f'{start_year+2}-12-31')).fetchall()
            result = [dict(row) for row in rows]
            for entry in result:
                entry['is_demo'] = bool(entry['is_demo'])
                entry['image_stale'] = bool(entry['image_path'] and entry['image_content_hash'] != entry['content_hash'])
            return result
        finally:
            conn.close()
