/**
 * AIAnalysisView.js
 * Painel de visualização de análises da IA
 */

class AIAnalysisView {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentAnalysis = null;
    }
    
    showAnalysis(analysis) {
        this.currentAnalysis = analysis;
        
        if (!analysis || !analysis.success) {
            this.showEmpty();
            return;
        }
        
        const html = `
            <div class="ai-analysis-content">
                <div class="analysis-header">
                    <h3>🔍 Análise de Região</h3>
                    <span class="confidence-badge ${this.getConfidenceClass(analysis.confidence)}">
                        ${(analysis.confidence * 100).toFixed(0)}% confiança
                    </span>
                </div>
                
                <div class="pattern-section">
                    <div class="pattern-icon">${this.getPatternEmoji(analysis.pattern)}</div>
                    <div class="pattern-info">
                        <div class="pattern-name">${analysis.pattern || 'Indefinido'}</div>
                        <div class="pattern-desc">${this.getPatternDescription(analysis.pattern)}</div>
                    </div>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric">
                        <label>Preço Inicial</label>
                        <value>${analysis.region?.start_price?.toFixed(5) || '-'}</value>
                    </div>
                    <div class="metric">
                        <label>Preço Final</label>
                        <value>${analysis.region?.end_price?.toFixed(5) || '-'}</value>
                    </div>
                    <div class="metric">
                        <label>Distância</label>
                        <value>${analysis.region ? 
                            (analysis.region.end_price - analysis.region.start_price).toFixed(5) 
                            : '-'}</value>
                    </div>
                    <div class="metric">
                        <label>Barras</label>
                        <value>${analysis.region ? 
                            (analysis.region.end_idx - analysis.region.start_idx) 
                            : '-'}</value>
                    </div>
                </div>
                
                <div class="narrative-section">
                    <h4>📖 Narrativa</h4>
                    <p>${analysis.narrative || 'Sem narrativa disponível'}</p>
                </div>
                
                ${analysis.key_levels ? `
                <div class="levels-section">
                    <h4>🎯 Níveis Identificados</h4>
                    <ul>
                        ${analysis.key_levels.map(l => `
                            <li class="level-${l.type}">${l.type}: ${l.price.toFixed(5)}</li>
                        `).join('')}
                    </ul>
                </div>
                ` : ''}
                
                ${analysis.prediction ? `
                <div class="prediction-section">
                    <h4>🔮 Predição</h4>
                    <div class="prediction-bar">
                        <div class="prob-up" style="width: ${analysis.prediction.probability_up * 100}%">
                            📈 ${(analysis.prediction.probability_up * 100).toFixed(0)}%
                        </div>
                        <div class="prob-down" style="width: ${analysis.prediction.probability_down * 100}%">
                            📉 ${(analysis.prediction.probability_down * 100).toFixed(0)}%
                        </div>
                    </div>
                    <div class="expected-return">
                        Retorno esperado: ${analysis.prediction.expected_return > 0 ? '+' : ''}
                        ${(analysis.prediction.expected_return * 100).toFixed(2)}%
                    </div>
                </div>
                ` : ''}
                
                <div class="recommendation ${analysis.recommendation?.toLowerCase().replace(' ', '-')}">
                    💡 ${analysis.recommendation || 'Aguardar'}
                </div>
            </div>
        `;
        
        this.container.innerHTML = html;
    }
    
    showEmpty() {
        this.container.innerHTML = `
            <div class="empty-state">
                <p>Selecione uma região no gráfico (Shift+Click e arraste) para analisar</p>
            </div>
        `;
    }
    
    getConfidenceClass(confidence) {
        if (confidence > 0.8) return 'high';
        if (confidence > 0.6) return 'medium';
        return 'low';
    }
    
    getPatternEmoji(pattern) {
        const emojis = {
            'trend_continuation': '📈',
            'trend_reversal': '🔄',
            'accumulation': '⬇️',
            'distribution': '⬆️',
            'absorption': '⚖️',
            'breakout': '💥',
            'mean_reversion': '📊'
        };
        return emojis[pattern] || '🔍';
    }
    
    getPatternDescription(pattern) {
        const descriptions = {
            'trend_continuation': 'Tendência atual deve continuar',
            'trend_reversal': 'Possível reversão de tendência',
            'accumulation': 'Acumulação institucional detectada',
            'distribution': 'Distribuição institucional detectada',
            'absorption': 'Absorção de fluxo no nível atual',
            'breakout': 'Rompimento de nível importante',
            'mean_reversion': 'Retorno à média estatística'
        };
        return descriptions[pattern] || 'Padrão não categorizado';
    }
}

window.AIAnalysisView = AIAnalysisView;