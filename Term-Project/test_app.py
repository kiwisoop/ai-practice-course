import io
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch

from storage import Database, KST
from server import DiaryHandler


class DiaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.env = patch.dict(os.environ, {'DIARY_DATA_DIR': self.temp.name})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.db = Database()

    def test_crud_survives_reopening_and_period_changes(self):
        self.db.save_diary('2024-11-16', '기록 보존 검사')
        self.db.set_setting('start_year', 2025)
        reopened = Database()
        self.assertEqual(reopened.get_diary('2024-11-16')['content'], '기록 보존 검사')
        self.assertEqual(reopened.get_setting('start_year'), 2025)
        reopened.save_diary('2024-11-16', '수정한 기록')
        self.assertEqual(self.db.get_diary('2024-11-16')['content'], '수정한 기록')
        reopened.delete_diary('2024-11-16')
        self.assertEqual(self.db.get_diary('2024-11-16')['content'], '')

    def test_actual_calendar_dates_not_just_even_years(self):
        for valid in ('1900-03-01', '2000-02-29', '2024-02-29'):
            with self.subTest(valid=valid):
                self.db.save_diary(valid, '실제 날짜')
                self.assertEqual(self.db.get_diary(valid)['date'], valid)
        for invalid in ('1900-02-29', '2025-02-29', '2100-02-29', '2024-04-31', '2024-13-01', '2024-2-1', None, 123):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.db.save_diary(invalid, '잘못된 날짜')
        self.assertEqual(self.db.get_diary('2025-02-28')['content'], '')

    def test_future_and_content_validation_preserve_previous_record(self):
        self.db.save_diary('2024-11-16', '원본')
        for invalid in ('', '   ', None, 1, [], 'a' * 10001):
            with self.subTest(invalid=type(invalid).__name__), self.assertRaises(ValueError):
                self.db.save_diary('2024-11-16', invalid)
        tomorrow = (datetime.now(KST).date() + timedelta(days=1)).isoformat()
        with self.assertRaises(ValueError):
            self.db.save_diary(tomorrow, '미래')
        self.assertEqual(self.db.get_diary('2024-11-16')['content'], '원본')

    def test_invalid_period_does_not_change_setting(self):
        self.db.set_setting('start_year', 2024)
        for invalid in (True, 1899, 2098, 2024.5, '2024', None):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.db.set_setting('start_year', invalid)
        self.assertEqual(self.db.get_setting('start_year'), 2024)

    def test_demo_never_overwrites_real_record(self):
        self.db.save_diary('2024-11-17', '실제 기록')
        self.db.load_demo_data()
        self.db.load_demo_data()
        self.assertEqual(self.db.get_diary('2024-11-17')['content'], '실제 기록')
        self.assertFalse(self.db.get_diary('2024-11-17')['is_demo'])
        self.assertTrue(self.db.get_diary('2025-11-17')['is_demo'])
        self.assertTrue(self.db.get_diary('2026-11-17')['is_demo'])

    def test_long_demo_upgrades_only_untouched_legacy_sample(self):
        old = '오랜만에 친구를 만나 한참을 웃었다.\n함께 걷던 길의 은행잎이 유난히 노랬다.'
        entry = self.db.save_diary('2024-11-17', old)
        self.db.attach_image(entry['date'], entry['content_hash'], '/assets/demo-walk.png')
        self.db.load_demo_data()
        upgraded = self.db.get_diary(entry['date'])
        self.assertGreater(len(upgraded['content']), 1000)
        self.assertTrue(upgraded['is_demo'])
        self.assertTrue(upgraded['image_stale'], '이전 시연 그림을 새 일기의 생성 결과로 표시하지 않음')
        self.assertEqual(upgraded['image_path'], '/assets/demo-walk.png')
        self.db.attach_image(upgraded['date'], upgraded['content_hash'], '/media/' + 'a'*32 + '.png')
        before = self.db.get_diary(entry['date'])
        self.db.load_demo_data()
        self.assertEqual(self.db.get_diary(entry['date']), before)

    def test_edited_legacy_sample_is_preserved(self):
        content = '오랜만에 친구를 만나 한참을 웃었다.\n내가 추가한 개인 기록.'
        entry = self.db.save_diary('2024-11-17', content)
        self.db.attach_image(entry['date'], entry['content_hash'], '/assets/demo-walk.png')
        self.db.load_demo_data()
        self.assertEqual(self.db.get_diary(entry['date'])['content'], content)

    def test_image_is_preserved_and_marked_stale_after_edit(self):
        self.db.load_demo_data()
        seed = self.db.get_diary('2025-11-17')
        self.assertTrue(seed['image_stale'])
        self.db.attach_image(seed['date'], seed['content_hash'], seed['image_path'])
        before = self.db.get_diary('2025-11-17')
        self.assertFalse(before['image_stale'])
        self.db.save_diary('2025-11-17', '수정한 이야기')
        after = self.db.get_diary('2025-11-17')
        self.assertNotEqual(before['content_hash'], after['content_hash'])
        self.assertEqual(before['image_path'], after['image_path'])
        self.assertEqual(before['image_content_hash'], after['image_content_hash'])
        self.assertTrue(after['image_stale'])
        self.assertFalse(after['is_demo'])

    def request(self, method, path, body=None, headers=None):
        raw = json.dumps(body, ensure_ascii=False).encode() if body is not None else b''
        handler = object.__new__(DiaryHandler)
        handler.command = method
        handler.path = path
        handler.server = SimpleNamespace(server_port=8765)
        handler.headers = {'Host': '127.0.0.1:8765', 'Origin': 'http://127.0.0.1:8765',
                           'Content-Type': 'application/json', 'Content-Length': str(len(raw)), **(headers or {})}
        handler.rfile = io.BytesIO(raw)
        handler.reply = Mock()
        handler.handle_request()
        return handler.reply.call_args.args

    def test_api_crud_and_demo_contract(self):
        self.assertEqual(self.request('POST', '/api/diary', {'date': '2024-11-16', 'content': 'API 검사'})[0], 200)
        status, entry = self.request('GET', '/api/diary?date=2024-11-16')
        self.assertEqual((status, entry['content']), (200, 'API 검사'))
        self.assertIn('content_hash', entry)
        self.assertEqual(self.request('DELETE', '/api/diary?date=2024-11-16'), (200, {'deleted': True}))
        self.assertEqual(self.request('GET', '/api/diary?date=2024-11-16')[1]['content'], '')
        self.assertEqual(self.request('POST', '/api/demo', {})[1], {'start_year': 2024, 'month': 11, 'day': 17})

    def test_private_files_and_paths_are_not_exposed(self):
        for path in ('/server.py', '/storage.py', '/.env', '/data/diary.sqlite3', '/collaboration/007-response.json', '/design/ASSET_PROMPTS.md', '/../storage.py', '/%2e%2e/storage.py'):
            with self.subTest(path=path):
                self.assertEqual(self.request('GET', path)[0], 404)
        self.assertEqual(self.request('GET', '/')[0], 200)
        self.assertEqual(self.request('GET', '/assets/demo-walk.png')[0], 200)

    def test_request_validation_rejects_before_writes(self):
        for body in ([], None, {'date': None, 'content': 'x'}, {'date': '2024-11-16', 'content': None}):
            with self.subTest(body=body):
                self.assertIn(self.request('POST', '/api/diary', body)[0], (400, 413))
        for length in ('-1', '65537', '0'):
            self.assertEqual(self.request('POST', '/api/demo', {}, {'Content-Length': length})[0], 413)
        self.assertEqual(self.request('POST', '/api/demo', {}, {'Content-Length': 'bad'})[0], 400)
        self.assertEqual(self.request('POST', '/api/demo', {}, {'Content-Type': 'text/plain'})[0], 415)
        self.assertEqual(self.request('GET', '/api/settings', headers={'Host': 'evil.test'})[0], 403)
        self.assertEqual(self.request('POST', '/api/demo', {}, {'Origin': 'https://evil.test'})[0], 403)
        self.assertEqual(self.db.get_diary('2024-11-16')['content'], '')


if __name__ == '__main__':
    unittest.main()
