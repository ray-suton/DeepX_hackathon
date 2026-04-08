from __future__ import annotations

from math import inf
from typing import Any

from .contracts import (
    Confidence,
    HardwareProfile,
    HardwareResult,
    NormalizedWorkloadSpec,
    Precision,
    RequestInput,
    ReportPayload,
    WinnerSummary,
    utc_now_iso,
)
from .errors import (
    EstimationFailedError,
    InvalidInputError,
    InvalidUploadError,
    ParseFailedError,
    UnsupportedModelError,
)
from .parser import parse_uploaded_model
from .sample_models import get_sample_model


PRECISION_VALUES: set[str] = {"fp32", "fp16", "int8"}
PRECISION_WEIGHT: dict[str, float] = {"fp32": 1.0, "fp16": 0.72, "int8": 0.55}

HARDWARE_PROFILES: tuple[HardwareProfile, ...] = (
    HardwareProfile(
        hardware_id="deepx",
        hardware_label="DeepX",
        compute_tflops=180.0,
        memory_bandwidth_gbps=900.0,
        power_watts=42.0,
        fixed_overhead_ms=0.8,
        precision_power_scale={"fp32": 1.0, "fp16": 0.9, "int8": 0.82},
    ),
    HardwareProfile(
        hardware_id="gpu_baseline",
        hardware_label="GPU Baseline",
        compute_tflops=120.0,
        memory_bandwidth_gbps=600.0,
        power_watts=95.0,
        fixed_overhead_ms=1.4,
        precision_power_scale={"fp32": 1.0, "fp16": 0.88, "int8": 0.78},
    ),
    HardwareProfile(
        hardware_id="cpu_baseline",
        hardware_label="CPU Baseline",
        compute_tflops=25.0,
        memory_bandwidth_gbps=120.0,
        power_watts=65.0,
        fixed_overhead_ms=3.0,
        precision_power_scale={"fp32": 1.0, "fp16": 0.96, "int8": 0.9},
    ),
)


def normalize_request(payload: dict[str, Any]) -> RequestInput:
    input_mode = payload.get("input_mode")
    model_name = payload.get("model_name")
    sample_model_id = payload.get("sample_model_id")
    batch_size = payload.get("batch_size")
    precision = payload.get("precision") or "fp16"

    if input_mode not in {"upload", "sample"}:
        raise InvalidInputError(
            "input_mode must be 'upload' or 'sample'.",
            "Choose either an uploaded ONNX model or a sample model.",
            {"input_mode": input_mode},
        )

    if bool(model_name) == bool(sample_model_id):
        raise InvalidInputError(
            "Exactly one of model_name or sample_model_id must be provided.",
            "Provide only one model source for v1.",
            {"model_name": model_name, "sample_model_id": sample_model_id},
        )

    if not isinstance(batch_size, int) or batch_size <= 0:
        raise InvalidInputError(
            "batch_size must be a positive integer.",
            "Enter a batch size greater than zero.",
            {"batch_size": batch_size},
        )

    if precision not in PRECISION_VALUES:
        raise InvalidInputError(
            "precision must be one of fp32, fp16, or int8.",
            "Pick a supported precision value.",
            {"precision": precision},
        )

    if input_mode == "upload" and not isinstance(model_name, str):
        raise InvalidUploadError(
            "Uploaded model input must include a model_name identifier.",
            "Try the sample model or provide a file-backed model identifier.",
        )

    if input_mode == "sample" and not isinstance(sample_model_id, str):
        raise InvalidInputError(
            "sample_mode requests must include sample_model_id.",
            "Choose one of the built-in sample models.",
        )

    return RequestInput(
        input_mode=input_mode,  # type: ignore[arg-type]
        model_name=model_name if isinstance(model_name, str) else None,
        sample_model_id=sample_model_id if isinstance(sample_model_id, str) else None,
        batch_size=batch_size,
        precision=precision,  # type: ignore[arg-type]
    )


def resolve_workload_spec(request: RequestInput) -> NormalizedWorkloadSpec:
    identifier = request.sample_model_id if request.input_mode == "sample" else request.model_name
    if not identifier:
        raise ParseFailedError(
            "The request did not include a recognizable model identifier.",
            "Try the sample model or upload a known demo model.",
        )

    blueprint = get_sample_model(identifier)
    if blueprint is None:
        if request.input_mode == "upload":
            raise ParseFailedError(
                "The MVP parser cannot read this uploaded ONNX model yet.",
                "Try the sample model or upload one of the known demo models.",
                {"model_name": identifier},
            )
        raise UnsupportedModelError(
            "This model is not part of the MVP sample set yet.",
            "Try a sample model supported by the demo.",
            {"model_name": identifier},
        )

    return NormalizedWorkloadSpec(
        model_id=blueprint.model_id,
        input_mode=request.input_mode,
        batch_size=request.batch_size,
        precision=request.precision,
        input_shape=blueprint.input_shape,
        layer_counts=blueprint.layer_counts,
        flops_total=blueprint.flops_total,
        parameter_bytes=blueprint.parameter_bytes,
        activation_bytes=blueprint.activation_bytes,
        unsupported_layers=list(blueprint.unsupported_layers),
        parser_warnings=list(blueprint.parser_warnings),
    )


def resolve_uploaded_workload_spec(request: RequestInput, file_bytes: bytes) -> NormalizedWorkloadSpec:
    return parse_uploaded_model(request, file_bytes)


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def estimate_hardware_results(spec: NormalizedWorkloadSpec) -> list[HardwareResult]:
    if spec.batch_size <= 0:
        raise EstimationFailedError(
            "Batch size must be positive for estimation.",
            "Go back and choose a batch size greater than zero.",
        )

    precision_weight = PRECISION_WEIGHT[spec.precision]
    total_bytes = spec.parameter_bytes + (spec.activation_bytes * spec.batch_size)
    results: list[HardwareResult] = []

    for profile in HARDWARE_PROFILES:
        compute_ms = (spec.flops_total * precision_weight) / (profile.compute_tflops * 1_000_000_000_000) * 1000
        memory_ms = (total_bytes / (profile.memory_bandwidth_gbps * 1_000_000_000)) * 1000
        overhead_ms = profile.fixed_overhead_ms
        latency_ms = compute_ms + memory_ms + overhead_ms
        throughput_inf_per_sec = spec.batch_size / (latency_ms / 1000)
        power_watts = profile.power_watts * profile.precision_power_scale[spec.precision]
        perf_per_watt = throughput_inf_per_sec / power_watts if power_watts else inf
        results.append(
            HardwareResult(
                hardware_id=profile.hardware_id,
                hardware_label=profile.hardware_label,
                latency_ms=round(latency_ms, 2),
                throughput_inf_per_sec=round(throughput_inf_per_sec, 2),
                power_watts=round(power_watts, 2),
                perf_per_watt=round(perf_per_watt, 2),
                breakdown={
                    "compute_ms": round(compute_ms, 2),
                    "memory_ms": round(memory_ms, 2),
                    "overhead_ms": round(overhead_ms, 2),
                },
            )
        )

    return results


def derive_winner_summary(results: list[HardwareResult], batch_size: int) -> WinnerSummary:
    if not results:
        raise EstimationFailedError(
            "No hardware results were produced.",
            "Try the sample model again.",
        )

    ordered_by_latency = sorted(results, key=lambda item: item.latency_ms)
    ordered_by_efficiency = sorted(results, key=lambda item: item.perf_per_watt, reverse=True)
    best_latency = ordered_by_latency[0]
    best_efficiency = ordered_by_efficiency[0]

    if len(ordered_by_latency) > 1:
        gap = abs(ordered_by_latency[1].latency_ms - best_latency.latency_ms)
        relative_gap = gap / ordered_by_latency[1].latency_ms if ordered_by_latency[1].latency_ms else 0.0
        if relative_gap <= 0.05:
            return WinnerSummary(
                winner_hardware_id=best_latency.hardware_id,
                winner_dimension="balanced",
                headline="No single hardware is a clear latency winner for this workload.",
                secondary_note=f"{best_efficiency.hardware_label} is the best efficiency pick under the current assumptions.",
            )

    headline = f"{best_latency.hardware_label} is the fastest option for this workload at batch size {batch_size}."
    secondary_note = f"{best_efficiency.hardware_label} also leads performance per watt under the current assumptions."
    if best_latency.hardware_id == best_efficiency.hardware_id:
        secondary_note = f"{best_latency.hardware_label} also leads performance per watt under the current assumptions."

    return WinnerSummary(
        winner_hardware_id=best_latency.hardware_id,
        winner_dimension="latency",
        headline=headline,
        secondary_note=secondary_note,
    )


def derive_confidence(spec: NormalizedWorkloadSpec, results: list[HardwareResult]) -> Confidence:
    score = 0.86
    reasons: list[str] = ["Model graph parsed successfully."]

    if spec.input_shape is None:
        score -= 0.12
        reasons.append("Input shape could not be fully derived.")
    if spec.unsupported_layers:
        score -= min(0.15, 0.05 * len(spec.unsupported_layers))
        reasons.append("Unsupported layers were detected.")
    if spec.parser_warnings:
        score -= min(0.18, 0.06 * len(spec.parser_warnings))
        reasons.append("Parser warnings reduced confidence.")

    if not results:
        score -= 0.25
        reasons.append("No hardware estimates were produced.")
    else:
        reasons.append("Power estimates are heuristic rather than measured.")

    score = _clamp(score, 0.35, 0.95)
    if score >= 0.8:
        label = "high"
    elif score >= 0.6:
        label = "medium"
    else:
        label = "low"

    return Confidence(label=label, score=round(score, 2), reasons=reasons)


def derive_report(request: RequestInput, spec: NormalizedWorkloadSpec, results: list[HardwareResult]) -> ReportPayload:
    winner_summary = derive_winner_summary(results, request.batch_size)
    confidence = derive_confidence(spec, results)
    assumptions = [
        "Results are analytical estimates, not measured benchmark runs.",
        "Hardware profiles are predefined for DeepX, GPU baseline, and CPU baseline.",
        "Latency is estimated from compute, memory, and fixed overhead terms.",
    ]
    return ReportPayload(
        report_id=f"ephemeral-{spec.model_id.replace('.onnx', '')}-{request.precision}-b{request.batch_size}",
        generated_at=utc_now_iso(),
        request=request,
        workload_spec=spec,
        hardware_results=results,
        winner_summary=winner_summary,
        confidence=confidence,
        assumptions=assumptions,
    )


def build_report(payload: dict[str, Any]) -> ReportPayload:
    request = normalize_request(payload)
    spec = resolve_workload_spec(request)
    results = estimate_hardware_results(spec)
    return derive_report(request, spec, results)


def build_report_from_upload(filename: str, file_bytes: bytes, batch_size: int, precision: Precision = "fp16") -> ReportPayload:
    request = normalize_request(
        {
            "input_mode": "upload",
            "model_name": filename,
            "sample_model_id": None,
            "batch_size": batch_size,
            "precision": precision,
        }
    )
    spec = resolve_uploaded_workload_spec(request, file_bytes)
    results = estimate_hardware_results(spec)
    return derive_report(request, spec, results)


def build_sample_payload(sample_model_id: str, batch_size: int, precision: Precision = "fp16") -> dict[str, Any]:
    return {
        "input_mode": "sample",
        "model_name": None,
        "sample_model_id": sample_model_id,
        "batch_size": batch_size,
        "precision": precision,
    }


def build_demo_report(sample_model_id: str = "resnet50-demo", batch_size: int = 8, precision: Precision = "fp16") -> dict[str, Any]:
    report = build_report(build_sample_payload(sample_model_id, batch_size, precision))
    return report.to_dict()
