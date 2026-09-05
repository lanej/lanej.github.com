"""Avoid overlapping publishers while the repository's Pages source is migrated.

Only reads repository settings and run status. Does not change admin settings.
"""
import json
import os
import time
from pathlib import Path
from urllib.request import Request, urlopen

repo=os.environ['GITHUB_REPOSITORY']
sha=os.environ['GITHUB_SHA']
headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'}
def get(path):
    with urlopen(Request('https://api.github.com/repos/'+repo+'/'+path,headers=headers),timeout=30) as response:
        return json.load(response)
settings=get('pages')
summary={k:settings.get(k) for k in ('build_type','cname','https_enforced')}
Path('artifacts/live').mkdir(parents=True,exist_ok=True)
Path('artifacts/live/pages-settings.json').write_text(json.dumps(summary,indent=2))
assert settings['cname']=='lanej.io' and settings['https_enforced'], 'Unexpected Pages domain or HTTPS setting'
print(json.dumps(summary))
if settings['build_type']=='legacy':
    print('Pages still uses branch publishing; waiting for its run before deploying the Hugo artifact.')
    for attempt in range(36):
        runs=get('actions/runs?per_page=30')['workflow_runs']
        legacy=[r for r in runs if r['head_sha']==sha and (r['name'].lower()=='pages build and deployment' or 'dynamic/pages/' in r['path'])]
        if legacy and all(r['status']=='completed' for r in legacy):
            print('Legacy publishing run completed. Deploying tested Hugo output last.')
            break
        if not legacy and attempt>=12:
            print('No legacy run scheduled for this revision.')
            break
        time.sleep(5)
    else:
        raise RuntimeError('Legacy publisher did not finish within three minutes')
