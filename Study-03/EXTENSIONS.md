# 8·9주차 보완 기능 사용법

설치·API 키 없이 index.html을 연다. 유지 관리 명령은 Python 3과 Node.js 18 이상이 필요하다. 외부 패키지는 추가하지 않았다.

## 게임

| 모드 | 문제 | 채점 | 힌트 |
| --- | --- | --- | --- |
| 기본 | 기존 고정 50문제 | 정답 1점, 총 50점 | 없음 |
| 스피드 | 기본 50문제, 문제당 15초 | 정답 10점·힌트 후 8점·오답/시간 초과 0점 | 보기 2개 |
| 분야별 연습 | 선택 분야 10문제 | 정답 1점 | 보기 2개, 감점 없음 |
| 오늘의 퀴즈 | 기본+확장 문제은행에서 날짜별 10문제 | 정답 1점 | 보기 2개, 감점 없음 |

같은 로컬 날짜와 같은 문제은행이면 일일 문제가 같다. PC 시계·시간대·문제은행이 바뀌면 달라질 수 있다. 진행 중 날짜가 바뀌어도 현재 게임은 유지된다. 시간 초과도 한 번만 오답 처리하며 해설을 읽고 다음 문제로 이동한다. 완료 후 ‘다른 모드 선택’으로 돌아갈 수 있다.

기록은 모드별로 저장한다. 기존 기본 모드 기록도 읽는다. 분야별 연습의 순위는 선택 분야에 관계없이 연습 모드 완료 기록끼리 비교한다. 일일 순위도 날짜별 분리 없이 일일 모드 기록끼리 비교한다. 정식 평가나 부정행위 방지 시스템은 아니다.

## 교사 보고서

1. 학생은 완료 화면에서 이름을 입력해 결과를 저장하고 ‘선생님 보고서용 기록 JSON 내보내기’를 누른다. 저장하지 않은 결과는 내보내지 않는다.
2. 시작 화면의 ‘선생님 대시보드’ 링크를 누르거나 teacher_report.html을 연다.
3. 기록 JSON을 하나 이상 선택한다. 동일 기록은 중복 집계하지 않는다. 모드를 골라 순위·정답률·평균·분야별 평균 정답 수를 확인한다.
4. CSV 또는 HTML로 내보낸다. HTML에는 자체 스타일을 포함해 별도 CSS 없이 읽을 수 있다. 잘못된 파일을 가져오면 현재 보고서를 유지한다.

등급은 정답률 90% 이상 A, 80% B, 70% C, 60% D, 나머지 F라는 학습용 예시이다. 공식 수업 성적이 아니다. 파일당/전체 가져오기 크기는 최대 10MB, 합산 기록은 최대 10,000개다. 이름과 점수는 개인 정보가 될 수 있으므로 공개 저장소에 올리지 않는다. 서버로 전송하지 않으며 브라우저 보고서의 가져온 내용은 새로고침하면 초기화된다.

CLI에서도 같은 검증·순위·등급 함수를 사용한다. 출력 경로가 이미 있으면 덮어쓰지 않는다.

```sh
node teacher_cli.js --records quiz-records.json --mode normal
node teacher_cli.js --records quiz-records.json --mode practice --format csv --output report.csv
node teacher_cli.js --records quiz-records.json --format html --output report.html
```

## 반복 명령과 체이닝

아래 명령은 Study-03 폴더에서 실행한다. 형식 검사는 정답의 사실 검증을 대신하지 않는다.

```sh
python3 quiz_tools.py validate 한국사
python3 quiz_tools.py range 1 20
python3 quiz_tools.py check
python3 quiz_tools.py stats
python3 quiz_tools.py daily --date 2026-11-10
node check-extensions.js
python3 check_tools.py
```

`.claude/commands/`에 quiz-validate, quiz-range, quiz-add, quiz-check, quiz-stats, quiz-leaderboard, quiz-daily, teacher-dashboard를 제공한다. 해당 폴더를 프로젝트로 연 Claude에서 사용할 명령 파일이며, 이번에는 동일 기능의 CLI를 Codex에서 실제 실행했다. Claude 호출 자체는 검사하지 않았다.

quiz-add는 분야·난이도를 인수로 받아 후보를 만들고 출처를 대조하는 절차이다. 실제 파일 추가는 아래 CLI가 수행한다. 예제 1문제는 이미 추가되어 있으므로 그대로 다시 적용하면 중복 오류가 나는 것이 정상이다.

```sh
python3 quiz_tools.py add 새문제.json
python3 quiz_tools.py add 새문제.json --apply
```

첫 명령은 저장하지 않고 후보를 검사한다. --apply는 출처를 직접 확인한 review_status=verified 후보를 확장 파일에 저장하고 실행 데이터 생성→게임 검사를 연결한다. 실패하면 변경한 확장 데이터와 실행 데이터를 복구한다. 기본 questions.json의 50문제는 유지한다. 질문·보기·정답·해설·HTTPS 출처·확인일이 필요하며 중복 ID/질문은 거절한다.

연결 실행 예시는 다음과 같다. 앞 단계가 실패하면 멈춘다.

```sh
python3 quiz_tools.py add 새문제.json --apply && python3 quiz_tools.py stats
python3 quiz_tools.py check && python3 quiz_tools.py stats && python3 quiz_tools.py daily
```

daily는 구조 검사 후 전체 분야·난이도·정답 위치 통계와 날짜별 10문제를 reports/daily_quiz.json으로 출력한다. 실행 생성물과 개인 기록은 Git에서 제외한다. 검증한 확장 예제 EX-CS-01의 근거는 examples/add-question.json과 extra-questions.json에 있다.

## 구현에서 해결한 문제

- 기존 50문제 조건과 문제 추가를 함께 유지하기 위해 확장 문제은행을 분리했다. 추가 문제는 일일 모드에 반영된다.
- 제한 시간이 끝나는 순간의 클릭도 한 번만 처리하고 화면을 갱신한다.
- 모드별 만점이 달라 기록을 분리하고 보고서의 정답률은 실제 문제 수로 계산한다.
- 보고서 이름은 HTML로 해석하지 않고 CSV 수식 시작 문자도 문자로 저장한다.
- 새 기능과 실제 검사 결과를 분리해서 기록하며 교재 예시의 모든 도구를 사용했다고 주장하지 않는다.
