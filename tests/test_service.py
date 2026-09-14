import json
import tempfile
import unittest
from pathlib import Path
from app import backup, restore, verify
from service import clean_bookmarks


class ServiceTests(unittest.TestCase):
    def test_bookmark_secret_fields_removed(self):
        result=clean_bookmarks({'type':'url','name':'Docs','url':'https://user:password@example.com/doc?token=abc#secret'})
        self.assertEqual(result['url'],'https://example.com/doc')
        self.assertIsNone(clean_bookmarks({'type':'url','url':'javascript:alert(1)'}))

    def test_service_export_is_hashed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);bookmarks=root/'Bookmarks'
            bookmarks.write_text(json.dumps({'roots':{'bookmark_bar':{'type':'folder','name':'Bar','children':[]}}}))
            dest=root/'backup'
            result=backup([],dest,bookmarks=[bookmarks])
            self.assertTrue(result['ok']);self.assertTrue(verify(dest)['ok'])
            (dest/'_service/bookmarks-1.json').write_text('changed')
            self.assertFalse(verify(dest)['ok'])

    def test_restore_preview_and_copy(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'source';source.mkdir()
            (source/'document.txt').write_text('fixture')
            backup([source],root/'backup')
            restore(root/'backup',root/'restored')
            self.assertFalse((root/'restored').exists())
            self.assertTrue(restore(root/'backup',root/'restored',True)['ok'])
            self.assertEqual((root/'restored/1-source/document.txt').read_text(),'fixture')
            with self.assertRaises(ValueError):restore(root/'backup',root/'restored',True)

    def test_corrupt_backup_cannot_restore(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'source';source.mkdir()
            (source/'file').write_text('fixture');backup([source],root/'backup')
            (root/'backup/1-source/file').write_text('tampered')
            with self.assertRaises(ValueError):restore(root/'backup',root/'restored',True)
            self.assertFalse((root/'restored').exists())

    def test_manifest_path_traversal(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/'manifest.json').write_text(json.dumps({'schema_version':1,'complete':True,'files':[{'path':'../outside','sha256':'0'*64}]}))
            with self.assertRaises(ValueError):verify(root)
