# 3주차 — MNIST 손글씨 숫자 인식 프로그램

이번 **인공지능활용실습 3주차 과제**에서는 손으로 쓴 숫자를 인식하는 프로그램을 만들었습니다. 검은 화면에 0부터 9까지 숫자 하나를 그리면, MNIST 데이터로 학습한 인공지능이 어떤 숫자인지 예상하고 신뢰도를 함께 보여줍니다.

처음에는 Python 데스크톱 프로그램으로 시작했고, 이후 같은 기능을 브라우저에서도 사용할 수 있도록 웹 버전까지 확장했습니다. 두 버전은 같은 인공지능 모델을 함께 사용합니다.

- **데스크톱 버전:** Python과 Tkinter로 실행
- **웹 버전:** Python 로컬 서버와 웹 브라우저로 실행

## 무엇을 만들었나요?

- 손으로 그린 숫자 0~9 인식
- 예측 숫자와 신뢰도 표시
- 빈 화면 인식 요청 시 안내 메시지 표시
- 데스크톱과 웹 버전이 같은 모델 및 이미지 전처리 코드 공유
- 학습된 모델 포함: 처음 실행할 때 다시 학습할 필요 없음
- 마우스와 터치 입력 지원(웹 버전)

## 사용 방법

1. 검은색 입력 영역에 흰색으로 숫자 하나를 크게 그립니다.
2. `Recognize` 버튼을 누릅니다.
3. 화면 아래에서 예측 숫자와 신뢰도를 확인합니다.
4. 다시 입력하려면 `Clear` 버튼을 누릅니다.

숫자는 입력 영역 가운데에 하나만 크게 그리면 더 잘 인식됩니다.

## 실행 전에 준비할 것

- 64비트 Windows, macOS 또는 Ubuntu
- Python **3.11 권장**
- 인터넷 연결: 최초 라이브러리 설치 시 필요
- 웹 버전 실행용 최신 웹 브라우저

이 프로젝트에는 학습이 끝난 모델이 들어 있어서 GPU가 없어도 실행할 수 있습니다. 아래 설명에서는 다른 Python 프로젝트와 라이브러리가 섞이지 않도록 `.venv`라는 가상환경을 사용합니다.

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

## Windows에서 실행하기

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

## macOS에서 실행하기

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

## Ubuntu에서 실행하기

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

## 제대로 설치되었는지 확인하기

가상환경을 활성화한 상태에서 다음 명령으로 설치를 확인합니다.

```bash
python -c "import tensorflow, numpy, PIL; print('설치 완료')"
python -m unittest discover -s tests
```

정상이라면 테스트 2개가 실행되고 마지막에 `OK`가 표시됩니다. 제가 확인한 내용은 다음과 같습니다.

- 그린 숫자가 MNIST 입력 형식인 `1 × 28 × 28 × 1` 배열로 변환되는지
- 아무것도 그리지 않은 이미지를 올바르게 거부하는지

## 숫자를 어떻게 인식하나요?

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

이 과정은 `mnist_model.py`에서 처리합니다. 데스크톱 버전과 웹 버전이 이 파일을 함께 사용하기 때문에 같은 코드를 두 번 만들지 않아도 됩니다.

## AI와 함께 과제를 진행한 과정

AI에게 한 번에 결과물 전체를 만들어 달라고 하기보다는, 해야 할 일을 작은 단계로 나누어 요청하고 각 단계가 끝날 때마다 직접 확인했습니다.

AI에게 요청한 핵심 내용은 다음과 같습니다.

> 손글씨로 숫자를 입력하면 이를 인식하는 프로그램을 만들어 줘. 코드와 주석은 영어로 작성해 줘.

> 데스크톱 버전과 웹 버전으로 나누고, 공통 모델 코드는 함께 사용할 수 있게 정리해 줘.

> Windows에서 파일을 더블 클릭해 실행할 수 있게 만들어 줘.

### 1. 과제에서 요구하는 내용부터 정리했습니다

먼저 교재를 보면서 MNIST 숫자 인식, Python 프로그램, Windows 실행 파일이 필요하다는 점을 확인했습니다. 프로젝트 폴더와 파일명에는 영문과 숫자를 사용하고, 코드와 주석은 영어로 작성하기로 정했습니다.

### 2. 데스크톱 버전을 먼저 만들었습니다

AI의 도움을 받아 Tkinter로 숫자를 그릴 수 있는 화면을 만들었습니다. `Clear` 버튼으로 입력을 지우고 `Recognize` 버튼을 누르면 숫자와 신뢰도가 나오도록 구성했습니다. 만들어진 코드를 바로 제출하지 않고 실제로 실행해 보면서 버튼과 숫자 입력이 제대로 동작하는지 확인했습니다.

### 3. 실행 환경을 다시 만들 수 있게 정리했습니다

필요한 라이브러리는 `requirements.txt`에 기록했습니다. 또한 다른 컴퓨터에서도 프로젝트 라이브러리만 따로 설치할 수 있도록 `.venv` 가상환경을 사용했습니다. Windows에서는 명령어를 잘 모르는 사람도 실행할 수 있도록 배치 파일을 추가했습니다.

### 4. 같은 기능을 웹 버전으로 확장했습니다

데스크톱 프로그램에서 사용하던 모델과 이미지 처리 코드를 `mnist_model.py`에 모았습니다. 웹 버전은 브라우저에서 그린 이미지를 Python 서버로 보내고, 같은 모델의 결과를 받아 화면에 표시하도록 만들었습니다.

### 5. AI가 참고할 작업 규칙을 남겼습니다

프로젝트 전체와 각 버전 폴더에 `AGENTS.md`를 두었습니다. 이 파일에는 프로젝트 구조, 실행 명령, 코드 작성 규칙을 적었습니다. 덕분에 AI와 작업을 다시 시작해도 이전에 정한 방식을 이어서 사용할 수 있습니다.

### 6. 실행하고 테스트하면서 수정했습니다

AI가 만든 결과도 직접 실행해 확인했습니다. 숫자를 그렸을 때 입력 이미지가 MNIST 형식으로 변환되는지, 빈 화면을 인식하려 할 때 오류를 안내하는지 테스트했습니다. 저장된 모델이 정상적으로 열리는지와 웹 예측 요청이 정상적으로 처리되는지도 확인했습니다.

마지막으로 과제 폴더를 교재와 같은 `Study-01` 이름으로 바꾸고, 중복 문서를 README에 합친 뒤 GitHub 링크가 끊어지지 않는지 다시 확인했습니다.

### 제가 직접 확인한 부분

- AI가 작성한 코드를 실제 환경에서 실행했습니다.
- 필요한 라이브러리를 가상환경에 설치하고 테스트 2개를 실행했습니다.
- 저장된 모델을 불러오고 웹 버전에서 예측 결과가 나오는지 확인했습니다.
- 중복된 설명과 필요 없는 제출 문서를 정리했습니다.
- API 키, 비밀번호, 개인 메모, 가상환경은 GitHub에 올리지 않았습니다.

### 과정을 확인할 수 있는 자료

- `AGENTS.md`: AI에게 제공한 공통 개발 규칙
- `desktop_version/AGENTS.md`: 데스크톱 버전 규칙
- `web_version/AGENTS.md`: 웹 버전 규칙
- `tests/test_preprocessing.py`: 기능 검증 코드
- Git 커밋 기록: 처음 프로그램을 만든 시점부터 구조와 문서를 고친 과정

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

## 파일은 이렇게 정리했습니다

| 구분 | 처리 | 이유 |
|---|---|---|
| `SUBMISSION.md` | README에 통합 후 삭제 | 과제 설명과 README 내용이 중복됨 |
| `mnist_model.keras` | 유지 | 재학습 없이 바로 실행하기 위해 필요 |
| `tests/` | 유지 | 결과뿐 아니라 검증 과정을 보여줌 |
| `AGENTS.md` 3개 | 유지 | AI에게 제공한 작업 규칙과 단계별 구조를 보여줌 |
| `run_desktop.bat`, `run_web.bat` | 유지 | Windows에서 더블 클릭으로 실행할 수 있음 |
| `.venv`, `__pycache__`, `.DS_Store`, `memo.txt` | GitHub에서 제외 | 개인 환경·캐시·임시 파일이며 다른 컴퓨터에서 다시 생성 가능 |

## 각 파일의 역할

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

## 실행이 잘되지 않을 때

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

## 아직 아쉬운 점

- MNIST 숫자 0~9만 인식하며 문자나 여러 자리 숫자는 지원하지 않습니다.
- 신뢰도는 모델의 예측 확률이며 정답을 보장하지 않습니다.
- 웹 서버는 과제 실습용 로컬 서버이며 외부 공개 서비스용이 아닙니다.

## 만들면서 배운 점

처음에는 인공지능 모델만 있으면 손글씨 숫자를 바로 잘 맞힐 수 있을 것이라고 생각했습니다. 하지만 직접 그린 숫자는 MNIST 이미지와 모양이나 위치가 달라서, 숫자 부분을 잘라내고 크기를 맞춘 뒤 가운데로 옮기는 과정이 매우 중요했습니다.

AI를 사용하면 코드를 빠르게 만들 수 있었지만, 실행 환경을 준비하고 결과가 맞는지 테스트하며 파일을 정리하는 일은 직접 확인해야 했습니다. 이번 과제를 통해 AI에게 구체적으로 요청하는 방법뿐 아니라, AI가 만든 결과를 그대로 믿지 않고 실행과 테스트로 검증하는 과정도 중요하다는 점을 배웠습니다.
