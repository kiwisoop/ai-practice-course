import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import server
import video_export as video
import test_app


class VideoTests(unittest.TestCase):
    setUp = test_app.DiaryTests.setUp
    request = test_app.DiaryTests.request

    def select(self):
        self.db.load_demo_data()
        for entry in self.db.list_diaries(2024):
            self.db.attach_image(entry['date'], entry['content_hash'], entry['image_path'])
        return [{'date': e['date'], 'content_hash': e['content_hash'], 'caption': '가을의 기록'}
                for e in self.db.list_diaries(2024)]

    def test_memories_period_and_video_use_saved_images_only(self):
        selection = self.select()
        self.db.save_diary('2023-11-17', '기간 밖 기록')
        status, data = self.request('GET', '/api/memories')
        self.assertEqual(status, 200)
        self.assertEqual([e['date'] for e in data['entries']], [i['date'] for i in selection])
        with patch.object(server, 'export_video') as render:
            status, result = self.request('POST', '/api/video', {'items': selection})
        self.assertEqual((status, result['seconds']), (200, 12))
        self.assertRegex(result['url'], r'^/videos/[0-9a-f]{32}\.mp4$')
        self.assertEqual(render.call_args.args[0][0]['image_path'], server.ROOT / 'assets/demo-walk.png')

    def test_changed_missing_duplicate_and_long_selections_never_render(self):
        selected = self.select()[0]
        bad = [[], [selected] * 9, [selected, selected], [{**selected, 'caption': '가' * 65}],
               [{**selected, 'content_hash': 'old'}], [{**selected, 'date': '../.env'}]]
        with patch.object(server, 'export_video') as render:
            for items in bad:
                with self.subTest(items=len(items)):
                    self.assertEqual(self.request('POST', '/api/video', {'items': items})[0], 400)
            self.db.save_diary(selected['date'], '수정한 기록')
            changed = self.db.get_diary(selected['date'])
            self.assertEqual(self.request('POST', '/api/video', {'items': [{**selected, 'content_hash': changed['content_hash']}]})[0], 400)
            render.assert_not_called()

    def test_busy_and_failure_release_lock_and_preserve_diary(self):
        selected = self.select()
        server.VIDEO_LOCK.acquire()
        try:
            self.assertEqual(self.request('POST', '/api/video', {'items': selected})[0], 409)
        finally:
            server.VIDEO_LOCK.release()
        before = self.db.list_diaries(2024)
        with patch.object(server, 'export_video', side_effect=ValueError('영상 생성 실패')):
            self.assertEqual(self.request('POST', '/api/video', {'items': selected})[0], 400)
        self.assertFalse(server.VIDEO_LOCK.locked())
        self.assertEqual(self.db.list_diaries(2024), before)

    def test_video_download_range_and_private_path_rejection(self):
        folder = Path(self.db.db_path).parent / 'videos'
        folder.mkdir()
        (folder / ('a' * 32 + '.mp4')).write_bytes(b'0123456789')
        url = '/videos/' + 'a' * 32 + '.mp4'
        self.assertEqual(self.request('GET', url)[:3], (200, b'0123456789', 'video/mp4'))
        for spec, expected in [('bytes=0-1', b'01'), ('bytes=5-', b'56789'), ('bytes=-3', b'789')]:
            status, body, mime, headers = self.request('GET', url, headers={'Range': spec})
            self.assertEqual((status, body), (206, expected))
            self.assertIn('Content-Range', headers)
        for spec in ('bytes=20-', 'bytes=-0', 'bytes=4-2', 'bytes=a-b', 'bytes=0-1,3-4'):
            self.assertEqual(self.request('GET', url, headers={'Range': spec})[0], 416)
        for path in ('/videos/../.env', '/videos/test.mp4', '/videos/' + 'b' * 32 + '.mp4'):
            self.assertEqual(self.request('GET', path)[0], 404)

    def test_shorts_work_for_short_and_long_diaries_without_provider_calls(self):
        for content in ('산책했다.', '긴 하루를 기록했다. ' * 150):
            entry = self.db.save_diary('2024-11-16', content)
            self.db.attach_image(entry['date'], entry['content_hash'], '/assets/demo-walk.png')
            with patch.object(server, 'export_video') as render, patch.object(server.image_api, 'generate_image') as provider:
                status, result = self.request('POST', '/api/shorts', {'items':[{'date':entry['date'], 'content_hash':entry['content_hash']}], 'captions':['잠깐의 산책', '가벼워진 마음']})
                self.assertEqual((status,result['seconds']), (200,8))
                self.assertEqual([i['caption'] for i in render.call_args.args[0]], ['잠깐의 산책','가벼워진 마음'])
                self.assertEqual(render.call_args.kwargs, {'shorts':True, 'music':'bright', 'switch_music':None})
                self.assertTrue(all(i['date'] == entry['date'] for i in render.call_args.args[0]))
                provider.assert_not_called()
            self.assertEqual(self.db.get_diary(entry['date'])['content'], content.strip())

    def test_shorts_caption_validation_and_image_version(self):
        item = self.select()[0]
        with patch.object(server, 'export_video') as render:
            for captions in (None, [], ['a']*9, ['가'*65], [''], [123], ['a\nb'], ['a\rb']):
                self.assertEqual(self.request('POST','/api/shorts',{'items':[item],'captions':captions})[0],400)
            self.assertEqual(self.request('POST','/api/shorts',{'items':[item,item],'captions':['한 장면']})[0],400)
            self.db.save_diary(item['date'], '수정한 기록')
            edited = self.db.get_diary(item['date'])
            self.assertEqual(self.request('POST','/api/shorts',{'items':[{**item,'content_hash':edited['content_hash']}],'captions':['한 장면']})[0],400)
            render.assert_not_called()

    @unittest.skipUnless(Path(video.FFMPEG).is_file(), 'ffmpeg-full 설치 필요')
    def test_real_shorts_long_caption_gets_more_reading_time_and_audio(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'shorts.mp4'
            items = [{'date':'2024-11-17', 'caption':caption, 'image_path':server.ROOT / 'assets/demo-walk.png'} for caption in ('가'*64, '조금 가벼워진 마음')]
            video.export_video(items, output, shorts=True)
            info = json.loads(subprocess.check_output([video.FFPROBE,'-v','error','-show_streams','-show_format','-of','json',str(output)]))
            self.assertAlmostEqual(float(info['format']['duration']),12,places=1)
            self.assertEqual((info['streams'][0]['width'],info['streams'][0]['height']),(720,1280))
            self.assertEqual(info['streams'][1]['codec_name'],'aac')
            subprocess.run([video.FFMPEG,'-v','error','-i',str(output),'-f','null','-'],check=True,capture_output=True)

    def test_long_demo_is_read_only_and_supports_video_seeking(self):
        before = self.db.list_diaries(2024)
        with patch.object(server, 'Database', side_effect=AssertionError('시연은 DB를 사용하지 않습니다')):
            status, page, mime = self.request('GET', '/demo/long-diary')
            self.assertEqual((status, mime), (200, 'text/html; charset=utf-8'))
            self.assertIn('1,013자'.encode(), page)
            self.assertIn(b'/demo/three-year.mp4', page)
            self.assertEqual(self.request('GET', '/demo/three-year.mp4', headers={'Range':'bytes=0-15'})[0], 206)
            self.assertEqual(self.request('GET', '/demo/three-year-poster.png')[0], 200)
            self.assertIn(b'/demo/shorts.mp4', page)
            status, body, mime, headers = self.request('GET', '/demo/shorts.mp4', headers={'Range':'bytes=0-31'})
            self.assertEqual((status, len(body), mime), (206, 32, 'video/mp4'))
            self.assertIn(b'ftyp', body)
            self.assertTrue(headers['Content-Range'].startswith('bytes 0-31/'))
            self.assertEqual(self.request('GET', '/demo/shorts-poster.png')[0], 200)
            self.assertEqual(self.request('GET', '/previews/build_shorts.py')[0], 404)
            self.assertEqual(self.request('GET', '/demo/../.env')[0], 404)
        self.assertEqual(self.db.list_diaries(2024), before)

    def test_caption_literals_and_maximum_korean_length_are_preserved(self):
        text = '가' * 64
        self.assertEqual(video._wrap_caption(text).replace('\n', ''), text)
        self.assertEqual(video._wrap_caption("100% %{n} ' : $()"), "100% %{n} ' : $()")

    @unittest.skipUnless(Path(video.FFMPEG).is_file(), 'ffmpeg-full 설치 필요')
    def test_real_mp4_has_exact_duration_korean_scene_and_audio(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'review.mp4'
            items = [{'date':'2024-11-17', 'caption':"가을 산책 100% %{n} ' :", 'image_path':server.ROOT / 'assets/demo-walk.png'}]
            video.export_video(items, output)
            info = json.loads(subprocess.check_output([video.FFPROBE, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(output)]))
            picture, sound = info['streams']
            self.assertEqual((picture['codec_name'], picture['width'], picture['height'], picture['pix_fmt']), ('h264', 720, 1280, 'yuv420p'))
            self.assertEqual(sound['codec_name'], 'aac')
            self.assertAlmostEqual(float(info['format']['duration']), 4, places=1)
            subprocess.run([video.FFMPEG, '-v', 'error', '-i', str(output), '-f', 'null', '-'], check=True, capture_output=True)
            before = output.read_bytes()
            with self.assertRaises(ValueError):
                video.export_video(items, output)
            self.assertEqual(output.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
