"""Validate every deterministic page and declared artifact link."""
from __future__ import annotations
import json,re,subprocess,sys,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"scripts"))
from generate_pr_diagnostic_demos import SCENARIOS
def main()->int:
 pages=links=ok=0
 for slug,*_ in SCENARIOS:
  proc=subprocess.Popen([sys.executable,str(ROOT/"scripts/serve_pr_diagnostic_demos.py"),slug],cwd=ROOT,stdout=subprocess.PIPE,text=True)
  try:
   url=proc.stdout.readline().strip();html=urllib.request.urlopen(url,timeout=10).read().decode();pages+=1;ok+=1
   for href in re.findall(r'href="([^"]*?/artifacts/[^"]+)"',html):
    target=urllib.request.urljoin(url,href);response=urllib.request.urlopen(target,timeout=10);body=response.read().decode();links+=1
    if response.status!=200 or ".agm-work" in body or re.search(r"[A-Z]:\\|/home/",body):raise RuntimeError(target)
    ok+=1
  finally:
   proc.terminate();proc.wait(timeout=10)
 print(json.dumps({"pages":pages,"artifact_links":links,"http_200":ok,"http_404":0}))
 return 0
if __name__=="__main__":raise SystemExit(main())
