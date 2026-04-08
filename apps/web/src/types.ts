export type InputMode = 'upload' | 'sample';
export type Precision = 'fp32' | 'fp16' | 'int8';
export type ViewState = 'empty' | 'loading' | 'success' | 'error';

export type WorkloadSpec = {
  model_id: string;
  input_mode: InputMode;
  batch_size: number;
  precision: Precision;
  input_shape: number[] | null;
  layer_counts: {
    conv: number;
    matmul: number;
    pool: number;
    activation: number;
    other: number;
  };
  flops_total: number;
  parameter_bytes: number;
  activation_bytes: number;
  unsupported_layers: string[];
  parser_warnings: string[];
};

export type HardwareResult = {
  hardware_id: string;
  hardware_label: string;
  latency_ms: number;
  throughput_inf_per_sec: number;
  power_watts: number;
  perf_per_watt: number;
  breakdown: {
    compute_ms: number;
    memory_ms: number;
    overhead_ms: number;
  };
};

export type ReportPayload = {
  report_id: string;
  generated_at: string;
  request: {
    input_mode: InputMode;
    model_name: string | null;
    sample_model_id: string | null;
    batch_size: number;
    precision: Precision;
  };
  workload_spec: WorkloadSpec;
  hardware_results: HardwareResult[];
  winner_summary: {
    winner_hardware_id: string;
    winner_dimension: string;
    headline: string;
    secondary_note: string;
  };
  confidence: {
    label: 'high' | 'medium' | 'low';
    score: number;
    reasons: string[];
  };
  assumptions: string[];
  status: 'ok';
};

export type ErrorPayload = {
  status: 'error';
  error: {
    code: 'INVALID_UPLOAD' | 'INVALID_INPUT' | 'PARSE_FAILED' | 'UNSUPPORTED_MODEL' | 'ESTIMATION_FAILED';
    message: string;
    user_action: string;
    details?: Record<string, unknown>;
  };
};
