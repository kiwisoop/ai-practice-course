# 3주차 — MNIST 손글씨 숫자 인식 프로그램

Codex를 이용해 만든 인공지능활용실습 과제입니다. 마우스나 터치로 0부터 9까지 숫자를 그리면 MNIST 데이터로 학습한 합성곱 신경망이 숫자와 신뢰도를 표시합니다.

## 바로 실행하기

- Python 3.11 권장, 3.9 이상 사용 가능
- 학습된 모델 `mnist_model.keras`가 포함되어 있어 별도 학습 없이 실행 가능

```text
python -m pip install -r requirements.txt
python web_version/server.py
```

실행 후 브라우저에서 `http://127.0.0.1:8000`을 엽니다.

## Windows에서 데스크톱 버전 실행

1. `desktop_version` 폴더를 엽니다.
2. `run_desktop.bat`을 더블 클릭합니다.
3. 첫 실행 시 설치와 학습이 끝날 때까지 기다립니다.
4. 검은 상자에 숫자를 그리고 `Recognize`를 누릅니다.

## Windows에서 웹 버전 실행

1. `web_version` 폴더를 엽니다.
2. `run_web.bat`을 더블 클릭합니다.
3. 학습이 끝나면 브라우저가 자동으로 열립니다.
4. 검은 상자에 숫자를 그리고 `Recognize`를 누릅니다.
5. 종료하려면 명령 프롬프트에서 `Ctrl+C`를 누릅니다.

## 데스크톱 버전 터미널 실행

```text
python -m pip install -r requirements.txt
python desktop_version/digit_recognition.py
```

## 검사

```text
python -m unittest discover -s tests
```

## 폴더 구조

```text
week03-handwriting/
├── .gitignore
├── AGENTS.md
├── README.md
├── SUBMISSION.md
├── mnist_model.keras
├── mnist_model.py
├── requirements.txt
├── desktop_version/
│   ├── AGENTS.md
│   ├── digit_recognition.py
│   └── run_desktop.bat
├── web_version/
│   ├── AGENTS.md
│   ├── server.py
│   ├── run_web.bat
│   ├── templates/index.html
│   └── static/
│       ├── app.js
│       └── style.css
└── tests/test_preprocessing.py
```

## 제출 파일

과제 제출란에는 이 폴더의 GitHub 주소를 입력하고, 자세한 과제 설명은 `SUBMISSION.md`를 참고합니다.
