import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { STLLoader }  from 'three/examples/jsm/loaders/STLLoader.js';
import { OBJLoader }  from 'three/examples/jsm/loaders/OBJLoader.js';
import { PLYLoader }  from 'three/examples/jsm/loaders/PLYLoader.js';

import PipelineProgress    from './components/PipelineProgress.jsx';
import InferenceProgressBar from './components/InferenceProgressBar.jsx';
import PrintabilityReport  from './components/PrintabilityReport.jsx';
import ViewportHUD         from './components/ViewportHUD.jsx';
import ConsoleLog          from './components/ConsoleLog.jsx';
import BenchmarkPanel      from './components/BenchmarkPanel.jsx';

/* ─────────────────────────────────────────────────────────────
   Custom hook: useLogger
   Returns { logs, log, clearLogs, logRef }
   ───────────────────────────────────────────────────────────── */
function useLogger() {
  const [logs, setLogs] = useState([]);
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [logs]);

  const log = useCallback((msg, type = 'info') => {
    const ts = new Date().toLocaleTimeString('en-US', { hour12: false });
    setLogs(prev => [...prev.slice(-199), { ts, msg, type }]);
  }, []);

  const clearLogs = useCallback(() => setLogs([]), []);
  return { logs, log, clearLogs, logRef };
}

/* ─────────────────────────────────────────────────────────────
   Custom hook: useApi
   Central authenticated fetch helper
   ───────────────────────────────────────────────────────────── */
function useApi(apiUrl, token) {
  return useCallback(async (endpoint, method = 'GET', body = null, isMultipart = false) => {
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    let options = { method, headers };
    if (body) {
      if (isMultipart) { options.body = body; }
      else { headers['Content-Type'] = 'application/json'; options.body = JSON.stringify(body); }
    }

    let targetUrl = `${apiUrl}${endpoint}`;
    if (endpoint.startsWith('/auth/')) {
      targetUrl = `${apiUrl.replace(/\/v\d+$/, '')}${endpoint}`;
    }

    const response = await fetch(targetUrl, options);
    if (response.status === 204) return null;
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.message || response.statusText);
    return payload;
  }, [apiUrl, token]);
}

/* ─────────────────────────────────────────────────────────────
   Helper: Section Panel (collapsible accordion)
   ───────────────────────────────────────────────────────────── */
function SectionPanel({ id, openId, onToggle, icon, bgColor, label, badge, children }) {
  const isOpen = openId === id;
  return (
    <div className="section-panel">
      <div className="section-header" onClick={() => onToggle(id)}>
        <div className="section-header-title">
          <div className="section-header-icon" style={{ background: bgColor || 'var(--panel-light)', color: '#fff' }}>
            {icon}
          </div>
          {label}
          {badge != null && (
            <span className="badge badge-accent" style={{ marginLeft: 4, fontSize: 9 }}>{badge}</span>
          )}
        </div>
        <span className={`section-header-chevron ${isOpen ? 'open' : ''}`}>▼</span>
      </div>
      {isOpen && <div className="section-body">{children}</div>}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   Helper: Item card with actions
   ───────────────────────────────────────────────────────────── */
function ItemCard({ active, onClick, title, sub, badge, badgeClass, actions }) {
  return (
    <div className={`item-card ${active ? 'active' : ''}`} onClick={onClick}>
      <div className="item-card-header">
        <span className="item-card-title">{title}</span>
        <div className="flex-row" style={{ gap: 4 }}>
          {badge && <span className={`badge ${badgeClass || 'badge-muted'}`}>{badge}</span>}
          {actions && (
            <div className="item-card-actions" onClick={e => e.stopPropagation()}>
              {actions}
            </div>
          )}
        </div>
      </div>
      {sub && <div className="item-card-sub">{sub}</div>}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────
   Helper: Mesh scene object
   ───────────────────────────────────────────────────────────── */
function MeshObject({ geometry, color, specular, shininess, wireframe }) {
  if (!geometry) return null;
  return (
    <mesh geometry={geometry} castShadow receiveShadow>
      <meshPhongMaterial color={color} specular={specular} shininess={shininess} wireframe={wireframe} />
    </mesh>
  );
}

/* ═══════════════════════════════════════════════════════════════
   Main App Component
   ═══════════════════════════════════════════════════════════════ */
export default function App() {
  // ── Core state ──────────────────────────────────────────────
  const [apiUrl,     setApiUrl]     = useState('http://localhost:8000/api/v2');
  const [token,      setToken]      = useState(localStorage.getItem('token') || '');
  const [username,   setUsername]   = useState('admin');
  const [password,   setPassword]   = useState('admin');
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'));

  // ── Data lists ───────────────────────────────────────────────
  const [volumes,  setVolumes]  = useState([]);
  const [masks,    setMasks]    = useState([]);
  const [meshes,   setMeshes]   = useState([]);
  const [implants, setImplants] = useState([]);

  // ── AI Plugin registries ──────────────────────────────────────
  const [segModels,     setSegModels]     = useState([]);
  const [implantModels, setImplantModels] = useState([]);
  const [segModel,      setSegModel]      = useState('');
  const [implantModel,  setImplantModel]  = useState('mirror_implant');

  // ── Selection ────────────────────────────────────────────────
  const [selectedVolume,  setSelectedVolume]  = useState(null);
  const [selectedMask,    setSelectedMask]    = useState(null);
  const [selectedMesh,    setSelectedMesh]    = useState(null);
  const [selectedImplant, setSelectedImplant] = useState(null);

  // ── Form params ──────────────────────────────────────────────
  const [smoothIters,    setSmoothIters]    = useState(10);
  const [decimateRatio,  setDecimateRatio]  = useState(0.5);
  const [meshFormat,     setMeshFormat]     = useState('stl');
  const [implantFormat,  setImplantFormat]  = useState('stl');
  const [uploadFile,     setUploadFile]     = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  // ── UI state ─────────────────────────────────────────────────
  const [openSection,  setOpenSection]  = useState('auth');
  const [wireframe,    setWireframe]    = useState(false);
  const [printReport,  setPrintReport]  = useState(null);
  const [running,      setRunning]      = useState(null); // 'segment' | 'reconstruct' | 'implant'

  // ── Inference task tracking ───────────────────────────────────
  const [activeTask,  setActiveTask]  = useState(null);  // { task_id, status, progress, ... }
  const [taskElapsed, setTaskElapsed] = useState(0);
  const taskStartRef = useRef(null);

  // ── 3D geometry ───────────────────────────────────────────────
  const [boneGeometry,    setBoneGeometry]    = useState(null);
  const [implantGeometry, setImplantGeometry] = useState(null);
  const controlsRef = useRef(null);

  const { logs, log, logRef } = useLogger();
  const request = useApi(apiUrl, token);

  // ── Load on login ─────────────────────────────────────────────
  useEffect(() => {
    if (isLoggedIn) {
      fetchVolumes(); fetchMeshes(); fetchImplants();
      fetchSegModels(); fetchImplantModels();
    }
  }, [isLoggedIn]);

  // ── Task elapsed timer ────────────────────────────────────────
  useEffect(() => {
    if (!activeTask || activeTask.status !== 'RUNNING') return;
    const id = setInterval(() => {
      setTaskElapsed(Math.floor((Date.now() - taskStartRef.current) / 1000));
    }, 1000);
    return () => clearInterval(id);
  }, [activeTask]);

  /* ── Auth ─────────────────────────────────────────────────── */
  async function handleLogin(e) {
    e.preventDefault();
    try {
      log('Authenticating…', 'info');
      const res = await request('/auth/login', 'POST', { username, password });
      const accToken = res.data.access_token;
      setToken(accToken);
      localStorage.setItem('token', accToken);
      setIsLoggedIn(true);
      log('Authenticated successfully.', 'success');
      setOpenSection('ingestion');
    } catch (err) { log(`Login failed: ${err.message}`, 'error'); }
  }

  async function handleRegister(e) {
    e.preventDefault();
    try {
      log('Creating account…', 'info');
      await request('/auth/register', 'POST', {
        email: username.includes('@') ? username : `${username}@medai.local`,
        username, password, dob: null, gender: null,
        first_name: null, last_name: null, full_name: username,
        phone: null, address: null, identity_card: null,
        identity_card_date: null, identity_card_place: null,
      });
      log('Account created. You may now log in.', 'success');
    } catch (err) { log(`Registration failed: ${err.message}`, 'error'); }
  }

  function handleLogout() {
    setToken(''); localStorage.removeItem('token'); setIsLoggedIn(false);
    setVolumes([]); setMasks([]); setMeshes([]); setImplants([]);
    setSelectedVolume(null); setSelectedMask(null); setSelectedMesh(null); setSelectedImplant(null);
    setBoneGeometry(null); setImplantGeometry(null); setPrintReport(null);
    setActiveTask(null);
    log('Logged out.', 'info');
    setOpenSection('auth');
  }

  /* ── Data fetchers ───────────────────────────────────────────── */
  async function fetchVolumes() {
    try {
      const res = await request('/volumes/all');
      setVolumes(res.data || []);
    } catch (err) { log(`Volumes: ${err.message}`, 'error'); }
  }

  async function fetchMasks(volId) {
    try {
      const res = await request('/inference/masks/all');
      setMasks((res.data || []).filter(m => m.volume_id === volId));
    } catch (err) { log(`Masks: ${err.message}`, 'error'); }
  }

  async function fetchMeshes() {
    try { const res = await request('/meshes/all'); setMeshes(res.data || []); }
    catch (err) { log(`Meshes: ${err.message}`, 'error'); }
  }

  async function fetchImplants() {
    try { const res = await request('/implants/all'); setImplants(res.data || []); }
    catch (err) { log(`Implants: ${err.message}`, 'error'); }
  }

  async function fetchSegModels() {
    try {
      const res = await request('/inference/models');
      const models = res.data || [];
      setSegModels(models);
      if (models.length > 0) setSegModel(prev => prev || models[0].name);
    } catch (err) { log(`Models: ${err.message}`, 'error'); }
  }

  async function fetchImplantModels() {
    try {
      const res = await request('/implants/models');
      const models = res.data || [];
      setImplantModels(models);
      if (models.length > 0) setImplantModel(prev => prev || models[0].name);
    } catch (err) { log(`Implant models: ${err.message}`, 'error'); }
  }

  /* ── Upload ──────────────────────────────────────────────────── */
  async function handleUpload(e) {
    e.preventDefault();
    if (!uploadFile) return;
    try {
      log(`Uploading ${uploadFile.name}…`, 'info');
      setUploadProgress(25);
      const formData = new FormData();
      formData.append('file', uploadFile);
      setUploadProgress(55);
      const res = await request('/volumes/upload', 'POST', formData, true);
      setUploadProgress(100);
      log(`Volume ingested. ID: ${res.data.id}`, 'success');
      setTimeout(() => setUploadProgress(0), 1500);
      setUploadFile(null);
      fetchVolumes();
      setOpenSection('segmentation');
    } catch (err) {
      log(`Upload failed: ${err.message}`, 'error');
      setUploadProgress(0);
    }
  }

  /* ── AI Segmentation (with exponential back-off polling) ──────── */
  async function handleSegmentation() {
    if (!selectedVolume || !segModel) return;
    try {
      setRunning('segment');
      log(`Queuing AI segmentation (${segModel}) on Volume ${selectedVolume.id}…`, 'info');
      const res = await request(`/inference/segment/${selectedVolume.id}`, 'POST', { model_name: segModel });
      const taskId = res.data.task_id;
      log(`Task queued. ID: ${taskId}`, 'info');
      taskStartRef.current = Date.now();
      setTaskElapsed(0);

      // Exponential back-off polling: 1s, 1.5s, 2s, 2.5s… cap at 4s
      let delay = 1000;
      let attempts = 0;
      const poll = async () => {
        if (attempts > 240) {
          log('Polling timed out.', 'error');
          setRunning(null); setActiveTask(null); return;
        }
        attempts++;
        try {
          const statusRes = await request(`/inference/tasks/${taskId}`);
          const taskInfo = statusRes.data;
          setActiveTask({ ...taskInfo, task_id: taskId });

          if (taskInfo.status === 'SUCCESS') {
            log(`Inference complete. Mask ID: ${taskInfo.result_id}`, 'success');
            setRunning(null);
            setActiveTask(prev => ({ ...prev, status: 'SUCCESS', progress: 100 }));
            setTimeout(() => setActiveTask(null), 3000);
            fetchMasks(selectedVolume.id);
            setOpenSection('geometry');
          } else if (taskInfo.status === 'FAILED') {
            log(`Inference failed: ${taskInfo.error}`, 'error');
            setRunning(null);
            setTimeout(() => setActiveTask(null), 5000);
          } else {
            delay = Math.min(delay * 1.2, 4000);
            setTimeout(poll, delay);
          }
        } catch (err) {
          log(`Polling error: ${err.message}`, 'warn');
          setTimeout(poll, 2000);
        }
      };
      setTimeout(poll, 1000);
    } catch (err) {
      log(`Segmentation failed: ${err.message}`, 'error');
      setRunning(null);
    }
  }

  /* ── 3D Reconstruction ───────────────────────────────────────── */
  async function handleReconstruction() {
    if (!selectedMask) return;
    try {
      setRunning('reconstruct');
      log(`Reconstructing Mask ${selectedMask.id} → ${meshFormat.toUpperCase()}…`, 'info');
      const res = await request(`/meshes/reconstruct/${selectedMask.id}`, 'POST', {
        smooth_iterations: parseInt(smoothIters),
        decimate_ratio: parseFloat(decimateRatio),
        export_format: meshFormat,
      });
      log(`Mesh generated. ID: ${res.data.id}`, 'success');
      fetchMeshes();
      setSelectedMesh(res.data);
      await loadGeometry(res.data.id, meshFormat, 'bone');
      await checkPrintability(res.data.id);
      setRunning(null);
      setOpenSection('implant');
    } catch (err) {
      log(`Reconstruction failed: ${err.message}`, 'error');
      setRunning(null);
    }
  }

  /* ── Implant Generation ──────────────────────────────────────── */
  async function handleImplant() {
    if (!selectedMask) return;
    try {
      setRunning('implant');
      log(`Generating PSI implant for Mask ${selectedMask.id}…`, 'info');
      const res = await request(`/implants/recommend/${selectedMask.id}`, 'POST', {
        model_name: implantModel,
        smooth_iterations: parseInt(smoothIters),
        decimate_ratio: parseFloat(decimateRatio),
        export_format: implantFormat,
      });
      log(`Implant generated. ID: ${res.data.id}`, 'success');
      fetchImplants();
      setSelectedImplant(res.data);
      await loadGeometry(res.data.id, implantFormat, 'implant');
      setRunning(null);
    } catch (err) {
      log(`Implant generation failed: ${err.message}`, 'error');
      setRunning(null);
    }
  }

  /* ── Printability check ──────────────────────────────────────── */
  async function checkPrintability(meshId) {
    try {
      const res = await request(`/meshes/${meshId}/printability`);
      setPrintReport(res.data);
    } catch (err) { log(`Printability check: ${err.message}`, 'warn'); }
  }

  /* ── 3D Geometry Loader ───────────────────────────────────────── */
  async function loadGeometry(id, format, target) {
    try {
      log(`Loading ${target} geometry (ID: ${id})…`, 'info');
      const endpoint = target === 'bone' ? `/meshes/${id}/download` : `/implants/${id}/download`;
      const response = await fetch(`${apiUrl}${endpoint}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Mesh download failed');
      const buffer = await response.arrayBuffer();

      let geom = null;
      const fmt = format.toLowerCase();
      if (fmt === 'stl')      geom = new STLLoader().parse(buffer);
      else if (fmt === 'ply') geom = new PLYLoader().parse(buffer);
      else if (fmt === 'obj') {
        const text = new TextDecoder().decode(buffer);
        new OBJLoader().parse(text).traverse(child => { if (child.isMesh) geom = child.geometry; });
      }

      if (geom) {
        geom.computeVertexNormals();
        geom.center();
        if (target === 'bone') setBoneGeometry(geom);
        else setImplantGeometry(geom);
        log(`${target} geometry loaded.`, 'success');
      }
    } catch (err) { log(`Geometry error: ${err.message}`, 'error'); }
  }

  /* ── File download ────────────────────────────────────────────── */
  async function downloadFile(id, format, target) {
    try {
      const endpoint = target === 'bone' ? `/meshes/${id}/download` : `/implants/${id}/download`;
      const response = await fetch(`${apiUrl}${endpoint}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = `${target}_${id}.${format}`; a.click();
      URL.revokeObjectURL(url);
      log(`Downloaded ${target} (${format}).`, 'success');
    } catch (err) { log(`Download failed: ${err.message}`, 'error'); }
  }

  const toggleSection = (sec) => setOpenSection(openSection === sec ? '' : sec);

  /* ═══════════════════════════════════════════════════════════════
     RENDER
     ═══════════════════════════════════════════════════════════════ */
  return (
    <div className="app-container">

      {/* ══ SIDEBAR ══════════════════════════════════════════════ */}
      <aside className="sidebar">

        {/* Logo / Header */}
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">🔬</div>
            <div>
              <div className="sidebar-title">MedAI-OS</div>
            </div>
          </div>
          <div className="sidebar-subtitle">Medical AI Laboratory Operating System</div>
        </div>

        {/* Pipeline Progress Stepper */}
        <PipelineProgress
          volumes={volumes}
          masks={masks}
          meshes={meshes}
          implants={implants}
          running={running}
        />

        {/* Active Inference Progress */}
        {activeTask && (
          <InferenceProgressBar taskInfo={activeTask} elapsed={taskElapsed} />
        )}

        {/* ── Section: API Config ─────────────────────────────── */}
        <SectionPanel
          id="api" openId={openSection} onToggle={toggleSection}
          icon="⚙" bgColor="rgba(79,98,128,0.4)" label="API Server"
        >
          <div className="field-group">
            <label>FastAPI URL</label>
            <input type="text" value={apiUrl} onChange={e => setApiUrl(e.target.value)} placeholder="http://localhost:8000/api/v2" />
          </div>
        </SectionPanel>

        {/* ── Section: Auth ───────────────────────────────────── */}
        <SectionPanel
          id="auth" openId={openSection} onToggle={toggleSection}
          icon="🔑" bgColor="rgba(59,130,246,0.4)" label="Authentication"
        >
          {isLoggedIn ? (
            <div>
              <div className="flex-row-spread" style={{ marginBottom: 'var(--sp-2)' }}>
                <span style={{ fontSize: 'var(--text-sm)', color: 'var(--muted)' }}>Signed in as</span>
                <span className="badge badge-success">{username}</span>
              </div>
              <button className="ghost" onClick={handleLogout}>Sign Out</button>
            </div>
          ) : (
            <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-2)' }}>
              <div className="field-group">
                <label>Username</label>
                <input id="username-input" type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="admin" autoComplete="username" />
              </div>
              <div className="field-group">
                <label>Password</label>
                <input id="password-input" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" autoComplete="current-password" />
              </div>
              <div className="flex-row" style={{ gap: 'var(--sp-2)' }}>
                <button id="login-btn" type="submit">Sign In</button>
                <button id="register-btn" className="ghost" type="button" onClick={handleRegister}>Register</button>
              </div>
            </form>
          )}
        </SectionPanel>

        {isLoggedIn && (
          <>
            {/* ── Section: Volumetric Ingestion ─────────────────── */}
            <SectionPanel
              id="ingestion" openId={openSection} onToggle={toggleSection}
              icon="📡" bgColor="rgba(6,182,212,0.4)" label="Volumetric Ingestion"
              badge={volumes.length || null}
            >
              <form onSubmit={handleUpload} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-2)' }}>
                <div className="field-group">
                  <label>DICOM ZIP / NIfTI File</label>
                  <input id="upload-input" type="file" accept=".zip,.nii,.nii.gz" onChange={e => setUploadFile(e.target.files[0])} />
                </div>
                {uploadFile && (
                  <p style={{ fontSize: 'var(--text-xs)', color: 'var(--muted)' }}>
                    📄 {uploadFile.name} ({(uploadFile.size / 1024 / 1024).toFixed(1)} MB)
                  </p>
                )}
                <button id="upload-btn" type="submit" disabled={!uploadFile}>
                  Upload Volume
                </button>
              </form>

              {uploadProgress > 0 && (
                <div>
                  <div className="progress-track" style={{ marginBottom: 4 }}>
                    <div className={`progress-bar ${uploadProgress < 100 ? 'animated' : 'success'}`}
                         style={{ width: `${uploadProgress}%` }} />
                  </div>
                  <p style={{ fontSize: 'var(--text-xs)', color: 'var(--muted)', textAlign: 'center' }}>
                    {uploadProgress}%
                  </p>
                </div>
              )}

              {/* Volume list */}
              {volumes.length > 0 && (
                <div>
                  <div className="divider" />
                  <label>Available Volumes</label>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 160, overflowY: 'auto' }}>
                    {volumes.map(v => (
                      <ItemCard
                        key={v.id}
                        active={selectedVolume?.id === v.id}
                        onClick={() => { setSelectedVolume(v); fetchMasks(v.id); log(`Selected Volume ${v.id}.`); setOpenSection('segmentation'); }}
                        title={`Vol-${v.id}  ${v.patient_id ? `· ${v.patient_id}` : '(Anon)'}`}
                        sub={`Spacing: ${v.spacing.map(n => n.toFixed(1)).join(' × ')} mm`}
                        badge={v.modality || 'CT'}
                        badgeClass="badge-accent"
                        actions={[
                          <button key="d" className="ghost icon-btn sm" title="Delete"
                            onClick={async () => { await request(`/volumes/${v.id}`, 'DELETE'); fetchVolumes(); log(`Deleted Volume ${v.id}.`, 'warn'); }}>
                            🗑
                          </button>
                        ]}
                      />
                    ))}
                  </div>
                </div>
              )}
            </SectionPanel>

            {/* ── Section: AI Segmentation ──────────────────────── */}
            <SectionPanel
              id="segmentation" openId={openSection} onToggle={toggleSection}
              icon="🧠" bgColor="rgba(168,85,247,0.4)" label="AI Segmentation"
              badge={masks.length || null}
            >
              <div className="field-group">
                <label>Model (auto-discovered)</label>
                <select id="model-select" value={segModel} onChange={e => setSegModel(e.target.value)}>
                  {segModels.length === 0 && <option value="">No models discovered</option>}
                  {segModels.map(m => (
                    <option key={m.name} value={m.name}>{m.name} v{m.version}</option>
                  ))}
                </select>
              </div>

              {selectedVolume ? (
                <div className="flex-row" style={{ gap: 4 }}>
                  <span className="badge badge-accent" style={{ flexShrink: 0 }}>Vol-{selectedVolume.id}</span>
                  <button
                    id="segment-btn"
                    disabled={!segModel || running === 'segment'}
                    onClick={handleSegmentation}
                    style={{ flex: 1 }}
                  >
                    {running === 'segment' ? <><span className="spinner" /> Running…</> : '▶ Run Segmentation'}
                  </button>
                </div>
              ) : (
                <p className="list-empty">Select a volume above first</p>
              )}

              {masks.length > 0 && (
                <div>
                  <div className="divider" />
                  <label>Segmentation Masks</label>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 140, overflowY: 'auto' }}>
                    {masks.map(m => (
                      <ItemCard
                        key={m.id}
                        active={selectedMask?.id === m.id}
                        onClick={() => { setSelectedMask(m); log(`Selected Mask ${m.id}.`); setOpenSection('geometry'); }}
                        title={`Mask-${m.id}`}
                        sub={`${m.inference_time_sec?.toFixed(2) ?? '—'}s · ${m.vram_consumed_mb?.toFixed(0) ?? '—'} MB VRAM`}
                        badge={m.model_name}
                        badgeClass="badge-purple"
                      />
                    ))}
                  </div>
                </div>
              )}
            </SectionPanel>

            {/* ── Section: AI Benchmark & Telemetry ─────────────── */}
            <SectionPanel
              id="benchmark" openId={openSection} onToggle={toggleSection}
              icon="📊" bgColor="rgba(236,72,153,0.35)" label="AI Benchmark & Telemetry"
            >
              <BenchmarkPanel
                apiUrl={apiUrl}
                token={token}
                onSelectModel={(mName) => {
                  setSegModel(mName);
                  setOpenSection('segmentation');
                  log(`Selected model from telemetry: ${mName}`, 'info');
                }}
              />
            </SectionPanel>

            {/* ── Section: 3D Mesh Reconstruction ──────────────── */}
            <SectionPanel
              id="geometry" openId={openSection} onToggle={toggleSection}
              icon="🦴" bgColor="rgba(34,197,94,0.35)" label="3D Mesh Reconstruction"
              badge={meshes.length || null}
            >
              <div className="input-row">
                <div className="field-group">
                  <label>Smooth Iters</label>
                  <input type="number" min="0" max="100" value={smoothIters} onChange={e => setSmoothIters(e.target.value)} />
                </div>
                <div className="field-group">
                  <label>Decimate</label>
                  <input type="number" step="0.05" min="0.05" max="1" value={decimateRatio} onChange={e => setDecimateRatio(e.target.value)} />
                </div>
              </div>

              <div className="field-group">
                <label>Export Format</label>
                <select value={meshFormat} onChange={e => setMeshFormat(e.target.value)}>
                  <option value="stl">STL — Stereolithography</option>
                  <option value="obj">OBJ — Wavefront Mesh</option>
                  <option value="ply">PLY — Polygon Format</option>
                </select>
              </div>

              {selectedMask ? (
                <button
                  id="reconstruct-btn"
                  className="success"
                  disabled={running === 'reconstruct'}
                  onClick={handleReconstruction}
                >
                  {running === 'reconstruct' ? <><span className="spinner" /> Processing…</> : `⬡ Generate ${meshFormat.toUpperCase()} Mesh`}
                </button>
              ) : (
                <p className="list-empty">Select a mask above first</p>
              )}

              {meshes.length > 0 && (
                <div>
                  <div className="divider" />
                  <label>Reconstructed Meshes</label>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 160, overflowY: 'auto' }}>
                    {meshes.map(m => (
                      <ItemCard
                        key={m.id}
                        active={selectedMesh?.id === m.id}
                        onClick={() => {
                          setSelectedMesh(m);
                          loadGeometry(m.id, m.file_path.split('.').pop(), 'bone');
                          checkPrintability(m.id);
                        }}
                        title={`Mesh-${m.id}`}
                        sub={`${m.triangle_count?.toLocaleString()} facets · ${Math.round((m.volume_mm3 || 0) / 1000)} cc`}
                        badge={m.is_watertight ? 'Watertight' : 'Non-manifold'}
                        badgeClass={m.is_watertight ? 'badge-success' : 'badge-warning'}
                        actions={[
                          <button key="d" className="ghost icon-btn sm" title="Download"
                            onClick={() => downloadFile(m.id, m.file_path.split('.').pop(), 'bone')}>
                            📥
                          </button>
                        ]}
                      />
                    ))}
                  </div>
                </div>
              )}
            </SectionPanel>

            {/* ── Section: Implant PSI ──────────────────────────── */}
            <SectionPanel
              id="implant" openId={openSection} onToggle={toggleSection}
              icon="⚙️" bgColor="rgba(242,201,76,0.35)" label="Implant PSI"
              badge={implants.length || null}
            >
              <div className="field-group">
                <label>Generative CAD Model</label>
                <select value={implantModel} onChange={e => setImplantModel(e.target.value)}>
                  {implantModels.length === 0 && <option value="">No models discovered</option>}
                  {implantModels.map(m => (
                    <option key={m.name} value={m.name}>{m.name} · {m.method}</option>
                  ))}
                </select>
              </div>

              <div className="field-group">
                <label>Export Format</label>
                <select value={implantFormat} onChange={e => setImplantFormat(e.target.value)}>
                  <option value="stl">STL Mesh</option>
                  <option value="obj">OBJ CAD Format</option>
                  <option value="ply">PLY Colormap</option>
                </select>
              </div>

              {selectedMask ? (
                <button
                  id="implant-btn"
                  className="purple"
                  disabled={running === 'implant'}
                  onClick={handleImplant}
                >
                  {running === 'implant' ? <><span className="spinner" /> Synthesizing…</> : '✦ Generate PSI Implant'}
                </button>
              ) : (
                <p className="list-empty">Select a mask above first</p>
              )}

              {implants.length > 0 && (
                <div>
                  <div className="divider" />
                  <label>Generated Implants</label>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 140, overflowY: 'auto' }}>
                    {implants.map(i => (
                      <ItemCard
                        key={i.id}
                        active={selectedImplant?.id === i.id}
                        onClick={() => { setSelectedImplant(i); loadGeometry(i.id, i.file_path.split('.').pop(), 'implant'); }}
                        title={`Implant-${i.id}`}
                        sub={`${Math.round((i.volume_mm3 || 0) / 1000)} cc · ${i.triangle_count?.toLocaleString()} facets`}
                        badge={i.method}
                        badgeClass="badge-gold"
                        actions={[
                          <button key="d" className="ghost icon-btn sm" title="Download"
                            onClick={() => downloadFile(i.id, i.file_path.split('.').pop(), 'implant')}>
                            📥
                          </button>
                        ]}
                      />
                    ))}
                  </div>
                </div>
              )}
            </SectionPanel>
          </>
        )}

        {/* Console Log — always visible at bottom */}
        <div style={{ marginTop: 'auto', paddingTop: 'var(--sp-2)' }}>
          <ConsoleLog logs={logs} logRef={logRef} />
        </div>
      </aside>

      {/* ══ MAIN VIEWPORT ═══════════════════════════════════════ */}
      <main className="main-viewport">
        <Canvas
          camera={{ position: [150, 150, 150], fov: 45 }}
          shadows
          gl={{ antialias: true, alpha: false }}
        >
          {/* Lighting rig */}
          <ambientLight intensity={0.45} />
          <directionalLight intensity={1.0} position={[100, 150, 100]} castShadow />
          <directionalLight intensity={0.35} position={[-80, -60, -100]} color="#6080ff" />
          <pointLight position={[0, 200, 0]} intensity={0.2} color="#ffffff" />

          {/* Reference grid */}
          <gridHelper args={[500, 25, '#1c2333', '#151c29']} position={[0, -80, 0]} />

          {/* Bone mesh (ivory/white) */}
          <MeshObject
            geometry={boneGeometry}
            color="#dde4ee"
            specular="#445566"
            shininess={30}
            wireframe={wireframe}
          />

          {/* Implant mesh (gold glow) */}
          <MeshObject
            geometry={implantGeometry}
            color="#f2c94c"
            specular="#ffffff"
            shininess={70}
            wireframe={wireframe}
          />

          <OrbitControls
            ref={controlsRef}
            enableDamping
            dampingFactor={0.08}
            minDistance={20}
            maxDistance={800}
          />
        </Canvas>

        {/* Floating: Viewport HUD */}
        <ViewportHUD
          wireframe={wireframe}
          setWireframe={setWireframe}
          onClear={() => { setBoneGeometry(null); setImplantGeometry(null); setPrintReport(null); log('Viewport cleared.'); }}
          selectedMesh={selectedMesh}
          selectedImplant={selectedImplant}
          onDownloadMesh={() => selectedMesh && downloadFile(selectedMesh.id, selectedMesh.file_path.split('.').pop(), 'bone')}
          onDownloadImplant={() => selectedImplant && downloadFile(selectedImplant.id, selectedImplant.file_path.split('.').pop(), 'implant')}
          cameraRef={controlsRef}
        />

        {/* Floating: Printability Report */}
        <PrintabilityReport report={printReport} onClose={() => setPrintReport(null)} />

        {/* Empty state overlay */}
        {!boneGeometry && !implantGeometry && (
          <div style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center',
            pointerEvents: 'none',
          }}>
            <div style={{ fontSize: 56, marginBottom: 16, opacity: 0.12 }}>🦴</div>
            <p style={{ color: 'var(--muted)', fontSize: 'var(--text-sm)', opacity: 0.5 }}>
              3D Viewport — No geometry loaded
            </p>
            <p style={{ color: 'var(--muted)', fontSize: 'var(--text-xs)', opacity: 0.35, marginTop: 4 }}>
              Upload a scan, run segmentation, then reconstruct a mesh
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
