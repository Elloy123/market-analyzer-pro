/**
 * AIOrchestrator.js
 * Coordena todas as análises de IA no frontend
 */

class AIOrchestrator {
    constructor(wsClient) {
        this.ws = wsClient;
        this.analyses = new Map();
        this.currentAnalysis = null;
        this.attentionHeatmap = null;
        
        this.setupListeners();
    }
    
    setupListeners() {
        // Escuta mensagens do WebSocket
        this.ws.addListener('region_analysis', (data) => {
            this.handleRegionAnalysis(data);
        });
        
        this.ws.addListener('attention_heatmap', (data) => {
            this.handleAttentionHeatmap(data);
        });
        
        this.ws.addListener('route_analysis', (data) => {
            this.handleRouteAnalysis(data);
        });
    }
    
    // API Pública
    
    analyzeRegion(startIdx, endIdx) {
        this.ws.send({
            type: 'analyze_region',
            start_idx: startIdx,
            end_idx: endIdx
        });
    }
    
    getAttentionHeatmap(centerIdx, window = 20) {
        this.ws.send({
            type: 'attention_heatmap',
            center_idx: centerIdx,
            window: window
        });
    }
    
    analyzeRoute(targetIdx) {
        this.ws.send({
            type: 'route_analysis',
            target_idx: targetIdx
        });
    }
    
    sendFeedback(predicted, actual) {
        this.ws.send({
            type: 'ai_feedback',
            predicted: predicted,
            actual: actual
        });
    }
    
    // Handlers
    
    handleRegionAnalysis(data) {
        if (data.success) {
            this.currentAnalysis = {
                type: 'region',
                ...data
            };
            this.onAnalysisUpdate?.(this.currentAnalysis);
        }
    }
    
    handleAttentionHeatmap(data) {
        if (data.success) {
            this.attentionHeatmap = data.heatmap;
            this.onAttentionUpdate?.(data);
        }
    }
    
    handleRouteAnalysis(data) {
        if (data.success) {
            this.onRouteUpdate?.(data);
        }
    }
    
    // Geração de Narrativas
    
    generateNarrative(analysis) {
        if (!analysis) return 'Aguardando análise...';
        
        const lines = [];
        
        // Padrão detectado
        if (analysis.pattern) {
            const patternEmojis = {
                'trend_continuation': '📈',
                'trend_reversal': '🔄',
                'accumulation': '⬇️',
                'distribution': '⬆️',
                'absorption': '⚖️',
                'breakout': '💥',
                'mean_reversion': '📊'
            };
            lines.push(`${patternEmojis[analysis.pattern] || '🔍'} Padrão: ${analysis.pattern}`);
        }
        
        // Confiança
        if (analysis.confidence) {
            const confidencePct = (analysis.confidence * 100).toFixed(0);
            lines.push(`🎯 Confiança: ${confidencePct}%`);
        }
        
        // Recomendação
        if (analysis.recommendation) {
            lines.push(`💡 ${analysis.recommendation}`);
        }
        
        // Narrativa completa
        if (analysis.narrative) {
            lines.push('');
            lines.push(analysis.narrative);
        }
        
        return lines.join('\n');
    }
}

window.AIOrchestrator = AIOrchestrator;