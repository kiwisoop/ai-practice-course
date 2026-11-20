import base64
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import HTTPError

import image_api
from server import create_image, IMAGE_LOCK, media_file
from storage import Database

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jZ1cAAAAASUVORK5CYII=')
KEY = 'test-only-not-a-real-key'


class Response(io.BytesIO):
    def __init__(self, body, mime='application/json'):
        super().__init__(body)
        self.headers = {'Content-Type': mime}


def api_result(credits=10):
    return Response(json.dumps({'data': [{'url': 'data:image/png;base64,' + base64.b64encode(PNG).decode()}],
                                'credits_charged': credits}).encode())


class ImageAPITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / '.env'
        self.env = patch.dict(os.environ, {'FACTCHAT_API_KEY': KEY})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.env_path = patch.object(image_api, 'ENV_PATH', self.path)
        self.env_path.start()
        self.addCleanup(self.env_path.stop)

    def test_key_from_local_file_and_invalid_key_never_calls_api(self):
        os.environ['FACTCHAT_API_KEY'] = ''
        self.path.write_text('# example\nFACTCHAT_API_KEY="' + KEY + '"\n')
        self.assertEqual(image_api.get_api_key(), KEY)
        self.path.unlink()
        with patch.object(image_api, 'build_opener') as opener:
            self.assertFalse(image_api.configured())
            with self.assertRaises(ValueError):
                image_api.generate_image('2024-11-17', '가상 일기')
            opener.assert_not_called()
            os.environ['FACTCHAT_API_KEY'] = 'bad key'
            self.assertFalse(image_api.configured())
            with self.assertRaises(ValueError):
                image_api.generate_image('2024-11-17', '가상 일기')
            opener.assert_not_called()

    def test_success_uses_selected_model_once_and_returns_actual_credits(self):
        opener = Mock()
        opener.open.return_value = api_result(9.5)
        with patch.object(image_api, 'build_opener', return_value=opener):
            body, extension, credits = image_api.generate_image('2024-11-17', '친구와 산책했다.')
        self.assertEqual((body, extension, credits), (PNG, 'png', 9.5))
        self.assertEqual(opener.open.call_count, 1)
        request = opener.open.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(payload['model'], 'gpt-image-2.5-sunburst')
        self.assertEqual(payload['number_of_images'], 1)
        self.assertNotIn('quality', payload)
        self.assertNotIn(KEY, payload['prompt'])
        self.assertIn('친구와 산책했다.', payload['prompt'])

    def test_long_demo_is_sent_in_full_to_selected_image_model(self):
        entries = json.loads((Path(__file__).parent / 'demo_diaries.json').read_text())
        for entry in entries:
            self.assertGreater(len(entry['content']), 1000)
            opener = Mock()
            opener.open.return_value = api_result()
            with patch.object(image_api, 'build_opener', return_value=opener):
                image_api.generate_image(entry['date'], entry['content'])
            payload = json.loads(opener.open.call_args.args[0].data)
            reference = json.loads(payload['prompt'].split('\n', 1)[1])
            self.assertEqual(reference['diary'], entry['content'])
            self.assertEqual(reference['date'], entry['date'])
            self.assertEqual(payload['model'], 'gpt-image-2.5-sunburst')
            self.assertEqual(opener.open.call_count, 1)

    def test_bad_dates_mime_and_base64_are_rejected(self):
        for invalid in ('2024-2-1', '2025-02-29', None):
            with self.subTest(invalid=invalid), patch.object(image_api, 'build_opener') as opener:
                with self.assertRaises(ValueError):
                    image_api.generate_image(invalid, 'test')
                opener.assert_not_called()
        for url in ('data:image/png;base64,%%%','data:image/jpeg;base64,' + base64.b64encode(PNG).decode(), 'data:image/svg+xml;base64,PHN2Zz4='):
            with self.subTest(url=url), self.assertRaises(ValueError):
                image_api._read_image(url)

    def test_failed_api_is_not_retried_and_key_is_not_in_error(self):
        opener = Mock()
        opener.open.side_effect = HTTPError(image_api.API_ENDPOINT, 429, 'private raw response', {}, None)
        with patch.object(image_api, 'build_opener', return_value=opener):
            with self.assertRaises(ValueError) as error:
                image_api.generate_image('2024-11-17', 'test')
        self.assertNotIn(KEY, str(error.exception))
        self.assertNotIn('private raw response', str(error.exception))
        self.assertEqual(opener.open.call_count, 1)

    def test_remote_download_has_no_api_key_and_blocks_private_dns(self):
        api = Mock(); download = Mock()
        api.open.return_value = Response(json.dumps({'data':[{'url':'https://images.example/art.png'}]}).encode())
        download.open.return_value = Response(PNG, 'image/png')
        addresses = [(2, 1, 6, '', ('93.184.216.34', 443))]
        with patch.object(image_api, 'build_opener', side_effect=[api, download]), patch.object(image_api.socket, 'getaddrinfo', return_value=addresses):
            self.assertEqual(image_api.generate_image('2024-11-17', 'test')[:2], (PNG, 'png'))
        headers = dict((k.lower(), v) for k, v in download.open.call_args.args[0].header_items())
        self.assertNotIn('authorization', headers)
        private = [(2, 1, 6, '', ('127.0.0.1', 443))]
        with patch.object(image_api.socket, 'getaddrinfo', return_value=private), self.assertRaises(ValueError):
            image_api._public_url('https://images.example/art.png')
        with self.assertRaises(ValueError):
            image_api.NoRedirects().redirect_request(None, None, 302, '', {}, 'https://elsewhere.example/')
        with patch.object(image_api.socket, 'getaddrinfo', return_value=private), self.assertRaises(ValueError):
            image_api.ImageRedirects().redirect_request(Mock(full_url='https://images.example/'), None, 302, '', {}, 'https://local.example/art.png')


class ImageStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.env = patch.dict(os.environ, {'DIARY_DATA_DIR': self.temp.name})
        self.env.start(); self.addCleanup(self.env.stop)
        self.db = Database()
        self.entry = self.db.save_diary('2024-11-16', '시연용 일기')
        self.request = {'date':self.entry['date'], 'content_hash':self.entry['content_hash'], 'consent':True}

    def test_generation_persists_and_reopen_reuses_without_new_charge(self):
        with patch('server.image_api.generate_image', return_value=(PNG, 'png', 10)) as generate:
            status, result = create_image(self.db, self.request)
            self.assertEqual(status, 200)
            self.assertFalse(result['cached'])
            self.assertEqual(result['credits_charged'], 10)
            entry = Database().get_diary(self.entry['date'])
            self.assertEqual(media_file(self.db, entry['image_path']).read_bytes(), PNG)
            self.assertFalse(entry['image_stale'])
            status, result = create_image(Database(), self.request)
            self.assertTrue(result['cached'])
            self.assertEqual(result['credits_charged'], 0)
            self.assertEqual(generate.call_count, 1)

    def test_failure_and_midflight_edit_preserve_diary_and_old_image(self):
        with patch('server.image_api.generate_image', return_value=(PNG, 'png', 10)):
            create_image(self.db, self.request)
        old = self.db.get_diary(self.entry['date'])
        with patch('server.image_api.generate_image', side_effect=ValueError('mock failure')):
            with self.assertRaises(ValueError):
                create_image(self.db, dict(self.request, regenerate=True))
        self.assertEqual(self.db.get_diary(self.entry['date'])['image_path'], old['image_path'])
        def changed_during_generation(*args):
            self.db.save_diary(self.entry['date'], '생성 중 수정한 본문')
            return PNG, 'png', 10
        with patch('server.image_api.generate_image', side_effect=changed_during_generation):
            status, result = create_image(self.db, dict(self.request, regenerate=True))
        self.assertEqual(status, 409)
        current = self.db.get_diary(self.entry['date'])
        self.assertEqual(current['content'], '생성 중 수정한 본문')
        self.assertEqual(current['image_path'], old['image_path'])
        self.assertTrue(current['image_stale'])
        self.assertEqual(len(list((Path(self.temp.name) / 'images').glob('*'))), 1)

    def test_no_consent_stale_request_and_duplicate_never_call_provider(self):
        with patch('server.image_api.generate_image') as generate:
            with self.assertRaises(ValueError):
                create_image(self.db, dict(self.request, consent=False))
            status, _ = create_image(self.db, dict(self.request, content_hash='old'))
            self.assertEqual(status, 409)
            IMAGE_LOCK.acquire()
            try:
                self.assertEqual(create_image(self.db, self.request)[0], 409)
            finally:
                IMAGE_LOCK.release()
            generate.assert_not_called()
        self.assertIsNone(media_file(self.db, '/media/../server.py'))
        self.assertIsNone(media_file(self.db, '/data/diary.sqlite3'))


if __name__ == '__main__':
    unittest.main()
