# Paladin Demo Runbook

This runbook is for local demo use under time pressure.

## 1. Start the backend

From [apps/api](/Users/rui.gao/Desktop/MBZUAI/Hackathons/Gstack/projects/paladin/apps/api):

```bash
uv sync
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Expected health check:

```bash
curl -sS http://127.0.0.1:8000/healthz
```

Expected response:

```json
{"status":"ok"}
```

## 2. Start the frontend

From [apps/web](/Users/rui.gao/Desktop/MBZUAI/Hackathons/Gstack/projects/paladin/apps/web):

```bash
npm install
npm run dev
```

Open the local Vite URL shown in the terminal.

## 3. Happy-path demo

1. Open the Simulation screen.
2. Leave input mode on `Sample model`.
3. Use `ResNet50 demo`.
4. Keep batch size `8`.
5. Keep precision `FP16`.
6. Click `Generate estimate`.
7. Narrate:
   - winner summary first
   - assumptions and confidence second
   - latency / throughput / perf-per-watt third

## 4. Real upload path

If you have a valid ONNX file:

1. Switch to `Upload ONNX`
2. Choose the `.onnx` file
3. Set batch size and precision
4. Click `Generate estimate`

The frontend sends multipart form data to `/api/v1/report/upload`.

## 5. Fallback path

If the API is down or unreachable:

- the frontend falls back to demo payload data
- a warning banner appears in the report
- continue the demo using the sample-model story

If upload parsing fails:

- switch back to `Sample model`
- use `ResNet50 demo`

## 6. Useful verification commands

Sample JSON path:

```bash
curl -sS -X POST http://127.0.0.1:8000/api/v1/report \
  -H 'Content-Type: application/json' \
  -d '{"input_mode":"sample","model_name":null,"sample_model_id":"resnet50-demo","batch_size":8,"precision":"fp16"}'
```

Backend tests:

```bash
cd apps/api
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

Frontend build:

```bash
cd apps/web
npm run build
```

## 7. Demo talking points

- Paladin is analytical, not a benchmark runner.
- The value is reducing hardware evaluation friction before boards are shipped.
- Confidence and assumptions are visible because trust matters more than fake precision.
