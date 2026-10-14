# DriftCTL Quickstart

This guide walks through the basic DriftCTL workflow against a target you own or are explicitly authorized to assess.

## 1. Set up the environment

Requirements: Python 3.11 or newer, plus network access to the authorized test target.

```bash
git clone https://github.com/2300031984/driftctl.git
cd driftctl
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Capture a snapshot

```bash
python -m driftctl.cli.main scan TARGET
```

Replace `TARGET` with the host and port of your authorized test application, for example `127.0.0.1:8080` for a local lab.

## 3. Compare observations

Capture another snapshot after making a controlled change to the lab, then compare the latest snapshots:

```bash
python -m driftctl.cli.main diff TARGET
```

Use history to review changes across snapshots:

```bash
python -m driftctl.cli.main history TARGET
```

## 4. Establish and check a baseline

Create a baseline from the latest snapshot:

```bash
python -m driftctl.cli.main baseline TARGET
```

Compare the current state with that baseline:

```bash
python -m driftctl.cli.main anomalies TARGET
```

## 5. Investigate a finding

Use the finding ID printed by DriftCTL:

```bash
python -m driftctl.cli.main explain CHANGE-0001
python -m driftctl.cli.main evidence CHANGE-0001
```

Replace `CHANGE-0001` with the actual finding ID. Explanations summarize the observed change and its security significance; evidence helps trace the finding back to the snapshots.

## 6. Run tests

```bash
pytest -v
```

Report the actual test result when sharing changes. This guide documents the CLI workflow; it does not imply that tests were run as part of writing this document.

## Safe-use reminder

Use DriftCTL only in local labs, on systems you own, or within a clearly authorized assessment scope. Avoid unnecessary request volume and treat collected snapshots and findings as potentially sensitive data.