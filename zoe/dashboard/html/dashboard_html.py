"""HTML completo del dashboard web de ZOE (embebido)."""

from __future__ import annotations


def _get_dashboard_html() -> str:
    """Devuelve el HTML completo del dashboard (embebido)."""
    return '''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#0a0a0f">
<link rel="manifest" href="/manifest.json">
<title>ZOE v2.1.2 -- Synthetic Cognitive Organism</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #0a0a0f; color: #e0e0e0; font-family: 'Segoe UI', system-ui, sans-serif; height: 100vh; overflow-y: auto; }

/* Top bar */
.topbar { display: flex; align-items: center; padding: 8px 16px; background: #12121a; border-bottom: 1px solid #2a2a3a; gap: 16px; }
.topbar .logo { font-size: 18px; font-weight: bold; color: #7c4dff; }
.topbar .llm-select { background: #1a1a2a; color: #e0e0e0; border: 1px solid #3a3a4a; padding: 4px 8px; border-radius: 4px; font-size: 13px; }
.topbar .meta-status { display: flex; align-items: center; gap: 6px; font-size: 13px; color: #4caf50; }
.topbar .meta-dot { width: 8px; height: 8px; border-radius: 50%; background: #4caf50; }
.topbar .meta-dot.sleeping { background: #2196f3; }
.topbar .meta-dot.drowsy { background: #ff9800; }
.topbar .spacer { flex: 1; }

/* Main layout */
.main { display: grid; grid-template-columns: 260px 1fr 280px; height: calc(100vh - 49px); }
.panel { padding: 12px; overflow-y: auto; }
.panel-left { border-right: 1px solid #1a1a2a; background: #0d0d14; }
.panel-right { border-left: 1px solid #1a1a2a; background: #0d0d14; }
.panel-center { display: flex; flex-direction: column; }

/* State indicators */
.state-item { margin-bottom: 10px; }
.state-label { font-size: 11px; color: #888; margin-bottom: 3px; text-transform: uppercase; letter-spacing: 0.5px; }
.state-bar { height: 6px; background: #1a1a2a; border-radius: 3px; overflow: hidden; }
.state-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease; }
.state-fill.energy { background: linear-gradient(90deg, #f44336, #ff9800, #4caf50); }
.state-fill.fatigue { background: linear-gradient(90deg, #4caf50, #ff9800, #f44336); }
.state-fill.tension { background: #7c4dff; }
.state-fill.physics { background: #00bcd4; }

/* Tensions */
.tension-item { margin-bottom: 6px; }
.tension-name { font-size: 10px; color: #aaa; }

/* Actions */
.actions { margin-top: 16px; display: flex; flex-direction: column; gap: 6px; }
.action-btn { background: #1a1a2a; color: #e0e0e0; border: 1px solid #2a2a3a; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; text-align: left; transition: background 0.2s; }
.action-btn:hover { background: #2a2a3a; border-color: #7c4dff; }

/* Chat */
.chat-header { padding: 8px 16px; border-bottom: 1px solid #1a1a2a; font-size: 14px; color: #888; }
.chat-messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.msg { max-width: 80%; padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.5; }
.msg.user { align-self: flex-end; background: #1a3a5a; color: #fff; }
.msg.zoe { align-self: flex-start; background: #2a1a3a; color: #e0e0e0; border: 1px solid #3a2a4a; }
.msg .ts { font-size: 10px; color: #666; margin-top: 4px; }
.msg .sys { font-size: 10px; color: #7c4dff; margin-top: 2px; }
.chat-input { padding: 12px; border-top: 1px solid #1a1a2a; display: flex; gap: 8px; }
.chat-input input { flex: 1; background: #1a1a2a; color: #e0e0e0; border: 1px solid #2a2a3a; padding: 10px 14px; border-radius: 8px; font-size: 14px; outline: none; }
.chat-input input:focus { border-color: #7c4dff; }
.chat-input button { background: #7c4dff; color: #fff; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: bold; }
.chat-input button:hover { background: #651fff; }
.chat-input button:disabled { background: #3a3a4a; cursor: not-allowed; }

/* ZOE v2.1.1 -- Indicador de pensando */
.thinking-indicator {
  display: none;
  padding: 8px 16px;
  background: #1a0a2e;
  border-top: 1px solid #3a1a5a;
  color: #b39ddb;
  font-size: 13px;
  font-style: italic;
  align-items: center;
  gap: 8px;
  animation: thinkingFadeIn 0.3s ease;
}
.thinking-indicator.active {
  display: flex;
}
.thinking-icon { font-size: 16px; }
.thinking-text { color: #b39ddb; }
.thinking-dots span {
  display: inline-block;
  animation: thinkingBounce 1.4s infinite ease-in-out both;
}
.thinking-dots span:nth-child(1) { animation-delay: -0.32s; }
.thinking-dots span:nth-child(2) { animation-delay: -0.16s; }
.thinking-dots span:nth-child(3) { animation-delay: 0s; }
@keyframes thinkingBounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}
@keyframes thinkingFadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Thoughts */
.thoughts-header { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid #1a1a2a; }
.thought { background: #12121a; border-left: 3px solid #7c4dff; padding: 8px 10px; margin-bottom: 8px; border-radius: 0 6px 6px 0; font-size: 12px; }

/* ACD badges (Fase 5) */
.acd-badge { display: inline-block; padding: 1px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-left: 8px; vertical-align: middle; }
.acd-l0_reflex { background: #1b5e20; color: #a5d6a7; }
.acd-l1_fast { background: #0d47a1; color: #90caf9; }
.acd-l2_standard { background: #e65100; color: #ffcc80; }
.acd-l3_deep { background: #4a148c; color: #ce93d8; }
.acd-meta { font-size: 10px; color: #888; margin-left: 6px; vertical-align: middle; }
.thought .ts { font-size: 9px; color: #555; }
.thought .sys { font-size: 9px; color: #7c4dff; }

/* Federation */
.fed-section { margin-top: 16px; padding-top: 12px; border-top: 1px solid #1a1a2a; }
.fed-header { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
.fed-peer { display: flex; align-items: center; gap: 6px; font-size: 12px; margin-bottom: 4px; }
.fed-dot { width: 6px; height: 6px; border-radius: 50%; background: #4caf50; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2a2a3a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3a3a4a; }

/* Responsive -- PWA mobile support (Sprint 1.3) */
@media (max-width: 768px) {
  .main { grid-template-columns: 1fr; height: calc(100vh - 49px); }
  .panel-left, .panel-right {
    display: none;
    position: absolute;
    top: 49px;
    bottom: 0;
    width: 85%;
    max-width: 320px;
    z-index: 100;
    background: #0d0d14;
    overflow-y: auto;
  }
  .panel-left { left: 0; border-right: 1px solid #2a2a3a; }
  .panel-right { right: 0; border-left: 1px solid #2a2a3a; }
  .panel-left.show, .panel-right.show { display: block; }
  .topbar { padding: 6px 10px; gap: 8px; }
  .topbar .logo { font-size: 15px; }
  .topbar .llm-select { font-size: 12px; max-width: 120px; }
  .topbar .meta-status { font-size: 11px; }
  .panel { padding: 8px; }
  .chat-messages { font-size: 14px; }
  .chat-input { font-size: 14px; }
  .btn-mobile-toggle { display: inline-block !important; }
}

@media (max-width: 480px) {
  .topbar .logo { font-size: 13px; }
  .topbar .llm-select { max-width: 90px; font-size: 11px; }
  .chat-messages { font-size: 13px; }
  .chat-input { font-size: 13px; padding: 6px; }
  .state-label { font-size: 10px; }
}
</style>
</head>
<body>

<div class="topbar">
  <span class="logo">&#129655; ZOE v1.0</span>
  <select class="llm-select" id="llmSelect" onchange="switchLLM()">
    <option value="mock">Mock</option>
    <option value="ollama">Ollama (Qwen 2.5 3B)</option>
    <option value="zai">ZAI (GLM-4)</option>
    <option value="openai_compatible">OpenAI-compatible</option>
  </select>
  <div class="meta-status">
    <span class="meta-dot" id="metaDot"></span>
    <span id="metaText">Awake</span>
  </div>
  <div class="spacer"></div>
  <span style="font-size:12px;color:#666" id="iterText">Iter: 0</span>
</div>

<div class="main">
  <!-- LEFT PANEL: State -->
  <div class="panel panel-left">
    <div class="state-item">
      <div class="state-label">Energia</div>
      <div class="state-bar"><div class="state-fill energy" id="barEnergy" style="width:100%"></div></div>
    </div>
    <div class="state-item">
      <div class="state-label">Fatiga</div>
      <div class="state-bar"><div class="state-fill fatigue" id="barFatigue" style="width:0%"></div></div>
    </div>
    <div class="state-item">
      <div class="state-label">Arousal</div>
      <div class="state-bar"><div class="state-fill tension" id="barArousal" style="width:30%"></div></div>
    </div>
    <div class="state-item">
      <div class="state-label">Atencion</div>
      <div class="state-bar"><div class="state-fill physics" id="barAttention" style="width:50%"></div></div>
    </div>

    <div style="margin-top:16px;font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Tensiones</div>
    <div id="tensions"></div>

    <div class="actions">
      <button class="action-btn" onclick="feedFile()">&#128451; Alimentar documento</button>
      <button class="action-btn" onclick="showStats()">&#128202; Estadisticas</button>
      <button class="action-btn" onclick="showMemory()">&#129504; Memoria</button>
      <button class="action-btn" onclick="showIdentity()">&#129655; Identidad</button>
      <button class="action-btn" onclick="toggleSleep()">&#128164; Dormir / &#9728;&#65039; Despertar</button>
      <button class="action-btn" onclick="showHistory()">&#128220; Historial</button>
      <button class="action-btn" onclick="showCapsules()">&#128230; Capsulas</button>
      <button class="action-btn" onclick="showQuarantine()">&#128274; Cuarentena</button>
      <button class="action-btn" onclick="showMarketplace()">&#127978; Marketplace</button>
    </div>

    <div class="fed-section">
      <div class="fed-header">Federacion</div>
      <div id="federation"><div style="font-size:11px;color:#666">Sin peers conectados</div></div>
    </div>
  </div>

  <!-- CENTER PANEL: Chat -->
  <div class="panel-center">
    <div class="chat-header">Conversacion con ZOE</div>
    <div class="chat-messages" id="chatMessages"></div>
    <!-- ZOE v2.1.1 -- Indicador de pensando -->
    <div class="thinking-indicator" id="thinkingIndicator">
      <span class="thinking-icon">&#129302;</span>
      <span class="thinking-text">ZOE está pensando</span>
      <span class="thinking-dots"><span>.</span><span>.</span><span>.</span></span>
    </div>
    <div class="chat-input">
      <input type="text" id="chatInput" placeholder="Escribe a ZOE..." onkeypress="if(event.key==='Enter')sendMessage()">
      <button id="sendBtn" onclick="sendMessage()">Enviar</button>
    </div>
  </div>

  <!-- RIGHT PANEL: Thoughts + Federation -->
  <div class="panel panel-right">
    <div class="thoughts-header">&#128173; Pensamientos Autonomos</div>
    <div id="thoughts"></div>
  </div>
</div>

<input type="file" id="fileInput" style="display:none" onchange="uploadFile(event)">


</div>

<script>
// ZOE v2.1.2 -- Dashboard JS
// Sprint 5.21: Auth eliminada para localhost. No se necesita token.

let ws = null;
let isSleeping = false;

function connectWS() {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  // Sprint 5.12 -- anadir token al WS via query param

  ws = new WebSocket(proto + "//" + location.host + "/ws");

  ws.onopen = () => { console.log('WS connected'); };
  ws.onclose = () => { console.log('WS disconnected, retrying...'); setTimeout(connectWS, 2000); };
  ws.onerror = (e) => { console.error('WS error:', e); };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleMessage(data);
  };
}

function handleMessage(data) {
  if (data.type === 'chat_response') {
    const meta = data.acd_level
      ? ` <span class="acd-badge acd-${data.acd_level.toLowerCase()}">${data.acd_level}</span>`
        + `<span class="acd-meta">${data.latency_ms.toFixed(0)}ms${data.cache_hit ? ' &#128190;' : ''}</span>`
      : '';
    addMessage('zoe', data.content, data.timestamp, meta);
    // Sprint 5.24 F1v2-6 (BUG-013 UI): si hay mentor_intervention,
    // mostrarla como mensaje separado del tutor.
    if (data.mentor_intervention) {
      const mi = data.mentor_intervention;
      const miType = mi.type || 'guidance';
      const miSeverity = mi.severity || 'info';
      const miMsg = mi.message || mi.intervention || '';
      if (miMsg) {
        const miMeta = ` <span class="acd-badge acd-mentor" style="background:#fef3c7;color:#92400e;">&#127819; Mentor (${miType})</span>`;
        addMessage('mentor', miMsg, data.timestamp, miMeta);
      }
    }
    // ZOE v2.1.1 -- Ocultar indicador de pensando
    hideThinking();
    document.getElementById('sendBtn').disabled = false;
  } else if (data.type === 'mentor_intervention') {
    // Sprint 5.24 F1v2-6: mentor intervention autónoma (de _broadcast_loop)
    const miMsg = data.content || '';
    if (miMsg) {
      const miMeta = ` <span class="acd-badge acd-mentor" style="background:#fef3c7;color:#92400e;">&#127819; Mentor</span>`;
      addMessage('mentor', miMsg, data.timestamp, miMeta);
    }
  } else if (data.type === 'state_update') {
    updateState(data);
  } else if (data.type === 'autonomous_thought') {
    addThought(data);
  } else if (data.type === 'command_result') {
    addMessage('zoe', data.result, data.timestamp);
  } else if (data.type === 'capsule_loaded') {
    // Fase 6A: evento WS de capsula cargada
    if (data.success) {
      addMessage('zoe', `&#128230; Capsula '${data.capsule}' cargada: ${data.entries_loaded} entries. Componentes: ${(data.components_injected||[]).join(', ')}`, data.timestamp);
    } else {
      addMessage('zoe', `&#10007; Error cargando capsula '${data.capsule}': ${data.error}`, data.timestamp);
    }
    // Refrescar UI del modal si esta abierto
    if (document.getElementById('capsulesModal').style.display === 'flex') {
      loadCapsulesList();
      loadCapsulesLoaded();
    }
  } else if (data.type === 'capsule_unloaded') {
    if (data.success) {
      addMessage('zoe', `&#128230; Capsula '${data.capsule}' descargada.`, data.timestamp);
    } else {
      addMessage('zoe', `&#10007; Error descargando '${data.capsule}'`, data.timestamp);
    }
    if (document.getElementById('capsulesModal').style.display === 'flex') {
      loadCapsulesList();
      loadCapsulesLoaded();
    }
  } else if (data.type === 'capsules_state') {
    // Update state sin mostrar mensaje
    if (document.getElementById('capsulesModal').style.display === 'flex') {
      loadCapsulesLoaded();
    }
  }
}

function sendMessage() {
  const input = document.getElementById('chatInput');
  const msg = input.value.trim();
  if (!msg || !ws || ws.readyState !== 1) return;

  addMessage('user', msg, Date.now()/1000);
  // ZOE v2.1.1 -- Mostrar indicador de pensando
  showThinking();
  ws.send(JSON.stringify({ type: 'chat', message: msg }));
  input.value = '';
  document.getElementById('sendBtn').disabled = true;
}

// ZOE v2.1.1 -- Indicador de pensando
function showThinking() {
  const indicator = document.getElementById('thinkingIndicator');
  if (indicator) indicator.classList.add('active');
}
function hideThinking() {
  const indicator = document.getElementById('thinkingIndicator');
  if (indicator) indicator.classList.remove('active');
}

function addMessage(role, content, ts, meta) {
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  const time = new Date(ts * 1000).toLocaleTimeString();
  div.innerHTML = `${content}${meta || ''}<div class="ts">${time}</div>`;
  document.getElementById('chatMessages').appendChild(div);
  div.scrollIntoView({ behavior: 'smooth' });
}

function addThought(data) {
  const div = document.createElement('div');
  div.className = 'thought';
  const time = new Date(data.timestamp * 1000).toLocaleTimeString();
  const sys = data.system || 'system1';
  div.innerHTML = `${data.content}<div class="ts">${time}</div><div class="sys">${sys}</div>`;
  const container = document.getElementById('thoughts');
  container.insertBefore(div, container.firstChild);
  // Keep max 20
  while (container.children.length > 20) container.removeChild(container.lastChild);
}

function updateState(data) {
  document.getElementById('barEnergy').style.width = (data.energy * 100) + '%';
  document.getElementById('barFatigue').style.width = (data.fatigue * 100) + '%';
  document.getElementById('barArousal').style.width = (data.arousal * 100) + '%';
  document.getElementById('barAttention').style.width = (data.attention * 100) + '%';
  document.getElementById('iterText').textContent = `Iter: ${data.iterations}`;

  // Metabolism
  const dot = document.getElementById('metaDot');
  const text = document.getElementById('metaText');
  dot.className = 'meta-dot';
  if (data.metabolism === 'sleeping') { dot.classList.add('sleeping'); text.textContent = 'Sleeping'; isSleeping = true; }
  else if (data.metabolism === 'drowsy') { dot.classList.add('drowsy'); text.textContent = 'Drowsy'; }
  else { text.textContent = 'Awake'; isSleeping = false; }

  // Tensions
  if (data.tensions) {
    let html = '';
    for (const [name, t] of Object.entries(data.tensions)) {
      const pct = t.value * 100;
      const shortName = name.replace(/_/g, ' ').replace(/vs/g, '&harr;').substring(0, 20);
      html += `<div class="tension-item"><div class="tension-name">${shortName} (i=${t.intensity.toFixed(2)})</div><div class="state-bar"><div class="state-fill tension" style="width:${pct}%"></div></div></div>`;
    }
    document.getElementById('tensions').innerHTML = html;
  }
}

function switchLLM() {
  const sel = document.getElementById('llmSelect');
  const backend = sel.value;
  let model = null;
  if (backend === 'ollama') model = 'qwen2.5:3b';
  if (backend === 'zai') model = 'glm-4.6';

  fetch('/llm', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({backend, model}) })
    .then(r => r.json())
    .then(d => { if (d.status === 'switched') addMessage('zoe', `LLM cambiado a ${d.backend}${d.model ? ' ('+d.model+')' : ''}`, Date.now()/1000); })
    .catch(e => addMessage('zoe', `Error cambiando LLM: ${e}`, Date.now()/1000));
}

function feedFile() { document.getElementById('fileInput').click(); }

function uploadFile(event) {
  const file = event.target.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append('file', file);
  fetch('/feed', { method: 'POST', body: formData })
    .then(r => r.json())
    .then(d => { addMessage('zoe', `&#128218; He leido '${d.filename}' (${d.size} chars). Almacenado en memoria semantica.`, Date.now()/1000); })
    .catch(e => addMessage('zoe', `Error: ${e}`, Date.now()/1000));
  event.target.value = '';
}

function showStats() {
  fetch('/stats').then(r=>r.json()).then(d => {
    let txt = `&#128202; ESTADISTICAS\\nIteraciones: ${d.iterations}\\nPensamientos: ${d.thoughts}\\nSystem 1: ${d.system1_uses||0}\\nSystem 2: ${d.system2_uses||0}\\nWorkspace: ${d.workspace_competitions||0}\\nMemoria: ${d.memory_stats?.total_entries||0} entries\\nConsolidaciones: ${d.consolidation_cycles||0}`;
    addMessage('zoe', txt, Date.now()/1000);
  });
}

function showMemory() {
  fetch('/memory').then(r=>r.json()).then(d => {
    let txt = `&#129504; MEMORIA (${d.count} entries)\\n`;
    d.entries.slice(-5).forEach(e => { txt += `[${e.type}] ${e.content.substring(0,60)}...\\n`; });
    addMessage('zoe', txt, Date.now()/1000);
  });
}

function showIdentity() {
  fetch('/identity').then(r=>r.json()).then(d => {
    addMessage('zoe', `&#129655; IDENTIDAD\\nNombre: ${d.name}\\nHash: ${d.hash.substring(0,32)}...\\nVectores: ${d.vectors.length}\\nValores: ${d.values.length}\\nProposito: ${d.purpose.substring(0,80)}...`, Date.now()/1000);
  });
}

function showHistory() {
  fetch('/history').then(r=>r.json()).then(d => {
    let txt = `&#128220; HISTORIAL (${d.count} mensajes)\\n`;
    d.conversations.slice(-10).forEach(c => { txt += `[${c.role}] ${c.content.substring(0,50)}...\\n`; });
    addMessage('zoe', txt, Date.now()/1000);
  });
}

function toggleSleep() {
  if (isSleeping) { fetch('/wake', {method:'POST'}); }
  else { fetch('/sleep', {method:'POST'}); }
}

// ============================================================
// Fase 6A: Capsules UI
// ============================================================

function showCapsules() {
  document.getElementById('capsulesModal').style.display = 'flex';
  loadCapsulesList();
  loadCapsulesLoaded();
}

function hideCapsules() {
  document.getElementById('capsulesModal').style.display = 'none';
}

async function loadCapsulesList() {
  try {
    const r = await fetch('/api/capsules');
    const d = await r.json();
    const div = document.getElementById('capsulesAvailableList');
    if (!d.available || d.available.length === 0) {
      div.innerHTML = '<div style="color:#666;padding:10px">No hay capsulas disponibles</div>';
      return;
    }
    div.innerHTML = d.available.map(c => `
      <div class="cap-item">
        <div class="cap-info">
          <div class="cap-name">${c.name} <span class="cap-version">v${c.version}</span></div>
          <div class="cap-meta">
            <span class="cap-trust cap-trust-${c.trust_level}">${c.trust_level}</span>
            <span class="cap-domain">${c.domain}</span>
            ${c.is_loaded ? '<span class="cap-loaded">&#10003; cargada</span>' : ''}
          </div>
          <div class="cap-desc">${c.description || ''}</div>
        </div>
        <div class="cap-actions">
          ${c.is_loaded
            ? `<button class="cap-btn cap-btn-unload" onclick="unloadCapsule('${c.name}')">Descargar</button>`
            : `<button class="cap-btn cap-btn-load" onclick="loadCapsule('${c.name}')">Cargar</button>`
          }
          <button class="cap-btn cap-btn-info" onclick="capsuleInfo('${c.name}')">Info</button>
          <button class="cap-btn cap-btn-validate" onclick="validateCapsule('${c.name}')">Validar</button>
        </div>
      </div>
    `).join('');
  } catch (e) {
    console.error('loadCapsulesList error:', e);
  }
}

async function loadCapsulesLoaded() {
  try {
    const r = await fetch('/api/capsules/loaded');
    const d = await r.json();
    const div = document.getElementById('capsulesLoadedList');
    if (!d.loaded || d.loaded.length === 0) {
      div.innerHTML = '<div style="color:#666;padding:10px">Sin capsulas cargadas</div>';
      return;
    }
    div.innerHTML = d.loaded.map(c => `
      <div class="cap-item cap-loaded-item">
        <div class="cap-info">
          <div class="cap-name">${c.name} <span class="cap-version">v${c.version}</span></div>
          <div class="cap-meta">
            <span class="cap-trust cap-trust-${c.trust_level}">${c.trust_level}</span>
            <span class="cap-entries">${c.entries_injected} entries</span>
          </div>
          <div class="cap-desc">${c.description || ''}</div>
        </div>
        <div class="cap-actions">
          <button class="cap-btn cap-btn-unload" onclick="unloadCapsule('${c.name}')">Descargar</button>
        </div>
      </div>
    `).join('');
  } catch (e) {
    console.error('loadCapsulesLoaded error:', e);
  }
}

function loadCapsule(name) {
  // Fase 6A: usar WebSocket para que el evento se broadcastee a todos los clientes
  if (ws && ws.readyState === 1) {
    ws.send(JSON.stringify({ type: 'capsule_action', action: 'load', name: name }));
  } else {
    // Fallback a REST si WS no disponible
    fetch('/api/capsules/load', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name})
    }).then(r => r.json()).then(d => {
      if (d.success) {
        addMessage('zoe', `&#128230; Capsula '${name}' cargada: ${d.entries_loaded} entries inyectados.`, Date.now()/1000);
        loadCapsulesList();
        loadCapsulesLoaded();
      } else {
        addMessage('zoe', `&#10007; Error cargando '${name}': ${d.error}`, Date.now()/1000);
      }
    }).catch(e => console.error('loadCapsule error:', e));
  }
}

function unloadCapsule(name) {
  // Fase 6A: usar WebSocket para broadcast
  if (ws && ws.readyState === 1) {
    ws.send(JSON.stringify({ type: 'capsule_action', action: 'unload', name: name }));
  } else {
    // Fallback REST
    fetch('/api/capsules/unload', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name})
    }).then(r => r.json()).then(d => {
      if (d.success) {
        addMessage('zoe', `&#128230; Capsula '${name}' descargada.`, Date.now()/1000);
        loadCapsulesList();
        loadCapsulesLoaded();
      } else {
        addMessage('zoe', `&#10007; Error descargando '${name}'`, Date.now()/1000);
      }
    }).catch(e => console.error('unloadCapsule error:', e));
  }
}

async function capsuleInfo(name) {
  try {
    const r = await fetch(`/api/capsules/${name}/info`);
    const d = await r.json();
    alert(JSON.stringify(d, null, 2));
  } catch (e) {
    console.error('capsuleInfo error:', e);
  }
}

async function validateCapsule(name) {
  try {
    const r = await fetch(`/api/capsules/${name}/validate`, {method: 'POST'});
    const d = await r.json();

    let msg = `&#128230; Validacion de '${name}':\n\n`;
    msg += `Valido: ${d.valid ? '&#10003; SI' : '&#10007; NO'}\n\n`;

    if (d.checks && d.checks.length > 0) {
      msg += 'Checks:\\n';
      for (const c of d.checks) {
        const icon = c.status === 'pass' ? '&#10003;' : c.status === 'fail' ? '&#10007;' : c.status === 'skip' ? '&#9675;' : '&#9888;';
        msg += `  ${icon} ${c.name}: ${c.status}\n`;
      }
    }

    if (d.stats && Object.keys(d.stats).length > 0) {
      msg += '\\nEstadisticas:\\n';
      for (const [k, v] of Object.entries(d.stats)) {
        msg += `  ${k}: ${v}\n`;
      }
    }

    if (d.errors && d.errors.length > 0) {
      msg += '\\nErrores:\\n';
      for (const e of d.errors) msg += `  &#10007; ${e}\n`;
    }

    if (d.warnings && d.warnings.length > 0) {
      msg += '\\nAvisos:\\n';
      for (const w of d.warnings) msg += `  &#9888; ${w}\n`;
    }

    alert(msg);
  } catch (e) {
    console.error('validateCapsule error:', e);
    alert('Error: ' + e);
  }
}

async function createCapsule() {
  const name = document.getElementById('newCapName').value.trim();
  const domain = document.getElementById('newCapDomain').value.trim() || 'todo.domain';
  const trust = document.getElementById('newCapTrust').value;
  const desc = document.getElementById('newCapDesc').value.trim() || 'Capsula creada desde Dashboard';
  const components = document.getElementById('newCapComponents').value || 'semantic,validators';
  const useCases = document.getElementById('newCapUseCases').value.trim();

  if (!name) { alert('Nombre requerido'); return; }

  try {
    const r = await fetch('/api/capsules/create', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name, domain, trust_level: trust, description: desc, components, use_cases: useCases})
    });
    const d = await r.json();
    if (d.success) {
      addMessage('zoe', `&#128230; Capsula '${name}' creada. Edita los archivos en zoe/capsules/${name}/`, Date.now()/1000);
      document.getElementById('newCapName').value = '';
      document.getElementById('newCapDesc').value = '';
      loadCapsulesList();
    } else {
      alert('Error: ' + (d.error || 'desconocido'));
    }
  } catch (e) {
    console.error('createCapsule error:', e);
    alert('Error: ' + e);
  }
}

// ============================================================
// Fase 6B Punto 3: Cuarentena UI
// ============================================================

function showQuarantine() {
  document.getElementById('quarantineModal').style.display = 'flex';
  loadQuarantineData();
}

function hideQuarantine() {
  document.getElementById('quarantineModal').style.display = 'none';
}

async function loadQuarantineData() {
  try {
    const [listR, statsR] = await Promise.all([
      fetch('/api/quarantine'),
      fetch('/api/quarantine/stats'),
    ]);
    const listD = await listR.json();
    const statsD = await statsR.json();

    // Render stats
    const statsDiv = document.getElementById('quarantineStats');
    statsDiv.innerHTML = `
      <div class="q-stat"><span class="q-stat-num">${statsD.total || 0}</span><span class="q-stat-lbl">Total</span></div>
      <div class="q-stat"><span class="q-stat-num q-active">${statsD.active || 0}</span><span class="q-stat-lbl">Activas</span></div>
      <div class="q-stat"><span class="q-stat-num q-verified">${statsD.verified || 0}</span><span class="q-stat-lbl">Verificadas</span></div>
      <div class="q-stat"><span class="q-stat-num q-rejected">${statsD.rejected || 0}</span><span class="q-stat-lbl">Rechazadas</span></div>
      <div class="q-stat"><span class="q-stat-num q-expired">${statsD.expired || 0}</span><span class="q-stat-lbl">Expiradas</span></div>
    `;

    // Render active entries
    const activeDiv = document.getElementById('quarantineActive');
    if (!listD.active || listD.active.length === 0) {
      activeDiv.innerHTML = '<div style="color:#666;padding:10px">Sin entries en cuarentena activa.</div>';
    } else {
      activeDiv.innerHTML = listD.active.map(e => `
        <div class="q-item">
          <div class="q-info">
            <div class="q-claim">${e.claim ? e.claim.substring(0, 120) : '(sin claim)'}...</div>
            <div class="q-meta">
              <span class="q-domain">${e.domain || 'sin dominio'}</span>
              <span class="q-source">${e.source}</span>
              <span class="q-conf">conf=${(e.confidence || 0).toFixed(2)}</span>
              <span class="q-reason">${e.reason}</span>
            </div>
            <div class="q-confirm">Confirmaciones: ${e.confirmations ? e.confirmations.length : 0} &middot; Contradicciones: ${e.contradictions ? e.contradictions.length : 0}</div>
          </div>
          <div class="q-actions">
            <button class="q-btn q-btn-promote" onclick="promoteQuarantine('${e.entry_id}')">&#10003; Promover</button>
            <button class="q-btn q-btn-reject" onclick="rejectQuarantine('${e.entry_id}')">&#10007; Rechazar</button>
          </div>
        </div>
      `).join('');
    }

    // Render pending
    const pendingDiv = document.getElementById('quarantinePending');
    if (!listD.pending || listD.pending.length === 0) {
      pendingDiv.innerHTML = '<div style="color:#666;padding:10px">Sin entries pendientes de verificacion.</div>';
    } else {
      pendingDiv.innerHTML = `<div style="color:#888;padding:4px;font-size:11px;">${listD.pending.length} entries pendientes (incluye activas que aun no tienen suficientes verificaciones)</div>`;
    }
  } catch (e) {
    console.error('loadQuarantineData error:', e);
  }
}

async function promoteQuarantine(entryId) {
  try {
    const r = await fetch(`/api/quarantine/${entryId}/promote`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({confidence: 0.75}),
    });
    const d = await r.json();
    if (d.success) {
      addMessage('zoe', `&#128274; Entry '${entryId}' promovida (confianza=${d.entry.confidence}).`, Date.now()/1000);
      loadQuarantineData();
    } else {
      addMessage('zoe', `&#10007; Error promoviendo: ${d.error}`, Date.now()/1000);
    }
  } catch (e) {
    console.error('promoteQuarantine error:', e);
  }
}

async function rejectQuarantine(entryId) {
  try {
    const r = await fetch(`/api/quarantine/${entryId}/reject`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({source: 'dashboard_manual'}),
    });
    const d = await r.json();
    if (d.success) {
      addMessage('zoe', `&#128274; Entry '${entryId}' rechazada.`, Date.now()/1000);
      loadQuarantineData();
    } else {
      addMessage('zoe', `&#10007; Error rechazando: ${d.error}`, Date.now()/1000);
    }
  } catch (e) {
    console.error('rejectQuarantine error:', e);
  }
}

// ============================================================
// Fase 6B Punto 3: Marketplace UI
// ============================================================

function showMarketplace() {
  document.getElementById('marketplaceModal').style.display = 'flex';
  loadMarketplaceCapsules();
  loadMarketplaceUseCases();
}

function hideMarketplace() {
  document.getElementById('marketplaceModal').style.display = 'none';
}

async function loadMarketplaceCapsules() {
  try {
    const r = await fetch('/api/marketplace/capsules');
    const d = await r.json();
    const div = document.getElementById('marketplaceCapsulesList');

    if (!d.capsules || d.capsules.length === 0) {
      div.innerHTML = '<div style="color:#666;padding:10px">No hay capsulas en el marketplace todavia. !Se el primero en subir una!</div>';
      return;
    }

    div.innerHTML = d.capsules.map(c => `
      <div class="mp-item">
        <div class="mp-info">
          <div class="mp-name">${c.name} <span class="mp-version">v${c.version}</span></div>
          <div class="mp-meta">
            <span class="mp-license mp-license-${c.license.type}">${c.license.type}</span>
            ${c.license.price > 0 ? `<span class="mp-price">${c.license.price} ${c.license.currency}</span>` : ''}
            <span class="mp-author">por ${c.author}</span>
            <span class="mp-downloads">&#11015; ${c.downloads}</span>
            ${c.rating > 0 ? `<span class="mp-rating">&#9733; ${c.rating.toFixed(1)} (${c.rating_count})</span>` : ''}
          </div>
          <div class="mp-desc">${c.description || ''}</div>
          <div class="mp-tags">${(c.tags || []).map(t => `<span class="mp-tag">${t}</span>`).join('')}</div>
        </div>
        <div class="mp-actions">
          <button class="mp-btn mp-btn-download" onclick="downloadFromMarketplace('${c.name}')">&#11015; Instalar</button>
        </div>
      </div>
    `).join('');

    // Stats
    if (d.stats) {
      document.getElementById('marketplaceStats').innerHTML = `
        <span>Total: ${d.stats.total}</span> &middot; <span>Capsulas: ${d.stats.capsules}</span> &middot;
        <span>Casos: ${d.stats.use_cases}</span> &middot; <span>Downloads: ${d.stats.total_downloads}</span>
      `;
    }
  } catch (e) {
    console.error('loadMarketplaceCapsules error:', e);
  }
}

async function loadMarketplaceUseCases() {
  try {
    const r = await fetch('/api/marketplace/use_cases');
    const d = await r.json();
    const div = document.getElementById('marketplaceUseCasesList');

    if (!d.use_cases || d.use_cases.length === 0) {
      div.innerHTML = '<div style="color:#666;padding:10px">No hay casos de uso en el marketplace.</div>';
      return;
    }

    div.innerHTML = d.use_cases.map(c => `
      <div class="mp-item">
        <div class="mp-info">
          <div class="mp-name">${c.name}</div>
          <div class="mp-meta">
            <span class="mp-license mp-license-${c.license.type}">${c.license.type}</span>
            <span class="mp-author">por ${c.author}</span>
            <span class="mp-downloads">&#11015; ${c.downloads}</span>
          </div>
          <div class="mp-desc">${c.description || ''}</div>
        </div>
      </div>
    `).join('');
  } catch (e) {
    console.error('loadMarketplaceUseCases error:', e);
  }
}

async function downloadFromMarketplace(name) {
  try {
    const r = await fetch(`/api/marketplace/download/${name}`, {method: 'POST'});
    const d = await r.json();
    if (d.success) {
      addMessage('zoe', `&#127978; Capsula '${name}' instalada desde marketplace: ${d.message}`, Date.now()/1000);
      loadMarketplaceCapsules();
    } else {
      addMessage('zoe', `&#10007; Error descargando: ${d.message || d.error}`, Date.now()/1000);
    }
  } catch (e) {
    console.error('downloadFromMarketplace error:', e);
  }
}

async function uploadToMarketplace() {
  const name = document.getElementById('mpUploadName').value.trim();
  const author = document.getElementById('mpUploadAuthor').value.trim() || 'anonymous';
  const description = document.getElementById('mpUploadDesc').value.trim();
  const licenseType = document.getElementById('mpUploadLicense').value;
  const price = parseFloat(document.getElementById('mpUploadPrice').value) || 0;
  const tags = document.getElementById('mpUploadTags').value.trim().split(',').map(t => t.trim()).filter(t => t);

  if (!name) { alert('Nombre de capsula requerido'); return; }

  const licenseData = {type: licenseType};
  if (price > 0) { licenseData.price = price; licenseData.currency = 'EUR'; }
  if (licenseType === 'subscription') { licenseData.subscription_period = 'monthly'; }

  try {
    const r = await fetch('/api/marketplace/upload', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name, author, description, license: licenseData, tags}),
    });
    const d = await r.json();
    if (d.success) {
      addMessage('zoe', `&#127978; Capsula '${name}' subida al marketplace. Hash: ${d.content_hash.substring(0, 16)}...`, Date.now()/1000);
      document.getElementById('mpUploadName').value = '';
      document.getElementById('mpUploadDesc').value = '';
      document.getElementById('mpUploadTags').value = '';
      loadMarketplaceCapsules();
    } else {
      alert('Error: ' + (d.error || 'desconocido'));
    }
  } catch (e) {
    console.error('uploadToMarketplace error:', e);
    alert('Error: ' + e);
  }
}

async function uploadUseCaseToMarketplace() {
  const name = document.getElementById('mpUCName').value.trim();
  const author = document.getElementById('mpUCAuthor').value.trim() || 'anonymous';
  const description = document.getElementById('mpUCDesc').value.trim();
  const licenseType = document.getElementById('mpUCLicense').value;

  if (!name) { alert('Nombre de caso de uso requerido'); return; }

  try {
    const r = await fetch('/api/marketplace/upload_use_case', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name, author, description, license: {type: licenseType}}),
    });
    const d = await r.json();
    if (d.success) {
      addMessage('zoe', `&#127978; Caso de uso '${name}' subido al marketplace.`, Date.now()/1000);
      document.getElementById('mpUCName').value = '';
      document.getElementById('mpUCDesc').value = '';
      loadMarketplaceUseCases();
    } else {
      alert('Error: ' + (d.error || 'desconocido'));
    }
  } catch (e) {
    console.error('uploadUseCaseToMarketplace error:', e);
    alert('Error: ' + e);
  }
}

// Init
connectWS();
// Set initial LLM select
document.getElementById('llmSelect').value = 'mock';
</script>

<!-- Modal Capsulas (Fase 6A) -->
<div id="capsulesModal" class="capsules-modal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;align-items:center;justify-content:center;">
  <div class="capsules-modal-content" style="background:#0d0d14;border:1px solid #2a2a3a;border-radius:8px;width:90%;max-width:1100px;max-height:90vh;overflow-y:auto;padding:24px;color:#e0e0e0;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
      <h2 style="margin:0;font-size:20px;color:#866f2c;">&#128230; Capsulas de Conocimiento</h2>
      <button onclick="hideCapsules()" style="background:none;border:none;color:#888;font-size:24px;cursor:pointer;">&times;</button>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;">
      <div>
        <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Disponibles</h3>
        <div id="capsulesAvailableList" style="max-height:400px;overflow-y:auto;background:#0a0a12;border-radius:6px;padding:8px;"></div>
      </div>
      <div>
        <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Cargadas</h3>
        <div id="capsulesLoadedList" style="max-height:400px;overflow-y:auto;background:#0a0a12;border-radius:6px;padding:8px;"></div>
      </div>
    </div>

    <div style="border-top:1px solid #2a2a3a;padding-top:20px;">
      <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Crear nueva capsula</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
        <input id="newCapName" placeholder="Nombre (snake_case)" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <input id="newCapDomain" placeholder="dominio.subdominio" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <select id="newCapTrust" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
          <option value="curated">curated</option>
          <option value="verified">verified</option>
          <option value="community">community</option>
          <option value="experimental">experimental</option>
        </select>
        <input id="newCapComponents" placeholder="semantic,causal,validators" value="semantic,validators" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <input id="newCapUseCases" placeholder="caso1,caso2 (opcional)" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <input id="newCapDesc" placeholder="Descripcion breve" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
      </div>
      <button onclick="createCapsule()" style="margin-top:12px;background:#866f2c;color:white;border:none;padding:10px 20px;border-radius:4px;cursor:pointer;font-weight:600;">Crear capsula</button>
    </div>
  </div>
</div>

<style>
.cap-item { display:flex;justify-content:space-between;align-items:center;padding:10px;border-bottom:1px solid #1a1a24; }
.cap-info { flex:1; }
.cap-name { font-size:13px;font-weight:600;color:#e0e0e0; }
.cap-version { font-size:10px;color:#666;font-weight:normal; }
.cap-meta { font-size:10px;color:#888;margin-top:3px;display:flex;gap:8px;align-items:center; }
.cap-trust { padding:1px 6px;border-radius:3px;font-weight:600;font-size:9px;text-transform:uppercase; }
.cap-trust-verified { background:#1b5e20;color:#a5d6a7; }
.cap-trust-curated { background:#0d47a1;color:#90caf9; }
.cap-trust-community { background:#e65100;color:#ffcc80; }
.cap-trust-experimental { background:#4a148c;color:#ce93d8; }
.cap-domain { color:#666; }
.cap-loaded { color:#448158; }
.cap-desc { font-size:11px;color:#888;margin-top:4px; }
.cap-actions { display:flex;gap:6px; }
.cap-btn { background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:11px; }
.cap-btn:hover { background:#2a2a3a; }
.cap-btn-load { background:#1b5e20;border-color:#2e7d32;color:#a5d6a7; }
.cap-btn-unload { background:#4a148c;border-color:#6a1b9a;color:#ce93d8; }
.cap-btn-info { background:#0d47a1;border-color:#1565c0;color:#90caf9; }
.cap-btn-validate { background:#e65100;border-color:#ef6c00;color:#ffcc80; }

/* Cuarentena UI */
.q-stat { display:inline-block;text-align:center;margin:0 12px; }
.q-stat-num { display:block;font-size:24px;font-weight:700; }
.q-stat-lbl { font-size:10px;color:#888;text-transform:uppercase; }
.q-active { color:#ffcc80; }
.q-verified { color:#a5d6a7; }
.q-rejected { color:#ef9a9a; }
.q-expired { color:#888; }
.q-item { display:flex;justify-content:space-between;align-items:center;padding:10px;border-bottom:1px solid #1a1a24; }
.q-info { flex:1; }
.q-claim { font-size:12px;color:#e0e0e0;font-style:italic; }
.q-meta { font-size:10px;color:#888;margin-top:3px;display:flex;gap:8px;flex-wrap:wrap; }
.q-domain { background:#1a1a24;padding:1px 6px;border-radius:3px; }
.q-source { color:#90caf9; }
.q-conf { color:#ce93d8; }
.q-reason { color:#ef9a9a; }
.q-confirm { font-size:10px;color:#666;margin-top:3px; }
.q-actions { display:flex;gap:6px; }
.q-btn { border:none;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:11px;color:white; }
.q-btn-promote { background:#2e7d32; }
.q-btn-reject { background:#c62828; }

/* Marketplace UI */
.mp-item { display:flex;justify-content:space-between;align-items:center;padding:10px;border-bottom:1px solid #1a1a24; }
.mp-info { flex:1; }
.mp-name { font-size:13px;font-weight:600;color:#e0e0e0; }
.mp-version { font-size:10px;color:#666;font-weight:normal; }
.mp-meta { font-size:10px;color:#888;margin-top:3px;display:flex;gap:8px;align-items:center;flex-wrap:wrap; }
.mp-license { padding:1px 6px;border-radius:3px;font-weight:600;font-size:9px;text-transform:uppercase; }
.mp-license-free { background:#1b5e20;color:#a5d6a7; }
.mp-license-opensource { background:#0d47a1;color:#90caf9; }
.mp-license-research { background:#4a148c;color:#ce93d8; }
.mp-license-paid { background:#e65100;color:#ffcc80; }
.mp-license-subscription { background:#bf360c;color:#ffab91; }
.mp-price { color:#ffcc80;font-weight:600; }
.mp-author { color:#90caf9; }
.mp-downloads { color:#888; }
.mp-rating { color:#ffd54f; }
.mp-desc { font-size:11px;color:#888;margin-top:4px; }
.mp-tags { margin-top:4px; }
.mp-tag { display:inline-block;background:#1a1a24;color:#aaa;padding:1px 6px;border-radius:3px;font-size:9px;margin-right:4px; }
.mp-actions { display:flex;gap:6px; }
.mp-btn { border:none;padding:6px 12px;border-radius:4px;cursor:pointer;font-size:11px;color:white; }
.mp-btn-download { background:#1565c0; }
</style>

<!-- Modal Cuarentena (Fase 6B) -->
<div id="quarantineModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;align-items:center;justify-content:center;">
  <div style="background:#0d0d14;border:1px solid #2a2a3a;border-radius:8px;width:90%;max-width:900px;max-height:90vh;overflow-y:auto;padding:24px;color:#e0e0e0;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
      <h2 style="margin:0;font-size:20px;color:#866f2c;">&#128274; Conocimiento en Cuarentena</h2>
      <button onclick="hideQuarantine()" style="background:none;border:none;color:#888;font-size:24px;cursor:pointer;">&times;</button>
    </div>

    <div id="quarantineStats" style="text-align:center;margin-bottom:20px;padding:16px;background:#0a0a12;border-radius:6px;"></div>

    <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Entradas Activas</h3>
    <div id="quarantineActive" style="max-height:350px;overflow-y:auto;background:#0a0a12;border-radius:6px;padding:8px;margin-bottom:16px;"></div>

    <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Pendientes</h3>
    <div id="quarantinePending" style="background:#0a0a12;border-radius:6px;padding:8px;"></div>
  </div>
</div>

<!-- Modal Marketplace (Fase 6B) -->
<div id="marketplaceModal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:1000;align-items:center;justify-content:center;">
  <div style="background:#0d0d14;border:1px solid #2a2a3a;border-radius:8px;width:90%;max-width:1100px;max-height:90vh;overflow-y:auto;padding:24px;color:#e0e0e0;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
      <h2 style="margin:0;font-size:20px;color:#866f2c;">&#127978; Marketplace</h2>
      <button onclick="hideMarketplace()" style="background:none;border:none;color:#888;font-size:24px;cursor:pointer;">&times;</button>
    </div>

    <div id="marketplaceStats" style="font-size:11px;color:#888;margin-bottom:16px;padding:8px;background:#0a0a12;border-radius:4px;"></div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;">
      <div>
        <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Capsulas Disponibles</h3>
        <div id="marketplaceCapsulesList" style="max-height:300px;overflow-y:auto;background:#0a0a12;border-radius:6px;padding:8px;"></div>
      </div>
      <div>
        <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Casos de Uso Disponibles</h3>
        <div id="marketplaceUseCasesList" style="max-height:300px;overflow-y:auto;background:#0a0a12;border-radius:6px;padding:8px;"></div>
      </div>
    </div>

    <div style="border-top:1px solid #2a2a3a;padding-top:20px;">
      <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Subir Capsula al Marketplace</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px;">
        <input id="mpUploadName" placeholder="Nombre capsula" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <input id="mpUploadAuthor" placeholder="Autor" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <select id="mpUploadLicense" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
          <option value="free">Free</option>
          <option value="opensource">Open Source</option>
          <option value="research">Research</option>
          <option value="paid">Paid</option>
          <option value="subscription">Subscription</option>
        </select>
        <input id="mpUploadPrice" type="number" placeholder="Precio EUR (si paid/sub)" value="0" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <input id="mpUploadTags" placeholder="tags, separados, por coma" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <input id="mpUploadDesc" placeholder="Descripcion" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
      </div>
      <button onclick="uploadToMarketplace()" style="background:#866f2c;color:white;border:none;padding:10px 20px;border-radius:4px;cursor:pointer;font-weight:600;">Subir capsula</button>
    </div>

    <div style="border-top:1px solid #2a2a3a;padding-top:20px;margin-top:16px;">
      <h3 style="font-size:14px;color:#857648;margin-bottom:10px;text-transform:uppercase;letter-spacing:1px;">Subir Caso de Uso al Marketplace</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px;">
        <input id="mpUCName" placeholder="Nombre caso (sin .yaml)" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <input id="mpUCAuthor" placeholder="Autor" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
        <select id="mpUCLicense" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;">
          <option value="free">Free</option>
          <option value="opensource">Open Source</option>
          <option value="research">Research</option>
          <option value="paid">Paid</option>
        </select>
        <input id="mpUCDesc" placeholder="Descripcion" style="background:#1a1a24;border:1px solid #2a2a3a;color:#e0e0e0;padding:8px;border-radius:4px;grid-column:span 3;">
      </div>
      <button onclick="uploadUseCaseToMarketplace()" style="background:#866f2c;color:white;border:none;padding:10px 20px;border-radius:4px;cursor:pointer;font-weight:600;">Subir caso de uso</button>
    </div>
  </div>
</div>
</body>
</html>'''
