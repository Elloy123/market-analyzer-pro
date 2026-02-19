/**
 * AttentionVisualizer.js
 * Visualiza heatmap de atenção da IA sobre o gráfico
 */

class AttentionVisualizer {
    constructor(chart) {
        this.chart = chart;
        this.heatmap = null;
        this.zones = [];
    }
    
    setHeatmap(heatmapData) {
        this.heatmap = heatmapData.heatmap;
        this.zones = heatmapData.zones || [];
        this.draw();
    }
    
    draw() {
        if (!this.heatmap || !this.chart.clusters.length) return;
        
        const ctx = this.chart.ctx;
        const width = this.chart.canvas.width / window.devicePixelRatio;
        const height = this.chart.canvas.height / window.devicePixelRatio;
        
        // Mapeia heatmap para clusters visíveis
        const startIdx = 0;
        const endIdx = this.chart.clusters.length;
        
        this.heatmap.forEach((value, i) => {
            const clusterIdx = startIdx + i;
            if (clusterIdx >= this.chart.clusters.length) return;
            
            const x = this.chart.indexToX(clusterIdx);
            const intensity = value; // 0 a 1
            
            // Cor baseada na intensidade
            const r = Math.floor(255 * intensity);
            const g = Math.floor(100 * (1 - intensity));
            const b = Math.floor(100 * (1 - intensity));
            
            ctx.fillStyle = `rgba(${r}, ${g}, ${b}, 0.3)`;
            ctx.fillRect(x - 10, 0, 20, height);
        });
        
        // Destaca zonas de alta atenção
        this.zones.forEach(zone => {
            if (zone.type === 'high') {
                const x = this.chart.indexToX(zone.center);
                ctx.strokeStyle = '#ff5722';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, height);
                ctx.stroke();
            }
        });
    }
    
    clear() {
        this.heatmap = null;
        this.zones = [];
    }
}

window.AttentionVisualizer = AttentionVisualizer;