# DriftCTL

### Attack Surface Drift Detection CLI

DriftCTL is a Python-based cybersecurity CLI that detects changes in an application's externally observable attack surface over time.

Instead of performing a one-time security scan, DriftCTL establishes a known baseline, captures snapshots, compares changes, classifies their security significance, and preserves findings with evidence and explanations.

> **DriftCTL v1.0** — Baseline-driven attack surface monitoring for authorized targets.

---

## Why DriftCTL?

An application's attack surface changes continuously.

Endpoints can be added, removed, exposed, restricted, or modified. A security control that required authentication yesterday may behave differently today.

Traditional reconnaissance answers:

> **"What is exposed right now?"**

DriftCTL focuses on:

> **"What changed since the last known state, and why does that change matter?"**

---

## Core Workflow

```text
                    Authorized Target
                           │
                           ▼
                    HTTP Discovery
                           │
                           ▼
                      Snapshot
                           │
                           ▼
                    Normalization
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
        Snapshot Diff              Baseline
              │                         │
              ▼                         ▼
       Change Classification      Anomaly Detection
              │                         │
              └────────────┬────────────┘
                           ▼
                    Security Findings
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           History      Evidence    Explainability
```

---

## Features

### Attack Surface Discovery

Discovers HTTP endpoints from the target and linked application pages.

Current observations include:

- HTTP endpoints
- HTTP status codes
- Content type
- Server fingerprint
- Response content length

### Snapshot Management

Every scan creates a timestamped snapshot:

```text
data/snapshots/
```

Snapshots provide the historical state required for drift analysis.

### Change Detection

DriftCTL identifies:

- `NEW` — previously unseen asset
- `REMOVED` — previously observed asset no longer present
- `CHANGED` — existing asset changed behavior or metadata

### Risk Classification

Changes are classified according to their security significance.

Examples:

```text
401 → 200    HIGH
403 → 200    HIGH

200 → 401    LOW
200 → 403    LOW

New /admin   MEDIUM
New /api/*   MEDIUM

<500 → ≥500  MEDIUM
```

The classifier is directional: it distinguishes weakened security controls from strengthened controls.

### Semantic Findings

DriftCTL generates semantic fingerprints for security events.

For example:

```text
/api/users
401 → 200
```

is treated as an authentication-control change rather than as a generic HTTP metadata difference.

This allows findings to remain correlated even when unrelated response metadata changes.

### Historical Tracking

Review attack-surface changes across all captured snapshots:

```bash
python -m driftctl.cli.main history 127.0.0.1:8080
```

### Security Findings

Findings receive persistent IDs:

```text
CHANGE-0001
CHANGE-0002
CHANGE-0003
```

Duplicate security events can be correlated using semantic fingerprints.

### Explainability

DriftCTL explains why a change matters:

```bash
python -m driftctl.cli.main explain CHANGE-0001
```

The explanation includes:

- Observed change
- Security significance
- Evidence
- Recommended action
- Fingerprint
- Detection timestamp

### Evidence Reconstruction

Evidence can be reconstructed from the snapshot pair that produced the finding:

```bash
python -m driftctl.cli.main evidence CHANGE-0001
```

### Baseline Detection

Create a known-good baseline:

```bash
python -m driftctl.cli.main baseline 127.0.0.1:8080
```

The baseline represents the expected attack-surface state.

### Anomaly Detection

Compare the latest snapshot against the baseline:

```bash
python -m driftctl.cli.main anomalies 127.0.0.1:8080
```

Example:

```text
Attack Surface Anomalies: 127.0.0.1:8080

Detected 1 anomaly(s)

[MEDIUM] CHANGED /api/users
    Observation: http_endpoint
    Reason: HTTP status changed from 200 to 401
    Baseline: {'status_code': 200, ...}
    Current: {'status_code': 401, ...}
```

---

# Installation

## Requirements

- Python 3.11+
- Linux/macOS/WSL recommended
- Network access to an authorized test target

## Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd driftctl
```

## Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

---

# Usage

## Scan

Create a new attack-surface snapshot:

```bash
python -m driftctl.cli.main scan TARGET
```

Example:

```bash
python -m driftctl.cli.main scan 127.0.0.1:8080
```

---

## Diff

Compare the two most recent snapshots:

```bash
python -m driftctl.cli.main diff TARGET
```

---

## History

Display historical attack-surface changes:

```bash
python -m driftctl.cli.main history TARGET
```

---

## Baseline

Create a baseline from the latest snapshot:

```bash
python -m driftctl.cli.main baseline TARGET
```

---

## Anomalies

Compare the latest snapshot against the baseline:

```bash
python -m driftctl.cli.main anomalies TARGET
```

---

## Explain a Finding

```bash
python -m driftctl.cli.main explain CHANGE-0001
```

---

## Show Evidence

```bash
python -m driftctl.cli.main evidence CHANGE-0001
```

---

## Migrate Legacy Findings

```bash
python -m driftctl.cli.main migrate-findings
```

---

# Example Detection Scenario

Consider an API endpoint:

```text
/api/users
```

Initial baseline:

```text
/api/users → 401 Unauthorized
```

Later snapshot:

```text
/api/users → 200 OK
```

DriftCTL detects:

```text
[HIGH] CHANGED /api/users
```

and explains that the endpoint changed from requiring authentication to returning a successful response.

The finding is assigned a semantic fingerprint and can be investigated through:

```bash
python -m driftctl.cli.main explain CHANGE-0001
```

and:

```bash
python -m driftctl.cli.main evidence CHANGE-0001
```

---

# Local Security Lab

DriftCTL was developed and tested against an isolated local Flask application.

Example target:

```text
127.0.0.1:8080
```

The lab contains controlled endpoints whose behavior can be changed to simulate attack-surface drift.

Example scenario:

```text
Baseline:

/api/users → 200


Modified application:

/api/users → 401


DriftCTL:

CHANGED /api/users
```

This allows the detection engine to be tested without scanning third-party systems.

---

# Testing

The project contains automated tests covering:

- Baseline creation and loading
- Snapshot comparison
- New endpoints
- Removed endpoints
- Changed endpoints
- Historical tracking
- Risk classification
- Directional authentication changes
- Directional authorization changes
- Semantic finding fingerprints
- Anomaly detection

Run the complete test suite:

```bash
pytest -v
```

Current status:

```text
20 passed
```

---

# Project Structure

```text
driftctl/
├── driftctl/
│   ├── cli/
│   │   └── main.py
│   │
│   ├── collectors/
│   │   ├── basic.py
│   │   ├── dns.py
│   │   ├── http.py
│   │   ├── ports.py
│   │   └── subdomains.py
│   │
│   ├── core/
│   │   ├── anomaly.py
│   │   ├── baseline.py
│   │   ├── diff.py
│   │   ├── evidence.py
│   │   ├── explain.py
│   │   ├── findings.py
│   │   ├── history.py
│   │   ├── models.py
│   │   └── risk.py
│   │
│   └── storage/
│       ├── findings.py
│       └── snapshots.py
│
├── tests/
│   ├── test_anomaly.py
│   ├── test_baseline.py
│   ├── test_diff.py
│   ├── test_findings.py
│   ├── test_history.py
│   └── test_risk.py
│
├── README.md
├── requirements.txt
├── pytest.ini
└── .gitignore
```

---

# Design Principles

## Baseline First

DriftCTL does not assume that every unusual state is automatically malicious.

A state becomes anomalous when it differs from the established baseline.

## Semantic Detection

Findings represent meaningful security events instead of raw metadata differences.

## Evidence Preservation

Every important change should be traceable back to the snapshots that produced it.

## Explainability

A detection system should explain why a change matters rather than simply reporting a difference.

## Safe Testing

Development and validation are performed against controlled, authorized environments.

---

# Security Scope

DriftCTL is intended for:

- Local security labs
- CTF environments
- Applications you own
- Explicitly authorized security assessments
- Defensive attack-surface monitoring

Do not use DriftCTL to scan systems without authorization.

---

# Technology Stack

- Python
- Pydantic
- Requests
- BeautifulSoup
- Rich
- Pytest
- JSON-based snapshot storage

---

# Roadmap

## v1.0 — Attack Surface Drift Detection

- [x] HTTP discovery
- [x] Snapshot engine
- [x] Snapshot diffing
- [x] Risk classification
- [x] Semantic fingerprints
- [x] Persistent findings
- [x] Historical tracking
- [x] Evidence reconstruction
- [x] Explainability
- [x] Baselines
- [x] Anomaly detection
- [x] Automated tests

## Future Releases

### v1.1

- Advanced reporting
- JSON/HTML exports
- Improved baseline management
- Finding lifecycle management

### v1.2

- Scheduled monitoring
- Webhook notifications
- Slack/Discord/email integrations

### v1.3

- Expanded DNS and subdomain collectors
- Port-state monitoring
- JavaScript endpoint discovery
- API-focused drift detection

### v2.0

- AI-assisted security analysis
- Intelligent change prioritization
- Historical behavioral analysis
- Advanced anomaly scoring

---

# Author

**Chintala Sai Varun**

Computer Science & Engineering  
Cybersecurity | Cloud | Security Automation

---

# License

This project is intended as an educational and defensive cybersecurity project.

Add an appropriate open-source license before publishing if you want others to reuse or modify the code.
