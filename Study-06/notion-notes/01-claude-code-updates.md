# Claude Code 최신 업데이트 리서치 노트

- **확인일:** 2026-11-17 (한국 시간)
- **조회 대상:** Anthropic 공식 `anthropics/claude-code` 저장소 `CHANGELOG.md` 및 Claude Code MCP 공식 문서
- **Notion 연동 상태:** 원격 Notion MCP(`https://mcp.notion.com/mcp`)는 OAuth 브라우저 인증이 필요하여(`HTTP 401`), 수업용 리서치 노트를 마크다운 원본으로 먼저 작성·보관함.

## 1. 공식 출처 링크

1. **Claude Code 공식 Changelog (GitHub):** <https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md>
2. **Claude Code 공식 Releases:** <https://github.com/anthropics/claude-code/releases>
3. **Claude Code MCP 공식 문서:** <https://docs.claude.com/en/docs/claude-code/mcp>

## 2. 최신 버전 요약 (v2.1.320 ~ v2.1.326 기준)

2026년 11월 17일 기준 공식 `CHANGELOG.md`의 최신 릴리스는 **v2.1.326**이며, 최근 업데이트는 다음 4가지 영역에 집중되어 있습니다.

### ① MCP(Model Context Protocol) 연결 및 관리 안정성 강화
- **관리형 설정 안내 개선:** 세션 중 관리자가 `managed-mcp.json`을 추가해 MCP 서버 로딩이 중단될 때 원인을 명확히 설명하는 안내 메시지 추가.
- **설정 오류 진단 개선:** `claude mcp add-json` 실행 시 모호한 `"Invalid input"` 대신 수정해야 할 항목을 구체적으로 안내하도록 개선.
- **로컬(stdio) 및 원격(HTTP) 연결 개선:** `/mcp` 메뉴에서 로컬 stdio 서버 시작 실패 원인을 표시하고, 느린 서버 연결 대기 중 `Esc` 또는 `Ctrl+C` 두 번으로 대기를 닫고 백그라운드 재연결로 전환할 수 있도록 수정.
- **도구 스키마 호환성 향상:** 루트 `anyOf` / `oneOf` 스키마를 가진 MCP 도구가 첫 번째 분기만 보여주던 문제를 수정하여 숫자·문자열 등 다중 타입 인자 전달 정확도 향상.

### ② 에이전트 팀(Agent Teams) 및 서브에이전트 제어
- **Code Mode 연동:** 에이전트 팀이 활성화된 상태에서 Code Mode를 켤 수 있도록 지원하며, 기존 설정 세션도 Code Mode로 시작되도록 개선.
- **서브에이전트 상태 표시 및 제어:** 프롬프트 하단 에이전트 행에서 각 서브에이전트가 대기 중인 작업을 명확히 표시하고, `/tasks`에서 백그라운드 명령을 실행한 서브에이전트 이름을 확인 가능. 서브에이전트 화면에서 `Esc`로 중단할 수 있는 푸터 힌트 추가.
- **관리형 설정 모델 우선순위 수정:** Claude Desktop의 Code 탭에서도 터미널과 동일하게 관리형 설정의 서브에이전트 모델 지정이 적용되도록 수정.

### ③ 권한·샌드박스·설정 검증 보호 장치
- **권한 규칙 검증:** `--allowedTools`, `--disallowedTools`, `--tools`에 불완전한 규칙이 들어간 경우 시작 시 경고 표시.
- **설정 파일 저장 실패 경고:** `/permissions`나 `/add-dir`에서 설정 파일을 실제로 기록하지 못했을 때 조용히 넘어가지 않고 파일명과 경고를 터미널에 표시.
- **깊은 중첩 설정 방어:** 비정상적으로 깊게 중첩된 설정 파일(64단계 초과)로 인한 비정상 종료를 막고 경고와 함께 무시하도록 처리.
- **안전한 데이터 삭제 확인:** `claude purge` 실행 시 표준 출력이 리디렉션된 상태에서도 삭제 확인 프롬프트가 터미널에 표시되도록 개선해 실수로 프로젝트 데이터가 삭제되는 사고 방지.

### ④ 원격 세션(Remote Control) 및 복구 기능(`/rewind`) 개선
- **원격 제어 상태 동기화:** 백그라운드 서브에이전트가 실행 중일 때 모바일/웹 원격 제어에서 유휴 상태로 잘못 표시되던 문제를 수정하고, 원격에서 Stop 실행 시 서브에이전트도 함께 종료되도록 개선.
- **세션 및 체크포인트 복구(`/rewind`):** `/branch` 연속 실행 후 `/rewind` 시 일부 파일만 복원되던 문제를 수정하고, 메모리 부족이나 빈 응답 후 재개된 세션에서 이전 대화 이력이 유실되지 않도록 보완.

## 3. 15주차 수업 관점의 시사점

- 교재(15·16번 PDF)에서 다루는 `claude mcp add`, `claude mcp list`, `/mcp` 워크플로는 최신 Claude Code(v2.1.326)에서도 핵심 인터페이스로 유지되고 있습니다.
- 특히 로컬 stdio 서버 시작 실패 원인 표시와 `claude mcp add-json` 진단 메시지 개선은 Sequential Thinking, Playwright, Context7 같은 외부 MCP 서버를 연결할 때 디버깅 시간을 줄여 줍니다.
