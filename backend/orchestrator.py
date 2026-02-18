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

from ai_models.predictor import OrderFlowPredictor
from ai_models.local_llm import LocalNarrativeGenerator, NarrativeContext
from ai_models.integrated_ai import IntegratedAI
from ai_models.region_analyzer import RegionAnalyzer, RegionPattern
from ai_models.attention_visualizer import AttentionVisualizer
from ai_models.route_analyzer import RouteAnalyzer
from ai_models.absorption_analyzer import AbsorptionAnalyzer, AbsorptionOutcome
from ai_models.execution_analyzer import ExecutionProfileAnalyzer, ExecutionStyle

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Resultado unificado de todas as análises"""
    timestamp: int
    symbol: str
    price: float
    
    # Análise básica
    bar_type: str
    delta: float
    volume: float
    imbalance_ratio: float
    
    # Análise de execução
    execution_style: str
    aggressive_ratio: float
    execution_pressure: float
    
    # Análise de absorção
    in_absorption_zone: bool
    absorption_info: Optional[Dict]
    
    # Predição da IA
    ai_prediction: Optional[Dict]
    
    # Contexto de rota
    route_context: Optional[Dict]
    
    # Setup gerado
    setup: Optional[Dict]
    
    # Narrativa
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
        
        # Inicializa analisadores
        self.predictor = OrderFlowPredictor()
        self.narrative = LocalNarrativeGenerator()
        self.execution_analyzer = ExecutionProfileAnalyzer(self.data)
        self.absorption_analyzer = AbsorptionAnalyzer(self.data)
        self.route_analyzer = None  # Inicializado sob demanda
        self.region_analyzer = None  # Inicializado sob demanda
        self.attention_visualizer = None  # Inicializado após treino
        
        # IA integrada (inicializada quando tiver dados suficientes)
        self.integrated_ai = None
        
        # Estado atual
        self.current_bar = None
        self.recent_bars = []
        self.max_history = 1000
        
        # Treina se tiver dados
        if len(self.data) > 200:
            self._initialize_ai()
    
    def _initialize_ai(self):
        """Inicializa modelos de IA"""
        try:
            self.predictor.train(self.data)
            self.integrated_ai = IntegratedAI(self.data)
            self.attention_visualizer = AttentionVisualizer(self.predictor)
            logger.info("✅ IA inicializada com sucesso")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao inicializar IA: {e}")
    
    def update_data(self, new_bar: Dict):
        """Atualiza dados com nova barra"""
        self.current_bar = new_bar
        self.recent_bars.append(new_bar)
        
        if len(self.recent_bars) > self.max_history:
            self.recent_bars.pop(0)
        
        # Atualiza DataFrame
        new_row = pd.DataFrame([new_bar])
        self.data = pd.concat([self.data, new_row], ignore_index=True)
        
        # Mantém limite
        if len(self.data) > 10000:
            self.data = self.data.iloc[-5000:].reset_index(drop=True)
    
    def analyze_current(self) -> AnalysisResult:
        """
        Análise completa da barra atual
        """
        if not self.current_bar:
            return self._empty_result()
        
        bar = self.current_bar
        
        # 1. Perfil de execução
        exec_profile = self.execution_analyzer.analyze_bar(bar)
        
        # 2. Contexto de absorção
        abs_context = self._check_absorption_context(bar)
        
        # 3. Predição da IA
        ai_pred = self._get_ai_prediction(bar)
        
        # 4. Contexto de rota (se tiver histórico)
        route_ctx = self._get_route_context()
        
        # 5. Gera setup
        setup = self._generate_setup(bar, exec_profile, abs_context, ai_pred)
        
        # 6. Gera narrativa
        narrative = self._generate_narrative(bar, exec_profile, abs_context, ai_pred, setup)
        
        return AnalysisResult(
            timestamp=bar.get('timestamp', 0),
            symbol=self.symbol,
            price=bar.get('close', 0),
            bar_type=self._classify_bar_type(bar),
            delta=bar.get('delta', 0),
            volume=bar.get('volume', 0),
            imbalance_ratio=abs(bar.get('delta', 0)) / bar.get('volume', 1),
            execution_style=exec_profile.style.value,
            aggressive_ratio=exec_profile.aggressive_ratio,
            execution_pressure=exec_profile.execution_pressure,
            in_absorption_zone=abs_context['in_zone'],
            absorption_info=abs_context['zone'] if abs_context['in_zone'] else None,
            ai_prediction=ai_pred,
            route_context=route_ctx,
            setup=setup,
            narrative=narrative
        )
    
    def analyze_region(self, start_idx: int, end_idx: int) -> Dict:
        """
        Análise de região selecionada
        """
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
                'pattern': result.pattern.value,
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
        """
        Gera heatmap de atenção da IA
        """
        if self.attention_visualizer is None:
            return {'success': False, 'error': 'IA não inicializada'}
        
        try:
            heatmap = self.attention_visualizer.generate_attention_heatmap(center_idx, window)
            zones = self.attention_visualizer.get_attention_zones(heatmap)
            
            return {
                'success': True,
                'center_idx': center_idx,
                'heatmap': heatmap,
                'zones': zones
            }
        except Exception as e:
            logger.error(f"Erro no heatmap: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_route_analysis(self, target_idx: int) -> Dict:
        """
        Análise de como o preço chegou até o índice
        """
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
                'segments': [
                    {
                        'type': s.type,
                        'duration': s.duration_bars,
                        'delta': s.total_delta
                    } for s in route.segments
                ],
                'report': report
            }
        except Exception as e:
            logger.error(f"Erro na análise de rota: {e}")
            return {'success': False, 'error': str(e)}
    
    def _check_absorption_context(self, bar: Dict) -> Dict:
        """Verifica contexto de absorção"""
        # Simplificado - implementação completa no absorption_analyzer
        return {
            'in_zone': False,
            'zone': None
        }
    
    def _get_ai_prediction(self, bar: Dict) -> Optional[Dict]:
        """Obtém predição da IA"""
        if not self.predictor.is_trained:
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
    
    def _generate_setup(self, bar: Dict, exec_profile, abs_context, ai_pred) -> Optional[Dict]:
        """Gera setup de trading"""
        setup = {'valid': False}
        
        # Regras de setup
        if ai_pred and ai_pred['confidence'] > 0.6:
            if ai_pred['direction'] == 'UP' and exec_profile.execution_pressure > 0.2:
                setup = {
                    'valid': True,
                    'direction': 'LONG',
                    'entry': bar['close'],
                    'stop': bar['low'] * 0.9995,
                    'target': bar['close'] + (bar['close'] - bar['low'] * 0.9995) * 2,
                    'confidence': (ai_pred['confidence'] + exec_profile.aggressive_ratio) / 2
                }
            elif ai_pred['direction'] == 'DOWN' and exec_profile.execution_pressure < -0.2:
                setup = {
                    'valid': True,
                    'direction': 'SHORT',
                    'entry': bar['close'],
                    'stop': bar['high'] * 1.0005,
                    'target': bar['close'] - (bar['high'] * 1.0005 - bar['close']) * 2,
                    'confidence': (ai_pred['confidence'] + exec_profile.aggressive_ratio) / 2
                }
        
        return setup
    
    def _generate_narrative(self, bar, exec_profile, abs_context, ai_pred, setup) -> str:
        """Gera narrativa em português"""
        # Usa LLM local ou gera narrativa básica
        lines = []
        
        # Tipo de barra
        if abs(bar.get('delta', 0)) > bar.get('volume', 1) * 0.7:
            lines.append(f"{'🟢' if bar['delta'] > 0 else '🔴'} Barra de {'compra' if bar['delta'] > 0 else 'venda'} dominante")
        else:
            lines.append("⚪ Barra equilibrada")
        
        # Execução
        if exec_profile.style == ExecutionStyle.AGGRESSIVE_DOMINANT:
            lines.append(f"⚡ Execução agressiva ({exec_profile.aggressive_ratio*100:.0f}% market orders)")
        elif exec_profile.style == ExecutionStyle.PASSIVE_DOMINANT:
            lines.append(f"🛡️ Execução passiva ({exec_profile.passive_ratio*100:.0f}% limit orders)")
        
        # Predição
        if ai_pred:
            lines.append(f"🧠 IA prevê: {ai_pred['direction']} ({ai_pred['confidence']*100:.0f}%)")
        
        # Setup
        if setup['valid']:
            lines.append(f"🎯 Setup: {setup['direction']} @ {setup['entry']:.5f}")
        
        return "\n".join(lines)
    
    def _classify_bar_type(self, bar: Dict) -> str:
        """Classifica tipo da barra"""
        delta_ratio = abs(bar.get('delta', 0)) / bar.get('volume', 1)
        
        if delta_ratio > 0.8:
            return 'IMBALANCE_EXTREME'
        elif delta_ratio > 0.5:
            return 'IMBALANCE_STRONG'
        elif bar.get('volume', 0) > 1000 and delta_ratio < 0.2:
            return 'ABSORPTION'
        else:
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
        if self.predictor:
            self.predictor.online_learning(self.current_bar, actual_outcome)