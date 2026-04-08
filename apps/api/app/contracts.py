from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal


InputMode = Literal["upload", "sample"]
Precision = Literal["fp32", "fp16", "int8"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


@dataclass(slots=True)
class RequestInput:
    input_mode: InputMode
    model_name: str | None
    sample_model_id: str | None
    batch_size: int
    precision: Precision = "fp16"


@dataclass(slots=True)
class NormalizedWorkloadSpec:
    model_id: str
    input_mode: InputMode
    batch_size: int
    precision: Precision
    input_shape: list[int] | None
    layer_counts: dict[str, int]
    flops_total: int
    parameter_bytes: int
    activation_bytes: int
    unsupported_layers: list[str] = field(default_factory=list)
    parser_warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class HardwareProfile:
    hardware_id: str
    hardware_label: str
    compute_tflops: float
    memory_bandwidth_gbps: float
    power_watts: float
    fixed_overhead_ms: float
    precision_power_scale: dict[str, float]


@dataclass(slots=True)
class HardwareResult:
    hardware_id: str
    hardware_label: str
    latency_ms: float
    throughput_inf_per_sec: float
    power_watts: float
    perf_per_watt: float
    breakdown: dict[str, float]


@dataclass(slots=True)
class WinnerSummary:
    winner_hardware_id: str
    winner_dimension: str
    headline: str
    secondary_note: str


@dataclass(slots=True)
class Confidence:
    label: str
    score: float
    reasons: list[str]


@dataclass(slots=True)
class ReportPayload:
    report_id: str
    generated_at: str
    request: RequestInput
    workload_spec: NormalizedWorkloadSpec
    hardware_results: list[HardwareResult]
    winner_summary: WinnerSummary
    confidence: Confidence
    assumptions: list[str]
    status: str = "ok"

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "request": asdict(self.request),
            "workload_spec": asdict(self.workload_spec),
            "hardware_results": [asdict(result) for result in self.hardware_results],
            "winner_summary": asdict(self.winner_summary),
            "confidence": asdict(self.confidence),
            "assumptions": list(self.assumptions),
            "status": self.status,
        }

