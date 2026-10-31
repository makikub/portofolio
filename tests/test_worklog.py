import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/article_pipeline'))
import worklog as w

class Worklog(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.config={'state_dir':str(self.root/'state'),'seed_dir':str(self.root/'public-seeds')}
        self.data={'provenance':{'device_id':'mac-mini','source_tool':'codex','project_id':'video-test'},'goal':'検証の境界を残す'}

    def test_minimal_defaults_private(self):
        result=w.record(self.data,self.config)
        log=w.read(result['path'])['log']
        self.assertEqual(log['visibility'],'private')
        self.assertEqual(log['result']['status'],'unknown')
        self.assertFalse((self.root/'public-seeds').exists())

    def test_dedup_across_device_and_tool(self):
        first=w.record(self.data,self.config)
        self.data['provenance']['device_id']='macbook-pro'
        self.data['provenance']['source_tool']='grokbot'
        second=w.record(self.data,self.config)
        self.assertEqual(first['event_id'],second['event_id'])
        self.assertTrue(second['duplicate'])
        self.assertEqual(len(w.read(second['path'])['origins']),2)

    def test_explicit_event_conflict(self):
        self.data['event_id']='task-01'; w.record(self.data,self.config)
        self.data['goal']='異なる内容に変更する'
        with self.assertRaises(w.GateError): w.record(self.data,self.config)

    def test_candidate_never_releases(self):
        self.data['visibility']='consider_for_article'
        result=w.record(self.data,self.config); item=w.read(result['path'])
        draft=w.candidate(item['log'],item['recorded_at'])
        self.assertFalse(draft['seed']['public_release'])
        self.assertEqual(w.ingest(draft,self.config)['status'],'private_only')
        self.assertFalse((self.root/'public-seeds').exists())

    def test_no_public_visibility(self):
        self.data['visibility']='public'
        with self.assertRaises(w.GateError): w.record(self.data,self.config)

    def test_refs_are_not_executed_or_opened(self):
        self.data['evidence']=[{'kind':'test','ref':'not-a-file: $(must-not-run)','verification':'not_run'}]
        self.assertEqual(w.record(self.data,self.config)['status'],'private_log_saved')

    def test_stdin_cli(self):
        import json
        import subprocess
        config=self.root/'config.json'; w.write(config,self.config)
        command=[sys.executable,str(Path(w.__file__)),'record','--config',str(config),'--file','-']
        result=subprocess.run(command,input=json.dumps(self.data),text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'],'private_log_saved')
        self.assertFalse((self.root/'public-seeds').exists())
