"""1인용 로컬 다이어리 서버. 개인 기록과 요청 내용을 로그에 남기지 않는다."""
import json
import re
import threading
import uuid
import hashlib
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

from storage import Database, KST
import image_api
import story_api
import narration
from video_export import export_video, item_duration, make_card, make_ending, MUSIC, DEFAULT_MUSIC, ending_music

ROOT = Path(__file__).resolve().parent
IMAGE_LOCK = threading.Lock()
VIDEO_LOCK = threading.Lock()
STORY_LOCK = threading.Lock()
STORY_VERSION = 1
MEDIA_PATTERN = re.compile(r'/media/[0-9a-f]{32}\.(png|jpg|webp)')
FILES = {
    '/assets/MaruBuri-Regular.woff2': ('assets/MaruBuri-Regular.woff2', 'font/woff2'),
    '/assets/MaruBuri-SemiBold.woff2': ('assets/MaruBuri-SemiBold.woff2', 'font/woff2'),
    '/': ('static/index.html', 'text/html; charset=utf-8'),
    '/style.css': ('static/style.css', 'text/css; charset=utf-8'),
    '/app.js': ('static/app.js', 'application/javascript; charset=utf-8'),
    '/demo/long-diary': ('static/long-diary-demo.html', 'text/html; charset=utf-8'),
    '/demo/shorts': ('static/long-diary-demo.html', 'text/html; charset=utf-8'),
    '/demo/shorts-poster.png': ('previews/example-day-poster.png', 'image/png'),
    '/demo/three-year-poster.png': ('previews/example-three-year-poster.png', 'image/png'),
    '/demo/long-diary-poster.png': ('previews/shorts-2.png', 'image/png'),
    **{f'/assets/demo-{name}.png': (f'assets/demo-{name}.png', 'image/png')
       for name in ('walk', 'tea', 'diary')},
}


# Read-only example videos rendered from the virtual demo diaries (no personal data).
DEMO_VIDEOS = {
    '/demo/shorts.mp4': 'previews/example-day.mp4',
    '/demo/three-year.mp4': 'previews/example-three-year.mp4',
    '/demo/long-diary.mp4': 'previews/long-diary-shorts.mp4',
}


def media_file(db, url):
    if not isinstance(url, str) or not MEDIA_PATTERN.fullmatch(url):
        return None
    return Path(db.db_path).parent / 'images' / url.rsplit('/', 1)[1]


def create_image(db, data):
    if data.get('consent') is not True:
        raise ValueError('일기 전송과 이미지 생성 비용 안내에 동의해 주세요.')
    if not isinstance(data.get('regenerate', False), bool):
        raise ValueError('이미지 요청 형식이 올바르지 않습니다.')
    if not IMAGE_LOCK.acquire(blocking=False):
        return 409, {'error': '다른 그림을 생성하고 있어요. 완료될 때까지 기다려 주세요.'}
    try:
        entry = db.get_diary(data.get('date'))
        if not entry['content']:
            raise ValueError('먼저 일기를 저장해 주세요.')
        if data.get('content_hash') != entry['content_hash']:
            return 409, {'error': '일기가 변경됐습니다. 최신 기록을 확인해 주세요.'}
        previous = media_file(db, entry['image_path'])
        if previous and previous.is_file() and not entry['image_stale'] and not data.get('regenerate', False):
            return 200, {'entry': entry, 'cached': True, 'credits_charged': 0}
        body, extension, credits = image_api.generate_image(entry['date'], entry['content'])
        if extension not in ('png', 'jpg', 'webp'):
            raise ValueError('지원하지 않는 이미지 형식입니다.')
        folder = Path(db.db_path).parent / 'images'
        folder.mkdir(mode=0o700, exist_ok=True)
        name = uuid.uuid4().hex + '.' + extension
        destination = folder / name
        created = False
        try:
            with destination.open('xb') as image:
                created = True
                image.write(body)
            url = '/media/' + name
            if not db.attach_image(entry['date'], entry['content_hash'], url):
                destination.unlink()
                return 409, {'error': '생성 중 일기가 바뀌거나 삭제되어 그림을 연결하지 않았습니다. 원래 기록은 유지됩니다.'}
        except Exception:
            if created:
                destination.unlink(missing_ok=True)
            raise
        return 200, {'entry': db.get_diary(entry['date']), 'cached': False, 'credits_charged': credits}
    finally:
        IMAGE_LOCK.release()


def prepare_story(db, data):
    if data.get('consent') is not True:
        raise ValueError('일기를 학교 AI에 보내 이야기 구성에 사용하는 안내를 확인해 주세요.')
    if not STORY_LOCK.acquire(blocking=False):
        return 409, {'error': '다른 이야기를 구성하고 있어요. 잠시 기다려 주세요.'}
    try:
        entry = db.get_diary(data.get('date'))
        if not entry['content'] or entry['content_hash'] != data.get('content_hash'):
            return 409, {'error': '일기가 바뀌었습니다. 저장된 최신 일기를 확인해 주세요.'}
        key = 'shorts_story:' + entry['date']
        try:
            cached = json.loads(db.get_setting(key, 'null'))
        except (ValueError, TypeError):
            cached = None
        if (isinstance(cached, dict) and cached.get('version') == STORY_VERSION
                and cached.get('content_hash') == entry['content_hash']
                and isinstance(cached.get('captions'), list) and 1 <= len(cached['captions']) <= 8
                and all(isinstance(line, str) and 1 <= len(line.strip()) <= 64 and '\n' not in line and '\r' not in line for line in cached['captions'])):
            return 200, {'captions': cached['captions'], 'cached': True, 'credits_charged': 0, 'edited': cached.get('edited') is True,
                         'demo': cached.get('demo') is True}
        story = story_api.generate_story(entry['date'], entry['content'])
        if db.get_diary(entry['date'])['content_hash'] != entry['content_hash']:
            return 409, {'error': '구성 중 일기가 바뀌어 결과를 연결하지 않았습니다. 원본은 유지됩니다.'}
        db.set_setting(key, json.dumps({'version': STORY_VERSION, 'content_hash': entry['content_hash'],
                                       'captions': story['captions']}, ensure_ascii=False))
        return 200, {**story, 'cached': False}
    finally:
        STORY_LOCK.release()


def scene_key(entry, caption):
    digest = hashlib.sha256((entry['content_hash'] + '\n' + caption).encode()).hexdigest()
    return 'shorts_scene:' + entry['date'] + ':' + digest


def scene_image(db, entry, caption):
    url = db.get_setting(scene_key(entry, caption))
    file = media_file(db, url)
    return (url, file) if file and file.is_file() and not file.is_symlink() else (None, None)


def create_scene(db, data):
    if data.get('check_only') is True:
        # Free lookup so the page can state how many new (paid) pictures a request needs.
        caption = story_api.validate_captions([data.get('caption')])[0]
        entry = db.get_diary(data.get('date'))
        if not entry['content'] or entry['content_hash'] != data.get('content_hash'):
            return 409, {'error': '일기가 변경됐습니다. 저장된 내용을 확인해 주세요.'}
        return 200, {'cached': scene_image(db, entry, caption)[1] is not None}
    if data.get('consent') is not True:
        raise ValueError('장면 그림의 일기 전송과 생성 비용을 확인해 주세요.')
    caption = story_api.validate_captions([data.get('caption')])[0]
    entry = db.get_diary(data.get('date'))
    if not entry['content'] or entry['content_hash'] != data.get('content_hash'):
        return 409, {'error': '일기가 변경됐습니다. 저장된 내용을 확인해 주세요.'}
    if not IMAGE_LOCK.acquire(blocking=False):
        return 409, {'error': '다른 그림을 생성 중입니다.'}
    try:
        url, file = scene_image(db, entry, caption)
        if file:
            return 200, {'url': url, 'cached': True, 'credits_charged': 0}
        body, extension, credits = image_api.generate_image(entry['date'], entry['content'], scene=caption)
        if extension not in ('png', 'jpg', 'webp'):
            raise ValueError('지원하지 않는 이미지 형식입니다.')
        if db.get_diary(entry['date'])['content_hash'] != entry['content_hash']:
            return 409, {'error': '생성 중 일기가 바뀌어 그림을 연결하지 않았습니다. 사용량을 확인해 주세요.'}
        folder = Path(db.db_path).parent / 'images'
        folder.mkdir(mode=0o700, exist_ok=True)
        name = uuid.uuid4().hex + '.' + extension
        with (folder / name).open('xb') as output:
            output.write(body)
        url = '/media/' + name
        db.set_setting(scene_key(entry, caption), url)
        return 200, {'url': url, 'cached': False, 'credits_charged': credits}
    finally:
        IMAGE_LOCK.release()


def create_three_year_video(db, data):
    music = chosen_music(data)  # validate before any paid story call
    narrate = chosen_narration(data)
    selection = data.get('items')
    if not isinstance(selection, list) or len(selection) != 3 or any(not isinstance(i, dict) for i in selection):
        raise ValueError('같은 날짜의 세 해 일기를 선택해 주세요.')
    entries = [db.get_diary(i.get('date')) for i in selection]
    dates = [e['date'] for e in entries]
    years = [int(d[:4]) for d in dates]
    if years != list(range(years[0], years[0]+3)) or len({d[5:] for d in dates}) != 1:
        raise ValueError('연속된 세 해의 같은 월·일만 연결할 수 있어요.')
    if any(not e['content'] or e['content_hash'] != i.get('content_hash') for e, i in zip(entries, selection)):
        return 409, {'error': '세 해의 일기를 모두 저장하고 최신 내용을 확인해 주세요.'}
    for entry in entries:
        image = media_file(db, entry['image_path'])
        if entry['image_stale'] or not image or not image.is_file() or image.is_symlink():
            raise ValueError('각 연도의 최신 수채화를 먼저 만들어 주세요.')
    month, day = int(dates[0][5:7]), int(dates[0][8:10])
    # Title card, then a year card before each year's own scenes (no AI call, text only).
    items = [make_card(f'{years[0]} → {years[2]}', f'{month}월 {day}일 · 같은 날, 세 해의 기록', 2.5)]
    for offset, entry in enumerate(entries):
        later = f'{offset}년 후 · ' if offset else ''
        items.append(make_card(entry['date'][:4], f"{later}{entry['date'][:4]}년 {month}월 {day}일", 1.5))
        try:
            status, story = prepare_story(db, {**entry, 'consent': data.get('consent')})
        except ValueError as error:
            return 400, {'error': str(error), 'may_charge': True}
        if status != 200:
            return status, {**story, 'may_charge': True}
        captions = story['captions']
        # Reuse each year's opening and closing scene, without inventing comparisons.
        for index in dict.fromkeys((0, len(captions)-1)):
            caption = captions[index]
            _, image = scene_image(db, entry, caption)
            if image is None:
                image = media_file(db, entry['image_path'])
                if entry['image_stale'] or not image:
                    raise ValueError('각 연도의 최신 수채화를 먼저 만들어 주세요.')
            if not image.is_file() or image.is_symlink():
                raise ValueError('저장된 그림을 찾지 못했습니다.')
            items.append({'date': entry['date'], 'caption': caption, 'image_path': image})
    if any(db.get_diary(e['date'])['content_hash'] != e['content_hash'] for e in entries):
        return 409, {'error': '구성 중 일기가 바뀌었습니다. 다시 확인해 주세요.'}
    # Closing montage: the three years' watercolors side by side (already checked above, no new pictures).
    items.append(make_ending('같은 날, 세 해', [media_file(db, e['image_path']) for e in entries], [e['date'][:4] for e in entries]))
    return render_and_save_video(db, items, {e['date']: e['content_hash'] for e in entries}, 'three-year', True,
                                 music, ending_music(music), narrate)


def chosen_music(data):
    music = data.get('music', DEFAULT_MUSIC)
    if music not in MUSIC:
        raise ValueError('배경음악 선택을 확인해 주세요.')
    return music


def chosen_narration(data):
    """Narration is opt-in per request and checked before any paid call."""
    value = data.get('narration', False)
    if not isinstance(value, bool):
        raise ValueError('내레이션 선택을 확인해 주세요.')
    if value and not narration.available():
        raise ValueError('내레이션 음성 모델이 설치되지 않았어요. 내레이션을 끄고 다시 시도해 주세요.')
    return value


def render_and_save_video(db, items, sources, kind, shorts, music=DEFAULT_MUSIC, switch_music=None, narrate=False):
    if not VIDEO_LOCK.acquire(blocking=False):
        return 409, {'error': '다른 영상을 만들고 있어요. 잠시 기다려 주세요.'}
    try:
        folder = Path(db.db_path).parent / 'videos'
        folder.mkdir(exist_ok=True)
        filename = uuid.uuid4().hex + '.mp4'
        output = folder / filename
        if narrate and shorts:
            # Local voice (no credits); cached per sentence, so remaking a video reuses the same audio.
            scenes = [item for item in items if item.get('card') is not True]
            voices = narration.synthesize([item['caption'] for item in scenes], Path(db.db_path).parent / 'narration')
            items = [dict(item) for item in items]
            scene_items = iter(item for item in items if item.get('card') is not True)
            for voice in voices:
                next(scene_items)['narration'] = voice
        try:
            export_video(items, output, **({'shorts': True} if shorts else {}), music=music, switch_music=switch_music)
        except Exception:
            output.unlink(missing_ok=True)
            raise
        metadata = {'url': '/videos/' + filename, 'seconds': sum(item_duration(i, shorts) for i in items),
                    'sources': sources, 'kind': kind, 'created_at': datetime.now(KST).isoformat(),
                    'music': [MUSIC[name][2] for name in dict.fromkeys(m for m in (music, switch_music) if m)]}
        if narrate and shorts:
            metadata['voice'] = narration.CREDIT
        db.save_video(filename[:-4], metadata)
        return 200, metadata
    finally:
        VIDEO_LOCK.release()


def create_video(db, data, shorts=False):
    selection = data.get('items')
    if not isinstance(selection, list) or not 1 <= len(selection) <= 8:
        raise ValueError('그림이 있는 일기를 1~8개 선택해 주세요.')
    if shorts:
        captions = data.get('captions')
        if (len(selection) != 1 or not isinstance(captions, list) or not 1 <= len(captions) <= 8
                or any(not isinstance(caption, str) or not caption.strip() or len(caption) > 64 or '\n' in caption or '\r' in caption for caption in captions)):
            raise ValueError('일기 하나와 1~8개의 자막(장면당 64자 이내)을 확인해 주세요.')
    items = []
    seen = set()
    for item in selection:
        if not isinstance(item, dict):
            raise ValueError('영상 선택 형식이 올바르지 않습니다.')
        entry = db.get_diary(item.get('date'))
        caption = captions[0] if shorts else item.get('caption')
        if entry['date'] in seen or not entry['content'] or not isinstance(caption, str) or len(caption) > 64:
            raise ValueError('일기 선택과 자막(64자 이내)을 확인해 주세요.')
        seen.add(entry['date'])
        if entry['content_hash'] != item.get('content_hash') or entry['image_stale']:
            raise ValueError('선택한 일기가 변경됐거나 그림이 이전 내용입니다. 확인 후 다시 선택해 주세요.')
        image = media_file(db, entry['image_path'])
        if entry['image_path'] in FILES:
            image = ROOT / FILES[entry['image_path']][0]
        if not image or not image.is_file() or image.is_symlink():
            raise ValueError('먼저 선택한 일기의 그림을 만들어 주세요.')
        items.append({'date': entry['date'], 'caption': caption, 'image_path': image})
    if shorts:
        items = [{**items[0], 'caption': caption.strip()} for caption in captions]
        if data.get('scene_images') is True:
            # At most three pictures, reused in order across the complete story.
            anchors = sorted({0, (len(captions)-1)//2, len(captions)-1})
            for index, item in enumerate(items):
                anchor = max(a for a in anchors if a <= index)
                _, image = scene_image(db, entry, captions[anchor].strip())
                if image is None:
                    raise ValueError('이 이야기의 장면 그림을 먼저 준비해 주세요.')
                item['image_path'] = image
    status, result = render_and_save_video(db, items, {i['date']: i['content_hash'] for i in selection}, 'day' if shorts else 'memory', shorts,
                                           chosen_music(data), None, chosen_narration(data))
    if shorts and status == 200:
        remember_edited_story(db, entry, [caption.strip() for caption in captions])
    return status, result


def remember_edited_story(db, entry, captions):
    """Keep the captions used in a finished day video so reopening and the 3-year video reuse them."""
    key = 'shorts_story:' + entry['date']
    try:
        cached = json.loads(db.get_setting(key, 'null'))
    except (ValueError, TypeError):
        cached = None
    if not isinstance(cached, dict) or cached.get('content_hash') != entry['content_hash'] or cached.get('captions') == captions:
        return
    if db.get_diary(entry['date'])['content_hash'] != entry['content_hash']:
        return
    db.set_setting(key, json.dumps({'version': STORY_VERSION, 'content_hash': entry['content_hash'], 'captions': captions,
                                   'ai_captions': cached.get('ai_captions', cached['captions']), 'edited': True}, ensure_ascii=False))


class DiaryHandler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def log_message(self, format, *args):
        pass

    def reply(self, status, body, content_type='application/json; charset=utf-8', headers=None):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        try:
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def read_json(self):
        if self.headers.get('Content-Type', '').split(';', 1)[0].strip() != 'application/json':
            self.reply(415, {'error': 'JSON 형식으로 요청해 주세요.'})
            return None
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            raise ValueError('요청 길이가 올바르지 않습니다.')
        if not 0 < length <= 65536:
            self.reply(413, {'error': '요청이 비었거나 너무 큽니다.'})
            return None
        try:
            data = json.loads(self.rfile.read(length))
        except (ValueError, UnicodeError):
            raise ValueError('요청 내용을 읽지 못했습니다.') from None
        if not isinstance(data, dict):
            raise ValueError('요청은 JSON 객체여야 합니다.')
        return data

    def handle_request(self):
        host = f'127.0.0.1:{self.server.server_port}'
        if self.headers.get('Host') != host or (
                self.command != 'GET' and self.headers.get('Origin') != f'http://{host}'):
            self.reply(403, {'error': '로컬 앱 화면에서 요청해 주세요.'})
            return
        parsed = urlsplit(self.path)
        path = parsed.path
        try:
            if self.command == 'GET' and (path in DEMO_VIDEOS or re.fullmatch(r'/videos/[0-9a-f]{32}\.mp4', path)):
                if path in DEMO_VIDEOS:
                    video = ROOT / DEMO_VIDEOS[path]
                else:
                    db = Database()
                    video = Path(db.db_path).parent / 'videos' / path.rsplit('/',1)[1]
                if not video.is_file() or video.is_symlink():
                    self.reply(404, {'error':'영상을 찾을 수 없습니다.'})
                    return
                size = video.stat().st_size
                headers = {'Accept-Ranges': 'bytes'}
                requested = self.headers.get('Range')
                if requested:
                    match = re.fullmatch(r'bytes=(\d*)-(\d*)', requested)
                    if not match or not any(match.groups()):
                        self.reply(416, b'', 'video/mp4', {'Content-Range': f'bytes */{size}'})
                        return
                    first, last = match.groups()
                    start = int(first) if first else max(0, size - int(last))
                    end = min(int(last), size - 1) if first and last else size - 1
                    if start > end or start >= size:
                        self.reply(416, b'', 'video/mp4', {'Content-Range': f'bytes */{size}'})
                        return
                    with video.open('rb') as stream:
                        stream.seek(start)
                        body = stream.read(end - start + 1)
                    headers['Content-Range'] = f'bytes {start}-{end}/{size}'
                    self.reply(206, body, 'video/mp4', headers)
                else:
                    self.reply(200, video.read_bytes(), 'video/mp4', headers)
                return
            if self.command == 'GET' and path.startswith('/media/'):
                db = Database()
                image = media_file(db, path)
                if not image or not db.has_image(path) or not image.is_file() or image.is_symlink():
                    self.reply(404, {'error': '그림을 찾을 수 없습니다.'})
                    return
                mime = {'.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp'}[image.suffix]
                self.reply(200, image.read_bytes(), mime)
                return
            if self.command == 'GET' and path in FILES:
                filename, mime = FILES[path]
                try:
                    body = (ROOT / filename).read_bytes()
                except FileNotFoundError:
                    self.reply(404, {'error': '앱 파일을 찾을 수 없습니다.'})
                    return
                self.reply(200, body, mime)
                return
            routes = {('GET', '/api/settings'), ('POST', '/api/settings'),
                      ('GET', '/api/diary'), ('POST', '/api/diary'),
                      ('DELETE', '/api/diary'), ('POST', '/api/demo'), ('POST', '/api/image'), ('GET', '/api/memories'), ('POST', '/api/video'), ('POST', '/api/shorts'), ('POST', '/api/shorts/story'), ('POST', '/api/shorts/scene'), ('POST', '/api/three-year-video'), ('GET', '/api/videos')}
            if (self.command, path) not in routes:
                self.reply(404, {'error': '페이지를 찾을 수 없습니다.'})
                return
            data = self.read_json() if self.command == 'POST' else {}
            if data is None:
                return
            db = Database()
            if path == '/api/settings':
                if self.command == 'POST':
                    db.set_setting('start_year', data.get('start_year'))
                result = {'start_year': db.get_setting('start_year', 2024)}
                if self.command == 'GET':
                    result['image_api'] = {'configured': image_api.configured(), 'model': image_api.MODEL,
                                           'estimated_credits': image_api.DEFAULT_CREDITS}
                    result['music'] = {'default': DEFAULT_MUSIC, 'tracks': [{'id': key, 'label': label, 'credit': credit} for key, (_, label, credit) in MUSIC.items()]}
                    result['narration'] = {'available': narration.available(), 'credit': narration.CREDIT}
            elif path == '/api/memories':
                result = {'entries': db.list_diaries(db.get_setting('start_year', 2024))}
            elif path == '/api/videos':
                dates = parse_qs(parsed.query).get('date', [])
                if len(dates) != 1:
                    raise ValueError('영상의 날짜를 선택해 주세요.')
                result = {'videos': db.list_videos(dates[0])}
            elif path == '/api/shorts/scene':
                status, result = create_scene(db, data)
                self.reply(status, result)
                return
            elif path == '/api/three-year-video':
                status, result = create_three_year_video(db, data)
                self.reply(status, result)
                return
            elif path == '/api/shorts/story':
                status, result = prepare_story(db, data)
                self.reply(status, result)
                return
            elif path in ('/api/video', '/api/shorts'):
                status, result = create_video(db, data, shorts=path == '/api/shorts')
                self.reply(status, result)
                return
            elif path == '/api/image':
                status, result = create_image(db, data)
                self.reply(status, result)
                return
            elif path == '/api/demo':
                db.load_demo_data()
                db.set_setting('start_year', 2024)
                result = {'start_year': 2024, 'month': 11, 'day': 17}
            elif self.command == 'POST':
                result = db.save_diary(data.get('date'), data.get('content'))
            else:
                dates = parse_qs(parsed.query).get('date', [])
                if len(dates) != 1:
                    raise ValueError('일기 날짜를 하나 선택해 주세요.')
                if self.command == 'DELETE':
                    db.delete_diary(dates[0])
                    result = {'deleted': True}
                else:
                    result = db.get_diary(dates[0])
            self.reply(200, result)
        except ValueError as error:
            self.reply(400, {'error': str(error)})
        except Exception:
            self.reply(500, {'error': '처리하지 못했습니다. 입력 내용은 그대로 두고 다시 시도해 주세요.'})

    do_GET = handle_request
    do_POST = handle_request
    do_DELETE = handle_request


def run_server(port=8766):
    with ThreadingHTTPServer(('127.0.0.1', port), DiaryHandler) as server:
        print(f'3년 다이어리: http://127.0.0.1:{port}', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    run_server()
