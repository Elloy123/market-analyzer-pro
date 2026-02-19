"""
Micro Cluster Engine
Detecta micro-aglomerações de atividade no mesmo nível de preço
Útil para identificar suporte/resistência de alta frequência
"""

from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
import numpy as np

class MicroClusterEngine:
    """
    Detecta micro-clusters de atividade em níveis específicos de preço
    usando step_price como granularidade
    """
    
    def __init__(self, step_price: float, levels: int = 10):
        self.step_price = step_price
        self.levels = levels
        self.price_levels: Dict[int, Dict] = defaultdict(lambda: {
            'buy_volume': 0.0,
            'sell_volume': 0.0,
            'tick_count': 0,
            'last_update': 0
        })
        self.active_levels: deque = deque(maxlen=levels * 2)
        self.decay_factor = 0.95  # Decaimento de níveis antigos
        
    def process_tick(self, tick: Dict) -> Dict:
        """Processa tick e atualiza níveis de preço"""
        price = tick['price']
        volume = tick.get('volume_synthetic', 1.0)
        side = tick.get('side', 'buy')
        timestamp = tick.get('timestamp', 0)
        
        # Normaliza preço para nível discreto usando step_price
        level = int(price / self.step_price)
        
        # Atualiza nível
        pl = self.price_levels[level]
        if side == 'buy':
            pl['buy_volume'] += volume
        else:
            pl['sell_volume'] += volume
        pl['tick_count'] += 1
        pl['last_update'] = timestamp
        
        # Adiciona à lista de níveis ativos
        if level not in self.active_levels:
            self.active_levels.append(level)
        
        # Aplica decaimento em níveis antigos
        self._apply_decay(timestamp)
        
        # Análise de micro-clusters
        analysis = self._analyze_micro_clusters(level)
        
        return {
            'current_level': level,
            'level_price': level * self.step_price,
            'micro_clusters': analysis['clusters'],
            'dominant_side': analysis['dominant_side'],
            'level_intensity': analysis['intensity'],
            'support_resistance': analysis['sr_levels']
        }
    
    def _apply_decay(self, current_time: int):
        """Aplica decaimento temporal aos níveis"""
        cutoff_time = current_time - 60000  # 1 minuto
        
        levels_to_reset = []
        for level, data in self.price_levels.items():
            if data['last_update'] < cutoff_time:
                # Decaimento exponencial
                data['buy_volume'] *= self.decay_factor
                data['sell_volume'] *= self.decay_factor
                
                # Remove se muito pequeno
                if data['buy_volume'] + data['sell_volume'] < 1:
                    levels_to_reset.append(level)
        
        for level in levels_to_reset:
            del self.price_levels[level]
    
    def _analyze_micro_clusters(self, current_level: int) -> Dict:
        """Analisa micro-clusters nos níveis próximos"""
        nearby_levels = [
            l for l in self.active_levels 
            if abs(l - current_level) <= self.levels
        ]
        
        clusters = []
        sr_levels = {'support': [], 'resistance': []}
        
        for level in nearby_levels:
            data = self.price_levels[level]
            total_vol = data['buy_volume'] + data['sell_volume']
            
            if total_vol < 5:  # Mínimo para considerar
                continue
            
            delta = data['buy_volume'] - data['sell_volume']
            imbalance = abs(delta) / total_vol if total_vol > 0 else 0
            
            cluster_info = {
                'level': level,
                'price': level * self.step_price,
                'volume': total_vol,
                'delta': delta,
                'imbalance': imbalance,
                'tick_count': data['tick_count']
            }
            clusters.append(cluster_info)
            
            # Identifica potenciais S/R
            if imbalance > 0.7:
                if delta > 0:
                    sr_levels['support'].append(cluster_info)
                else:
                    sr_levels['resistance'].append(cluster_info)
        
        # Ordena por volume
        clusters.sort(key=lambda x: x['volume'], reverse=True)
        
        # Determina lado dominante no nível atual
        current_data = self.price_levels[current_level]
        curr_delta = current_data['buy_volume'] - current_data['sell_volume']
        dominant = 'buy' if curr_delta > 0 else 'sell' if curr_delta < 0 else 'neutral'
        
        # Intensidade do nível atual
        total_nearby = sum(c['volume'] for c in clusters[:5])
        current_vol = current_data['buy_volume'] + current_data['sell_volume']
        intensity = current_vol / max(total_nearby, 1) if total_nearby > 0 else 0
        
        return {
            'clusters': clusters[:5],  # Top 5
            'dominant_side': dominant,
            'intensity': min(1.0, intensity),
            'sr_levels': sr_levels
        }
    
    def get_level_profile(self, center_level: int, range_levels: int = 5) -> Dict:
        """Retorna perfil detalhado de níveis próximos"""
        profile = {}
        for offset in range(-range_levels, range_levels + 1):
            level = center_level + offset
            data = self.price_levels[level]
            profile[level] = {
                'price': level * self.step_price,
                'buy_vol': data['buy_volume'],
                'sell_vol': data['sell_volume'],
                'net_delta': data['buy_volume'] - data['sell_volume'],
                'ticks': data['tick_count']
            }
        return profile
    
    def reset(self):
        self.price_levels.clear()
        self.active_levels.clear()