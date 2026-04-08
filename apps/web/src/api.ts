import type { ErrorPayload, Precision, ReportPayload } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

export type ReportRequest =
  | {
      input_mode: 'sample';
      model_name: null;
      sample_model_id: string;
      batch_size: number;
      precision: Precision;
    }
  | {
      input_mode: 'upload';
      model_name: string;
      sample_model_id: null;
      batch_size: number;
      precision: Precision;
    };

export async function createReport(request: ReportRequest): Promise<ReportPayload> {
  const response = await fetch(`${API_BASE_URL}/api/v1/report`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  const payload = (await response.json()) as ReportPayload | ErrorPayload;
  if (!response.ok || payload.status === 'error') {
    const message =
      payload.status === 'error'
        ? `${payload.error.message} ${payload.error.user_action}`.trim()
        : 'The report request failed.';
    throw new Error(message);
  }

  return payload;
}

export async function createUploadedReport(
  file: File,
  batchSize: number,
  precision: Precision,
): Promise<ReportPayload> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('batch_size', String(batchSize));
  formData.append('precision', precision);

  const response = await fetch(`${API_BASE_URL}/api/v1/report/upload`, {
    method: 'POST',
    body: formData,
  });

  const payload = (await response.json()) as ReportPayload | ErrorPayload;
  if (!response.ok || payload.status === 'error') {
    const message =
      payload.status === 'error'
        ? `${payload.error.message} ${payload.error.user_action}`.trim()
        : 'The upload report request failed.';
    throw new Error(message);
  }

  return payload;
}
