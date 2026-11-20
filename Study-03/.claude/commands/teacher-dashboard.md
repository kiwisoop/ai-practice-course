---
description: 교사 대시보드와 보고서 생성·내보내기를 이어서 실행한다
argument-hint: "[기록파일.json]"
---

Study-03의 teacher_report.html을 연다. 학생이 퀴즈 완료 화면에서 내보낸 JSON을 파일 선택으로 가져오고, 모드별 순위·정답률·등급·분야별 평균과 CSV/HTML 내보내기를 사용한다.

파일 인수를 전달하면 다음 순서로 명령어를 이어서 실행한다(명령어 체이닝).

1. `/quiz-check` — 문제 데이터와 기록 검사
2. `/create-report <파일>` — 상대평가 등급 보고서
3. `/export-report <파일> csv` — `report_detailed.csv` 저장

경로가 안전한지 확인하고 기존 파일은 덮어쓰지 않는다. 성적은 예시 기준이며 공식 성적이 아니다. 허가 없이 개인 기록을 GitHub에 올리지 않는다.
