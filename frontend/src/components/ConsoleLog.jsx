/**
 * ConsoleLog.jsx
 * Styled terminal-like log panel with color-coded log levels.
 * Props:
 *  - logs  {Array<{ts, type, msg}>}
 *  - logRef {React.Ref}
 */
export default function ConsoleLog({ logs, logRef }) {
  const typeClass = {
    info:    'log-info',
    success: 'log-success',
    error:   'log-error',
    warn:    'log-warn',
    warning: 'log-warn',
  };

  return (
    <div>
      <div className="flex-row-spread" style={{ marginBottom: 'var(--sp-1)' }}>
        <p style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          System Console
        </p>
        <span style={{ fontSize: 'var(--text-xs)', color: 'var(--muted)' }}>
          {logs.length} entries
        </span>
      </div>
      <div ref={logRef} className="console-log">
        {logs.length === 0 ? (
          <span className="log-info">{'>'} Waiting for connection…</span>
        ) : (
          logs.map((log, i) => (
            <span key={i} className={`log-line ${typeClass[log.type] || 'log-info'}`}>
              <span className="log-ts">[{log.ts}]</span>
              {log.msg}
            </span>
          ))
        )}
      </div>
    </div>
  );
}
