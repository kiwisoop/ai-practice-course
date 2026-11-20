import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
import math

# Preferred first: ffmpeg-full ships drawtext (subtitles). Plain builds may not.
FFMPEG_CANDIDATES = [
    '/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg',
    '/usr/local/opt/ffmpeg-full/bin/ffmpeg',
    '/opt/homebrew/bin/ffmpeg',
    '/usr/local/bin/ffmpeg',
    '/usr/bin/ffmpeg',
]


def _has_drawtext(ffmpeg):
    try:
        result = subprocess.run([ffmpeg, '-hide_banner', '-filters'], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0 and any(line.split()[1:2] == ['drawtext'] for line in result.stdout.splitlines() if line.strip())


def find_ffmpeg(environ=None, candidates=None, which=shutil.which, has_drawtext=None):
    """Return (ffmpeg, ffprobe) that can render Korean subtitles, or the best guess when none qualifies.

    Order: FFMPEG environment variable, known ffmpeg-full paths, then the PATH.
    """
    environ = os.environ if environ is None else environ
    has_drawtext = _has_drawtext if has_drawtext is None else has_drawtext
    ordered = [environ.get('FFMPEG', '')] + list(FFMPEG_CANDIDATES if candidates is None else candidates) + [which('ffmpeg') or '']
    found = []
    for path in ordered:
        if path and path not in found and Path(path).is_file():
            found.append(path)
    for path in found:
        probe = Path(path).with_name('ffprobe')
        if probe.is_file() and has_drawtext(path):
            return path, str(probe)
    if found:
        return found[0], str(Path(found[0]).with_name('ffprobe'))
    return 'ffmpeg', 'ffprobe'


FFMPEG, FFPROBE = find_ffmpeg()

def _find_korean_font():
    """시스템에서 한글 폰트 찾기"""
    font_paths = [
        os.environ.get('DIARY_FONT', ''),
        '/System/Library/Fonts/AppleSDGothicNeo.ttc',
        '/Library/Fonts/NanumGothic.ttf',
        '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.otf',
        'C:\\Windows\\Fonts\\malgun.ttf',
    ]
    for font_path in font_paths:
        if font_path and Path(font_path).is_file():
            return font_path
    return None

def _check_ffmpeg():
    """ffmpeg 설치 확인"""
    try:
        subprocess.run(
            [FFMPEG, '-version'],
            capture_output=True,
            timeout=5,
            shell=False
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def _check_ffprobe():
    """ffprobe 설치 확인"""
    try:
        subprocess.run(
            [FFPROBE, '-version'],
            capture_output=True,
            timeout=5,
            shell=False
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def _validate_date(date_str):
    """날짜 검증 YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False

MAX_CARDS = 5
CARD_SECONDS = (1, 4)


def make_card(title, subtitle='', seconds=2.0):
    """A plain text card (no picture) shown between diary scenes."""
    return {'card': True, 'title': title, 'subtitle': subtitle, 'seconds': seconds}


def make_ending(title, images, labels, seconds=3.5):
    """Closing montage: each year's picture stacked top to bottom, appearing one after another."""
    return {'card': True, 'ending': True, 'title': title, 'images': [str(i) for i in images], 'labels': labels, 'seconds': seconds}


def _validate_card(item, i):
    if item.get('ending') is True:
        images, labels = item.get('images'), item.get('labels')
        if (not isinstance(images, list) or not isinstance(labels, list) or not 2 <= len(images) <= 3 or len(images) != len(labels)
                or any(not isinstance(label, str) or not label.strip() or len(label) > 8 or '\n' in label for label in labels)
                or any(not isinstance(image, str) or not Path(image).is_file() for image in images)):
            raise ValueError(f'마무리 장면 {i}의 그림·연도를 확인해 주세요')
    for field, limit in (('title', 24), ('subtitle', 32)):
        value = item.get(field, '')
        if not isinstance(value, str) or len(value) > limit or '\n' in value or '\r' in value:
            raise ValueError(f'카드 {i}의 {field}를 확인해 주세요')
    if not item.get('title', '').strip():
        raise ValueError(f'카드 {i}의 제목이 비었습니다')
    seconds = item.get('seconds')
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not CARD_SECONDS[0] <= seconds <= CARD_SECONDS[1]:
        raise ValueError(f'카드 {i}의 시간은 {CARD_SECONDS[0]}~{CARD_SECONDS[1]}초여야 합니다')
    if round(seconds * 24) != seconds * 24:
        raise ValueError(f'카드 {i}의 시간은 1/24초 단위여야 합니다')


def item_duration(item, shorts=False):
    if item.get('card') is True:
        return item['seconds']
    return scene_duration(item['caption']) if shorts else 4


PANEL_REVEAL = 0.45


def _create_ending(item, output_video, font_path, temp_dir, index):
    seconds, count = item['seconds'], len(item['images'])
    panel_height = 1140 // count
    title = Path(temp_dir) / f'ending_{index:02d}_title.txt'
    title.write_text(item['title'], encoding='utf-8')
    inputs, chains = [], []
    for panel, (image, label) in enumerate(zip(item['images'], item['labels'])):
        label_file = Path(temp_dir) / f'ending_{index:02d}_label_{panel}.txt'
        label_file.write_text(label, encoding='utf-8')
        inputs += ['-loop', '1', '-framerate', '24', '-t', str(seconds), '-i', image]
        chains.append(
            f'[{panel}:v]scale=720:{panel_height - 8}:force_original_aspect_ratio=increase,crop=720:{panel_height - 8},setsar=1,'
            f"drawtext=fontfile='{font_path}':textfile='{label_file}':expansion=none:fontsize=40:fontcolor=white:x=28:y=h-text_h-24"
            ':shadowcolor=black@0.7:shadowx=2:shadowy=3,'
            f'pad=720:{panel_height}:0:0:color=0x2b2520,fade=t=in:st={panel * PANEL_REVEAL}:d={PANEL_REVEAL}[p{panel}]')
    stacked = ''.join(f'[p{panel}]' for panel in range(count))
    chains.append(
        f'{stacked}vstack=inputs={count},pad=720:1280:0:1280-ih:color=0x2b2520,'
        f"drawtext=fontfile='{font_path}':textfile='{title}':expansion=none:fontsize=40:fontcolor=0xf5f1e8:x=(w-text_w)/2:y=(140-text_h)/2,"
        f'fps=24,fade=t=out:st={seconds - 0.5}:d=0.5[v]')
    result = subprocess.run([FFMPEG, '-v', 'error', '-y', '-filter_threads', '1', *inputs,
                             '-filter_complex', ';'.join(chains), '-map', '[v]', '-t', str(seconds), '-r', '24',
                             '-c:v', 'libx264', '-preset', 'fast', '-pix_fmt', 'yuv420p', str(output_video)],
                            capture_output=True, timeout=180)
    if result.returncode:
        raise ValueError('마무리 장면을 만들지 못했습니다.')


def _create_card(item, output_video, font_path, temp_dir, index):
    if item.get('ending') is True:
        return _create_ending(item, output_video, font_path, temp_dir, index)
    seconds = item['seconds']
    title = Path(temp_dir) / f'card_{index:02d}_title.txt'
    title.write_text(item['title'], encoding='utf-8')
    filters = [
        f"drawtext=fontfile='{font_path}':textfile='{title}':expansion=none:fontsize=64:fontcolor=0xf5f1e8:x=(w-text_w)/2:y=(h-text_h)/2-40",
    ]
    if item.get('subtitle'):
        subtitle = Path(temp_dir) / f'card_{index:02d}_subtitle.txt'
        subtitle.write_text(item['subtitle'], encoding='utf-8')
        filters.append(f"drawtext=fontfile='{font_path}':textfile='{subtitle}':expansion=none:fontsize=32:fontcolor=0xd9cbb4:x=(w-text_w)/2:y=(h/2)+40")
    filters += ['setsar=1', f'fade=t=in:st=0:d=0.3,fade=t=out:st={seconds - 0.3}:d=0.3']
    result = subprocess.run([FFMPEG, '-v', 'error', '-y', '-filter_threads', '1',
                             '-f', 'lavfi', '-i', f'color=c=0x2b2520:s=720x1280:r=24:d={seconds}',
                             '-vf', ','.join(filters), '-t', str(seconds), '-r', '24', '-c:v', 'libx264',
                             '-preset', 'fast', '-pix_fmt', 'yuv420p', str(output_video)],
                            capture_output=True, timeout=120)
    if result.returncode:
        raise ValueError('제목 카드를 만들지 못했습니다.')


def _validate_items(items):
    """항목 검증"""
    if not isinstance(items, list):
        raise ValueError('items는 리스트여야 합니다')
    if any(not isinstance(item, dict) for item in items):
        raise ValueError('각 항목은 dict여야 합니다')
    cards = [item for item in items if item.get('card') is True]
    scenes = [item for item in items if item.get('card') is not True]
    # Title/year cards are not scenes: the 8-scene limit applies to diary pictures only.
    if not 1 <= len(scenes) <= 8 or len(cards) > MAX_CARDS:
        raise ValueError(f'장면은 1~8개, 카드는 {MAX_CARDS}개 이하여야 합니다')

    for i, item in enumerate(items):
        if item.get('card') is True:
            _validate_card(item, i)
            continue

        if 'date' not in item:
            raise ValueError(f'항목 {i}에 date가 없습니다')
        if not _validate_date(item['date']):
            raise ValueError(f'항목 {i}의 날짜 형식이 올바르지 않습니다')
        
        if 'caption' not in item:
            raise ValueError(f'항목 {i}에 caption이 없습니다')
        caption = item['caption']
        if not isinstance(caption, str):
            raise ValueError(f'항목 {i}의 caption은 문자열이어야 합니다')
        if len(caption) > 64:
            raise ValueError(f'항목 {i}의 caption이 64자를 초과합니다')
        
        if 'image_path' not in item:
            raise ValueError(f'항목 {i}에 image_path가 없습니다')
        image_path = Path(item['image_path'])
        if not image_path.exists():
            raise ValueError(f'항목 {i}의 이미지 파일이 없습니다')
        if not image_path.is_file():
            raise ValueError(f'항목 {i}의 image_path는 파일이어야 합니다')

def _wrap_caption(text, max_width=36):
    """자막 줄바꿈 (한글 18자 기준, 최대 4줄)"""
    text = ' '.join(text.split())
    lines = []
    current_line = ''
    char_count = 0
    
    for char in text:
        if char == '\n':
            lines.append(current_line)
            current_line = ''
            char_count = 0
            if len(lines) >= 4:
                break
        else:
            char_width = 2 if ord(char) > 127 else 1
            if char_count + char_width > max_width:
                if current_line:
                    lines.append(current_line)
                    if len(lines) >= 4:
                        return '\n'.join(lines[:4])
                current_line = char
                char_count = char_width
            else:
                current_line += char
                char_count += char_width
    
    if current_line and len(lines) < 4:
        lines.append(current_line)
    
    return '\n'.join(lines[:4])

def _escape_drawtext(text):
    """drawtext를 위한 텍스트 이스케이프"""
    text = text.replace(':', '\\:')
    text = text.replace("'", "'\\''")
    return text

def _create_subtitle_file(caption_text, temp_dir):
    """자막 파일 생성"""
    subtitle_file = Path(temp_dir) / 'subtitle.txt'
    with open(subtitle_file, 'w', encoding='utf-8') as f:
        f.write(caption_text)
    return str(subtitle_file)

def _create_concat_file(video_files, temp_dir):
    """concat demuxer 입력 파일 생성"""
    concat_file = Path(temp_dir) / 'concat.txt'
    with open(concat_file, 'w', encoding='utf-8') as f:
        for video_file in video_files:
            f.write(f"file '{video_file}'\n")
    return str(concat_file)

def _create_scene_video(
    image_path,
    date_str,
    caption,
    output_video,
    font_path,
    temp_dir
):
    """개별 장면 비디오 생성"""
    cream_color = 'f5f1e8'
    
    # 자막 줄바꿈
    wrapped_caption = _wrap_caption(caption)
    subtitle_file = _create_subtitle_file(wrapped_caption, temp_dir)
    
    # 필터 구성
    filter_parts = []
    
    # 1. 이미지 스케일 및 패딩
    filter_parts.append(
        f'scale=720:800:force_original_aspect_ratio=decrease,'
        f'pad=720:1280:(ow-iw)/2:180:color=#{cream_color}'
    )
    
    # 2. zoompan (느린 확대)
    filter_parts.append('zoompan=z=\'min(zoom+0.0015,1.5)\':d=1:x=(iw-iw/zoom)/2:y=(ih-ih/zoom)/2:s=720x1280:fps=24')
    
    # 3. 페이드 (4초 = 96 프레임 at 24fps)
    filter_parts.append('fade=t=in:st=0:d=0.5,fade=t=out:st=3.5:d=0.5')
    
    # 4. 날짜 텍스트
    date_text = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y.%m.%d')
    date_text_escaped = _escape_drawtext(date_text)
    
    if font_path:
        font_path_escaped = font_path.replace("'", "'\\''")
        filter_parts.append(
            f"drawtext=fontfile='{font_path_escaped}':text='{date_text_escaped}':"
            f"fontsize=28:fontcolor=3d3429:x=(w-text_w)/2:y=100:line_spacing=8"
        )
    
    # 5. 자막 텍스트
    subtitle_file_escaped = subtitle_file.replace("'", "'\\''")
    if font_path:
        font_path_escaped = font_path.replace("'", "'\\''")
        filter_parts.append(
            f"drawtext=fontfile='{font_path_escaped}':textfile='{subtitle_file_escaped}':"
            f"fontsize=30:fontcolor=3d3429:x=(w-text_w)/2:y=1000:line_spacing=12:expansion=none"
        )
    else:
        filter_parts.append(
            f"drawtext=textfile='{subtitle_file_escaped}':"
            f"fontsize=30:fontcolor=3d3429:x=(w-text_w)/2:y=1000:line_spacing=12:expansion=none"
        )
    
    # ffmpeg 명령어
    cmd = [
        FFMPEG,
        '-y', '-filter_threads', '1',
        '-loop', '1', '-framerate', '24',
        '-i', str(image_path),
        '-c:v', 'libx264',
        '-vf', ','.join(filter_parts),
        '-t', '4',
        '-r', '24',
        '-pix_fmt', 'yuv420p',
        '-preset', 'fast',
        str(output_video)
    ]
    
    result = subprocess.run(
        cmd,
        shell=False,
        timeout=180,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise ValueError(f'장면 생성 실패')

def scene_duration(caption):
    return max(4, math.ceil(len(caption) / 8))


def _display_width(text):
    return sum(2 if ord(char) > 127 else 1 for char in text)


def caption_lines(caption, max_width=22):
    """Split a caption into short phrases (about 11 Korean characters) for line-by-line reveal.

    Breaks at spaces; a single word longer than a line is split by characters. Text is never dropped.
    """
    lines, current = [], ''
    for word in ' '.join(caption.split()).split(' '):
        while _display_width(word) > max_width:
            head = ''
            for char in word:
                if _display_width(head + char) > max_width:
                    break
                head += char
            if current:
                lines.append(current)
                current = ''
            lines.append(head)
            word = word[len(head):]
        candidate = (current + ' ' + word).strip()
        if current and _display_width(candidate) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def reveal_times(line_count, seconds):
    """When each phrase starts to appear: spread over the first half of the scene, 0.35–0.8 s apart."""
    step = min(0.8, max(0.35, seconds * 0.5 / max(line_count, 1)))
    return [round(0.3 + index * step, 3) for index in range(line_count)]


REVEAL_SECONDS = 0.4
CAPTION_BOTTOM = 1010  # Keeps captions above the Shorts/Reels buttons at the bottom of the screen.


def _create_shorts_scene(image_path, date_str, caption, output_video, font_path, temp_dir, scene_index=0):
    date_text = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y.%m.%d')
    seconds = scene_duration(caption)
    frames = seconds * 24 - 1
    pan = f'on/{frames}' if scene_index % 2 == 0 else f'1-on/{frames}'
    lines = caption_lines(caption)
    fontsize = 36 if len(lines) >= 4 else 42
    line_height = round(fontsize * 1.45)
    box_top = CAPTION_BOTTOM - len(lines) * line_height - 48
    filters = [
        'scale=800:1400:force_original_aspect_ratio=increase,crop=800:1400',
        f"zoompan=z='1.04+0.06*on/{frames}':d=1:x=(iw-iw/zoom)*({pan}):y=(ih-ih/zoom)/2:s=720x1280:fps=24",
        'drawbox=x=0:y=0:w=iw:h=ih:color=black@0.20:t=fill',
        f'drawbox=x=30:y={box_top}:w=660:h={CAPTION_BOTTOM - box_top}:color=black@0.38:t=fill',
        f"drawtext=fontfile='{font_path}':text='{date_text}':fontsize=23:fontcolor=white:x=48:y=90:shadowcolor=black@0.6:shadowx=1:shadowy=2",
    ]
    # Phrase-by-phrase reveal: each line fades in and rises slightly, like the diary being read aloud.
    for index, (line, start) in enumerate(zip(lines, reveal_times(len(lines), seconds))):
        text_file = Path(temp_dir) / f'caption_{scene_index:02d}_{index:02d}.txt'
        text_file.write_text(line, encoding='utf-8')
        y = box_top + 24 + index * line_height
        filters.append(
            f"drawtext=fontfile='{font_path}':textfile='{text_file}':expansion=none:fontsize={fontsize}:fontcolor=white"
            f":x=(w-text_w)/2:y='{y}+16*max(0,1-(t-{start})/{REVEAL_SECONDS})'"
            f":alpha='if(lt(t,{start}),0,min(1,(t-{start})/{REVEAL_SECONDS}))'"
            ':shadowcolor=black@0.7:shadowx=2:shadowy=3')
    filters.append(f'fade=t=in:st=0:d=0.15,fade=t=out:st={seconds-0.15}:d=0.15')
    result = subprocess.run([FFMPEG, '-v', 'error', '-y', '-filter_threads', '1',
                             '-loop', '1', '-framerate', '24', '-i', str(image_path),
                             '-vf', ','.join(filters), '-t', str(seconds), '-r', '24', '-c:v', 'libx264',
                             '-preset', 'fast', '-pix_fmt', 'yuv420p', str(output_video)],
                            capture_output=True, timeout=180)
    if result.returncode:
        raise ValueError('쇼츠 장면을 만들지 못했습니다.')


MUSIC_DIR = Path(__file__).parent / 'assets'
# id: (file under assets/, label shown in the app, attribution required by the license)
MUSIC = {
    'bright': ('music/bright-redwood-trail.mp3', '경쾌한 어쿠스틱', 'Redwood Trail — Jason Shaw (audionautix.com), CC BY 3.0'),
    'warm': ('music/warm-warm-sunset.ogg', '따뜻한 어쿠스틱', 'Warm Sunset — MusicLFiles, CC BY 4.0'),
    'calm': ('music/calm-acoustic-meditation.ogg', '잔잔한 기타', 'Acoustic Meditation — Jason Shaw, CC BY 3.0 US'),
    'hopeful': ('music/hopeful-ukulele-rising.ogg', '희망찬 우쿨렐레', 'Ukulele Rising — Squire Tuck, CC BY 4.0'),
    'guitar': ('guitar.ogg', '기존 기타 샘플', 'AcousticGuitarSample — RyGuy, Public Domain'),
}
DEFAULT_MUSIC = 'bright'
MUSIC_CROSSFADE = 1.5
MUSIC_LOUDNESS = 'loudnorm=I=-18:TP=-2:LRA=11'  # Even level across tracks of different loudness.


def ending_music(music):
    """The closing montage switches to a brighter track (never the same one)."""
    return 'bright' if music == 'hopeful' else 'hopeful'


def music_filter(duration, switch_at=None):
    """Audio graph: input 1 is the main track; with switch_at, input 2 crossfades in for the ending."""
    tail = f'{MUSIC_LOUDNESS},aresample=48000,afade=t=in:d=1,afade=t=out:st={duration - 1.5}:d=1.5[a]'
    if switch_at is None:
        return f'[1:a]aresample=48000,{tail}'
    fade = MUSIC_CROSSFADE
    delay = round(switch_at * 1000)
    return (f'[1:a]aresample=48000,atrim=0:{switch_at + fade},afade=t=out:st={switch_at}:d={fade},asetpts=PTS-STARTPTS[m];'
            f'[2:a]aresample=48000,atrim=0:{duration - switch_at},asetpts=PTS-STARTPTS,afade=t=in:d={fade},adelay=delays={delay}:all=1[e];'
            f'[m][e]amix=inputs=2:normalize=0:duration=longest,{tail}')


def export_video(items, output_path, shorts=False, music=DEFAULT_MUSIC, switch_music=None):
    """영상 생성. switch_music: the ending card (make_ending) starts with this track instead."""
    if not _check_ffmpeg():
        raise ValueError('ffmpeg가 설치되지 않았습니다')
    if not _check_ffprobe():
        raise ValueError('ffprobe가 설치되지 않았습니다')
    
    _validate_items(items)
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.exists():
        raise ValueError('기존 영상 파일을 덮어쓰지 않습니다')
    
    font_path = _find_korean_font()
    if not font_path:
        raise ValueError('한글 자막용 시스템 글꼴을 찾지 못했습니다')
    
    # 배경음악: the chosen track, plus an optional ending track that crossfades in at the ending montage.
    if music not in MUSIC or (switch_music is not None and switch_music not in MUSIC):
        raise ValueError('배경음악 선택을 확인해 주세요')
    tracks = [MUSIC_DIR / MUSIC[music][0]]
    switch_at = None
    if switch_music is not None:
        ending = [index for index, item in enumerate(items) if item.get('ending') is True]
        if ending:
            switch_at = sum(item_duration(item, shorts) for item in items[:ending[0]])
            tracks.append(MUSIC_DIR / MUSIC[switch_music][0])
    if any(not track.is_file() for track in tracks):
        raise ValueError('배경음악 파일이 없습니다')
    credits = ' / '.join(dict.fromkeys(MUSIC[name][2] for name in ([music] + ([switch_music] if switch_at is not None else []))))
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        scene_videos = []
        
        try:
            # 각 장면 생성
            scene_index = 0
            for i, item in enumerate(items):
                scene_output = temp_path / f'scene_{i:02d}.mp4'
                if item.get('card') is True:
                    _create_card(item, str(scene_output), font_path, temp_dir, i)
                    scene_videos.append(str(scene_output))
                    continue
                renderer = _create_shorts_scene if shorts else _create_scene_video
                renderer(
                    item['image_path'],
                    item['date'],
                    item['caption'],
                    str(scene_output),
                    font_path,
                    temp_dir,
                    # Pan direction alternates over pictures only, so cards do not break the rhythm.
                    **({'scene_index': scene_index} if shorts else {})
                )
                scene_index += 1
                scene_videos.append(str(scene_output))
            
            # concat 파일 생성
            concat_file = _create_concat_file(scene_videos, temp_dir)
            
            duration = sum(item_duration(item, shorts) for item in items)
            # 최종 영상 생성
            final_cmd = [
                FFMPEG,
                '-y', '-filter_threads', '1',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                *[arg for track in tracks for arg in ('-stream_loop', '-1', '-i', str(track))],
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-c:a', 'aac',
                '-filter_complex', music_filter(duration, switch_at),
                '-map', '0:v:0',
                '-map', '[a]',
                '-pix_fmt', 'yuv420p',
                '-r', '24',
                # CC BY attribution travels with the file itself.
                '-metadata', f'comment=Music: {credits}',
                '-t', str(duration), '-movflags', 'faststart',
                str(output_path)
            ]
            
            result = subprocess.run(
                final_cmd,
                shell=False,
                timeout=180,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                if output_path.exists():
                    output_path.unlink()
                raise ValueError('영상 생성 실패')
            
            if not output_path.exists():
                raise ValueError('영상 파일이 생성되지 않았습니다')
        
        except subprocess.TimeoutExpired:
            if output_path.exists():
                output_path.unlink()
            raise ValueError('영상 생성 시간 초과')
        except Exception as e:
            if output_path.exists():
                try:
                    output_path.unlink()
                except:
                    pass
            if isinstance(e, ValueError):
                raise
            raise ValueError('영상 생성에 실패했습니다. 원본 기록은 유지됩니다.')
