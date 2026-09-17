/**
 * ViewportHUD.jsx
 * Floating controls overlay for the 3D WebGL viewport.
 * Props:
 *  - wireframe      {bool}
 *  - setWireframe   {fn}
 *  - onClear        {fn}
 *  - onScreenshot   {fn}
 *  - selectedMesh   {Object|null}
 *  - selectedImplant{Object|null}
 *  - onDownloadMesh    {fn}
 *  - onDownloadImplant {fn}
 *  - cameraRef      {React.Ref}  - OrbitControls ref for camera presets
 */
import { useCallback } from 'react';
import * as THREE from 'three';

const CAMERA_PRESETS = [
  { label: 'Iso',   emoji: '◈', position: [150, 150, 150] },
  { label: 'Front', emoji: '▣', position: [0,   0,   300] },
  { label: 'Side',  emoji: '▤', position: [300, 0,   0]   },
  { label: 'Top',   emoji: '▥', position: [0,   300, 0]   },
];

export default function ViewportHUD({
  wireframe, setWireframe,
  onClear,
  selectedMesh, selectedImplant,
  onDownloadMesh, onDownloadImplant,
  cameraRef,
}) {
  const setCamera = useCallback((pos) => {
    if (!cameraRef?.current) return;
    const controls = cameraRef.current;
    const camera = controls.object;
    camera.position.set(...pos);
    camera.lookAt(new THREE.Vector3(0, 0, 0));
    controls.target.set(0, 0, 0);
    controls.update();
  }, [cameraRef]);

  const ext = (fp) => fp?.split('.').pop()?.toUpperCase() ?? 'STL';

  return (
    <div className="hud-panel" style={{ top: 20, left: 20, width: 220 }}>
      <div className="hud-title">🎮 Viewport Controls</div>

      {/* Camera Presets */}
      <div>
        <p style={{ fontSize: 'var(--text-xs)', color: 'var(--muted)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>Camera</p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 4 }}>
          {CAMERA_PRESETS.map(({ label, emoji, position }) => (
            <button
              key={label}
              className="ghost sm"
              style={{ padding: '5px 8px', fontSize: 'var(--text-xs)' }}
              onClick={() => setCamera(position)}
            >
              {emoji} {label}
            </button>
          ))}
        </div>
      </div>

      <div className="divider" />

      {/* Scene Controls */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        <button
          className="ghost sm"
          onClick={() => setWireframe(!wireframe)}
          style={{ fontSize: 'var(--text-xs)' }}
        >
          {wireframe ? '◼ Solid View' : '⬡ Wireframe'}
        </button>
        <button
          className="ghost sm danger"
          onClick={onClear}
          style={{ fontSize: 'var(--text-xs)' }}
        >
          🗑 Clear Canvas
        </button>
      </div>

      {/* Downloads */}
      {(selectedMesh || selectedImplant) && (
        <>
          <div className="divider" />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {selectedMesh && (
              <button
                className="ghost sm"
                style={{ fontSize: 'var(--text-xs)' }}
                onClick={onDownloadMesh}
              >
                📥 Bone Mesh ({ext(selectedMesh.file_path)})
              </button>
            )}
            {selectedImplant && (
              <button
                className="purple sm"
                style={{ fontSize: 'var(--text-xs)' }}
                onClick={onDownloadImplant}
              >
                📥 Implant ({ext(selectedImplant.file_path)})
              </button>
            )}
          </div>
        </>
      )}

      {/* Stats HUD */}
      {(selectedMesh || selectedImplant) && (
        <>
          <div className="divider" />
          <div className="metric-grid">
            {selectedMesh && (
              <>
                <div className="metric-card">
                  <span className="metric-label">Facets</span>
                  <span className="metric-value" style={{ fontSize: 'var(--text-sm)' }}>
                    {(selectedMesh.triangle_count || 0).toLocaleString()}
                  </span>
                </div>
                <div className="metric-card">
                  <span className="metric-label">Volume</span>
                  <div className="flex-row" style={{ gap: 2, alignItems: 'baseline' }}>
                    <span className="metric-value" style={{ fontSize: 'var(--text-sm)' }}>
                      {Math.round((selectedMesh.volume_mm3 || 0) / 1000)}
                    </span>
                    <span className="metric-unit">cc</span>
                  </div>
                </div>
              </>
            )}
          </div>
        </>
      )}
    </div>
  );
}
