# -*- coding: utf-8 -*-
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/article_pipeline'))
import pipeline as p
import worklog as w
import intake

PUBLIC_URL='https://github.com/makikub/portofolio/commit/165ec4f4d7d06d4322cab5606965757441103bb1'

def fixture(config):
    log={'provenance':{'device_id':'synthetic-device','source_tool':'codex','project_id':'synthetic-public-demo'},'goal':'公開された作業ログCLIの境界を確認する合成例','roles':{'ai':['共通ログと記事候補変換の境界を整理する。'],'human':['公開資料の範囲だけを題材にする方針を選ぶ。']},'attempts':[{'action':'公開コードのrecordとcandidate処理を参照する。','outcome':'公開許可が自動付与されない構造を確認する。'}],'result':{'status':'completed','summary':'公開コードには既定をprivateにする記録処理がある。'},'failures':['この例は合成データであり実際の制作成果を主張しない。'],'evidence':[{'kind':'commit','ref':PUBLIC_URL,'verification':'observed'}],'lessons':['作業記録と公開判断を分ける設計を検討できる。']}
    recorded=w.record(log,config)
    private=w.candidate(w.read(recorded['path'])['log'],'2026-10-31T00:00:00+00:00')
    intake.ingest(private,config)
    released=copy.deepcopy(private)
    # Simulate explicit review with a new event revision, never automatic promotion.
    released['event_id']+='-reviewed'
    released['seed']['public_release']=True
    released['seed']['evidence']=[{'url':PUBLIC_URL,'note':'公開コミットの作業ログ実装を参照する。'}]
    released['seed']['sections']['results']=[{'text':'公開コードでは記録時のvisibilityの既定がprivateとして定義されている。','kind':'observed','evidence':[PUBLIC_URL]}]
    released['seed']['sections']['reproduction']=[{'text':'公開コードを読み、保存と候補変換の境界を確認する合成例。実サービスの運用結果ではない。','kind':'inference','evidence':[]}]
    released['seed']['summary']='公開コードだけを使った合成fixture。実サービスの効果や本番稼働を主張しない。'
    intake.ingest(released,config)
    return released

class ArticleFlow(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.config={'state_dir':str(self.root/'state'),'seed_dir':str(self.root/'seeds'),'target_repo':p.TARGET,'base':'main','public_evidence_repos':[p.TARGET]}
        self.envelope=fixture(self.config)

    def test_public_only_full_flow_to_exact_pr_payload(self):
        with patch.object(p,'command',side_effect=AssertionError('no external writes')):
            result=p.run(self.config,self.root/'state')
        self.assertEqual(result['planned_pr_count'],1)
        self.assertFalse(result['remote_evidence_verified'])
        payload=p.read(self.root/'state/pr-payload.json')[0]
        self.assertEqual(payload,p.pr_payload(self.envelope['seed']))
        self.assertTrue(payload['draft'])
        self.assertEqual((self.root/'state/preview.md').read_text(),p.render_markdown(self.envelope['seed']))
        public=json.dumps(payload,ensure_ascii=False)
        for forbidden in ['device_id','source_tool','project_id','private_refs',str(self.root),'synthetic-device']:
            self.assertNotIn(forbidden,public)
        self.assertIn(PUBLIC_URL,public)

    def test_public_verification_is_read_only(self):
        def read_only(path):
            if path=='repos/'+p.TARGET: return {'visibility':'public','owner':{'login':'makikub'}}
            self.assertIn('/commits/',path)
            return {'sha':PUBLIC_URL.rsplit('/',1)[1]}
        with patch.object(p,'gh',side_effect=read_only),patch.object(p,'command',side_effect=AssertionError('no writes')):
            result=p.run(self.config,self.root/'state',verify_remote=True)
        self.assertTrue(result['remote_evidence_verified'])

    def test_private_remote_rejects_and_clears_payload(self):
        p.run(self.config,self.root/'state')
        with patch.object(p,'gh',return_value={'visibility':'private','owner':{'login':'makikub'}}):
            with self.assertRaises(p.GateError): p.run(self.config,self.root/'state',verify_remote=True)
        self.assertEqual(p.read(self.root/'state/pr-payload.json'),[])
        self.assertEqual((self.root/'state/preview.md').read_text(),'')

    def test_unknown_evidence_and_provenance_rejected(self):
        for mutation in ('unknown','provenance'):
            s=copy.deepcopy(self.envelope['seed'])
            if mutation=='unknown': s['sections']['results'][0]['evidence']=['https://github.com/makikub/portofolio/issues/999']
            else: s['private_refs']=['synthetic-private-ref']
            with self.assertRaises(p.GateError): p.validate(s,self.config)

    def test_common_secrets_and_local_paths_rejected(self):
        for value in ['AKIA'+'A'*16,'Bearer '+'b'*24,'xoxb-'+'x'*20,'glpat-'+'z'*20,'/tmp/private-note.txt','C:\\private\\note.txt','ssh://private.example/file','~/personal-note.txt','HTTPS://private.example/document']:
            with self.subTest(value=value):
                s=copy.deepcopy(self.envelope['seed']);s['summary']='Synthetic input '+value
                with self.assertRaises(p.GateError): p.validate(s,self.config)

    def test_markdown_does_not_activate_injected_markup(self):
        s=copy.deepcopy(self.envelope['seed'])
        s['title']='<script>alert(1)</script> [synthetic]'
        text=p.render_markdown(s)
        self.assertNotIn('<script>',text)
        self.assertIn('\\[synthetic\\]',text)

    def test_empty_run_invalidates_previous_preview(self):
        p.run(self.config,self.root/'state')
        for path in (self.root/'seeds').glob('*.json'): path.unlink()
        self.assertEqual(p.run(self.config,self.root/'state')['status'],'skipped')
        self.assertEqual(p.read(self.root/'state/pr-payload.json'),[])

    def test_duplicate_evidence_selects_one_article(self):
        other=copy.deepcopy(self.envelope['seed']);other['id']='another-fixture'
        p.write(self.root/'seeds/other.json',other)
        self.assertEqual(p.run(self.config,self.root/'state')['count'],1)
