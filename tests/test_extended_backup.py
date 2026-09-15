import json
import sqlite3
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from app import backup,verify,restore


class ExtendedBackupTests(unittest.TestCase):
    def test_firefox_bookmarks_only_no_history(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);database=root/'places.sqlite'
            connection=sqlite3.connect(database)
            connection.executescript('CREATE TABLE moz_places(id INTEGER,url TEXT);CREATE TABLE moz_bookmarks(id INTEGER,title TEXT,fk INTEGER,type INTEGER);')
            connection.execute('INSERT INTO moz_places VALUES(1,?)',('https://example.com/doc?token=private',))
            connection.execute('INSERT INTO moz_places VALUES(2,?)',('https://history.example/private',))
            connection.execute('INSERT INTO moz_bookmarks VALUES(1,?,1,1)',('Saved',));connection.commit();connection.close()
            self.assertTrue(backup([],root/'backup',bookmarks=[database])['ok'])
            result=(root/'backup/_service/bookmarks-1.json').read_text()
            self.assertNotIn('history.example',result);self.assertNotIn('token=private',result)
            self.assertIn('https://example.com/doc',result)

    def test_acl_manifest_verified_and_explicit_restore(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'source';source.mkdir();(source/'file').write_text('fixture')
            with patch('acl.capture',return_value={'platform':'windows','entries':[{'path':'1-source/file','status':'OK','sddl':'fixture'}]}):
                backup([source],root/'backup',preserve_acl=True)
            self.assertTrue(verify(root/'backup')['ok'])
            with patch('acl.restore',return_value={'ok':True,'restored':1}) as permissions:
                restore(root/'backup',root/'restored',True,True);permissions.assert_called_once()
