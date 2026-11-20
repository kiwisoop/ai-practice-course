"""v2 additions: FFmpeg discovery, title/year cards, and real card rendering. No paid API calls."""
import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

import hashlib
import sqlite3
from unittest.mock import patch

import server
import test_app
import test_enhancements
import video_export as video


class FFmpegDiscoveryTests(unittest.TestCase):
    def tools(self, folder, name):
        directory = Path(folder) / name
        directory.mkdir()
        for tool in ('ffmpeg', 'ffprobe'):
            path = directory / tool
            path.write_text('#!/bin/sh\n')
            path.chmod(path.stat().st_mode | stat.S_IEXEC)
        return str(directory / 'ffmpeg')

    def test_env_then_candidates_then_path_and_drawtext_required(self):
        with tempfile.TemporaryDirectory() as folder:
            env_tool, full, plain, on_path = (self.tools(folder, n) for n in ('env', 'full', 'plain', 'path'))
            def found(environ, candidates, ok):
                return video.find_ffmpeg(environ, candidates, which=lambda _: on_path, has_drawtext=lambda p: p in ok)[0]
            self.assertEqual(found({'FFMPEG': env_tool}, [full], {env_tool, full}), env_tool)
            self.assertEqual(found({}, [plain, full], {full}), full, 'skip builds without subtitles')
            self.assertEqual(found({}, [], {on_path}), on_path)
            self.assertEqual(found({}, [plain], set()), plain, 'best guess when none can draw text')
        self.assertEqual(video.find_ffmpeg({}, [], which=lambda _: None), ('ffmpeg', 'ffprobe'))


class CardTests(unittest.TestCase):
    def scene(self):
        return {'date': '2024-11-17', 'caption': '산책', 'image_path': str(Path(__file__).parent / 'assets/demo-walk.png')}

    def test_cards_do_not_count_as_scenes_and_are_validated(self):
        video._validate_items([video.make_card('제목', '부제', 2.5)] + [self.scene()] * 8)
        bad = [[video.make_card('제목')], [video.make_card('제목')] * 6 + [self.scene()],
               [video.make_card('', '부제'), self.scene()], [video.make_card('가' * 25), self.scene()],
               [video.make_card('제목', '줄\n바꿈'), self.scene()], [video.make_card('제목', '', 0.5), self.scene()],
               [video.make_card('제목', '', 1.01), self.scene()], [{**video.make_card('제목'), 'seconds': True}, self.scene()],
               [self.scene()] * 9]
        for items in bad:
            with self.subTest(items=len(items)), self.assertRaises(ValueError):
                video._validate_items(items)

    def test_caption_phrases_keep_all_text_and_reveal_in_order(self):
        for caption in ('친구와 은행나무 길을 걸었다', '가' * 64, 'abc ' * 16, '오늘 아침에는 늦잠을 자서 버스를 놓쳤지만 덕분에 천천히 걸으며 하늘을 볼 수 있었다'):
            with self.subTest(caption=caption[:10]):
                lines = video.caption_lines(caption)
                self.assertEqual(''.join(lines).replace(' ', ''), caption.replace(' ', ''))
                self.assertTrue(all(video._display_width(line) <= 22 for line in lines))
                times = video.reveal_times(len(lines), video.scene_duration(caption))
                self.assertEqual(times, sorted(times))
                # Every phrase is fully visible well before the scene ends.
                self.assertLess(times[-1] + video.REVEAL_SECONDS, video.scene_duration(caption) - 0.5)

    def test_ending_validation(self):
        image = self.scene()['image_path']
        video._validate_items([video.make_ending('같은 날, 세 해', [image] * 3, ['2024', '2025', '2026']), self.scene()])
        for images, labels in (([image] * 3, ['2024', '2025']), ([image], ['2024']), ([image, '/nope.png'], ['2024', '2025']),
                               ([image] * 2, ['2024', '가' * 9]), ([image] * 2, ['2024', ''])):
            with self.subTest(labels=labels), self.assertRaises(ValueError):
                video._validate_items([video.make_ending('끝', images, labels), self.scene()])

    def test_duration_includes_cards(self):
        items = [video.make_card('제목', '', 2.5), self.scene(), video.make_card('2024', '', 1.5)]
        self.assertEqual(sum(video.item_duration(i, True) for i in items), 2.5 + 4 + 1.5)

    @unittest.skipUnless(Path(video.FFMPEG).is_file(), 'ffmpeg 필요')
    def test_real_mp4_with_cards_has_exact_length_and_audio(self):
        items = [video.make_card('2024 → 2026', '11월 17일 · 같은 날, 세 해의 기록', 2.5),
                 video.make_card('2024', '2024년 11월 17일', 1.5), self.scene(),
                 video.make_ending('같은 날, 세 해', [self.scene()['image_path']] * 3, ['2024', '2025', '2026'])]
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'cards.mp4'
            video.export_video(items, output, shorts=True)
            info = json.loads(subprocess.check_output([video.FFPROBE, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(output)]))
            streams = {s['codec_type']: s for s in info['streams']}
            self.assertEqual((streams['video']['width'], streams['video']['height']), (720, 1280))
            self.assertIn('audio', streams)
            self.assertAlmostEqual(float(info['format']['duration']), 11.5, delta=0.1)
            subprocess.run([video.FFMPEG, '-v', 'error', '-i', str(output), '-f', 'null', '-'], check=True, capture_output=True)


class DemoDataTests(unittest.TestCase):
    """New virtual demo diaries: safe upgrade of the previous demo text and AI-free demo captions."""
    setUp = test_app.DiaryTests.setUp
    request = test_app.DiaryTests.request

    def test_previous_demo_upgraded_only_when_untouched(self):
        previous = json.loads((Path(__file__).parent / 'demo_diaries_previous.json').read_text(encoding='utf-8'))
        current = json.loads((Path(__file__).parent / 'demo_diaries.json').read_text(encoding='utf-8'))
        conn = sqlite3.connect(self.db.db_path)
        for item in previous:
            digest = hashlib.sha256(item['content'].encode()).hexdigest()
            conn.execute('INSERT INTO diary (date, content, content_hash, image_path, is_demo, updated_at) VALUES (?, ?, ?, ?, 1, ?)',
                         (item['date'], item['content'], digest, item['image_path'], 'x'))
        conn.commit(); conn.close()
        self.db.save_diary('2025-11-17', '내가 고쳐 쓴 기록')  # edited by the user: is_demo becomes 0
        self.db.load_demo_data()
        self.assertEqual(self.db.get_diary('2024-11-17')['content'], current[0]['content'])
        self.assertEqual(self.db.get_diary('2025-11-17')['content'], '내가 고쳐 쓴 기록')
        self.assertEqual(self.db.get_diary('2026-11-17')['content'], current[2]['content'])
        self.assertIsNone(self.db.get_setting('shorts_story:2025-11-17'), '사용자 기록에는 시연 자막을 넣지 않음')

    def test_demo_captions_need_no_ai_call_and_respect_existing_story(self):
        self.db.load_demo_data()
        entry = self.db.get_diary('2024-11-17')
        with patch.object(server.story_api, 'generate_story') as provider:
            status, story = self.request('POST', '/api/shorts/story', {**entry, 'consent': True})
        provider.assert_not_called()
        self.assertEqual((status, story['demo'], story['credits_charged']), (200, True, 0))
        self.assertEqual(story['captions'][0], '리허설 첫 소절부터 박자를 놓쳤다')
        custom = json.dumps({'version': 1, 'content_hash': entry['content_hash'], 'captions': ['내가 고친 문장'], 'edited': True}, ensure_ascii=False)
        self.db.set_setting('shorts_story:2024-11-17', custom)
        self.db.load_demo_data()
        self.assertEqual(self.db.get_setting('shorts_story:2024-11-17'), custom)


class MusicTests(unittest.TestCase):
    """Background music choice, ending crossfade and CC BY credit. No paid API calls."""
    setUp = test_app.DiaryTests.setUp
    request = test_app.DiaryTests.request

    def test_tracks_exist_with_credit_and_ending_switches_to_another_track(self):
        for key, (path, label, credit) in video.MUSIC.items():
            with self.subTest(key=key):
                self.assertTrue((video.MUSIC_DIR / path).is_file())
                self.assertTrue(label and credit)
        self.assertIn(video.DEFAULT_MUSIC, video.MUSIC)
        for key in video.MUSIC:
            self.assertNotEqual(video.ending_music(key), key)

    def test_filter_crossfades_only_with_switch(self):
        self.assertNotIn('[2:a]', video.music_filter(20))
        graph = video.music_filter(30, 26.5)
        self.assertIn('atrim=0:28.0', graph)
        self.assertIn('adelay=delays=26500:all=1', graph)
        self.assertIn('loudnorm', graph)

    def test_invalid_music_rejected_before_any_paid_call(self):
        with patch.object(server.story_api, 'generate_story') as story, patch.object(server.image_api, 'generate_image') as image:
            status, body = self.request('POST', '/api/three-year-video', {'items': [], 'consent': True, 'music': '../../.env'})
        self.assertEqual(status, 400)
        story.assert_not_called(); image.assert_not_called()

    def test_settings_list_tracks_and_day_video_records_music(self):
        status, settings = self.request('GET', '/api/settings')
        self.assertEqual(settings['music']['default'], video.DEFAULT_MUSIC)
        self.assertEqual({t['id'] for t in settings['music']['tracks']}, set(video.MUSIC))
        entry = test_enhancements.EnhancementTests.entry_with_image(self)
        seen = {}
        def encode(items, path, **kwargs):
            seen.update(kwargs); path.write_bytes(b'video')
        with patch.object(server, 'export_video', side_effect=encode):
            status, movie = self.request('POST', '/api/shorts', {'items': [entry], 'captions': ['아침 산책'], 'music': 'calm'})
        self.assertEqual((status, seen['music'], seen['switch_music']), (200, 'calm', None))
        self.assertEqual(movie['music'], [video.MUSIC['calm'][2]])
        self.assertEqual(self.request('POST', '/api/shorts', {'items': [entry], 'captions': ['아침 산책'], 'music': 'nope'})[0], 400)

    @unittest.skipUnless(Path(video.FFMPEG).is_file(), 'ffmpeg 필요')
    def test_real_mp4_with_ending_switch_has_audio_length_and_credit(self):
        scene = {'date': '2024-11-17', 'caption': '산책', 'image_path': str(Path(__file__).parent / 'assets/demo-walk.png')}
        items = [scene, video.make_ending('같은 날, 세 해', [scene['image_path']] * 2, ['2024', '2025'])]
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'music.mp4'
            video.export_video(items, output, shorts=True, music='calm', switch_music='hopeful')
            info = json.loads(subprocess.check_output([video.FFPROBE, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(output)]))
            self.assertAlmostEqual(float(info['format']['duration']), 7.5, delta=0.1)
            self.assertIn('audio', [s['codec_type'] for s in info['streams']])
            comment = info['format'].get('tags', {}).get('comment', '')
            self.assertIn('Jason Shaw', comment); self.assertIn('Squire Tuck', comment)


if __name__ == '__main__':
    unittest.main()
