[← Study-00 시작 홈페이지](../Study-00/SCREENSHOTS.md) · [전체 갤러리로](../SCREENSHOTS.md) · [다음: Study-02 Kiwibird 할 일 관리 →](../Study-02/SCREENSHOTS.md)

# 🐍 Study-01 · 손글씨 숫자 인식

숫자를 그리면 MNIST로 학습한 인공지능이 어떤 숫자인지와 신뢰도를 알려 주는 프로그램입니다.

## 한눈에 보기

| 항목 | 내용 |
| --- | --- |
| 분류 | 🐍 Python · 교재 03 |
| 하는 일 | 마우스·터치로 그린 숫자 하나 → 예측 숫자와 신뢰도 |
| 기술 | Python, TensorFlow/Keras, NumPy, Pillow, Tkinter, HTML Canvas |
| 실행 방법 | 데스크톱: `desktop_version/run_desktop` · 웹: `web_version/run_web` (Python 필요, API 키 불필요) |
| 자세한 설명 | [README.md](./README.md) |

### 주요 기능

- 손으로 그린 숫자 0–9 인식, 예측 숫자와 신뢰도 표시
- 빈 화면에서 인식을 누르면 안내 메시지 표시
- 데스크톱(Tkinter)과 웹 버전이 같은 모델과 전처리 코드를 공유
- 학습된 모델(`mnist_model.keras`) 포함: 처음 실행할 때 다시 학습할 필요 없음
- 웹 버전은 마우스와 터치 입력 지원

## 화면 보기

### 1. 웹 버전 입력 화면

검은 입력 영역에 숫자를 크게 그리고 `Recognize`를 누르면 아래 `Result`에 예측 숫자와 신뢰도가 나옵니다. `Clear`로 다시 그립니다.

![손글씨 숫자 입력 화면](../docs/images/study01.jpg)

> 이 프로젝트는 TensorFlow가 설치된 Python 환경이 필요해 GitHub Pages로 바로 실행할 수 없습니다. 위 화면은 과제 진행 중(3주차) 로컬에서 캡처한 것입니다.

---

[← Study-00 시작 홈페이지](../Study-00/SCREENSHOTS.md) · [전체 갤러리로](../SCREENSHOTS.md) · [다음: Study-02 Kiwibird 할 일 관리 →](../Study-02/SCREENSHOTS.md)
