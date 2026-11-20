"""Runs inside the separate TTS environment (not the app's Python).

Reads {"model_dir", "voice", "speed", "steps", "items": [{"text", "out"}]} as JSON on stdin and
writes one WAV per item with Supertonic 3. Called only by narration.py; prints nothing on success.
"""
import json
import sys


def main():
    job = json.load(sys.stdin)
    from supertonic import TTS  # imported here so a missing package gives a clear exit code

    tts = TTS(model='supertonic-3', model_dir=job['model_dir'], auto_download=False)
    style = tts.get_voice_style(voice_name=job['voice'])
    for item in job['items']:
        wav, _ = tts.synthesize(item['text'], voice_style=style, total_steps=job['steps'], speed=job['speed'], lang='ko')
        tts.save_audio(wav, item['out'])


if __name__ == '__main__':
    main()
