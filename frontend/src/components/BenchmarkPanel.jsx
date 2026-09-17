/**
 * BenchmarkPanel.jsx
 * Visual AI Benchmark Leaderboard and telemetry comparator.
 * Connects to /api/v1/inference/benchmark/leaderboard and /inference/benchmark/compare
 */
import { useState, useEffect, useCallback } from 'react';

export default function BenchmarkPanel({ apiUrl, token, onSelectModel }) {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchLeaderboard = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiUrl}/inference/benchmark/leaderboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      const list = json.data?.leaderboard || json.data || (Array.isArray(json) ? json : []);
      // Normalize fields if needed
      const normalized = list.map(item => ({
        model_name: item.model_name,
        total_runs: item.run_count ?? item.total_runs ?? 0,
        avg_inference_time_sec: item.avg_inference_sec ?? item.avg_inference_time_sec ?? 0,
        avg_vram_mb: item.avg_vram_mb ?? 0
      }));
      setLeaderboard(normalized);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [apiUrl, token]);

  useEffect(() => {
    fetchLeaderboard();
  }, [fetchLeaderboard]);

  const maxTime = Math.max(...leaderboard.map(d => d.avg_inference_time_sec || 0), 1);
  const maxVram = Math.max(...leaderboard.map(d => d.avg_vram_mb || 0), 1);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: 'var(--text-xs)', color: 'var(--muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          AI Plugin Telemetry ({leaderboard.length} Models)
        </span>
        <button
          className="ghost sm"
          style={{ padding: '3px 8px', fontSize: '11px' }}
          onClick={fetchLeaderboard}
          disabled={loading}
        >
          {loading ? '↻ Loading...' : '↻ Refresh'}
        </button>
      </div>

      {error && (
        <div style={{ padding: '8px 10px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239,68,68,0.25)', borderRadius: 'var(--radius-sm)', color: '#fca5a5', fontSize: 'var(--text-xs)' }}>
          ⚠️ {error}
        </div>
      )}

      {leaderboard.length === 0 && !loading && !error && (
        <div style={{ textAlign: 'center', padding: '16px 8px', color: 'var(--muted)', fontSize: 'var(--text-xs)' }}>
          No inference runs recorded yet. Execute segmentation to view performance telemetry.
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {leaderboard.map((item, idx) => {
          const timePercent = Math.min(100, Math.round(((item.avg_inference_time_sec || 0) / maxTime) * 100));
          const vramPercent = Math.min(100, Math.round(((item.avg_vram_mb || 0) / maxVram) * 100));

          return (
            <div
              key={item.model_name || idx}
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-md)',
                padding: '10px 12px',
                display: 'flex',
                flexDirection: 'column',
                gap: 8,
                transition: 'var(--transition-fast)',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--primary-glow)'; e.currentTarget.style.background = 'rgba(99,102,241,0.06)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.background = 'rgba(255, 255, 255, 0.03)'; }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span style={{ fontWeight: 700, fontSize: 'var(--text-xs)', color: idx === 0 ? 'var(--accent)' : 'var(--text)' }}>
                    #{idx + 1} {item.model_name}
                  </span>
                  <span className="badge-cyan" style={{ fontSize: '10px', padding: '1px 5px' }}>
                    {item.total_runs} runs
                  </span>
                </div>
                {onSelectModel && (
                  <button
                    className="ghost sm"
                    style={{ fontSize: '10px', padding: '2px 6px' }}
                    onClick={() => onSelectModel(item.model_name)}
                  >
                    Select
                  </button>
                )}
              </div>

              {/* Metric 1: Avg Latency */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--muted)', marginBottom: 3 }}>
                  <span>Latency</span>
                  <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--primary-light)', fontWeight: 600 }}>
                    {item.avg_inference_time_sec != null ? `${item.avg_inference_time_sec.toFixed(2)}s` : 'N/A'}
                  </span>
                </div>
                <div style={{ height: 4, background: 'rgba(255,255,255,0.08)', borderRadius: 2, overflow: 'hidden' }}>
                  <div style={{ width: `${Math.max(5, timePercent)}%`, height: '100%', background: 'linear-gradient(90deg, #6366f1, #a855f7)', borderRadius: 2 }} />
                </div>
              </div>

              {/* Metric 2: Avg VRAM */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--muted)', marginBottom: 3 }}>
                  <span>VRAM</span>
                  <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent)', fontWeight: 600 }}>
                    {item.avg_vram_mb != null ? `${item.avg_vram_mb.toFixed(1)} MB` : 'N/A'}
                  </span>
                </div>
                <div style={{ height: 4, background: 'rgba(255,255,255,0.08)', borderRadius: 2, overflow: 'hidden' }}>
                  <div style={{ width: `${Math.max(5, vramPercent)}%`, height: '100%', background: 'linear-gradient(90deg, #06b6d4, #10b981)', borderRadius: 2 }} />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
