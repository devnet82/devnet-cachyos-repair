#!/usr/bin/env python3
"""Isolated Devnet Ollama model-switching QA candidate; no VM control."""
import argparse, json, os, tempfile, time, urllib.request, urllib.error
from pathlib import Path
BASE="http://127.0.0.1:11434"
class RouterError(RuntimeError): pass
class Ollama:
    def __init__(self,base=BASE,timeout=180):
        if base!=BASE: raise RouterError("Only local Ollama permitted")
        self.base,self.timeout=base,timeout
    def call(self,path,payload=None):
        data=None if payload is None else json.dumps(payload).encode()
        request=urllib.request.Request(self.base+path,data=data,headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(request,timeout=self.timeout) as response: return json.load(response)
        except (urllib.error.URLError,ValueError,TimeoutError) as exc: raise RouterError("Ollama request failed") from exc
    def loaded(self): return {x["name"] for x in self.call("/api/ps").get("models",[])}
    def unload(self,model):
        self.call("/api/generate",{"model":model,"prompt":"","stream":False,"keep_alive":0})
        for _ in range(10):
            if model not in self.loaded(): return
            time.sleep(.2)
        raise RouterError("Unloading model could not be verified")
    def load(self,model):
        self.call("/api/generate",{"model":model,"prompt":"","stream":False,"keep_alive":"10m"})
        for _ in range(10):
            if model in self.loaded(): return
            time.sleep(.2)
        raise RouterError("Loading model could not be verified")
    def run(self,model,prompt,retain=False):
        if self.loaded()-{model}: raise RouterError("Other Ollama models loaded")
        try:
            result=self.call("/api/generate",{"model":model,"prompt":prompt,"stream":False,"keep_alive":"10m" if retain else 0,"options":{"num_predict":2048}})
            if not result.get("done") or result.get("done_reason")=="length" or not isinstance(result.get("response"),str):
                raise RouterError("Incomplete or truncated response")
            return result["response"]
        finally:
            if not retain: self.unload(model)
    def switch(self,default,specialist,task):
        if self.loaded()-{default}: raise RouterError("Other Ollama models loaded")
        if default in self.loaded(): self.unload(default)
        try: return self.run(specialist,task)
        finally: self.load(default)
def checkpoint(path,record):
    path=Path(path)
    if not path.parent.is_dir() or path.is_symlink(): raise RouterError("Invalid checkpoint path")
    fd,tmp=tempfile.mkstemp(prefix=".router-",dir=path.parent)
    try:
        os.fchmod(fd,0o600)
        with os.fdopen(fd,"w") as f:
            json.dump(record,f,indent=2); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
def execute(client,task,specialist,default,path):
    path=Path(path)
    if path.exists() or path.is_symlink(): raise RouterError("Refusing checkpoint overwrite")
    if not path.parent.is_dir() or not task.strip() or not specialist or not default or specialist==default:
        raise RouterError("Invalid task, models or checkpoint")
    record={"status":"STARTED","task":task,"specialist":specialist,"default":default}
    checkpoint(path,record)
    try:
        record["specialist_response"]=client.switch(default,specialist,task)
        record["status"]="SPECIALIST_FINISHED"; checkpoint(path,record)
        record["summary"]=client.run(default,"Summarise without inventing tests or actions:\n"+record["specialist_response"],retain=True)
        record["status"]="FINISHED"; checkpoint(path,record)
        return record
    except Exception as exc:
        record["status"]="BLOCKED";record["error"]=f"{type(exc).__name__}: {exc}"
        checkpoint(path,record);raise
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--specialist",required=True);p.add_argument("--default",default="qwen3.5:9b")
    p.add_argument("--task",required=True);p.add_argument("--checkpoint",required=True)
    a=p.parse_args()
    print(execute(Ollama(),a.task,a.specialist,a.default,a.checkpoint)["summary"])
if __name__=="__main__": main()
