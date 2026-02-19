/**
 * app.js
 * Aplicação principal que integra todos os componentes
 */

class MarketAnalyzerApp {
    constructor() {
        this.ws = null;
        this.chart = null;
        this.regionSelector = null;
        this.aiOrchestrator = null;
        this.analysisPanel = null;
        this.aiView = null;
        this.routeView = null;
        
        this.currentSymbol = 'XAUUSD';
        this.clusterConfig = null;
        
        this.init();
    }
    
    async init() {
        // Inicializa WebSocket
        this.ws = new WSClient();
        await this.ws.connect();
        
        // Configura listeners
        this.setupWSListeners();
        
        // Inicializa componentes UI
        this.initChart();
        this.initPanels();
        this.initAI();
        
        // Configura controles
        this.setupControls();
        
        console.log('✅ Market Analyzer Pro iniciado');
    }
    
    setupWSListeners() {
        this.ws.addListener('connected', (data) => {
            console.log('Conectado:', data);
            this.currentSymbol = data.symbol;
            this.clusterConfig = data.config;
            
            // Atualiza chart com config
            if (this.chart && data.config) {
                this.chart.config.clusterThreshold = data.config.delta_th;
                this.chart.config.stepPrice = data.config.step;
            }
        });
        
        this.ws.addListener('tick', (data) => {
            this.onTick(data);
        });
        
        this.ws.addListener('cluster_closed', (data) => {
            this.onClusterClosed(data);
        });
        
        this.ws.addListener('symbol_changed', (data) => {
            this.currentSymbol = data.symbol;
            this.clusterConfig = data.config;
            
            if (this.chart) {
                this.chart.clear();
                this.chart.config.clusterThreshold = data.config.delta_th;
                this.chart.config.stepPrice = data.config.step;
            }
        });
    }
    
    initChart() {
        const canvas = document.getElementById('mainChart');
        if (!canvas) return;
        
        // Configuração inicial (será atualizada pelo servidor)
        this.chart = new AtemporalChart('mainChart', {
            clusterThreshold: 100,
            stepPrice: 0.5
        });
        
        // Seletor de região
        this.regionSelector = new RegionSelector(this.chart);
        this.regionSelector.onRegionSelected = (region) => {
            this.aiOrchestrator.analyzeRegion(region.startIndex, region.endIndex);
        };
        
        // Click em barra
        this.chart.onBarClick = (cluster, index) => {
            this.aiOrchestrator.analyzeRoute(index);
        };
        
        // Resize handler
        window.addEventListener('resize', () => {
            this.chart.resize();
        });
    }
    
    initPanels() {
        // Painel de análise em tempo real
        const marketPanel = document.getElementById('marketPanel');
        if (marketPanel) {
            this.analysisPanel = new MarketAnalysisPanel('marketPanel');
        }
        
        // View de análise da IA
        const aiPanel = document.getElementById('aiPanel');
        if (aiPanel) {
            this.aiView = new AIAnalysisView('aiPanel');
        }
        
        // View de rota
        const routePanel = document.getElementById('routePanel');
        if (routePanel) {
            this.routeView = new RegionAnalysisView('routePanel');
        }
    }
    
    initAI() {
        this.aiOrchestrator = new AIOrchestrator(this.ws);
        
        this.aiOrchestrator.onAnalysisUpdate = (analysis) => {
            this.aiView?.showAnalysis(analysis);
        };
        
        this.aiOrchestrator.onRouteUpdate = (data) => {
            this.routeView?.showRouteAnalysis(data);
        };
        
        this.aiOrchestrator.onAttentionUpdate = (data) => {
            // Atualiza visualização de atenção no gráfico
            console.log('Attention update:', data);
        };
    }
    
    setupControls() {
        // Seletor de símbolo
        const symbolSelect = document.getElementById('symbolSelect');
        if (symbolSelect) {
            symbolSelect.addEventListener('change', (e) => {
                this.switchSymbol(e.target.value);
            });
        }
        
        // Botão de limpar
        const clearBtn = document.getElementById('clearBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.chart?.clear();
            });
        }
        
        // Botão de análise manual
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => {
                // Analisa últimas 50 barras
                const end = this.chart.clusters.length - 1;
                const start = Math.max(0, end - 50);
                this.aiOrchestrator.analyzeRegion(start, end);
            });
        }
    }
    
    onTick(data) {
        // Adiciona ao gráfico
        if (this.chart) {
            this.chart.addTick(data);
        }
        
        // Atualiza painel
        if (this.analysisPanel) {
            this.analysisPanel.update(data);
        }
    }
    
    onClusterClosed(data) {
        // Cluster fechado pelo backend
        if (this.chart) {
            this.chart.addCluster(data);
        }
    }
    
    switchSymbol(symbol) {
        this.ws.send({
            type: 'switch_symbol',
            symbol: symbol
        });
    }
}

// Inicialização quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MarketAnalyzerApp();
});