import React, { useState, useEffect, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { STLLoader } from 'three/examples/jsm/loaders/STLLoader.js';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';
import { PLYLoader } from 'three/examples/jsm/loaders/PLYLoader.js';

export default function App() {
  // Connection & Authentication
  const [apiUrl, setApiUrl] = useState('http://localhost:8000/api/v2');
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin');
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem('token'));

  // Database Records lists
  const [volumes, setVolumes] = useState([]);
  const [masks, setMasks] = useState([]);
  const [meshes, setMeshes] = useState([]);
  const [implants, setImplants] = useState([]);

  // AI plugin registries (auto-discovered by the backend)
  const [segModels, setSegModels] = useState([]);
  const [implantModels, setImplantModels] = useState([]);
  const [segModel, setSegModel] = useState('');

  // Selection states
  const [selectedVolume, setSelectedVolume] = useState(null);
  const [selectedMask, setSelectedMask] = useState(null);
  const [selectedMesh, setSelectedMesh] = useState(null);
  const [selectedImplant, setSelectedImplant] = useState(null);

  // Form parameters
  const [smoothIters, setSmoothIters] = useState(10);
  const [decimateRatio, setDecimateRatio] = useState(0.5);
  const [meshFormat, setMeshFormat] = useState('stl');
  const [implantFormat, setImplantFormat] = useState('stl');
  const [implantModel, setImplantModel] = useState('mirror_implant');

  // Printability check data
  const [printReport, setPrintReport] = useState(null);

  // Viewport states
  const [wireframe, setWireframe] = useState(false);
  const [boneGeometry, setBoneGeometry] = useState(null);
  const [implantGeometry, setImplantGeometry] = useState(null);

  // File upload progress
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  // Console Logs
  const [logs, setLogs] = useState([]);
  const logRef = useRef(null);

  // Sections toggle
  const [openSection, setOpenSection] = useState('auth');

  // Auto-scroll console
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);

  function log(msg, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    setLogs((prev) => [...prev, `[${timestamp}] [${type.toUpperCase()}] ${msg}`]);
  }

  // API Call helper
  async function request(endpoint, method = 'GET', body = null, isMultipart = false) {
    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    let options = { method, headers };
    
    if (body) {
      if (isMultipart) {
        options.body = body;
      } else {
        headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(body);
      }
    }

    let targetUrl = `${apiUrl}${endpoint}`;
    if (endpoint.startsWith('/auth/')) {
      // Auth routes are mounted directly on /api/auth without version prefixes
      const apiRoot = apiUrl.replace(/\/v\d+$/, '');
      targetUrl = `${apiRoot}${endpoint}`;
    }
    const response = await fetch(targetUrl, options);
    
    if (response.status === 204) {
      return null;
    }

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.message || response.statusText);
    }
    return payload;
  }

  // Handle Authentication
  async function handleLogin(e) {
    e.preventDefault();
    try {
      log('Attempting authentication...', 'info');
      // The backend's /auth/login expects a JSON body ({username, password}),
      // not an OAuth2 form-encoded request.
      const res = await request('/auth/login', 'POST', { username, password });
      const accToken = res.data.access_token;
      
      setToken(accToken);
      localStorage.setItem('token', accToken);
      setIsLoggedIn(true);
      log('User authenticated successfully.', 'success');
      setOpenSection('ingestion');
      fetchVolumes(accToken);
    } catch (err) {
      log(`Login failed: ${err.message}`, 'error');
    }
  }

  async function handleRegister(e) {
    e.preventDefault();
    try {
      log('Attempting account creation...', 'info');
      // RegisterRequest requires every field to be present (Optional[] only
      // means the value may be null, not that the key can be omitted).
      await request('/auth/register', 'POST', {
        email: username.includes('@') ? username : `${username}@medai.local`,
        username,
        password,
        dob: null,
        gender: null,
        first_name: null,
        last_name: null,
        full_name: username,
        phone: null,
        address: null,
        identity_card: null,
        identity_card_date: null,
        identity_card_place: null,
      });
      log('Account created successfully. You can now log in.', 'success');
    } catch (err) {
      log(`Registration failed: ${err.message}`, 'error');
    }
  }

  function handleLogout() {
    setToken('');
    localStorage.removeItem('token');
    setIsLoggedIn(false);
    setVolumes([]);
    setMasks([]);
    setMeshes([]);
    setImplants([]);
    setSelectedVolume(null);
    setSelectedMask(null);
    setSelectedMesh(null);
    setSelectedImplant(null);
    setBoneGeometry(null);
    setImplantGeometry(null);
    setPrintReport(null);
    log('User logged out.', 'info');
    setOpenSection('auth');
  }

  // Fetch Database Records
  async function fetchVolumes(activeToken = token) {
    try {
      const res = await request('/volumes/all');
      setVolumes(res.data || []);
      log('Fetched volumes list.', 'info');
    } catch (err) {
      log(`Failed to fetch volumes: ${err.message}`, 'error');
    }
  }

  async function fetchMasks(volId) {
    try {
      const res = await request('/inference/masks/all');
      const filtered = (res.data || []).filter((m) => m.volume_id === volId);
      setMasks(filtered);
    } catch (err) {
      log(`Failed to fetch masks: ${err.message}`, 'error');
    }
  }

  async function fetchMeshes() {
    try {
      const res = await request('/meshes/all');
      setMeshes(res.data || []);
    } catch (err) {
      log(`Failed to fetch meshes: ${err.message}`, 'error');
    }
  }

  async function fetchImplants() {
    try {
      const res = await request('/implants/all');
      setImplants(res.data || []);
    } catch (err) {
      log(`Failed to fetch implants: ${err.message}`, 'error');
    }
  }

  // Fetch the AI plugin registries so the UI reflects whatever segmentation /
  // implant models the backend has actually discovered, instead of hardcoding
  // model names that may not be registered.
  async function fetchSegModels() {
    try {
      const res = await request('/inference/models');
      const models = res.data || [];
      setSegModels(models);
      if (models.length > 0) setSegModel((prev) => prev || models[0].name);
    } catch (err) {
      log(`Failed to fetch segmentation models: ${err.message}`, 'error');
    }
  }

  async function fetchImplantModels() {
    try {
      const res = await request('/implants/models');
      const models = res.data || [];
      setImplantModels(models);
      if (models.length > 0) setImplantModel((prev) => prev || models[0].name);
    } catch (err) {
      log(`Failed to fetch implant models: ${err.message}`, 'error');
    }
  }

  // Load lists on login
  useEffect(() => {
    if (isLoggedIn) {
      fetchVolumes();
      fetchMeshes();
      fetchImplants();
      fetchSegModels();
      fetchImplantModels();
    }
  }, [isLoggedIn]);

  // Handle Scan Upload
  async function handleUpload(e) {
    e.preventDefault();
    if (!uploadFile) return;
    try {
      log(`Uploading ${uploadFile.name}...`, 'info');
      setUploadProgress(20);
      
      const formData = new FormData();
      formData.append('file', uploadFile);
      
      setUploadProgress(50);
      const res = await request('/volumes/upload', 'POST', formData, true);
      setUploadProgress(100);
      log(`Volume ingested successfully. ID: ${res.data.id}`, 'success');
      setTimeout(() => setUploadProgress(0), 1500);
      fetchVolumes();
    } catch (err) {
      log(`Upload failed: ${err.message}`, 'error');
      setUploadProgress(0);
    }
  }

  // Trigger AI Segmentation
  async function handleSegmentation() {
    if (!selectedVolume || !segModel) return;
    try {
      log(`Scheduling AI Segmentation (${segModel}) on Volume ${selectedVolume.id}...`, 'info');
      const res = await request(`/inference/segment/${selectedVolume.id}`, 'POST', {
        model_name: segModel
      });
      const taskId = res.data.task_id;
      log(`Task scheduled. Ticket: ${taskId}`, 'info');

      // Poll task status
      let attempts = 0;
      const interval = setInterval(async () => {
        attempts++;
        if (attempts > 180) {
          clearInterval(interval);
          log('Polling timed out.', 'error');
          return;
        }
        const statusRes = await request(`/inference/tasks/${taskId}`);
        const taskInfo = statusRes.data;
        if (taskInfo.status === 'SUCCESS') {
          clearInterval(interval);
          log(`Inference successful. Mask ID: ${taskInfo.result_id}`, 'success');
          fetchMasks(selectedVolume.id);
        } else if (taskInfo.status === 'FAILED') {
          clearInterval(interval);
          log(`Inference failed: ${taskInfo.error}`, 'error');
        } else {
          log(`Task progress: ${taskInfo.progress}%`, 'info');
        }
      }, 1000);

    } catch (err) {
      log(`Segmentation failed: ${err.message}`, 'error');
    }
  }

  // Trigger 3D Reconstruction
  async function handleReconstruction() {
    if (!selectedMask) return;
    try {
      log(`Reconstructing mask ${selectedMask.id} as ${meshFormat.toUpperCase()}...`, 'info');
      const res = await request(`/meshes/reconstruct/${selectedMask.id}`, 'POST', {
        smooth_iterations: parseInt(smoothIters),
        decimate_ratio: parseFloat(decimateRatio),
        export_format: meshFormat
      });
      log(`Mesh reconstructed. ID: ${res.data.id}`, 'success');
      fetchMeshes();
      setSelectedMesh(res.data);
      loadGeometry(res.data.id, meshFormat, 'bone');
      checkPrintability(res.data.id);
    } catch (err) {
      log(`Reconstruction failed: ${err.message}`, 'error');
    }
  }

  // Trigger Implant Recommendation
  async function handleImplant() {
    if (!selectedMask) return;
    try {
      log(`Reconstructing implant for defect mask ${selectedMask.id}...`, 'info');
      const res = await request(`/implants/recommend/${selectedMask.id}`, 'POST', {
        model_name: implantModel,
        smooth_iterations: parseInt(smoothIters),
        decimate_ratio: parseFloat(decimateRatio),
        export_format: implantFormat
      });
      log(`Implant generated successfully. ID: ${res.data.id}`, 'success');
      fetchImplants();
      setSelectedImplant(res.data);
      loadGeometry(res.data.id, implantFormat, 'implant');
    } catch (err) {
      log(`Implant generation failed: ${err.message}`, 'error');
    }
  }

  // Check Printability
  async function checkPrintability(meshId) {
    try {
      const res = await request(`/meshes/${meshId}/printability`);
      setPrintReport(res.data);
      log('Printability assessment complete.', 'info');
    } catch (err) {
      log(`Printability check failed: ${err.message}`, 'error');
    }
  }

  // Parse and Load Geometries locally
  async function loadGeometry(id, format, target) {
    try {
      log(`Loading 3D asset ${target} (ID: ${id}) into viewport...`, 'info');
      const endpoint = target === 'bone' ? `/meshes/${id}/download` : `/implants/${id}/download`;
      
      const response = await fetch(`${apiUrl}${endpoint}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) throw new Error('Mesh download failed');
      
      const buffer = await response.arrayBuffer();
      let geom = null;

      if (format === 'stl') {
        geom = new STLLoader().parse(buffer);
      } else if (format === 'ply') {
        geom = new PLYLoader().parse(buffer);
      } else if (format === 'obj') {
        const text = new TextDecoder().decode(buffer);
        const objGroup = new OBJLoader().parse(text);
        objGroup.traverse((child) => {
          if (child.isMesh) {
            geom = child.geometry;
          }
        });
      }

      if (geom) {
        geom.computeVertexNormals();
        geom.center();
        
        if (target === 'bone') {
          setBoneGeometry(geom);
        } else {
          setImplantGeometry(geom);
        }
        log(`3D ${target} geometry loaded.`, 'success');
      } else {
        log('Failed to parse 3D buffer.', 'error');
      }
    } catch (err) {
      log(`Error loading geometry: ${err.message}`, 'error');
    }
  }

  // Download assets locally
  async function downloadFile(id, format, target) {
    try {
      const endpoint = target === 'bone' ? `/meshes/${id}/download` : `/implants/${id}/download`;
      const response = await fetch(`${apiUrl}${endpoint}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${target}_${id}.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
      log(`Downloaded ${target} mesh file.`, 'success');
    } catch (err) {
      log(`Download failed: ${err.message}`, 'error');
    }
  }

  // Render Section Helper
  const toggleSection = (sec) => setOpenSection(openSection === sec ? '' : sec);

  return (
    <div className="app-container">
      {/* Sidebar Controls panel */}
      <aside className="sidebar">
        <div>
          <h2 style={{ fontSize: '18px', fontWeight: 'bold', color: 'var(--accent)' }}>MedAI-OS Clinical Suite</h2>
          <p className="item-card-sub">Bone Segmentation, Mesh Tuning & implant Fitting</p>
        </div>

        {/* 1. API Configuration */}
        <div className="section-panel">
          <div className="section-header" onClick={() => toggleSection('api')}>
            <span>API Server Node</span>
            <span>{openSection === 'api' ? '▼' : '▲'}</span>
          </div>
          {openSection === 'api' && (
            <div className="section-body">
              <input 
                type="text" 
                value={apiUrl} 
                onChange={(e) => setApiUrl(e.target.value)} 
                placeholder="FastAPI API URL"
              />
            </div>
          )}
        </div>

        {/* 2. Authentication panel */}
        <div className="section-panel">
          <div className="section-header" onClick={() => toggleSection('auth')}>
            <span>User Authentication</span>
            <span>{openSection === 'auth' ? '▼' : '▲'}</span>
          </div>
          {openSection === 'auth' && (
            <div className="section-body">
              {isLoggedIn ? (
                <div>
                  <p style={{ fontSize: '12px', marginBottom: '8px' }}>Signed in as: <strong style={{ color: 'var(--success)' }}>{username}</strong></p>
                  <button className="ghost" onClick={handleLogout}>Log Out</button>
                </div>
              ) : (
                <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <input 
                    type="text" 
                    value={username} 
                    onChange={(e) => setUsername(e.target.value)} 
                    placeholder="Username"
                  />
                  <input 
                    type="password" 
                    value={password} 
                    onChange={(e) => setPassword(e.target.value)} 
                    placeholder="Password"
                  />
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button type="submit">Log In</button>
                    <button className="ghost" onClick={handleRegister}>Register</button>
                  </div>
                </form>
              )}
            </div>
          )}
        </div>

        {isLoggedIn && (
          <>
            {/* 3. Volumetric Ingestion (Upload) */}
            <div className="section-panel">
              <div className="section-header" onClick={() => toggleSection('ingestion')}>
                <span>Volumetric Ingestion</span>
                <span>{openSection === 'ingestion' ? '▼' : '▲'}</span>
              </div>
              {openSection === 'ingestion' && (
                <div className="section-body">
                  <form onSubmit={handleUpload} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <input 
                      type="file" 
                      onChange={(e) => setUploadFile(e.target.files[0])}
                    />
                    <button type="submit" disabled={!uploadFile}>Upload DICOM/NIfTI</button>
                  </form>
                  {uploadProgress > 0 && (
                    <div style={{ marginTop: '6px' }}>
                      <div className="progress">
                        <div style={{ width: `${uploadProgress}%` }}></div>
                      </div>
                      <p style={{ fontSize: '10px', color: 'var(--muted)', textAlign: 'center', marginTop: '4px' }}>Uploading: {uploadProgress}%</p>
                    </div>
                  )}
                  
                  <div style={{ marginTop: '10px' }}>
                    <p style={{ fontSize: '11px', color: 'var(--muted)', marginBottom: '6px' }}>Available Volumes:</p>
                    <div className="list">
                      {volumes.map((v) => (
                        <div 
                          key={v.id} 
                          className={`item-card ${selectedVolume?.id === v.id ? 'active' : ''}`}
                          onClick={() => {
                            setSelectedVolume(v);
                            fetchMasks(v.id);
                            log(`Selected Volume ${v.id}.`, 'info');
                          }}
                        >
                          <div className="item-card-title">
                            <span>ID: {v.id} ({v.patient_id || 'Anon'})</span>
                          </div>
                          <div className="item-card-sub">
                            Spacing: {v.spacing.map(n => n.toFixed(1)).join(', ')}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* 4. AI Segmentation */}
            <div className="section-panel">
              <div className="section-header" onClick={() => toggleSection('segmentation')}>
                <span>AI Segmentation</span>
                <span>{openSection === 'segmentation' ? '▼' : '▲'}</span>
              </div>
              {openSection === 'segmentation' && (
                <div className="section-body">
                  <div>
                    <label>AI Model (auto-discovered)</label>
                    <select value={segModel} onChange={(e) => setSegModel(e.target.value)}>
                      {segModels.length === 0 && <option value="">No models discovered</option>}
                      {segModels.map((m) => (
                        <option key={m.name} value={m.name}>{m.name} (v{m.version})</option>
                      ))}
                    </select>
                  </div>
                  <button
                    disabled={!selectedVolume || !segModel}
                    onClick={handleSegmentation}
                  >
                    Run Segmentation
                  </button>

                  {selectedVolume && (
                    <div style={{ marginTop: '10px' }}>
                      <p style={{ fontSize: '11px', color: 'var(--muted)', marginBottom: '6px' }}>Volume Mask Outputs:</p>
                      <div className="list">
                        {masks.map((m) => (
                          <div 
                            key={m.id} 
                            className={`item-card ${selectedMask?.id === m.id ? 'active' : ''}`}
                            onClick={() => {
                              setSelectedMask(m);
                              log(`Selected Mask ${m.id}.`, 'info');
                            }}
                          >
                            <div className="item-card-title">
                              <span>Mask ID: {m.id}</span>
                              <span style={{ fontSize: '10px', color: 'var(--success)' }}>{m.model_name}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* 5. 3D Surface Reconstruction */}
            <div className="section-panel">
              <div className="section-header" onClick={() => toggleSection('geometry')}>
                <span>3D Mesh Reconstruction</span>
                <span>{openSection === 'geometry' ? '▼' : '▲'}</span>
              </div>
              {openSection === 'geometry' && (
                <div className="section-body">
                  <div>
                    <label>Laplacian Smooth iterations</label>
                    <input 
                      type="number" 
                      value={smoothIters} 
                      onChange={(e) => setSmoothIters(e.target.value)}
                    />
                  </div>
                  <div>
                    <label>Decimate ratio (0.1 = 10%)</label>
                    <input 
                      type="number" 
                      step="0.05" 
                      value={decimateRatio} 
                      onChange={(e) => setDecimateRatio(e.target.value)}
                    />
                  </div>
                  <div>
                    <label>Mesh Format Option</label>
                    <select value={meshFormat} onChange={(e) => setMeshFormat(e.target.value)}>
                      <option value="stl">STL (Stereolithography)</option>
                      <option value="obj">OBJ (Wavefront Mesh)</option>
                      <option value="ply">PLY (Polygon format)</option>
                    </select>
                  </div>
                  <button 
                    disabled={!selectedMask} 
                    className="success"
                    onClick={handleReconstruction}
                  >
                    Generate Mesh ({meshFormat.toUpperCase()})
                  </button>
                  
                  {meshes.length > 0 && (
                    <div style={{ marginTop: '10px' }}>
                      <p style={{ fontSize: '11px', color: 'var(--muted)', marginBottom: '6px' }}>Reconstructed Meshes:</p>
                      <div className="list">
                        {meshes.map((m) => (
                          <div 
                            key={m.id} 
                            className={`item-card ${selectedMesh?.id === m.id ? 'active' : ''}`}
                            onClick={() => {
                              setSelectedMesh(m);
                              loadGeometry(m.id, m.file_path.split('.').pop(), 'bone');
                              checkPrintability(m.id);
                            }}
                          >
                            <div className="item-card-title">
                              <span>Mesh ID: {m.id}</span>
                              <span style={{ fontSize: '10px', color: m.is_watertight ? 'var(--success)' : 'var(--warning)' }}>
                                {m.is_watertight ? 'Watertight' : 'Non-manifold'}
                              </span>
                            </div>
                            <div className="item-card-sub">
                              Facets: {m.triangle_count.toLocaleString()} | Vol: {Math.round(m.volume_mm3 / 1000)} cc
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* 6. Implant Recommendation */}
            <div className="section-panel">
              <div className="section-header" onClick={() => toggleSection('implant')}>
                <span>Implant PSI Recommendation</span>
                <span>{openSection === 'implant' ? '▼' : '▲'}</span>
              </div>
              {openSection === 'implant' && (
                <div className="section-body">
                  <div>
                    <label>Generative CAD Model (auto-discovered)</label>
                    <select value={implantModel} onChange={(e) => setImplantModel(e.target.value)}>
                      {implantModels.length === 0 && <option value="">No models discovered</option>}
                      {implantModels.map((m) => (
                        <option key={m.name} value={m.name}>{m.name} ({m.method})</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label>Implant Format Option</label>
                    <select value={implantFormat} onChange={(e) => setImplantFormat(e.target.value)}>
                      <option value="stl">STL Mesh</option>
                      <option value="obj">OBJ CAD Format</option>
                      <option value="ply">PLY Colormap Format</option>
                    </select>
                  </div>
                  <button 
                    disabled={!selectedMask} 
                    style={{ background: '#bf5af2' }}
                    onClick={handleImplant}
                  >
                    Generate PSI Implant
                  </button>
                  
                  {implants.length > 0 && (
                    <div style={{ marginTop: '10px' }}>
                      <p style={{ fontSize: '11px', color: 'var(--muted)', marginBottom: '6px' }}>Generated Implants:</p>
                      <div className="list">
                        {implants.map((i) => (
                          <div 
                            key={i.id} 
                            className={`item-card ${selectedImplant?.id === i.id ? 'active' : ''}`}
                            onClick={() => {
                              setSelectedImplant(i);
                              loadGeometry(i.id, i.file_path.split('.').pop(), 'implant');
                            }}
                          >
                            <div className="item-card-title">
                              <span>Implant ID: {i.id}</span>
                              <span style={{ fontSize: '10px', color: 'var(--success)' }}>{i.method}</span>
                            </div>
                            <div className="item-card-sub">
                              Vol: {Math.round(i.volume_mm3 / 1000)} cc | Facets: {i.triangle_count.toLocaleString()}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        )}

        {/* Logs Console */}
        <div style={{ marginTop: 'auto' }}>
          <p style={{ fontSize: '11px', fontWeight: 'bold', color: 'var(--muted)', marginBottom: '6px' }}>MedAI-OS System Console Logs</p>
          <div ref={logRef} className="console-log">
            {logs.length === 0 ? 'Initialize connection to begin clinical suite session.' : logs.join('\n')}
          </div>
        </div>
      </aside>

      {/* Main Viewport Workspace */}
      <main className="main-viewport">
        {/* Render interactive 3D WebGL Canvas */}
        <div style={{ width: '100%', height: '100%' }}>
          <Canvas camera={{ position: [150, 150, 150], fof: 45 }}>
            <ambientLight intensity={0.6} />
            <directionalLight intensity={0.9} position={[100, 100, 100]} />
            <directionalLight intensity={0.4} position={[-100, -50, -100]} color="#88aaff" />
            <gridHelper args={[400, 20, 0x30363d, 0x21262d]} />
            
            {/* Main bone mesh (grey) */}
            {boneGeometry && (
              <mesh geometry={boneGeometry} castShadow receiveShadow>
                <meshPhongMaterial 
                  color="#e6edf3" 
                  specular="#333333" 
                  shininess={25} 
                  wireframe={wireframe} 
                />
              </mesh>
            )}

            {/* Recommended Implant mesh (glowing gold) */}
            {implantGeometry && (
              <mesh geometry={implantGeometry} castShadow receiveShadow>
                <meshPhongMaterial 
                  color="#f2c94c" 
                  specular="#ffffff" 
                  shininess={60} 
                  wireframe={wireframe} 
                />
              </mesh>
            )}

            <OrbitControls enableDamping />
          </Canvas>
        </div>

        {/* Floating Viewport control HUD overlay */}
        <div style={{
          position: 'absolute',
          top: '20px',
          left: '20px',
          background: 'rgba(22, 27, 34, 0.85)',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          padding: '16px',
          width: '240px',
          backdropFilter: 'blur(10px)',
          zIndex: 10,
          display: 'flex',
          flexDirection: 'column',
          gap: '10px'
        }}>
          <h4 style={{ fontSize: '13px', fontWeight: 'bold', color: 'var(--accent)', borderBottom: '1px solid var(--border)', paddingBottom: '6px' }}>
            Viewport Controls
          </h4>
          
          <div style={{ display: 'flex', gap: '6px' }}>
            <button className="ghost" style={{ padding: '6px' }} onClick={() => setWireframe(!wireframe)}>
              Toggle Wireframe
            </button>
            <button className="ghost" style={{ padding: '6px' }} onClick={() => {
              setBoneGeometry(null);
              setImplantGeometry(null);
              setPrintReport(null);
              log('Viewport cleared.', 'info');
            }}>
              Clear Canvas
            </button>
          </div>

          {selectedMesh && (
            <button 
              className="ghost" 
              onClick={() => downloadFile(selectedMesh.id, selectedMesh.file_path.split('.').pop(), 'bone')}
            >
              📥 Download Bone Mesh ({selectedMesh.file_path.split('.').pop().toUpperCase()})
            </button>
          )}

          {selectedImplant && (
            <button 
              style={{ background: '#bf5af2' }}
              onClick={() => downloadFile(selectedImplant.id, selectedImplant.file_path.split('.').pop(), 'implant')}
            >
              📥 Download Implant ({selectedImplant.file_path.split('.').pop().toUpperCase()})
            </button>
          )}
        </div>

        {/* 3D Printing Printability calibrator HUD overlay */}
        {printReport && (
          <div style={{
            position: 'absolute',
            bottom: '20px',
            right: '20px',
            background: 'rgba(22, 27, 34, 0.85)',
            border: '1px solid var(--border)',
            borderRadius: '8px',
            padding: '16px',
            width: '320px',
            backdropFilter: 'blur(10px)',
            zIndex: 10,
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: '6px' }}>
              <h4 style={{ fontSize: '13px', fontWeight: 'bold', color: 'var(--accent)' }}>
                3D Printing Check Report
              </h4>
              <span className={`pill ${printReport.ready_to_print ? 'ok' : 'bad'}`} style={{
                background: printReport.ready_to_print ? 'rgba(63, 185, 80, 0.15)' : 'rgba(248, 81, 73, 0.15)',
                color: printReport.ready_to_print ? 'var(--success)' : 'var(--danger)',
                border: `1px solid ${printReport.ready_to_print ? 'var(--success)' : 'var(--danger)'}`,
                padding: '2px 8px',
                borderRadius: '999px',
                fontSize: '10px',
                fontWeight: 'bold'
              }}>
                {printReport.ready_to_print ? 'READY TO PRINT' : 'NOT READY'}
              </span>
            </div>
            
            <div style={{ fontSize: '11px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', color: 'var(--muted)' }}>
              <div>Watertight: <strong style={{ color: printReport.is_watertight ? 'var(--success)' : 'var(--danger)' }}>{printReport.is_watertight ? 'YES' : 'NO'}</strong></div>
              <div>Consistent Normals: <strong style={{ color: printReport.winding_consistent ? 'var(--success)' : 'var(--danger)' }}>{printReport.winding_consistent ? 'YES' : 'NO'}</strong></div>
              <div>Euler Number: <strong style={{ color: 'var(--text)' }}>{printReport.euler_number}</strong></div>
              <div>Empty Space Check: <strong style={{ color: 'var(--success)' }}>{printReport.is_empty ? 'EMPTY' : 'VALID SURFACE'}</strong></div>
              <div>Surface Area: <strong style={{ color: 'var(--text)' }}>{Math.round(printReport.area_mm2).toLocaleString()} mm²</strong></div>
              <div>Mesh Volume: <strong style={{ color: 'var(--text)' }}>{Math.round(printReport.volume_mm3).toLocaleString()} mm³</strong></div>
            </div>

            {printReport.issues.length > 0 && (
              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '6px', marginTop: '4px' }}>
                <p style={{ fontSize: '10px', fontWeight: 'bold', color: 'var(--danger)', marginBottom: '2px' }}>Calibration Issues:</p>
                <ul style={{ paddingLeft: '14px', fontSize: '10px', color: 'var(--warning)' }}>
                  {printReport.issues.map((iss, index) => (
                    <li key={index}>{iss}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
