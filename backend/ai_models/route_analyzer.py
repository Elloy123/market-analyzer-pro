"""
RouteAnalyzer - Analisa caminho percorrido pelo preço
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class RouteSegment:
    type: str  # IMPULSE, CONSOLIDATION, ABSORPTION
    start_idx: int
    end_idx: int
    start_price: float
    end_price: float
    duration: int
    total_delta: float
    total_volume: float

@dataclass
class PriceRoute:
    origin_bar: Dict
    target_bar: Dict
    segments: List[RouteSegment]
    total_distance: float
    total_duration: int
    avg_speed: float
    exhaustion_level: float
    path_quality: str

class RouteAnalyzer:
    """Analisa como preço chegou até ponto"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.lookback = 20
    
    def analyze_route_to(self, target_idx: int) -> PriceRoute:
        """Analisa rota até índice"""
        target = self.data.iloc[target_idx].to_dict()
        
        # Encontra origem
        origin_idx = self._find_origin(target_idx)
        origin = self.data.iloc[origin_idx].to_dict()
        
        # Segmenta
        segments = self._segment_path(origin_idx, target_idx)
        
        # Métricas
        distance = abs(target['close'] - origin['close'])
        duration = target_idx - origin_idx
        
        return PriceRoute(
            origin_bar=origin,
            target_bar=target,
            segments=segments,
            total_distance=distance,
            total_duration=duration,
            avg_speed=distance / max(duration, 1),
            exhaustion_level=self._calc_exhaustion(target_idx, segments),
            path_quality=self._assess_quality(segments)
        )
    
    def _find_origin(self, target_idx: int) -> int:
        """Encontra onde movimento começou"""
        if target_idx == 0:
            return 0
        
        target_dir = 1 if self.data.iloc[target_idx]['close'] > self.data.iloc[target_idx]['open'] else -1
        
        for i in range(target_idx - 1, max(0, target_idx - self.lookback), -1):
            bar_dir = 1 if self.data.iloc[i]['close'] > self.data.iloc[i]['open'] else -1
            
            if bar_dir != target_dir:
                return i + 1
        
        return max(0, target_idx - self.lookback)
    
    def _segment_path(self, start: int, end: int) -> List[RouteSegment]:
        """Divide caminho em segmentos"""
        segments = []
        i = start
        
        while i < end:
            window_end = min(i + 3, end)
            window = self.data.iloc[i:window_end]
            
            seg_type = self._classify_segment(window)
            seg_end = self._find_segment_end(i, end, seg_type)
            
            seg_data = self.data.iloc[i:seg_end]
            segments.append(RouteSegment(
                type=seg_type,
                start_idx=i,
                end_idx=seg_end,
                start_price=seg_data.iloc[0]['open'],
                end_price=seg_data.iloc[-1]['close'],
                duration=seg_end - i,
                total_delta=seg_data['delta'].sum(),
                total_volume=seg_data['volume'].sum()
            ))
            
            i = seg_end
        
        return segments
    
    def _classify_segment(self, data: pd.DataFrame) -> str:
        """Classifica tipo de segmento"""
        if len(data) < 2:
            return 'IMPULSE'
        
        price_change = abs(data['close'].iloc[-1] - data['open'].iloc[0])
        range_total = data['high'].max() - data['low'].min()
        volume = data['volume'].sum()
        delta_ratio = abs(data['delta'].sum()) / volume
        
        if price_change > range_total * 0.6 and delta_ratio > 0.5:
            return 'IMPULSE'
        if volume > data['volume'].mean() * 1.5 and price_change < range_total * 0.3:
            return 'ABSORPTION'
        if price_change < range_total * 0.4:
            return 'CONSOLIDATION'
        
        return 'MIXED'
    
    def _find_segment_end(self, start: int, max_idx: int, current_type: str) -> int:
        """Encontra fim do segmento"""
        for i in range(start + 1, min(start + 10, max_idx)):
            window = self.data.iloc[i:min(i+3, max_idx)]
            new_type = self._classify_segment(window)
            
            if new_type != current_type and new_type != 'MIXED':
                return i
        
        return min(start + 5, max_idx)
    
    def _calc_exhaustion(self, target_idx: int, segments: List[RouteSegment]) -> float:
        """Calcula exaustão"""
        if not segments:
            return 0.5
        
        factors = []
        
        # Duração
        total_bars = sum(s.duration for s in segments)
        factors.append(min(1.0, total_bars / 15))
        
        # Volume decaindo
        if len(segments) >= 2:
            vol_trend = segments[-1].total_volume / (segments[-2].total_volume + 1)
            factors.append(1.0 - vol_trend if vol_trend < 1 else 0)
        
        # Delta decaindo
        if len(segments) >= 2:
            delta_trend = abs(segments[-1].total_delta) / (abs(segments[-2].total_delta) + 1)
            factors.append(1.0 - delta_trend if delta_trend < 1 else 0)
        
        return np.mean(factors) if factors else 0.5
    
    def _assess_quality(self, segments: List[RouteSegment]) -> str:
        """Avalia qualidade do caminho"""
        if len(segments) == 1:
            return 'CLEAN'
        if len(segments) > 4:
            return 'CHOPPY'
        
        types = [s.type for s in segments]
        if 'ABSORPTION' in types and 'IMPULSE' in types:
            return 'RESISTED'
        
        return 'CLEAN'
    
    def generate_route_report(self, route: PriceRoute) -> str:
        """Gera relatório da rota"""
        direction = "ALTA" if route.target_bar['close'] > route.origin_bar['close'] else "BAIXA"
        
        lines = [
            f"🛤️ ROTA - {direction}",
            f"Origem: {route.origin_bar['close']:.5f}",
            f"Destino: {route.target_bar['close']:.5f}",
            f"Distância: {route.total_distance:.1f} pips em {route.total_duration} barras",
            "",
            "Segmentos:"
        ]
        
        for i, seg in enumerate(route.segments, 1):
            icon = {'IMPULSE': '⚡', 'CONSOLIDATION': '⏸️', 'ABSORPTION': '🧽'}.get(seg.type, '→')
            lines.append(f"{i}. {icon} {seg.type}: {seg.duration}b | Δ{seg.total_delta:+.0f}")
        
        lines.extend([
            "",
            f"Exaustão: {route.exhaustion_level*100:.0f}%",
            f"Qualidade: {route.path_quality}"
        ])
        
        return "\n".join(lines)