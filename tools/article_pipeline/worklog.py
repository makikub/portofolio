#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Harness end-of-task work logs. Private by default; no network or hook changes."""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
from pathlib import Path
import re
import sys
from pipeline import GateError, read, require, write
from intake import ingest

ALIAS = re.compile(r'[a-z0-9][a-z0-9._-]{1,100}\Z')

def strings(value, field):
    require(isinstance(value,list) and all(isinstance(x,str) and len(x)<=4000 for x in value),field)
    return value

def normalize(data):
    require(isinstance(data,dict),'object_required')
    allowed={'schema_version','event_id','provenance','goal','roles','attempts','result','failures','evidence','lessons','visibility'}
    require(set(data)<=allowed,'unknown_fields')
    require(data.get('schema_version',1)==1,'schema_version')
    provenance=data['provenance']
    require(set(provenance)=={'device_id','source_tool','project_id'},'provenance_fields')
    require(provenance['source_tool'] in ('codex','claude-code','grokbot','manual'),'source_tool')
    for key in ('device_id','project_id'):
        require(isinstance(provenance[key],str) and ALIAS.fullmatch(provenance[key]),'provenance_alias')
    require(isinstance(data['goal'],str) and 1<=len(data['goal'])<=2000,'goal')
    roles=data.get('roles',{'ai':[],'human':[]})
    require(set(roles)=={'ai','human'},'roles')
    for role in roles: strings(roles[role],'role_items')
    attempts=data.get('attempts',[])
    require(isinstance(attempts,list),'attempts')
    for attempt in attempts:
        require(set(attempt)=={'action','outcome'} and all(isinstance(v,str) and len(v)<=4000 for v in attempt.values()),'attempt')
    result=data.get('result',{'status':'unknown','summary':'未記入'})
    require(set(result)=={'status','summary'} and result['status'] in ('completed','partial','failed','unknown') and isinstance(result['summary'],str) and len(result['summary'])<=4000,'result')
    evidence=data.get('evidence',[])
    require(isinstance(evidence,list),'evidence')
    for e in evidence:
        require(set(e)=={'kind','ref','verification'},'evidence_fields')
        require(e['kind'] in ('pr','commit','test','artifact','note'),'evidence_kind')
        require(e['verification'] in ('observed','reported','not_run'),'verification')
        require(isinstance(e['ref'],str) and 1<=len(e['ref'])<=4000,'evidence_ref')
    visibility=data.get('visibility','private')
    require(visibility in ('private','consider_for_article'),'visibility_is_not_release')
    out={'schema_version':1,'provenance':provenance,'goal':data['goal'],'roles':roles,'attempts':attempts,'result':result,'failures':strings(data.get('failures',[]),'failures'),'evidence':evidence,'lessons':strings(data.get('lessons',[]),'lessons'),'visibility':visibility}
    # Device/tool are provenance, not task identity. Same content across devices dedups.
    identity={k:v for k,v in out.items() if k!='provenance'}
    identity['project_id']=provenance['project_id']
    digest=hashlib.sha256(json.dumps(identity,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    event=data.get('event_id','task-'+digest[:24])
    require(isinstance(event,str) and ALIAS.fullmatch(event),'event_id')
    out['event_id']=event
    return out

def record(data, config):
    log=normalize(data)
    state=Path(config['state_dir']).expanduser()
    state.mkdir(parents=True,exist_ok=True,mode=0o700)
    key=hashlib.sha256((log['provenance']['project_id']+':'+log['event_id']).encode()).hexdigest()
    path=state/'worklogs'/(key+'.json')
    with (state/'run.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        existing=read(path) if path.exists() else None
        if existing:
            before={k:v for k,v in existing['log'].items() if k!='provenance'}
            after={k:v for k,v in log.items() if k!='provenance'}
            require(before==after,'event_conflict_use_revision')
            if log['provenance'] not in existing['origins']:
                existing['origins'].append(log['provenance']); write(path,existing)
        else:
            write(path,{'recorded_at':dt.datetime.now(dt.timezone.utc).isoformat(),'origins':[log['provenance']],'log':log})
    return {'status':'private_log_saved','event_id':log['event_id'],'duplicate':existing is not None,'path':str(path)}

def candidate(log, recorded_at):
    def claims(lines):
        return [{'text':text,'kind':'inference','evidence':[]} for text in lines] or [{'text':'作業ログでは未記入。公開前に確認する。','kind':'inference','evidence':[]}]
    return {'event_id':log['event_id'],'device_id':log['provenance']['device_id'],'source_tool':log['provenance']['source_tool'],'project_id':log['provenance']['project_id'],'private_refs':[e['ref'] for e in log['evidence']], 'seed':{'id':'worklog-'+hashlib.sha256((log['provenance']['project_id']+':'+log['event_id']).encode()).hexdigest()[:24],'date':recorded_at[:10],'title':log['goal'][:120],'summary':'作業終了ログから生成した私的な記事候補。根拠と公開可否は未確認。','public_release':False,'evidence':[],'sections':{'problem':claims([log['goal']]),'agent_role':claims(log['roles']['ai']),'human_decisions':claims(log['roles']['human']),'steps':claims([a['action']+' → '+a['outcome'] for a in log['attempts']]),'results':claims([log['result']['status']+': '+log['result']['summary']]),'failures':claims(log['failures']),'reproduction':claims([]),'limitations':claims(['ログの結果は再検証していない。実施済み・伝聞・未実施の区別は私的根拠一覧で確認する。']),'lesson':claims(log['lessons'])}}}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['record','candidate'])
    parser.add_argument('--config',required=True)
    parser.add_argument('--file',required=True,help='JSON path; record also accepts - for stdin')
    args=parser.parse_args()
    try:
        config=read(args.config)
        if args.action=='record':
            data=json.load(sys.stdin) if args.file=='-' else read(args.file)
            result=record(data,config)
        else:
            item=read(args.file)
            normalized=normalize(item['log'])
            draft=candidate(normalized,item['recorded_at'])
            result=ingest(draft,config)
            result['event_id']=normalized['event_id']
        print(json.dumps(result,ensure_ascii=False))
    except (GateError,ValueError,KeyError,TypeError,OSError):
        print(json.dumps({'status':'failed','reason':'worklog_validation_failed'}))
        raise SystemExit(1)

if __name__=='__main__': main()
