import sys
from pathlib import Path
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/article_pipeline'))
import collect_local as c

class LocalCollection(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); (self.root/'project').mkdir()
        (self.root/'project/README.md').write_text('# A selected experiment\nAn observed result with limitations.')
        self.config={'state_dir':str(self.root/'state'),'local_sources':[{'root':str(self.root/'project'),'project_id':'video-test','device_id':'mac-mini','source_tool':'manual','files':['README.md']}]}

    def test_actual_file_private_and_repeat(self):
        self.assertEqual(c.collect(self.config)['created'],1)
        self.assertEqual(c.collect(self.config)['unchanged'],1)
        record=c.read(next((self.root/'state/local-candidates').glob('*.json')))
        self.assertFalse(record['public_release'])
        self.assertIn('observed result',record['excerpt'])

    def test_symlink_escape(self):
        (self.root/'outside.md').write_text('private')
        (self.root/'project/link.md').symlink_to(self.root/'outside.md')
        self.config['local_sources'][0]['files']=['link.md']
        with self.assertRaises(c.GateError): c.collect(self.config)

    def test_sensitive_names(self):
        self.config['local_sources'][0]['files']=['credentials.json']
        with self.assertRaises(c.GateError): c.collect(self.config)

    def test_excluded_project(self):
        self.config['denied_terms']=['project']
        with self.assertRaises(c.GateError): c.collect(self.config)
