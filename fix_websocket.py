#!/usr/bin/env python3
"""
Corrige o problema do WSClient não definido
"""

import os

def create_websocket_js():
    """Cria o arquivo websocket.js se não existir ou estiver vazio"""
    
    content = '''/**
 * websocket.js
 * Cliente WebSocket robusto para comunicacao com o backend
 */

class WSClient {
    constructor(url = 'ws://localhost:8766') {
        this.url = url;
        this.ws = null;
        this.listeners = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 1000;
        this.isConnected = false;
        this.messageQueue = [];
    }

    async connect() {
        return new Promise((resolve, reject) => {
            try {
                console.log('Conectando a ' + this.url + '...');
                this.ws = new WebSocket(this.url);

                this.ws.onopen = () => {
                    console.log('WebSocket conectado');
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    this.flushQueue();
                    this.emit('connected', {});
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        this.handleMessage(data);
                    } catch (e) {
                        console.error('Erro ao parsear mensagem:', e);
                    }
                };

                this.ws.onclose = () => {
                    console.log('WebSocket fechado');
                    this.isConnected = false;
                    this.attemptReconnect();
                };

                this.ws.onerror = (error) => {
                    console.error('Erro WebSocket:', error);
                    reject(error);
                };

            } catch (error) {
                console.error('Erro ao criar WebSocket:', error);
                reject(error);
            }
        });
    }

    handleMessage(data) {
        const type = data.type || 'unknown';
        
        if (type !== 'tick') {
            console.log(type + ':', data);
        }

        if (this.listeners.has(type)) {
            this.listeners.get(type).forEach(callback => {
                try {
                    callback(data.data || data);
                } catch (e) {
                    console.error('Erro no listener de ' + type + ':', e);
                }
            });
        }

        if (this.listeners.has('*')) {
            this.listeners.get('*').forEach(callback => {
                try {
                    callback(data);
                } catch (e) {
                    console.error('Erro no listener global:', e);
                }
            });
        }
    }

    addListener(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    emit(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (e) {
                    console.error('Erro ao emitir ' + event + ':', e);
                }
            });
        }
    }

    send(data) {
        const message = typeof data === 'string' ? data : JSON.stringify(data);
        
        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message);
        } else {
            this.messageQueue.push(message);
        }
    }

    flushQueue() {
        while (this.messageQueue.length > 0) {
            this.ws.send(this.messageQueue.shift());
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Maximo de tentativas de reconexao atingido');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);
        
        console.log('Reconectando em ' + delay + 'ms (tentativa ' + this.reconnectAttempts + ')');
        
        setTimeout(() => {
            this.connect().catch(() => {});
        }, delay);
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

window.WSClient = WSClient;
'''

    path = 'frontend/js/analysis/websocket.js'
    
    # Cria diretorio se nao existir
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # Verifica se arquivo existe e tem conteudo (com UTF-8)
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                existing = f.read()
            if len(existing) > 100:
                print(path + ' ja existe e parece valido')
                return
        except:
            pass  # Arquivo corrompido, vai sobrescrever
    
    # Cria arquivo com UTF-8
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('Criado: ' + path)

def update_index_html():
    """Atualiza index.html com ordem correta dos scripts"""
    
    html_content = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Analyzer Pro - IA Integrada</title>
    
    <link rel="stylesheet" href="css/main.css">
    <link rel="stylesheet" href="css/chart.css">
    <link rel="stylesheet" href="css/analysis-panel.css">
    <link rel="stylesheet" href="css/ai-panel.css">
    
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'><text y=\'.9em\' font-size=\'90\'>📊</text></svg>">
</head>
<body>
    <div id="app">
        <header class="main-header">
            <h1>📊 Market Analyzer Pro</h1>
            <div class="controls">
                <select id="symbolSelect">
                    <option value="XAUUSD">XAUUSD</option>
                    <option value="EURUSD">EURUSD</option>
                    <option value="GBPUSD">GBPUSD</option>
                    <option value="BTCUSD">BTCUSD</option>
                    <option value="USTEC">USTEC</option>
                </select>
                <button id="clearBtn">Limpar</button>
                <button id="analyzeBtn">Analisar Regiao</button>
            </div>
        </header>

        <div class="main-layout">
            <div class="chart-container">
                <canvas id="mainChart"></canvas>
                <div class="chart-overlay">
                    <div class="legend">
                        <span class="legend-item"><span class="color-box buy"></span> Compra</span>
                        <span class="legend-item"><span class="color-box sell"></span> Venda</span>
                        <span class="legend-item"><span class="color-box absorption"></span> Absorcao</span>
                    </div>
                </div>
            </div>

            <div class="side-panels">
                <div class="panel">
                    <h3>📈 Analise em Tempo Real</h3>
                    <div id="marketPanel" class="panel-content">
                        <div class="empty-state">Aguardando dados...</div>
                    </div>
                </div>

                <div class="panel">
                    <h3>🤖 Analise da IA</h3>
                    <div id="aiPanel" class="panel-content">
                        <div class="empty-state">
                            Shift+Click: Selecionar regiao<br>
                            Click: Analisar barra
                        </div>
                    </div>
                </div>

                <div class="panel">
                    <h3>🛤️ Analise de Rota</h3>
                    <div id="routePanel" class="panel-content">
                        <div class="empty-state">Selecione uma barra para ver a rota</div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="status-bar">
            <span id="connectionStatus">🟡 Conectando...</span>
            <span id="tickCount">Ticks: 0</span>
            <span id="clusterCount">Clusters: 0</span>
        </footer>
    </div>

    <!-- ORDEM CRITICA: WebSocket PRIMEIRO -->
    <script src="js/analysis/websocket.js"></script>
    <script src="js/chart/AtemporalChart.js"></script>
    <script src="js/chart/RegionSelector.js"></script>
    <script src="js/chart/VolumeProfile.js"></script>
    <script src="js/ai/AIOrchestrator.js"></script>
    <script src="js/ai/AttentionVisualizer.js"></script>
    <script src="js/analysis/AIAnalysisView.js"></script>
    <script src="js/analysis/MarketAnalysisPanel.js"></script>
    <script src="js/analysis/RegionAnalysisView.js"></script>
    <script src="js/app.js"></script>
</body>
</html>'''

    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print('Atualizado: frontend/index.html')

if __name__ == '__main__':
    create_websocket_js()
    update_index_html()
    print('\nPronto! Recarregue a pagina (Ctrl+F5)')