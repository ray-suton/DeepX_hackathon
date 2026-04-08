# Paladin MVP Plan

## One-Line Positioning

Paladin is a try-before-you-buy workload simulator for AI chip vendors.

## Problem

Emerging AI chip vendors lose deals because prospective customers cannot quickly test how their own inference workloads would perform on unfamiliar hardware. Generic benchmarks do not answer the buyer's actual question, and shipping evaluation boards takes time, setup effort, and trust that many early prospects do not have.

## Product

Paladin is a pre-sales chip evaluation portal for accelerator vendors. A prospect uploads an ONNX model, selects a small number of runtime parameters, and receives an analytical estimate comparing the vendor chip against baseline GPU and CPU hardware for that specific workload.

This is not a benchmark runner. It is a workload-specific estimation tool designed to reduce evaluation friction before hardware access.

## Customer and User

- Primary buyer: AI chip vendors and accelerator manufacturers
- Primary user: solutions engineers, field engineers, and technical sales teams
- Secondary user: prospective customers deciding whether to begin a hardware trial

## Demo Goal

Show, in less than 30 seconds, that a chip vendor can give a prospect a useful first-pass answer to: "How would my model likely run on your chip?"

## MVP Scope

### Inputs

- ONNX model upload
- Batch size
- Optional precision selection
- Optional fallback sample model

### Core Components

1. Model parser
   - Extract layer categories
   - Extract tensor shapes
   - Estimate FLOPs
   - Estimate parameter and activation memory

2. Hardware profile layer
   - DeepX profile
   - GPU baseline profile
   - CPU baseline profile
   - Each profile includes compute throughput, memory bandwidth, datatype support, and a simple power heuristic

3. Analytical estimator
   - Estimate latency from compute cost, memory cost, and fixed overhead
   - Estimate throughput from latency and batch size
   - Estimate power from hardware profile heuristics
   - Estimate performance per watt

4. Comparative dashboard
   - Winner summary
   - Summary cards for each hardware target
   - Latency breakdown chart
   - Throughput comparison chart
   - Perf-per-watt comparison chart
   - Assumptions and confidence panel above the fold

## Demo Flow

1. User lands on Paladin
2. User uploads an ONNX model or selects a sample model
3. User sets batch size and optional precision
4. Paladin parses the model and runs the analytical estimator
5. User sees a comparative report for DeepX, GPU, and CPU
6. User understands both the likely result and the assumptions behind it

## Trust Contract

Paladin must state clearly that the output is an analytical estimate, not a measured benchmark result.

The report should show:
- the model input used
- the batch size and precision used
- the hardware profiles used
- the main assumptions behind the estimate
- a simple confidence label such as high, medium, or low

If Paladin looks like fake benchmark theater, the idea weakens. If it looks transparent and honest, the idea gets stronger.

## Success Criteria

- A judge understands the product in under 20 seconds
- A user can get from upload to report in under 30 seconds
- The manufacturer-facing buyer is obvious
- The report feels useful without pretending to be exact
- The assumptions and confidence panel is visible without scrolling

## Out of Scope

- PyTorch or TensorFlow direct upload
- Training workloads
- Quantization simulation
- TCO or procurement workflow integration
- Full benchmark-grade calibration
- Multi-vendor marketplace
- Cloud versus edge scenario planner
- General-purpose hardware selection for all ML teams

## Risks

- Trust risk if the simulator presents estimates as exact measurements
- Credibility risk if the assumptions are hidden or vague
- Scope risk if the product drifts toward a generic infrastructure chooser

## Mitigations

- Add an assumptions and confidence panel above the fold
- Show the exact inputs used to generate estimates
- Keep the story centered on chip vendors reducing evaluation friction
- Use a fallback sample model so the demo cannot fail on upload

## Open Questions

- Which sample model is the safest fallback for the live demo?
- Which specific GPU and CPU baselines should be used in the comparison?
- How detailed should the layer breakdown be without slowing the demo down?

## Dream State Delta

Today: a demo-grade analytical estimator for one vendor-facing use case.

Later: a trusted vendor evaluation portal with calibration, benchmark imports, sales enablement, and usage analytics.
