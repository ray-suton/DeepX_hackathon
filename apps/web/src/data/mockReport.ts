import type { ReportPayload } from '../types';

export const mockReport: ReportPayload = {
  report_id: 'ephemeral-resnet50-fp16-b8',
  generated_at: '2026-04-08T06:45:00Z',
  request: {
    input_mode: 'upload',
    model_name: 'resnet50.onnx',
    sample_model_id: null,
    batch_size: 8,
    precision: 'fp16',
  },
  workload_spec: {
    model_id: 'resnet50.onnx',
    input_mode: 'upload',
    batch_size: 8,
    precision: 'fp16',
    input_shape: [1, 3, 224, 224],
    layer_counts: {
      conv: 53,
      matmul: 1,
      pool: 1,
      activation: 49,
      other: 6,
    },
    flops_total: 4089184256,
    parameter_bytes: 102760448,
    activation_bytes: 18874368,
    unsupported_layers: [],
    parser_warnings: [],
  },
  hardware_results: [
    {
      hardware_id: 'deepx',
      hardware_label: 'DeepX',
      latency_ms: 11.2,
      throughput_inf_per_sec: 89.3,
      power_watts: 42,
      perf_per_watt: 2.13,
      breakdown: {
        compute_ms: 7.8,
        memory_ms: 2.6,
        overhead_ms: 0.8,
      },
    },
    {
      hardware_id: 'gpu_baseline',
      hardware_label: 'GPU Baseline',
      latency_ms: 14.7,
      throughput_inf_per_sec: 68,
      power_watts: 95,
      perf_per_watt: 0.72,
      breakdown: {
        compute_ms: 8.2,
        memory_ms: 5.1,
        overhead_ms: 1.4,
      },
    },
    {
      hardware_id: 'cpu_baseline',
      hardware_label: 'CPU Baseline',
      latency_ms: 47.5,
      throughput_inf_per_sec: 21,
      power_watts: 65,
      perf_per_watt: 0.32,
      breakdown: {
        compute_ms: 32,
        memory_ms: 12.5,
        overhead_ms: 3,
      },
    },
  ],
  winner_summary: {
    winner_hardware_id: 'deepx',
    winner_dimension: 'latency',
    headline: 'DeepX is the fastest option for this workload at batch size 8.',
    secondary_note: 'DeepX also leads performance per watt under the current assumptions.',
  },
  confidence: {
    label: 'medium',
    score: 0.68,
    reasons: [
      'Model graph parsed successfully.',
      'No unsupported layers were detected.',
      'Power estimates are heuristic rather than measured.',
    ],
  },
  assumptions: [
    'Results are analytical estimates, not measured benchmark runs.',
    'Hardware profiles are predefined for DeepX, GPU baseline, and CPU baseline.',
    'Latency is estimated from compute, memory, and fixed overhead terms.',
  ],
  status: 'ok',
};

export const sampleModelOptions = [
  { id: 'resnet50-demo', name: 'ResNet50 demo', note: 'Safe fallback for live demo' },
  { id: 'mobilenetv2-demo', name: 'MobileNetV2 demo', note: 'Lighter edge-style workload' },
] as const;
