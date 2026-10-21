#!/usr/bin/env bash
# QA-only: installs official OrcaSlicer 2.5.0 Alpha in genuine ephemeral CachyOS live VM.
# A passing installation does NOT approve the Anycubic camera plugin.
set -Eeuo pipefail
exec >/mnt/devnet-orca-install-console.log 2>&1
trap 'rc=$?; echo "DEVNET_ORCA_GUEST_INSTALL_EXIT=$rc"; sync' EXIT
echo "DEVNET_ORCA_GUEST_INSTALL_BEGIN"
cat /etc/os-release
uname -r
command -v pacman
grep -iq cachyos /etc/os-release
test "$(sha256sum /mnt/OrcaSlicer.AppImage | awk '{print $1}')" = "386a5ef38991a4fc32ae2e35ee4261bea43d983683ac675a2c2e2395ab2bc7bb"
test "$(sha256sum /mnt/devnet_anycubic_camera.py | awk '{print $1}')" = "574e217288317b8a169a34135887a8a06b7c0b214e82e15c985c918304cb5daf"
echo DEVNET_ORCA_BIN_AND_PLUGIN_HASH_PASS
# OrcaSlicer 2.5.0 Alpha's AppImage needs WebKitGTK 4.1 host libraries on Arch/CachyOS.
if ! ldconfig -p | grep -q 'libwebkit2gtk-4.1.so.0'; then
  echo DEVNET_ORCA_INSTALLING_REQUIRED_WEBKITGTK41
  timeout 300 pacman -Sy --noconfirm --needed webkit2gtk-4.1
fi
ldconfig -p | grep -E 'libwebkit2gtk-4.1.so.0|libjavascriptcoregtk-4.1.so.0'
echo DEVNET_ORCA_HOST_WEBKITGTK41_PRESENT
mkdir -p /opt/devnet-orca-slicer-v2.5.0-alpha
install -m 755 /mnt/OrcaSlicer.AppImage /opt/devnet-orca-slicer-v2.5.0-alpha/OrcaSlicer.AppImage
cd /opt/devnet-orca-slicer-v2.5.0-alpha
./OrcaSlicer.AppImage --appimage-extract > /mnt/devnet-orca-extract.log 2>&1
test -x squashfs-root/AppRun
chmod a+rx /opt/devnet-orca-slicer-v2.5.0-alpha
chmod -R a+rX /opt/devnet-orca-slicer-v2.5.0-alpha/squashfs-root
echo DEVNET_REAL_ORCA_APPIMAGE_EXTRACT_INSTALL_PASS
# Discover the user running the actual Plasma graphical desktop, not the tty root user.
desktop_pid="$(pgrep -x plasmashell | head -1 || true)"
if [ -z "$desktop_pid" ]; then echo 'BLOCKED: no real KDE Plasma desktop process'; exit 7; fi
python3 - "$desktop_pid" <<'PY'
import json,os,pathlib,pwd,subprocess,sys,time
pid=int(sys.argv[1])
uid=int([x.split()[1] for x in pathlib.Path(f'/proc/{pid}/status').read_text().splitlines() if x.startswith('Uid:')][0])
pw=pwd.getpwuid(uid)
assert uid>=1000,("Plasma running under privileged account",uid)
home=pathlib.Path(pw.pw_dir)
env={}
for chunk in pathlib.Path(f'/proc/{pid}/environ').read_bytes().split(b'\0'):
    if b'=' in chunk:
        k,v=chunk.split(b'=',1)
        env[k.decode(errors='replace')]=v.decode(errors='replace')
for k in ('HOME','USER','LOGNAME'):
    env[k]=str(home) if k=='HOME' else pw.pw_name
env['XDG_RUNTIME_DIR']=env.get('XDG_RUNTIME_DIR') or f'/run/user/{uid}'
env['DISPLAY']=env.get('DISPLAY') or ':0'
env['LIBGL_ALWAYS_SOFTWARE']='1'
env['WEBKIT_DISABLE_DMABUF_RENDERER']='1'
env['NO_AT_BRIDGE']='1'
# Keep GUI auth and session bus inherited from KDE; do not create an unrelated dbus session.
print('PLASMA_GUI_USER',pw.pw_name,'UID',uid)
print('PLASMA_DISPLAY',env['DISPLAY'],'WAYLAND_DISPLAY',env.get('WAYLAND_DISPLAY',''))
print('PLASMA_DBUS',bool(env.get('DBUS_SESSION_BUS_ADDRESS')))
plugindir=home/'.config/OrcaSlicer/orca_plugins/devnet-anycubic-camera'
plugindir.mkdir(parents=True,exist_ok=True)
for directory in (home/'.config/OrcaSlicer',home/'.config/OrcaSlicer/orca_plugins',plugindir):
    os.chown(directory,uid,pw.pw_gid)
    directory.chmod(0o700)
src=pathlib.Path('/mnt/devnet_anycubic_camera.py')
dst=plugindir/'devnet_anycubic_camera.py'
dst.write_bytes(src.read_bytes())
os.chown(plugindir,uid,pw.pw_gid)
os.chown(dst,uid,pw.pw_gid)
# Add a desktop entry, so "installed" means launchable in the guest's KDE menu.
desktop=home/'.local/share/applications/devnet-orca-qa.desktop'
desktop.parent.mkdir(parents=True,exist_ok=True)
desktop.write_text('[Desktop Entry]\nType=Application\nName=OrcaSlicer 2.5.0 Alpha (Devnet QA)\nExec=/opt/devnet-orca-slicer-v2.5.0-alpha/squashfs-root/AppRun\nTerminal=false\nCategories=Graphics;3DGraphics;\n')
os.chown(desktop.parent,uid,pw.pw_gid)
os.chown(desktop,uid,pw.pw_gid)
def as_user():
    os.initgroups(pw.pw_name,pw.pw_gid)
    os.setgid(pw.pw_gid)
    os.setuid(uid)
command='/opt/devnet-orca-slicer-v2.5.0-alpha/squashfs-root/AppRun'
log=open('/mnt/devnet-orca-GUI.log','wb',buffering=0)
try:
    process=subprocess.Popen([command],cwd=pw.pw_dir,env=env,stdout=log,stderr=subprocess.STDOUT,preexec_fn=as_user,start_new_session=True)
    time.sleep(35)
    state='RUNNING' if process.poll() is None else 'EXITED_'+str(process.returncode)
    # Also check actual process; some launchers spawn and exit.
    p=subprocess.run(['pgrep','-af','OrcaSlicer|orca-slicer|squashfs-root/bin'],capture_output=True,text=True)
    print('ORCA_GUI_LAUNCHER_PID',process.pid,'STATE',state)
    print('ORCA_PROCESS_SCAN',p.stdout[:2500])
    print('PLUGIN_INSTALLED_TO',str(dst))
    report={'os':'CachyOS live KVM','orca_version':'2.5.0-alpha',
            'launcher_state':state,'launcher_pid':process.pid,
            'process_scan':p.stdout[:2500],
            'plugin_path':str(dst),
            'binary_sha256':'386a5ef38991a4fc32ae2e35ee4261bea43d983683ac675a2c2e2395ab2bc7bb',
            'plugin_sha256':'574e217288317b8a169a34135887a8a06b7c0b214e82e15c985c918304cb5daf',
            'install_verified':True,'gui_still_running':process.poll() is None,
            'plugin_loaded_in_real_host':'NOT_TESTED','camera_live':'NOT_TESTED',
            'qa_gate':'0.1.7','release_decision':'BLOCKED'}
    pathlib.Path('/mnt/devnet-orca-install.json').write_text(json.dumps(report,indent=2))
    if process.poll() is not None: raise RuntimeError('OrcaSlicer GUI process exited; see devnet-orca-GUI.log')
finally: log.close()
PY
echo DEVNET_ORCA_REAL_GUI_PROCESS_SURVIVED_35_SECONDS
sync
