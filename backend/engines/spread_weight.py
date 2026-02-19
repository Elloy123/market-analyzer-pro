"""
Spread Weight Engine
Pondera ticks baseado no spread e qualidade de execução
"""

from typing import Dict, List
from collections import deque
import numpy as np

class SpreadWeightEngine:
    """
    Analisa spread e atribui pesos aos ticks
    Spread apertado = maior confiança = peso maior
    """
    
    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.spreads: deque = deque(maxlen=window_size)
        self.weights: deque = deque(maxlen=window_size)
        self.avg_spread = 0.0
        
    def process_tick(self, tick: Dict) -> Dict:
        """Processa tick e calcula peso baseado no spread"""
        spread = tick.get('spread', 0)
        price = tick.get('price', 0)
        
        # Spread relativo ao preço (em basis points)
        if price > 0:
            relative_spread = (spread / price) * 10000  # bp
        else:
            relative_spread = 0
        
        self.spreads.append(relative_spread)
        
        # Calcula peso: spread apertado = peso maior
        if len(self.spreads) > 10:
            self.avg_spread = np.mean(list(self.spreads)[-10:])
        else:
            self.avg_spread = relative_spread if relative_spread > 0 else 1.0
        
        # Peso inversamente proporcional ao spread
        if relative_spread > 0 and self.avg_spread > 0:
            weight = min(3.0, max(0.5, self.avg_spread / relative_spread))
        else:
            weight = 1.0
        
        self.weights.append(weight)
        
        # Detecta anomalias de spread
        spread_anomaly = relative_spread > self.avg_spread * 3
        
        return {
            'spread_weight': weight,
            'relative_spread_bp': relative_spread,
            'avg_spread_bp': self.avg_spread,
            'spread_anomaly': spread_anomaly,
            'spread_quality': 'good' if weight > 1.5 else 'normal' if weight > 0.8 else 'poor'
        }
    
    def get_spread_trend(self) -> str:
        """Tendência do spread"""
        if len(self.spreads) < 20:
            return 'unknown'
        
        recent = np.mean(list(self.spreads)[-10:])
        older = np.mean(list(self.spreads)[-20:-10])
        
        if recent < older * 0.8:
            return 'tightening'  # Spread apertando - liquidez melhorando
        elif recent > older * 1.2:
            return 'widening'    # Spread abrindo - liquidez piorando
        return 'stable'
    
    def reset(self):
        self.spreads.clear()
        self.weights.clear()
        self.avg_spread = 0.0