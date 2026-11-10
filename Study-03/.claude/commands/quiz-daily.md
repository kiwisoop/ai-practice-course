---
description: 문제 검사·통계·날짜별 퀴즈 생성을 연결한다
argument-hint: "[YYYY-MM-DD]"
---

Study-03에서 `python3 quiz_tools.py check` 성공 후 `python3 quiz_tools.py stats`, `python3 quiz_tools.py daily` 순으로 실행한다. `$ARGUMENTS`가 있으면 ISO 날짜인지 검증한 뒤 daily에 `--date 날짜`를 전달한다. 실패하면 다음 단계를 실행하지 않는다. 보고서는 reports/daily_quiz.json에 생성되며 기본 50문제를 덮어쓰지 않는다.
