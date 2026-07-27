# P92 Human-Work Cognitive Pilot Harness

This directory is the tracked source for the P92 internal cognitive-pilot
delivery package. The delivery package is built outside the repository and
must be run against a separate, clean checkout at the frozen artifact commit:

`cb1d741dac841a18dce3de53141ff66b1a57649b`

P92 is not a formal sample. It does not modify AGM source, policy, or
participant-facing compilers. Runtime case state is copied from read-only
baselines into the delivery package's own `runtime/` directory.

Build the baselines and delivery package with:

```powershell
.\.venv\Scripts\python.exe experiments\p92_cognitive_pilot\scripts\build_p92_baselines.py `
  --repo-root . `
  --package-root experiments\p92_cognitive_pilot

.\.venv\Scripts\python.exe experiments\p92_cognitive_pilot\scripts\build_delivery.py `
  --source experiments\p92_cognitive_pilot `
  --output ..\P92_AGM_Human_Work_Cognitive_Pilot
```

The tracked tests are in `tests/test_p92_cognitive_pilot.py`.
