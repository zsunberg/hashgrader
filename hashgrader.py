# This is hashgrader! https://github.com/zsunberg/hashgrader/

import os, json
import hashlib
from glob import iglob

def grade(assignment, key, autopoints=100, fullscore=100, scorestring=str):
    try:
        json_files = [pos_json for pos_json in iglob(os.path.join('submission', '**', '*.json'), recursive=True)]

        # A submission may also contain source code, so a file actually named
        # results.json wins over any other json that happens to be in there.
        results_files = [f for f in json_files if os.path.basename(f).lower() == 'results.json']
        if results_files:
            json_files = results_files

        assert len(json_files) == 1, 'Expected exactly one json file, got ' + str(len(json_files)) + ': ' + str(json_files) + '.'

        sub_file = json_files[0]
        with open(sub_file) as f:
            sub = json.load(f)

        with open('submission_metadata.json') as f:
            meta = json.load(f)

        # For a group submission, meta['users'] holds every member of the
        # group, and any one of their emails may be the one that was hashed.
        emails = [u['email'] for u in meta['users']]
        se = sub['email']
        matches = [e for e in emails if e.lower() == se.lower()]
        assert matches, 'Submission email ({}) is not one of the submitting group members ({})!'.format(se, ', '.join(emails))

        assert sub['assignment'] == assignment, 'Submission from wrong homework (got {}, expected {}).'.format(sub['assignment'], assignment)

        # Hash with the email as it was typed on the student's machine: the
        # match above is case-insensitive, but sha256 is not.
        m = hashlib.sha256()
        score_str = scorestring(sub['score'])
        m.update((str(sub['assignment'])+str(se)+score_str+str(key)).encode('utf-8'))
        assert m.hexdigest() == sub['hash'], "Hash mismatch! If you think you submitted a valid json file, report this to the course staff."

        points = round(max(0, min(autopoints, autopoints*sub['score']/fullscore)), 1)
        output = 'Submission Successful! You received ' + str(points) + '/' + str(autopoints) + ' autograder points.'
        if len(emails) > 1:
            output += ' (Scored from the run by ' + se + '.)'
        d = {'score': points,
             'output': output,
             'leaderboard': [{'name':'score', 'value':sub['score']}]}

    except Exception as ex:
        d = {'score': 0, 'output': 'ERROR: '+str(ex)}
        print(str(ex))

    finally:
        with open('results/results.json', 'w') as f:
            json.dump(d, f)
