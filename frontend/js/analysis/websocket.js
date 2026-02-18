/**
 * WebSocket Manager
 */

class WebSocketManager {
    constructor(url = 'ws://localhost:8765') {
        this.url = url;
        this.ws = null;
        this.isConnected = false;
        this.listeners = [];
        this.reconnectInterval = 3000;
        this.reconnectTimer = null;
    }

    connect() {
        try {
            this.ws = new WebSocket(this.url);

            this.ws.onopen = () => {
                console.log('✅ WebSocket conectado');
                this.isConnected = true;
                this.notify({ type: 'connection', status: 'connected' });
                clearTimeout(this.reconnectTimer);
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.notify(data);
                } catch (e) {
                    console.error('Erro ao parsear:', e);
                }
            };

            this.ws.onerror = (error) => {
                console.error('❌ WebSocket erro:', error);
                this.isConnected = false;
            };

            this.ws.onclose = () => {
                console.log('🔌 WebSocket desconectado');
                this.isConnected = false;
                this.notify({ type: 'connection', status: 'disconnected' });
                
                // Reconectar
                this.reconnectTimer = setTimeout(() => {
                    console.log('🔄 Reconectando...');
                    this.connect();
                }, this.reconnectInterval);
            };

        } catch (err) {
            console.error('Falha ao criar WebSocket:', err);
        }
    }

    send(data) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
            return true;
        }
        return false;
    }

    onMessage(callback) {
        this.listeners.push(callback);
        return () => {
            this.listeners = this.listeners.filter(cb => cb !== callback);
        };
    }

    notify(data) {
        this.listeners.forEach(cb => cb(data));
    }

    // API Methods
    switchSymbol(symbol) {
        return this.send({ type: 'switch_symbol', symbol });
    }

    analyzeRegion(startIdx, endIdx) {
        return this.send({ type: 'analyze_region', start_idx: startIdx, end_idx: endIdx });
    }

    getAttentionHeatmap(centerIdx, window = 20) {
        return this.send({ type: 'attention_heatmap', center_idx: centerIdx, window });
    }

    getRouteAnalysis(targetIdx) {
        return this.send({ type: 'route_analysis', target_idx: targetIdx });
    }

    sendFeedback(predicted, actual) {
        return this.send({ type: 'ai_feedback', predicted, actual });
    }
}

// Singleton
const wsManager = new WebSocketManager();