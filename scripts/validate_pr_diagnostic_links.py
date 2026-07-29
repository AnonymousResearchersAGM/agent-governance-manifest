"""Validate every deterministic page and declared artifact link."""
from __future__ import annotations
import json,os,re,signal,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from generate_pr_diagnostic_demos import SCENARIOS
def _stop(proc):
 if proc.poll() is not None:return
 if os.name=="nt":proc.send_signal(signal.CTRL_BREAK_EVENT)
 else:proc.terminate()
 try:proc.wait(timeout=10)
 except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)

def main()->int:
 pages=links=ok=audit_records=inline_assertions=0
 for slug,*_ in SCENARIOS:
  before={p.resolve() for p in Path(tempfile.gettempdir()).glob("agm-pr-diagnostic-server-*")}
  flags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name=="nt" else 0
  proc=subprocess.Popen([sys.executable,str(ROOT/"scripts/serve_pr_diagnostic_demos.py"),slug],cwd=ROOT,stdout=subprocess.PIPE,text=True,creationflags=flags)
  try:
   url=proc.stdout.readline().strip()
   health=urllib.request.urlopen(urllib.request.urljoin(url,"healthz"),timeout=10)
   if health.status!=200 or json.loads(health.read())["status"]!="ok":raise RuntimeError("health check failed")
   response=urllib.request.urlopen(url,timeout=10);html=response.read().decode();pages+=1
   if response.status!=200 or not response.headers.get_content_type()=="text/html":raise RuntimeError(url)
   ok+=1
   visible=html.split("<details>",1)[0]
   if slug=="D8_system_handled":
    if "系统已阻止一次未经授权的操作" not in visible or "verify_evidence" in visible:raise RuntimeError("D8 inline assertion failed")
    inline_assertions+=1
   if slug=="D10_final_recommendation":
    if "最终审查建议回执" not in html:raise RuntimeError("D10 receipt assertion failed")
    inline_assertions+=1
    if not all(token in visible for token in ("未连接代码托管平台","未通过本页批准 PR","未通过本页合并 PR")):raise RuntimeError("D10 platform assertion failed")
    inline_assertions+=1
   for href in re.findall(r'href="([^"]*?/artifacts/[^"]+)"',html):
    target=urllib.request.urljoin(url,href);response=urllib.request.urlopen(target,timeout=10);body=response.read().decode();links+=1
    if response.status!=200 or response.headers.get_content_type()!="text/html" or ".agm-work" in body or re.search(r"[A-Z]:\\|/(?:home|Users|tmp)/",body):raise RuntimeError(target)
    ok+=1
   audit=json.loads(urllib.request.urlopen(urllib.request.urljoin(url,"audit-summary"),timeout=10).read())
   if audit!={"records":len(re.findall(r'href="([^"]*?/artifacts/[^"]+)"',html)),"invalid":0}:raise RuntimeError(f"invalid audit summary: {audit}")
   audit_records+=audit["records"]
  finally:
   _stop(proc)
  deadline=time.time()+5
  while time.time()<deadline and ({p.resolve() for p in Path(tempfile.gettempdir()).glob("agm-pr-diagnostic-server-*")}-before):time.sleep(.05)
  leaked={p.resolve() for p in Path(tempfile.gettempdir()).glob("agm-pr-diagnostic-server-*")}-before
  if leaked:raise RuntimeError("server runtime was not cleaned")
 if pages!=11 or inline_assertions!=3:raise RuntimeError("deterministic scenario set is incomplete")
 print(json.dumps({"pages":pages,"artifact_link_clicks":links,"inline_object_assertions":inline_assertions,"http_200":ok,"http_404":0,"read_audit_records":audit_records,"invalid_audit_lines":0}))
 return 0
if __name__=="__main__":raise SystemExit(main())
