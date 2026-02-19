/**
 * RegionAnalysisView.js
 * Visualização detalhada de análise de região selecionada
 */

class RegionAnalysisView {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }
    
    showRouteAnalysis(data) {
        if (!data.success) {
            this.container.innerHTML = '<p>Erro na análise de rota</p>';
            return;
        }
        
        const route = data.route;
        const segments = data.segments;
        
        const html = `
            <div class="route-analysis">
                <h4>🛤️ Análise de Rota</h4>
                
                <div class="route-summary">
                    <div class="route-stat">
                        <label>Origem</label>
                        <value>${route.origin_price.toFixed(5)}</value>
                    </div>
                    <div class="route-stat">
                        <label>Destino</label>
                        <value>${route.target_price.toFixed(5)}</value>
                    </div>
                    <div class="route-stat">
                        <label>Distância</label>
                        <value>${route.distance.toFixed(5)}</value>
                    </div>
                    <div class="route-stat">
                        <label>Duração</label>
                        <value>${route.duration_bars} barras</value>
                    </div>
                </div>
                
                <div class="route-quality">
                    <div class="quality-score ${route.quality}">
                        Qualidade: ${route.quality}
                    </div>
                    <div class="exhaustion-level">
                        Exaustão: ${(route.exhaustion * 100).toFixed(0)}%
                    </div>
                </div>
                
                <div class="segments-timeline">
                    <h5>Segmentos</h5>
                    ${segments.map((seg, i) => `
                        <div class="segment ${seg.type.toLowerCase()}">
                            <span class="seg-num">${i + 1}</span>
                            <span class="seg-type">${seg.type}</span>
                            <span class="seg-delta">${seg.delta > 0 ? '+' : ''}${seg.delta.toFixed(1)}</span>
                            <span class="seg-duration">${seg.duration}b</span>
                        </div>
                    `).join('')}
                </div>
                
                <div class="route-report">
                    <pre>${data.report}</pre>
                </div>
            </div>
        `;
        
        this.container.innerHTML = html;
    }
}

window.RegionAnalysisView = RegionAnalysisView;