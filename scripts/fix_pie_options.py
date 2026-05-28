import json, time, requests, random

BASE = 'http://localhost:5080'
HDR  = {'X-Admin-Key': 'cnCB0OJ52LKmXzdNSFRH4TviWqIGUbMt'}
ALL_LABELS = ['Cricket','Football','Tennis','Swimming','Basketball',
              'Science','Maths','English','Art','History','Geography','Music']

with open('diagram_questions.json') as f:
    qs = json.load(f)

posted = 0
for q in qs:
    opts = q.get('options', [])
    if len(opts) == 4:
        continue
    correct = opts[0] if opts else 'Cricket'
    wrongs = [o for o in opts if o != correct]
    extra = [l for l in ALL_LABELS if l not in opts]
    random.shuffle(extra)
    while len(wrongs) < 3:
        wrongs.append(extra.pop(0))
    new_opts = [correct] + wrongs[:3]
    random.shuffle(new_opts)
    q['options'] = new_opts
    q['correctAnswer'] = chr(65 + new_opts.index(correct))
    r = requests.post(f'{BASE}/api/admin/add-question', json=q, headers=HDR, timeout=15)
    txt = q.get('questionText', '')[:55]
    status = 'OK' if r.status_code in (200, 201) else f'FAIL {r.status_code}'
    print(f'[{status}] {txt}')
    if r.status_code in (200, 201):
        posted += 1
    time.sleep(0.1)

print(f'Posted {posted} pie chart questions')
