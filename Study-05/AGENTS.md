# Study-05 작업 규칙

- PRD.md와 14주차 교재의 공감 다이어리·PDF 요약 흐름을 따른다.
- Python 표준 HTTP 서버, pypdf와 기본 HTML·CSS·JavaScript를 사용한다.
- API 키는 화면 메모리에서만 다루며 일기·PDF·키를 서버 파일이나 로그에 기록하지 않는다.
- 일기는 브라우저에 저장하며 저장 실패·손상 시 기존 데이터를 덮어쓰지 않는다. 삭제는 확인 후 실행한다.
- 사용자와 AI 텍스트는 textContent로 렌더링하고 HTML로 해석하지 않는다.
- mock 검사와 실제 API 호출을 구분해 기록한다. 외부 업로드·제출·실 API 전송은 사용자 승인 범위에서 수행한다.
- 테스트: python -m unittest discover -v, node --check app.js.
