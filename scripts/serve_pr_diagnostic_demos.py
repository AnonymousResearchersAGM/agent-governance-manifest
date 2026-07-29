"""Serve one deterministic PR diagnostic scenario from a fresh runtime."""
from __future__ import annotations
import argparse,socket,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/"src"),str(ROOT/"scripts")]
from agm.vnext.pr_diagnostic.server import serve_pr_diagnostic
from agm.vnext.runtime import DemoExecutionContext,use_execution_context
from agm.vnext.service import GovernanceService
from generate_pr_diagnostic_demos import SCENARIOS,build_scenario
from generate_reviewer_guidance_demos import FIXED_TIME,make_project

def main()->int:
 p=argparse.ArgumentParser();p.add_argument("scenario",choices=[x[0] for x in SCENARIOS]);p.add_argument("--port",type=int,default=0);a=p.parse_args();args=next(x for x in SCENARIOS if x[0]==a.scenario)
 with tempfile.TemporaryDirectory(prefix="agm-pr-diagnostic-server-") as raw:
  with use_execution_context(DemoExecutionContext("serve-"+a.scenario,FIXED_TIME,"demo-key")):
   root=make_project(Path(raw),a.scenario);service=GovernanceService(root);case_id,_=build_scenario(service,*args)
   port=a.port
   if not port:
    with socket.socket() as probe:probe.bind(("127.0.0.1",0));port=probe.getsockname()[1]
   print(f"http://127.0.0.1:{port}/",flush=True);serve_pr_diagnostic(service,case_id=case_id,port=port)
 return 0
if __name__=="__main__":raise SystemExit(main())
