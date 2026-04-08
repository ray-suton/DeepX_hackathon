# TODOs

## P1 Demo Decisions

- Choose the default fallback sample model for the live demo so upload failure does not kill the flow.
- Pick the exact GPU and CPU baseline hardware profiles that DeepX will be compared against.
- Write the assumptions and confidence copy that explains the outputs are analytical estimates, not measured benchmark runs.
- Define the winner-summary logic so the report can say when DeepX is best for latency, throughput, or efficiency.

## P1 Build Tasks

- Implement ONNX parsing for layer categories, tensor shapes, FLOPs, parameter size, and activation memory.
- Implement three hardcoded hardware profiles: DeepX, one GPU baseline, and one CPU baseline.
- Implement the analytical estimator using compute cost, memory cost, and fixed overhead heuristics.
- Build the upload and configuration flow with ONNX upload, batch size, precision, and sample model fallback.
- Build the report page with summary cards, latency chart, throughput chart, perf-per-watt chart, and assumptions panel above the fold.

## P2 Polish

- Add a simple confidence label such as high, medium, or low based on how complete the model metadata is.
- Add a lightweight layer-type breakdown so the estimate feels workload-specific.
- Prepare one canned sample model path for demo backup in case live parsing fails.

## Not In Scope Today

- PyTorch or TensorFlow upload
- Training workload support
- Quantization simulation
- TCO modeling
- Multi-vendor marketplace features
