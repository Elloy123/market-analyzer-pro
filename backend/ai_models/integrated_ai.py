"""
IntegratedAI - Interface única para todos os modelos
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

from .predictor import OrderFlowPredictor, PredictionResult
from .local_llm import LocalNarrativeGenerator, NarrativeContext

@dataclass
class AIAnalysis:
    prediction: PredictionResult
    narrative: str
    explanation: str
    setup: Dict
    confidence_score: float
    recommended_action: str
    risk_assessment: str

class IntegratedAI:
    """Interface unificada da IA"""
    
    def __init__(self, data):
        self.data = data
        self.predictor = OrderFlowPredictor()
        self.narrative = LocalNarrativeGenerator()
        
        if len(data) > 200:
            self.predictor.train(data)
    
    def analyze(self, bar_idx: int, full_context: Dict = None) -> AIAnalysis:
        """Análise completa"""
        bar = self.data.iloc[bar_idx].to_dict()
        
        # Contexto
        context_start = max(0, bar_idx - 5)
        context = [self.data.iloc[i].to_dict() for i in range(context_start, bar_idx)]
        
        # Predição
        prediction = self.predictor.predict(bar, context)
        
        # Narrativa
        nc = NarrativeContext(
            bar=bar,
            prediction={'direction': prediction.direction, 'confidence': prediction.confidence},
            absorption=full_context.get('absorption') if full_context else None,
            retest=full_context.get('retest') if full_context else None,
            execution=full_context.get('execution') if full_context else None,
            route=full_context.get('route') if full_context else None
        )
        
        narrative = self.narrative.generate_narrative(nc)
        
        # Explicação
        features = self._extract_features(bar, context)
        explanation = self.narrative.explain_prediction(prediction, features)
        
        # Setup
        setup = full_context.get('setup') if full_context else {'valid': False}
        
        # Score combinado
        score = self._calc_confidence(prediction, full_context)
        
        # Ação
        action, risk = self._determine_action(prediction, score, setup)
        
        return AIAnalysis(prediction, narrative, explanation, setup, score, action, risk)
    
    def _extract_features(self, bar, context):
        """Extrai features"""
        return {
            'delta_ratio': bar.get('delta', 0) / bar.get('volume', 1),
            'volume_zscore': 0,
            'aggressive_ratio': (bar.get('aggressive_buy', 0) + bar.get('aggressive_sell', 0)) / bar.get('volume', 1),
            'imbalance': abs(bar.get('delta', 0)) / bar.get('volume', 1),
            'speed': bar.get('tick_count', 0) / (bar.get('duration_ms', 1000) / 1000)
        }
    
    def _calc_confidence(self, prediction, context):
        """Calcula confiança combinada"""
        scores = [prediction.confidence]
        
        if context:
            if context.get('absorption', {}).get('broken'):
                scores.append(0.9)
            if context.get('retest', {}).get('success'):
                scores.append(0.85)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _determine_action(self, prediction, confidence, setup):
        """Determina ação"""
        if confidence < 0.5:
            return "AGUARDAR", "Confiança insuficiente"
        
        if not setup.get('valid'):
            return f"MONITORAR {prediction.direction}", "Aguardar setup claro"
        
        direction = setup.get('direction', 'NEUTRAL')
        rr = abs(setup.get('target', 0) - setup.get('entry', 0)) / abs(setup.get('entry', 0) - setup.get('stop', 0)) if setup.get('stop') else 0
        
        risk = "FAVORÁVEL" if rr >= 2 else "ACEITÁVEL" if rr >= 1.5 else "DESFAVORÁVEL"
        
        return f"{direction} @ {setup.get('entry', 0):.5f}", f"Risco: {risk} (1:{rr:.1f})"
    
    def feedback(self, bar_idx: int, predicted: str, actual: str):
        """Feedback"""
        bar = self.data.iloc[bar_idx].to_dict()
        self.predictor.online_learning(bar, actual)
        correct = (predicted == actual) or (predicted == 'UP' and actual == 'UP') or (predicted == 'DOWN' and actual == 'DOWN')
        return correct