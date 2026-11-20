# Study-04 — FridgeChef

냉장고 사진에서 재료를 인식하고 레시피를 추천·보관하는 Python·Streamlit 앱 (교재 11–13).

## 구조
- `app.py`: Streamlit 화면 (로그인 → 대시보드 → 재료 인식 → 레시피 생성 → 저장)
- `api.py`: 학교 API 게이트웨이 호출 (이미지 인식·레시피 생성)
- `storage.py`: SQLite 저장
- `PRD_step1~3.md`: 교재 12의 단계별 요구사항
- `.claude/agents/`: code-bug-analyzer · performance-optimizer · ux-design-advisor (교재 13)

## 실행·검사
```sh
python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1
.venv/bin/python -m unittest -v
```

## 규칙
- API 키는 `.env`나 화면 입력으로만 받고 코드·로그·커밋에 넣지 않는다 (`.gitignore`에 `.env` 포함).
- 사용자 원본 사진은 파일로 저장하지 않는다.
- 변경 후 테스트를 실행하고 결과를 보고한다.
