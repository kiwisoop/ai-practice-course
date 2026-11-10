"""Run with: python3 check_tools.py"""
import copy
import json
import shutil
from pathlib import Path
import subprocess
import tempfile
import quiz_tools as tools

data, rows, _ = tools.read_bank()
assert len(data['questions']) == 50
assert len(tools.daily_questions(rows, '2026-11-10')) == 10
assert tools.daily_questions(rows, '2026-11-10') == tools.daily_questions(rows, '2026-11-10')
js = subprocess.check_output(['node', '-e', 'require("./questions-data.js");console.log(JSON.stringify(require("./quiz.js").dailyQuestions("2026-11-10").map(q=>q.id)))'], cwd=tools.ROOT, text=True)
assert json.loads(js) == [q['id'] for q in tools.daily_questions(rows, '2026-11-10')]
for key, value in [('answer_index', True), ('options', ['a'] * 4), ('category', 'invalid'), ('sources', [])]:
    bad = copy.deepcopy(rows[0]); bad[key] = value
    try: tools.validate_questions([bad], data['categories'])
    except ValueError: pass
    else: raise AssertionError(key)
try: tools.validate_questions(rows + [rows[0]], data['categories'])
except ValueError: pass
else: raise AssertionError('duplicate accepted')
with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp) / 'daily.json'
    tools.write_json(out, {'test': 1})
    tools.write_json(out, {'test': 2})
    assert json.loads(out.read_text()) == {'test': 2}
    isolated = Path(tmp) / 'quiz'; isolated.mkdir()
    for name in ('questions.json', 'questions-data.js', 'extra-questions.json', 'quiz_tools.py', 'build_data.py'):
        source = tools.ROOT / name
        if source.exists(): shutil.copy2(source, isolated / name)
    (isolated / 'check.js').write_text('process.exit(1)')
    candidate = copy.deepcopy(rows[0])
    candidate.update(id='ROLLBACK-TEST', question='Rollback fixture?', review_status='verified')
    candidate_path = Path(tmp) / 'candidate.json'
    tools.write_json(candidate_path, candidate)
    before = {p.name: p.read_bytes() for p in isolated.glob('*.json')}
    browser_before = (isolated / 'questions-data.js').read_bytes()
    result = subprocess.run(['python3', str(isolated / 'quiz_tools.py'), 'add', str(candidate_path), '--apply'], capture_output=True)
    assert result.returncode != 0
    assert before == {p.name: p.read_bytes() for p in isolated.glob('*.json')}
    assert browser_before == (isolated / 'questions-data.js').read_bytes()
print('PASS: validation, duplicates, atomic output, browser/CLI daily consistency and add rollback on failed checks.')
