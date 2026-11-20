import json
import unittest
from pathlib import Path
from unittest.mock import patch

import server
import test_app


class EnhancementTests(unittest.TestCase):
    # Reuse the existing isolated database and HTTP request harness.
    setUp = test_app.DiaryTests.setUp
    request = test_app.DiaryTests.request
    def entry_with_image(self, year=2024):
        entry = self.db.save_diary(f'{year}-11-17', '아침에는 공부하고 오후에는 친구와 걸었다. 저녁에는 차를 마셨다.')
        folder = Path(self.db.db_path).parent / 'images'; folder.mkdir(exist_ok=True)
        name = f'{year:032x}.png'
        (folder/name).write_bytes((server.ROOT/'assets/demo-walk.png').read_bytes())
        self.db.attach_image(entry['date'], entry['content_hash'], '/media/'+name)
        return self.db.get_diary(entry['date'])

    def test_scene_cache_reuse_serving_and_body_change(self):
        entry = self.entry_with_image()
        data = {**entry, 'caption': '친구와 은행나무 아래를 걸었다', 'consent': True}
        with patch.object(server.image_api,'generate_image',return_value=(b'picture','png',15)) as provider:
            status, scene = self.request('POST','/api/shorts/scene',data)
            self.assertEqual(status,200)
            self.assertEqual(self.request('POST','/api/shorts/scene',data)[1]['credits_charged'],0)
            self.assertEqual(provider.call_count,1)
            self.assertEqual(provider.call_args.kwargs['scene'],data['caption'])
            self.assertEqual(self.request('GET',scene['url'])[1],b'picture')
            self.db.save_diary(entry['date'],'수정된 일기')
            self.assertEqual(self.request('POST','/api/shorts/scene',data)[0],409)
            self.assertEqual(provider.call_count,1)
        self.db.delete_diary(entry['date'])
        self.assertFalse(self.db.has_image(scene['url']))

    def test_scene_failure_preserves_previous_pictures_and_consent_guard(self):
        entry = self.entry_with_image(); data={**entry,'caption':'아침에 공부했다','consent':True}
        with patch.object(server.image_api,'generate_image',return_value=(b'first','png',15)) as provider:
            self.assertEqual(self.request('POST','/api/shorts/scene',{**data,'consent':False})[0],400)
            self.assertEqual(provider.call_count,0)
            first=self.request('POST','/api/shorts/scene',data)[1]
            provider.side_effect=ValueError('연결 실패')
            self.assertEqual(self.request('POST','/api/shorts/scene',{**data,'caption':'저녁에 차를 마셨다'})[0],400)
            self.assertEqual(self.request('POST','/api/shorts/scene',data)[1]['url'],first['url'])
            self.assertEqual(provider.call_count,2)
        self.assertEqual(self.db.get_diary(entry['date'])['content'],entry['content'])

    def test_day_uses_three_scene_pictures_and_history_survives_edit(self):
        entry = self.entry_with_image(); captions=['아침 공부','친구와 산책','저녁 차']
        with patch.object(server.image_api,'generate_image',return_value=(b'image','png',15)):
            urls=[self.request('POST','/api/shorts/scene',{**entry,'caption':c,'consent':True})[1]['url'] for c in captions]
        def encode(items,path,**kwargs):
            self.assertEqual([i['image_path'].name for i in items],[u.split('/')[-1] for u in urls]); path.write_bytes(b'video')
        with patch.object(server,'export_video',side_effect=encode):
            status, video=self.request('POST','/api/shorts',{'items':[entry],'captions':captions,'scene_images':True})
        self.assertEqual(status,200)
        self.assertEqual(self.request('GET','/api/videos?date='+entry['date'])[1]['videos'][0]['stale'],False)
        self.db.save_diary(entry['date'],'나중에 수정한 일기')
        saved=self.request('GET','/api/videos?date='+entry['date'])[1]['videos'][0]
        self.assertTrue(saved['stale']); self.assertEqual(saved['url'],video['url'])
        self.db.delete_diary(entry['date'])
        self.assertEqual(len(self.db.list_videos(entry['date'])),1)

    def test_three_year_orders_reuses_and_requires_all_sources_before_paid_calls(self):
        entries=[self.entry_with_image(y) for y in (2024,2025,2026)]
        stories={'captions':['아침 공부','친구와 산책','저녁 차']}
        def encode(items,path,**kwargs):
            # v2: title card, then per year a year card followed by that year's opening and closing scenes.
            self.assertEqual([i['title'] if i.get('card') else i['date'] for i in items],
                             ['2024 → 2026'] + [x for e in entries for x in (e['date'][:4], e['date'], e['date'])] + ['같은 날, 세 해'])
            self.assertEqual([i['subtitle'] for i in items if i.get('card') and not i.get('ending')][1:],
                             ['2024년 11월 17일', '1년 후 · 2025년 11월 17일', '2년 후 · 2026년 11월 17일'])
            self.assertEqual(items[-1]['labels'], ['2024', '2025', '2026'])
            self.assertEqual([i['caption'] for i in items if not i.get('card')],['아침 공부','저녁 차']*3)
            path.write_bytes(b'video')
        with patch.object(server,'prepare_story',return_value=(200,stories)) as story, patch.object(server,'export_video',side_effect=encode), patch.object(server.image_api,'generate_image') as images:
            status, movie=self.request('POST','/api/three-year-video',{'items':entries,'consent':True})
            self.assertEqual(status,200); self.assertEqual(movie['kind'],'three-year'); self.assertEqual(movie['seconds'],24+2.5+1.5*3+3.5)
            images.assert_not_called(); self.assertEqual(story.call_count,3)
            story.reset_mock()
            self.db.save_diary(entries[1]['date'],'수정한 기록')
            self.assertEqual(self.request('POST','/api/three-year-video',{'items':entries,'consent':True})[0],409)
            story.assert_not_called()
            self.assertEqual(self.request('POST','/api/three-year-video',{'items':entries[::-1],'consent':True})[0],400)

    def test_six_captions_keep_middle_picture_until_final_scene(self):
        entry = self.entry_with_image(); captions=['아침 준비','밖으로 나감','은행잎 길','친구와 대화','돌아오는 길','집에서 마무리']
        urls = {}
        with patch.object(server.image_api,'generate_image',return_value=(b'image','png',15)):
            for i in (0,2,5):
                urls[i]=self.request('POST','/api/shorts/scene',{**entry,'caption':captions[i],'consent':True})[1]['url'].split('/')[-1]
        def encode(items,path,**kwargs):
            self.assertEqual([i['image_path'].name for i in items],[urls[i] for i in (0,0,2,2,2,5)])
            path.write_bytes(b'video')
        with patch.object(server,'export_video',side_effect=encode):
            self.assertEqual(self.request('POST','/api/shorts',{'items':[entry],'captions':captions,'scene_images':True})[0],200)



class ReviewFixTests(unittest.TestCase):
    setUp = test_app.DiaryTests.setUp
    request = test_app.DiaryTests.request
    entry_with_image = EnhancementTests.entry_with_image

    def test_nonexistent_date_error_is_korean(self):
        status, body = self.request('GET', '/api/videos?date=2025-02-29')
        self.assertEqual(status, 400)
        self.assertIn('날짜', body['error'])

    def test_scene_check_only_is_free_and_reports_cache(self):
        entry = self.entry_with_image()
        data = {**entry, 'caption': '친구와 산책'}
        with patch.object(server.image_api, 'generate_image', return_value=(b'image', 'png', 15)) as provider:
            self.assertEqual(self.request('POST', '/api/shorts/scene', {**data, 'check_only': True}), (200, {'cached': False}))
            self.request('POST', '/api/shorts/scene', {**data, 'consent': True})
            self.assertEqual(self.request('POST', '/api/shorts/scene', {**data, 'check_only': True}), (200, {'cached': True}))
            self.assertEqual(provider.call_count, 1)
        self.db.save_diary(entry['date'], '바뀐 본문')
        self.assertEqual(self.request('POST', '/api/shorts/scene', {**data, 'check_only': True})[0], 409)

    def test_edited_captions_are_reused_without_new_story_call(self):
        entry = self.entry_with_image()
        ai = {'captions': ['아침 공부', '저녁 차'], 'credits_charged': None, 'model': 'm', 'shortened': False}
        with patch.object(server.story_api, 'generate_story', return_value=ai) as provider:
            self.request('POST', '/api/shorts/story', {**entry, 'consent': True})
            edited = ['아침에 집중해서 공부했다', '저녁 차']
            with patch.object(server, 'export_video', side_effect=lambda items, path, **k: path.write_bytes(b'v')):
                self.assertEqual(self.request('POST', '/api/shorts', {'items': [entry], 'captions': edited})[0], 200)
            status, story = self.request('POST', '/api/shorts/story', {**entry, 'consent': True})
            self.assertEqual((status, story['captions'], story['edited']), (200, edited, True))
            self.assertEqual(provider.call_count, 1)
        self.assertEqual(self.db.get_diary(entry['date'])['content'], entry['content'])

    def test_three_year_story_failure_is_marked_as_possibly_charged(self):
        entries = [self.entry_with_image(y) for y in (2024, 2025, 2026)]
        with patch.object(server.story_api, 'generate_story', side_effect=ValueError('응답 오류')):
            status, body = self.request('POST', '/api/three-year-video', {'items': entries, 'consent': True})
        self.assertEqual((status, body.get('may_charge')), (400, True))
        self.assertEqual(self.request('POST', '/api/three-year-video', {'items': entries[::-1], 'consent': True})[1].get('may_charge'), None)
