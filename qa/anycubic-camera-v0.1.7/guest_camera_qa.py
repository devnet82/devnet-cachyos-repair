#!/usr/bin/env python3
"""Fail-closed Devnet Anycubic Camera 0.1.1 QA probes inside genuine CachyOS guest.
This is a VM smoke/regression harness, NOT an OrcaSlicer integration certification.
"""
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import traceback
import types
import urllib.error
import urllib.request
from unittest.mock import patch

HERE=pathlib.Path("/mnt")
SOURCE=HERE/"devnet_anycubic_camera.py"
EXPECTED_SHA="574e217288317b8a169a34135887a8a06b7c0b214e82e15c985c918304cb5daf"
RESULT=HERE/"devnet-guest-camera-qa.json"
checks=[]
blocked=[]

def test(label,func):
    try:
        func()
        checks.append({"name":label,"result":"PASS"})
    except Exception as e:
        checks.append({"name":label,"result":"FAIL","detail":repr(e)})

def require(cond,msg):
    if not cond: raise AssertionError(msg)

def guest_os():
    txt=pathlib.Path("/etc/os-release").read_text()
    require("cachyos" in txt.lower(),"not CachyOS")
    require(shutil.which("pacman") is not None,"pacman missing")
    require("cachyos" in os.uname().release.lower(),"not CachyOS kernel")

test("Genuine CachyOS guest OS/kernel/pacman",guest_os)

def exact_source():
    require(hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED_SHA,"candidate SHA mismatch")
test("Exact unmodified v0.1.1 plugin SHA",exact_source)

orca=types.ModuleType("orca")
class Base: pass
class PageBase:
    def save_config(self,config): self._config=config
    def get_config(self): return getattr(self,"_config","{}")
    def post_message(self,data): self._last=data
orca.base=Base
orca.pages=types.SimpleNamespace(PagesPluginCapabilityBase=PageBase)
orca.plugin=lambda cls:cls
registered=[]
orca.register_capability=lambda cls:registered.append(cls)
sys.modules["orca"]=orca
p=None
try:
    spec=importlib.util.spec_from_file_location("devnet_anycubic_camera",SOURCE)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    def metadata():
        require(mod.VERSION=="0.1.1","version mismatch")
        mod.DevnetAnycubicCamera().register_capabilities()
        require(registered==[mod.AnycubicCameraPage],"capability not registered")
        require("orca.postMessage" in mod.PAGE_HTML,"webview API missing")
    test("Plugin mock import, registration and version",metadata)

    def ips():
        for ip in ("192.168.1.11","172.31.22.3","10.1.2.3"):
            require(mod.valid_lan_ipv4(ip),"private IP rejected")
        for ip in ("127.0.0.1","8.8.8.8","192.168.1.11;id","","10.0.1.1/32","::1"):
            require(not mod.valid_lan_ipv4(ip),"unsafe IP accepted")
    test("Private-IP validation and command-injection rejection",ips)

    def callbacks():
        page=mod.AnycubicCameraPage()
        page.on_load()
        page.on_message({"type":"start","ip":"8.8.8.8"})
        require(page._last["state"]=="error","invalid IP not rejected")
        page.on_message({"type":"status"})
        require(page._last["state"]=="error","status not delivered")
        page.on_unload()
    test("Plugin callback errors/status/unload",callbacks)

    def mjpeg():
        b=mod.CameraBridge()
        b._serve_http()
        require(b.server.server_address[0]=="127.0.0.1","web server not bound to localhost")
        base="http://127.0.0.1:"+str(b.server.server_port)
        try:
            urllib.request.urlopen(base+"/feed/bad",timeout=5)
            raise AssertionError("unprotected endpoint")
        except urllib.error.HTTPError as e: require(e.code==404,"wrong response")
        sample=b"\xff\xd8"+b"0"*256+b"\xff\xd9"
        with b.condition:
            b.generation=1;b.state="streaming";b.frame=sample;b.frame_id=1;b.condition.notify_all()
        with urllib.request.urlopen(base+"/feed/"+b.token,timeout=6) as resp:
            chunk=resp.read(350)
        require(b"Content-Type: image/jpeg" in chunk,"MJPEG missing")
        b.close()
    test("Real loopback HTTP authentication and MJPEG delivery",mjpeg)

    def missing_ffmpeg_reconnect():
        b=mod.CameraBridge()
        class MockProc:
            killed=False
            def poll(self): return None
            def terminate(self): self.killed=True
        old=MockProc();b.proc=old
        with patch.object(mod.shutil,"which",return_value=None): b.start("192.168.1.100")
        require(old.killed,"OLD_PROCESS_NOT_TERMINATED: reconnect with missing ffmpeg")
        b.close()
    test("Regression: missing FFmpeg reconnect shuts old process",missing_ffmpeg_reconnect)

    def denied_termination():
        b=mod.CameraBridge()
        class MockProc:
            def poll(self): return None
            def terminate(self): raise PermissionError("denied")
        b.proc=MockProc()
        with patch.object(mod.shutil,"which",return_value="/usr/bin/ffmpeg"):
            try: b.start("192.168.1.100")
            except PermissionError:
                raise AssertionError("UNHANDLED_TERMINATION_PERMISSION_ERROR")
        b.proc=None;b.close()
    test("Regression: process termination permission error recovery",denied_termination)
except Exception as e:
    checks.append({"name":"Plugin mock import + tests","result":"FAIL","detail":traceback.format_exc()[-2000:]})
finally:
    sys.modules.pop("orca",None)

if not shutil.which("ffmpeg"):
    blocked.append("Real FFmpeg decoding on CachyOS guest: ffmpeg not installed")
if not (shutil.which("orca-slicer") or shutil.which("OrcaSlicer")):
    blocked.append("Real OrcaSlicer install/enable/webview GUI: application not installed")
blocked += [
    "Actual Kobra S1 Max camera/firmware network integration: no physical printer",
    "Windows 11 deployment/upgrade/rollback: outside this CachyOS VM",
    "OrcaSlicer plugin permissions/UI integration: requires real compatible OrcaSlicer host",
]
data={"qa_gate":"0.1.7","candidate":"Devnet Anycubic Camera v0.1.1","kernel":os.uname().release,
      "os_release":pathlib.Path("/etc/os-release").read_text()[:800],
      "tests":checks,"blocked":blocked,
      "passed":sum(c["result"]=="PASS" for c in checks),
      "failed":sum(c["result"]=="FAIL" for c in checks),
      "decision":"BLOCKED"}
RESULT.write_text(json.dumps(data,indent=2)+"\n")
print("DEVNET_ANYCUBIC_GUEST_TESTS",len(checks),"PASS",data["passed"],"FAIL",data["failed"])
print("DEVNET_ANYCUBIC_CACHYOS_VM_RELEASE_BLOCKED")
