/**
 * AtemporalChart.js - Gráfico atemporal por desequilíbrio de volume
 */
class AtemporalChart {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error('Canvas não encontrado:', canvasId);
            return;
        }
        this.ctx = this.canvas.getContext('2d');
        this.config = {
            clusterThreshold: options.clusterThreshold || 100,
            stepPrice: options.stepPrice || 0.5,
            maxClusters: options.maxClusters || 200,
            colors: { 
                buy: '#26a69a', 
                sell: '#ef5350', 
                neutral: '#78909c', 
                absorption: '#ff9800',
                poc: '#ffd700',
                valueArea: 'rgba(255, 215, 0, 0.1)',
                grid: 'rgba(255,255,255,0.05)', 
                text: '#b0bec5' 
            },
            ...options
        };
        this.clusters = [];
        this.currentCluster = null;
        this.priceRange = { min: Infinity, max: -Infinity };
        this.volumeProfile = null;
        this.selectedRegion = null;
        this.scale = { x: 1, y: 1 };
        this.offset = { x: 0, y: 0 };
        this.isDragging = false;
        this.lastMouse = { x: 0, y: 0 };
        this.hoverCluster = null;
        this.maxVolume = 0;
        
        this.init();
    }
    
    init() {
        this.resize();
        this.setupEvents();
    }
    
    resize() {
        const parent = this.canvas.parentElement;
        if (!parent) return;
        
        this.canvas.width = parent.clientWidth * window.devicePixelRatio;
        this.canvas.height = parent.clientHeight * window.devicePixelRatio;
        this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        this.canvas.style.width = parent.clientWidth + 'px';
        this.canvas.style.height = parent.clientHeight + 'px';
        this.draw();
    }
    
    setupEvents() {
        window.addEventListener('resize', () => this.resize());
        this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
        this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        this.canvas.addEventListener('mouseup', () => this.isDragging = false);
        this.canvas.addEventListener('wheel', (e) => { 
            e.preventDefault(); 
            this.scale.x *= e.deltaY > 0 ? 0.9 : 1.1; 
            this.draw(); 
        });
    }
    
    updatePriceRange(price) {
        this.priceRange.min = Math.min(this.priceRange.min, price);
        this.priceRange.max = Math.max(this.priceRange.max, price);
    }
    
    setSelectedRegion(start, end) {
        this.selectedRegion = { start, end };
        this.draw();
    }
    
    addTick(tick) {
        if (!this.currentCluster) this.startNewCluster(tick);
        
        const c = this.currentCluster;
        const price = tick.price;
        const volume = tick.volume_synthetic || 1;
        const side = tick.side || 'buy';
        
        c.close = price;
        c.high = Math.max(c.high, price);
        c.low = Math.min(c.low, price);
        c.volume += volume;
        
        if (side === 'buy') {
            c.buyVolume += volume;
            c.delta += volume;
        } else {
            c.sellVolume += volume;
            c.delta -= volume;
        }
        
        c.ticks.push(tick);
        c.endTime = tick.timestamp;
        
        this.updatePriceRange(price);
        
        if (this.shouldCloseCluster(c)) {
            this.closeCluster();
        }
        
        this.draw();
    }
    
    addCluster(data) {
        const cluster = {
            open: data.open_price,
            close: data.close_price,
            high: data.high_price,
            low: data.low_price,
            buyVolume: data.buy_volume,
            sellVolume: data.sell_volume,
            volume: data.volume,
            delta: data.delta,
            tickCount: data.tick_count,
            startTime: data.start_time,
            endTime: data.end_time,
            imbalanceRatio: data.imbalance_ratio,
            isClosed: true
        };
        
        this.clusters.push(cluster);
        this.updatePriceRange(cluster.high);
        this.updatePriceRange(cluster.low);
        
        if (this.clusters.length > this.config.maxClusters) {
            this.clusters.shift();
        }
        
        this.draw();
    }
    
    startNewCluster(tick) {
        this.currentCluster = {
            open: tick.price,
            close: tick.price,
            high: tick.price,
            low: tick.price,
            buyVolume: tick.side === 'buy' ? tick.volume_synthetic || 1 : 0,
            sellVolume: tick.side === 'sell' ? tick.volume_synthetic || 1 : 0,
            volume: tick.volume_synthetic || 1,
            delta: tick.side === 'buy' ? (tick.volume_synthetic || 1) : -(tick.volume_synthetic || 1),
            ticks: [tick],
            startTime: tick.timestamp,
            endTime: tick.timestamp,
            tickCount: 1
        };
    }
    
    shouldCloseCluster(c) {
        const cfg = this.config;
        if (Math.abs(c.delta) >= cfg.clusterThreshold) return true;
        if (c.volume >= cfg.clusterThreshold * 3) return true;
        if (c.endTime - c.startTime > 30000) return true;
        if (Math.abs(c.close - c.open) >= cfg.stepPrice * 5) return true;
        return false;
    }
    
    closeCluster() {
        if (!this.currentCluster) return;
        
        const c = this.currentCluster;
        c.isClosed = true;
        c.imbalanceRatio = Math.abs(c.delta) / c.volume;
        
        this.clusters.push({...c});
        
        if (this.clusters.length > this.config.maxClusters) {
            this.clusters.shift();
        }
        
        const lastTick = c.ticks[c.ticks.length - 1];
        this.startNewCluster(lastTick);
        
        if (this.onClusterClose) {
            this.onClusterClose(c);
        }
    }
    
    draw() {
        const ctx = this.ctx;
        const width = this.canvas.width / window.devicePixelRatio;
        const height = this.canvas.height / window.devicePixelRatio;
        
        ctx.clearRect(0, 0, width, height);
        
        if (this.clusters.length === 0 && !this.currentCluster) {
            this.drawEmptyState(width, height);
            return;
        }
        
        this.calculateScale(width, height);
        this.drawGrid(width, height);
        this.drawClusters(width, height);
        
        if (this.currentCluster) {
            this.drawCurrentCluster(width, height);
        }
        
        if (this.selectedRegion) {
            this.drawSelectedRegion(width, height);
        }
        
        this.drawUI(width, height);
    }
    
    calculateScale(width, height) {
        const padding = 50;
        const all = [...this.clusters];
        if (this.currentCluster) all.push(this.currentCluster);
        
        let minP = Infinity, maxP = -Infinity, maxV = 0;
        
        all.forEach(c => {
            minP = Math.min(minP, c.low);
            maxP = Math.max(maxP, c.high);
            maxV = Math.max(maxV, c.volume);
        });
        
        const range = maxP - minP;
        if (range === 0) return;
        
        minP -= range * 0.1;
        maxP += range * 0.1;
        
        this.priceRange = { min: minP, max: maxP };
        this.maxVolume = maxV;
        
        this.scale.y = (height - padding * 2) / (maxP - minP);
        this.scale.x = (width - padding * 2) / Math.max(all.length, 50);
        this.offset.x = padding;
        this.offset.y = padding - minP * this.scale.y;
    }
    
    priceToY(p) {
        return this.canvas.height / window.devicePixelRatio - (p * this.scale.y + this.offset.y);
    }
    
    indexToX(i) {
        return i * this.scale.x + this.offset.x;
    }
    
    drawClusters(width, height) {
        const ctx = this.ctx;
        
        this.clusters.forEach((c, i) => {
            const x = this.indexToX(i);
            const yO = this.priceToY(c.open);
            const yC = this.priceToY(c.close);
            const yH = this.priceToY(c.high);
            const yL = this.priceToY(c.low);
            
            const w = this.scale.x * 0.8;
            const hw = w / 2;
            
            const color = c.delta > 0 ? this.config.colors.buy : 
                         c.delta < 0 ? this.config.colors.sell : 
                         this.config.colors.neutral;
            
            const isAbs = c.imbalanceRatio < 0.3 && c.volume > 20;
            const finalColor = isAbs ? this.config.colors.absorption : color;
            
            ctx.strokeStyle = finalColor;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(x, yH);
            ctx.lineTo(x, yL);
            ctx.stroke();
            
            const t = Math.min(yO, yC);
            const h = Math.abs(yC - yO) || 1;
            
            ctx.fillStyle = finalColor;
            ctx.globalAlpha = 0.3 + (c.imbalanceRatio * 0.7);
            ctx.fillRect(x - hw, t, w, h || 2);
            ctx.globalAlpha = 1;
            ctx.strokeRect(x - hw, t, w, h || 2);
        });
    }
    
    drawCurrentCluster(width, height) {
        const ctx = this.ctx;
        const c = this.currentCluster;
        const x = this.indexToX(this.clusters.length);
        
        const yO = this.priceToY(c.open);
        const yC = this.priceToY(c.close);
        const yH = this.priceToY(c.high);
        const yL = this.priceToY(c.low);
        
        ctx.setLineDash([5, 5]);
        ctx.strokeStyle = this.config.colors.neutral;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x, yH);
        ctx.lineTo(x, yL);
        ctx.stroke();
        
        const t = Math.min(yO, yC);
        const h = Math.abs(yC - yO) || 1;
        ctx.strokeRect(x - 10, t, 20, h || 2);
        ctx.setLineDash([]);
        
        const prog = Math.abs(c.delta) / this.config.clusterThreshold;
        ctx.fillStyle = prog > 0.8 ? '#ff9800' : '#4caf50';
        ctx.fillRect(x - 15, yL + 5, 30 * Math.min(prog, 1), 3);
    }
    
    drawSelectedRegion(width, height) {
        const ctx = this.ctx;
        const { start, end } = this.selectedRegion;
        
        const x1 = this.indexToX(start);
        const x2 = this.indexToX(end);
        
        ctx.fillStyle = 'rgba(33, 150, 243, 0.2)';
        ctx.fillRect(x1, 0, x2 - x1, height);
        
        ctx.strokeStyle = '#2196f3';
        ctx.lineWidth = 1;
        ctx.strokeRect(x1, 0, x2 - x1, height);
    }
    
    drawGrid(width, height) {
        const ctx = this.ctx;
        const step = this.config.stepPrice;
        
        if (!this.priceRange || this.priceRange.min === Infinity) return;
        
        const minP = Math.floor(this.priceRange.min / step) * step;
        const maxP = Math.ceil(this.priceRange.max / step) * step;
        
        ctx.strokeStyle = this.config.colors.grid;
        ctx.lineWidth = 1;
        
        for (let p = minP; p <= maxP; p += step * 5) {
            const y = this.priceToY(p);
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
            
            ctx.fillStyle = this.config.colors.text;
            ctx.font = '10px monospace';
            ctx.fillText(p.toFixed(2), 5, y - 2);
        }
    }
    
    drawUI(width, height) {
        const ctx = this.ctx;
        
        if (this.currentCluster) {
            ctx.fillStyle = '#fff';
            ctx.font = '12px monospace';
            const c = this.currentCluster;
            const deltaPct = c.volume > 0 ? ((c.delta / c.volume) * 100).toFixed(1) : '0';
            ctx.fillText(
                'Delta: ' + c.delta.toFixed(1) + ' (' + deltaPct + '%) | Vol: ' + c.volume.toFixed(1) + ' | Ticks: ' + c.tickCount,
                10, 20
            );
        }
        
        ctx.fillStyle = this.config.colors.text;
        ctx.font = '11px monospace';
        ctx.fillText('Clusters: ' + this.clusters.length, 10, height - 10);
    }
    
    drawEmptyState(width, height) {
        const ctx = this.ctx;
        ctx.fillStyle = this.config.colors.text;
        ctx.font = '14px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('Aguardando dados...', width / 2, height / 2);
        ctx.textAlign = 'left';
    }
    
    onMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) * window.devicePixelRatio;
        
        this.isDragging = true;
        this.lastMouse = { x };
        
        const idx = this.getClusterAtX(x);
        if (idx !== null) {
            if (e.shiftKey && this.onRegionSelect) {
                this.onRegionSelect(idx);
            } else if (this.onBarClick) {
                this.onBarClick(this.clusters[idx], idx);
            }
        }
    }
    
    onMouseMove(e) {
        if (!this.isDragging) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) * window.devicePixelRatio;
        
        this.offset.x += x - this.lastMouse.x;
        this.lastMouse = { x };
        this.draw();
    }
    
    getClusterAtX(x) {
        const rx = x - this.offset.x;
        const idx = Math.round(rx / this.scale.x);
        return (idx >= 0 && idx < this.clusters.length) ? idx : null;
    }
    
    clear() {
        this.clusters = [];
        this.currentCluster = null;
        this.priceRange = { min: Infinity, max: -Infinity };
        this.selectedRegion = null;
        this.draw();
    }
}

window.AtemporalChart = AtemporalChart;