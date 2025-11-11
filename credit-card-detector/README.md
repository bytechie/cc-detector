# Credit Card Detector Starter Kit

This starter kit demonstrates a simple pipeline for detecting and redacting credit card numbers in logs. It includes a minimal Claude Subagent, Skills for detection and redaction, placeholders for Presidio services, and an n8n workflow export.

Quick start

1. Copy `.env.example` to `.env` and adjust values.
2. Run `./setup.sh` or `make setup` to create a virtualenv and install dependencies (if `requirements.txt` exists).
3. Optionally start docker services: `make docker-up`.
4. Start the subagent locally: `python -m claude_subagent.app` or `make start-subagent`.

Scan example:

# Credit Card Detector — Starter Kit

Lightweight starter kit for detecting and redacting credit-card numbers in logs. It contains:

- A minimal Claude Subagent (Flask) that exposes a `/scan` endpoint.
- Skills implemented in Python for detection and redaction, with optional Presidio wrappers.
- Docker Compose config to bring up Presidio analyzer/anonymizer services.
- An exported n8n workflow to integrate ingestion and alerts.
- Pytest unit tests and helper scripts for local development.

This README explains how to set up, run and test the project locally.

## Requirements

- Linux / macOS or WSL for Windows
- Python 3.11+ (the project venv is created in `credit-card-detector/.venv` by `setup.sh`)
- Docker & Docker Compose (optional, needed for Presidio services)

## Quick start (recommended)

1. Copy environment template and edit if needed:

```bash
cp .env.example .env
```

2. Create a virtualenv and install dependencies:

```bash
./setup.sh
# or manually:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run unit tests to verify everything is working:

```bash
# from repository root
PYTHONPATH=credit-card-detector .venv/bin/python -m pytest credit-card-detector/tests -q
```

## Development workflow

Start only the subagent (no Docker):

```bash
# Activate the venv created by setup.sh
source credit-card-detector/.venv/bin/activate
# Run the Flask subagent
python -m claude_subagent.app
```

Scan a quick example using curl:

```bash
curl -X POST http://localhost:5000/scan \
  -H 'Content-Type: application/json' \
  -d '{"text":"Charge: 4111 1111 1111 1111"}'
```

The response JSON contains two fields: `detections` (list of detection objects) and `redacted` (the redacted string).

## Health checks

The subagent exposes a `/health` endpoint that provides service status and dependency health checks:

```bash
curl http://localhost:5000/health
```

Health check response includes:
- `status`: Overall service status (`ok`, `degraded`)
- `service`: Name of the subagent service
- `dependencies`: Health status of Presidio analyzer and anonymizer services

**Example response:**
```json
{
  "status": "ok",
  "service": "claude-subagent",
  "dependencies": {
    "analyzer": {
      "name": "presidio-analyzer",
      "status": "healthy",
      "url": "http://localhost:3000"
    },
    "anonymizer": {
      "name": "presidio-anonymizer",
      "status": "unreachable",
      "url": "http://localhost:3001",
      "error": "Connection refused"
    }
  }
}
```

**Environment variables for custom Presidio URLs:**
```bash
export PRESIDIO_ANALYZER_URL=http://custom-host:3000
export PRESIDIO_ANONYMIZER_URL=http://custom-host:3001
```

## Using Presidio (optional)

To exercise the Presidio-backed skill wrappers, start the analyzer & anonymizer services with Docker Compose:

```bash
# from repository root
docker-compose up -d
# wait for services to be healthy, then call the subagent as above
```

The Presidio wrappers first try the service endpoints and fall back to the local skills when unavailable.

## Tests

Unit tests live under `credit-card-detector/tests`.

Run the tests (from repo root):

```bash
# using the venv created by setup.sh
PYTHONPATH=credit-card-detector .venv/bin/python -m pytest credit-card-detector/tests -q
```

If you prefer to run tests from inside the project folder:

```bash
cd credit-card-detector
source .venv/bin/activate
python -m pytest -q
```

## Makefile targets

- `make setup` — runs `./setup.sh` (create venv + install deps if requirements exist)
- `make docker-up` — `docker-compose up -d` (starts Presidio services)
- `make docker-down` — `docker-compose down`
- `make test-unit` — runs `pytest` (this target runs pytest in whatever working directory Make executes; see note below)

Note: the Makefile's `test-unit` assumes you're running from the `credit-card-detector` context; if running from repo root, run tests with `PYTHONPATH=credit-card-detector` as shown above.

## n8n workflow

Import `n8n-workflow/workflow.json` into an n8n instance and wire an HTTP trigger -> HTTP Request (to the subagent) -> conditional/alert/storage nodes as desired.

## CI / Next steps

- Add a GitHub Actions workflow to run tests and lint (ensure the workflow sets `PYTHONPATH=credit-card-detector` or runs pytest from the `credit-card-detector` folder).
- Add a `make coverage` target and coverage reporting.
- Consider publishing the detection code as a separate package if you want to reuse it in other projects.

## Security note

This repository contains example code that processes potentially sensitive data. Do not log or commit real PII. Use secrets management and access controls when running in production.

## License & Contributing

See `CONTRIBUTING.md` and `LICENSE.md` for contribution guidelines and license details.

Happy hacking — open an issue or PR if you'd like features or changes.
