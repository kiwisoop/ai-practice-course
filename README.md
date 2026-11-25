# AI Practice Course (인공지능활용실습 프로젝트)

본 저장소는 국립목포대학교 **인공지능활용실습** 수업의 실습 과제와 결과물을 관리하는 저장소입니다.  
AI 코딩 도구(Claude Code·Codex)와 함께 만든 **일곱 개의 실습 폴더**(`Study-00` ~ `Study-06`)와, 별도 저장소로 분리한 **기말 프로젝트**로 구성되어 있습니다.

> 📸 **프로그램을 실행하지 않고 화면으로 바로 보고 싶다면 → [실행 화면 갤러리 (SCREENSHOTS.md)](./SCREENSHOTS.md)**  
> 프로젝트별 자세한 화면은 아래 표의 **보기** 링크(각 폴더의 `SCREENSHOTS.md`)에 있습니다.  
> ▶ 브라우저 앱(Study-00·02·03·06)은 **설치 없이 온라인으로 바로 실행**할 수 있습니다.

---

## 📂 프로젝트 구성 요약

프로젝트는 **실행 방식**에 따라 세 가지로 나뉩니다.

| 분류 | 설명 | 필요한 것 |
| :--- | :--- | :--- |
| 🌐 **웹 앱** | 서버 없이 `index.html`만 열면 바로 실행 | 웹 브라우저 |
| 🐍 **Python 앱** | 내 컴퓨터에서 실행하는 데스크톱·로컬 웹 프로그램 | Python과 라이브러리 설치 |
| 🤖 **AI 연동 앱** | 로컬 Python 서버가 학교 AI API(FactChat)를 호출 | Python, 본인의 API 키 |

| 분류 | 프로젝트 | 프로그램 명 | 교재 | 설명 | 기술 스택 | 실행 화면 |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| 🌐 웹 | **[`Study-00`](./Study-00/)** | **시작 홈페이지 · 마케팅 포트폴리오** | 01–02 | 교재 프롬프트로 만든 시작 페이지, 모호한/구체적 프롬프트 비교, PRD 기반 포트폴리오 | HTML, CSS, Vanilla JS | [보기](./Study-00/SCREENSHOTS.md) · [▶ 실행](https://kiwisoop.github.io/ai-practice-course/Study-00/01-start-page/) |
| 🐍 Python | **[`Study-01`](./Study-01/)** | **손글씨 숫자 인식** | 03 | 숫자를 그리면 MNIST로 학습한 CNN이 숫자와 신뢰도를 알려 주는 데스크톱·웹 프로그램 | Python, TensorFlow/Keras, Tkinter | [보기](./Study-01/SCREENSHOTS.md) |
| 🌐 웹 | **[`Study-02`](./Study-02/)** | **Kiwibird 할 일 관리** | 04–06 | 할 일을 모두 끝내면 둥지의 알이 키위새로 바뀌는 개인용 할 일 관리 앱 | HTML, CSS, Vanilla JS, localStorage | [보기](./Study-02/SCREENSHOTS.md) · [▶ 실행](https://kiwisoop.github.io/ai-practice-course/Study-02/) |
| 🌐 웹 | **[`Study-03`](./Study-03/)** | **상식 한 바퀴 퀴즈** | 07–09 | 모든 문제에 출처가 붙은 50문제 퀴즈 + 커스텀 명령어 10개 + 교사용 보고서 | HTML, CSS, Vanilla JS, Python·Node.js 검사 도구 | [보기](./Study-03/SCREENSHOTS.md) · [▶ 실행](https://kiwisoop.github.io/ai-practice-course/Study-03/) |
| 🤖 AI 앱 | **[`Study-04`](./Study-04/)** | **FridgeChef 냉장고 요리사** | 11–13 | 냉장고 사진에서 재료를 인식하고 레시피를 추천·저장하는 앱 + 서브에이전트 개선 | Python, Streamlit, SQLite, FactChat API | [보기](./Study-04/SCREENSHOTS.md) |
| 🤖 AI 앱 | **[`Study-05`](./Study-05/)** | **공감 다이어리 · PDF 요약** | 14 | AI 개발팀(서브에이전트 5개)과 만든 일기 공감 앱과 PDF 요약 앱 | Python, pypdf, HTML·CSS·JS, FactChat API | [보기](./Study-05/SCREENSHOTS.md) |
| 🌐 웹 | **[`Study-06`](./Study-06/)** | **쇼핑 리스트 + MCP** | 15–16 | MCP 5개(Notion·Sequential Thinking·Context7·Playwright·GitHub)로 자동 검사·문서화·배포 | HTML, CSS, Vanilla JS, MCP | [보기](./Study-06/SCREENSHOTS.md) · [▶ 실행](https://kiwisoop.github.io/ai-practice-course/Study-06/claude-code-rerun/shopping-list.html) |
| ⭐ 기말 | **[`same-day-diary`](https://github.com/kiwisoop/same-day-diary)** | **3년 다이어리** | — | 같은 날짜의 일기를 3년간 모으고, AI가 이야기·수채화·음성 쇼츠 영상으로 만들어 줌 | 별도 저장소 참고 | [저장소](https://github.com/kiwisoop/same-day-diary) |

> 수업 진행 순서: 프롬프트(00) → Claude Code 시작(01) → 단계별 개발(02) → 커스텀 명령어(03) → API 연결(04) → 서브에이전트(04·05) → MCP(06) → 기말 프로젝트

---

## 0. [Study-00] 시작 홈페이지 · 마케팅 포트폴리오 (Prompt Basics)

교재 01 「AI 어시스턴트」와 교재 02 「프롬프트 활용」의 웹페이지 실습입니다. 교재는 claude.ai 아티팩트에서 진행하지만, 여기서는 Claude Code에 교재 프롬프트를 같은 순서로 입력해 HTML로 만들었습니다.

### ✨ 결과물
- **🏠 시작 홈페이지 (교재 01)**: 시계·Google 검색창·오늘의 할 일·서울 날씨·기술 뉴스를 2열 메모지 카드로 배치. 날씨(Open-Meteo)와 뉴스(Hacker News)는 실시간으로 불러옴
- **⚖️ 프롬프트 비교 (교재 02)**: "'멋진' 시작 홈페이지"라는 모호한 프롬프트의 결과와 구체적인 프롬프트의 결과를 나란히 비교
- **💼 마케팅 포트폴리오 (교재 02)**: 5W1H 템플릿으로 PRD 작성 → 5단계 프롬프트로 변환 → 뼈대·기능·디자인·점검 4단계로 완성한 프리랜서 마케터 포트폴리오 (가상 인물)

### 🤖 AI 활용 과정
- 교재 01의 프롬프트 6개(기본 요청 → 스타일·기능 추가 → 구글 스타일 → 할 일 추가 → 메모지 2열 배치)를 순서대로 반영했습니다.
- 포트폴리오는 단계마다 요청 → 생성 → 확인 → 수정을 반복했고, 점검 단계에서 개선점 3가지(모바일 메뉴, 차트 글자 크기, 좁은 카드)를 찾아 고쳤습니다. → [진행 기록](./Study-00/02-portfolio/PROMPTS.md)

### 🛠️ 기술 스택
- **Frontend**: HTML, CSS, Vanilla JavaScript, SVG 차트, localStorage
- **외부 데이터**: Open-Meteo 날씨, Hacker News 검색 API (API 키 불필요)

### 🚀 실행 방법
- **온라인**: [▶ 시작 홈페이지](https://kiwisoop.github.io/ai-practice-course/Study-00/01-start-page/) · [▶ 프롬프트 비교](https://kiwisoop.github.io/ai-practice-course/Study-00/02-prompt-compare/) · [▶ 포트폴리오](https://kiwisoop.github.io/ai-practice-course/Study-00/02-portfolio/)
- **로컬**: 각 폴더의 `index.html`을 브라우저에서 엽니다. 자세한 내용은 [`Study-00/README.md`](./Study-00/README.md)를 참고하세요.

---

## 1. [Study-01] 손글씨 숫자 인식 프로그램 (Handwritten Digit Recognizer)

검은 화면에 0~9 숫자 하나를 그리면, MNIST 데이터로 학습한 인공지능이 어떤 숫자인지 예측하고 신뢰도를 함께 보여 주는 프로그램입니다. Python 데스크톱 프로그램으로 시작해 같은 모델을 쓰는 웹 버전까지 확장했습니다.

### ✨ 주요 기능
- **숫자 인식**: 손으로 그린 숫자 0–9를 인식하고 예측 숫자와 신뢰도 표시
- **두 가지 버전**: Tkinter 데스크톱 버전과 브라우저 웹 버전(마우스·터치 입력)
- **공통 모델 코드**: 두 버전이 `mnist_model.py`의 모델·이미지 전처리 코드를 함께 사용
- **이미지 전처리**: 그린 숫자를 잘라 28×28 크기로 맞추고 가운데 정렬
- **학습된 모델 포함**: 처음 실행할 때 다시 학습할 필요 없음
- **입력 검증**: 빈 화면을 인식하려 하면 안내 메시지 표시
- **Windows 배치 파일**: 더블 클릭으로 가상환경 생성·설치·실행

### 🤖 AI 활용 과정
- 한 번에 완성을 요청하지 않고 **데스크톱 → 실행 환경 정리 → 웹 확장** 순서로 나누어 요청했습니다.
- 프로젝트 구조·실행 명령·코드 규칙을 `AGENTS.md`에 남겨, 다음 작업에서도 같은 방식으로 이어 갔습니다.

### 🛠️ 기술 스택
- **언어**: Python 3.11 권장
- **머신러닝**: TensorFlow/Keras (CNN), NumPy
- **GUI & 이미지 처리**: Tkinter, Pillow, HTML Canvas
- **웹 서버**: Python 표준 `http.server`

### 🚀 실행 방법
```bash
cd Study-01
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt

python desktop_version/digit_recognition.py   # 데스크톱 버전
python web_version/server.py                  # 웹 버전 → http://127.0.0.1:8000
```
Windows는 `desktop_version/run_desktop.bat`, `web_version/run_web.bat`을 더블 클릭합니다. OS별 상세 안내는 [`Study-01/README.md`](./Study-01/README.md)에 있습니다.

### 🧪 테스트 실행
```bash
python -m unittest discover -s tests   # 이미지 전처리·빈 화면 거부 테스트 2개
```

---

## 2. [Study-02] Kiwibird 할 일 관리 앱 (Personal Task Manager)

해야 할 일을 둥지에 하나씩 모아 가는 개인용 할 일 관리 앱입니다. 할 일이 생기면 둥지에 알이 나타나고, 등록한 일을 모두 끝내면 알 대신 키위새를 만날 수 있습니다.

### ✨ 주요 기능
- **🐣 둥지 대시보드**: 빈 둥지 → 알이 있는 둥지 → 키위새가 있는 둥지로 진행 상태 표현, 전체·카테고리별 완료율
- **📋 할 일 관리**: 추가·수정·완료·삭제, 6개 카테고리(업무·과제·공부·취미·개발·개인), 마감일(`D-1`, `오늘`, `기한 지남`)과 중요도
- **⚡ 키워드 자동 분류 (5주차)**: 입력 키워드로 카테고리 추천, 키워드 직접 설정, 미완료 할 일 일괄 재분류
- **🔍 검색·필터·정렬**: 상태·카테고리 필터와 정렬을 동시에 사용
- **⏱️ Kiwibird Focus**: 우선순위에 맞는 할 일 추천, 15·25·45분 또는 5–120분 집중 타이머
- **🌓 라이트 / 다크 모드**, 반응형 디자인
- **💾 저장과 백업**: 브라우저 자동 저장, JSON 내보내기·가져오기 (잘못된 파일이면 기존 목록 보호)

### 🤖 AI 활용 과정
- `PRD.md`로 요구사항을 먼저 정하고, `PROMPTS.md`의 **5단계**(기본 흐름 → 일정 → 대시보드 → 검색·집중 → 저장)로 나누어 하나씩 구현했습니다.
- 교재 06에서는 첫 버전의 화면 캡처를 AI에게 보여 주고 UI를 개선했습니다. 첫 버전은 [`web_version/`](./Study-02/web_version/README.md)에 그대로 보관했습니다.
- 단계마다 브라우저에서 둥지 → 알 → 키위새 → 완료 취소 시 알로 돌아가는 상태 전환을 반복해서 확인했습니다.

### 🛠️ 기술 스택
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Storage**: 브라우저 `localStorage`, JSON 파일 백업
- **설치·API·계정**: 모두 불필요

### 🚀 실행 방법
- **온라인**: [▶ 바로 열기](https://kiwisoop.github.io/ai-practice-course/Study-02/)
- **로컬**: `Study-02/index.html`을 브라우저에서 더블 클릭합니다.

### 🧪 테스트 실행
```bash
cd Study-02
node check.js   # 자동 분류 규칙 검사
```

---

## 3. [Study-03] 상식 한 바퀴: 출처를 확인하는 퀴즈 (Source-Checked Quiz)

교재 「할루시네이션 없는 AI 콘텐츠 만들기」를 바탕으로 만든 4지선다 퀴즈입니다. 한국사·과학·지리·일반상식·컴퓨터공학 각 10문제, 총 50문제이며, 답하면 **정답·해설·출처**가 함께 표시됩니다.

### ✨ 주요 기능
- **📚 출처가 붙은 50문제**: 모든 문제에 고유 ID·출처·확인 기록 보관
- **🎮 4가지 모드**: 기본 50문제 / 스피드(문제당 15초, 힌트로 오답 2개 제외) / 분야별 연습 / 오늘의 퀴즈(날짜별 10문제)
- **🏆 순위 저장**: 이름을 입력한 결과를 브라우저에 저장, 공동 순위 표시
- **👩‍🏫 교사 대시보드**: 학생 기록 JSON을 모아 순위·평균·학습용 등급 확인, CSV·HTML 보고서 내보내기
- **🛠️ 커스텀 명령어 10개** ([`.claude/commands/`](./Study-03/.claude/commands)): 문제 추가(`/quiz-add`), 검증(`/quiz-validate`, `/quiz-check`), 통계(`/quiz-stats`, `/quiz-range`), 보고서(`/create-report`, `/export-report`) 등
- **⌨️ 접근성**: 키보드 조작, 색상 외 정답·오답 표시, 모바일 320px 대응

### 🤖 AI 활용 과정
- AI가 만든 문제를 그대로 쓰지 않고 **출처 본문과 대조**해 할루시네이션을 걸렀습니다. → [출처 검토 기록](./Study-03/SOURCE_REVIEW.md)
- 반복 작업을 커스텀 명령어로 만들고, 명령어를 이어서 쓰는 **문제 추가 → 검사 → 통계** 흐름을 구성했습니다. → [확장 기능 사용법](./Study-03/EXTENSIONS.md)

### 🛠️ 기술 스택
- **Frontend**: HTML, CSS, Vanilla JavaScript, localStorage
- **도구**: Python(데이터 생성), Node.js(자동 검사)

### 🚀 실행 방법
- **온라인**: [▶ 바로 열기](https://kiwisoop.github.io/ai-practice-course/Study-03/)
- **로컬**: `Study-03/index.html`을 브라우저에서 더블 클릭합니다. 교사 대시보드는 `teacher_report.html`입니다.

### 🧪 테스트 실행
```bash
cd Study-03
python3 build_data.py      # 문제 원본(questions.json) → 실행용 데이터 생성
node check.js              # 50문제 구성·채점·순위 저장 검사
node check-extensions.js   # 4개 모드·타이머·힌트·교사 보고서 검사
```

---

## 4. [Study-04] FridgeChef: 냉장고 재료 인식·레시피 추천 (Fridge-to-Recipe AI)

냉장고 사진에서 **재료를 인식**하고, 조건에 맞는 **레시피를 생성**해 **사용자별로 저장**하는 Streamlit 앱입니다. 교재 13에서는 역할별 서브에이전트로 코드를 리뷰하고 개선했습니다.

### ✨ 주요 기능
- **1단계 · 재료 인식**: 사진 업로드와 미리보기, 확인된 재료·불확실한 재료 구분
- **2단계 · 맞춤 레시피**: 재료 편집, 난이도·시간·인분·요리 종류·식단 제한 설정, 분량·조리법·추정 칼로리
- **3단계 · 개인 보관함**: 레시피 저장, 폴더 이동, 평점·요리 횟수, 중복 저장 방지, 확인 후 삭제
- **대시보드·프로필**: 저장 레시피 통계, 자주 쓰는 재료 그래프, 취향·제외 재료 반영
- **계정**: 로컬 실습 계정(PBKDF2 해시 저장) 또는 데모 계정

### 🤖 AI 활용 과정
- 교재 12의 **3단계 PRD**(`PRD_step1~3.md`: 이미지 인식 → 레시피 생성 → 저장) 순서대로 개발했습니다.
- 교재 13에서는 **리뷰 → 성능 최적화 → UX 개선** 서브에이전트에 차례로 맡겨 버그 3건을 찾아 고쳤습니다. 수정 전 백업도 남겼습니다. → [13주차 기록](./Study-04/WEEK13.md)
- API 키는 `.env`나 화면 입력으로만 받고 저장소에는 올리지 않았습니다.

### 🛠️ 기술 스택
- **Backend / UI**: Python, Streamlit, Pillow
- **AI**: 학교 FactChat Gateway (사진 인식용 Claude + 레시피 생성용 텍스트 모델)
- **Storage**: SQLite

### 🚀 실행 방법
```bash
cd Study-04
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1   # → http://127.0.0.1:8501
```
실행 후 사이드바의 [API 연결 설정]에 본인 키를 입력합니다. 테스트용 사진은 `assets/fridge-sample.png`입니다. 자세한 내용은 [`Study-04/README.md`](./Study-04/README.md)를 참고하세요.

### 🧪 테스트 실행
```bash
.venv/bin/python -m unittest -v   # 자동 테스트 13개 (임시 DB·모의 API, 키 불필요)
```

---

## 5. [Study-05] 공감 다이어리 & PDF 요약 (Empathy Diary & PDF Summarizer)

교재 14의 두 예제를 **역할별 AI 개발팀(서브에이전트 5개)** 과 함께 만든 로컬 웹 앱입니다.

### 📔 공감 다이어리
- 오늘의 일을 적으면 AI가 **감정을 분석**하고 **공감 메시지**를 돌려줌
- 날씨·기분 선택, 줄노트·엽서·우표 디자인, 브라우저에 기록 저장 (삭제는 확인 후)

### 📄 PDF 요약
- PDF에서 글을 추출해 **일반 / 간단 요약** 생성, 페이지·글자 수 표시
- 10MB·100페이지·60,000자 제한, 원본은 서버에 저장하지 않음

### 🤖 AI 활용 과정
- 기획·백엔드·프런트엔드·QA·AI 통합 역할의 서브에이전트 5개([`.claude/agents/`](./Study-05/.claude/agents))로 역할을 나누어 개발했습니다.
- API 키는 화면 메모리에만 두고, 일기·PDF·키를 서버 파일이나 로그에 남기지 않도록 했습니다.

### 🛠️ 기술 스택
- **Backend**: Python 표준 HTTP 서버, pypdf
- **AI**: 학교 FactChat API
- **Frontend**: HTML, CSS, Vanilla JavaScript, 마루 부리 웹폰트

### 🚀 실행 방법
```bash
cd Study-05
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python server.py
```
- 다이어리: `http://127.0.0.1:8514/`
- PDF 요약: `http://127.0.0.1:8514/index_pdf.html`

### 🧪 테스트 실행
```bash
.venv/bin/python -m unittest discover -v   # 서버·AI 모듈 테스트 12개 (모의 API)
node test_frontend.cjs                     # 프런트엔드 검사
```

---

## 6. [Study-06] 쇼핑 리스트 + MCP 연동 (Shopping List with MCP)

Claude Code에 **MCP 5개를 직접 설치**하고 교재 15·16의 프롬프트를 그대로 입력해, 쇼핑 리스트 앱을 만들고 자동 검사·문서화·GitHub 배포까지 진행했습니다.

### ✨ 주요 기능 (쇼핑 리스트 앱)
- 상품 추가(Enter 또는 버튼), 구매 체크·해제, 개별 삭제
- 전체 / 완료 / 남은 항목 집계
- 브라우저 자동 저장과 새로고침 복원

### 🔌 MCP 실습 내용
| MCP | 한 일 |
| :--- | :--- |
| **Playwright** | 앱의 추가·체크·삭제를 자동으로 테스트하고 스크린샷 저장 |
| **Notion** | Claude Code 업데이트 요약, 체류 시간 늘리기 구상 등 페이지 3개 저장 |
| **Sequential Thinking** | 7단계로 생각을 나누어 4단계 로드맵 작성 → Notion 페이지 갱신 |
| **Context7** | Claude Code에 설치·연결 확인. 문서 조회(`/microsoft/playwright-mcp`)는 처음 버전에서 수행 |
| **GitHub** | [shopping-list-app](https://github.com/kiwisoop/shopping-list-app) 저장소 생성·업로드 |

실제로 호출된 도구와 횟수, 막혔던 문제 4가지와 해결 방법은 **[Claude Code 실행 기록](./Study-06/claude-code-rerun/README.md)** 에 있습니다.

### 🛠️ 기술 스택
- **Frontend**: HTML, CSS, Vanilla JavaScript (단일 파일), localStorage
- **도구**: Claude Code + MCP 5개

### 🚀 실행 방법
- **온라인**: [▶ 바로 열기](https://kiwisoop.github.io/ai-practice-course/Study-06/claude-code-rerun/shopping-list.html)
- **로컬**: `Study-06/claude-code-rerun/shopping-list.html`을 브라우저에서 엽니다.

### 🧪 테스트 실행
```bash
cd Study-06
python3 test_shopping_list.py   # Playwright MCP로 6개 시나리오 자동 검사 (Node.js 필요)
```

---

## ⭐ 7. 기말 프로젝트 · 3년 다이어리

기말 프로젝트는 별도 저장소로 분리했습니다. → **[kiwisoop/same-day-diary](https://github.com/kiwisoop/same-day-diary)**

같은 날짜의 일기를 3년 동안 쌓으면, AI가 일기를 짧은 이야기·수채화·목소리가 담긴 세로 쇼츠 영상으로 만들어 줍니다.

---

## 📋 교재별 실습 확인표

| 교재 | 실습 내용 | 결과물 |
| :---: | --- | --- |
| 01 | AI 어시스턴트, 클로드로 웹페이지 만들기 | [Study-00 시작 홈페이지](./Study-00/README.md#1-교재-01--시작-홈페이지) |
| 02 | 좋은 프롬프트·PRD 쓰기, 마케팅 포트폴리오 | [Study-00 프롬프트 비교](./Study-00/README.md#2-교재-02--프롬프트-비교) · [포트폴리오](./Study-00/README.md#3-교재-02--마케팅-포트폴리오) |
| 03 | Claude Code 설치, 손글씨 인식 | [Study-01](./Study-01/README.md) |
| 04 | `/init`·`/model` 등 단계별 프롬프트 | [Study-02](./Study-02/README.md) |
| 05 | `/compact`·`/resume`, 자동 분류 | [Study-02](./Study-02/README.md) |
| 06 | 화면 캡처로 UI 개선, 이전 버전 보관 | [Study-02/web_version](./Study-02/web_version/README.md) |
| 07 | 출처 확인으로 할루시네이션 막기 | [Study-03 출처 검토](./Study-03/SOURCE_REVIEW.md) |
| 08 | 커스텀 명령어 만들기 | [Study-03 명령어](./Study-03/.claude/commands) |
| 09 | 명령어 체이닝·상대평가 보고서·CSV | [Study-03 확장 기능](./Study-03/EXTENSIONS.md) · [report_detailed.csv](./Study-03/report_detailed.csv) |
| 10 | Obsidian·Claudian | 플러그인 설치·연결 확인 (개인 볼트라 결과 파일 없음) |
| 11 | API 키 설정·`.gitignore` | [Study-04](./Study-04/README.md) |
| 12 | 3단계 PRD로 API 앱 만들기 | [Study-04](./Study-04/README.md) |
| 13 | 리뷰·최적화·UX 서브에이전트 | [Study-04 13주차 기록](./Study-04/WEEK13.md) |
| 14 | AI 개발팀으로 앱 2개 만들기 | [Study-05](./Study-05/README.md) |
| 15 | Notion·Sequential Thinking MCP | [Claude Code 실행 기록](./Study-06/claude-code-rerun/README.md) (Notion 페이지 3개) |
| 16 | Context7·Playwright·GitHub MCP | [Claude Code 실행 기록](./Study-06/claude-code-rerun/README.md) · [shopping-list-app](https://github.com/kiwisoop/shopping-list-app) |

<details>
<summary>교재와 다르게 진행한 부분</summary>

- **도구:** 교재는 Claude Code 기준이지만 일부 실습은 Codex와 함께 했습니다. 작업 규칙은 `AGENTS.md`에 있고, 각 폴더의 `CLAUDE.md`가 이를 불러옵니다.
- **API:** 교재의 OpenRouter 대신 학교에서 제공한 API 게이트웨이(FactChat)를 사용했습니다.
- **교재 09:** 보고서 예시는 가상 학생 10명의 기록(`examples/sample-records.json`)으로 만들었습니다.
- **교재 15·16:** 처음에는 Codex에 연결된 도구로 대신했다가, 이후 Claude Code에 MCP를 직접 설치해 교재 프롬프트 그대로 다시 했습니다([실행 기록](./Study-06/claude-code-rerun/README.md)). 처음 버전은 [Study-06 README](./Study-06/README.md)에 남겨 두었습니다.

</details>

---

## 📂 저장소 디렉터리 구조

```text
ai-practice-course/
├── README.md                      # 저장소 전체 안내 및 프로젝트 설명서
├── SCREENSHOTS.md                 # 전체 프로젝트 실행 화면 갤러리
│                                  # (각 Study 폴더에도 자세한 SCREENSHOTS.md가 있음)
├── docs/images/                   # README용 화면 캡처
├── Study-00/                      # [프로젝트 0] 교재 01·02 웹페이지 실습 (Web)
│   ├── 01-start-page/             # 교재 01 시작 홈페이지
│   ├── 02-prompt-compare/         # 모호한 vs 구체적인 프롬프트 결과 비교
│   ├── 02-portfolio/              # PRD·5단계 프롬프트·뼈대 단계·완성 포트폴리오
│   ├── screenshots/               # 실행 화면
│   └── README.md
├── Study-01/                      # [프로젝트 1] 손글씨 숫자 인식 (Python)
│   ├── mnist_model.py             # 공통 모델: 학습·불러오기, 이미지 전처리, 예측
│   ├── mnist_model.keras          # 학습된 모델 (두 버전이 함께 사용)
│   ├── desktop_version/           # Tkinter 데스크톱 버전 + Windows 실행 배치 파일
│   ├── web_version/               # 웹 버전 (Python 서버 + HTML Canvas)
│   ├── tests/                     # 이미지 전처리 테스트
│   ├── AGENTS.md                  # AI에게 제공한 작업 규칙
│   └── README.md                  # OS별 실행 안내와 AI 활용 과정
├── Study-02/                      # [프로젝트 2] Kiwibird 할 일 관리 (Web)
│   ├── index.html / styles.css / script.js   # 앱 화면과 동작
│   ├── classification.js          # 키워드 자동 분류 (5주차)
│   ├── check.js                   # 자동 분류 검사
│   ├── assets/                    # 키위새·둥지 이미지
│   ├── web_version/               # 화면 개선 전 첫 버전 보관 (교재 06)
│   ├── PRD.md / PROMPTS.md        # 요구사항과 5단계 구현 프롬프트
│   ├── screenshots/               # 실행 화면
│   └── README.md
├── Study-03/                      # [프로젝트 3] 상식 한 바퀴 퀴즈 (Web)
│   ├── index.html / styles.css / quiz.js     # 퀴즈 화면과 동작
│   ├── teacher_report.html / teacher.js      # 교사 대시보드
│   ├── questions.json             # 문제·정답·해설·출처 원본
│   ├── build_data.py / check.js   # 실행용 데이터 생성과 검사
│   ├── check-extensions.js        # 4개 모드·힌트·교사 보고서 검사
│   ├── .claude/commands/          # 커스텀 명령어 10개
│   ├── SOURCE_REVIEW.md           # 출처 재검토 기록
│   ├── EXTENSIONS.md              # 확장 기능 사용법
│   ├── screenshots/               # 실행 화면
│   └── README.md
├── Study-04/                      # [프로젝트 4] FridgeChef (Streamlit + AI)
│   ├── app.py                     # Streamlit 화면
│   ├── api.py                     # 학교 API 호출 (이미지 인식·레시피 생성)
│   ├── storage.py                 # SQLite 저장
│   ├── test_*.py                  # 자동 테스트
│   ├── PRD_step1~3.md             # 단계별 요구사항
│   ├── .claude/agents/            # 리뷰·최적화·UX 서브에이전트 (교재 13)
│   ├── WEEK13.md                  # 13주차 서브에이전트 개선 기록
│   ├── screenshots/               # 실행 화면
│   └── README.md
├── Study-05/                      # [프로젝트 5] 공감 다이어리 · PDF 요약 (Python + AI)
│   ├── index.html / index_pdf.html           # 다이어리·PDF 요약 화면
│   ├── server.py                  # 로컬 서버
│   ├── ai.py                      # 감정 분석·PDF 추출과 요약
│   ├── test_*.py / test_frontend.cjs         # 자동 테스트
│   ├── .claude/agents/            # AI 개발팀 서브에이전트 5개
│   ├── screenshots/               # 실행 화면
│   └── README.md
└── Study-06/                      # [프로젝트 6] 쇼핑 리스트 + MCP (Web)
    ├── claude-code-rerun/         # ⭐ Claude Code + MCP 실행 기록 (먼저 볼 자료)
    ├── shopping-list.html         # 처음 버전 앱
    ├── test_shopping_list.py      # Playwright MCP 자동 검사
    ├── notion-notes/              # Notion·Sequential Thinking 결과 원본
    ├── screenshots/               # 실행 화면과 자동 검사 캡처
    └── README.md
```
