import os
import tempfile
import subprocess
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from vss import backup,drive


class VSSTests(unittest.TestCase):
    @unittest.skipUnless(os.name=='nt','Windows path mapping')
    def test_cleanup_timeout_is_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'source';source.mkdir()
            fake={'id':'{12345678-1234-1234-1234-123456789012}','device':r'\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy99'}
            with patch('vss.create',return_value=fake),patch('vss.remove',side_effect=subprocess.TimeoutExpired('fixture',90)):
                result=backup([source],root/'backup',lambda *args,**kwargs:{'ok':True})
            self.assertFalse(result['ok'])
            self.assertTrue(result['vss_cleanup_required'])
            state=json.loads(Path(result['vss_journal']).read_text(encoding='utf-8'))
            self.assertEqual(state['status'],'CLEANUP_REQUIRED')

    def test_drive_validation(self):
        self.assertEqual(drive(r'C:\Users\fixture'),'C:\\')
        with self.assertRaises(ValueError):drive(r'\\server\share\folder')

    @unittest.skipUnless(os.name=='nt','Windows path mapping')
    def test_cleanup_after_copy_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'source';source.mkdir()
            fake={'id':'{12345678-1234-1234-1234-123456789012}','device':r'\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy99'}
            with patch('vss.create',return_value=fake),patch('vss.remove') as remove:
                def fail(*args,**kwargs):raise RuntimeError('fixture failure')
                with self.assertRaises(RuntimeError):backup([source],root/'backup',fail)
                remove.assert_called_once_with(fake['id'])
                self.assertTrue(list(root.glob('vss-*.json')))
