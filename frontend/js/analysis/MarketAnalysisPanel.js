/**
 * MarketAnalysisPanel.js
 * Painel principal de análise de mercado em tempo real
 */

class MarketAnalysisPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentData = null;
    }
    
    update(data) {
        this.currentData = data;
        
        const analysis = data.analysis || {};
        const setup = analysis.setup || {};
        
        const html = `
            <div class="market-analysis-live">
                <div class="bar-info">
                    <div class="bar-type ${analysis.bar_type?.toLowerCase()}">
                        ${this.getBarTypeIcon(analysis.bar_type)} ${analysis.bar_type || 'NORMAL'}
                    </div>
                    <div class="execution-style">
                        ${this.getExecutionIcon(analysis.execution_style)} ${analysis.execution_style || 'Unknown'}
                    </div>
                </div>
                
                <div class="metrics-row">
                    <div class="metric-box">
                        <span class="label">Pressão</span>
                        <span class="value ${analysis.execution_pressure > 0 ? 'buy' : 'sell'}">
                            ${analysis.execution_pressure > 0 ? '+' : ''}
                            ${(analysis.execution_pressure || 0).toFixed(2)}
                        </span>
                    </div>
                    <div class="metric-box">
                        <span class="label">Agressivo</span>
                        <span class="value">
                            ${((analysis.aggressive_ratio || 0) * 100).toFixed(0)}%
                        </span>
                    </div>
                </div>
                
                ${analysis.ai_prediction ? `
                <div class="ai-prediction">
                    <div class="prediction-header">
                        <span>🧠 IA Prediction</span>
                        <span class="confidence">${(analysis.ai_prediction.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div class="direction ${analysis.ai_prediction.direction.toLowerCase()}">
                        ${analysis.ai_prediction.direction}
                    </div>
                    <div class="probabilities">
                        <div class="prob-up" style="width: ${analysis.ai_prediction.probability_up * 100}%"></div>
                        <div class="prob-down" style="width: ${analysis.ai_prediction.probability_down * 100}%"></div>
                    </div>
                </div>
                ` : ''}
                
                ${setup.valid ? `
                <div class="setup-box ${setup.direction.toLowerCase()}">
                    <div class="setup-header">
                        🎯 Setup: ${setup.direction}
                    </div>
                    <div class="setup-details">
                        <div>Entry: ${setup.entry.toFixed(5)}</div>
                        <div>Stop: ${setup.stop.toFixed(5)}</div>
                        <div>Target: ${setup.target.toFixed(5)}</div>
                        <div>RR: ${((setup.target - setup.entry) / (setup.entry - setup.stop)).toFixed(2)}</div>
                    </div>
                    <div class="setup-confidence">
                        Confiança: ${(setup.confidence * 100).toFixed(0)}%
                    </div>
                </div>
                ` : ''}
                
                <div class="narrative-box">
                    <pre>${analysis.narrative || 'Aguardando dados...'}</pre>
                </div>
            </div>
        `;
        
        this.container.innerHTML = html;
    }
    
    getBarTypeIcon(type) {
        const icons = {
            'IMBALANCE_EXTREME': '🔴',
            'IMBALANCE_STRONG': '🟠',
            'ABSORPTION': '🟡',
            'NORMAL': '⚪'
        };
        return icons[type] || '⚪';
    }
    
    getExecutionIcon(style) {
        const icons = {
            'AGGRESSIVE_DOMINANT': '⚡',
            'PASSIVE_DOMINANT': '🛡️',
            'BALANCED': '⚖️'
        };
        return icons[style] || '⚖️';
    }
}

window.MarketAnalysisPanel = MarketAnalysisPanel;