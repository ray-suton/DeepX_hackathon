# Paladin MVP Plan

## Problem

Emerging AI chip vendors lose deals because prospective customers cannot quickly test how their own inference workloads would perform on new hardware. Existing benchmarks are generic, hardware access is slow, and vendor-specific profiling tools do not help before evaluation hardware is in hand.

## Product

Paladin is a pre-sales chip evaluation portal for accelerator vendors. A prospect uploads an ONNX model, selects runtime parameters like batch size and precision, and receives an analytical performance estimate comparing the vendor chip against baseline GPU and CPU hardware.

## Target User

- Primary buyer: AI chip vendors and accelerator manufacturers
- Primary user: solutions engineers, field engineers, and technical sales teams
- Secondary user: prospective customers evaluating whether to begin a hardware trial

## MVP Scope

### Inputs

- ONNX model upload
- Batch size
- Optional precision selection
- Optional fallback sample model selection

### Core Components

1. Model parser
   - Extract layer types
   - Extract tensor shapes
   - Estimate FLOPs
   - Estimate parameter and activation memory

2. Hardware profile layer
   - DeepX profile
   - GPU baseline profile
   - CPU baseline profile
   - Each profile includes compute throughput, memory bandwidth, datatype support, and estimated power behavior

3. Analytical estimator
   - Estimate latency from compute and memory cost
   - Estimate throughput from latency and batch size
   - Estimate power from hardware profile heuristics
   - Estimate performance per watt

4. Dashboard
   - Summary cards for each hardware target
   - Latency breakdown chart
   - Throughput comparison chart
   - Perf-per-watt comparison chart
   - Assumptions and confidence panel

## Demo Flow

1. User lands on Paladin
2. User uploads an ONNX model or selects a sample model
3. User sets batch size and optional precision
4. Paladin parses the model and runs the analytical estimator
5. User sees a comparative report for DeepX, GPU, and CPU

## Success Criteria

- A judge can understand the product in under 20 seconds
- A user can get from upload to report in under 30 seconds
- The report clearly explains that results are analytical estimates, not measured benchmark runs
- The product makes the manufacturer-facing buyer obvious

## Out of Scope

- PyTorch or TensorFlow direct upload
- Training workloads
- Quantization simulation
- TCO or procurement workflow integration
- Full benchmark-grade calibration
- Multi-vendor marketplace
- Cloud versus edge scenario planner

## Risks

- Trust risk if the simulator presents estimates as exact measurements
- Credibility risk if the assumptions are hidden
- Scope risk if the product drifts toward a general hardware selection tool

## Mitigations

- Add an assumptions and confidence panel above the fold
- Show the exact inputs used to generate estimates
- Keep the story centered on chip vendors reducing evaluation friction

## Open Questions

- Which sample model is best for the demo if file upload fails?
- Which hardware baselines should be used for the comparison?
- How detailed should the layer breakdown be for a same-day demo?
