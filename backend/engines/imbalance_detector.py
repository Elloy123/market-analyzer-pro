"""
Imbalance Detector Engine
Detecta desequilíbrios extremos de compra/venda e absorção
"""

from typing import Dict, List, Optional
from collections import deque
import numpy as np

class ImbalanceDetectorEngine:
    """
    Detecta situações de desequilíbrio extremo entre compra e venda
    e identifica possíveis zonas de absorção
    """
    
    def __init__(self, threshold_ratio: float = 0.75):
        self.threshold_ratio = threshold_ratio  # 75% de desequilíbrio
        self.recent_deltas: deque = deque(maxlen=50)
        self.recent_volumes: deque = deque(maxlen=50)
        self.absorption_zones: deque = deque(maxlen=20)
        self.current_zone: Optional[Dict] = None
        
    def process_tick(self, tick: Dict, cluster_delta: float = 0, cluster_volume: float = 0) -> Dict:
        """
        Analisa tick no contexto do cluster atual
        
        Args:
            tick: Dados do tick
            cluster_delta: Delta acumulado do cluster atual
            cluster_volume: Volume acumulado do cluster atual
        """
        delta = tick.get('delta', 0)
        volume = tick.get('volume', 1)
        price = tick['price']
        
        self.recent_deltas.append(delta)
        self.recent_volumes.append(volume)
        
        # Calcula métricas de desequilíbrio
        if cluster_volume > 0:
            imbalance_ratio = abs(cluster_delta) / cluster_volume
        else:
            imbalance_ratio = 0
        
        # Detecta tipo de desequilíbrio
        imbalance_type = self._classify_imbalance(imbalance_ratio, cluster_delta)
        
        # Detecta absorção
        absorption = self._detect_absorption(price, cluster_delta, cluster_volume, imbalance_ratio)
        
        # Detecta stacking (acumulação unidirecional)
        stacking = self._detect_stacking()
        
        return {
            'imbalance_ratio': round(imbalance_ratio, 3),
            'imbalance_type': imbalance_type,
            'is_absorption': absorption['detected'],
            'absorption_strength': absorption['strength'],
            'absorption_zone': absorption.get('zone'),
            'stacking_buy': stacking['buy'],
            'stacking_sell': stacking['sell'],
            'composite_signal': self._calculate_signal(imbalance_type, absorption, stacking)
        }
    
    def _classify_imbalance(self, ratio: float, delta: float) -> str:
        """Classifica o tipo de desequilíbrio"""
        if ratio < 0.5:
            return 'balanced'
        elif ratio < 0.6:
            return 'slight_' + ('buy' if delta > 0 else 'sell')
        elif ratio < self.threshold_ratio:
            return 'moderate_' + ('buy' if delta > 0 else 'sell')
        elif ratio < 0.9:
            return 'strong_' + ('buy' if delta > 0 else 'sell')
        return 'extreme_' + ('buy' if delta > 0 else 'sell')
    
    def _detect_absorption(self, price: float, delta: float, volume: float, ratio: float) -> Dict:
        """
        Detecta absorção: grande volume com pequeno delta
        Indica que há participante absorvendo fluxo contrário
        """
        if volume < 10:  # Mínimo de volume para considerar
            return {'detected': False, 'strength': 0}
        
        # Absorção = muito volume, pouco movimento (delta pequeno relativo ao volume)
        absorption_ratio = 1 - ratio  # Quanto menor o ratio, maior a absorção
        
        if absorption_ratio > 0.4 and volume > 20:  # 40% de absorção com volume significativo
            strength = min(1.0, absorption_ratio * (volume / 50))
            
            zone = {
                'price': price,
                'volume': volume,
                'net_delta': delta,
                'absorption_type': 'buying' if delta > 0 else 'selling',
                'strength': strength
            }
            
            # Atualiza zona atual
            if self.current_zone is None or abs(price - self.current_zone['price']) > price * 0.001:
                if self.current_zone:
                    self.absorption_zones.append(self.current_zone)
                self.current_zone = zone
            
            return {'detected': True, 'strength': strength, 'zone': zone}
        
        return {'detected': False, 'strength': 0}
    
    def _detect_stacking(self) -> Dict:
        """Detecta stacking unidirecional (múltiplos deltas seguidos no mesmo sentido)"""
        if len(self.recent_deltas) < 5:
            return {'buy': 0, 'sell': 0}
        
        recent = list(self.recent_deltas)[-10:]
        
        buy_streak = 0
        sell_streak = 0
        current_streak = 0
        current_sign = 0
        
        for d in recent:
            if d > 0:
                if current_sign >= 0:
                    current_streak += 1
                    current_sign = 1
                else:
                    buy_streak = max(buy_streak, current_streak)
                    current_streak = 1
                    current_sign = 1
            elif d < 0:
                if current_sign <= 0:
                    current_streak += 1
                    current_sign = -1
                else:
                    sell_streak = max(sell_streak, current_streak)
                    current_streak = 1
                    current_sign = -1
        
        # Normaliza por volume
        buy_vol = sum(list(self.recent_volumes)[-buy_streak:]) if buy_streak > 0 else 0
        sell_vol = sum(list(self.recent_volumes)[-sell_streak:]) if sell_streak > 0 else 0
        
        return {
            'buy': buy_vol if buy_streak >= 3 else 0,
            'sell': sell_vol if sell_streak >= 3 else 0
        }
    
    def _calculate_signal(self, imbalance_type: str, absorption: Dict, stacking: Dict) -> float:
        """Calcula sinal composto (-1 a +1)"""
        signal = 0
        
        # Imbalance contribution
        if 'buy' in imbalance_type:
            signal += 0.3
            if 'extreme' in imbalance_type:
                signal += 0.3
            elif 'strong' in imbalance_type:
                signal += 0.2
        elif 'sell' in imbalance_type:
            signal -= 0.3
            if 'extreme' in imbalance_type:
                signal -= 0.3
            elif 'strong' in imbalance_type:
                signal -= 0.2
        
        # Absorption contribution (inverte o sinal - absorção indica reversão potencial)
        if absorption['detected']:
            zone_type = absorption.get('zone', {}).get('absorption_type', '')
            if zone_type == 'buying':
                signal -= absorption['strength'] * 0.2  # Absorção de compra = bearish
            else:
                signal += absorption['strength'] * 0.2  # Absorção de venda = bullish
        
        # Stacking contribution
        if stacking['buy'] > stacking['sell']:
            signal += min(0.3, stacking['buy'] / 100)
        elif stacking['sell'] > stacking['buy']:
            signal -= min(0.3, stacking['sell'] / 100)
        
        return max(-1, min(1, signal))
    
    def reset(self):
        self.recent_deltas.clear()
        self.recent_volumes.clear()
        self.absorption_zones.clear()
        self.current_zone = None