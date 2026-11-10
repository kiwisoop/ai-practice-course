---
description: 분야와 난이도로 새 문제를 검토한 뒤 확장 문제은행에 추가한다
argument-hint: "분야 난이도"
---

Study-03에서 `$1`을 기존 5개 분야 중 하나로, `$2`를 입문·중급·고급 중 하나로 검증한다. 알 수 없는 값은 설명을 요청하며 인수를 셸 코드로 실행하지 않는다.

1. AGENTS.md와 questions.json, extra-questions.json, examples/add-question.json을 읽는다. 중복 없는 ID와 질문으로 인수에 맞는 새 JSON 후보를 작성한다.
2. 실제 출처 본문과 질문·보기·정답·해설을 대조한다. 미확인 후보는 review_status를 verified로 설정하거나 적용하지 않는다.
3. 확인된 JSON에 difficulty와 review_status, 실제 확인일·출처·근거를 기록한다. `python3 quiz_tools.py add 후보파일.json`으로 추가 전 검사한다.
4. 사용자의 문제 추가 요청 범위에서 `python3 quiz_tools.py add 후보파일.json --apply`를 실행한다. 추가→데이터 생성→검사가 연결되며 실패하면 추가 데이터를 복구한다.
5. `python3 quiz_tools.py stats`로 결과를 확인한다. 기본 50문제는 유지하고 새 문제는 오늘의 퀴즈 후보에 포함된다. 확인한 근거와 실제 결과를 보고한다.
