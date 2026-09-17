/**
 * InferenceProgressBar.jsx
 * Animated progress bar for background inference tasks.
 * Props:
 *  - taskInfo  {Object|null}  - { status, progress, model_name, error }
 *  - elapsed   {number}       - elapsed seconds (computed in parent)
 */
export default function InferenceProgressBar({ taskInfo, elapsed }) {
  if (!taskInfo) return null;

  const { status, progress, model_name, error } = taskInfo;

  const statusColor = {
    PENDING:  'var(--muted)',
    RUNNING:  'var(--accent)',
    SUCCESS:  'var(--success)',
    FAILED:   'var(--danger)',
  }[status] || 'var(--muted)';

  const barClass = status === 'SUCCESS' ? 'progress-bar success'
                 : status === 'FAILED'  ? 'progress-bar danger'
                 : 'progress-bar animated';

  return (
    <div style={{
      background: 'var(--bg-2)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--r-md)',
      padding: 'var(--sp-3)',
      display: 'flex',
      flexDirection: 'column',
      gap: 'var(--sp-2)',
    }}>
      {/* Header row */}
      <div className="flex-row-spread">
        <div className="flex-row" style={{ gap: 'var(--sp-2)' }}>
          {status === 'RUNNING' && <span className="spinner" />}
          <span style={{ fontSize: 'var(--text-sm)', fontWeight: 600, color: statusColor }}>
            {status === 'PENDING'  && '⏳ Queued'}
            {status === 'RUNNING'  && `Running — ${model_name}`}
            {status === 'SUCCESS'  && '✓ Complete'}
            {status === 'FAILED'   && '✗ Failed'}
          </span>
        </div>
        <div className="flex-row" style={{ gap: 'var(--sp-2)' }}>
          {elapsed != null && status === 'RUNNING' && (
            <span style={{ fontSize: 'var(--text-xs)', color: 'var(--muted)', fontFamily: 'JetBrains Mono, monospace' }}>
              {elapsed}s
            </span>
          )}
          <span style={{ fontSize: 'var(--text-sm)', fontWeight: 700, color: statusColor }}>
            {progress}%
          </span>
        </div>
      </div>

      {/* Progress Track */}
      <div className="progress-track">
        <div className={barClass} style={{ width: `${progress}%` }} />
      </div>

      {/* Error message */}
      {error && (
        <p style={{ fontSize: 'var(--text-xs)', color: 'var(--danger)', marginTop: 2 }}>
          {error}
        </p>
      )}
    </div>
  );
}
