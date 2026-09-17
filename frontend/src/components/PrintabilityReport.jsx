/**
 * PrintabilityReport.jsx
 * Floating HUD card showing 3D printing readiness metrics.
 * Props:
 *  - report   {Object}    - printability assessment data from backend
 *  - onClose  {Function}  - close handler
 */
export default function PrintabilityReport({ report, onClose }) {
  if (!report) return null;

  const Check = ({ ok }) => (
    <span style={{ color: ok ? 'var(--success)' : 'var(--danger)', fontSize: 'var(--text-base)' }}>
      {ok ? '✓' : '✗'}
    </span>
  );

  return (
    <div className="hud-panel" style={{ bottom: 20, right: 20, width: 300 }}>
      <div className="hud-title">
        <span>🖨️ Printability Report</span>
        <span
          className={`badge ${report.ready_to_print ? 'badge-success' : 'badge-danger'}`}
          style={{ marginLeft: 'auto' }}
        >
          {report.ready_to_print ? 'READY' : 'NOT READY'}
        </span>
        <button
          className="ghost icon-btn sm"
          style={{ width: 'auto', marginLeft: 4 }}
          onClick={onClose}
          title="Close"
        >
          ✕
        </button>
      </div>

      <div className="print-grid">
        <div className="print-item">
          <span className="print-label">Watertight</span>
          <div className="flex-row" style={{ gap: 4 }}>
            <Check ok={report.is_watertight} />
            <span className="print-value" style={{ color: report.is_watertight ? 'var(--success)' : 'var(--danger)', fontSize: 'var(--text-sm)' }}>
              {report.is_watertight ? 'YES' : 'NO'}
            </span>
          </div>
        </div>

        <div className="print-item">
          <span className="print-label">Normals</span>
          <div className="flex-row" style={{ gap: 4 }}>
            <Check ok={report.winding_consistent} />
            <span className="print-value" style={{ color: report.winding_consistent ? 'var(--success)' : 'var(--danger)', fontSize: 'var(--text-sm)' }}>
              {report.winding_consistent ? 'CONSISTENT' : 'FLIPPED'}
            </span>
          </div>
        </div>

        <div className="print-item">
          <span className="print-label">Surface Area</span>
          <div className="flex-row" style={{ gap: 3, alignItems: 'baseline' }}>
            <span className="print-value">{Math.round(report.area_mm2).toLocaleString()}</span>
            <span className="metric-unit">mm²</span>
          </div>
        </div>

        <div className="print-item">
          <span className="print-label">Volume</span>
          <div className="flex-row" style={{ gap: 3, alignItems: 'baseline' }}>
            <span className="print-value">{Math.round(report.volume_mm3 / 1000)}</span>
            <span className="metric-unit">cc</span>
          </div>
        </div>

        <div className="print-item">
          <span className="print-label">Euler Number</span>
          <span className="print-value" style={{ fontSize: 'var(--text-sm)' }}>{report.euler_number}</span>
        </div>

        <div className="print-item">
          <span className="print-label">Surface</span>
          <span className="print-value" style={{ color: 'var(--success)', fontSize: 'var(--text-sm)' }}>
            {report.is_empty ? 'EMPTY' : 'VALID'}
          </span>
        </div>
      </div>

      {report.issues?.length > 0 && (
        <>
          <div className="divider" />
          <div>
            <p style={{ fontSize: 'var(--text-xs)', fontWeight: 700, color: 'var(--danger)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              ⚠ Calibration Issues
            </p>
            <ul style={{ paddingLeft: 14, display: 'flex', flexDirection: 'column', gap: 3 }}>
              {report.issues.map((iss, i) => (
                <li key={i} style={{ fontSize: 'var(--text-xs)', color: 'var(--warning)' }}>{iss}</li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
}
