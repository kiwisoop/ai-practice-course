"""Generate browser data from the canonical question bank. No dependencies."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
data = json.loads((root / "questions.json").read_text(encoding="utf-8"))
content = json.dumps(data, ensure_ascii=False, indent=2)
(root / "questions-data.js").write_text(
    "// Generated from questions.json by build_data.py; edit the JSON source.\n"
    + "globalThis.QUIZ_DATA = " + content + ";\n", encoding="utf-8"
)
print(f"Generated questions-data.js: {len(data['questions'])} questions")
