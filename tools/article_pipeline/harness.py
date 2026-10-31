#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scoped, private worklog entrypoint for personal harnesses."""
import argparse
import json
from pathlib import Path
import sys
from pipeline import GateError, read, require
from worklog import candidate, normalize, record
from intake import ingest

TOOLS = ('codex', 'claude-code', 'grokbot', 'manual')

def context(config, cwd, tool):
    require(tool in TOOLS, 'source_tool')
    physical = Path(cwd).expanduser().resolve(strict=True)
    if any(term.casefold() in str(physical).casefold() for term in config.get('denied_terms', []) if term):
        return {'status': 'skipped', 'reason': 'excluded_project'}
    matches = []
    for project in config.get('worklog_projects', []):
        root = Path(project['root']).expanduser().resolve(strict=True)
        if physical == root or (project.get('include_descendants', False) and root in physical.parents):
            matches.append(project)
    if not matches:
        return {'status': 'skipped', 'reason': 'outside_allowlist'}
    require(len(matches) == 1, 'ambiguous_project_scope')
    return {'status': 'eligible', 'provenance': {'device_id': config['device_id'], 'source_tool': tool, 'project_id': matches[0]['project_id']}, 'visibility': 'private'}

def save_scoped(config, cwd, tool, data):
    scope = context(config, cwd, tool)
    if scope['status'] != 'eligible':
        return scope
    require(isinstance(data, dict), 'worklog_object')
    require('provenance' not in data or data['provenance'] == scope['provenance'], 'forged_provenance')
    require(data.get('visibility', 'private') == 'private', 'private_only')
    value = dict(data, provenance=scope['provenance'], visibility='private')
    return record(value, config)

def weekly(config):
    allowed = {p['project_id'] for p in config.get('worklog_projects', [])}
    state = Path(config['state_dir']).expanduser()
    count = {'status': 'private_candidates', 'created': 0, 'unchanged': 0, 'skipped': 0}
    # All history is safe to revisit: intake deduplicates by project/event. No catch-up loss.
    for path in sorted((state / 'worklogs').glob('*.json')):
        item = read(path)
        log = normalize(item['log'])
        if log['provenance']['project_id'] not in allowed or log['provenance']['device_id'] != config['device_id']:
            count['skipped'] += 1
            continue
        # Already-curated private candidate records may differ. Preserve them; no overwrite.
        import hashlib
        key = hashlib.sha256((log['provenance']['project_id'] + ':' + log['event_id']).encode()).hexdigest()
        target = state / 'intake' / (key + '.json')
        if target.exists():
            count['unchanged'] += 1
            continue
        result = ingest(candidate(log, item['recorded_at']), config)
        count['unchanged' if result['duplicate'] else 'created'] += 1
    return count

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['context', 'record', 'weekly'])
    parser.add_argument('--config', required=True)
    parser.add_argument('--cwd', default='.')
    parser.add_argument('--tool', choices=TOOLS, default='manual')
    parser.add_argument('--file', default='-')
    args = parser.parse_args()
    try:
        config = read(args.config)
        if args.action == 'weekly':
            result = weekly(config)
        else:
            scope = context(config, args.cwd, args.tool)
            if args.action == 'context' or scope['status'] != 'eligible':
                result = scope  # Do not even read input content outside the allowlist.
            else:
                data = json.load(sys.stdin) if args.file == '-' else read(args.file)
                result = save_scoped(config, args.cwd, args.tool, data)
        print(json.dumps(result, ensure_ascii=False))
    except (GateError, ValueError, KeyError, TypeError, OSError):
        print(json.dumps({'status': 'failed', 'reason': 'harness_validation_failed'}))
        raise SystemExit(1)

if __name__ == '__main__':
    main()
