# /// script
# requires-python = ">=3.11"
# dependencies = []
#
# [tool.orcaslicer.plugin]
# name = "Devnet Anycubic Camera"
# description = "Local Kobra S1 Max webcam tab (stock firmware, LAN mode, FFmpeg)."
# author = "Devnet"
# version = "0.1.1"
# ///
"""OrcaSlicer >= 2.5.0-alpha plugin: Kobra S1 Max camera, stock firmware.

Reads the printer's HTTP-FLV stream using an external FFmpeg executable,
then relays JPEG frames to a local-only browser image via a loopback server.
No remote endpoints are contacted except the configured printer IP.
"""

import ipaddress
import json
import secrets
import shutil
import subprocess
import threading
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import orca

VERSION = "0.1.1"
FLV_PORT = 18088
FPS = 5
MAX_JPEG_BYTES = 8 * 1024 * 1024


def valid_lan_ipv4(value):
    """Allow only RFC1918 LAN IPv4 targets, never public/loopback hosts."""
    try:
        ip = ipaddress.IPv4Address(str(value).strip())
    except (ValueError, ipaddress.AddressValueError):
        return False
    return any(ip in subnet for subnet in (
        ipaddress.IPv4Network("10.0.0.0/8"),
        ipaddress.IPv4Network("172.16.0.0/12"),
        ipaddress.IPv4Network("192.168.0.0/16"),
    ))


class ReuseServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class CameraBridge:
    def __init__(self):
        self.lock = threading.RLock()
        self.condition = threading.Condition(self.lock)
        self.frame = None
        self.frame_id = 0
        self.generation = 0
        self.state = "stopped"
        self.error = ""
        self.ip = ""
        self.proc = None
        self.server = None
        self.server_thread = None
        self.token = secrets.token_urlsafe(24)
        self.recent_errors = deque(maxlen=10)

    def _serve_http(self):
        bridge = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_GET(self):
                if self.path.split("?", 1)[0] != "/feed/" + bridge.token:
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=devnetframe")
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                with bridge.lock:
                    generation = bridge.generation
                previous = -1
                try:
                    while True:
                        with bridge.condition:
                            bridge.condition.wait_for(
                                lambda: (bridge.frame_id != previous and bridge.frame is not None)
                                or bridge.generation != generation or bridge.state in ("stopped", "error"),
                                timeout=2.0,
                            )
                            if bridge.generation != generation or bridge.state in ("stopped", "error"):
                                return
                            if bridge.frame is None or bridge.frame_id == previous:
                                continue
                            frame = bridge.frame
                            previous = bridge.frame_id
                        self.wfile.write(
                            b"--devnetframe\r\nContent-Type: image/jpeg\r\nContent-Length: "
                            + str(len(frame)).encode("ascii") + b"\r\n\r\n"
                            + frame + b"\r\n"
                        )
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                    return

        self.server = ReuseServer(("127.0.0.1", 0), Handler)
        self.server_thread = threading.Thread(
            target=self.server.serve_forever,
            name="devnet-camera-http", daemon=True,
        )
        self.server_thread.start()

    def start(self, ip):
        """Called from Orca plugin callback to retain audit/permission context."""
        executable = shutil.which("ffmpeg")
        if not executable:
            with self.condition:
                self.state = "error"
                self.error = "FFmpeg not found. Install FFmpeg and restart OrcaSlicer."
                self.condition.notify_all()
            return
        # On reconfiguration close the old feed before opening the next one.
        with self.condition:
            self.generation += 1
            generation = self.generation
            old = self.proc
            self.proc = None
            self.frame = None
            self.frame_id += 1
            self.ip = ip
            self.error = ""
            self.state = "connecting"
            self.recent_errors.clear()
            self.condition.notify_all()
        if old and old.poll() is None:
            old.terminate()
        try:
            if self.server is None:
                self._serve_http()
            cmd = [
                executable, "-hide_banner", "-nostdin", "-loglevel", "error",
                "-rw_timeout", "30000000",
                "-i", f"http://{ip}:{FLV_PORT}/flv",
                "-map", "0:v:0", "-an", "-vf", f"fps={FPS}",
                "-q:v", "8", "-c:v", "mjpeg", "-f", "image2pipe", "pipe:1",
            ]
            flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            proc = subprocess.Popen(
                cmd, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                bufsize=0, creationflags=flags,
            )
            with self.condition:
                if generation != self.generation:
                    proc.terminate()
                    return
                self.proc = proc
            threading.Thread(target=self._read_frames, args=(proc, generation),
                             name="devnet-camera-reader", daemon=True).start()
            threading.Thread(target=self._read_errors, args=(proc, generation),
                             name="devnet-camera-errors", daemon=True).start()
        except (OSError, RuntimeError) as exc:
            with self.condition:
                if generation == self.generation:
                    self.state = "error"
                    self.error = f"Unable to start camera: {exc}"
                    self.condition.notify_all()

    def _read_errors(self, proc, generation):
        try:
            for line in iter(proc.stderr.readline, b""):
                clean = line.decode("utf-8", errors="replace").strip()[:240]
                if clean:
                    with self.lock:
                        if generation == self.generation:
                            self.recent_errors.append(clean)
        except (OSError, ValueError):
            pass

    def _read_frames(self, proc, generation):
        buf = bytearray()
        try:
            while True:
                chunk = proc.stdout.read(32768)
                if not chunk:
                    break
                with self.lock:
                    if generation != self.generation:
                        return
                buf.extend(chunk)
                while True:
                    begin = buf.find(b"\xff\xd8")
                    if begin == -1:
                        buf.clear()
                        break
                    if begin:
                        del buf[:begin]
                    end = buf.find(b"\xff\xd9", 2)
                    if end == -1:
                        if len(buf) > MAX_JPEG_BYTES:
                            buf.clear()
                        break
                    frame = bytes(buf[:end + 2])
                    del buf[:end + 2]
                    if len(frame) < 100:
                        continue
                    with self.condition:
                        if generation != self.generation:
                            return
                        self.frame = frame
                        self.frame_id += 1
                        self.state = "streaming"
                        self.condition.notify_all()
        except (OSError, ValueError) as exc:
            with self.lock:
                if generation == self.generation:
                    self.recent_errors.append(f"Read failed: {exc}")
        finally:
            try:
                rc = proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                proc.terminate()
                rc = -1
            with self.condition:
                if generation == self.generation:
                    self.state = "error"
                    details = self.recent_errors[-1] if self.recent_errors else f"FFmpeg exited ({rc})"
                    self.error = ("Camera feed stopped: " + details)[:310]
                    self.condition.notify_all()

    def stop(self):
        with self.condition:
            self.generation += 1
            old = self.proc
            self.proc = None
            self.frame = None
            self.frame_id += 1
            self.state = "stopped"
            self.error = ""
            self.condition.notify_all()
        if old and old.poll() is None:
            try:
                old.terminate()
            except OSError:
                pass

    def close(self):
        self.stop()
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None

    def snapshot(self):
        with self.lock:
            address = None
            if self.server is not None and self.state in ("connecting", "streaming"):
                address = f"http://127.0.0.1:{self.server.server_port}/feed/{self.token}?g={self.generation}"
            return {
                "type": "state", "state": self.state,
                "error": self.error, "printer_ip": self.ip,
                "frame_count": self.frame_id,
                "stream_url": address,
                "ffmpeg_found": bool(shutil.which("ffmpeg")),
            }


PAGE_HTML = r"""
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  :root{color-scheme:dark;} body{font-family:system-ui,sans-serif;background:#141a21;color:#eaf0f4;margin:0;padding:24px;}
  .wrap{max-width:1100px;margin:auto}.heading{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}
  h2{margin:0 0 14px;font-size:23px}.muted{color:#abbac8;font-size:13px}
  .controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:16px 0}
  input{background:#25313f;color:white;padding:11px 13px;border:1px solid #526071;border-radius:7px;max-width:190px;font:inherit}
  button{background:#387aa6;border:0;padding:12px 15px;color:white;cursor:pointer;border-radius:7px;font-weight:600}
  button.secondary{background:#384657}.screen{background:#070a0d;aspect-ratio:16/9;border:1px solid #394b60;border-radius:10px;overflow:hidden;position:relative}
  .screen img{width:100%;height:100%;object-fit:contain;display:none}
  .placeholder{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;text-align:center;color:#bdc7cf;padding:24px}
  .status{padding:12px 0;color:#ccd8e0;overflow-wrap:anywhere}.warn{color:#ffcf7c}.ok{color:#90d9b1}
</style></head><body><div class="wrap">
<div class="heading"><h2>Devnet Anycubic Camera</h2><span class="muted">Kobra S1 Max · v0.1.1 · stock firmware · LAN only</span></div>
<p class="muted">Camera feed is decoded locally with FFmpeg. No firmware changes and no cloud account required.</p>
<div class="controls">
<label for="ip">Printer IP:</label><input id="ip" placeholder="192.168.1.100" inputmode="decimal" autocomplete="off">
<button id="start">Connect camera</button><button id="stop" class="secondary">Stop</button>
</div>
<div class="screen"><img id="video" alt="Kobra S1 Max live camera"><div id="placeholder" class="placeholder">Enter your printer's local IP address and select Connect camera.</div></div>
<div id="status" class="status">Camera disconnected.</div>
<p class="muted">If the video stays blank, enable Local Network/LAN mode on the printer, start the camera once in the Anycubic app, and close any other camera viewers. First picture may be delayed.</p>
</div><script>
(() => {
 const ip = document.getElementById('ip'), img=document.getElementById('video'),
       placeholder=document.getElementById('placeholder'), status=document.getElementById('status');
 let currentURL='', loaded=false;
 function request(type, props={}) { if (window.orca?.postMessage) orca.postMessage(Object.assign({type},props)); }
 document.getElementById('start').onclick=()=>{ loaded=false;request('start',{ip:ip.value.trim()});};
 document.getElementById('stop').onclick=()=>{request('stop');};
 img.onload=()=>{loaded=true;placeholder.style.display='none';img.style.display='block';};
 img.onerror=()=>{ loaded=false;img.style.display='none';placeholder.style.display='flex';placeholder.textContent='Unable to display the local video feed.';};
 if (window.orca?.onMessage) orca.onMessage(d => {
  if (!d || d.type !== 'state') return;
  if(d.printer_ip && !ip.value) ip.value=d.printer_ip;
  if(d.stream_url && d.stream_url!==currentURL){currentURL=d.stream_url; loaded=false; img.style.display='none'; placeholder.style.display='flex'; img.src=currentURL;}
  if(!d.stream_url && currentURL){img.removeAttribute('src'); currentURL='';img.style.display='none';placeholder.style.display='flex';loaded=false;}
  if(d.state==='streaming') {status.textContent='Camera connected — live video';status.className='status ok';}
  else if(d.state==='connecting'){status.textContent='Connecting. The first picture may take 20 seconds or longer.';status.className='status';}
  else if(d.state==='error'){status.textContent=d.error || 'Camera error'; status.className='status warn';}
  else{status.textContent=d.ffmpeg_found ? 'Camera disconnected.' : 'FFmpeg not installed or not on PATH.';status.className='status';}
  if(!loaded && d.state==='connecting') placeholder.textContent='Connecting to printer camera…';
  if(!loaded && d.state==='streaming') placeholder.textContent='Waiting for first video image…';
  if(d.state==='error') placeholder.textContent='Camera unavailable. Check the message below.';
  if(d.state==='stopped') placeholder.textContent='Camera disconnected.';
 });
 request('ready'); setInterval(()=>request('status'),1500);
})();
</script></body></html>
"""


class AnycubicCameraPage(orca.pages.PagesPluginCapabilityBase):
    def get_name(self):
        return "Anycubic Camera"

    def on_load(self):
        self._bridge = CameraBridge()

    def on_unload(self):
        self._bridge.close()

    def get_default_config(self):
        return {"printer_ip": ""}

    def get_ui(self):
        return PAGE_HTML

    def on_message(self, data):
        if not isinstance(data, dict):
            return
        kind = data.get("type")
        if kind == "start":
            ip = str(data.get("ip", "")).strip()
            if not valid_lan_ipv4(ip):
                self._bridge.stop()
                with self._bridge.lock:
                    self._bridge.error = "Enter a valid private-network IPv4 address (e.g. 192.168.1.100)."
                    self._bridge.state = "error"
            else:
                self._bridge.start(ip)
                try:
                    self.save_config(json.dumps({"printer_ip": ip}))
                except (RuntimeError, ValueError, OSError):
                    pass
        elif kind == "stop":
            self._bridge.stop()
        elif kind == "ready":
            try:
                config = json.loads(self.get_config())
                if isinstance(config, dict):
                    ip = config.get("printer_ip", "")
                    if isinstance(ip, str):
                        with self._bridge.lock:
                            self._bridge.ip = ip
            except (ValueError, TypeError, RuntimeError):
                pass
        elif kind != "status":
            return
        self.post_message(self._bridge.snapshot())


@orca.plugin
class DevnetAnycubicCamera(orca.base):
    def register_capabilities(self):
        orca.register_capability(AnycubicCameraPage)
