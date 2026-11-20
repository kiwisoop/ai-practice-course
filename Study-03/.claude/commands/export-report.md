---
description: 보고서를 CSV(분야별 점수 포함) 또는 HTML 파일로 저장한다
argument-hint: "[기록파일.json] [csv|html]"
---

Study-03에서 `/create-report`와 같은 기준으로 보고서를 파일로 저장한다.

- CSV: `node teacher_cli.js --records <파일> --grading relative --format csv-detailed --output report_detailed.csv`
  - 순위·이름·점수·정답률·등급과 분야별(한국사·과학·지리·일반상식·컴퓨터공학) 점수를 담는다.
- HTML: `node teacher_cli.js --records <파일> --grading relative --format html --output report.html`

기존 파일은 덮어쓰지 않는다. 같은 이름이 있으면 새 이름을 정하고 사용자에게 알린다.
