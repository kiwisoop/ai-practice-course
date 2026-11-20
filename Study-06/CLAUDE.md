# Study-06 — 쇼핑 리스트 + MCP

교재 15–16 실습. 설치·서버 없이 브라우저에서 여는 단일 파일 쇼핑 리스트 앱.

## 구조
- `shopping-list.html`: 앱 전체 (HTML·CSS·JS, localStorage 저장)
- `test_shopping_list.py`: Playwright MCP(`@playwright/mcp`)로 6개 시나리오 자동 검사
- `notion-notes/`: Notion·Sequential Thinking 실습 원본
- `screenshots/`: 자동 검사 캡처

## 검사
```sh
python3 test_shopping_list.py
```

## 규칙
- 외부 라이브러리 없이 한 파일로 유지한다.
- 저장 데이터가 손상돼도 원본을 덮어쓰지 않는다.
- MCP 토큰·Notion 주소 등 개인 정보는 저장소에 넣지 않는다.
