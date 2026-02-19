/**
 * VolumeProfile.js
 * Calcula e exibe perfil de volume no gráfico
 */

class VolumeProfile {
    constructor(chart) {
        this.chart = chart;
        this.levels = 24;
        this.profile = null;
    }
    
    calculate(clusters) {
        if (clusters.length === 0) return null;
        
        // Encontra range de preço
        let minPrice = Infinity;
        let maxPrice = -Infinity;
        let totalVolume = 0;
        
        clusters.forEach(c => {
            minPrice = Math.min(minPrice, c.low);
            maxPrice = Math.max(maxPrice, c.high);
            totalVolume += c.volume;
        });
        
        // Cria níveis de preço usando step_price
        const step = this.chart.config.stepPrice;
        const range = maxPrice - minPrice;
        const nLevels = Math.max(this.levels, Math.ceil(range / step));
        
        const levelVolumes = new Array(nLevels).fill(0);
        const levelDeltas = new Array(nLevels).fill(0);
        
        // Distribui volume em níveis
        clusters.forEach(c => {
            const centerPrice = (c.high + c.low) / 2;
            const levelIdx = Math.floor((centerPrice - minPrice) / step);
            
            if (levelIdx >= 0 && levelIdx < nLevels) {
                levelVolumes[levelIdx] += c.volume;
                levelDeltas[levelIdx] += c.delta;
            }
        });
        
        // Encontra POC (Point of Control)
        let maxVol = 0;
        let pocIdx = 0;
        levelVolumes.forEach((vol, i) => {
            if (vol > maxVol) {
                maxVol = vol;
                pocIdx = i;
            }
        });
        
        // Calcula Value Area (70% do volume)
        const sortedLevels = levelVolumes.map((v, i) => ({ vol: v, idx: i }))
            .sort((a, b) => b.vol - a.vol);
        
        let cumsum = 0;
        const vaLevels = [];
        const target = totalVolume * 0.7;
        
        for (const { vol, idx } of sortedLevels) {
            cumsum += vol;
            vaLevels.push(idx);
            if (cumsum >= target) break;
        }
        
        this.profile = {
            POC: minPrice + (pocIdx * step),
            valueArea: {
                low: minPrice + (Math.min(...vaLevels) * step),
                high: minPrice + (Math.max(...vaLevels) * step)
            },
            levels: levelVolumes.map((vol, i) => ({
                price: minPrice + (i * step),
                volume: vol,
                delta: levelDeltas[i]
            })),
            totalVolume
        };
        
        return this.profile;
    }
    
    draw(ctx, width, height, priceToY) {
        if (!this.profile) return;
        
        const maxVol = Math.max(...this.profile.levels.map(l => l.volume));
        const barWidth = 60;
        
        // Desenha barras horizontais de volume
        this.profile.levels.forEach(level => {
            if (level.volume < 1) return;
            
            const y = priceToY(level.price);
            const barLength = (level.volume / maxVol) * barWidth;
            
            // Cor baseada no delta
            const deltaRatio = level.delta / level.volume;
            let color;
            if (deltaRatio > 0.3) color = '#26a69a';
            else if (deltaRatio < -0.3) color = '#ef5350';
            else color = '#78909c';
            
            ctx.fillStyle = color;
            ctx.globalAlpha = 0.5;
            ctx.fillRect(width - barLength - 5, y - 1, barLength, 2);
            ctx.globalAlpha = 1;
        });
    }
}

window.VolumeProfile = VolumeProfile;