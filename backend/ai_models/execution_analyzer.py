"""
ExecutionProfileAnalyzer - Perfil de execução (limite vs agressiva)
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass
from enum import Enum

class ExecutionStyle(Enum):
    PASSIVE_DOMINANT = "PASSIVE_DOMINANT"
    BALANCED = "BALANCED"
    AGGRESSIVE_DOMINANT = "AGGRESSIVE_DOMINANT"
    ICEBERG_SUSPECTED = "ICEBERG_SUSPECTED"

@dataclass
class ExecutionProfile:
    total_volume: float
    aggressive_volume: float
    passive_volume: float
    aggressive_ratio: float
    passive_ratio: float
    aggressive_buy_ratio: float
    aggressive_sell_ratio: float
    execution_pressure: float  # -1 a +1
    limit_order_imbalance: float
    style: ExecutionStyle
    confidence: float
    avg_order_size: float
    order_size_variance: float
    execution_speed: float

class ExecutionProfileAnalyzer:
    """Analisa perfil de execução"""
    
    def __init__(self, data: pd.DataFrame = None):
        self.data = data
        self.benchmarks = {}
        
        if data is not None:
            self._calc_benchmarks()
    
    def _calc_benchmarks(self):
        """Calcula benchmarks"""
        if 'aggressive_buy' not in self.data.columns:
            return
        
        total_agg = self.data['aggressive_buy'] + self.data['aggressive_sell']
        self.benchmarks = {
            'avg_aggressive_ratio': (total_agg / self.data['volume']).mean(),
            'high_threshold': (total_agg / self.data['volume']).quantile(0.8),
            'low_threshold': (total_agg / self.data['volume']).quantile(0.2)
        }
    
    def analyze_bar(self, bar: Dict) -> ExecutionProfile:
        """Analisa barra"""
        vol = bar.get('volume', 0)
        agg_buy = bar.get('aggressive_buy', 0)
        agg_sell = bar.get('aggressive_sell', 0)
        delta = bar.get('delta', 0)
        
        agg_vol = agg_buy + agg_sell
        passive_vol = vol - agg_vol
        
        agg_ratio = agg_vol / vol if vol > 0 else 0
        passive_ratio = 1 - agg_ratio
        
        agg_buy_ratio = agg_buy / agg_vol if agg_vol > 0 else 0.5
        agg_sell_ratio = agg_sell / agg_vol if agg_vol > 0 else 0.5
        
        # Pressão de execução
        pressure = (agg_buy - agg_sell) / vol if vol > 0 else 0
        
        # Desequilíbrio de passivas
        passive_delta = delta - (agg_buy - agg_sell)
        limit_imbalance = passive_delta / vol if vol > 0 else 0
        
        # Tamanho de ordem
        ticks = bar.get('tick_count', 1)
        avg_size = vol / max(ticks, 1)
        
        # Variância (estimada)
        variance = self._estimate_variance(bar)
        
        # Velocidade
        duration = bar.get('duration_ms', 1000)
        speed = vol / (duration / 1000) if duration > 0 else 0
        
        # Classifica
        style, conf = self._classify(agg_ratio, variance, speed, bar)
        
        return ExecutionProfile(
            total_volume=vol,
            aggressive_volume=agg_vol,
            passive_volume=passive_vol,
            aggressive_ratio=agg_ratio,
            passive_ratio=passive_ratio,
            aggressive_buy_ratio=agg_buy_ratio,
            aggressive_sell_ratio=agg_sell_ratio,
            execution_pressure=pressure,
            limit_order_imbalance=limit_imbalance,
            style=style,
            confidence=conf,
            avg_order_size=avg_size,
            order_size_variance=variance,
            execution_speed=speed
        )
    
    def _estimate_variance(self, bar: Dict) -> float:
        """Estima variância no tamanho das ordens"""
        vol = bar.get('volume', 0)
        ticks = bar.get('tick_count', 1)
        agg_buy = bar.get('aggressive_buy', 0)
        agg_sell = bar.get('aggressive_sell', 0)
        
        if ticks < 2:
            return 0.0
        
        agg_concentration = (agg_buy + agg_sell) / max(vol, 1)
        variance = agg_concentration * (1 - 1/max(ticks, 2))
        
        return min(1.0, variance)
    
    def _classify(self, agg_ratio: float, variance: float, 
                  speed: float, bar: Dict) -> Tuple[ExecutionStyle, float]:
        """Classifica estilo"""
        
        if variance > 0.6 and bar.get('tick_count', 0) > 20:
            return ExecutionStyle.ICEBERG_SUSPECTED, 0.8
        
        if agg_ratio > 0.7:
            return ExecutionStyle.AGGRESSIVE_DOMINANT, min(1.0, agg_ratio)
        elif agg_ratio < 0.3:
            return ExecutionStyle.PASSIVE_DOMINANT, min(1.0, 1 - agg_ratio)
        
        return ExecutionStyle.BALANCED, 1 - abs(agg_ratio - 0.5) * 2
    
    def generate_report(self, profile: ExecutionProfile) -> str:
        """Gera relatório"""
        lines = [
            "📊 PERFIL DE EXECUÇÃO",
            f"Estilo: {profile.style.value}",
            f"Confiança: {profile.confidence*100:.0f}%",
            "",
            f"Agressiva: {profile.aggressive_ratio*100:.1f}%",
            f"Passiva: {profile.passive_ratio*100:.1f}%",
            "",
            f"Pressão: {profile.execution_pressure:+.2f}",
            f"Velocidade: {profile.execution_speed:.0f} u/s"
        ]
        
        if profile.order_size_variance > 0.5:
            lines.append(f"🧊 Variância alta: {profile.order_size_variance*100:.0f}% (possível iceberg)")
        
        return "\n".join(lines)