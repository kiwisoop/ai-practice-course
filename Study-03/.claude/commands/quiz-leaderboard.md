---
description: 내보낸 JSON 기록으로 순위를 분석한다
argument-hint: "기록파일.json [normal|speed|practice|daily]"
---

Study-03에서 기록 파일의 경로와 모드를 검증한 뒤 `node teacher_cli.js --records 기록파일.json --mode 모드`를 실행한다. 경로는 개별 인수로 안전하게 전달하고 셸 코드로 실행하지 않는다. 이름과 점수는 외부 전송하지 않는다. 학습용 등급을 공식 성적으로 표현하지 않는다.
