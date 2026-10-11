#!/usr/bin/env python3
import io
import json
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from audit_archives import audit

class AuditArchiveTests(unittest.TestCase):
    def test_good_zip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"good.zip"
            with zipfile.ZipFile(p,"w",compression=zipfile.ZIP_DEFLATED) as z:
                z.writestr("app/VERSION","0.1.29\n")
                z.writestr("app/bin/tool.py","x = 3\n")
                z.writestr("app/install.sh","#!/bin/bash\necho test\n")
                z.writestr("app/c.json",'{"key": 1}')
                z.writestr("app/img.svg",'<svg xmlns="http://www.w3.org/2000/svg"></svg>')
            r=audit(p)
            self.assertEqual(r["overall"],"PARTIAL")
            self.assertEqual(r["checks"]["archive_integrity"]["status"],"PASS")
            self.assertEqual(r["checks"]["static_syntax"]["status"],"PASS")
            self.assertEqual(r["master_qa"],"BLOCKED")
    def test_missing(self):
        with tempfile.TemporaryDirectory() as d:
            r=audit(Path(d)/"none.zip")
            self.assertEqual(r["overall"],"FAIL")
    def test_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"unsafe.zip"
            with zipfile.ZipFile(p,"w") as z:z.writestr("../bad.py","x=1\n")
            r=audit(p)
            self.assertEqual(r["checks"]["unsafe_members"]["status"],"FAIL")
            self.assertEqual(r["overall"],"FAIL")
    def test_bad_python_syntax(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"syntax.zip"
            with zipfile.ZipFile(p,"w") as z:z.writestr("x.py","def invalid(\n")
            r=audit(p)
            self.assertEqual(r["checks"]["static_syntax"]["status"],"FAIL")
    def test_bad_bash_syntax(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"syntax.zip"
            with zipfile.ZipFile(p,"w") as z:z.writestr("install.sh","#!/bin/bash\nif true; then\n")
            r=audit(p)
            self.assertEqual(r["checks"]["static_syntax"]["status"],"FAIL")
    def test_duplicate_member(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"repeat.zip"
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore",UserWarning)
                with zipfile.ZipFile(p,"w") as z:
                    z.writestr("same/file","one")
                    z.writestr("same/file","two")
            r=audit(p)
            self.assertEqual(r["overall"],"FAIL")
    def test_good_gzip_tar(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"good.tar.gz"
            with tarfile.open(p,"w:gz") as t:
                data=b"x = 1\n"
                obj=tarfile.TarInfo("package/a.py")
                obj.size=len(data);t.addfile(obj,io.BytesIO(data))
            r=audit(p)
            self.assertEqual(r["checks"]["archive_integrity"]["status"],"PASS")
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"links.tar.gz"
            with tarfile.open(p,"w:gz") as t:
                obj=tarfile.TarInfo("package/linked");obj.type=tarfile.SYMTYPE;obj.linkname="../outside"
                t.addfile(obj)
            r=audit(p)
            self.assertEqual(r["checks"]["unsafe_members"]["status"],"FAIL")
    def test_digest_pinning(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"p.zip"
            with zipfile.ZipFile(p,"w") as z:z.writestr("x.py","pass\n")
            r=audit(p,"0"*64)
            self.assertEqual(r["checks"]["expected_sha256"]["status"],"FAIL")
    def test_truncated(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.zip"
            p.write_bytes(b"PK broken ZIP")
            r=audit(p)
            self.assertEqual(r["overall"],"FAIL")
if __name__ == "__main__":
    unittest.main(verbosity=2)
