#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read exact allowlisted project notes into private candidates; no recursive scans."""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
from pathlib import Path
import re
import time
from pipeline import GateError, read, require, write

SENSITIVE_NAME = re.compile(r'(?i)(^\.|credential|secret|token|history|session|\.env)')

def collect(config, days=7):
    require(1 <= days <= 90, 'invalid_window')
    state=Path(config['state_dir']).expanduser()
    state.mkdir(parents=True,exist_ok=True,mode=0o700)
    result={'status':'collected_private','created':0,'unchanged':0,'outside_window':0}
    with (state/'run.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for source in config.get('local_sources',[]):
            require(source['source_tool'] in ('codex','claude-code','grokbot','manual'), 'source_tool')
            for field in ('project_id','device_id'):
                require(re.fullmatch('[a-z0-9][a-z0-9._-]{1,100}',source[field]),'source_alias')
            root=Path(source['root']).expanduser().resolve(strict=True)
            require(not any(t.casefold() in str(root).casefold() for t in config.get('denied_terms',[]) if t),'excluded_project')
            for relative in source['files']:
                ref=Path(relative)
                require(not ref.is_absolute() and '..' not in ref.parts, 'relative_file_required')
                require(not any(SENSITIVE_NAME.search(part) for part in ref.parts),'sensitive_filename')
                path=(root/ref).resolve(strict=True)
                require(root in path.parents and path.suffix in ('.md','.json','.txt'), 'outside_allowlist')
                stat=path.stat()
                require(stat.st_size <= 65536,'source_too_large')
                if stat.st_mtime < time.time()-days*86400:
                    result['outside_window']+=1
                    continue
                content=path.read_text()
                digest=hashlib.sha256(content.encode()).hexdigest()
                event=hashlib.sha256((source['project_id']+':'+digest).encode()).hexdigest()
                target=state/'local-candidates'/(event+'.json')
                origin={'device_id':source['device_id'],'source_tool':source['source_tool'],'private_ref':str(path)}
                if target.exists():
                    item=read(target)
                    if origin not in item['origins']:
                        item['origins'].append(origin); write(target,item)
                    result['unchanged']+=1
                    continue
                title=next((line.lstrip('# ').strip() for line in content.splitlines() if line.startswith('# ')),ref.stem)
                # This is a private excerpt and outline, never a publishable seed.
                item={'event_id':event,'project_id':source['project_id'],'origins':[origin], 'source_sha256':digest,'source_modified_at':dt.datetime.fromtimestamp(stat.st_mtime,dt.timezone.utc).isoformat(),'public_release':False,'title':title,'excerpt':content[:12000], 'excerpt_truncated':len(content)>12000,'private_draft':{'angle':title+'から再現条件と判断を整理する','evidence_status':'作業メモの記述のみ。成果物と検証結果の直接照合は別途必要。','agent_role':'記録だけでは担当ツールを確定できない場合は未確認とする。','human_decisions':'採用・不採用の理由を作業メモから抽出し本人に確認する。','next_step':'共通プロンプトで課題・手順・成果・失敗・再現条件・限界・学びを文章化。公開根拠と公開許可を得るまで私的下書きに留める。'}}
                write(target,item); result['created']+=1
        with (state/'runs.jsonl').open('a') as log:
            log.write(json.dumps({'time':dt.datetime.now(dt.timezone.utc).isoformat(),**result})+'\n')
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True)
    parser.add_argument('--days',type=int,default=7)
    args=parser.parse_args()
    try:
        result=collect(read(args.config),args.days)
    except (GateError,ValueError,KeyError,TypeError,OSError):
        print(json.dumps({'status':'failed','reason':'local_collection_failed'}))
        raise SystemExit(1)
    print(json.dumps(result))

if __name__=='__main__': main()
