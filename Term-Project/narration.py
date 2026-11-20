"""Scene narration: reads each caption aloud with a local open-source voice (Supertonic 3, voice F1).

Runs entirely on this computer: no API call, no credits. The TTS model lives in its own Python
environment (.tts/), so the app itself keeps using only the standard library.
"""
import hashlib
import json
import os
import subprocess
import wave
from pathlib import Path

VOICE = 'F1'
SPEED = 1.0
STEPS = 10
CREDIT = 'AI 음성: Supertonic 3 (Supertone, OpenRAIL-M) · F1'
HERE = Path(__file__).resolve().parent
WORKER = HERE / 'tts_worker.py'
TIMEOUT = 180


def _tts_root(environ=None):
    """The folder holding venv/ and models/: DIARY_TTS_DIR, else v2/.tts, else Term-Project/.tts."""
    environ = os.environ if environ is None else environ
    if environ.get('DIARY_TTS_DIR'):
        return Path(environ['DIARY_TTS_DIR'])
    for candidate in (HERE / '.tts', HERE.parent / '.tts'):
        if candidate.is_dir():
            return candidate
    return HERE / '.tts'


def tts_paths(environ=None):
    root = _tts_root(environ)
    return root / 'venv' / 'bin' / 'python', root / 'models'


def available(environ=None):
    python, models = tts_paths(environ)
    return python.is_file() and (models / 'onnx' / 'vocoder.onnx').is_file() and (models / 'voice_styles' / f'{VOICE}.json').is_file()


def cache_name(text):
    key = json.dumps([VOICE, SPEED, STEPS, text], ensure_ascii=False)
    return hashlib.sha256(key.encode('utf-8')).hexdigest() + '.wav'


def wav_seconds(path):
    with wave.open(str(path), 'rb') as audio:
        return audio.getnframes() / float(audio.getframerate())


def synthesize(texts, cache_dir, environ=None, run=subprocess.run):
    """Return one WAV path per text, generating only the ones not cached yet."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    paths = [cache_dir / cache_name(text) for text in texts]
    missing = {str(path): text for path, text in zip(paths, texts) if not path.is_file()}
    if missing:
        if not available(environ):
            raise ValueError('내레이션 음성 모델이 설치되지 않았어요. 내레이션을 끄거나 README의 설치 방법을 확인해 주세요.')
        python, models = tts_paths(environ)
        # Write to temporary names first so a failed run never leaves half a file in the cache.
        items = [{'text': text, 'out': out + '.part.wav'} for out, text in missing.items()]
        job = {'model_dir': str(models), 'voice': VOICE, 'speed': SPEED, 'steps': STEPS, 'items': items}
        try:
            result = run([str(python), '-I', str(WORKER)], input=json.dumps(job, ensure_ascii=False), text=True,
                         capture_output=True, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            result = None
        if result is None or result.returncode != 0:
            for item in items:
                Path(item['out']).unlink(missing_ok=True)
            raise ValueError('내레이션 음성을 만들지 못했어요. 원본 일기는 그대로예요.')
        for item in items:
            part = Path(item['out'])
            if not part.is_file():
                raise ValueError('내레이션 음성 파일을 확인하지 못했어요.')
            part.replace(item['out'][:-len('.part.wav')])
    return paths
