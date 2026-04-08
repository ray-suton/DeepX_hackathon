from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SampleModelBlueprint:
    model_id: str
    aliases: tuple[str, ...]
    input_shape: list[int] | None
    layer_counts: dict[str, int]
    flops_total: int
    parameter_bytes: int
    activation_bytes: int
    unsupported_layers: list[str]
    parser_warnings: list[str]


SAMPLE_MODELS: dict[str, SampleModelBlueprint] = {
    "resnet50-demo": SampleModelBlueprint(
        model_id="resnet50.onnx",
        aliases=("resnet50-demo", "resnet50.onnx"),
        input_shape=[1, 3, 224, 224],
        layer_counts={"conv": 53, "matmul": 1, "pool": 1, "activation": 49, "other": 6},
        flops_total=4_089_184_256,
        parameter_bytes=102_760_448,
        activation_bytes=18_874_368,
        unsupported_layers=[],
        parser_warnings=[],
    ),
    "mobilenetv2-demo": SampleModelBlueprint(
        model_id="mobilenetv2.onnx",
        aliases=("mobilenetv2-demo", "mobilenetv2.onnx"),
        input_shape=[1, 3, 224, 224],
        layer_counts={"conv": 35, "matmul": 1, "pool": 1, "activation": 28, "other": 4},
        flops_total=300_000_000,
        parameter_bytes=14_000_000,
        activation_bytes=8_000_000,
        unsupported_layers=[],
        parser_warnings=[],
    ),
}

_ALIASES: dict[str, SampleModelBlueprint] = {}
for blueprint in SAMPLE_MODELS.values():
    for alias in blueprint.aliases:
        _ALIASES[alias] = blueprint


def get_sample_model(identifier: str) -> SampleModelBlueprint | None:
    return _ALIASES.get(identifier)

