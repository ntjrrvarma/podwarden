# PodWarden

PodWarden is an early-stage Kubernetes incident triage agent that ingests Prometheus Alertmanager webhook payloads and prepares the foundation for AI-assisted diagnosis and safe remediation.

The project currently focuses on:
- a FastAPI alert ingress,
- strict Pydantic models for Alertmanager payloads and remediation actions,
- a clean separation between ingestion, enrichment, triage, and execution.

## Current status

This repository is in an early prototype stage. The core webhook receiver is working and exposes a health endpoint plus an alert ingestion endpoint.

Implemented so far:
- `src/main.py`: FastAPI app with `/health` and `/alerts`
- `src/schemas.py`: Alertmanager and triage action schemas
- package structure for future triage, enrichment, and kubectl execution logic

## Why this exists

When a Kubernetes alert fires, engineers often need to manually collect logs, inspect pod events, and correlate the issue before deciding on a remediation step. PodWarden aims to reduce that overhead by turning alert payloads into structured, typed workflow inputs that can feed future diagnosis and execution layers.

## Project structure

```text
podwarden/
├── docs/
│   ├── day-01.md
│   └── devlogs/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── engine/
│   │   └── triage.py
│   ├── enrichers/
│   │   └── k8s.py
│   └── executors/
│       └── kubectl.py
├── README.md
├── requirements.txt
├── pyproject.toml
└── tests/
```

## Quickstart

### 1) Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Run the app

```bash
uvicorn src.main:app --reload --port 8000
```

### 4) Verify the service

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"healthy","service":"podwarden","version":"0.1.0"}
```

## API

### GET /health

Returns the liveness status of the service.

### POST /alerts

Accepts an Alertmanager webhook payload and queues it for background processing.

Example:

```bash
curl -X POST http://localhost:8000/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "version": "4",
    "groupKey": "{}/{}",
    "status": "firing",
    "receiver": "podwarden",
    "alerts": [
      {
        "status": "firing",
        "labels": {
          "alertname": "KubePodCrashLooping",
          "namespace": "production",
          "pod": "auth-api-7c874d5bc7-rk8lq",
          "severity": "critical"
        },
        "annotations": {
          "summary": "Pod is crash looping"
        },
        "startsAt": "2026-09-21T10:00:00Z"
      }
    ]
  }'
```

## Design notes

The current architecture is intentionally strict and deterministic:

- `src/schemas.py` defines typed contracts for Alertmanager data and triage output
- `src/main.py` handles ingestion and validation
- future enrichers will query Kubernetes telemetry such as pod state, logs, and events
- future triage logic will produce structured remediation guidance instead of free-form text
- future executor logic will validate commands before they are executed

## Documentation

- [docs/day-01.md](docs/day-01.md) for the first project milestone
- [docs/devlogs](docs/devlogs) for ongoing development notes and updates

## Roadmap

Planned next milestones include:
1. Kubernetes telemetry enrichment via the official Python client
2. AI-assisted diagnosis using runbook context and alert evidence
3. safe remediation command generation with validation layers
4. end-to-end incident processing from Alertmanager webhook to execution plan

## License

This project is currently being developed as an open-source infrastructure tool. See the repository license file for the current terms if one is added to the project.
