# Onboarding Flow

## Guided Onboarding (Recommended)
```bash
cd /Users/sachingill/project/code/ai/openclaw
source .venv/bin/activate
openclaw-onboarding --output .env
```

This flow asks for:
1. Mode (`demo` or `live`)
2. Tenant and autonomy settings
3. Datadog and Grafana connection values
4. Optional webhook secrets

## Non-Interactive Onboarding
```bash
openclaw-onboarding --non-interactive --mode demo --tenant-id t1 --autonomy-level L1 --max-risk-score 2.8 --output .env --overwrite
```

## First Run
```bash
# Demo
openclaw-sentinel --mode demo --cycles 1

# Live (after setting real values in .env and exporting them)
openclaw-sentinel --mode live --cycles 1
```
