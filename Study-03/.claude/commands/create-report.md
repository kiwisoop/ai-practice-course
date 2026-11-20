---
description: 퀴즈 기록으로 상대평가 등급 보고서를 만든다
argument-hint: "[기록파일.json]"
---

Study-03에서 인수로 받은 기록 파일(없으면 `examples/sample-records.json`)로 등급 보고서를 만든다.

1. `node teacher_cli.js --records <파일> --mode normal --grading relative --format json`을 실행한다.
2. 등급은 **상대평가**다. 순위 상위 10% A, 30%까지 B, 70%까지 C, 90%까지 D, 나머지 F이며 동점자는 같은 등급을 받는다.
   (교재 09: 처음 절대평가로 만들었더니 평균 점수 기준이라 등급이 한쪽으로 몰려 상대평가로 고쳤다.)
3. 순위·이름·점수·등급을 표로 요약하고, 등급별 인원과 평균 정답률을 알려 준다.

성적은 학습용 예시이며 공식 성적이 아니다. 실제 학생 기록은 GitHub에 올리지 않는다.
