import copy
import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/article_pipeline'))
import intake
from test_article_pipeline import seed

class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.config={'state_dir':str(self.root/'state'),'seed_dir':str(self.root/'seeds'),'public_evidence_repos':['makikub/portofolio']}
        self.e={'event_id':'experiment-01','device_id':'mac-mini','source_tool':'codex','project_id':'personal-video','private_refs':['local-private-reference'],'seed':seed()}

    def test_provenance_stays_private(self):
        self.assertEqual(intake.ingest(self.e,self.config)['status'],'released_seed')
        public=intake.read(self.root/'seeds/test-learning.json')
        self.assertEqual(public,seed())
        self.assertNotIn('device_id',public)
        records=list((self.root/'state/intake').glob('*.json'))
        self.assertEqual(intake.read(records[0])['origins'][0]['private_refs'],['local-private-reference'])

    def test_two_devices_same_event_dedup(self):
        intake.ingest(self.e,self.config)
        self.e['device_id']='macbook-pro'; self.e['source_tool']='claude-code'
        self.assertTrue(intake.ingest(self.e,self.config)['duplicate'])
        records=list((self.root/'state/intake').glob('*.json'))
        self.assertEqual(len(records),1)
        self.assertEqual(len(intake.read(records[0])['origins']),2)
        self.assertEqual(len(list((self.root/'seeds').glob('*.json'))),1)

    def test_unreleased_not_promoted(self):
        self.e['seed']['public_release']=False
        self.assertEqual(intake.ingest(self.e,self.config)['status'],'private_only')
        self.assertFalse((self.root/'seeds').exists())

    def test_conflicting_event_not_overwritten(self):
        intake.ingest(self.e,self.config)
        self.e['seed']['summary']='別の端末で変えられた内容です。'
        with self.assertRaises(intake.GateError): intake.ingest(self.e,self.config)
        self.assertEqual(intake.read(self.root/'seeds/test-learning.json'),seed())

    def test_grokbot_explicit_export_supported(self):
        self.e['source_tool']='grokbot'
        self.assertEqual(intake.ingest(self.e,self.config)['status'],'released_seed')

    def test_private_info_in_public_seed_rejected(self):
        self.e['seed']['summary']='/Users/example/private の資料を参照'
        with self.assertRaises(intake.GateError): intake.ingest(self.e,self.config)
