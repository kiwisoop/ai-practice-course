# 15주차 실습·검증 기록 (`TEST_REPORT.md`)

실습일·최종 확인일: 2026-11-17 (한국 시간)

## 1. MCP별 실제 사용 및 검증 결과 요약

| 구분 | 대상 MCP / 도구 | 실제 수행 상태 | 확인 결과 및 근거 |
| --- | --- | --- | --- |
| **Notion** | `https://mcp.notion.com/mcp` | **연결·인증 상태 점검 완료 / 원격 저장 미완료(사용자 OAuth 필요)** | `claude mcp list`에서 미등록 상태 확인. 원격 엔드포인트 호출 시 `HTTP 401 (Bearer realm="OAuth")` 응답 확인. 인증 없이 사용할 수 없으므로 수업용 노트 3종을 `notion-notes/`에 마크다운 원본으로 작성·보관함 |
| **Sequential Thinking** | `@modelcontextprotocol/server-sequential-thinking` (`v2.1.1`) | **실제 실행 완료** | 로컬 stdio MCP 서버를 실행해 `sequentialthinking` 도구를 총 6단계 호출(`thoughtNumber: 1~6`, Step 3에서 `isRevision: true`로 초기 가설 수정). 입출력 전문은 `notion-notes/sequential-thinking-mcp-log.json`에 기록 |
| **Context7** | `@upstash/context7-mcp` (`v4.7.1`) | **실제 실행 완료** | 로컬 stdio MCP 서버를 실행해 `resolve-library-id` 및 `query-docs` 도구로 `/microsoft/playwright`, `/microsoft/playwright-mcp` 공식 문서를 조회하고 자동 검증 스크립트 작성에 반영 |
| **Playwright** | `@playwright/mcp` (`v1.66.0-alpha-2026-11-09`) | **실제 실행 완료** | 격리된 헤드리스 브라우저(`--headless --isolated`)에서 `browser_navigate`, `browser_type`, `browser_click`, `browser_evaluate`, `browser_take_screenshot`을 호출해 `shopping-list.html`의 6대 시나리오 자동 검증 및 스크린샷 4장 촬영 |
| **GitHub** | `git` + `gh` (`kiwisoop` 인증 재사용) | **대체 수행 완료** | 교재의 신규 저장소(`shopping-list-app`) 생성 및 PAT `.env` 등록 대신, 이미 인증된 GitHub CLI/Git 자격증명을 재사용해 기존 수업 저장소(`kiwisoop/ai-practice-course`)에 `Study-06` 반영 |

---

## 2. 쇼핑 리스트(`shopping-list.html`) Playwright MCP 자동 검증 상세

실행 명령:

```sh
python3 test_shopping_list.py
```

실행 결과: **6개 시나리오 전체 통과 (`exit code 0`)**

| 번호 | 검사 항목 | 수행 동작 | 검증 결과 | 관련 캡처 |
| --- | --- | --- | --- | --- |
| **1** | **빈 입력 거부** | 입력창에 공백(`"   "`) 입력 후 `Enter` 제출 | 항목이 추가되지 않음(`전체: 0`), 오류 안내 문구(`상품 이름을 입력해 주세요.`)와 빈 목록 안내 유지 확인 | - |
| **2** | **사과·우유·빵 추가** | `사과`(`Enter`), `우유`(`추가` 버튼 클릭), `빵`(`Enter`) 순서로 추가 | 목록에 `["사과", "우유", "빵"]` 순서대로 렌더링, 하단 요약 `전체: 3 / 완료: 0 / 남음: 3` 일치 | `screenshots/01-added-items.png` |
| **3** | **구매 체크 시 완료 표시 및 해제 시 원상 복구** | `사과`, `우유` 체크박스 클릭 → 완료 표시 확인 후 `사과` 체크박스 다시 클릭 | 체크 시 `is-completed` 클래스(취소선) 적용 및 `완료: 2 / 남음: 1` 반영. `사과` 체크 해제 시 즉시 미완료 상태로 복구되고 `완료: 1 / 남음: 2` 반영 | `screenshots/02-checked-items.png`, `screenshots/shopping-list-test.png` |
| **4** | **삭제 시 해당 상품만 제거** | `우유` 삭제 버튼 클릭 후 `빵` 삭제 버튼 클릭 | 삭제한 `우유`, `빵`만 제거되고 `사과` 1개만 유지(`전체: 1 / 완료: 0 / 남음: 1`) | `screenshots/03-after-delete.png` |
| **5** | **새로고침 복원 및 안전한 텍스트 표시(XSS 방어)** | `<img src=x onerror=alert(1)>치즈` 입력 및 완료 체크 후 `location.reload()` 실행 | 새로고침 후에도 `["사과", "<img src=x onerror=alert(1)>치즈"]` 및 완료 상태가 그대로 복원되며, `<img>` 태그가 DOM 요소로 생성되지 않고 순수 텍스트(`textContent`)로만 표시됨 | - |
| **6** | **저장 실패 및 손상된 저장 데이터 복구** | `Storage.prototype.setItem` 예외 발생 모의 후 `토마토` 추가 / `localStorage`에 `{broken-json` 기록 후 새로고침 | 저장 실패 시에도 화면의 목록(`토마토` 포함)은 유실되지 않고 오류 배너로 안내함. 손상된 JSON 로드 시 앱이 멈추지 않고 빈 목록으로 안전하게 초기화하며 안내 문구를 표시함 | - |

---

## 3. Sequential Thinking 비교 검증 요약

- **비교 문서:**
  - 일반 방식: [`notion-notes/02-dwell-time-basic.md`](notion-notes/02-dwell-time-basic.md)
  - Sequential Thinking MCP 실제 사용: [`notion-notes/03-dwell-time-sequential-thinking.md`](notion-notes/03-dwell-time-sequential-thinking.md)
  - 상세 비교 분석: [`notion-notes/04-comparison-analysis.md`](notion-notes/04-comparison-analysis.md)
- **검증 결론:**
  - 문서 길이가 길다는 이유만으로 Sequential Thinking 결과가 더 우수하다고 판단하지 않았다.
  - 실제 비교 결과, 일반 방식은 5가지 핵심 아이디어를 빠르게 파악하기에 좋고, Sequential Thinking MCP 방식은 **Step 3(`isRevision: true`)에서 무거운 시각 효과 가설을 기각하고 경량 인라인 데모로 수정한 점**, **1주차 기준선(Baseline) 선행 측정을 포함한 점**, **로딩 속도(LCP)와 연락 전환율을 감시하는 가드레일 지표를 분리한 점**에서 실행 계획의 검증 가능성이 높았다.

---

## 4. 미완료 항목 및 사용자 후속 조치 안내

1. **Notion 원격 페이지 업로드 (OAuth 인증 필요):**
   - Notion MCP(`https://mcp.notion.com/mcp`)는 브라우저에서 사용자 본인의 Notion 워크스페이스 로그인 및 권한 승인(OAuth)이 필요하다.
   - 터미널에서 아래 명령을 순서대로 실행해 인증한 뒤, `notion-notes/`의 문서를 업로드하거나 페이지에 붙여넣을 수 있다.
     ```sh
     claude mcp add --transport http notion https://mcp.notion.com/mcp
     claude
     # Claude Code 프롬프트에서 /mcp 입력 -> notion 선택 -> 1. Authenticate로 브라우저 인증 진행
     ```
2. **LMS 과제 제출 확인:**
   - GitHub 저장소(`kiwisoop/ai-practice-course`) 업로드는 코드 및 실습 기록 보관이며, 학교 LMS 시스템의 과제 제출·출석 완료를 의미하지 않는다. LMS 제출란이 열려 있다면 별도로 제출해야 한다.
