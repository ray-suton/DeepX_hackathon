import { useEffect, useState, useTransition } from 'react';
import type { ChangeEvent } from 'react';
import { createReport, createUploadedReport } from './api';
import { mockReport, sampleModelOptions } from './data/mockReport';
import type { Precision, ReportPayload, ViewState } from './types';

type FormState = {
  inputMode: 'upload' | 'sample';
  sampleModelId: string;
  batchSize: string;
  precision: Precision;
  fileName: string;
  file: File | null;
};

const emptyFormState: FormState = {
  inputMode: 'sample',
  sampleModelId: sampleModelOptions[0].id,
  batchSize: '8',
  precision: 'fp16',
  fileName: '',
  file: null,
};

function App() {
  const [state, setState] = useState<ViewState>('empty');
  const [form, setForm] = useState<FormState>(emptyFormState);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<ReportPayload>(mockReport);
  const [isPending, startTransition] = useTransition();

  const updateForm = (next: Partial<FormState>) => {
    setForm((current) => ({ ...current, ...next }));
    setState('empty');
    setError(null);
  };

  const selectedSample =
    sampleModelOptions.find((option) => option.id === form.sampleModelId) ?? sampleModelOptions[0];

  useEffect(() => {
    if (state !== 'loading') {
      return;
    }

    let cancelled = false;

    const run = async () => {
      if (form.inputMode === 'upload' && !form.file) {
        setError('Upload a file or switch to the sample model fallback.');
        setState('error');
        return;
      }

      const batchSize = Number(form.batchSize);
      if (!Number.isFinite(batchSize) || batchSize <= 0) {
        setError('Batch size must be a positive number.');
        setState('error');
        return;
      }

      try {
        const nextReport =
          form.inputMode === 'upload' && form.file
            ? await createUploadedReport(form.file, batchSize, form.precision)
            : await createReport({
                input_mode: 'sample',
                model_name: null,
                sample_model_id: form.sampleModelId,
                batch_size: batchSize,
                precision: form.precision,
              });

        if (cancelled) {
          return;
        }
        setReport(nextReport);
        setError(null);
        setState('success');
      } catch (requestError) {
        if (cancelled) {
          return;
        }
        setReport(mockReport);
        setError(
          requestError instanceof Error
            ? `${requestError.message} Falling back to demo data.`
            : 'Could not reach the API. Falling back to demo data.',
        );
        setState('success');
      }
    };

    void run();

    return () => {
      cancelled = true;
    };
  }, [form.batchSize, form.file, form.fileName, form.inputMode, form.precision, form.sampleModelId, state]);

  const onGenerate = () => {
    setError(null);
    startTransition(() => {
      setState('loading');
    });
  };

  const onUseSample = () => {
    updateForm({
      inputMode: 'sample',
      sampleModelId: sampleModelOptions[0].id,
      fileName: '',
      file: null,
    });
  };

  const onFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const nextFile = event.target.files?.[0];
    updateForm({
      inputMode: 'upload',
      fileName: nextFile?.name ?? '',
      file: nextFile ?? null,
    });
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-mark">
          <span className="brand-dot" />
          Paladin
        </div>
        <nav className="nav-stack" aria-label="Primary">
          <button className="nav-item active" type="button">
            Simulation
          </button>
          <button className="nav-item" type="button">
            Reports
          </button>
          <button className="nav-item" type="button">
            Hardware profiles
          </button>
        </nav>
        <div className="sidebar-card">
          <div className="eyebrow">Trust contract</div>
          <p>Analytical estimate only. No benchmark theater.</p>
        </div>
      </aside>

      <main className="main-panel">
        <header className="hero">
          <div>
            <p className="eyebrow">AI chip vendor evaluation</p>
            <h1>Try before you buy, with one workload-specific estimate.</h1>
            <p className="lede">
              Upload a model, set runtime parameters, and compare DeepX against GPU and CPU
              baselines before any board is shipped.
            </p>
          </div>
          <div className="status-card">
            <span className="status-label">Confidence visible</span>
            <strong>{report.confidence.label.toUpperCase()}</strong>
            <span>{report.confidence.reasons[0]}</span>
          </div>
        </header>

        <section className="grid-layout">
          <section className="panel setup-panel">
            <div className="panel-heading">
              <h2>Setup</h2>
              <p>One request, one ephemeral report.</p>
            </div>

            <label className="field">
              <span>Input mode</span>
              <div className="segmented">
                <button
                  type="button"
                  className={form.inputMode === 'sample' ? 'segment active' : 'segment'}
                  onClick={onUseSample}
                >
                  Sample model
                </button>
                <button
                  type="button"
                  className={form.inputMode === 'upload' ? 'segment active' : 'segment'}
                  onClick={() => updateForm({ inputMode: 'upload' })}
                >
                  Upload ONNX
                </button>
              </div>
            </label>

            <label className="field">
              <span>Sample model</span>
              <select
                value={form.sampleModelId}
                onChange={(event) => updateForm({ sampleModelId: event.target.value })}
              >
                {sampleModelOptions.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.name}
                  </option>
                ))}
              </select>
              <small>{selectedSample.note}</small>
            </label>

            <label className="field">
              <span>Model file</span>
              <input type="file" accept=".onnx" onChange={onFileChange} />
              <small>{form.fileName || 'No file selected.'}</small>
            </label>

            <div className="field-row">
              <label className="field">
                <span>Batch size</span>
                <input
                  type="number"
                  min="1"
                  step="1"
                  value={form.batchSize}
                  onChange={(event) => updateForm({ batchSize: event.target.value })}
                />
              </label>

              <label className="field">
                <span>Precision</span>
                <select
                  value={form.precision}
                  onChange={(event) => updateForm({ precision: event.target.value as Precision })}
                >
                  <option value="fp32">FP32</option>
                  <option value="fp16">FP16</option>
                  <option value="int8">INT8</option>
                </select>
              </label>
            </div>

            <button className="primary-button" type="button" onClick={onGenerate} disabled={isPending}>
              {state === 'loading' ? 'Generating report...' : 'Generate estimate'}
            </button>

            <div className="mini-status">
              <span>Reports are ephemeral.</span>
              <span>Confidence and assumptions stay above the fold.</span>
            </div>
          </section>

          <section className="panel report-panel">
            <div className="panel-heading">
              <h2>Report</h2>
              <p>The same payload drives cards, charts, and trust UI.</p>
            </div>

            {state === 'empty' && (
              <div className="state-card empty-state">
                <strong>Ready when you are.</strong>
                <p>Select a sample model or upload an ONNX file, then generate a comparison.</p>
              </div>
            )}

            {state === 'loading' && (
              <div className="state-card loading-state" aria-live="polite">
                <strong>Estimating workload performance...</strong>
                <p>Parsing the workload spec and comparing DeepX, GPU, and CPU.</p>
              </div>
            )}

            {state === 'error' && (
              <div className="state-card error-state" role="alert">
                <strong>Could not generate the report.</strong>
                <p>{error}</p>
              </div>
            )}

            {state === 'success' && <ReportView report={report} error={error} />}
          </section>
        </section>
      </main>
    </div>
  );
}

function ReportView({ report, error }: { report: ReportPayload; error: string | null }) {
  const best = report.hardware_results[0];
  const maxThroughput = Math.max(...report.hardware_results.map((item) => item.throughput_inf_per_sec));

  return (
    <div className="report-stack">
      {error && (
        <div className="state-card error-state report-warning" role="status">
          <strong>Live API unavailable.</strong>
          <p>{error}</p>
        </div>
      )}
      <section className="headline-card">
        <div>
          <p className="eyebrow">Winner summary</p>
          <h3>{report.winner_summary.headline}</h3>
          <p>{report.winner_summary.secondary_note}</p>
        </div>
        <div className="winner-chip">
          <span>Best</span>
          <strong>{best.hardware_label}</strong>
          <small>{report.winner_summary.winner_dimension}</small>
        </div>
      </section>

      <section className="metrics-grid">
        {report.hardware_results.map((result) => (
          <article key={result.hardware_id} className="metric-card">
            <span className="metric-label">{result.hardware_label}</span>
            <strong>{result.latency_ms.toFixed(1)} ms</strong>
            <small>{result.throughput_inf_per_sec.toFixed(1)} inf/s</small>
            <div className="progress-track" aria-hidden="true">
              <span
                className="progress-fill"
                style={{
                  width: `${Math.max((result.throughput_inf_per_sec / maxThroughput) * 100, 12)}%`,
                }}
              />
            </div>
          </article>
        ))}
      </section>

      <section className="detail-grid">
        <article className="panel">
          <div className="panel-heading compact">
            <h4>Assumptions</h4>
            <p>Analytical estimate, not measured benchmark.</p>
          </div>
          <ul className="bullet-list">
            {report.assumptions.map((assumption) => (
              <li key={assumption}>{assumption}</li>
            ))}
          </ul>
        </article>

        <article className="panel">
          <div className="panel-heading compact">
            <h4>Confidence</h4>
            <p>
              {report.confidence.label.toUpperCase()} confidence, score {report.confidence.score}
            </p>
          </div>
          <div className="confidence-bar" aria-hidden="true">
            <span style={{ width: `${report.confidence.score * 100}%` }} />
          </div>
          <ul className="bullet-list">
            {report.confidence.reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </article>
      </section>

      <section className="chart-grid">
        <ChartCard
          title="Latency breakdown"
          items={report.hardware_results.map((result) => ({
            label: result.hardware_label,
            value: result.latency_ms,
          }))}
          unit="ms"
          accent="orange"
        />
        <ChartCard
          title="Throughput comparison"
          items={report.hardware_results.map((result) => ({
            label: result.hardware_label,
            value: result.throughput_inf_per_sec,
          }))}
          unit="inf/s"
          accent="green"
        />
        <ChartCard
          title="Performance per watt"
          items={report.hardware_results.map((result) => ({
            label: result.hardware_label,
            value: result.perf_per_watt,
          }))}
          unit="perf/W"
          accent="muted"
        />
      </section>
    </div>
  );
}

function ChartCard({
  title,
  items,
  unit,
  accent,
}: {
  title: string;
  items: Array<{ label: string; value: number }>;
  unit: string;
  accent: 'orange' | 'green' | 'muted';
}) {
  const max = Math.max(...items.map((item) => item.value));

  return (
    <article className="panel chart-card">
      <div className="panel-heading compact">
        <h4>{title}</h4>
        <p>{unit}</p>
      </div>
      <div className="chart-bars">
        {items.map((item) => (
          <div key={item.label} className="chart-row">
            <span>{item.label}</span>
            <div className="chart-track" aria-hidden="true">
              <div
                className={`chart-fill ${accent}`}
                style={{ width: `${Math.max((item.value / max) * 100, 16)}%` }}
              />
            </div>
            <strong>
              {item.value}
              {unit === 'ms' ? '' : ` ${unit}`}
            </strong>
          </div>
        ))}
      </div>
    </article>
  );
}

export default App;
