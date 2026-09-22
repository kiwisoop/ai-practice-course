# 3주차 — MNIST 손글씨 숫자 인식 프로그램

국립목포대학교 **인공지능활용실습 3주차 과제**입니다. 사용자가 마우스나 터치로 0부터 9까지 숫자 하나를 그리면, MNIST 데이터로 학습한 합성곱 신경망(CNN)이 숫자와 신뢰도를 표시합니다.

이 프로젝트는 같은 인공지능 모델을 다음 두 환경에서 사용합니다.

- **데스크톱 버전:** Python과 Tkinter로 실행
- **웹 버전:** Python 로컬 서버와 웹 브라우저로 실행

## 주요 기능

- 손으로 그린 숫자 0~9 인식
- 예측 숫자와 신뢰도 표시
- 빈 화면 인식 요청 시 안내 메시지 표시
- 데스크톱과 웹 버전이 같은 모델 및 이미지 전처리 코드 공유
- 학습된 모델 포함: 처음 실행할 때 다시 학습할 필요 없음
- 마우스와 터치 입력 지원(웹 버전)

## 실행 화면 사용법

1. 검은색 입력 영역에 흰색으로 숫자 하나를 크게 그립니다.
2. `Recognize` 버튼을 누릅니다.
3. 화면 아래에서 예측 숫자와 신뢰도를 확인합니다.
4. 다시 입력하려면 `Clear` 버튼을 누릅니다.

숫자는 입력 영역 중앙에 한 개만 그리고, 서로 붙지 않은 여러 숫자는 입력하지 않는 것이 좋습니다.

## 준비 사항

- 64비트 Windows, macOS 또는 Ubuntu
- Python **3.11 권장**
- 인터넷 연결: 최초 라이브러리 설치 시 필요
- 웹 버전 실행용 최신 웹 브라우저

TensorFlow 공식 설치 안내는 Python과 `pip`를 이용한 가상환경 설치를 권장합니다. 이 과제는 GPU가 없어도 실행되며, 포함된 모델을 CPU로 불러와 예측합니다.

- [Python 가상환경 공식 문서](https://docs.python.org/3/library/venv.html)
- [TensorFlow 공식 설치 문서](https://www.tensorflow.org/install/pip)

## 프로젝트 내려받기

Git이 설치되어 있다면 저장소를 복제합니다.

```bash
git clone https://github.com/kiwisoop/ai-practice-course.git
cd ai-practice-course/Study-01
```

Git을 사용하지 않는 경우 GitHub의 `Code` → `Download ZIP`을 누르고 압축을 푼 다음 `Study-01` 폴더로 이동합니다.

---

## Windows 설치 및 실행

### 방법 1: 배치 파일로 간단히 실행

1. [Python 공식 사이트](https://www.python.org/downloads/)에서 Python 3.11 64비트를 설치합니다.
2. 설치 화면에서 **Add Python to PATH**를 선택합니다.
3. `Study-01/desktop_version/run_desktop.bat`을 더블 클릭하면 데스크톱 버전이 실행됩니다.
4. 웹 버전은 `Study-01/web_version/run_web.bat`을 더블 클릭합니다.
5. 웹 버전이 실행되면 브라우저에서 <http://127.0.0.1:8000>을 엽니다.

배치 파일은 처음 실행할 때 `.venv` 가상환경을 만들고 필요한 라이브러리를 자동으로 설치합니다. 설치가 끝난 뒤에는 같은 파일을 다시 실행하면 됩니다.

### 방법 2: 명령 프롬프트에서 직접 실행

`Study-01` 폴더에서 명령 프롬프트를 열고 다음 명령을 입력합니다.

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

데스크톱 버전:

```bat
python desktop_version\digit_recognition.py
```

웹 버전:

```bat
python web_version\server.py
```

웹 서버를 종료하려면 명령 프롬프트에서 `Ctrl+C`를 누릅니다.

> 이 과제는 Windows에서 CPU로 실행할 수 있습니다. 최신 TensorFlow의 Windows 네이티브 GPU 지원은 제한되지만, 이 과제에는 GPU가 필요하지 않습니다.

---

## macOS 설치 및 실행

터미널을 열고 `Study-01` 폴더로 이동한 뒤 다음 명령을 입력합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

데스크톱 버전:

```bash
python desktop_version/digit_recognition.py
```

웹 버전:

```bash
python web_version/server.py
```

브라우저가 자동으로 열리지 않으면 <http://127.0.0.1:8000>에 접속합니다. 웹 서버는 터미널에서 `Ctrl+C`를 눌러 종료합니다.

macOS에서는 TensorFlow가 CPU로 실행됩니다. Apple Silicon과 Intel Mac 모두 Python과 TensorFlow가 지원하는 조합을 사용해야 하므로, 설치 오류가 생기면 Python 3.11 환경을 권장합니다.

---

## Ubuntu 설치 및 실행

Ubuntu 터미널에서 Python 가상환경과 Tkinter를 준비합니다.

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip python3-tk
```

`Study-01` 폴더로 이동한 뒤 가상환경을 만들고 라이브러리를 설치합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

데스크톱 버전:

```bash
python desktop_version/digit_recognition.py
```

웹 버전:

```bash
python web_version/server.py
```

브라우저에서 <http://127.0.0.1:8000>에 접속합니다. 웹 서버는 터미널에서 `Ctrl+C`를 눌러 종료합니다.

화면이 없는 원격 Ubuntu 서버에서는 데스크톱 창을 띄울 수 없으므로 웹 버전을 사용하되, 이 서버는 안전을 위해 현재 컴퓨터의 `127.0.0.1`에서만 접속되도록 설정되어 있습니다.

## 설치 확인 및 테스트

가상환경을 활성화한 상태에서 다음 명령으로 설치를 확인합니다.

```bash
python -c "import tensorflow, numpy, PIL; print('설치 완료')"
python -m unittest discover -s tests
```

정상이라면 테스트 2개가 실행되고 마지막에 `OK`가 표시됩니다. 테스트는 다음 내용을 검사합니다.

- 그린 숫자가 MNIST 입력 형식인 `1 × 28 × 28 × 1` 배열로 변환되는지
- 아무것도 그리지 않은 이미지를 올바르게 거부하는지

## 프로그램 처리 과정

```text
사용자가 숫자를 그림
        ↓
숫자가 있는 영역만 잘라냄
        ↓
긴 변을 20픽셀로 줄이고 28×28 이미지 중앙에 배치
        ↓
픽셀값을 0~1 범위로 정규화
        ↓
MNIST CNN 모델에 입력
        ↓
예측 숫자와 신뢰도 출력
```

`mnist_model.py`가 모델 로딩, 이미지 전처리, 예측을 담당합니다. 데스크톱 버전과 웹 버전은 이 파일을 함께 사용하므로 같은 기능을 중복해서 구현하지 않았습니다.

## AI를 활용한 개발 과정

이 과제에서는 AI를 결과물만 만드는 도구가 아니라 **계획, 구현, 점검을 돕는 개발 도구**로 사용했습니다.

1. **과제 요구사항 확인**
   - MNIST 숫자 인식, 실행 가능한 Python 프로그램, Windows 실행 파일이라는 핵심 요구를 정리했습니다.
   - 모든 코드와 주석은 영어로 작성한다는 규칙을 정했습니다.
2. **첫 번째 프로그램 제작**
   - AI에게 손글씨 숫자를 입력받아 인식하는 프로그램 제작을 요청했습니다.
   - 생성된 코드를 그대로 끝내지 않고 모델 입력 형태와 실행 흐름을 확인했습니다.
3. **환경 재현 준비**
   - 필요한 라이브러리를 `requirements.txt`에 기록했습니다.
   - 다른 컴퓨터에서도 같은 환경을 만들 수 있도록 `.venv` 가상환경 방식을 사용했습니다.
4. **데스크톱과 웹 버전 분리**
   - 공통 인공지능 코드는 `mnist_model.py`에 두고 화면 부분만 분리했습니다.
   - `desktop_version`에는 Tkinter 프로그램을, `web_version`에는 브라우저 프로그램을 배치했습니다.
5. **AI 작업 규칙 기록**
   - 루트와 각 버전 폴더의 `AGENTS.md`에 프로젝트 구조, 실행 명령, 코드 작성 규칙을 기록했습니다.
   - 이후 AI가 파일을 수정할 때도 같은 구조와 규칙을 따르도록 했습니다.
6. **검증 및 수정**
   - 전처리 테스트를 작성해 숫자 크기·배치와 빈 입력 처리를 확인했습니다.
   - 학습된 모델을 직접 불러오고 웹 예측 요청이 정상 응답하는지 확인했습니다.
   - 과제 폴더를 교재와 같은 `Study-01` 이름으로 정리하고 GitHub 링크를 다시 확인했습니다.
7. **버전 관리**
   - 작업 단계를 Git 커밋으로 나누어 변경 과정을 남겼습니다.
   - GitHub 저장소에서 과제별 폴더가 구분되도록 구성했습니다.

### AI 사용 시 확인한 점

- AI가 만든 코드도 직접 실행하고 오류 여부를 확인했습니다.
- 설치되지 않은 라이브러리는 가상환경에 설치한 뒤 테스트했습니다.
- 불필요한 파일과 중복 설명은 정리하고, 필요한 실행 방법은 README에 통합했습니다.
- API 키, 비밀번호, 개인 메모, 가상환경은 GitHub에 올리지 않았습니다.

### 과정 확인 자료

- `AGENTS.md`: AI에게 제공한 공통 개발 규칙
- `desktop_version/AGENTS.md`: 데스크톱 버전 규칙
- `web_version/AGENTS.md`: 웹 버전 규칙
- `tests/test_preprocessing.py`: 기능 검증 코드
- Git 커밋 기록: 최초 구현, 구조 정리, 문서 수정 과정을 확인할 수 있는 변경 이력

## 폴더 구조

```text
Study-01/
├── AGENTS.md                       # AI 공통 작업 규칙과 프로젝트 설명
├── README.md                       # 설치, 실행, 개발 과정 문서
├── mnist_model.keras               # 미리 학습된 MNIST 모델
├── mnist_model.py                  # 공통 모델 로딩, 전처리, 예측 코드
├── requirements.txt                # Python 라이브러리 목록
├── desktop_version/
│   ├── AGENTS.md                   # 데스크톱 버전 작업 규칙
│   ├── digit_recognition.py        # Tkinter 데스크톱 프로그램
│   └── run_desktop.bat             # Windows 데스크톱 실행 파일
├── web_version/
│   ├── AGENTS.md                   # 웹 버전 작업 규칙
│   ├── server.py                   # 로컬 웹 서버와 예측 API
│   ├── run_web.bat                 # Windows 웹 버전 실행 파일
│   ├── templates/index.html        # 웹 화면
│   └── static/
│       ├── app.js                  # 그리기 및 예측 요청
│       └── style.css               # 웹 화면 스타일
└── tests/
    └── test_preprocessing.py       # 이미지 전처리 테스트
```

## 파일 정리 기준

| 구분 | 처리 | 이유 |
|---|---|---|
| `SUBMISSION.md` | README에 통합 후 삭제 | 과제 설명과 README 내용이 중복됨 |
| `mnist_model.keras` | 유지 | 재학습 없이 바로 실행하기 위해 필요 |
| `tests/` | 유지 | 결과뿐 아니라 검증 과정을 보여줌 |
| `AGENTS.md` 3개 | 유지 | AI에게 제공한 작업 규칙과 단계별 구조를 보여줌 |
| `run_desktop.bat`, `run_web.bat` | 유지 | Windows에서 더블 클릭으로 실행할 수 있음 |
| `.venv`, `__pycache__`, `.DS_Store`, `memo.txt` | GitHub에서 제외 | 개인 환경·캐시·임시 파일이며 다른 컴퓨터에서 다시 생성 가능 |

## 주요 파일 설명

- `mnist_model.py`
  - 저장된 모델이 있으면 불러옵니다.
  - 모델이 없을 때만 MNIST 데이터를 내려받아 3회 학습하고 저장합니다.
  - 입력 이미지를 자르고 중앙 정렬한 뒤 예측합니다.
- `desktop_version/digit_recognition.py`
  - Tkinter 입력창, Clear 버튼, Recognize 버튼을 제공합니다.
- `web_version/server.py`
  - 정적 웹 파일을 제공하고 `/predict` 요청을 처리합니다.
  - 입력 크기를 제한하고 잘못된 요청에는 오류 메시지를 반환합니다.
- `web_version/static/app.js`
  - 마우스·터치 그리기, 초기화, 서버 예측 요청을 처리합니다.

## 문제 해결

### `python` 또는 `python3` 명령을 찾을 수 없음

Python을 설치한 뒤 터미널을 완전히 닫았다가 다시 엽니다. Windows에서는 설치할 때 `Add Python to PATH`를 선택했는지 확인합니다.

### `No matching distribution found for tensorflow`

64비트 Python인지 확인하고 Python 3.11로 새 가상환경을 만듭니다. 기존 `.venv`를 다른 운영체제에서 복사해 사용하지 말고 해당 컴퓨터에서 새로 생성해야 합니다.

### Ubuntu에서 `No module named tkinter`

```bash
sudo apt install -y python3-tk
```

### 브라우저가 열리지 않음

서버가 실행 중인 터미널을 닫지 말고 브라우저 주소창에 <http://127.0.0.1:8000>을 직접 입력합니다.

### 인식 결과가 부정확함

- 숫자를 입력 영역 중앙에 크게 그립니다.
- 한 번에 숫자 하나만 그립니다.
- 너무 가늘거나 끊어진 선을 피합니다.
- `Clear`를 누른 뒤 다시 입력합니다.

## 한계

- MNIST 숫자 0~9만 인식하며 문자나 여러 자리 숫자는 지원하지 않습니다.
- 신뢰도는 모델의 예측 확률이며 정답을 보장하지 않습니다.
- 웹 서버는 과제 실습용 로컬 서버이며 외부 공개 서비스용이 아닙니다.

## 느낀 점

모델을 만드는 것뿐 아니라 실제 사용자가 그린 이미지를 학습 데이터와 비슷한 형태로 바꾸는 전처리가 중요하다는 것을 확인했습니다. 또한 AI가 코드를 빠르게 작성해 주더라도 요구사항 정리, 실행 환경 구성, 테스트, 오류 확인, 파일 구조 정리는 사용자가 직접 판단하고 검증해야 한다는 점을 배웠습니다.
