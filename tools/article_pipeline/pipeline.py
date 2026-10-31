#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local, explicit-release article pipeline. Python standard library only."""
import argparse
import datetime as dt
import fcntl
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

TARGET = 'makikub/portofolio'
SECTIONS = ('problem', 'agent_role', 'human_decisions', 'steps', 'results', 'failures', 'reproduction', 'limitations', 'lesson')
BLOCK = re.compile(r'(?i)(/Users/|/home/|file://|localhost|127\.0\.0\.1|slack\.com|docs\.google\.com|BEGIN .*PRIVATE KEY|(?:gh[pousr]_|github_pat_|sk-)[A-Za-z0-9_-]{10,}|(?:password|token|secret|api[_-]?key)\s*[:=]|[\w.+-]+@[\w.-]+\.[a-z]{2,})')
EXTRA_SENSITIVE = re.compile(r'(?i)(?:/tmp/|/private/|/var/|/etc/|/Volumes/|/opt/|/mnt/|/root/|/Library/|/Applications/|~/|[A-Z]:\\|(?:AKIA|ASIA)[A-Z0-9]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|glpat-[A-Za-z0-9_-]{10,}|Bearer\s+[A-Za-z0-9._-]{10,}|eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+|(?:ssh|s3|ftp)://)')
LINK = re.compile(r'https?://[^\s<>"\)]+', re.IGNORECASE)
EVIDENCE = re.compile(r'https://github\.com/(makikub/[A-Za-z0-9_.-]+)/(commit/[0-9a-f]{40}|pull/[1-9][0-9]*|issues/[1-9][0-9]*)\Z')

class GateError(Exception):
    pass

def require(ok, message):
    if not ok:
        raise GateError(message)

def command(*args, cwd=None):
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if p.returncode:
        # Never persist stderr: remote content and credentials could be in it.
        raise GateError('external_command_failed:' + args[0])
    return p.stdout.strip()

def gh(path):
    return json.loads(command('gh', 'api', path))

def read(path):
    return json.loads(Path(path).read_text())

def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)

def validate(seed, config):
    require(set(seed) == {'id', 'date', 'title', 'summary', 'public_release', 'evidence', 'sections'}, 'seed_fields')
    require(isinstance(seed['id'], str) and re.fullmatch('[a-z0-9][a-z0-9-]{2,70}', seed['id']), 'seed_id')
    require(seed['public_release'] is True, 'public_release_required')
    require(isinstance(seed['date'], str) and seed['date'] == dt.date.fromisoformat(seed['date']).isoformat(), 'date')
    for key in ('title', 'summary'):
        require(isinstance(seed[key], str) and 8 <= len(seed[key]) <= 300, 'missing_' + key)
    require(isinstance(seed['evidence'], list) and 1 <= len(seed['evidence']) <= 20, 'evidence_required')
    allowed = set(config['public_evidence_repos'])
    urls = []
    for item in seed['evidence']:
        require(set(item) == {'url', 'note'}, 'evidence_fields')
        m = EVIDENCE.fullmatch(item['url'])
        require(m and m[1] in allowed, 'evidence_not_allowlisted')
        require(isinstance(item['note'], str) and len(item['note']) >= 8, 'evidence_note')
        urls.append(item['url'])
    require(len(urls) == len(set(urls)), 'duplicate_evidence')
    require(set(seed['sections']) == set(SECTIONS), 'required_sections')
    for name, claims in seed['sections'].items():
        require(isinstance(claims, list) and claims, 'empty_section:' + name)
        for claim in claims:
            require(set(claim) == {'text', 'kind', 'evidence'}, 'claim_fields')
            require(isinstance(claim['text'], str) and len(claim['text']) >= 8, 'short_claim')
            require(claim['kind'] in ('observed', 'inference', 'planned'), 'claim_kind')
            require(isinstance(claim['evidence'], list) and set(claim['evidence']) <= set(urls), 'unknown_evidence')
            require(claim['kind'] != 'observed' or claim['evidence'], 'fact_without_evidence')
            if name == 'results':
                require(claim['kind'] == 'observed', 'results_must_be_observed')
    raw = json.dumps(seed, ensure_ascii=False)
    require(not BLOCK.search(raw) and not EXTRA_SENSITIVE.search(raw), 'sensitive_content')
    require(not any(term.casefold() in raw.casefold() for term in config.get('denied_terms', []) if term), 'excluded_content')
    require(set(LINK.findall(raw)) <= set(urls), 'unapproved_url')
    return seed

def verify_evidence(seeds):
    repos = set()
    for seed in seeds:
        for item in seed['evidence']:
            m = EVIDENCE.fullmatch(item['url'])
            repo, ref = m[1], m[2]
            if repo not in repos:
                meta = gh('repos/' + repo)
                require(meta['visibility'] == 'public' and meta['owner']['login'] == 'makikub', 'nonpublic_evidence')
                repos.add(repo)
            kind, number = ref.split('/')
            endpoint = {'commit': 'commits', 'pull': 'pulls', 'issues': 'issues'}[kind]
            gh('repos/' + repo + '/' + endpoint + '/' + number)

def evidence_marker(url):
    return '<!-- evidence:' + hashlib.sha256(url.encode()).hexdigest() + ' -->'

def select(seeds, articles):
    ids = {a['id'] for a in articles}
    evidence = {e['url'] for a in articles for e in a['evidence']}
    chosen = []
    for seed in sorted(seeds, key=lambda s: (s['date'], s['id'])):
        urls = {e['url'] for e in seed['evidence']}
        if seed['id'] in ids or urls & evidence:
            continue
        ids.add(seed['id'])
        evidence.update(urls)
        chosen.append(seed)
    return chosen

def articles_at(root):
    return [read(p) for p in sorted((Path(root) / 'src/data/articles').glob('*.json'))]

def collect(config, state):
    # Candidate metadata stays local; never promote raw commit messages to articles.
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)).isoformat()
    candidates = []
    for repo in config['collect_repos']:
        require(re.fullmatch(r'makikub/[A-Za-z0-9_.-]+', repo), 'collection_owner')
        require(not BLOCK.search(repo), 'excluded_source')
        require(not any(term.casefold() in repo.casefold() for term in config.get('denied_terms', []) if term), 'excluded_source')
        meta = gh('repos/' + repo)
        require(meta['visibility'] == 'public', 'collection_not_public')
        commits = gh('repos/' + repo + '/commits?per_page=100&since=' + since)
        require(len(commits) < 100, 'collection_window_too_large')
        for commit in commits:
            candidates.append({'id': repo + ':' + commit['sha'], 'url': commit['html_url'], 'public_release': False})
    write(state / 'candidates.json', candidates)
    return {'status': 'collected', 'count': len(candidates)}

def markdown_text(value):
    return re.sub(r'([\\`*_{}\[\]()#+.!|>-])', r'\\\1', html.escape(value, quote=False))

def render_markdown(seed):
    headings = dict(zip(SECTIONS, ('課題', 'AIの役割', '人の判断', '手順', '確認できた成果', '失敗', '再現条件', '限界', '学び')))
    labels = {'observed': '確認した事実', 'inference': '考察', 'planned': '計画'}
    lines = ['# ' + markdown_text(seed['title']), '', markdown_text(seed['summary']), '']
    for section in SECTIONS:
        lines.extend(['## ' + headings[section], ''])
        for claim in seed['sections'][section]:
            lines.extend(['**' + labels[claim['kind']] + '**', '', markdown_text(claim['text']), ''])
            for url in claim['evidence']:
                lines.extend(['[根拠](' + url + ')', ''])
    lines.extend(['## 根拠資料', ''])
    lines.extend('- [' + markdown_text(e['note']) + '](' + e['url'] + ')' for e in seed['evidence'])
    return '\n'.join(lines) + '\n'

def pr_payload(seed):
    body = '\n'.join(evidence_marker(e['url']) for e in seed['evidence'])
    body += '\n\n公開許可済み記事種から生成。事実と根拠、公開可否、再現条件、限界を本人がレビューしてください。Draftの本文と差分も公開され得ます。自動承認・マージは行いません。\n\n'
    body += render_markdown(seed)
    return {'repository': TARGET, 'base': 'main', 'head': 'articles/' + seed['id'], 'draft': True, 'title': '実践ノート: ' + seed['title'], 'body': body, 'article_path': 'src/data/articles/' + seed['id'] + '.json', 'article': seed}

def run(config, state, publish=False, verify_remote=False):
    require(Path(config['seed_dir']).expanduser().resolve() != state.resolve(), 'seed_and_state_must_be_separate')
    # Invalidate prior output before any validation failure or empty run.
    state.mkdir(parents=True, exist_ok=True)
    write(state / 'preview.json', [])
    write(state / 'pr-payload.json', [])
    (state / 'preview.md').write_text('')
    require(config['target_repo'] == TARGET and config['base'] == 'main', 'target_mismatch')
    seeds = [validate(read(p), config) for p in sorted(Path(config['seed_dir']).expanduser().glob('*.json'))]
    # Empty run needs neither network nor checkout.
    if not seeds:
        return {'status': 'skipped', 'reason': 'no_released_seeds'}
    require(len({s['id'] for s in seeds}) == len(seeds), 'duplicate_seed_id')
    if not publish:
        chosen = select(seeds, articles_at(Path(__file__).resolve().parents[2]))
        if verify_remote:
            verify_evidence(chosen)
        write(state / 'preview.json', chosen)
        write(state / 'pr-payload.json', [pr_payload(seed) for seed in chosen[:1]])
        (state / 'preview.md').write_text(render_markdown(chosen[0]) if chosen else '')
        return {'status': 'dry_run', 'count': len(chosen), 'planned_pr_count': min(len(chosen), 1), 'remote_evidence_verified': verify_remote, 'remote_pr_dedup_checked': False}
    require(gh('user')['login'] == 'makikub', 'wrong_github_account')
    meta = gh('repos/' + TARGET)
    require(meta['default_branch'] == 'main', 'unexpected_default_branch')
    verify_evidence(seeds)
    with tempfile.TemporaryDirectory(prefix='article-pr-') as tmp:
        command('git', 'clone', '--quiet', '--single-branch', '--branch', 'main', 'https://github.com/' + TARGET + '.git', tmp)
        require((Path(tmp) / 'src/pages/notes/[slug].astro').exists(), 'merge_pipeline_setup_first')
        pages = json.loads(command('gh', 'api', '--paginate', '--slurp', 'repos/' + TARGET + '/pulls?state=all&per_page=100'))
        previous = [pr for page in pages for pr in page]
        used_branches = {pr['head']['ref'] for pr in previous if pr['head']['repo'] and pr['head']['repo']['full_name'] == TARGET}
        used_markers = ' '.join(pr.get('body') or '' for pr in previous if pr['head']['repo'] and pr['head']['repo']['full_name'] == TARGET)
        fresh = [s for s in seeds if 'articles/' + s['id'] not in used_branches and not any(evidence_marker(e['url']) in used_markers for e in s['evidence'])]
        chosen = select(fresh, articles_at(tmp))
        if not chosen:
            return {'status': 'skipped', 'reason': 'already_published'}
        # Single seed per run: stable branch identity across retries and edited seed content.
        seed = chosen[0]
        branch = 'articles/' + seed['id']
        prs = json.loads(command('gh', 'pr', 'list', '--repo', TARGET, '--state', 'all', '--head', branch, '--json', 'url,state'))
        if prs:
            return {'status': 'skipped', 'reason': 'pr_already_exists', 'pr': prs[0]['url']}
        remote = command('git', 'ls-remote', '--heads', 'origin', branch, cwd=tmp)
        article = Path(tmp) / 'src/data/articles' / (seed['id'] + '.json')
        if remote:
            # Recover only an exactly matching pushed article; never overwrite remote work.
            command('git', 'fetch', 'origin', branch, cwd=tmp)
            command('git', 'checkout', '-b', branch, 'FETCH_HEAD', cwd=tmp)
            require(article.exists() and read(article) == seed, 'remote_branch_requires_review')
            names = command('git', 'diff', '--name-only', 'origin/main...HEAD', cwd=tmp).splitlines()
            require(names == ['src/data/articles/' + seed['id'] + '.json'], 'unexpected_remote_changes')
        else:
            command('git', 'checkout', '-b', branch, cwd=tmp)
            write(article, seed)
            command('git', 'add', '--', str(article), cwd=tmp)
            command('git', '-c', 'user.name=makikub', '-c', 'user.email=makikub@users.noreply.github.com', 'commit', '-m', 'docs: add reviewed learning seed ' + seed['id'], cwd=tmp)
            command('git', 'push', 'origin', branch, cwd=tmp)
        body = Path(tmp) / 'article-pr-body.md'
        payload = pr_payload(seed)
        body.write_text(payload['body'])
        url = command('gh', 'pr', 'create', '--repo', payload['repository'], '--base', payload['base'], '--head', payload['head'], '--draft', '--title', payload['title'], '--body-file', str(body))
        return {'status': 'draft_pr_created', 'pr': url}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['collect', 'dry-run', 'publish', 'check'])
    parser.add_argument('--config', required=True)
    parser.add_argument('--verify-remote', action='store_true', help='Read-only public evidence verification for dry-run')
    args = parser.parse_args()
    config = read(args.config)
    state = Path(config['state_dir']).expanduser()
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (state / 'run.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps({'status': 'skipped', 'reason': 'already_running'}))
            return
        try:
            if args.action == 'collect':
                result = collect(config, state)
            elif args.action == 'check':
                items = articles_at(Path(__file__).resolve().parents[2])
                for item in items:
                    validate(item, config)
                require(len(select(items, [])) == len(items), 'duplicate_published_evidence')
                result = {'status': 'checked', 'count': len(items)}
            else:
                result = run(config, state, args.action == 'publish', args.verify_remote)
        except (GateError, ValueError, KeyError, TypeError, OSError):
            result = {'status': 'failed', 'reason': 'validation_or_external_command_failed', 'action': args.action}
        with (state / 'runs.jsonl').open('a') as log:
            log.write(json.dumps({'time': dt.datetime.now(dt.timezone.utc).isoformat(), **result}) + '\n')
        print(json.dumps(result, ensure_ascii=False))
        if result['status'] == 'failed':
            sys.exit(1)

if __name__ == '__main__':
    main()
