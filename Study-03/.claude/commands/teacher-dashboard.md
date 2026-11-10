---
description: 교사 대시보드와 내보내기를 안내한다
argument-hint: "[기록파일.json]"
---

Study-03의 teacher_report.html을 연다. 학생이 퀴즈 완료 화면에서 내보낸 JSON을 파일 선택으로 가져오고, 모드별 순위·정답률·등급·분야별 평균과 CSV/HTML 내보내기를 사용한다.

파일 인수를 전달한 경우 안전한 경로인지 확인하고 `node teacher_cli.js --records 기록파일.json --format html --output 새보고서.html`로 로컬 HTML을 생성할 수 있다. 기존 파일은 덮어쓰지 않는다. 성적은 예시 기준이며 공식 성적이 아니다. 허가 없이 개인 기록을 GitHub에 올리지 않는다.
