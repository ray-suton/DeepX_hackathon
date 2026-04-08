from __future__ import annotations

from collections import Counter
from math import prod

import onnx

from .contracts import NormalizedWorkloadSpec, RequestInput
from .errors import ParseFailedError, UnsupportedModelError


SUPPORTED_OPS = {
    "Conv",
    "Gemm",
    "MatMul",
    "Relu",
    "Sigmoid",
    "Tanh",
    "Add",
    "Mul",
    "BatchNormalization",
    "MaxPool",
    "AveragePool",
    "GlobalAveragePool",
    "Flatten",
    "Reshape",
    "Transpose",
    "Concat",
}

LAYER_BUCKETS = {
    "Conv": "conv",
    "Gemm": "matmul",
    "MatMul": "matmul",
    "MaxPool": "pool",
    "AveragePool": "pool",
    "GlobalAveragePool": "pool",
    "Relu": "activation",
    "Sigmoid": "activation",
    "Tanh": "activation",
}

DTYPE_BYTES = {
    onnx.TensorProto.FLOAT: 4,
    onnx.TensorProto.FLOAT16: 2,
    onnx.TensorProto.DOUBLE: 8,
    onnx.TensorProto.INT8: 1,
    onnx.TensorProto.UINT8: 1,
    onnx.TensorProto.INT16: 2,
    onnx.TensorProto.INT32: 4,
    onnx.TensorProto.INT64: 8,
}


def _dim_to_int(dim: onnx.TensorShapeProto.Dimension) -> int | None:
    if dim.HasField("dim_value"):
        return int(dim.dim_value)
    return None


def _shape_product(shape: list[int | None]) -> int | None:
    if any(value is None or value <= 0 for value in shape):
        return None
    return prod(int(value) for value in shape if value is not None)


def _extract_input_shape(model: onnx.ModelProto) -> list[int] | None:
    for tensor in model.graph.input:
        shape = tensor.type.tensor_type.shape
        dims = [_dim_to_int(dim) for dim in shape.dim]
        if dims:
            normalized = [value if value is not None else 1 for value in dims]
            return normalized
    return None


def _parameter_bytes(model: onnx.ModelProto) -> int:
    total = 0
    for initializer in model.graph.initializer:
        item_size = DTYPE_BYTES.get(initializer.data_type, 4)
        size = prod(initializer.dims) if initializer.dims else 0
        total += size * item_size
    return int(total)


def _estimate_flops(model: onnx.ModelProto) -> int:
    total = 0
    for initializer in model.graph.initializer:
        size = prod(initializer.dims) if initializer.dims else 0
        total += size * 2
    total += len(model.graph.node) * 100_000
    return int(max(total, 1_000_000))


def parse_uploaded_model(request: RequestInput, file_bytes: bytes) -> NormalizedWorkloadSpec:
    try:
        model = onnx.load_model_from_string(file_bytes)
    except Exception as exc:  # pragma: no cover - onnx error types vary
        raise ParseFailedError(
            "The uploaded file could not be parsed as an ONNX model.",
            "Upload a valid ONNX model or use a sample model.",
            {"exception": exc.__class__.__name__},
        ) from exc

    input_shape = _extract_input_shape(model)
    parameter_bytes = _parameter_bytes(model)
    flops_total = _estimate_flops(model)
    layer_counter: Counter[str] = Counter()
    unsupported_layers: list[str] = []

    for node in model.graph.node:
        bucket = LAYER_BUCKETS.get(node.op_type, "other")
        layer_counter[bucket] += 1
        if node.op_type not in SUPPORTED_OPS:
            unsupported_layers.append(node.op_type)

    parser_warnings: list[str] = []
    if input_shape is None:
        parser_warnings.append("Input shape could not be fully derived from the uploaded graph.")

    activation_elements = _shape_product([*input_shape] if input_shape else [request.batch_size, 3, 224, 224])
    activation_bytes = int((activation_elements or (request.batch_size * 3 * 224 * 224)) * 4)

    unique_unsupported = sorted(set(unsupported_layers))
    node_count = max(len(model.graph.node), 1)
    if len(unique_unsupported) / node_count > 0.35:
        raise UnsupportedModelError(
            "This uploaded model uses too many operators outside the MVP parser support set.",
            "Try a simpler ONNX export or use a sample model for the demo.",
            {"unsupported_layers": unique_unsupported},
        )

    if unique_unsupported:
        parser_warnings.append("Some operators are outside the MVP parser support set.")

    return NormalizedWorkloadSpec(
        model_id=request.model_name or "uploaded-model.onnx",
        input_mode=request.input_mode,
        batch_size=request.batch_size,
        precision=request.precision,
        input_shape=input_shape,
        layer_counts={
            "conv": layer_counter.get("conv", 0),
            "matmul": layer_counter.get("matmul", 0),
            "pool": layer_counter.get("pool", 0),
            "activation": layer_counter.get("activation", 0),
            "other": layer_counter.get("other", 0),
        },
        flops_total=flops_total,
        parameter_bytes=parameter_bytes,
        activation_bytes=activation_bytes,
        unsupported_layers=unique_unsupported,
        parser_warnings=parser_warnings,
    )
