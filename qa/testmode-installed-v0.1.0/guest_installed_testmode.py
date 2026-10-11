#!/usr/bin/env python3
"""QA-only isolated original-ZIP test-mode installs in INSTALLED CachyOS BTRFS.

Not full production dependency or physical hardware acceptance. Runs only as
unprivileged VM user in disposable HOME, with a pinned candidate digest.
"""
import hashlib,json,os,stat,subprocess,sys
from pathlib import Path,PurePosixPath
from zipfile import ZipFile

def digest(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
def require(v,msg):
 if not v:raise AssertionError(msg)
def cmd(home,pkg,script,envx=None,timeout=90):
 env=dict(os.environ)
 env.update({"HOME":str(home),"XDG_CONFIG_HOME":str(home/".config"),"XDG_CACHE_HOME":str(home/".cache"),
             "XDG_DATA_HOME":str(home/".local/share"),"PYTHONNOUSERSITE":"1","DEVNET_QA_VM":"1"})
 if envx:env.update(envx)
 try:
  p=subprocess.run(["bash",str(pkg/script)],cwd=pkg,env=env,text=True,
             capture_output=True,errors="replace",timeout=timeout)
  return p.returncode,(p.stdout+"\n"+p.stderr)[-4500:]
 except subprocess.TimeoutExpired:return 124,"TIMEOUT"

def rgb(home,pkg,checks):
 cfg=home/".config/devnet-rgb-master/config.json"
 cfg.parent.mkdir(parents=True,exist_ok=True)
 original={"app_version":"8.8","poll_seconds":7,"local_device_names":["TEST_GPU"],"bands":[{"color":"blue","min":20}]}
 cfg.write_text(json.dumps(original))
 env={"DEVNET_TEST_MODE":"1"}
 rc,out=cmd(home,pkg,"install.sh",env)
 require(rc==0,"RGB v8.11 TEST_MODE installation failed: "+out)
 b=home/".local/bin"
 require((b/"devnet-rgb-control").is_file() and (b/"devnet-rgb-doctor").is_file(),"RGB installed binary absent")
 new=json.loads(cfg.read_text())
 require(new.get("app_version")=="8.11","RGB app_version mismatch")
 for k in ("poll_seconds","local_device_names","bands"):
  require(new.get(k)==original[k],"RGB config migration lost "+k)
 checks["testmode_install"]="PASS"
 checks["configuration_migration_fixture"]="PASS"
 before=digest(cfg)
 rc,out=cmd(home,pkg,"install.sh",env)
 require(rc==0 and before==digest(cfg),"RGB repeat install failed: "+out)
 checks["repeat_install"]="PASS"
 rc,out=cmd(home,pkg,"uninstall.sh",env)
 require(rc==0,"RGB uninstall failed: "+out)
 require(not (b/"devnet-rgb-control").exists() and not (b/"devnet-rgb-doctor").exists(),"RGB binaries remain after uninstall")
 require(cfg.is_file() and digest(cfg)==before,"RGB config not preserved on uninstall")
 checks["testmode_uninstall_preserve_config"]="PASS"

def chatbox(home,pkg,checks):
 cfg=home/".config/devnet-chatbox/preferences.json";cfg.parent.mkdir(parents=True,exist_ok=True)
 cfg.write_text('{"private_setting":"preserve-me"}\n')
 orig=digest(cfg)
 env={"DEVNET_CHATBOX_TEST_MODE":"1"}
 rc,out=cmd(home,pkg,"install.sh",env)
 require(rc==0,"ChatBox TEST_MODE install failed: "+out)
 b=home/".local/bin";target=home/".local/share/devnet-chatbox"
 require((b/"devnet-chatbox").exists() and (target/"VERSION").read_text().strip()=="0.1.3.133-gtk","Installed ChatBox missing or wrong version")
 require(digest(cfg)==orig,"user configuration changed")
 checks["testmode_install"]="PASS"
 before=digest(target/"app/main.py")
 rc,out=cmd(home,pkg,"install.sh",env)
 require(rc==0,"ChatBox repeat install failed: "+out)
 require(digest(target/"app/main.py")==before,"App changed on identical install")
 checks["repeat_install"]="PASS"
 rc,out=cmd(home,pkg,"install.sh",{**env,"DEVNET_CHATBOX_TEST_FAIL_AFTER_DELETE":"1"})
 require(rc!=0,"ChatBox injected failure unexpectedly succeeded")
 require((b/"devnet-chatbox").exists() and digest(target/"app/main.py")==before,"ChatBox interrupted transaction not rolled back")
 checks["interrupted_install_rollback"]="PASS"
 rc,out=cmd(home,pkg,"uninstall.sh",env)
 require(rc==0 and not (b/"devnet-chatbox").exists(),"ChatBox uninstall failed: "+out)
 require(digest(cfg)==orig,"ChatBox config lost on uninstall")
 checks["testmode_uninstall_preserve_config"]="PASS"

def wrapper(home,pkg,checks):
 root=home/"Steam Library"
 tools=root/"steamapps/compatdata/438100/pfx/drive_c/users/steamuser/AppData/LocalLow/VRChat/VRChat/Tools"
 tools.mkdir(parents=True,exist_ok=True)
 (tools/"yt-dlp.exe").write_text("ORIGINAL_VRCHAT\n")
 (tools/"yt-dlp-real.exe").write_text("REAL_YTDLP\n")
 (tools/"deno.exe").write_text("FAKE_DENO\n")
 tools_original=digest(tools/"yt-dlp.exe")
 bindir=home/"fake-compiler";bindir.mkdir()
 compiler=bindir/"x86_64-w64-mingw32-gcc"
 compiler.write_text("#!/usr/bin/env bash\nset -e\nwhile [ \"$#\" -gt 0 ]; do if [ \"$1\" = -o ]; then shift; printf 'FAKE_WRAPPER_FIXTURE\\n' > \"$1\"; exit 0; fi; shift; done\nexit 2\n")
 compiler.chmod(0o755)
 env={"STEAM_COMPAT_CLIENT_INSTALL_PATH":str(root),"PATH":str(bindir)+":"+os.environ.get("PATH","/usr/bin:/bin")}
 rc,out=cmd(home,pkg,"install.sh",env)
 require(rc==0,"Wrapper fake-prefix install failed: "+out)
 require((tools/"yt-dlp.exe").read_text().strip()=="FAKE_WRAPPER_FIXTURE","Wrapper binary not staged in isolated prefix")
 checks["fixture_install"]="PASS"
 rc,out=cmd(home,pkg,"install.sh",env)
 require(rc==0,"Wrapper repeated fake prefix install failed: "+out)
 checks["repeat_fixture_install"]="PASS"
 rc,out=cmd(home,pkg,"uninstall.sh",env)
 require(rc==0 and digest(tools/"yt-dlp.exe")==tools_original,"Wrapper did not restore original yt-dlp: "+out)
 checks["fixture_uninstall_restore_original"]="PASS"
 (tools/"deno.exe").unlink()
 current=digest(tools/"yt-dlp.exe")
 rc,out=cmd(home,pkg,"install.sh",env)
 require(rc!=0 and current==digest(tools/"yt-dlp.exe"),"Missing Deno did not fail safely")
 checks["missing_dependency_preflight"]="PASS"

def main():
 if len(sys.argv)!=6:raise SystemExit("usage: guest APP ZIP SHA HOME OUT")
 app,archive,expected,home,result=sys.argv[1:]
 archive=Path(archive);home=Path(home);result=Path(result)
 d={"schema":"devnet-installed-cachyos-original-testmode-v0.1.0","app":app,
   "checks":{},"full_production_install":"NOT_TESTED",
   "real_device_or_steam_runtime":"NOT_TESTED","gui_visual_acceptance":"NOT_TESTED",
   "vm_mode":"ORIGINAL_PACKAGE_EXPLICIT_TEST_MODE_OR_ISOLATED_FAKE_STEAM_PREFIX",
   "release_approval":"BLOCKED"}
 try:
  require(os.geteuid()!=0,"never execute app as root")
  require("ID=cachyos" in Path("/etc/os-release").read_text(),"not CachyOS")
  require(subprocess.run(["findmnt","-no","FSTYPE","/"],capture_output=True,text=True).stdout.strip()=="btrfs","not BTRFS installed guest")
  d["checks"]["installed_native_cachyos_btrfs"]="PASS"
  require(digest(archive)==expected,"original ZIP digest mismatch")
  with ZipFile(archive) as z:
   require(z.testzip() is None,"ZIP corrupt")
   for entry in z.infolist():
    n=entry.filename
    require(not n.startswith(("/","\\")) and "\\" not in n and ".." not in PurePosixPath(n).parts and not stat.S_ISLNK(entry.external_attr>>16),"unsafe archive member")
   unpack=home/"candidate-extracted";unpack.mkdir()
   z.extractall(unpack)
   for info in z.infolist():
    if info.is_dir():continue
    p=unpack/info.filename
    if p.is_file() and (info.filename.endswith(".sh") or bool((info.external_attr>>16)&0o111) or info.filename.endswith("/bin/devnet-chatbox")):
     p.chmod(p.stat().st_mode|0o111)
  d["checks"]["original_candidate_checksum"]="PASS"
  package=next(x for x in unpack.iterdir() if x.is_dir())
  if app=="rgb":rgb(home,package,d["checks"])
  elif app=="chatbox":chatbox(home,package,d["checks"])
  elif app=="wrapper":wrapper(home,package,d["checks"])
  else:raise ValueError("unsupported app")
 except Exception as exc:
  d["checks"]["fixture_test"]="FAIL"
  d["error"]=str(exc)[:450]
 result.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
 print(json.dumps(d["checks"],sort_keys=True))
 return 1 if "FAIL" in d["checks"].values() else 0
if __name__=="__main__":raise SystemExit(main())
