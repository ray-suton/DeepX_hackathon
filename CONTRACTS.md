# Paladin Contracts

This file is the implementation handoff for the MVP data contract.

## [PM] Scope Contract

### Core Promise

Given an ONNX model or a fallback sample model plus runtime inputs, Paladin returns one comparative report payload for `DeepX`, `GPU`, and `CPU`.

### v1 Guarantees

- One request produces one report payload
- Reports are ephemeral
- The report is analytical, not benchmark-measured
- The same report payload drives all cards, charts, and trust UI
- Unsupported or invalid inputs fail clearly

### v1 Non-Goals

- Saved report persistence
- Multi-user support
- Authentication
- Export pipelines beyond optional client-side export
- Benchmark-grade calibration

## [Backend] Input Contract

Two accepted entry modes:

1. Uploaded ONNX model
2. Named sample model fallback

Transport:
- Sample mode uses JSON `POST /api/v1/report`
- Upload mode uses multipart `POST /api/v1/report/upload`

Request shape:

```json
{
  "input_mode": "upload",
  "model_name": "resnet50.onnx",
  "sample_model_id": null,
  "batch_size": 8,
  "precision": "fp16"
}
```

```json
{
  "input_mode": "sample",
  "model_name": null,
  "sample_model_id": "resnet50-demo",
  "batch_size": 8,
  "precision": "fp16"
}
```

Rules:
- `input_mode` must be `upload` or `sample`
- exactly one of `model_name` or `sample_model_id` must be present
- `batch_size` must be a positive integer
- `precision` defaults to `fp16` if omitted
- allowed precision values for v1: `fp32`, `fp16`, `int8`

Upload shape:
- `file`: ONNX file bytes
- `batch_size`: positive integer form field
- `precision`: `fp32`, `fp16`, or `int8`

## [Backend] Normalized Workload Spec

The parser must emit one normalized workload spec consumed by all hardware estimators.

```json
{
  "model_id": "resnet50.onnx",
  "input_mode": "upload",
  "batch_size": 8,
  "precision": "fp16",
  "input_shape": [1, 3, 224, 224],
  "layer_counts": {
    "conv": 53,
    "matmul": 1,
    "pool": 1,
    "activation": 49,
    "other": 6
  },
  "flops_total": 4089184256,
  "parameter_bytes": 102760448,
  "activation_bytes": 18874368,
  "unsupported_layers": [],
  "parser_warnings": []
}
```

Required fields:
- `model_id`
- `input_mode`
- `batch_size`
- `precision`
- `layer_counts`
- `flops_total`
- `parameter_bytes`
- `activation_bytes`
- `unsupported_layers`
- `parser_warnings`

Notes:
- `input_shape` may be `null` if it cannot be derived
- `unsupported_layers` may be non-empty even when report generation continues
- `parser_warnings` are user-visible inputs to confidence derivation

## [Backend] Report Payload

This is the single source of truth payload for the frontend.

```json
{
  "report_id": "ephemeral-resnet50-fp16-b8",
  "generated_at": "2026-04-08T06:45:00Z",
  "request": {
    "input_mode": "upload",
    "model_name": "resnet50.onnx",
    "sample_model_id": null,
    "batch_size": 8,
    "precision": "fp16"
  },
  "workload_spec": {
    "model_id": "resnet50.onnx",
    "input_shape": [1, 3, 224, 224],
    "layer_counts": {
      "conv": 53,
      "matmul": 1,
      "pool": 1,
      "activation": 49,
      "other": 6
    },
    "flops_total": 4089184256,
    "parameter_bytes": 102760448,
    "activation_bytes": 18874368,
    "unsupported_layers": [],
    "parser_warnings": []
  },
  "hardware_results": [
    {
      "hardware_id": "deepx",
      "hardware_label": "DeepX",
      "latency_ms": 11.2,
      "throughput_inf_per_sec": 89.3,
      "power_watts": 42.0,
      "perf_per_watt": 2.13,
      "breakdown": {
        "compute_ms": 7.8,
        "memory_ms": 2.6,
        "overhead_ms": 0.8
      }
    },
    {
      "hardware_id": "gpu_baseline",
      "hardware_label": "GPU Baseline",
      "latency_ms": 14.7,
      "throughput_inf_per_sec": 68.0,
      "power_watts": 95.0,
      "perf_per_watt": 0.72,
      "breakdown": {
        "compute_ms": 8.2,
        "memory_ms": 5.1,
        "overhead_ms": 1.4
      }
    },
    {
      "hardware_id": "cpu_baseline",
      "hardware_label": "CPU Baseline",
      "latency_ms": 47.5,
      "throughput_inf_per_sec": 21.0,
      "power_watts": 65.0,
      "perf_per_watt": 0.32,
      "breakdown": {
        "compute_ms": 32.0,
        "memory_ms": 12.5,
        "overhead_ms": 3.0
      }
    }
  ],
  "winner_summary": {
    "winner_hardware_id": "deepx",
    "winner_dimension": "latency",
    "headline": "DeepX is the fastest option for this workload at batch size 8.",
    "secondary_note": "DeepX also leads performance per watt under the current assumptions."
  },
  "confidence": {
    "label": "medium",
    "score": 0.68,
    "reasons": [
      "Model graph parsed successfully.",
      "No unsupported layers were detected.",
      "Power estimates are heuristic rather than measured."
    ]
  },
  "assumptions": [
    "Results are analytical estimates, not measured benchmark runs.",
    "Hardware profiles are predefined for DeepX, GPU baseline, and CPU baseline.",
    "Latency is estimated from compute, memory, and fixed overhead terms."
  ],
  "status": "ok"
}
```

## [Backend] Error Payload

All failures must return a structured error payload.

```json
{
  "status": "error",
  "error": {
    "code": "UNSUPPORTED_MODEL",
    "message": "This model uses operators not supported by the MVP parser.",
    "user_action": "Try the sample model or upload a simpler ONNX model.",
    "details": {
      "unsupported_layers": ["custom_op_v2"]
    }
  }
}
```

Allowed v1 error codes:
- `INVALID_UPLOAD`
- `INVALID_INPUT`
- `PARSE_FAILED`
- `UNSUPPORTED_MODEL`
- `ESTIMATION_FAILED`

Rules:
- `message` is plain-English and user-visible
- `user_action` tells the user what to do next
- `details` is optional and safe to expose

## [Backend] Unsupported-Model Policy

v1 policy:
- If the parser cannot read the ONNX file at all, return `PARSE_FAILED`
- If required metadata is missing and estimation cannot continue, return `PARSE_FAILED`
- If unsupported layers make the estimate meaningless, return `UNSUPPORTED_MODEL`
- If unsupported layers are minor and estimation can still proceed, continue with:
  - `status: ok`
  - non-empty `unsupported_layers`
  - reduced confidence
  - explicit warning in `confidence.reasons`

This avoids silent partial truth.

## [Frontend] Rendering Contract

Frontend rules:
- Never recompute estimator values in the UI
- Never derive winner or confidence logic in the UI
- Read everything from the report payload
- Use `status` to branch between report and error rendering

Required UI states:
- empty
- loading
- report success
- structured error

## [QA] Minimum Assertions

Happy path:
- valid upload yields `status: ok`
- sample fallback yields `status: ok`
- `hardware_results` contains exactly 3 entries
- `winner_summary`, `confidence`, and `assumptions` are present

Failure path:
- invalid file yields structured `INVALID_UPLOAD`
- unsupported model yields structured `UNSUPPORTED_MODEL`
- parser failure yields structured `PARSE_FAILED`
- estimation failure yields structured `ESTIMATION_FAILED`

Consistency:
- all cards and charts use the same payload instance
- confidence and assumptions render above the fold on the report page
