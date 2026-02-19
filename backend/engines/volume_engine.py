"""
Volume Imbalance Engine - Core do sistema atemporal
Implementa agregação de ticks por desequilíbrio de volume (cluster threshold)
e cálculo de step price conforme o repositório imbalanceengine
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import logging

logger = logging.getLogger(__name__)

@dataclass
class ClusterConfig:
    """Configuração de cluster por símbolo - IGUAL ao MT5 Bridge v7"""
    symbol: str
    digits: int
    base_price: float
    multiplier: float
    base_volume: float
    delta_threshold: float  # Cluster threshold - quando fechar o cluster
    step_price: float       # Step price - incremento de preço do cluster
    
    @classmethod
    def from_sym_cfg(cls, symbol: str, cfg: dict):
        return cls(
            symbol=symbol,
            digits=cfg['dig'],
            base_price=cfg['base'],
            multiplier=cfg['mult'],
            base_volume=cfg['bv'],
            delta_threshold=cfg['delta_th'],
            step_price=cfg['step']
        )

@dataclass
class Cluster:
    """Representa um cluster de volume atemporal"""
    open_price: float
    close_price: float
    high_price: float
    low_price: float
    buy_volume: float
    sell_volume: float
    delta: float
    tick_count: int
    start_time: int
    end_time: int
    is_closed: bool = False
    
    @property
    def volume(self) -> float:
        return self.buy_volume + self.sell_volume
    
    @property
    def imbalance_ratio(self) -> float:
        if self.volume == 0:
            return 0.0
        return abs(self.delta) / self.volume

class VolumeImbalanceEngine:
    """
    Engine principal de agregação atemporal por desequilíbrio de volume.
    
    Lógica de formação de clusters (IGUAL ao imbalanceengine):
    1. Coleta ticks até atingir delta_threshold de desequilíbrio
    2. Ou até atingir limite de tempo/volume
    3. Fecha cluster e inicia novo quando threshold é atingido
    
    Cálculos:
    - Cluster Threshold: delta_threshold do SYM_CFG
    - Step Price: step do SYM_CFG (incremento mínimo de preço)
    - Fechamento: Quando |delta| >= delta_threshold OU mudança de direção forte
    """
    
    def __init__(self, config: ClusterConfig):
        self.config = config
        self.current_cluster: Optional[Cluster] = None
        self.clusters: deque = deque(maxlen=500)
        self.pending_ticks: List[Dict] = []
        
        # Estado interno
        self.last_price = 0.0
        self.running_delta = 0.0
        self.running_volume = 0.0
        
        # Estatísticas
        self.total_clusters = 0
        self.avg_cluster_size = 0.0
        
    def process_tick(self, tick: Dict) -> Optional[Cluster]:
        """
        Processa um tick e retorna cluster fechado se atingir threshold
        
        Args:
            tick: {'price', 'volume_synthetic', 'side', 'timestamp', ...}
        
        Returns:
            Cluster fechado ou None se ainda acumulando
        """
        price = tick['price']
        volume = tick.get('volume_synthetic', 1.0)
        side = tick.get('side', 'buy')
        timestamp = tick.get('timestamp', 0)
        
        # Inicializa primeiro cluster
        if self.current_cluster is None:
            self.current_cluster = Cluster(
                open_price=price,
                close_price=price,
                high_price=price,
                low_price=price,
                buy_volume=volume if side == 'buy' else 0,
                sell_volume=volume if side == 'sell' else 0,
                delta=volume if side == 'buy' else -volume,
                tick_count=1,
                start_time=timestamp,
                end_time=timestamp
            )
            self.last_price = price
            return None
        
        # Atualiza cluster atual
        cluster = self.current_cluster
        cluster.close_price = price
        cluster.high_price = max(cluster.high_price, price)
        cluster.low_price = min(cluster.low_price, price)
        cluster.end_time = timestamp
        cluster.tick_count += 1
        
        if side == 'buy':
            cluster.buy_volume += volume
            cluster.delta += volume
        else:
            cluster.sell_volume += volume
            cluster.delta -= volume
        
        # Verifica se deve fechar o cluster (CLUSTER THRESHOLD)
        should_close = self._should_close_cluster(cluster, tick)
        
        if should_close:
            cluster.is_closed = True
            completed = cluster
            
            # Salva cluster completado
            self.clusters.append(completed)
            self.total_clusters += 1
            self.avg_cluster_size = (
                (self.avg_cluster_size * (self.total_clusters - 1) + completed.volume) 
                / self.total_clusters
            )
            
            # Inicia novo cluster
            self.current_cluster = Cluster(
                open_price=price,
                close_price=price,
                high_price=price,
                low_price=price,
                buy_volume=volume if side == 'buy' else 0,
                sell_volume=volume if side == 'sell' else 0,
                delta=volume if side == 'buy' else -volume,
                tick_count=1,
                start_time=timestamp,
                end_time=timestamp
            )
            
            logger.debug(f"🔒 Cluster fechado: {completed.volume:.1f} vol, "
                        f"Δ={completed.delta:+.1f}, "
                        f"ratio={completed.imbalance_ratio:.2f}")
            
            return completed
        
        return None
    
    def _should_close_cluster(self, cluster: Cluster, tick: Dict) -> bool:
        """
        Determina se o cluster deve ser fechado baseado em:
        1. Delta Threshold (desequilíbrio de volume)
        2. Mudança de direção significativa
        3. Limite de tempo/volume de segurança
        """
        config = self.config
        
        # 1. Threshold principal de desequilíbrio
        if abs(cluster.delta) >= config.delta_threshold:
            return True
        
        # 2. Mudança de direção (reversão)
        # Se delta mudou de sinal e atingiu 30% do threshold
        if cluster.delta * self.running_delta < 0:  # Mudança de sinal
            if abs(cluster.delta) >= config.delta_threshold * 0.3:
                return True
        
        # 3. Limite de volume máximo (safety)
        max_volume = config.delta_threshold * 3  # 3x o threshold
        if cluster.volume >= max_volume:
            return True
        
        # 4. Limite de tempo (30 segundos para intraday)
        time_diff = cluster.end_time - cluster.start_time
        if time_diff > 30000:  # 30 segundos
            return True
        
        # 5. Gap de preço significativo (> 5 steps)
        price_gap = abs(tick['price'] - cluster.open_price)
        if price_gap >= config.step_price * 5:
            return True
        
        return False
    
    def get_current_cluster(self) -> Optional[Cluster]:
        """Retorna cluster em formação"""
        return self.current_cluster
    
    def get_clusters(self, n: int = 100) -> List[Cluster]:
        """Retorna últimos n clusters fechados"""
        return list(self.clusters)[-n:]
    
    def get_volume_profile(self, levels: int = 24) -> Dict:
        """
        Calcula perfil de volume baseado em clusters fechados
        Retorna distribuição de volume por níveis de preço
        """
        if not self.clusters:
            return {'empty': True}
        
        clusters = list(self.clusters)
        prices = [c.close_price for c in clusters]
        volumes = [c.volume for c in clusters]
        
        min_p, max_p = min(prices), max(prices)
        range_p = max_p - min_p
        
        if range_p == 0:
            return {'empty': True}
        
        # Cria níveis de preço usando step_price
        step = self.config.step_price
        n_steps = max(levels, int(range_p / step))
        
        profile = {
            'levels': [],
            ' POC': 0,  # Point of Control (maior volume)
            'value_area': {'high': 0, 'low': 0},
            'total_volume': sum(volumes)
        }
        
        # Distribui volume em níveis
        level_volumes = {}
        for c in clusters:
            level = round((c.close_price - min_p) / step)
            level_volumes[level] = level_volumes.get(level, 0) + c.volume
        
        # Encontra POC
        max_vol = 0
        poc_level = 0
        for level, vol in level_volumes.items():
            if vol > max_vol:
                max_vol = vol
                poc_level = level
        
        profile['POC'] = min_p + (poc_level * step)
        
        # Calcula Value Area (70% do volume)
        sorted_levels = sorted(level_volumes.items(), key=lambda x: x[1], reverse=True)
        cumsum = 0
        va_levels = []
        target = profile['total_volume'] * 0.7
        
        for level, vol in sorted_levels:
            cumsum += vol
            va_levels.append(level)
            if cumsum >= target:
                break
        
        if va_levels:
            profile['value_area']['low'] = min_p + (min(va_levels) * step)
            profile['value_area']['high'] = min_p + (max(va_levels) * step)
        
        return profile
    
    def reset(self):
        """Reseta estado do engine"""
        self.current_cluster = None
        self.clusters.clear()
        self.pending_ticks.clear()
        self.last_price = 0.0
        self.running_delta = 0.0
        self.running_volume = 0.0