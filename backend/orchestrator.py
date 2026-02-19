"""
AnalysisOrchestrator - Gerencia todos os analisadores do sistema
Similar ao VolumeEngineOrchestrator mas para análise de contexto
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
import logging

# Imports dos engines de volume
from engines import (
    VolumeImbalanceEngine, 
    ClusterConfig,
    TickVelocityEngine,
    SpreadWeightEngine,
    MicroClusterEngine,
    ATRNormalizeEngine,
    ImbalanceDetectorEngine
)

# Imports dos modelos de IA (com tratamento de erro)
try:
    from ai_models.predictor import OrderFlowPredictor
    from ai_models.local_llm import LocalNarrativeGenerator, NarrativeContext
    from ai_models.integrated_ai import IntegratedAI
    from ai_models.region_analyzer import RegionAnalyzer, RegionPattern
    from ai_models.attention_visualizer import AttentionVisualizer
    from ai_models.route_analyzer import RouteAnalyzer
    from ai_models.absorption_analyzer import AbsorptionAnalyzer, AbsorptionOutcome
    from ai_models.execution_analyzer import ExecutionProfileAnalyzer, ExecutionStyle
except ImportError as e:
    print(f"⚠️ Módulos de IA não encontrados (usando fallback): {e}")
    OrderFlowPredictor = None
    LocalNarrativeGenerator = None
    NarrativeContext = None
    IntegratedAI = None
    RegionAnalyzer = None
    RegionPattern = None
    AttentionVisualizer = None
    RouteAnalyzer = None
    AbsorptionAnalyzer = None
    AbsorptionOutcome = None
    ExecutionProfileAnalyzer = None
    ExecutionStyle = None

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Resultado unificado de todas as análises"""
    timestamp: int
    symbol: str
    price: float
    bar_type: str
    delta: float
    volume: float
    imbalance_ratio: float
    execution_style: str
    aggressive_ratio: float
    execution_pressure: float
    in_absorption_zone: bool
    absorption_info: Optional[Dict]
    ai_prediction: Optional[Dict]
    route_context: Optional[Dict]
    setup: Optional[Dict]
    narrative: str

    def to_dict(self) -> Dict:
        return asdict(self)


class AnalysisOrchestrator:
    """
    Orquestrador central que coordena todos os analisadores
    """
    
    def __init__(self, historical_data: pd.DataFrame = None):
        self.data = historical_data or pd.DataFrame()
        self.symbol = "XAUUSD"
        
        # Engines de volume (NOVOS)
        self.volume_engine = None
        self.velocity_engine = TickVelocityEngine()
        self.spread_engine = SpreadWeightEngine()
        self.micro_cluster_engine = None
        self.atr_engine = ATRNormalizeEngine()
        self.imbalance_engine = ImbalanceDetectorEngine()
        self.cluster_config = None
        
        # Analisadores de IA (com verificação)
        self.predictor = OrderFlowPredictor() if OrderFlowPredictor else None
        self.narrative = LocalNarrativeGenerator() if LocalNarrativeGenerator else None
        self.execution_analyzer = ExecutionProfileAnalyzer(self.data) if ExecutionProfileAnalyzer else None
        self.absorption_analyzer = AbsorptionAnalyzer(self.data) if AbsorptionAnalyzer else None
        self.route_analyzer = None
        self.region_analyzer = None
        self.attention_visualizer = None
        self.integrated_ai = None
        
        # Estado
        self.current_bar = None
        self.recent_bars = []
        self.max_history = 1000
        
        # Treina IA se possível
        if len(self.data) > 200 and self.predictor:
            self._initialize_ai()

    def _initialize_ai(self):
        """Inicializa modelos de IA"""
        try:
            self.predictor.train(self.data)
            if IntegratedAI:
                self.integrated_ai = IntegratedAI(self.data)
            if AttentionVisualizer and self.predictor:
                self.attention_visualizer = AttentionVisualizer(self.predictor)
            logger.info("✅ IA inicializada")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao inicializar IA: {e}")

    def switch_symbol(self, symbol: str, config: dict = None):
        """Troca de símbolo e reinicializa engines"""
        self.symbol = symbol
        
        if config:
            self.cluster_config = ClusterConfig.from_sym_cfg(symbol, config)
            self.volume_engine = VolumeImbalanceEngine(self.cluster_config)
            self.micro_cluster_engine = MicroClusterEngine(
                step_price=config['step'],
                levels=10
            )
        
        # Reseta engines
        self.velocity_engine.reset()
        self.spread_engine.reset()
        self.atr_engine.reset()
        self.imbalance_engine.reset()
        
        logger.info(f"🔄 Símbolo: {symbol}, threshold: {config.get('delta_th', 100) if config else 'N/A'}")

    def update_data(self, new_bar: Dict):
        """Atualiza dados com nova barra/tick"""
        self.current_bar = new_bar
        self.recent_bars.append(new_bar)
        
        if len(self.recent_bars) > self.max_history:
            self.recent_bars.pop(0)
        
        # Processa nos engines de volume
        if self.volume_engine:
            closed_cluster = self.volume_engine.process_tick(new_bar)
            # TODO: emitir evento de cluster fechado se necessário
        
        # Processa em outros engines
        self.velocity_engine.process_tick(new_bar)
        self.spread_engine.process_tick(new_bar)
        
        if self.micro_cluster_engine:
            self.micro_cluster_engine.process_tick(new_bar)
        
        self.atr_engine.process_tick(new_bar)
        
        # Análise de desequilíbrio
        current = self.volume_engine.get_current_cluster() if self.volume_engine else None
        if current:
            self.imbalance_engine.process_tick(
                new_bar, 
                cluster_delta=current.delta,
                cluster_volume=current.volume
            )
        
        # Atualiza DataFrame
        new_row = pd.DataFrame([new_bar])
        self.data = pd.concat([self.data, new_row], ignore_index=True)
        
        if len(self.data) > 10000:
            self.data = self.data.iloc[-5000:].reset_index(drop=True)

    def analyze_current(self) -> AnalysisResult:
        """Análise completa da barra atual"""
        if not self.current_bar:
            return self._empty_result()
        
        bar = self.current_bar
        
        # Métricas dos engines de volume
        volume_metrics = {}
        if self.volume_engine:
            current = self.volume_engine.get_current_cluster()
            if current:
                volume_metrics = {
                    'cluster_delta': current.delta,
                    'cluster_volume': current.volume,
                    'imbalance_ratio': current.imbalance_ratio,
                    'tick_count_in_cluster': current.tick_count
                }
        
        velocity = self.velocity_engine.get_current_velocity()
        spread = self.spread_engine.get_spread_trend()
        atr = self.atr_engine._classify_regime()
        
        # Análise de desequilíbrio
        imbalance = self.imbalance_engine.process_tick(
            bar,
            volume_metrics.get('cluster_delta', 0),
            volume_metrics.get('cluster_volume', 0)
        )
        
        # Análise de execução (fallback se não disponível)
        if self.execution_analyzer:
            exec_profile = self.execution_analyzer.analyze_bar(bar)
            exec_style = exec_profile.style.value if hasattr(exec_profile.style, 'value') else str(exec_profile.style)
            exec_pressure = exec_profile.execution_pressure
            agg_ratio = exec_profile.aggressive_ratio
        else:
            exec_style = 'UNKNOWN'
            exec_pressure = 0.0
            agg_ratio = 0.5
        
        # Predição da IA
        ai_pred = self._get_ai_prediction(bar)
        
        # Contexto de rota
        route_ctx = self._get_route_context()
        
        # Gera setup
        setup = self._generate_setup(bar, imbalance, ai_pred, exec_pressure)
        
        # Gera narrativa
        narrative = self._generate_narrative(bar, imbalance, ai_pred, setup, volume_metrics, exec_style)
        
        return AnalysisResult(
            timestamp=bar.get('timestamp', 0),
            symbol=self.symbol,
            price=bar.get('price', 0),
            bar_type=self._classify_bar_type(bar, imbalance),
            delta=bar.get('delta', 0),
            volume=bar.get('volume', 0),
            imbalance_ratio=imbalance.get('imbalance_ratio', 0),
            execution_style=exec_style,
            aggressive_ratio=agg_ratio,
            execution_pressure=exec_pressure,
            in_absorption_zone=imbalance.get('is_absorption', False),
            absorption_info=imbalance.get('absorption_zone') if imbalance.get('is_absorption') else None,
            ai_prediction=ai_pred,
            route_context=route_ctx,
            setup=setup,
            narrative=narrative
        )

    def analyze_region(self, start_idx: int, end_idx: int) -> Dict:
        """Análise de região selecionada"""
        if RegionAnalyzer is None:
            return {'success': False, 'error': 'RegionAnalyzer não disponível'}
        
        if self.region_analyzer is None:
            self.region_analyzer = RegionAnalyzer(self.data)
        
        try:
            result = self.region_analyzer.analyze_region(start_idx, end_idx)
            return {
                'success': True,
                'region': {
                    'start_idx': result.start_idx,
                    'end_idx': result.end_idx,
                    'start_price': result.start_price,
                    'end_price': result.end_price
                },
                'pattern': result.pattern.value if hasattr(result.pattern, 'value') else str(result.pattern),
                'confidence': result.confidence,
                'narrative': result.narrative,
                'key_levels': result.key_levels,
                'volume_profile': result.volume_profile,
                'delta_profile': result.delta_profile,
                'prediction': result.prediction,
                'recommendation': result.recommendation
            }
        except Exception as e:
            logger.error(f"Erro na análise de região: {e}")
            return {'success': False, 'error': str(e)}

    def get_attention_heatmap(self, center_idx: int, window: int = 20) -> Dict:
        """Gera heatmap de atenção da IA"""
        if self.attention_visualizer is None:
            return {'success': False, 'error': 'IA não inicializada'}
        
        try:
            heatmap = self.attention_visualizer.generate_attention_heatmap(center_idx, window)
            zones = self.attention_visualizer.get_attention_zones(heatmap)
            return {'success': True, 'center_idx': center_idx, 'heatmap': heatmap, 'zones': zones}
        except Exception as e:
            logger.error(f"Erro no heatmap: {e}")
            return {'success': False, 'error': str(e)}

    def get_route_analysis(self, target_idx: int) -> Dict:
        """Análise de como o preço chegou até o índice"""
        if RouteAnalyzer is None:
            return {'success': False, 'error': 'RouteAnalyzer não disponível'}
        
        if self.route_analyzer is None:
            self.route_analyzer = RouteAnalyzer(self.data)
        
        try:
            route = self.route_analyzer.analyze_route_to(target_idx)
            report = self.route_analyzer.generate_route_report(route)
            return {
                'success': True,
                'route': {
                    'origin_price': route.origin_bar['close'],
                    'target_price': route.target_bar['close'],
                    'distance': route.total_distance,
                    'duration_bars': route.total_duration,
                    'exhaustion': route.exhaustion_level,
                    'quality': route.path_quality
                },
                'segments': [{'type': s.type, 'duration': s.duration_bars, 'delta': s.total_delta} for s in route.segments],
                'report': report
            }
        except Exception as e:
            logger.error(f"Erro na análise de rota: {e}")
            return {'success': False, 'error': str(e)}

    def _get_ai_prediction(self, bar: Dict) -> Optional[Dict]:
        """Obtém predição da IA"""
        if not self.predictor or not hasattr(self.predictor, 'is_trained') or not self.predictor.is_trained:
            return None
        
        try:
            pred = self.predictor.predict(bar, self.recent_bars[-10:])
            return {
                'direction': pred.direction,
                'confidence': pred.confidence,
                'probability_up': pred.probability_up,
                'probability_down': pred.probability_down,
                'expected_return': pred.expected_return
            }
        except Exception as e:
            logger.warning(f"Erro na predição: {e}")
            return None

    def _get_route_context(self) -> Optional[Dict]:
        """Obtém contexto de rota"""
        if len(self.data) < 10:
            return None
        
        try:
            recent = self.data.iloc[-10:]
            return {
                'trend': 'UP' if recent['close'].iloc[-1] > recent['close'].iloc[0] else 'DOWN',
                'avg_delta': recent['delta'].mean(),
                'total_volume': recent['volume'].sum()
            }
        except:
            return None

    def _generate_setup(self, bar: Dict, imbalance: Dict, ai_pred: Optional[Dict], exec_pressure: float) -> Optional[Dict]:
        """Gera setup de trading"""
        setup = {'valid': False}
        
        if ai_pred and ai_pred.get('confidence', 0) > 0.6:
            direction = ai_pred['direction']
            confidence = ai_pred['confidence']
            
            if direction == 'UP' and exec_pressure > 0.2:
                stop = bar['low'] * 0.9995 if 'low' in bar else bar['price'] * 0.9995
                target = bar['price'] + (bar['price'] - stop) * 2
                setup = {
                    'valid': True,
                    'direction': 'LONG',
                    'entry': bar['price'],
                    'stop': stop,
                    'target': target,
                    'confidence': (confidence + abs(exec_pressure)) / 2
                }
            elif direction == 'DOWN' and exec_pressure < -0.2:
                stop = bar['high'] * 1.0005 if 'high' in bar else bar['price'] * 1.0005
                target = bar['price'] - (stop - bar['price']) * 2
                setup = {
                    'valid': True,
                    'direction': 'SHORT',
                    'entry': bar['price'],
                    'stop': stop,
                    'target': target,
                    'confidence': (confidence + abs(exec_pressure)) / 2
                }
        
        return setup

    def _generate_narrative(self, bar, imbalance, ai_pred, setup, volume_metrics, exec_style) -> str:
        """Gera narrativa em português"""
        lines = []
        
        # Tipo de barra
        imb_ratio = imbalance.get('imbalance_ratio', 0)
        if imb_ratio > 0.7:
            lines.append(f"{'🟢' if bar.get('delta', 0) > 0 else '🔴'} Barra de {'compra' if bar.get('delta', 0) > 0 else 'venda'} dominante (ratio: {imb_ratio:.2f})")
        else:
            lines.append("⚪ Barra equilibrada")
        
        # Execução
        if 'AGGRESSIVE' in exec_style:
            lines.append(f"⚡ Execução agressiva detectada")
        elif 'PASSIVE' in exec_style:
            lines.append(f"🛡️ Execução passiva (limit orders)")
        
        # Cluster info
        if volume_metrics:
            lines.append(f"📊 Cluster: Δ={volume_metrics.get('cluster_delta', 0):.1f}, Vol={volume_metrics.get('cluster_volume', 0):.1f}")
        
        # Absorção
        if imbalance.get('is_absorption'):
            zone = imbalance.get('absorption_zone', {})
            lines.append(f"⚖️ Absorção de {zone.get('absorption_type', 'desconhecida')} detectada (força: {imbalance.get('absorption_strength', 0):.2f})")
        
        # Predição
        if ai_pred:
            lines.append(f"🧠 IA prevê: {ai_pred['direction']} ({ai_pred['confidence']*100:.0f}%)")
        
        # Setup
        if setup and setup.get('valid'):
            lines.append(f"🎯 Setup: {setup['direction']} @ {setup['entry']:.5f}")
        
        return "\n".join(lines)

    def _classify_bar_type(self, bar: Dict, imbalance: Dict) -> str:
        """Classifica tipo da barra"""
        delta_ratio = imbalance.get('imbalance_ratio', 0)
        volume = bar.get('volume', 0)
        
        if delta_ratio > 0.8:
            return 'IMBALANCE_EXTREME'
        elif delta_ratio > 0.5:
            return 'IMBALANCE_STRONG'
        elif volume > 1000 and delta_ratio < 0.2:
            return 'ABSORPTION'
        return 'NORMAL'

    def _empty_result(self) -> AnalysisResult:
        """Resultado vazio"""
        return AnalysisResult(
            timestamp=0, symbol='', price=0, bar_type='UNKNOWN',
            delta=0, volume=0, imbalance_ratio=0,
            execution_style='UNKNOWN', aggressive_ratio=0, execution_pressure=0,
            in_absorption_zone=False, absorption_info=None,
            ai_prediction=None, route_context=None, setup=None, narrative=''
        )

    def feedback(self, predicted_direction: str, actual_outcome: str):
        """Recebe feedback para aprendizado"""
        if self.predictor and hasattr(self.predictor, 'online_learning'):
            self.predictor.online_learning(self.current_bar, actual_outcome)