"""
ATR Normalize Engine
Normaliza métricas baseado na volatilidade atual (ATR)
Permite comparação entre diferentes regimes de mercado
"""

from typing import Dict, List
from collections import deque
import numpy as np

class ATRNormalizeEngine:
    """
    Calcula ATR (Average True Range) e normaliza métricas
    para torná-las comparáveis entre diferentes condições de mercado
    """
    
    def __init__(self, period: int = 14):
        self.period = period
        self.prices: deque = deque(maxlen=period * 2)
        self.tr_values: deque = deque(maxlen=period)
        self.atr = 0.0
        self.normalized_atr = 0.0  # ATR como % do preço
        
    def process_tick(self, tick: Dict) -> Dict:
        """Processa tick e atualiza ATR"""
        price = tick['price']
        self.prices.append(price)
        
        if len(self.prices) < 2:
            return {'atr': 0, 'normalized': 0, 'regime': 'unknown'}
        
        # Calcula True Range
        current = price
        previous = list(self.prices)[-2]
        
        tr = abs(current - previous)
        self.tr_values.append(tr)
        
        # Calcula ATR
        if len(self.tr_values) >= self.period:
            self.atr = np.mean(list(self.tr_values)[-self.period:])
            self.normalized_atr = (self.atr / current) * 100 if current > 0 else 0
        
        # Determina regime de volatilidade
        regime = self._classify_regime()
        
        return {
            'atr': round(self.atr, 5),
            'normalized_atr_pct': round(self.normalized_atr, 4),
            'regime': regime,
            'volatility_factor': self._get_volatility_factor(),
            'normalized_volume': self._normalize_volume(tick.get('volume_synthetic', 1))
        }
    
    def _classify_regime(self) -> str:
        """Classifica regime de volatilidade"""
        if self.normalized_atr < 0.01:
            return 'very_low'
        elif self.normalized_atr < 0.05:
            return 'low'
        elif self.normalized_atr < 0.15:
            return 'normal'
        elif self.normalized_atr < 0.30:
            return 'high'
        return 'extreme'
    
    def _get_volatility_factor(self) -> float:
        """Fator de ajuste baseado na volatilidade"""
        # Em alta volatilidade, reduz sensibilidade
        # Em baixa volatilidade, aumenta sensibilidade
        base = 0.1
        if self.normalized_atr > 0:
            return base / self.normalized_atr
        return 1.0
    
    def _normalize_volume(self, volume: float) -> float:
        """Normaliza volume pelo regime de volatilidade"""
        factor = self._get_volatility_factor()
        return volume * factor
    
    def normalize_price_move(self, price_change: float) -> float:
        """Normaliza movimento de preço pelo ATR"""
        if self.atr > 0:
            return price_change / self.atr
        return price_change
    
    def reset(self):
        self.prices.clear()
        self.tr_values.clear()
        self.atr = 0.0
        self.normalized_atr = 0.0