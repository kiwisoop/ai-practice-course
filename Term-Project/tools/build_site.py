"""GitHub Pages용 정적 시연판(site/)을 static/ 원본에서 만든다.

python3 tools/build_site.py

- 서버 절대경로(/style.css, /assets/...)를 Pages 하위 폴더에서도 열리는 상대경로로 바꾼다.
- app.js보다 먼저 site/mock-api.js를 불러 /api/* 요청을 브라우저 안에서 처리한다(학교 AI 호출 없음).
- 미디어(assets/, previews/)는 복사하지 않고 '../'로 참조한다.
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / 'static'
SITE = ROOT / 'site'

BANNER = ('<div class="static-banner" role="note"><strong>온라인 시연판</strong> · 일기는 이 브라우저에만 저장돼요 · '
          'AI 이야기·그림·영상은 미리 만든 결과를 보여 줘요(토큰 사용 없음) · 전체 기능은 로컬 실행 · '
          '<a href="https://github.com/kiwisoop/ai-practice-course/tree/main/Term-Project">프로젝트 설명</a></div>')
BANNER_CSS = ('\n.static-banner { padding: 8px 16px; font-size: 13px; text-align: center; color: #fffdf6; background: var(--green); }\n'
              '.static-banner a { color: inherit; }\n')

COMMON = [
    ('href="/style.css"', 'href="style.css"'),
]
PAGES = {
    'index.html': [
        ('<script src="/app.js"></script>', '<script src="mock-api.js"></script>\n  <script src="app.js"></script>'),
        ('href="/demo/shorts"', 'href="shorts.html"'),
        ('<body>', '<body>\n  ' + BANNER),
    ],
    'long-diary-demo.html': [
        ('href="/"', 'href="index.html"'),
        ('/demo/shorts.mp4', '../previews/example-day.mp4'),
        ('/demo/three-year.mp4', '../previews/example-three-year.mp4'),
        ('/demo/shorts-poster.png', '../previews/example-day-poster.png'),
        ('/demo/three-year-poster.png', '../previews/example-three-year-poster.png'),
    ],
}
OUTPUT = {'index.html': 'index.html', 'long-diary-demo.html': 'shorts.html'}


def replace_all(text, pairs, name):
    for old, new in pairs:
        if old not in text:
            raise SystemExit(f'{name}: "{old}"를 찾지 못했습니다. 원본이 바뀌었는지 확인하세요.')
        text = text.replace(old, new)
    return text


def build():
    SITE.mkdir(exist_ok=True)
    for source, target in OUTPUT.items():
        text = (STATIC / source).read_text(encoding='utf-8')
        text = replace_all(text, COMMON + PAGES[source], source)
        if 'src="/' in text or 'href="/' in text:
            raise SystemExit(f'{source}: 절대경로가 남아 있습니다.')
        (SITE / target).write_text(text, encoding='utf-8')
    css = (STATIC / 'style.css').read_text(encoding='utf-8').replace("url('/assets/", "url('../assets/")
    (SITE / 'style.css').write_text(css + BANNER_CSS, encoding='utf-8')
    shutil.copyfile(STATIC / 'app.js', SITE / 'app.js')
    demos = json.loads((ROOT / 'demo_diaries.json').read_text(encoding='utf-8'))
    (SITE / 'demo_diaries.json').write_text(json.dumps(demos, ensure_ascii=False, indent=1), encoding='utf-8')
    print('site/ 생성 완료:', ', '.join(sorted(p.name for p in SITE.iterdir())))


if __name__ == '__main__':
    build()
