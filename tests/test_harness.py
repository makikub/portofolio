# -*- coding: utf-8 -*-
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/article_pipeline'))
import harness as h

class Harness(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.project=self.root/'personal'; self.project.mkdir()
        self.config={'device_id':'mac-mini','state_dir':str(self.root/'state'),'seed_dir':str(self.root/'seeds'),'worklog_projects':[{'project_id':'personal-demo','root':str(self.project),'include_descendants':True}]}
        self.data={'goal':'Synthetic private task log','result':{'status':'completed','summary':'Fixture only'}}

    def test_codex_and_claude_private_record(self):
        for tool in ['codex','claude-code']:
            result=h.save_scoped(self.config,self.project,tool,self.data)
            self.assertEqual(result['status'],'private_log_saved')
        records=list((self.root/'state/worklogs').glob('*.json'))
        self.assertEqual(len(records),1)
        self.assertEqual(len(h.read(records[0])['origins']),2)
        self.assertFalse((self.root/'seeds').exists())

    def test_unlisted_directory_skips_without_input_read(self):
        config=self.root/'config.json';config.write_text(json.dumps(self.config))
        result=subprocess.run([sys.executable,h.__file__,'record','--config',str(config),'--cwd',str(self.root),'--tool','codex','--file',str(self.root/'missing.json')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0)
        self.assertEqual(json.loads(result.stdout)['reason'],'outside_allowlist')
        self.assertFalse((self.root/'state').exists())

    def test_path_normalization_and_symlink_escape(self):
        nested=self.project/'nested';nested.mkdir()
        self.assertEqual(h.context(self.config,str(nested/'..')+'/', 'codex')['status'],'eligible')
        alias=self.root/'alias';alias.symlink_to(self.project)
        self.assertEqual(h.context(self.config,alias,'codex')['status'],'eligible')
        escape=self.project/'escape';escape.symlink_to(self.root)
        self.assertEqual(h.context(self.config,escape,'codex')['status'],'skipped')

    def test_excluded_and_ambiguous_scopes(self):
        self.config['denied_terms']=['personal']
        self.assertEqual(h.context(self.config,self.project,'codex')['status'],'skipped')
        self.config['denied_terms']=[]
        self.config['worklog_projects']*=2
        with self.assertRaises(h.GateError):h.context(self.config,self.project,'codex')

    def test_forged_provenance_or_release_rejected(self):
        self.data['provenance']={'project_id':'another'}
        with self.assertRaises(h.GateError):h.save_scoped(self.config,self.project,'codex',self.data)
        del self.data['provenance'];self.data['visibility']='consider_for_article'
        with self.assertRaises(h.GateError):h.save_scoped(self.config,self.project,'codex',self.data)

    def test_weekly_deduplicates_without_release(self):
        h.save_scoped(self.config,self.project,'codex',self.data)
        self.assertEqual(h.weekly(self.config)['created'],1)
        self.assertEqual(h.weekly(self.config)['unchanged'],1)
        self.assertFalse((self.root/'seeds').exists())
