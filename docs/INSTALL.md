# Installation

## Quick Install
```bash
cd /Users/sachingill/project/code/ai/openclaw
./scripts/install.sh
```

The installer will:
1. Validate Python 3.10+
2. Create `.venv` if missing
3. Install package in editable mode
4. Print next-step commands

## Manual Install
```bash
cd /Users/sachingill/project/code/ai/openclaw
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
```
