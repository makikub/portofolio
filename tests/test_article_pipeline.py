import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('pipeline', Path(__file__).resolve().parents[1] / 'tools/article_pipeline/pipeline.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
URL = 'https://github.com/makikub/portofolio/commit/' + 'a' * 40

def seed():
    return {'id': 'test-learning', 'date': '2026-10-31', 'title': 'AIと人が役割を分ける実験', 'summary': '公開された検証を根拠に手順と限界を整理します。', 'public_release': True, 'evidence': [{'url': URL, 'note': '公開コミットで検証する変更内容'}], 'sections': {key: [{'text': 'この記述はテスト専用の確認内容です。', 'kind': 'observed', 'evidence': [URL]}] for key in p.SECTIONS}}

class Gates(unittest.TestCase):
    def setUp(self):
        self.config = {'public_evidence_repos': ['makikub/portofolio'], 'collect_repos': [], 'target_repo': p.TARGET, 'base': 'main', 'denied_terms': ['excluded-client']}

    def test_valid(self):
        self.assertEqual(p.validate(seed(), self.config)['id'], 'test-learning')

    def test_release_required(self):
        s=seed(); s['public_release']=False
        with self.assertRaises(p.GateError): p.validate(s, self.config)

    def test_all_sections_required(self):
        s=seed(); del s['sections']['failures']
        with self.assertRaises(p.GateError): p.validate(s, self.config)

    def test_observed_needs_evidence(self):
        s=seed(); s['sections']['results'][0]['evidence']=[]
        with self.assertRaises(p.GateError): p.validate(s, self.config)

    def test_plans_not_results(self):
        s=seed(); s['sections']['results'][0]['kind']='planned'
        with self.assertRaises(p.GateError): p.validate(s, self.config)

    def test_sensitive_and_unknown_links(self):
        for text in ['excluded-client の実データを掲載する', '/Users/person/private.txt', 'https://private.example.com/document', 'name@example.com の連絡先', 'token=abcdefghi の値を確認する']:
            with self.subTest(text=text):
                s=seed(); s['summary']=text
                with self.assertRaises(p.GateError): p.validate(s, self.config)

    def test_unapproved_repo(self):
        with self.assertRaises(p.GateError): p.validate(seed(), {'public_evidence_repos': []})

    def test_evidence_private_fails(self):
        with patch.object(p, 'gh', return_value={'visibility':'private', 'owner':{'login':'makikub'}}):
            with self.assertRaises(p.GateError): p.verify_evidence([seed()])

    def test_dedup_id_and_commit(self):
        a=seed(); b=copy.deepcopy(a); b['id']='another-learning'
        self.assertEqual(p.select([a,b], []), [b])  # stable alphabetical order
        self.assertEqual(p.select([b], [a]), [])
        self.assertEqual(p.select([a], [a]), [])

    def test_empty_does_not_call_network(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(p, 'gh', side_effect=AssertionError('network')):
            self.config['seed_dir']=str(Path(tmp)/'seeds')
            self.assertEqual(p.run(self.config, Path(tmp), True)['status'], 'skipped')

    def test_dry_run_no_network_or_git(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(p, 'command', side_effect=AssertionError('command')):
            self.config['seed_dir']=str(Path(tmp)/'seeds')
            p.write(Path(tmp)/'seeds/seed.json', seed())
            result=p.run(self.config, Path(tmp))
            self.assertEqual(result['count'], 1)
            self.assertFalse(result['remote_evidence_verified'])

    def test_traversal_id(self):
        s=seed(); s['id']='../../escape'
        with self.assertRaises(p.GateError): p.validate(s,self.config)

    def test_empty_collection(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(p.collect(self.config,Path(tmp))['count'],0)


class PublishRecovery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.seeds = self.root / 'seeds'
        p.write(self.seeds / 'seed.json', seed())
        self.config = {'seed_dir': str(self.seeds), 'public_evidence_repos': ['makikub/portofolio'], 'target_repo': p.TARGET, 'base': 'main', 'denied_terms': ['excluded-client']}
        self.calls=[]
        self.previous=[]
        self.remote=False
        self.changed=False

    def gh(self,path):
        if path=='user': return {'login':'makikub'}
        return {'default_branch':'main'}

    def command(self,*args,cwd=None):
        self.calls.append(args)
        if args[:2]==('git','clone'):
            target=Path(args[-1]); (target/'src/pages/notes').mkdir(parents=True)
            (target/'src/pages/notes/[slug].astro').touch()
        if args[:2]==('gh','api'): return json.dumps([self.previous])
        if args[:3]==('gh','pr','list'): return '[]'
        if args[:3]==('gh','pr','create'): return 'https://github.com/makikub/portofolio/pull/999'
        if args[:2]==('git','ls-remote'): return 'sha refs/heads/articles/test-learning' if self.remote else ''
        if args[:2]==('git','fetch'):
            s=seed()
            if self.changed: s['summary']='別の利用者が変更した記事内容です。'
            p.write(Path(cwd)/'src/data/articles/test-learning.json',s)
        if args[:2]==('git','diff'): return 'src/data/articles/test-learning.json'
        return ''

    def execute(self):
        with patch.object(p,'gh',side_effect=self.gh), patch.object(p,'verify_evidence'), patch.object(p,'command',side_effect=self.command):
            return p.run(self.config,self.root,True)

    def test_creates_draft_without_merge(self):
        self.assertEqual(self.execute()['status'],'draft_pr_created')
        create=[c for c in self.calls if c[:3]==('gh','pr','create')][0]
        self.assertIn('--draft',create)
        self.assertFalse(any('merge' in c or 'approve' in c for c in self.calls))

    def test_recovers_push_without_repush(self):
        self.remote=True
        self.assertEqual(self.execute()['status'],'draft_pr_created')
        self.assertFalse(any(c[:2]==('git','push') for c in self.calls))

    def test_changed_remote_is_not_overwritten(self):
        self.remote=True; self.changed=True
        with self.assertRaises(p.GateError): self.execute()
        self.assertFalse(any(c[:2]==('git','push') for c in self.calls))

    def test_existing_or_closed_pr_is_not_recreated(self):
        self.previous=[{'head':{'ref':'articles/test-learning','repo':{'full_name':p.TARGET}},'body':''}]
        self.assertEqual(self.execute()['status'],'skipped')
        self.assertFalse(any(c[:2]==('git','push') for c in self.calls))

    def test_same_evidence_other_id_skipped(self):
        self.previous=[{'head':{'ref':'articles/previous-id','repo':{'full_name':p.TARGET}},'body':p.evidence_marker(URL)}]
        self.assertEqual(self.execute()['status'],'skipped')

    def test_wrong_account_fails_before_clone(self):
        with patch.object(p,'gh',return_value={'login':'another-user'}),patch.object(p,'command',side_effect=AssertionError('must not execute')):
            with self.assertRaises(p.GateError): p.run(self.config,self.root,True)

if __name__ == '__main__': unittest.main()
