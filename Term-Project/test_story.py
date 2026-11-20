import io
import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

import story_api
import server
import test_app


class StoryTests(unittest.TestCase):
    setUp = test_app.DiaryTests.setUp
    request = test_app.DiaryTests.request

    def entry(self):
        return self.db.save_diary('2024-11-16', '아침에는 마음이 무거웠다. 친구와 산책한 뒤 조금 편안해졌다.')

    def test_full_long_diary_and_safe_key_use_and_validated_response(self):
        text = json.loads((Path(__file__).parent / 'demo_diaries.json').read_text())[0]['content']
        content = json.dumps({'captions':['발표 준비에 조급했던 아침','친구와 은행잎 길을 걸었다','이야기하며 마음이 편안해졌다','돌아와 하나씩 다시 시작했다']})
        response = io.BytesIO(json.dumps({'choices':[{'message':{'content':'```json\n'+content+'\n```'}}], 'credits_charged':0.7}).encode())
        opener = Mock(); opener.open.return_value = response
        with patch.object(story_api,'get_api_key',return_value='test-only-key'), patch.object(story_api,'build_opener',return_value=opener):
            result = story_api.generate_story('2024-11-17',text)
        payload = json.loads(opener.open.call_args.args[0].data)
        self.assertEqual(json.loads(payload['messages'][1]['content'])['diary'],text)
        self.assertEqual(payload['max_tokens'],800)
        self.assertEqual(result['credits_charged'],0.7)
        self.assertEqual(len(result['captions']),4)
        self.assertNotIn('test-only-key',json.dumps(payload))
        self.assertEqual(opener.open.call_count,1)

    def test_long_model_sentence_is_split_without_losing_words(self):
        sentence = '친구와 은행나무 아래를 걸었다. ' * 5
        response = io.BytesIO(json.dumps({'choices':[{'message':{'content':json.dumps({'captions':[sentence]})}}]}).encode())
        opener = Mock(); opener.open.return_value = response
        with patch.object(story_api,'get_api_key',return_value='fake-key'), patch.object(story_api,'build_opener',return_value=opener):
            result = story_api.generate_story('2024-11-17','가상 일기')
        self.assertGreater(len(result['captions']),1)
        self.assertTrue(all(len(line)<=64 for line in result['captions']))
        self.assertEqual(' '.join(result['captions']),sentence.strip())
        self.assertIsNone(result['credits_charged'])

    def test_bad_input_and_bad_or_unbounded_response(self):
        with patch.object(story_api,'get_api_key',return_value='fake-key'), patch.object(story_api,'build_opener') as factory:
            for date in (None, '2024-2-1', '2025-02-29'):
                with self.assertRaises(ValueError): story_api.generate_story(date,'일기')
            for text in (' ', None, '가'*10001):
                with self.assertRaises(ValueError): story_api.generate_story('2024-11-17',text)
            factory.assert_not_called()
            for body in (b'[]',b'{}',b'null',b'x'*(story_api.MAX_RESPONSE_SIZE+1),
                         json.dumps({'choices':[{'message':{'content':'{"captions":["'+('a'*257)+'"]}'}}]}).encode()):
                factory.return_value.open.return_value=io.BytesIO(body)
                with self.assertRaises(ValueError):story_api.generate_story('2024-11-17','가상 일기')
        for captions in ([], ['a']*9, ['가'*65], [None], ['a\nb'], ['a\rb']):
            with self.assertRaises(ValueError): story_api.validate_captions(captions)

    def test_network_failure_no_retry_and_no_secret_in_message(self):
        for error in (HTTPError('https://example.test',401,'secret-body',{},None),URLError('private details')):
            with patch.object(story_api,'get_api_key',return_value='private-key'), patch.object(story_api,'build_opener') as factory:
                factory.return_value.open.side_effect=error
                with self.assertRaises(ValueError) as caught:story_api.generate_story('2024-11-17','원문')
                self.assertNotIn('private',str(caught.exception))
                self.assertEqual(factory.return_value.open.call_count,1)

    def test_api_cache_reopen_edit_invalidation_and_delete(self):
        entry=self.entry(); data={'date':entry['date'],'content_hash':entry['content_hash'],'consent':True}
        generated={'captions':['조급했던 하루','산책하며 편안해졌다'],'credits_charged':0.5,'model':story_api.MODEL}
        with patch.object(server.story_api,'generate_story',return_value=generated) as provider:
            status,result=self.request('POST','/api/shorts/story',data)
            self.assertEqual((status,result['cached'],result['credits_charged']),(200,False,0.5))
            self.assertEqual(self.request('POST','/api/shorts/story',data)[1]['credits_charged'],0)
            self.assertEqual(provider.call_count,1)
            changed=self.db.save_diary(entry['date'],'수정한 새 이야기')
            self.assertEqual(self.request('POST','/api/shorts/story',data)[0],409)
            data['content_hash']=changed['content_hash']
            self.assertEqual(self.request('POST','/api/shorts/story',data)[0],200)
            self.assertEqual(provider.call_count,2)
        self.db.delete_diary(entry['date'])
        self.assertIsNone(self.db.get_setting('shorts_story:'+entry['date']))

    def test_consent_busy_and_midflight_changes_never_use_stale_story(self):
        entry=self.entry(); data={'date':entry['date'],'content_hash':entry['content_hash'],'consent':True}
        with patch.object(server.story_api,'generate_story') as provider:
            self.assertEqual(self.request('POST','/api/shorts/story',{**data,'consent':False})[0],400)
            server.STORY_LOCK.acquire()
            try:self.assertEqual(self.request('POST','/api/shorts/story',data)[0],409)
            finally:server.STORY_LOCK.release()
            provider.assert_not_called()
            def changed(*args):
                self.db.save_diary(entry['date'],'구성 중 수정한 일기')
                return {'captions':['이전 이야기'],'credits_charged':0.5}
            provider.side_effect=changed
            self.assertEqual(self.request('POST','/api/shorts/story',data)[0],409)
        self.assertFalse(server.STORY_LOCK.locked())
        self.assertIsNone(self.db.get_setting('shorts_story:'+entry['date']))
        self.assertEqual(self.db.get_diary(entry['date'])['content'],'구성 중 수정한 일기')


if __name__=='__main__':unittest.main()


class StoryOverflowTests(unittest.TestCase):
    def test_overlong_paid_response_is_kept_in_scene_order(self):
        lines = [f'{i}번째 장면 ' + '가나다라 ' * 30 for i in range(1, 7)]
        response = io.BytesIO(json.dumps({'choices':[{'message':{'content':json.dumps({'captions':lines})}}]}).encode())
        opener = Mock(); opener.open.return_value = response
        with patch.object(story_api,'get_api_key',return_value='fake-key'), patch.object(story_api,'build_opener',return_value=opener):
            result = story_api.generate_story('2024-11-17','가상 일기')
        self.assertTrue(result['shortened'])
        self.assertEqual(len(result['captions']), 6)
        self.assertTrue(all(len(c) <= 64 for c in result['captions']))
        self.assertEqual([c.split('번째')[0] for c in result['captions']], [str(i) for i in range(1, 7)])
        self.assertEqual(opener.open.call_count, 1)
