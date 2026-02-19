#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera o frontend completo do ImbalanceChart v7 - MT5 Engine Edition
"""

import os

def create_file(path, content):
    """Cria arquivo com conteúdo"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ {path}")

# ============================================================================
# INDEX.HTML - Frontend Completo
# ============================================================================

index_html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ImbalanceChart v7 — MT5 Engine Edition</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --bg: #0a0e17;
    --bg-panel: #111827;
    --bg-card: #0d1321;
    --border: #1e293b;
    --border-active: #334155;
    --text: #94a3b8;
    --text-strong: #e2e8f0;
    --text-dim: #475569;
    --bull: #00e676;
    --bear: #ff1744;
    --highlight: #ffd740;
    --accent: #ff6b35;
    --grid: #1e293b;
    --grid-strong: #334155;
    --crosshair: #64748b;
    --absorption-buy: #00e676;
    --absorption-sell: #ff5252;
  }

  body {
    font-family: 'JetBrains Mono', monospace;
    background: var(--bg);
    color: var(--text);
    overflow: hidden;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }

  /* ===== HEADER ===== */
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 12px;
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
  }
  .header-left { display: flex; align-items: center; gap: 12px; }
  .header h1 {
    font-size: 14px;
    font-weight: 600;
    color: var(--bull);
    letter-spacing: -0.3px;
  }
  .header h1 span { color: var(--accent); }

  .status-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 0.5px;
  }
  .status-badge.connected { background: #22c55e15; border: 1px solid #22c55e44; color: var(--bull); }
  .status-badge.disconnected { background: #ef444415; border: 1px solid #ef444444; color: var(--bear); }
  .status-badge.binance { background: #f59e0b15; border: 1px solid #f59e0b44; color: var(--highlight); }

  .price-display {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-strong);
    font-variant-numeric: tabular-nums;
  }
  .price-display.up { color: var(--bull); }
  .price-display.down { color: var(--bear); }

  /* ===== CONTROLS BAR ===== */
  .controls {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 12px;
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
    flex-wrap: wrap;
  }
  .ctrl-group {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .ctrl-label {
    font-size: 9px;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .ctrl-value {
    font-size: 11px;
    color: var(--highlight);
    font-weight: 600;
    min-width: 45px;
  }
  input[type="range"] {
    width: 90px;
    height: 3px;
    accent-color: var(--highlight);
    cursor: pointer;
  }
  .btn {
    padding: 3px 10px;
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 3px;
    color: var(--text);
    font-family: inherit;
    font-size: 10px;
    cursor: pointer;
    transition: all 0.15s;
  }
  .btn:hover { border-color: var(--highlight); color: var(--text-strong); }
  .btn.active { background: var(--highlight); color: var(--bg); border-color: var(--highlight); }
  .btn.live { background: var(--bull); color: #fff; border-color: var(--bull); font-weight: 700; }
  .btn.live.stopped { background: var(--bear); border-color: var(--bear); }
  .btn.accent { background: var(--accent); color: #fff; border-color: var(--accent); }

  /* ===== ENGINE PANEL ===== */
  .engine-panel {
    display: none;
    padding: 6px 12px;
    background: var(--bg-card);
    border-bottom: 1px solid #ff6b3533;
    flex-shrink: 0;
  }
  .engine-panel.visible { display: block; }
  .engine-panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
  }
  .engine-panel-header span {
    font-size: 10px;
    font-weight: 600;
    color: var(--accent);
  }
  .engine-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 6px;
  }
  .engine-card {
    background: var(--bg);
    border-radius: 4px;
    padding: 6px 8px;
    border: 1px solid var(--border);
  }
  .engine-card-title {
    font-size: 8px;
    color: var(--highlight);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 3px;
  }
  .engine-card-value {
    font-size: 11px;
    color: var(--text-strong);
    display: flex;
    gap: 8px;
    align-items: center;
  }
  .engine-card-value .dim { color: var(--text-dim); font-size: 9px; }
  .engine-card-value .bull { color: var(--absorption-buy); }
  .engine-card-value .bear { color: var(--absorption-sell); }
  .engine-card-value .burst { color: var(--accent); font-weight: 700; }

  /* ===== FORMING CLUSTER STATUS ===== */
  .forming-bar {
    display: none;
    padding: 4px 12px;
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
    align-items: center;
    gap: 12px;
    font-size: 10px;
  }
  .forming-bar.visible { display: flex; }
  .delta-bar-bg {
    width: 80px;
    height: 4px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
  }
  .delta-bar-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.1s;
  }

  /* ===== CHART AREA ===== */
  .chart-container {
    flex: 1;
    position: relative;
    overflow: hidden;
    min-height: 0;
  }
  #chart {
    display: block;
    cursor: crosshair;
  }

  /* ===== LEGEND OVERLAY ===== */
  .legend {
    position: absolute;
    bottom: 8px;
    left: 8px;
    display: flex;
    gap: 10px;
    font-size: 8px;
    opacity: 0.6;
    pointer-events: none;
  }
  .legend-item { display: flex; align-items: center; gap: 3px; }
  .legend-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <div class="header-left">
    <h1>📊 Imbalance Chart <span>v7</span> — MT5 Engine Edition</h1>
    <span class="status-badge disconnected" id="wsStatus">⬤ DESCONECTADO</span>
    <span class="status-badge binance" id="binanceStatus" style="display:none">⬤ BINANCE</span>
  </div>
  <div style="display:flex;align-items:center;gap:12px;">
    <span class="price-display" id="priceDisplay">--</span>
    <span style="font-size:10px;color:var(--text-dim)" id="tickCounter">0 ticks</span>
  </div>
</div>

<!-- CONTROLS -->
<div class="controls">
  <div class="ctrl-group">
    <span class="ctrl-label">Símbolo</span>
    <select id="symbolSelect" onchange="switchSymbol(this.value)" style="background:var(--bg);color:var(--text-strong);border:1px solid var(--border);border-radius:3px;padding:2px 6px;font-family:inherit;font-size:10px;">
      <option value="XAUUSD" selected>XAU/USD</option>
      <option value="BTCUSD">BTC/USD</option>
      <option value="USTEC">USTEC</option>
      <option value="EURUSD">EUR/USD</option>
      <option value="GBPUSD">GBP/USD</option>
    </select>
  </div>
  <div class="ctrl-group">
    <span class="ctrl-label">Δ Threshold</span>
    <input type="range" id="thresholdSlider" min="10" max="5000" value="100" step="10">
    <span class="ctrl-value" id="thresholdValue">100</span>
  </div>
  <div class="ctrl-group">
    <span class="ctrl-label">Price Step</span>
    <input type="range" id="stepSlider" min="0" max="100" value="5" step="1">
    <span class="ctrl-value" id="stepValue">$0.50</span>
  </div>
  <div class="ctrl-group">
    <span class="ctrl-label">Modo</span>
    <button class="btn active" data-mode="hybrid" onclick="setViewMode('hybrid')">Hybrid</button>
    <button class="btn" data-mode="clean" onclick="setViewMode('clean')">Clean</button>
    <button class="btn" data-mode="raw" onclick="setViewMode('raw')">Raw</button>
  </div>
  <div class="ctrl-group">
    <span class="ctrl-label">Hist</span>
    <button class="btn" onclick="loadHistory(1)">1h</button>
    <button class="btn" onclick="loadHistory(4)">4h</button>
    <button class="btn" onclick="loadHistory(12)">12h</button>
    <button class="btn" onclick="loadHistory(24)">24h</button>
    <button class="btn" onclick="loadHistory(240)" style="color:#ff6b35">10d</button>
  </div>
  <div class="ctrl-group">
    <span class="ctrl-label">⚖️ Peso</span>
    <select id="weightSelect" onchange="setWeightMode(this.value)" style="background:var(--bg);color:var(--highlight);border:1px solid var(--border);border-radius:3px;padding:2px 6px;font-family:inherit;font-size:9px;">
      <option value="price_weighted" selected>Preço</option>
      <option value="spread_weighted">Spread</option>
      <option value="equal">Igual</option>
    </select>
  </div>
  <div class="ctrl-group">
    <button class="btn accent" id="engineToggle" onclick="toggleEnginePanel()">🔥 Engines</button>
    <button class="btn" id="calibToggle" onclick="toggleCalibration()" style="border-color:#9c27b0;color:#ce93d8">⚙️ Config</button>
  </div>
  <div class="ctrl-group">
    <span class="ctrl-label">✏️ Desenho</span>
    <button class="btn" data-draw="hline" onclick="setDrawTool('hline')">— H</button>
    <button class="btn" data-draw="vline" onclick="setDrawTool('vline')">| V</button>
    <button class="btn" data-draw="rect" onclick="setDrawTool('rect')">▭</button>
    <button class="btn" data-draw="trend" onclick="setDrawTool('trend')">↗</button>
    <button class="btn" onclick="setDrawTool('none')" style="color:var(--text-dim)">✕</button>
    <button class="btn" onclick="clearDrawings()" style="color:var(--bear)">🗑</button>
    <button class="btn live" id="liveBtn" onclick="toggleLive()">▶ LIVE</button>
    <button class="btn" onclick="findClusters()" style="color:#00bcd4;border-color:#00bcd444" title="Encontrar clusters no gráfico">🔍 Achar</button>
    <button class="btn" onclick="resetChart()">↺ Reset</button>
  </div>
  <div class="ctrl-group" style="margin-left:auto">
    <span class="ctrl-label">Clusters:</span>
    <span class="ctrl-value" id="clusterCount" style="color:var(--text-strong)">0</span>
    <span style="font-size:9px;color:var(--text-dim);margin-left:4px" id="sourceLabel">--</span>
  </div>
</div>

<!-- ENGINE PANEL -->
<div class="engine-panel" id="enginePanel">
  <div class="engine-panel-header">
    <span>🔥 Engine Analysis — Real-time</span>
    <span style="font-size:9px;color:var(--text-dim)">Fonte: MT5 Exness | <span id="engineSourceLabel">--</span></span>
  </div>
  <div class="engine-grid">
    <div class="engine-card">
      <div class="engine-card-title">⚡ Tick Velocity</div>
      <div class="engine-card-value">
        <span id="eng_velocity">-- t/s</span>
        <span class="dim">base: <span id="eng_velocity_base">--</span></span>
        <span class="burst" id="eng_burst" style="display:none">🔥 BURST</span>
      </div>
    </div>
    <div class="engine-card">
      <div class="engine-card-title">🧩 Micro Absorção</div>
      <div class="engine-card-value">
        <span id="eng_absorption">Sem absorção</span>
        <span class="dim">Total: <span id="eng_abs_total">0</span></span>
      </div>
    </div>
    <div class="engine-card">
      <div class="engine-card-title">📊 ATR (5s Candles)</div>
      <div class="engine-card-value">
        <span id="eng_atr">--</span>
        <span id="eng_atr_regime" class="dim">warmup</span>
      </div>
    </div>
    <div class="engine-card">
      <div class="engine-card-title">🔥 Imbalance Stacking</div>
      <div class="engine-card-value">
        <span class="bull" id="eng_stack_buy">Buy: S0</span>
        <span class="bear" id="eng_stack_sell">Sell: S0</span>
        <span id="eng_dominant" style="font-weight:700"></span>
      </div>
    </div>
    <div class="engine-card">
      <div class="engine-card-title">📉 Volatilidade</div>
      <div class="engine-card-value">
        <span id="eng_vol">-- bps</span>
        <span id="eng_vol_regime" class="dim">--</span>
      </div>
    </div>
    <div class="engine-card">
      <div class="engine-card-title">📡 Sinal Composto</div>
      <div class="engine-card-value">
        <span id="eng_signal" style="font-size:14px;font-weight:700">0%</span>
        <span class="dim" id="eng_signal_label">neutro</span>
      </div>
    </div>
  </div>
</div>

<!-- CALIBRATION PANEL -->
<div class="engine-panel" id="calibPanel" style="border-color:#9c27b044">
  <div class="engine-panel-header">
    <span style="color:#ce93d8">⚙️ Configuração Visual + Calibragem</span>
    <span style="font-size:9px;color:var(--text-dim)">Cores, opacidade, engines</span>
  </div>
  <div class="engine-grid" style="grid-template-columns:repeat(auto-fit, minmax(200px, 1fr))">
    <!-- CORES DO CLUSTER -->
    <div class="engine-card" style="border-color:#26a69a44">
      <div class="engine-card-title" style="color:#26a69a">🎨 Cluster</div>
      <div style="display:flex;flex-direction:column;gap:4px">
        <div class="ctrl-group" style="gap:4px"><span class="ctrl-label" style="min-width:60px">Bull</span>
          <input type="color" value="#00e676" onchange="setColor('bull',this.value);setColor('bullBody',this.value);setColor('histogramBullColor',this.value)" style="width:24px;height:18px;border:0;cursor:pointer"></div>
        <div class="ctrl-group" style="gap:4px"><span class="ctrl-label" style="min-width:60px">Bear</span>
          <input type="color" value="#ff1744" onchange="setColor('bear',this.value);setColor('bearBody',this.value);setColor('histogramBearColor',this.value)" style="width:24px;height:18px;border:0;cursor:pointer"></div>
        <div class="ctrl-group" style="gap:4px"><span class="ctrl-label" style="min-width:60px">Opacidade</span>
          <input type="range" min="10" max="100" value="70" step="5" oninput="CONFIG.clusterOpacity=+this.value;this.nextElementSibling.textContent=this.value+'%';render()" style="width:80px">
          <span class="ctrl-value">70%</span></div>
        <div class="ctrl-group" style="gap:4px"><span class="ctrl-label" style="min-width:60px">Borda</span>
          <input type="range" min="0" max="4" value="1.5" step="0.5" oninput="CONFIG.clusterBorderWidth=+this.value;render()" style="width:60px">
          <input type="color" value="#ffffff" onchange="setColor('clusterBorderColor',this.value)" style="width:20px;height:16px;border:0;cursor:pointer"></div>
        <div class="ctrl-group" style="gap:4px"><span class="ctrl-label" style="min-width:60px">Wick</span>
          <input type="color" value="#556677" onchange="setColor('wickColor',this.value)" style="width:24px;height:18px;border:0;cursor:pointer"></div>
      </div>
    </div>
    <!-- POC + PREÇO -->
    <div class="engine-card" style="border-color:#ffd74044">
      <div class="engine-card-title" style="color:#ffd740">📍 POC & Preço</div>
      <div style="display:flex;flex-direction:column;gap:4px">
        <div class="ctrl-group" style="gap:4px"><span class="ctrl-label" style="min-width:60px">POC Cor</span>
          <input type="color" value="#ffd740" onchange="setColor('pocColor',this.value)" style="width:24px;height:18px;border:0;cursor:pointer"></div>
        <div class="ctrl-group" style="gap:4px"><span class="ctrl-label" style="min-width:60px">POC Linha</span>
          <input type="range" min="1" max="6" value="3" step="0.5" oninput="CONFIG.pocLineWidth=+this.value;render()" style="width:80px"></div>
        <div class="ctrl-group" style="gap:4px"><span class="ctrl-label" style="min-width:60px">Preço</span>
          <input type="color" value="#00bcd4" onchange="setColor('currentPriceColor',this.value)" style="width:24px;height:18px;border:0;cursor:pointer"></div>
        <div class="ctrl-group" style="gap:4px"><span class="ctrl-label" style="min-width:60px">Hist Opac</span>
          <input type="range" min="10" max="100" value="85" step="5" oninput="CONFIG.histogramOpacity=+this.value;this.nextElementSibling.textContent=this.value+'%';render()" style="width:80px">
          <span class="ctrl-value">85%</span></div>
      </div>
    </div>
    <!-- MARKERS -->
    <div class="engine-card" style="border-color:#ff00ff44">
      <div class="engine-card-title" style="color:#ff69b4">◉ Markers</div>
      <div style="display:flex;flex-direction:column;gap:4px">
        <div class="ctrl-group" style="gap:4px"><span class="ctrl-label" style="min-width:60px">Absorção</span>
          <input type="color" value="#00e676" onchange="setColor('absorptionBuy',this.value)" style="width:20px;height:16px;border:0;cursor:pointer" title="Buy">
          <input type="color" value="#ff5252" onchange="setColor('absorptionSell',this.value)" style="width:20px;height:16px;border:0;cursor:pointer" title="Sell">
          <label style="font-size:8px;color:var(--text-dim)"><input type="checkbox" checked onchange="CONFIG.showAbsorptionLevels=this.checked;render()"> Nível</label></div>
        <div class="ctrl-group" style="gap:4px"><span class="ctrl-label" style="min-width:60px">Imbalance</span>
          <input type="color" value="#ff00ff" onchange="setColor('imbalanceMarkerColor',this.value)" style="width:24px;height:18px;border:0;cursor:pointer">
          <label style="font-size:8px;color:var(--text-dim)"><input type="checkbox" checked onchange="CONFIG.showImbalanceLevels=this.checked;render()"> Nível</label></div>
        <div class="ctrl-group" style="gap:4px"><span class="ctrl-label" style="min-width:60px">Wick %</span>
          <input type="range" min="20" max="90" value="50" step="5" oninput="CONFIG.wickWarningThreshold=+this.value;this.nextElementSibling.textContent=this.value+'%';render()" style="width:80px">
          <span class="ctrl-value">50%</span></div>
      </div>
    </div>
    <!-- DESENHO -->
    <div class="engine-card" style="border-color:#ffd74044">
      <div class="engine-card-title" style="color:#ffd740">✏️ Desenho</div>
      <div style="display:flex;flex-direction:column;gap:4px">
        <div class="ctrl-group" style="gap:4px"><span class="ctrl-label" style="min-width:60px">Cor</span>
          <input type="color" value="#ffd740" id="drawColorPicker" onchange="CONFIG.drawColor=this.value" style="width:24px;height:18px;border:0;cursor:pointer"></div>
        <div class="ctrl-group" style="gap:4px"><span class="ctrl-label" style="min-width:60px">Opacidade</span>
          <input type="range" min="20" max="100" value="80" step="5" oninput="CONFIG.drawOpacity=+this.value;this.nextElementSibling.textContent=this.value+'%'" style="width:80px">
          <span class="ctrl-value">80%</span></div>
        <div class="ctrl-group" style="gap:4px"><span class="ctrl-label" style="min-width:60px">Espessura</span>
          <input type="range" min="0.5" max="5" value="1.5" step="0.5" oninput="CONFIG.drawLineWidth=+this.value" style="width:80px"></div>
      </div>
    </div>
  </div>
</div>

<!-- FORMING CLUSTER STATUS -->
<div class="forming-bar" id="formingBar">
  <span style="color:var(--highlight)">🔄 Formando</span>
  <span>Δ: <strong id="formingDelta" style="font-variant-numeric:tabular-nums">0</strong></span>
  <span style="color:var(--text-dim)">Body: <span id="formingBody">0%</span> | Wick: <span id="formingWick">0%</span></span>
  <span id="formingAbsorptions" style="color:var(--accent);display:none"></span>
  <span id="formingStacking" style="display:none"></span>
  <div class="delta-bar-bg">
    <div class="delta-bar-fill" id="deltaBarFill"></div>
  </div>
</div>

<!-- CHART -->
<div class="chart-container" id="chartContainer">
  <canvas id="chart"></canvas>
  <div class="legend">
    <div class="legend-item"><div class="legend-dot" style="background:var(--absorption-buy)"></div> Buy Absorção</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--absorption-sell)"></div> Sell Absorção</div>
    <div class="legend-item"><div class="legend-dot" style="background:var(--highlight)"></div> Wick >50%</div>
  </div>
</div>

<script src="js/app.js"></script>
</body>
</html>'''

# ============================================================================
# APP.JS - Lógica completa do ImbalanceChart
# ============================================================================

app_js = '''/**
 * ImbalanceChart v7 - MT5 Engine Edition
 * Frontend completo com gráfico atemporal
 */

const WS_URL = 'ws://localhost:8766';
const PRICE_WIDTH = 80;

// Configurações visuais
let CONFIG = {
  bg: '#0a0e17',
  bgPanel: '#111827',
  bull: '#00e676',
  bear: '#ff1744',
  bullDark: '#004d40',
  bearDark: '#4a0000',
  bullBody: '#00c853',
  bearBody: '#d50000',
  highlight: '#ffd740',
  accent: '#ff6b35',
  grid: '#1a2332',
  gridStrong: '#2a3a4d',
  text: '#8899aa',
  textStrong: '#e2e8f0',
  crosshair: '#546e7a',
  absorptionBuy: '#00e676',
  absorptionSell: '#ff5252',
  clusterGap: 4,
  histogramBullColor: '#00e676',
  histogramBearColor: '#ff1744',
  histogramOpacity: 85,
  wickWarningThreshold: 50,
  pocColor: '#ffd740',
  currentPriceColor: '#00bcd4',
  clusterOpacity: 70,
  clusterBorderWidth: 1.5,
  clusterBorderColor: '#ffffff',
  showClusterBorder: true,
  wickColor: '#556677',
  wickWidth: 1,
  pocLineWidth: 3,
  showPOC: true,
  showCurrentPrice: true,
  showVolumeLabels: true,
  showWickWarning: true,
  showAbsorptionLevels: true,
  showImbalanceLevels: true,
  absorptionMarkerColor: '#ffff00',
  imbalanceMarkerColor: '#ff00ff',
  drawColor: '#ffd740',
  drawOpacity: 80,
  drawLineWidth: 1.5,
};

// Estado global
let ws = null;
let isLive = false;
let clusters = [];
let threshold = 100;
let priceStep = 0.50;
let viewMode = 'hybrid';
let showEnginePanel = true;
let showCalibration = false;
let lastPrice = 0;
let lastSide = 'buy';
let totalTicks = 0;
let engineState = {};
let dataSource = 'searching';
let currentSymbol = 'XAUUSD';
let weightMode = 'price_weighted';
let HISTOGRAM_RATIO = 0.25;
let HIST_SPLIT = 0.55;

// Configurações de símbolos
const SYMBOLS = {
  'BTCUSD':  { label: 'BTC/USD',  dig: 2, delta_th: 200, step: 10.0 },
  'XAUUSD':  { label: 'XAU/USD',  dig: 2, delta_th: 100,  step: 0.50 },
  'EURUSD':  { label: 'EUR/USD',  dig: 5, delta_th: 50,   step: 0.0001 },
  'GBPUSD':  { label: 'GBP/USD',  dig: 5, delta_th: 60,   step: 0.0001 },
  'USTEC':   { label: 'USTEC',    dig: 2, delta_th: 150,  step: 1.0 },
};

// Clusters
let closedClusters = [];
let formingCluster = null;
let formingTicks = [];
let masterTicks = [];

// View state
let viewState = {
  offsetX: 0,
  offsetY: 0,
  scaleX: 1,
  scaleY: 1,
  isDragging: false,
  lastX: 0,
  lastY: 0,
};

// Crosshair
let crosshair = { x: 0, y: 0, visible: false };

// Drawing tools
let drawTool = 'none';
let drawings = [];
let currentDrawing = null;
let selectedDrawing = null;
let nextDrawId = 1;

// Canvas
let canvas, ctx;
let chartW, chartH, histH, totalH;

// Inicialização
function init() {
  canvas = document.getElementById('chart');
  ctx = canvas.getContext('2d');
  resize();
  window.addEventListener('resize', resize);
  setupCanvasEvents();
  setupControls();
  render();
  toggleLive();
}

function resize() {
  const container = document.getElementById('chartContainer');
  const w = container.clientWidth;
  const h = container.clientHeight;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = w * dpr;
  canvas.height = h * dpr;
  canvas.style.width = w + 'px';
  canvas.style.height = h + 'px';
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  totalH = h;
  histH = Math.floor(h * HISTOGRAM_RATIO);
  chartH = h - histH;
  chartW = w - PRICE_WIDTH;
  render();
}

// WebSocket
function connectWS() {
  if (ws && ws.readyState <= 1) return;
  ws = new WebSocket(WS_URL);

  ws.onopen = () => {
    document.getElementById('wsStatus').className = 'status-badge connected';
    document.getElementById('wsStatus').textContent = '⬤ WS CONECTADO';
    ws.send(JSON.stringify({ type: 'switch_symbol', symbol: currentSymbol }));
    ws.send(JSON.stringify({ action: 'get_history', symbol: currentSymbol, hours: 24 }));
  };

  ws.onmessage = (e) => {
    try {
      const msg = JSON.parse(e.data);
      if (msg.type === 'tick') {
        processTick(msg.data);
      } else if (msg.type === 'connected') {
        const src = msg.data?.source || 'unknown';
        dataSource = src;
        const badge = document.getElementById('binanceStatus');
        if (src === 'mt5') {
          badge.style.display = 'inline-flex';
          badge.textContent = '⬤ MT5 EXNESS';
          badge.className = 'status-badge connected';
        } else {
          badge.style.display = 'inline-flex';
          badge.textContent = '⬤ SIMULAÇÃO';
          badge.className = 'status-badge disconnected';
        }
        document.getElementById('sourceLabel').textContent = src.toUpperCase();
      } else if (msg.type === 'history') {
        if (msg.ticks && msg.ticks.length > 0) {
          const sym = msg.symbol || currentSymbol;
          const cfg = SYMBOLS[sym];
          if (cfg) {
            currentSymbol = sym;
            threshold = cfg.delta_th;
            priceStep = cfg.step;
            document.getElementById('thresholdSlider').value = threshold;
            document.getElementById('thresholdValue').textContent = threshold >= 1000 ? (threshold/1000)+'k' : threshold;
          }
          const histTicks = msg.ticks.map(t => ({
            price: t.price,
            volume: Math.round(t.volume_synthetic || 1),
            side: t.side || 'buy',
            timestamp: t.timestamp || Date.now(),
            is_absorption: false,
            absorption_type: null,
            absorption_strength: 0,
            composite_signal: 0,
            stacking_buy: 0,
            stacking_sell: 0,
          }));
          fullReprocess(histTicks);
          totalTicks = histTicks.length;
          autoFitView();
          document.getElementById('sourceLabel').textContent = msg.count + ' ticks (' + (msg.hours||'?') + 'h)';
          render();
        }
      } else if (msg.type === 'symbol_changed') {
        if (msg.config) {
          document.getElementById('sourceLabel').textContent = msg.symbol;
        }
      }
    } catch(err) {}
  };

  ws.onclose = () => {
    document.getElementById('wsStatus').className = 'status-badge disconnected';
    document.getElementById('wsStatus').textContent = '⬤ DESCONECTADO';
    document.getElementById('binanceStatus').style.display = 'none';
    if (isLive) setTimeout(connectWS, 3000);
  };

  ws.onerror = () => ws.close();
}

function disconnectWS() {
  if (ws) { ws.close(); ws = null; }
  document.getElementById('wsStatus').className = 'status-badge disconnected';
  document.getElementById('wsStatus').textContent = '⬤ DESCONECTADO';
  document.getElementById('binanceStatus').style.display = 'none';
}

// Processamento de ticks
function processTick(data) {
  const tick = {
    price: data.price,
    volume: Math.round(data.volume_synthetic || 1),
    side: data.side || 'buy',
    timestamp: data.timestamp || Date.now(),
    is_absorption: data.is_absorption || false,
    absorption_type: data.absorption_type || null,
    absorption_strength: data.absorption_strength || 0,
    composite_signal: data.composite_signal || 0,
    stacking_buy: data.stacking_buy || 0,
    stacking_sell: data.stacking_sell || 0,
  };

  lastPrice = tick.price;
  lastSide = tick.side;
  totalTicks++;

  if (data.engines) {
    engineState = data.engines;
    updateEnginePanel();
  }

  masterTicks.push(tick);
  addTickToForming(tick);

  clusters = [...closedClusters];
  if (formingCluster) clusters.push(formingCluster);

  updateUI();
  render();
}

function addTickToForming(tick) {
  const vol = tick.volume;
  const dp = priceStep > 0 ? Math.round(tick.price / priceStep) * priceStep : tick.price;

  if (formingCluster && Math.abs(formingCluster.delta) >= threshold) {
    formingCluster.isClosed = true;
    formingCluster.endTime = tick.timestamp;
    recalcBodyWick(formingCluster);
    closedClusters.push(formingCluster);
    formingCluster = null;
    formingTicks = [];
  }

  if (!formingCluster) {
    formingCluster = {
      id: closedClusters.length,
      open: dp, high: dp, low: dp, close: dp,
      volumeBuy: tick.side === 'buy' ? vol : 0,
      volumeSell: tick.side === 'sell' ? vol : 0,
      volumeTotal: vol, volumeBody: vol, volumeWick: 0, wickPercent: 0,
      delta: tick.side === 'buy' ? vol : -vol,
      tickCount: 1, startTime: tick.timestamp,
      isClosed: false, poc: dp,
      priceLevels: priceStep > 0 ? [{price: dp, volumeBuy: tick.side === 'buy' ? vol : 0, volumeSell: tick.side === 'sell' ? vol : 0, volumeTotal: vol}] : [],
      absorptionCount: tick.is_absorption ? 1 : 0,
      absorptionBuyCount: tick.absorption_type === 'buy_absorption' ? 1 : 0,
      absorptionSellCount: tick.absorption_type === 'sell_absorption' ? 1 : 0,
      maxAbsorptionStrength: tick.absorption_strength || 0,
      maxStackingBuy: tick.stacking_buy || 0,
      maxStackingSell: tick.stacking_sell || 0,
      compositeSignalAvg: tick.composite_signal || 0,
      absorptionLevels: tick.is_absorption ? [{price: dp, type: tick.absorption_type, strength: tick.absorption_strength || 0}] : [],
      imbalanceLevels: (tick.stacking_buy > 0 || tick.stacking_sell > 0) ? [{price: dp, buy: tick.stacking_buy || 0, sell: tick.stacking_sell || 0}] : [],
    };
    formingTicks = [tick];
    return;
  }

  const c = formingCluster;
  c.close = dp;
  c.high = Math.max(c.high, dp);
  c.low = Math.min(c.low, dp);
  c.volumeTotal += vol;
  c.tickCount++;
  formingTicks.push(tick);

  if (tick.side === 'buy') { c.volumeBuy += vol; c.delta += vol; }
  else { c.volumeSell += vol; c.delta -= vol; }

  if (priceStep > 0) {
    const ex = c.priceLevels.find(l => l.price === dp);
    if (ex) {
      if (tick.side === 'buy') ex.volumeBuy += vol; else ex.volumeSell += vol;
      ex.volumeTotal += vol;
    } else {
      c.priceLevels.push({price: dp, volumeBuy: tick.side === 'buy' ? vol : 0, volumeSell: tick.side === 'sell' ? vol : 0, volumeTotal: vol});
    }
    let maxV = 0;
    for (const l of c.priceLevels) {
      if (l.volumeTotal > maxV) { maxV = l.volumeTotal; c.poc = l.price; }
    }
  }

  if (tick.is_absorption) {
    c.absorptionCount++;
    if (tick.absorption_type === 'buy_absorption') c.absorptionBuyCount++;
    if (tick.absorption_type === 'sell_absorption') c.absorptionSellCount++;
    c.maxAbsorptionStrength = Math.max(c.maxAbsorptionStrength, tick.absorption_strength || 0);
    if (!c.absorptionLevels) c.absorptionLevels = [];
    c.absorptionLevels.push({price: dp, type: tick.absorption_type, strength: tick.absorption_strength || 0});
  }
  
  if ((tick.stacking_buy || 0) > 0 || (tick.stacking_sell || 0) > 0) {
    if (!c.imbalanceLevels) c.imbalanceLevels = [];
    c.imbalanceLevels.push({price: dp, buy: tick.stacking_buy || 0, sell: tick.stacking_sell || 0});
  }
  
  c.maxStackingBuy = Math.max(c.maxStackingBuy, tick.stacking_buy || 0);
  c.maxStackingSell = Math.max(c.maxStackingSell, tick.stacking_sell || 0);
  const n = c.tickCount;
  c.compositeSignalAvg = (c.compositeSignalAvg * (n - 1) + (tick.composite_signal || 0)) / n;
}

function recalcBodyWick(cluster) {
  const bodyHigh = Math.max(cluster.open, cluster.close);
  const bodyLow = Math.min(cluster.open, cluster.close);
  let bodyVol = 0;
  let wickVol = 0;
  
  for (const level of cluster.priceLevels) {
    if (level.price >= bodyLow && level.price <= bodyHigh) {
      bodyVol += level.volumeTotal;
    } else {
      wickVol += level.volumeTotal;
    }
  }
  
  cluster.volumeBody = bodyVol;
  cluster.volumeWick = wickVol;
  cluster.wickPercent = cluster.volumeTotal > 0 ? (wickVol / cluster.volumeTotal) * 100 : 0;
}

function fullReprocess(tickArray) {
  closedClusters = [];
  formingCluster = null;
  formingTicks = [];
  masterTicks = [...tickArray];
  for (const tick of tickArray) addTickToForming(tick);
  clusters = [...closedClusters];
  if (formingCluster) clusters.push(formingCluster);
}

function getAllTicks() {
  return masterTicks;
}

// Renderização
function render() {
  if (!ctx) return;
  const w = canvas.width / (window.devicePixelRatio || 1);
  const h = canvas.height / (window.devicePixelRatio || 1);

  ctx.fillStyle = CONFIG.bg;
  ctx.fillRect(0, 0, w, h);

  if (clusters.length === 0) {
    ctx.fillStyle = CONFIG.text;
    ctx.font = '14px JetBrains Mono';
    ctx.textAlign = 'center';
    ctx.fillText('Aguardando ticks do MT5...', w / 2, h / 2 - 10);
    ctx.font = '11px JetBrains Mono';
    ctx.fillStyle = CONFIG.crosshair;
    ctx.fillText('Clique ▶ LIVE para conectar ao MT5 Exness', w / 2, h / 2 + 12);
    return;
  }

  const clusterWidth = Math.max(8, 40 * viewState.scaleX);

  let priceHigh = -Infinity, priceLow = Infinity;
  for (const c of clusters) {
    priceHigh = Math.max(priceHigh, c.high);
    priceLow = Math.min(priceLow, c.low);
  }
  const range = (priceHigh - priceLow) * viewState.scaleY;
  const center = (priceHigh + priceLow) / 2;
  const pad = range * 0.15;
  const viewHigh = center + range / 2 + pad + viewState.offsetY;
  const viewLow = center - range / 2 - pad + viewState.offsetY;

  const priceToY = (p) => {
    const r = viewHigh - viewLow;
    if (r === 0 || !isFinite(r)) return chartH / 2;
    const y = ((viewHigh - p) / r) * chartH;
    return isFinite(y) ? y : chartH / 2;
  };
  
  const yToPrice = (y) => viewHigh - (y / chartH) * (viewHigh - viewLow);
  const clusterToX = (i) => viewState.offsetX + i * (clusterWidth + CONFIG.clusterGap) + clusterWidth / 2;

  let maxVolume = 1;
  for (const c of clusters) maxVolume = Math.max(maxVolume, c.volumeTotal);

  // Grid
  ctx.lineWidth = 0.5;
  const gridLines = 10;
  const gridStep = (viewHigh - viewLow) / gridLines;
  for (let i = 0; i <= gridLines; i++) {
    const y = (chartH / gridLines) * i;
    const price = viewHigh - gridStep * i;
    ctx.strokeStyle = i % 2 === 0 ? CONFIG.gridStrong + '66' : CONFIG.grid + '44';
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(chartW, y);
    ctx.stroke();
    ctx.fillStyle = CONFIG.text;
    ctx.font = '9px JetBrains Mono';
    ctx.textAlign = 'left';
    ctx.fillText(price.toFixed(2), chartW + 5, y + 3);
  }

  ctx.strokeStyle = CONFIG.gridStrong;
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(chartW, 0);
  ctx.lineTo(chartW, totalH);
  ctx.stroke();

  // Current price line
  if (lastPrice > 0 && lastPrice >= viewLow && lastPrice <= viewHigh) {
    const cpY = priceToY(lastPrice);
    ctx.strokeStyle = CONFIG.currentPriceColor;
    ctx.lineWidth = 1.5;
    ctx.setLineDash([8, 4]);
    ctx.beginPath();
    ctx.moveTo(0, cpY);
    ctx.lineTo(chartW, cpY);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = CONFIG.currentPriceColor;
    ctx.fillRect(chartW + 1, cpY - 10, PRICE_WIDTH - 6, 20);
    ctx.fillStyle = '#000';
    ctx.font = 'bold 10px JetBrains Mono';
    ctx.textAlign = 'left';
    ctx.fillText('$' + lastPrice.toFixed(2), chartW + 4, cpY + 4);
    ctx.fillStyle = CONFIG.currentPriceColor;
    ctx.beginPath();
    ctx.moveTo(chartW, cpY);
    ctx.lineTo(chartW - 6, cpY - 5);
    ctx.lineTo(chartW - 6, cpY + 5);
    ctx.closePath();
    ctx.fill();
  }

  // Clusters
  for (let idx = 0; idx < clusters.length; idx++) {
    const cluster = clusters[idx];
    const centerX = clusterToX(idx);
    const x = centerX - clusterWidth / 2;
    const cw = clusterWidth;

    if (centerX < -cw || centerX > chartW + cw) continue;

    const isBull = cluster.close >= cluster.open;
    const deltaIntensity = Math.min(1, Math.abs(cluster.delta) / (threshold * 0.8));

    const highY = priceToY(cluster.high);
    const lowY = priceToY(cluster.low);
    ctx.strokeStyle = CONFIG.wickColor;
    ctx.lineWidth = CONFIG.wickWidth;
    ctx.beginPath();
    ctx.moveTo(centerX, highY);
    ctx.lineTo(centerX, lowY);
    ctx.stroke();

    let bodyTop = priceToY(Math.max(cluster.open, cluster.close));
    let bodyBottom = priceToY(Math.min(cluster.open, cluster.close));
    if (!isFinite(bodyTop)) bodyTop = chartH / 2 - 5;
    if (!isFinite(bodyBottom)) bodyBottom = chartH / 2 + 5;
    const bodyH = Math.max(3, bodyBottom - bodyTop);

    const baseAlpha = (CONFIG.clusterOpacity / 100) * (0.3 + deltaIntensity * 0.7);
    const alphaHex = Math.round(Math.min(255, baseAlpha * 255)).toString(16).padStart(2, '0');
    const borderAlpha = Math.round(Math.min(255, (0.5 + deltaIntensity * 0.5) * 255)).toString(16).padStart(2, '0');

    if (viewMode === 'clean') {
      ctx.fillStyle = (isBull ? CONFIG.bullBody : CONFIG.bearBody) + alphaHex;
      ctx.fillRect(x, bodyTop, cw, bodyH);
    } else {
      const grad = ctx.createLinearGradient(x, bodyTop, x, bodyTop + bodyH);
      if (isBull) {
        grad.addColorStop(0, CONFIG.bull + alphaHex);
        grad.addColorStop(0.5, CONFIG.bullBody + alphaHex);
        grad.addColorStop(1, CONFIG.bullDark + alphaHex);
      } else {
        grad.addColorStop(0, CONFIG.bearDark + alphaHex);
        grad.addColorStop(0.5, CONFIG.bearBody + alphaHex);
        grad.addColorStop(1, CONFIG.bear + alphaHex);
      }
      ctx.fillStyle = grad;
      ctx.fillRect(x, bodyTop, cw, bodyH);
    }

    if (CONFIG.showClusterBorder && CONFIG.clusterBorderWidth > 0) {
      ctx.strokeStyle = CONFIG.clusterBorderColor + borderAlpha;
      ctx.lineWidth = CONFIG.clusterBorderWidth;
      ctx.strokeRect(x, bodyTop, cw, bodyH);
    }

    if (viewState.scaleX >= 0.9 && bodyH > 14) {
      ctx.fillStyle = isBull ? '#ffffff' + borderAlpha : '#ffffff' + borderAlpha;
      ctx.font = 'bold 8px JetBrains Mono';
      ctx.textAlign = 'center';
      const deltaText = (cluster.delta >= 0 ? '+' : '') + (Math.abs(cluster.delta) >= 1000 ? (cluster.delta / 1000).toFixed(1) + 'k' : cluster.delta);
      ctx.fillText(deltaText, centerX, bodyTop + bodyH / 2 + 3);
    }

    // POC
    if (cluster.priceLevels.length > 0) {
      const pocY = priceToY(cluster.poc);
      ctx.strokeStyle = CONFIG.pocColor + '22';
      ctx.lineWidth = 7;
      ctx.beginPath();
      ctx.moveTo(x - 6, pocY);
      ctx.lineTo(x + cw + 6, pocY);
      ctx.stroke();
      ctx.strokeStyle = CONFIG.pocColor + '55';
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(x - 5, pocY);
      ctx.lineTo(x + cw + 5, pocY);
      ctx.stroke();
      ctx.strokeStyle = CONFIG.pocColor;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(x - 4, pocY);
      ctx.lineTo(x + cw + 4, pocY);
      ctx.stroke();
      ctx.fillStyle = CONFIG.pocColor;
      ctx.beginPath();
      ctx.moveTo(x - 6, pocY);
      ctx.lineTo(x - 3, pocY - 3);
      ctx.lineTo(x, pocY);
      ctx.lineTo(x - 3, pocY + 3);
      ctx.closePath();
      ctx.fill();
      if (viewState.scaleX >= 1.2) {
        ctx.fillStyle = CONFIG.pocColor;
        ctx.font = 'bold 7px JetBrains Mono';
        ctx.textAlign = 'center';
        ctx.fillText('POC', centerX, pocY - 5);
      }
    }

    // Footprint
    if (viewMode !== 'clean' && cluster.priceLevels.length > 0) {
      const maxLevelVol = Math.max(...cluster.priceLevels.map(l => l.volumeTotal));
      const barRatio = viewMode === 'raw' ? 0.9 : 0.65;

      for (const level of cluster.priceLevels) {
        const ly = priceToY(level.price);
        const volRatio = level.volumeTotal / maxLevelVol;
        const barW = volRatio * cw * barRatio;
        const levelAlpha = Math.round(80 + volRatio * 175).toString(16).padStart(2, '0');
        const isBuyDom = level.volumeBuy >= level.volumeSell;
        ctx.fillStyle = (isBuyDom ? CONFIG.histogramBullColor : CONFIG.histogramBearColor) + levelAlpha;
        ctx.fillRect(centerX - barW / 2, ly - 1.5, barW, 3);
        if (volRatio > 0.7) {
          ctx.fillStyle = (isBuyDom ? '#b9f6ca' : '#ffcdd2') + '66';
          ctx.fillRect(centerX - barW / 2, ly - 0.5, barW, 1);
        }
        if (viewMode === 'raw' && viewState.scaleX >= 1.5 && level.volumeTotal > 0) {
          ctx.fillStyle = isBuyDom ? CONFIG.bull + 'cc' : CONFIG.bear + 'cc';
          ctx.font = '6px JetBrains Mono';
          ctx.textAlign = 'center';
          ctx.fillText(level.volumeTotal.toString(), centerX, ly + 6);
        }
      }

      // Absorption markers
      if (CONFIG.showAbsorptionLevels && cluster.absorptionLevels && cluster.absorptionLevels.length > 0) {
        for (const abs of cluster.absorptionLevels) {
          const ay = priceToY(abs.price);
          const dotR = Math.max(2, Math.min(4, viewState.scaleX * 2.5));
          const isBuyAbs = abs.type === 'buy_absorption';
          const dotColor = isBuyAbs ? CONFIG.absorptionBuy : CONFIG.absorptionSell;
          ctx.shadowColor = dotColor;
          ctx.shadowBlur = 6;
          ctx.fillStyle = dotColor;
          ctx.beginPath();
          ctx.arc(x + cw - dotR - 2, ay, dotR, 0, Math.PI * 2);
          ctx.fill();
          ctx.shadowBlur = 0;
          ctx.fillStyle = '#ffffff';
          ctx.beginPath();
          ctx.arc(x + cw - dotR - 2, ay, dotR * 0.4, 0, Math.PI * 2);
          ctx.fill();
          ctx.strokeStyle = dotColor + '55';
          ctx.lineWidth = 0.5;
          ctx.setLineDash([2, 2]);
          ctx.beginPath();
          ctx.moveTo(x, ay);
          ctx.lineTo(x + cw, ay);
          ctx.stroke();
          ctx.setLineDash([]);
        }
      }

      // Imbalance markers
      if (CONFIG.showImbalanceLevels && cluster.imbalanceLevels && cluster.imbalanceLevels.length > 0) {
        for (const imb of cluster.imbalanceLevels) {
          const iy = priceToY(imb.price);
          const isBuyImb = imb.buy > imb.sell;
          const imbColor = isBuyImb ? CONFIG.imbalanceMarkerColor : CONFIG.imbalanceMarkerColor;
          const dotR = Math.max(1.5, Math.min(3, viewState.scaleX * 2));
          ctx.fillStyle = imbColor;
          ctx.beginPath();
          ctx.moveTo(x + dotR + 1, iy);
          ctx.lineTo(x + dotR + 1 + dotR, iy - dotR);
          ctx.lineTo(x + dotR + 1 + dotR * 2, iy);
          ctx.lineTo(x + dotR + 1 + dotR, iy + dotR);
          ctx.closePath();
          ctx.fill();
          ctx.fillStyle = imbColor + '44';
          ctx.fillRect(x, iy - 0.5, cw * 0.15, 1);
        }
      }
    }

    if (viewState.scaleX >= 1) {
      ctx.font = '7px JetBrains Mono';
      ctx.textAlign = 'center';
      ctx.fillStyle = '#667788';
      ctx.fillText('W:' + cluster.volumeWick, centerX, lowY + 10);
      ctx.fillStyle = isBull ? CONFIG.bull + 'cc' : CONFIG.bear + 'cc';
      ctx.fillText('B:' + cluster.volumeBody, centerX, highY - 4);
    }

    if (!cluster.isClosed) {
      ctx.strokeStyle = CONFIG.highlight;
      ctx.lineWidth = 2;
      ctx.setLineDash([5, 3]);
      ctx.strokeRect(x - 1, bodyTop - 1, cw + 2, bodyH + 2);
      ctx.setLineDash([]);
      ctx.shadowColor = CONFIG.highlight;
      ctx.shadowBlur = 6;
      ctx.strokeStyle = CONFIG.highlight + '44';
      ctx.lineWidth = 1;
      ctx.strokeRect(x - 2, bodyTop - 2, cw + 4, bodyH + 4);
      ctx.shadowBlur = 0;
    }

    // Wick warning
    if (cluster.wickPercent >= CONFIG.wickWarningThreshold) {
      const warningY = lowY + 16;
      ctx.shadowColor = CONFIG.highlight;
      ctx.shadowBlur = 8;
      ctx.fillStyle = CONFIG.highlight;
      ctx.beginPath();
      ctx.arc(centerX, warningY, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;
      ctx.fillStyle = '#fff';
      ctx.beginPath();
      ctx.arc(centerX, warningY, 2, 0, Math.PI * 2);
      ctx.fill();
      if (viewState.scaleX >= 0.8) {
        ctx.fillStyle = CONFIG.highlight;
        ctx.font = 'bold 8px JetBrains Mono';
        ctx.textAlign = 'center';
        ctx.fillText(cluster.wickPercent.toFixed(0) + '%', centerX, warningY + 13);
      }
    }

    // Absorption markers
    if (cluster.absorptionCount > 0) {
      const ms = Math.min(6, Math.max(3, cw * 0.3));
      if (cluster.absorptionBuyCount > cluster.absorptionSellCount) {
        ctx.fillStyle = CONFIG.absorptionBuy;
        ctx.beginPath();
        ctx.moveTo(centerX, lowY + ms * 3);
        ctx.lineTo(centerX - ms, lowY + ms * 3 + ms * 1.5);
        ctx.lineTo(centerX + ms, lowY + ms * 3 + ms * 1.5);
        ctx.closePath();
        ctx.fill();
        if (cluster.absorptionBuyCount > 1 && viewState.scaleX >= 0.8) {
          ctx.fillStyle = CONFIG.absorptionBuy;
          ctx.font = 'bold 7px JetBrains Mono';
          ctx.textAlign = 'center';
          ctx.fillText('' + cluster.absorptionBuyCount, centerX, lowY + ms * 3 + ms * 1.5 + 10);
        }
      } else if (cluster.absorptionSellCount > 0) {
        ctx.fillStyle = CONFIG.absorptionSell;
        ctx.beginPath();
        ctx.moveTo(centerX, highY - ms * 3);
        ctx.lineTo(centerX - ms, highY - ms * 3 - ms * 1.5);
        ctx.lineTo(centerX + ms, highY - ms * 3 - ms * 1.5);
        ctx.closePath();
        ctx.fill();
        if (cluster.absorptionSellCount > 1 && viewState.scaleX >= 0.8) {
          ctx.fillStyle = CONFIG.absorptionSell;
          ctx.font = 'bold 7px JetBrains Mono';
          ctx.textAlign = 'center';
          ctx.fillText('' + cluster.absorptionSellCount, centerX, highY - ms * 3 - ms * 1.5 - 4);
        }
      }
    }

    // Stacking bars
    if (cluster.maxStackingBuy >= 2 || cluster.maxStackingSell >= 2) {
      const barW2 = Math.max(2, cw * 0.12);
      const bTop = bodyTop;
      const bH = Math.max(4, bodyH);
      if (cluster.maxStackingBuy >= 2) {
        const intensity = Math.min(cluster.maxStackingBuy / 5, 1);
        const alpha = Math.round(intensity * 200 + 55).toString(16).padStart(2, '0');
        ctx.fillStyle = CONFIG.absorptionBuy + alpha;
        ctx.fillRect(x - barW2 - 1, bTop, barW2, bH);
        if (viewState.scaleX >= 0.8) {
          ctx.fillStyle = CONFIG.absorptionBuy;
          ctx.font = 'bold 7px JetBrains Mono';
          ctx.textAlign = 'right';
          ctx.fillText('S' + cluster.maxStackingBuy, x - barW2 - 2, bTop + bH / 2 + 3);
        }
      }
      if (cluster.maxStackingSell >= 2) {
        const intensity = Math.min(cluster.maxStackingSell / 5, 1);
        const alpha = Math.round(intensity * 200 + 55).toString(16).padStart(2, '0');
        ctx.fillStyle = CONFIG.absorptionSell + alpha;
        ctx.fillRect(x + cw + 1, bTop, barW2, bH);
        if (viewState.scaleX >= 0.8) {
          ctx.fillStyle = CONFIG.absorptionSell;
          ctx.font = 'bold 7px JetBrains Mono';
          ctx.textAlign = 'left';
          ctx.fillText('S' + cluster.maxStackingSell, x + cw + barW2 + 2, bTop + bH / 2 + 3);
        }
      }
    }

    // Composite signal
    if (Math.abs(cluster.compositeSignalAvg) > 0.2 && viewState.scaleX >= 0.7) {
      const dotX = x + cw - 3;
      const dotY = highY - 2;
      const dotSize = Math.min(4, 2 + Math.abs(cluster.compositeSignalAvg) * 3);
      ctx.fillStyle = cluster.compositeSignalAvg > 0 ? CONFIG.absorptionBuy + '88' : CONFIG.absorptionSell + '88';
      ctx.beginPath();
      ctx.arc(dotX, dotY, dotSize, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // Volume histogram
  if (histH > 0) {
    const histY = chartH;
    const labelH = 14;
    const gap = 4;
    const availH = histH - labelH - gap;
    const bar1H = availH * HIST_SPLIT;
    const bar2H = availH * (1 - HIST_SPLIT);

    const histGrad = ctx.createLinearGradient(0, histY, 0, histY + histH);
    histGrad.addColorStop(0, '#0f1923');
    histGrad.addColorStop(1, '#0a0e17');
    ctx.fillStyle = histGrad;
    ctx.fillRect(0, histY, chartW + PRICE_WIDTH, histH);

    ctx.strokeStyle = crosshair.visible && Math.abs(crosshair.y - histY) < 6 ? '#667788' : '#334455';
    ctx.lineWidth = crosshair.visible && Math.abs(crosshair.y - histY) < 6 ? 3 : 2;
    ctx.beginPath();
    ctx.moveTo(0, histY);
    ctx.lineTo(chartW + PRICE_WIDTH, histY);
    ctx.stroke();

    const midY = histY + labelH + bar1H + gap / 2;
    const nearMid = crosshair.visible && Math.abs(crosshair.y - midY) < 5;
    ctx.strokeStyle = nearMid ? '#8899aa' : '#1e2d3d';
    ctx.lineWidth = nearMid ? 2 : 0.5;
    ctx.beginPath();
    ctx.moveTo(0, midY);
    ctx.lineTo(chartW, midY);
    ctx.stroke();

    ctx.font = 'bold 8px JetBrains Mono';
    ctx.textAlign = 'left';
    ctx.fillStyle = CONFIG.highlight;
    ctx.fillText('VOL', 4, histY + 10);
    ctx.fillStyle = '#667788';
    ctx.fillText('BODY/WICK', 4, midY + 10);

    for (let idx = 0; idx < clusters.length; idx++) {
      const cluster = clusters[idx];
      const centerX = clusterToX(idx);
      const x = centerX - clusterWidth / 2;
      if (centerX < -clusterWidth || centerX > chartW + clusterWidth) continue;

      const isBull = cluster.close >= cluster.open;
      const volRatio = cluster.volumeTotal / maxVolume;

      const v1H = volRatio * (bar1H - 4);
      const v1Y = histY + labelH + bar1H - v1H;

      const vGrad = ctx.createLinearGradient(x, v1Y, x, v1Y + v1H);
      if (isBull) {
        vGrad.addColorStop(0, CONFIG.bull);
        vGrad.addColorStop(1, CONFIG.bullDark + 'cc');
      } else {
        vGrad.addColorStop(0, CONFIG.bear);
        vGrad.addColorStop(1, CONFIG.bearDark + 'cc');
      }
      ctx.fillStyle = vGrad;
      ctx.fillRect(x + 0.5, v1Y, clusterWidth - 1, v1H);

      ctx.fillStyle = isBull ? '#b9f6ca55' : '#ffcdd255';
      ctx.fillRect(x + 0.5, v1Y, clusterWidth - 1, Math.min(2, v1H));

      if (volRatio > 0.3 && viewState.scaleX >= 0.8 && v1H > 10) {
        ctx.fillStyle = '#ffffffbb';
        ctx.font = '7px JetBrains Mono';
        ctx.textAlign = 'center';
        const vText = cluster.volumeTotal >= 1000 ? (cluster.volumeTotal / 1000).toFixed(1) + 'k' : '' + cluster.volumeTotal;
        ctx.fillText(vText, centerX, v1Y + v1H / 2 + 3);
      }

      const v2H = volRatio * (bar2H - 4);
      const v2Y = midY + gap / 2;

      if (cluster.volumeTotal > 0) {
        const bodyPct = cluster.volumeBody / cluster.volumeTotal;
        const wickPct = cluster.volumeWick / cluster.volumeTotal;
        const bodyBarH = v2H * bodyPct;
        const wickBarH = v2H * wickPct;
        const baseY2 = v2Y + bar2H - v2H;

        if (wickBarH > 0) {
          const wickColor = cluster.wickPercent >= 50 ? '#ffd740' : '#455a64';
          ctx.fillStyle = wickColor + 'cc';
          ctx.fillRect(x + 0.5, baseY2, clusterWidth - 1, wickBarH);
        }
        if (bodyBarH > 0) {
          ctx.fillStyle = isBull ? '#4caf50cc' : '#e53935cc';
          ctx.fillRect(x + 0.5, baseY2 + wickBarH, clusterWidth - 1, bodyBarH);
        }
      }

      if (cluster.wickPercent >= CONFIG.wickWarningThreshold) {
        ctx.fillStyle = CONFIG.highlight + 'aa';
        ctx.fillRect(x, histY + histH - 3, clusterWidth, 3);
      }
    }
  }

  // Drawings
  for (const d of drawings) {
    const isSel = d.id === selectedDrawing;
    const opacHex = Math.round((CONFIG.drawOpacity / 100) * 255).toString(16).padStart(2, '0');
    ctx.strokeStyle = d.color + opacHex;
    ctx.lineWidth = isSel ? CONFIG.drawLineWidth + 1 : CONFIG.drawLineWidth;
    
    if (d.type === 'hline') {
      const y = priceToY(d.p1.y);
      ctx.setLineDash(isSel ? [] : [6, 4]);
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(chartW, y);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = d.color;
      ctx.font = 'bold 9px JetBrains Mono';
      ctx.textAlign = 'left';
      const symDig = (SYMBOLS[currentSymbol] || {}).dig || 2;
      ctx.fillText(d.p1.y.toFixed(symDig), chartW + 4, y - 3);
      if (isSel) {
        ctx.beginPath();
        ctx.arc(chartW - 8, y, 4, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }

  // Crosshair
  if (crosshair.visible) {
    ctx.strokeStyle = CONFIG.crosshair;
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(crosshair.x, 0);
    ctx.lineTo(crosshair.x, totalH);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, crosshair.y);
    ctx.lineTo(chartW, crosshair.y);
    ctx.stroke();
    ctx.setLineDash([]);

    if (crosshair.y < chartH) {
      const price = yToPrice(crosshair.y);
      ctx.fillStyle = CONFIG.highlight;
      ctx.fillRect(chartW + 1, crosshair.y - 10, PRICE_WIDTH - 6, 20);
      ctx.fillStyle = '#000';
      ctx.font = 'bold 10px JetBrains Mono';
      ctx.textAlign = 'left';
      ctx.fillText(price.toFixed(2), chartW + 4, crosshair.y + 4);
    }
  }

  // Header overlay
  ctx.fillStyle = '#0a0e17ee';
  ctx.fillRect(0, 0, 420, 34);
  ctx.fillStyle = CONFIG.highlight;
  ctx.font = 'bold 12px JetBrains Mono';
  ctx.textAlign = 'left';
  ctx.fillText((SYMBOLS[currentSymbol]||{}).label||currentSymbol + ' | ' + viewMode.toUpperCase() + ' | MT5 LIVE', 8, 13);
  ctx.fillStyle = CONFIG.text;
  ctx.font = '9px JetBrains Mono';
  const closedCount = clusters.filter(c => c.isClosed).length;
  ctx.fillText('Clusters: ' + closedCount + ' | Δ: ' + (threshold >= 1000 ? (threshold/1000)+'k' : threshold) + ' | Step: $' + priceStep.toFixed(0) + ' | Zoom: ' + (viewState.scaleX * 100).toFixed(0) + '%', 8, 26);

  // Legend
  ctx.fillStyle = CONFIG.bgPanel + 'dd';
  ctx.fillRect(chartW - 210, 0, 210, 28);
  ctx.font = '7px JetBrains Mono';
  ctx.textAlign = 'left';
  ctx.fillStyle = CONFIG.absorptionBuy; ctx.fillText('▲ Buy Absorção', chartW - 205, 10);
  ctx.fillStyle = CONFIG.absorptionSell; ctx.fillText('▼ Sell Absorção', chartW - 205, 20);
  ctx.fillStyle = CONFIG.absorptionBuy; ctx.fillText('║ Stacking Buy', chartW - 110, 10);
  ctx.fillStyle = CONFIG.absorptionSell; ctx.fillText('║ Stacking Sell', chartW - 110, 20);

  // Minimap
  if (clusters.length > 2) {
    const mmW = 100, mmH = 24;
    const mmX = chartW - mmW - 8;
    const mmY = chartH - mmH - 8;

    ctx.fillStyle = CONFIG.bgPanel;
    ctx.fillRect(mmX, mmY, mmW, mmH);
    ctx.strokeStyle = CONFIG.gridStrong;
    ctx.lineWidth = 1;
    ctx.strokeRect(mmX, mmY, mmW, mmH);

    const mmScale = mmW / clusters.length;
    for (let i = 0; i < clusters.length; i++) {
      const c = clusters[i];
      const mx = mmX + i * mmScale;
      ctx.fillStyle = (c.close >= c.open ? CONFIG.bull : CONFIG.bear) + '77';
      ctx.fillRect(mx, mmY + 2, Math.max(1, mmScale), mmH - 4);
      if (c.wickPercent >= CONFIG.wickWarningThreshold) {
        ctx.fillStyle = CONFIG.highlight + 'cc';
        ctx.fillRect(mx, mmY + mmH - 4, Math.max(1, mmScale), 3);
      }
      if (c.absorptionCount > 0) {
        ctx.fillStyle = c.absorptionBuyCount > c.absorptionSellCount ? CONFIG.absorptionBuy + '88' : CONFIG.absorptionSell + '88';
        ctx.fillRect(mx, mmY, Math.max(1, mmScale), 3);
      }
    }

    const totalWidth = clusters.length * (clusterWidth + CONFIG.clusterGap);
    const vpW = (chartW / totalWidth) * mmW;
    const vpX = mmX + (-viewState.offsetX / totalWidth) * mmW;
    ctx.strokeStyle = CONFIG.highlight;
    ctx.lineWidth = 2;
    ctx.strokeRect(Math.max(mmX, vpX), mmY, Math.min(vpW, mmW), mmH);
  }
}

// Eventos do canvas
function setupCanvasEvents() {
  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    crosshair = { x: Math.min(x, chartW), y, visible: true };

    if (viewState.isDragging) {
      if (viewState.dragMode === 'zoom') {
        const dy = e.clientY - viewState.lastY;
        const zoomFactor = 1 + dy * 0.005;
        viewState.scaleY = Math.max(0.1, Math.min(20, viewState.scaleY * zoomFactor));
        viewState.lastY = e.clientY;
      } else if (viewState.dragMode === 'histResize') {
        const newChartH = Math.max(100, Math.min(totalH - 40, y));
        HISTOGRAM_RATIO = Math.max(0.05, Math.min(0.6, 1 - newChartH / totalH));
        histH = Math.floor(totalH * HISTOGRAM_RATIO);
        chartH = totalH - histH;
      } else if (viewState.dragMode === 'histSplitResize') {
        const histY = chartH;
        const labelH = 14;
        const gap = 4;
        const availH = histH - labelH - gap;
        const relativeY = y - histY - labelH;
        HIST_SPLIT = Math.max(0.15, Math.min(0.85, relativeY / availH));
      } else if (viewState.dragMode === 'moveDrawing' && selectedDrawing !== null) {
        const drawing = drawings.find(d => d.id === selectedDrawing);
        if (drawing && drawing.type === 'hline') {
          drawing.p1.y = yToPrice(y);
        }
      } else {
        const dx = e.clientX - viewState.lastX;
        const dy = e.clientY - viewState.lastY;
        viewState.offsetX += dx;
        if (clusters.length > 0) {
          let pH = -Infinity, pL = Infinity;
          for (const c of clusters) { pH = Math.max(pH, c.high); pL = Math.min(pL, c.low); }
          const priceRange = (pH - pL) * viewState.scaleY * 1.3;
          const pricePerPixel = priceRange / chartH;
          viewState.offsetY += dy * pricePerPixel;
        }
        viewState.lastX = e.clientX;
        viewState.lastY = e.clientY;
      }
    }
    
    if (!viewState.isDragging) {
      const histBorderY = chartH;
      const labelH = 14, gap = 4;
      const availH = histH - labelH - gap;
      const midSepY = chartH + labelH + availH * HIST_SPLIT + gap / 2;
      
      if (Math.abs(y - histBorderY) < 6 && x < chartW) {
        canvas.style.cursor = 'row-resize';
      } else if (y > chartH && Math.abs(y - midSepY) < 5 && x < chartW) {
        canvas.style.cursor = 'row-resize';
      } else if (x > chartW) {
        canvas.style.cursor = 'ns-resize';
      } else if (drawTool !== 'none') {
        canvas.style.cursor = 'crosshair';
      } else {
        canvas.style.cursor = 'crosshair';
      }
    }
    render();
  });

  canvas.addEventListener('mouseleave', () => {
    crosshair.visible = false;
    viewState.isDragging = false;
    render();
  });

  canvas.addEventListener('mousedown', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (Math.abs(y - chartH) < 6 && x < chartW) {
      viewState.isDragging = true;
      viewState.dragMode = 'histResize';
    } else if (y > chartH && x < chartW) {
      const labelH = 14, gap = 4;
      const availH = histH - labelH - gap;
      const midSepY = chartH + labelH + availH * HIST_SPLIT + gap / 2;
      if (Math.abs(y - midSepY) < 5) {
        viewState.isDragging = true;
        viewState.dragMode = 'histSplitResize';
      }
    } else if (x > chartW) {
      viewState.isDragging = true;
      viewState.lastY = e.clientY;
      viewState.dragMode = 'zoom';
    } else if (drawTool !== 'none') {
      const price = yToPrice(y);
      const clusterIdx = Math.round((x - viewState.offsetX) / (Math.max(8, 40 * viewState.scaleX) + CONFIG.clusterGap));
      
      if (!currentDrawing) {
        currentDrawing = {
          id: nextDrawId++,
          type: drawTool,
          p1: { x: clusterIdx, y: price },
          p2: null,
          color: CONFIG.drawColor,
        };
        if (drawTool === 'hline' || drawTool === 'vline') {
          drawings.push({ ...currentDrawing });
          currentDrawing = null;
          setDrawTool('none');
        }
      } else {
        currentDrawing.p2 = { x: clusterIdx, y: price };
        drawings.push({ ...currentDrawing });
        currentDrawing = null;
        setDrawTool('none');
      }
      render();
    } else {
      selectedDrawing = null;
      for (const d of drawings) {
        if (d.type === 'hline') {
          const dy = Math.abs(priceToY(d.p1.y) - y);
          if (dy < 6) { selectedDrawing = d.id; break; }
        }
      }
      viewState.isDragging = true;
      viewState.lastX = e.clientX;
      viewState.lastY = e.clientY;
      viewState.dragMode = selectedDrawing ? 'moveDrawing' : 'pan';
    }
  });

  canvas.addEventListener('mouseup', () => {
    viewState.isDragging = false;
  });

  canvas.addEventListener('wheel', (e) => {
    e.preventDefault();
    if (e.ctrlKey) {
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      viewState.scaleX = Math.max(0.2, Math.min(15, viewState.scaleX * delta));
    } else if (e.shiftKey) {
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      viewState.scaleY = Math.max(0.1, Math.min(20, viewState.scaleY * delta));
    } else {
      viewState.offsetX += e.deltaY > 0 ? 50 : -50;
    }
    render();
  }, { passive: false });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Delete' || e.key === 'Backspace') {
      if (selectedDrawing !== null && document.activeElement === document.body) {
        e.preventDefault();
        deleteSelectedDrawing();
      }
    }
    if (e.key === 'Escape') {
      setDrawTool('none');
      currentDrawing = null;
      selectedDrawing = null;
      render();
    }
  });
}

function yToPrice(y) {
  if (clusters.length === 0) return 0;
  let pH = -Infinity, pL = Infinity;
  for (const c of clusters) { pH = Math.max(pH, c.high); pL = Math.min(pL, c.low); }
  const range = (pH - pL) * viewState.scaleY;
  const center = (pH + pL) / 2;
  const pad = range * 0.15;
  const vH = center + range / 2 + pad;
  const vL = center - range / 2 - pad;
  const r = vH - vL;
  return r === 0 ? center : vH - (y / chartH) * r;
}

// Controles
function setupControls() {
  const thSlider = document.getElementById('thresholdSlider');
  const thValue = document.getElementById('thresholdValue');
  thSlider.addEventListener('input', () => {
    threshold = Number(thSlider.value);
    thValue.textContent = threshold >= 1000 ? (threshold / 1000) + 'k' : threshold;
    const allT = getAllTicks();
    if (allT.length > 0) fullReprocess(allT);
    render();
  });

  const stSlider = document.getElementById('stepSlider');
  const stValue = document.getElementById('stepValue');
  stSlider.addEventListener('input', () => {
    const val = Number(stSlider.value);
    const sym = SYMBOLS[currentSymbol] || {};
    const baseStep = sym.step || 0.01;
    priceStep = val === 0 ? 0 : val * baseStep;
    stValue.textContent = priceStep === 0 ? 'AUTO' : (priceStep >= 1 ? '$' + priceStep.toFixed(0) : priceStep.toFixed(4));
    const allT = getAllTicks();
    if (allT.length > 0) fullReprocess(allT);
    render();
  });
}

function setColor(key, value) {
  CONFIG[key] = value;
  render();
}

function autoFitView() {
  if (clusters.length === 0) return;
  const cw = Math.max(8, 40 * viewState.scaleX);
  const totalWidth = clusters.length * (cw + CONFIG.clusterGap);
  const visibleClusters = Math.floor(chartW / (cw + CONFIG.clusterGap));
  const targetIdx = Math.max(0, clusters.length - visibleClusters);
  viewState.offsetX = -(targetIdx * (cw + CONFIG.clusterGap)) + 20;
  viewState.offsetY = 0;
  viewState.scaleY = 1;
}

function findClusters() {
  if (clusters.length === 0) {
    document.getElementById('sourceLabel').textContent = 'Nenhum cluster';
    return;
  }
  viewState.scaleX = 1;
  viewState.scaleY = 1;
  viewState.offsetY = 0;
  autoFitView();
  render();
  const symDig = (SYMBOLS[currentSymbol] || {}).dig || 2;
  document.getElementById('sourceLabel').textContent = clusters.length + ' clusters | ' + clusters[clusters.length-1].close.toFixed(symDig);
}

function setViewMode(mode) {
  viewMode = mode;
  document.querySelectorAll('[data-mode]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.mode === mode);
  });
  render();
}

function setDrawTool(tool) {
  drawTool = tool;
  currentDrawing = null;
  document.querySelectorAll('[data-draw]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.draw === tool);
  });
  canvas.style.cursor = tool !== 'none' ? 'crosshair' : 'crosshair';
}

function clearDrawings() {
  drawings = [];
  selectedDrawing = null;
  currentDrawing = null;
  render();
}

function deleteSelectedDrawing() {
  if (selectedDrawing !== null) {
    drawings = drawings.filter(d => d.id !== selectedDrawing);
    selectedDrawing = null;
    render();
  }
}

function toggleEnginePanel() {
  showEnginePanel = !showEnginePanel;
  document.getElementById('enginePanel').classList.toggle('visible', showEnginePanel);
  document.getElementById('engineToggle').classList.toggle('active', showEnginePanel);
  resize();
}

function toggleLive() {
  isLive = !isLive;
  const btn = document.getElementById('liveBtn');
  if (isLive) {
    btn.textContent = '⏹ PARAR';
    btn.classList.add('stopped');
    connectWS();
  } else {
    btn.textContent = '▶ LIVE';
    btn.classList.remove('stopped');
    disconnectWS();
  }
}

function toggleCalibration() {
  showCalibration = !showCalibration;
  document.getElementById('calibPanel').classList.toggle('visible', showCalibration);
  document.getElementById('calibToggle').classList.toggle('active', showCalibration);
  resize();
}

function switchSymbol(sym) {
  currentSymbol = sym;
  if (ws && ws.readyState === 1) {
    ws.send(JSON.stringify({ type: 'switch_symbol', symbol: sym }));
    setTimeout(() => loadHistory(24), 500);
  }
  closedClusters = [];
  formingCluster = null;
  formingTicks = [];
  masterTicks = [];
  clusters = [];
  totalTicks = 0;
  lastPrice = 0;

  const cfg = SYMBOLS[sym] || {};
  if (cfg.delta_th) {
    threshold = cfg.delta_th;
    document.getElementById('thresholdSlider').value = threshold;
    document.getElementById('thresholdValue').textContent = threshold >= 1000 ? (threshold/1000)+'k' : threshold;
  }
  if (cfg.step !== undefined) {
    priceStep = cfg.step;
    document.getElementById('stepSlider').value = priceStep >= 1 ? priceStep : Math.round(priceStep * 10000);
    document.getElementById('stepValue').textContent = priceStep >= 1 ? '$' + priceStep.toFixed(0) : priceStep.toFixed(4);
  }
  
  const el = document.getElementById('engineSourceLabel');
  if (el) el.textContent = (cfg.label || sym);

  render();
}

function setWeightMode(mode) {
  weightMode = mode;
  if (ws && ws.readyState === 1) {
    ws.send(JSON.stringify({ action: 'set_weight_mode', mode: mode }));
  }
}

function loadHistory(hours) {
  if (!ws || ws.readyState !== 1) return;
  document.getElementById('sourceLabel').textContent = 'carregando ' + hours + 'h...';
  ws.send(JSON.stringify({
    action: 'get_history',
    symbol: currentSymbol,
    hours: hours,
  }));
}

function resetChart() {
  closedClusters = [];
  formingCluster = null;
  formingTicks = [];
  masterTicks = [];
  clusters = [];
  totalTicks = 0;
  viewState.offsetX = 0;
  viewState.offsetY = 0;
  viewState.scaleX = 1;
  viewState.scaleY = 1;
  updateUI();
  render();
}

// UI Updates
function updateUI() {
  const priceEl = document.getElementById('priceDisplay');
  const symDig = (SYMBOLS[currentSymbol] || {}).dig || 2;
  priceEl.textContent = lastPrice > 0 ? lastPrice.toFixed(symDig) : '--';
  priceEl.className = 'price-display ' + (lastSide === 'buy' ? 'up' : 'down');
  document.getElementById('tickCounter').textContent = totalTicks.toLocaleString() + ' ticks';
  document.getElementById('clusterCount').textContent = clusters.filter(c => c.isClosed).length;

  const forming = clusters.find(c => !c.isClosed);
  const bar = document.getElementById('formingBar');
  if (forming) {
    bar.classList.add('visible');
    const deltaEl = document.getElementById('formingDelta');
    deltaEl.textContent = (forming.delta >= 0 ? '+' : '') + forming.delta;
    deltaEl.style.color = forming.delta >= 0 ? CONFIG.bull : CONFIG.bear;
    document.getElementById('formingBody').textContent = forming.volumeTotal > 0 ? ((forming.volumeBody / forming.volumeTotal) * 100).toFixed(0) + '%' : '0%';
    document.getElementById('formingWick').textContent = forming.wickPercent.toFixed(0) + '%';
    const absEl = document.getElementById('formingAbsorptions');
    if (forming.absorptionCount > 0) {
      absEl.style.display = 'inline';
      absEl.textContent = '🧩 ' + forming.absorptionCount + ' abs (' + forming.absorptionBuyCount + 'B / ' + forming.absorptionSellCount + 'S)';
    } else {
      absEl.style.display = 'none';
    }
    const stackEl = document.getElementById('formingStacking');
    if (forming.maxStackingBuy >= 2 || forming.maxStackingSell >= 2) {
      stackEl.style.display = 'inline';
      stackEl.style.color = forming.maxStackingBuy > forming.maxStackingSell ? CONFIG.absorptionBuy : CONFIG.absorptionSell;
      stackEl.style.fontWeight = '700';
      stackEl.textContent = '🔥 Stack B' + forming.maxStackingBuy + '/S' + forming.maxStackingSell;
    } else {
      stackEl.style.display = 'none';
    }
    const fill = document.getElementById('deltaBarFill');
    const pct = Math.min(100, (Math.abs(forming.delta) / threshold) * 100);
    fill.style.width = pct + '%';
    fill.style.background = forming.delta >= 0 ? CONFIG.bull : CONFIG.bear;
  } else {
    bar.classList.remove('visible');
  }
}

function updateEnginePanel() {
  const e = engineState;
  if (e.tick_velocity) {
    document.getElementById('eng_velocity').textContent = (e.tick_velocity.velocity || 0).toFixed(1) + ' t/s';
    document.getElementById('eng_velocity_base').textContent = (e.tick_velocity.baseline || 0).toFixed(1);
    document.getElementById('eng_burst').style.display = e.tick_velocity.is_burst ? 'inline' : 'none';
  }
  if (e.micro_cluster) {
    const absEl = document.getElementById('eng_absorption');
    if (e.micro_cluster.is_absorption) {
      const isBuy = e.micro_cluster.absorption_type === 'buy_absorption';
      absEl.textContent = isBuy ? '🟢 BUY ABS' : '🔴 SELL ABS';
      absEl.style.color = isBuy ? CONFIG.absorptionBuy : CONFIG.absorptionSell;
    } else {
      absEl.textContent = 'Sem absorção';
      absEl.style.color = CONFIG.text;
    }
    document.getElementById('eng_abs_total').textContent = e.micro_cluster.total_absorptions || 0;
  }
  if (e.atr_normalize) {
    const atr = e.atr_normalize.atr;
    document.getElementById('eng_atr').textContent = atr ? (atr * 100).toFixed(4) : '--';
    const regimeEl = document.getElementById('eng_atr_regime');
    regimeEl.textContent = e.atr_normalize.regime || 'warmup';
    regimeEl.style.color = e.atr_normalize.regime === 'expanding' ? CONFIG.absorptionSell : e.atr_normalize.regime === 'contracting' ? CONFIG.absorptionBuy : CONFIG.text;
  }
  if (e.imbalance_detector) {
    document.getElementById('eng_stack_buy').textContent = 'Buy: S' + (e.imbalance_detector.stacking_buy || 0);
    document.getElementById('eng_stack_sell').textContent = 'Sell: S' + (e.imbalance_detector.stacking_sell || 0);
    const dom = document.getElementById('eng_dominant');
    if (e.imbalance_detector.dominant_direction) {
      dom.textContent = '→ ' + e.imbalance_detector.dominant_direction.toUpperCase();
      dom.style.color = e.imbalance_detector.dominant_direction === 'buy' ? CONFIG.absorptionBuy : CONFIG.absorptionSell;
    } else {
      dom.textContent = '';
    }
  }
  if (e.spread_weight) {
    document.getElementById('eng_vol').textContent = (e.spread_weight.volatility || 0).toFixed(2) + ' bps';
    const regEl = document.getElementById('eng_vol_regime');
    regEl.textContent = e.spread_weight.regime || '--';
    regEl.style.color = e.spread_weight.regime === 'high' ? CONFIG.absorptionSell : e.spread_weight.regime === 'low' ? CONFIG.absorptionBuy : CONFIG.text;
  }
  const signal = e.micro_cluster?.signal || 0;
  const sigEl = document.getElementById('eng_signal');
  sigEl.textContent = (signal * 100).toFixed(0) + '%';
  sigEl.style.color = signal > 0.2 ? CONFIG.absorptionBuy : signal < -0.2 ? CONFIG.absorptionSell : CONFIG.text;
  const labEl = document.getElementById('eng_signal_label');
  labEl.textContent = signal > 0 ? 'bullish' : signal < 0 ? 'bearish' : 'neutro';
}

// Start
document.addEventListener('DOMContentLoaded', init);
'''

# Criar arquivos
create_file('frontend/index.html', index_html)
create_file('frontend/js/app.js', app_js)

print("\n✅ Frontend do ImbalanceChart v7 criado com sucesso!")
print("🚀 Execute o backend e acesse http://localhost:8001")