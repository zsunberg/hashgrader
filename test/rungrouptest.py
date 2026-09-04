# Exercises the group-submission path: a results.json hashed by one member is
# accepted when any member of the group submits it.
import sys, os, json, hashlib, shutil, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(HERE))
from hashgrader import grade

KEY = 'password'
ASSIGNMENT = 'Lab-1'

def hashed(assignment, email, score, key):
    return hashlib.sha256((str(assignment)+str(email)+str(score)+str(key)).encode('utf-8')).hexdigest()

def run(emails, sub, extra_files=()):
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, 'submission'))
    os.makedirs(os.path.join(d, 'results'))
    with open(os.path.join(d, 'submission', 'results.json'), 'w') as f:
        json.dump(sub, f)
    for name, content in extra_files:
        with open(os.path.join(d, 'submission', name), 'w') as f:
            f.write(content)
    with open(os.path.join(d, 'submission_metadata.json'), 'w') as f:
        json.dump({'users': [{'email': e} for e in emails]}, f)
    cwd = os.getcwd()
    try:
        os.chdir(d)
        grade(assignment=ASSIGNMENT, key=KEY, autopoints=50.0, fullscore=200)
        with open(os.path.join('results', 'results.json')) as f:
            return json.load(f)
    finally:
        os.chdir(cwd)
        shutil.rmtree(d)

def sub_for(email, score=100):
    return {'assignment': ASSIGNMENT, 'email': email, 'score': score,
            'hash': hashed(ASSIGNMENT, email, score, KEY)}

group = ['a@colorado.edu', 'b@colorado.edu', 'c@colorado.edu']
fails = []

def check(name, cond, detail):
    print(('PASS  ' if cond else 'FAIL  ') + name + ('' if cond else '  -> ' + str(detail)))
    if not cond:
        fails.append(name)

r = run(group, sub_for('a@colorado.edu'))
check('first member hashed', r['score'] == 25.0, r)

r = run(group, sub_for('c@colorado.edu'))
check('last member hashed', r['score'] == 25.0, r)

r = run(group, sub_for('C@Colorado.EDU'))
check('case-insensitive match still hashes', r['score'] == 25.0, r)

r = run(group, sub_for('outsider@colorado.edu'))
check('non-member rejected', r['score'] == 0 and 'not one of' in r['output'], r)

r = run(['a@colorado.edu'], sub_for('a@colorado.edu'))
check('solo submission still works', r['score'] == 25.0, r)

r = run(group, sub_for('a@colorado.edu', 500))
check('score capped at autopoints', r['score'] == 50.0, r)

r = run(group, sub_for('a@colorado.edu'),
        extra_files=[('Project.json', '{}'), ('solve.m', 'x = A\\b;')])
check('stray json alongside results.json ignored', r['score'] == 25.0, r)

bad = sub_for('a@colorado.edu')
bad['score'] = 200
r = run(group, bad)
check('tampered score rejected', r['score'] == 0 and 'Hash mismatch' in r['output'], r)

r = run(group, sub_for('a@colorado.edu'))
check('leaderboard value present', r['leaderboard'][0]['value'] == 100, r)

print('\n' + ('ALL PASS' if not fails else 'FAILURES: ' + ', '.join(fails)))
sys.exit(1 if fails else 0)
