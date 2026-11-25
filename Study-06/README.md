# 교재 15·16 — 쇼핑 리스트와 MCP 연동

교재 15·16번 PDF의 Notion·Sequential Thinking·Context7·Playwright·GitHub 실습을 정리했다. 기존 작업을 재사용하고 남아 있던 Notion 저장과 검증을 완료했다.

> **2026-11-20 다시 하기:** 아래 기록은 처음에 Codex 도구로 대신한 버전이다. 교재대로 Claude Code에 MCP를 직접 설치해 다시 한 기록은 [claude-code-rerun/](claude-code-rerun/README.md) 폴더에 있고, GitHub 실습 결과는 [kiwisoop/shopping-list-app](https://github.com/kiwisoop/shopping-list-app) 저장소다.

## 프로젝트 한눈에 보기

| 항목 | 내용 |
| --- | --- |
| 과제 | 인공지능활용실습 교재 15·16 · MCP 연동 |
| **먼저 볼 자료** | **[Claude Code 실행 기록 (claude-code-rerun/)](claude-code-rerun/README.md)** — 교재 프롬프트 그대로 MCP를 직접 설치해 수행 |
| 사용한 MCP | Notion · Sequential Thinking · Context7 · Playwright · GitHub |
| 결과물 | 쇼핑 리스트 앱, Notion 페이지 3개, [shopping-list-app](https://github.com/kiwisoop/shopping-list-app) 저장소 |
| 실행 방식 | `shopping-list.html`을 브라우저에서 열기 ([온라인으로 열기](https://kiwisoop.github.io/ai-practice-course/Study-06/claude-code-rerun/shopping-list.html)). 설치·API 키 불필요 |
| 이 문서 아래 내용 | 처음에 Codex 도구로 대신한 버전의 기록 (참고용으로 보관) |

![Playwright MCP 검사 화면](screenshots/shopping-list-test.png)

## 실행

`shopping-list.html`을 브라우저에서 연다. 설치·서버·API 키 없이 실행된다.

- 상품 추가: 입력 후 Enter 또는 추가 버튼
- 구매 체크·해제: 완료 항목에 취소선 표시
- 개별 삭제·전체/완료/남음 집계
- 브라우저 자동 저장·새로고침 복원
- 빈 입력 거부·키보드 조작·안전한 텍스트 표시
- 저장 공간 오류 시 화면 목록 유지. 손상된 JSON·필드·중복 ID가 있으면 기존 저장값을 덮어쓰지 않고 현재 화면에서만 사용

공유 컴퓨터의 브라우저 기록은 다른 이용자에게 보일 수 있다. 기밀·개인정보를 입력하지 않는다.

## 교재 15·16 도구 수행 기록 (처음 버전 · Codex로 대신)

| 도구 | 실제 수행 |
| --- | --- |
| Notion | 기존 Codex 연결로 인증 확인. 리서치·일반 전략·체계적 전략 3개를 개인 초안으로 저장하고 재조회 확인 |
| Sequential Thinking | 기존 계획의 6단계 요청을 실제 stdio 서버 v2.1.1에서 재검증. 가설 수정 요청 포함 |
| Context7 | 연결된 MCP로 `/microsoft/playwright-mcp`를 조회해 격리 브라우저·평가·스크린샷 문서 확인 |
| Playwright MCP | 실제 격리 브라우저로 6개 시나리오와 저장 원본 보존 회귀 검사 통과 |
| GitHub | 처음에는 별도 저장소 없이 이 저장소의 Study-06에 보관. 다시 하기에서 GitHub MCP로 [shopping-list-app](https://github.com/kiwisoop/shopping-list-app) 저장소를 만듦 |

이 표는 처음 버전 기록이다. 이때는 Claude Code에 MCP를 설치하지 않고, 이미 연결된 Codex의 Notion·Context7·GitHub와 로컬 MCP를 재사용했다. Claude Code에 직접 설치해 교재대로 다시 한 기록은 [claude-code-rerun/](claude-code-rerun/README.md) 폴더에 있다. 두 버전 모두 토큰을 코드나 환경 파일에 넣지 않았다.

## Notion 결과 (처음 버전)

처음 버전에서 Notion 개인 초안으로 저장한 페이지다. 개인 페이지라 주소는 공개 저장소에 넣지 않았다. 다시 하기에서 Claude Code로 만든 페이지는 [claude-code-rerun/](claude-code-rerun/README.md)에 따로 정리했다.

1. Claude Code 최신 업데이트 리서치 노트
2. 체류 시간 늘리기 — 일반 방식
3. 체류 시간 늘리기-체계적인 구상

내용 원본과 비교표는 `notion-notes/`에 있다. 기존 작업의 원격 MCP는 OAuth 미인증으로 기록되어 있었지만, 이번 Codex 연결에서는 정상 저장했다. 계정 이메일·워크스페이스 ID·인증 정보는 포함하지 않는다.

체류 시간 개선안은 실험 결과가 아닌 수업용 계획이다. 수치·방문자 행동은 가정이나 검증 목표이며, 2배 달성을 보장하거나 도구의 우수성을 입증하지 않는다.

## 자동 검사

Node.js·npx와 Python 3가 필요하다. 최초 실행은 패키지 다운로드나 브라우저 설치가 필요할 수 있다.

```sh
python3 test_shopping_list.py
```

검사는 `@playwright/mcp@latest`를 stdio로 실행하고 `--headless --isolated`로 개인 프로필과 분리한다. 설치된 버전에 따라 MCP 인터페이스가 달라질 수 있다.

- 사과·우유·빵 추가, 구매 체크·해제, 대상만 삭제
- 빈 입력 거부·HTML 문자열의 안전한 표시
- 새로고침 복원·저장 실패 시 화면 유지
- 손상된 JSON·잘못된 저장 필드를 새 입력으로 덮어쓰지 않음

스크린샷은 테스트용 항목만 포함한다. 상세 결과는 [TEST_REPORT.md](TEST_REPORT.md)에 있다.

## 자료 구성

- `shopping-list.html`: 실행 앱
- `test_shopping_list.py`: 실제 Playwright MCP 검사
- `PRD.md`: 실습 요구사항
- `TEST_REPORT.md`: 수행 내역·검증·한계
- `screenshots/`: 자동 검사 캡처
- `notion-notes/`: 리서치·비교 문서와 기존 Sequential Thinking 실행 기록
- `claude-code-rerun/`: Claude Code로 다시 한 실습 기록과 그때 만든 앱·`CLAUDE.md`·스크린샷

GitHub 업로드는 실습 자료 보관이다. LMS 제출·퀴즈·출석 완료는 별도 확인해야 한다.

---

[📸 실행 화면 보기](./SCREENSHOTS.md) · [전체 과제 목록으로 돌아가기](../README.md)
