from pathlib import Path
import tempfile
import unittest
from app import allowed,backup,verify

class BackupTests(unittest.TestCase):
    def test_secret_filters(self):
        for value in ('.env','.ssh/id_rsa','Cookies','tokens.json','passwords.txt','x.pfx'):self.assertFalse(allowed(value))
    def test_verify_changes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'source';root.mkdir();(root/'photo.jpg').write_bytes(b'image')
            dest=Path(d)/'backup';backup([root],dest);self.assertTrue(verify(dest)['ok'])
            (dest/'1-source/photo.jpg').write_bytes(b'changed');self.assertFalse(verify(dest)['ok'])
    def test_nested_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):backup([d],Path(d)/'backup')
