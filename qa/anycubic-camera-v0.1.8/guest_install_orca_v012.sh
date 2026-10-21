#!/usr/bin/env bash
# Devnet Master QA Gate v0.1.8: real software installation in disposable CachyOS VM.
set -u
exec >/mnt/devnet-software-install-console.log 2>&1
QA_GUEST=NOT_TESTED;QA_PKG=NOT_TESTED;QA_FFMPEG=NOT_TESTED
QA_ORCA_ARCHIVE=NOT_TESTED;QA_ORCA_INTEGRITY=NOT_TESTED;QA_ORCA_INSTALL=NOT_TESTED
QA_ORCA_LAUNCH=NOT_TESTED;QA_ORCA_GUI=NOT_TESTED
QA_PLUGIN=NOT_TESTED;QA_HARDWARE=NOT_TESTED;QA_APP_SHA=""
APP=/opt/devnet-qa/OrcaSlicer.AppImage
echo "DEVNET_SOFTWARE_INSTALL_V018_GUEST_START"
cat /etc/os-release; uname -r
if grep -qi 'cachyos' /etc/os-release && command -v pacman >/dev/null 2>&1;then QA_GUEST=PASS;else QA_GUEST=FAIL;fi
mkdir -p /opt/devnet-qa /tmp/devnet-qa-home
# Fully sync aged live ISO before installing dependencies: avoid partial upgrade / FFmpeg ABI mismatch.
echo "VM_DEPS_EPHEMERAL_TARGETED_INSTALL"
echo "Installing real guest packages into a disposable live ISO. No production host changes."
if timeout 220 pacman -Sy --noconfirm ffmpeg libbluray webkit2gtk-4.1 gstreamer gst-plugins-base-libs gst-plugins-base gst-plugins-good xorg-server-xvfb xorg-xauth xorg-xwininfo xorg-xwd >/tmp/devnet-pacman-install.log 2>&1;then
  QA_PKG=PASS
else
  QA_PKG=FAIL
  tail -n 45 /tmp/devnet-pacman-install.log
fi
if command -v ffmpeg >/dev/null 2>&1 && ffmpeg -version >/tmp/devnet-ffmpeg-version.txt 2>&1;then QA_FFMPEG=PASS;else QA_FFMPEG=FAIL;fi
if [ -s /mnt/OrcaSlicer.AppImage ];then
  QA_ORCA_ARCHIVE=PASS
  QA_APP_SHA="$(sha256sum /mnt/OrcaSlicer.AppImage | cut -d' ' -f1)"
  if [ -s /mnt/OrcaSlicer.AppImage.sha256 ] && [ "$QA_APP_SHA" = "$(tr -d '\r\n' </mnt/OrcaSlicer.AppImage.sha256)" ];then QA_ORCA_INTEGRITY=PASS;else QA_ORCA_INTEGRITY=FAIL;fi
  if install -m 755 /mnt/OrcaSlicer.AppImage "$APP";then
    QA_ORCA_INSTALL=PASS
    echo "APP_INSTALLED_PATH=$APP"
    "$APP" --appimage-version >/tmp/devnet-appimage-version.log 2>&1 || true
  else QA_ORCA_INSTALL=FAIL;fi
else
  QA_ORCA_ARCHIVE=FAIL;QA_ORCA_INTEGRITY=FAIL;QA_ORCA_INSTALL=FAIL
fi
if [ "$QA_ORCA_INSTALL" = PASS ] && [ "$QA_PKG" = PASS ];then
  echo "Starting genuine OrcaSlicer on Xvfb"
  Xvfb :84 -screen 0 1280x800x24 -nolisten tcp >/tmp/devnet-xvfb.log 2>&1 &
  xvfb_pid=$!
  sleep 3
  if kill -0 "$xvfb_pid" 2>/dev/null;then
    export DISPLAY=:84 HOME=/tmp/devnet-qa-home XDG_CONFIG_HOME=/tmp/devnet-qa-home/.config
    export QT_QPA_PLATFORM=xcb LIBGL_ALWAYS_SOFTWARE=1 WEBKIT_DISABLE_DMABUF_RENDERER=1 SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
    # Stage the exact plugin as a local OrcaSlicer plugin in the disposable guest profile.
    plugin_dir="$XDG_CONFIG_HOME/OrcaSlicer/orca_plugins/devnet-anycubic-camera"
    mkdir -p "$plugin_dir"
    cp -f /mnt/devnet_anycubic_camera.py "$plugin_dir/devnet_anycubic_camera.py"
    sha256sum "$plugin_dir/devnet_anycubic_camera.py" > /tmp/devnet-staged-plugin.sha256
    echo "PLUGIN_STAGED_PATH=$plugin_dir/devnet_anycubic_camera.py"
    # The local Plugins dialog normally writes this activation record.
    # Use a disposable QA profile only; NEVER modify the user's live OrcaSlicer configuration.
    cat > "$plugin_dir/.install_state.json" <<'PLUGIN_STATE'
{
  "capabilities": [],
  "enabled": true,
  "installed_from": "local",
  "installed_version": "0.1.2",
  "plugin_name": "Devnet Anycubic Camera",
  "permissions": {
    "fs_read": [], "fs_readwrite": [], "network_http": [],
    "network_socket": [], "process": [], "threading": [], "events": []
  }
}
PLUGIN_STATE
    echo "PLUGIN_ACTIVATION_RECORD_STAGED"
    # Check actual loaded capabilities in Orca logs separately: pre-staging is NOT equivalent to live integration.
    timeout 75 "$APP" --appimage-extract-and-run >/tmp/devnet-orca-launch.log 2>&1 &
    app_pid=$!
    sleep 22
    if kill -0 "$app_pid" 2>/dev/null;then QA_ORCA_LAUNCH=PASS;else QA_ORCA_LAUNCH=FAIL;echo "ORCA_EXITED_EARLY";fi
    if command -v xwininfo >/dev/null 2>&1;then
      xwininfo -root -tree >/tmp/devnet-xwininfo.log 2>&1 || true
      if grep -Eiq 'OrcaSlicer|Orca Slicer' /tmp/devnet-xwininfo.log;then QA_ORCA_GUI=PASS;else QA_ORCA_GUI=FAIL;fi
    fi
    if command -v xwd >/dev/null 2>&1;then xwd -root -silent -display :84 -out /mnt/devnet-orca-xvfb.xwd >/dev/null 2>&1 || true;fi
    echo "ORCA_RUNTIME_LOGS_BEGIN"
    if [ -d "$XDG_CONFIG_HOME/OrcaSlicer/log" ];then
      grep -RiaE 'Devnet Anycubic Camera|Anycubic Camera|plugin.*(loaded|error|failed)' "$XDG_CONFIG_HOME/OrcaSlicer/log" | tail -n 60 > /tmp/devnet-orca-plugin-load.log || true
      cat /tmp/devnet-orca-plugin-load.log || true
    fi
    echo "ORCA_RUNTIME_LOGS_END"
    kill "$app_pid" >/dev/null 2>&1 || true
  else QA_ORCA_LAUNCH=FAIL;QA_ORCA_GUI=FAIL;fi
  kill "$xvfb_pid" >/dev/null 2>&1 || true
fi
# Plugin manager / real Kobra must be separately inspected and cannot be automatically passed.
export QA_GUEST QA_PKG QA_FFMPEG QA_ORCA_ARCHIVE QA_ORCA_INTEGRITY QA_ORCA_INSTALL QA_ORCA_LAUNCH QA_ORCA_GUI QA_PLUGIN QA_HARDWARE QA_APP_SHA
python3 - <<'PY'
import json,os,pathlib
keys=("GUEST","PKG","FFMPEG","ORCA_ARCHIVE","ORCA_INTEGRITY","ORCA_INSTALL","ORCA_LAUNCH","ORCA_GUI","PLUGIN","HARDWARE")
states={k.lower():os.environ["QA_"+k] for k in keys}
report={"gate_version":"0.1.8","candidate":"Devnet Anycubic Camera v0.1.2","host_software":"OrcaSlicer v2.5.0-alpha","checks":states,"host_sha256":os.environ.get("QA_APP_SHA",""),"release_decision":"BLOCKED"}
for path,key in (("/tmp/devnet-ffmpeg-version.txt","ffmpeg_version"),("/tmp/devnet-appimage-version.log","appimage_runtime"),("/tmp/devnet-orca-launch.log","orca_launch_tail"),("/tmp/devnet-xwininfo.log","window_tree_tail"),("/tmp/devnet-pacman-install.log","pacman_log_tail"),("/tmp/devnet-staged-plugin.sha256","staged_plugin_checksum"),("/tmp/devnet-orca-plugin-load.log","plugin_load_log")):
 p=pathlib.Path(path)
 if p.exists():report[key]=p.read_text(errors="replace")[-7000:]
pathlib.Path("/mnt/devnet-software-install-v0.1.8.json").write_text(json.dumps(report,indent=2)+"\n")
print("QA_V018_RESULTS",states,"RELEASE_BLOCKED")
PY
sync
