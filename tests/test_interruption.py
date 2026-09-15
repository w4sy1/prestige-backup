import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import app


class InterruptedBackupTests(unittest.TestCase):
    def fixture(self, root):
        source=root/'source';source.mkdir();(source/'file.txt').write_text('fixture')
        return source,root/'backup'

    def test_interrupt_before_first_copy_leaves_incomplete_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            source,destination=self.fixture(Path(temporary))
            with patch('app.shutil.copy2',side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):app.backup([source],destination)
            self.assertFalse(app.verify(destination)['ok'])
            self.assertFalse(json.loads((destination/'manifest.json').read_text())['complete'])

    def test_no_intermediate_manifest_claims_completion(self):
        with tempfile.TemporaryDirectory() as temporary:
            source,destination=self.fixture(Path(temporary));states=[];write=app.atomic_json
            def track(path,value):
                if Path(path).name=='manifest.json':states.append(value['complete'])
                return write(path,value)
            with patch('app.atomic_json',side_effect=track),patch('app.export_service',return_value=([],[])):
                app.backup([source],destination,system=True)
            self.assertTrue(states[-1])
            self.assertFalse(any(states[:-1]))

    def test_export_failure_does_not_complete_copy(self):
        with tempfile.TemporaryDirectory() as temporary:
            source,destination=self.fixture(Path(temporary))
            with patch('app.export_service',side_effect=OSError('fixture failure')):
                with self.assertRaises(OSError):app.backup([source],destination,system=True)
            self.assertFalse(app.verify(destination)['ok'])
            with self.assertRaises(ValueError):app.restore(destination,Path(temporary)/'restore',True)

    def test_copy_io_error_is_not_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            source,destination=self.fixture(Path(temporary))
            with patch('app.shutil.copy2',side_effect=PermissionError('fixture failure')):
                self.assertFalse(app.backup([source],destination)['ok'])
            self.assertTrue(app.verify(destination)['backup_errors'])

    def test_manifest_errors_override_complete_and_hash_case_is_allowed(self):
        with tempfile.TemporaryDirectory() as temporary:
            source,destination=self.fixture(Path(temporary));app.backup([source],destination)
            path=destination/'manifest.json';record=json.loads(path.read_text())
            record['files'][0]['sha256']=record['files'][0]['sha256'].upper()
            path.write_text(json.dumps(record));self.assertTrue(app.verify(destination)['ok'])
            record['errors']=[{'error':'fixture'}];path.write_text(json.dumps(record))
            self.assertFalse(app.verify(destination)['ok'])

    def test_invalid_size_rejected_and_mismatch_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            source,destination=self.fixture(Path(temporary));app.backup([source],destination)
            path=destination/'manifest.json';record=json.loads(path.read_text())
            record['files'][0]['size']=100;path.write_text(json.dumps(record))
            self.assertFalse(app.verify(destination)['ok'])
            record['files'][0]['size']=-1;path.write_text(json.dumps(record))
            with self.assertRaises(ValueError):app.verify(destination)

    def test_interrupted_restore_keeps_journal_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source,destination=self.fixture(root);app.backup([source],destination)
            target=root/'restored'
            def interrupt(source_file,target_file):
                target_file.write(b'partial')
                raise KeyboardInterrupt
            with patch('app.shutil.copyfileobj',side_effect=interrupt):
                with self.assertRaises(KeyboardInterrupt):app.restore(destination,target,True)
            journals=list(root.glob('prestige-restore-*.json'))
            self.assertEqual(len(journals),1)
            self.assertEqual(json.loads(journals[0].read_text())['status'],'IN_PROGRESS')
            with self.assertRaises(ValueError):app.restore(destination,target,True)
            self.assertEqual((target/'1-source/file.txt').read_bytes(),b'partial')

    def test_restore_io_error_and_success_have_distinct_journal_states(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source,destination=self.fixture(root);app.backup([source],destination)
            with patch('app.shutil.copyfileobj',side_effect=OSError('fixture failure')):
                result=app.restore(destination,root/'failed',True)
            self.assertFalse(result['ok'])
            self.assertEqual(json.loads(Path(result['journal']).read_text())['status'],'FAILED')
            result=app.restore(destination,root/'success',True)
            self.assertTrue(result['ok'])
            self.assertEqual(json.loads(Path(result['journal']).read_text())['status'],'COMPLETE')
