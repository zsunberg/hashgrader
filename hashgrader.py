import os, json
import hashlib
from glob import iglob

def grade(assignment, key, autopoints=100, fullscore=100):
    try:
        json_files = [pos_json for pos_json in iglob(os.path.join('submission', '**', '*.json'), recursive=True)]
    
        assert len(json_files) == 1, 'Expected exactly one json file, got ' + str(len(json_files)) + ': ' + str(json_files) + '.'
    
        sub_file = json_files[0]
        with open(sub_file) as f:
            sub = json.load(f)
    
        with open('submission_metadata.json') as f:
            meta = json.load(f)
    
        me = meta['users'][0]['email']
        se = sub['email']
        assert me == se, 'Gradescope email ({}) and DMUStudent evaluate email ({}) did not match!'.format(me, se)
    
        assert sub['assignment'] == assignment, 'Submission from wrong homework (got {}, expected {}).'.format(sub['assignment'], assignment)
    
        m = hashlib.sha256()
        m.update((sub['assignment']+me+str(sub["score"])+key).encode('utf-8'))
        assert m.hexdigest() == sub['hash'], "Hash mismatch! If you think you submitted a valid json file, report this to the course staff."
    
        points = round(max(0, min(autopoints, autopoints*sub['score']/fullscore)), 1)
        d = {'score': points,
             'output': 'Submission Successful! You received ' + str(points) + '/' + str(autopoints) + ' autograder points.',
             'leaderboard': [{'name':'score', 'value':sub['score']}]}
    
    except Exception as ex:
        d = {'score': 0, 'output': 'ERROR: '+str(ex)}
        print(str(ex))
    
    finally:
        with open('results/results.json', 'w') as f:
            json.dump(d, f)
