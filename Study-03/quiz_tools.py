"""Offline quiz maintenance commands. Structural checks do not prove factual correctness."""
import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def read_bank():
    data = json.loads((ROOT / 'questions.json').read_text())
    extra_path = ROOT / 'extra-questions.json'
    extras = json.loads(extra_path.read_text())['questions'] if extra_path.exists() else []
    rows = data['questions'] + extras
    validate_questions(rows, data['categories'])
    return data, rows, extras


def validate_questions(rows, categories):
    ids, texts = set(), set()
    for q in rows:
        if not isinstance(q, dict) or not isinstance(q.get('id'), str) or not q['id'].strip() or q['id'] in ids:
            raise ValueError('문제 ID가 없거나 중복되었습니다.')
        if q.get('category') not in categories or any(not isinstance(q.get(k), str) or not q[k].strip() for k in ('topic', 'question', 'explanation')):
            raise ValueError('문제 분야·주제·질문·해설을 확인하세요.')
        if q['question'].strip() in texts:
            raise ValueError('질문이 중복되었습니다.')
        options = q.get('options')
        if not isinstance(options, list) or len(options) != 4 or any(not isinstance(o, str) or not o.strip() for o in options) or len(set(options)) != 4:
            raise ValueError('서로 다른 보기 4개가 필요합니다.')
        if type(q.get('answer_index')) is not int or not 0 <= q['answer_index'] < 4:
            raise ValueError('answer_index는 0~3 정수여야 합니다.')
        if not isinstance(q.get('sources'), list) or not q['sources']:
            raise ValueError('출처가 필요합니다.')
        for source in q['sources']:
            if not isinstance(source, dict) or any(not isinstance(source.get(k), str) or not source[k].strip() for k in ('publisher', 'title', 'url', 'checked_on', 'evidence_summary')) or not source['url'].startswith('https://'):
                raise ValueError('HTTPS 출처와 확인 근거를 입력하세요.')
            date.fromisoformat(source['checked_on'])
        ids.add(q['id']); texts.add(q['question'].strip())


def statistics(rows):
    return {'question_count': len(rows), 'categories': dict(Counter(q['category'] for q in rows)),
            'difficulty': dict(Counter(q.get('difficulty', '입문') for q in rows)),
            'answer_positions': dict(sorted(Counter(q['answer_index'] + 1 for q in rows).items()))}


def daily_questions(rows, day):
    date.fromisoformat(day)
    seed = 1
    for ch in day:
        seed = (seed * 31 + ord(ch)) & 0xffffffff
    pool = rows[:]
    for i in range(len(pool) - 1, 0, -1):
        seed = (seed * 1664525 + 1013904223) & 0xffffffff
        j = seed % (i + 1)
        pool[i], pool[j] = pool[j], pool[i]
    return pool[:10]


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    temp.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('check', 'stats', 'validate'):
        command = sub.add_parser(name)
        if name == 'validate': command.add_argument('category', nargs='?')
    command = sub.add_parser('range')
    command.add_argument('start', type=int); command.add_argument('end', type=int)
    command = sub.add_parser('add')
    command.add_argument('file', type=Path)
    command.add_argument('--apply', action='store_true', help='출처를 직접 확인한 추가 문제를 확장 문제은행에 저장')
    command = sub.add_parser('daily')
    command.add_argument('--date', default=date.today().isoformat())
    command.add_argument('--output', type=Path, default=ROOT / 'reports' / 'daily_quiz.json')
    args = parser.parse_args()
    data, rows, extras = read_bank()
    if args.command == 'check':
        subprocess.run(['node', str(ROOT / 'check.js')], check=True, cwd=ROOT)
        print('구조·게임 검사 완료. 정답의 사실 검증은 SOURCE_REVIEW.md 참조.')
    elif args.command == 'stats':
        print(json.dumps(statistics(rows), ensure_ascii=False, indent=2))
    elif args.command in ('range', 'validate'):
        if args.command == 'range':
            if not 1 <= args.start <= args.end <= len(rows): raise ValueError('문제 범위를 확인하세요.')
            selected = rows[args.start - 1:args.end]
        else:
            if args.category and args.category not in data['categories']: raise ValueError('알 수 없는 분야입니다.')
            selected = [q for q in rows if not args.category or q['category'] == args.category]
        for q in selected:
            flags = [word for word in ('가장', '최초', '최대', '최소', '현재') if word in q['question']]
            print(q['id'], q['question'], '범위·기준 검토 필요: ' + ', '.join(flags) if flags else '형식 검사 통과')
        print('표현 검사 결과는 사실 확인을 대체하지 않습니다.')
    elif args.command == 'add':
        candidate = json.loads(args.file.read_text())
        validate_questions(rows + [candidate], data['categories'])
        if candidate.get('review_status') != 'verified': raise ValueError('출처를 직접 확인한 뒤 review_status를 verified로 기록하세요.')
        if not args.apply:
            print('추가 전 검사 통과. 실제 저장은 --apply를 사용하세요. 기본 50문제는 변경하지 않습니다.')
            return
        path = ROOT / 'extra-questions.json'
        previous = path.read_bytes() if path.exists() else None
        old_browser = (ROOT / 'questions-data.js').read_bytes()
        try:
            write_json(path, {'version': 1, 'questions': extras + [candidate]})
            subprocess.run([sys.executable, str(ROOT / 'build_data.py')], check=True)
            subprocess.run(['node', str(ROOT / 'check.js')], check=True, cwd=ROOT)
        except Exception:
            if previous is None: path.unlink(missing_ok=True)
            else: path.write_bytes(previous)
            (ROOT / 'questions-data.js').write_bytes(old_browser)
            raise
        print('확장 문제 추가→실행 데이터 생성→검사 완료. 기본 50문제는 유지했습니다.')
    elif args.command == 'daily':
        selected = daily_questions(rows, args.date)
        write_json(args.output, {'date': args.date, 'questions': selected, 'statistics': statistics(rows)})
        print(f'문제 검사→통계→날짜별 10문제 출력 완료: {args.output}')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as error:
        print(f'실패: {error}', file=sys.stderr)
        raise SystemExit(1)
