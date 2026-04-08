# Paladin

Paladin is a try-before-you-buy workload simulator for AI chip vendors.

It lets a prospect upload an ONNX model, choose runtime settings like batch size
and precision, and get an analytical comparison of how that workload would likely
perform on DeepX versus GPU and CPU baselines.

## What is in this repo

- `apps/api` — FastAPI backend for report generation
- `apps/web` — Vite + React dashboard frontend
- `CONTRACTS.md` — backend/frontend payload contract
- `DESIGN.md` — visual system and UI direction
- `PLAN.md` — MVP plan and scope
- `RUNBOOK.md` — local demo and verification steps

## Current MVP

- ONNX upload or sample model fallback
- Batch size and precision controls
- Analytical report payload with:
  - latency
  - throughput
  - power
  - performance per watt
- Confidence and assumptions shown in the report
- Ephemeral reports only, no persistence

## Local development

### Backend

```bash
cd apps/api
uv sync
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8002
```

### Frontend

```bash
cd apps/web
npm install
VITE_API_BASE_URL=http://127.0.0.1:8002 npm run dev -- --host 127.0.0.1 --port 4173
```

## Verification

### Backend tests

```bash
cd apps/api
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

### Frontend build

```bash
cd apps/web
npm run build
```

## Notes

Paladin is intentionally analytical, not benchmark-measured. The product is built
to reduce hardware evaluation friction before physical boards are shipped.
