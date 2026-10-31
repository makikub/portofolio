#!/usr/bin/env python3
"""Import one explicitly selected private reflection; never scan conversations."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import re
from pipeline import GateError, read, require, validate, write

FIELDS = {'event_id', 'device_id', 'source_tool', 'project_id', 'private_refs', 'seed'}

def ingest(envelope, config):
    require(isinstance(envelope, dict) and set(envelope) == FIELDS, 'intake_fields')
    for field in ('event_id', 'device_id', 'project_id'):
        require(isinstance(envelope[field], str) and re.fullmatch('[a-z0-9][a-z0-9._-]{1,100}', envelope[field]), 'intake_alias')
    require(envelope['source_tool'] in ('codex', 'claude-code', 'grokbot', 'manual'), 'source_tool')
    require(isinstance(envelope['private_refs'], list) and all(isinstance(ref, str) for ref in envelope['private_refs']), 'private_refs')
    seed = envelope['seed']
    require(isinstance(seed, dict) and type(seed.get('public_release')) is bool, 'release_flag')
    released = seed['public_release']
    if released:
        validate(seed, config)
    key = hashlib.sha256((envelope['project_id'] + ':' + envelope['event_id']).encode()).hexdigest()
    state = Path(config['state_dir']).expanduser()
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (state / 'run.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        record = state / 'intake' / (key + '.json')
        origin = {field: envelope[field] for field in ('device_id', 'source_tool', 'private_refs')}
        prior = read(record) if record.exists() else None
        if prior:
            require(prior['seed'] == seed, 'event_content_changed_use_new_event_revision')
        target = Path(config['seed_dir']).expanduser() / (seed['id'] + '.json') if released else None
        if target and target.exists():
            require(read(target) == seed, 'existing_seed_changed')
        origins = prior['origins'] if prior else []
        if origin not in origins:
            origins.append(origin)
        # Provenance is deliberately absent from the public article schema.
        write(record, {'event_id': envelope['event_id'], 'project_id': envelope['project_id'], 'origins': origins, 'seed': seed})
        if target:
            write(target, seed)
        return {'status': 'released_seed' if released else 'private_only', 'duplicate': prior is not None}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file', required=True)
    parser.add_argument('--config', required=True)
    args=parser.parse_args()
    try:
        result=ingest(read(args.file),read(args.config))
    except (GateError, ValueError, KeyError, TypeError, OSError):
        print(json.dumps({'status':'failed','reason':'intake_validation_failed'}))
        raise SystemExit(1)
    print(json.dumps(result))

if __name__ == '__main__':
    main()
