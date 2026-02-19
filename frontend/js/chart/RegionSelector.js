/**
 * RegionSelector.js
 * Gerencia seleção de regiões no gráfico para análise da IA
 */

class RegionSelector {
    constructor(chart) {
        this.chart = chart;
        this.isSelecting = false;
        this.startIndex = null;
        this.endIndex = null;
        this.onRegionSelected = null;
        
        this.setupEvents();
    }
    
    setupEvents() {
        // Shift+Click para iniciar seleção
        this.chart.canvas.addEventListener('mousedown', (e) => {
            if (e.shiftKey) {
                e.preventDefault();
                this.startSelection(e);
            }
        });
        
        this.chart.canvas.addEventListener('mousemove', (e) => {
            if (this.isSelecting) {
                this.updateSelection(e);
            }
        });
        
        this.chart.canvas.addEventListener('mouseup', (e) => {
            if (this.isSelecting) {
                this.endSelection(e);
            }
        });
    }
    
    startSelection(e) {
        const rect = this.chart.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) * window.devicePixelRatio;
        
        this.startIndex = this.chart.getClusterAtX(x);
        if (this.startIndex !== null) {
            this.isSelecting = true;
            this.endIndex = this.startIndex;
        }
    }
    
    updateSelection(e) {
        const rect = this.chart.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) * window.devicePixelRatio;
        
        this.endIndex = this.chart.getClusterAtX(x);
        if (this.endIndex !== null) {
            // Ordena indices
            const start = Math.min(this.startIndex, this.endIndex);
            const end = Math.max(this.startIndex, this.endIndex);
            
            this.chart.setSelectedRegion(start, end);
        }
    }
    
    endSelection(e) {
        if (this.startIndex !== null && this.endIndex !== null) {
            const start = Math.min(this.startIndex, this.endIndex);
            const end = Math.max(this.startIndex, this.endIndex);
            
            if (end > start) {
                // Callback com região selecionada
                this.onRegionSelected?.({
                    startIndex: start,
                    endIndex: end,
                    clusters: this.chart.clusters.slice(start, end + 1)
                });
            }
        }
        
        this.isSelecting = false;
        this.startIndex = null;
        this.endIndex = null;
    }
    
    clear() {
        this.chart.setSelectedRegion(null);
    }
}

window.RegionSelector = RegionSelector;