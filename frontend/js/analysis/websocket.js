/**
 * websocket.js
 * Cliente WebSocket robusto para comunicação com o backend
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
                console.log(`🔌 Conectando a ${this.url}...`);
                this.ws = new WebSocket(this.url);

                this.ws.onopen = () => {
                    console.log('✅ WebSocket conectado');
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
                        console.error('❌ Erro ao parsear mensagem:', e);
                    }
                };

                this.ws.onclose = () => {
                    console.log('🔌 WebSocket fechado');
                    this.isConnected = false;
                    this.attemptReconnect();
                };

                this.ws.onerror = (error) => {
                    console.error('❌ Erro WebSocket:', error);
                    reject(error);
                };

            } catch (error) {
                console.error('❌ Erro ao criar WebSocket:', error);
                reject(error);
            }
        });
    }

    handleMessage(data) {
        const type = data.type || 'unknown';
        
        // Log para debug
        if (type === 'tick') {
            // Não loga ticks para não poluir console
        } else {
            console.log(`📨 Mensagem recebida: ${type}`, data);
        }

        // Notifica listeners específicos
        if (this.listeners.has(type)) {
            this.listeners.get(type).forEach(callback => {
                try {
                    callback(data.data || data);
                } catch (e) {
                    console.error(`❌ Erro no listener de ${type}:`, e);
                }
            });
        }

        // Notifica listeners genéricos
        if (this.listeners.has('*')) {
            this.listeners.get('*').forEach(callback => {
                try {
                    callback(data);
                } catch (e) {
                    console.error('❌ Erro no listener global:', e);
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

    removeListener(event, callback) {
        if (this.listeners.has(event)) {
            const index = this.listeners.get(event).indexOf(callback);
            if (index > -1) {
                this.listeners.get(event).splice(index, 1);
            }
        }
    }

    emit(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (e) {
                    console.error(`❌ Erro ao emitir ${event}:`, e);
                }
            });
        }
    }

    send(data) {
        const message = typeof data === 'string' ? data : JSON.stringify(data);
        
        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message);
        } else {
            console.log('⏳ Mensagem enfileirada (WebSocket não conectado)');
            this.messageQueue.push(message);
        }
    }

    flushQueue() {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.ws.send(message);
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('❌ Máximo de tentativas de reconexão atingido');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);
        
        console.log(`🔄 Tentando reconectar em ${delay}ms (tentativa ${this.reconnectAttempts})`);
        
        setTimeout(() => {
            this.connect().catch(() => {
                // Erro já é logado no connect
            });
        }, delay);
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }

    // Métodos utilitários
    
    switchSymbol(symbol) {
        this.send({
            type: 'switch_symbol',
            symbol: symbol
        });
    }

    requestHistory(symbol, hours = 24) {
        this.send({
            type: 'get_history',
            symbol: symbol,
            hours: hours
        });
    }

    analyzeRegion(startIdx, endIdx) {
        this.send({
            type: 'analyze_region',
            start_idx: startIdx,
            end_idx: endIdx
        });
    }

    getAttentionHeatmap(centerIdx, window = 20) {
        this.send({
            type: 'attention_heatmap',
            center_idx: centerIdx,
            window: window
        });
    }

    analyzeRoute(targetIdx) {
        this.send({
            type: 'route_analysis',
            target_idx: targetIdx
        });
    }

    sendFeedback(predicted, actual) {
        this.send({
            type: 'ai_feedback',
            predicted: predicted,
            actual: actual
        });
    }
}

// Exporta para uso global
window.WSClient = WSClient;