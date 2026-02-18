"""
AttentionVisualizer - Gera heatmap de atenção da IA
"""

import pandas as pd
import numpy as np
from typing import List, Dict

class AttentionVisualizer:
    """Visualiza onde a IA está 'prestando atenção'"""
    
    def __init__(self, predictor):
        self.predictor = predictor
        self.data = predictor.data if hasattr(predictor, 'data') else None
    
    def generate_attention_heatmap(self, center_idx: int, window: int = 20) -> List[Dict]:
        """Gera heatmap ao redor de barra central"""
        if not self.data:
            return []
        
        start = max(0, center_idx - window)
        end = min(len(self.data) - 1, center_idx + window)
        
        heatmap = []
        
        for i in range(start, end + 1):
            bar = self.data.iloc[i].to_dict()
            importance = self._calc_importance(bar, i, center_idx)
            
            heatmap.append({
                'index': i,
                'timestamp': bar.get('timestamp', i),
                'price': bar['close'],
                'importance': importance['score'],
                'reason': importance['reason'],
                'color_intensity': min(1.0, importance['score'])
            })
        
        return heatmap
    
    def _calc_importance(self, bar: Dict, idx: int, center: int) -> Dict:
        """Calcula importância da barra"""
        score = 0.0
        reasons = []
        
        # Proximidade do centro
        dist = abs(idx - center)
        score += 1.0 / (1 + dist * 0.1) * 0.2
        
        # Volume anômalo
        if self.data is not None and len(self.data) > 20:
            avg_vol = self.data['volume'].rolling(20).mean().iloc[idx] if idx > 0 else bar['volume']
            if bar['volume'] > avg_vol * 2:
                score += 0.25
                reasons.append("Volume anômalo")
        
        # Delta extremo
        delta_ratio = abs(bar.get('delta', 0)) / bar.get('volume', 1)
        if delta_ratio > 0.7:
            score += 0.25
            reasons.append("Imbalance extremo")
        
        # Agressão alta
        agg = (bar.get('aggressive_buy', 0) + bar.get('aggressive_sell', 0)) / bar.get('volume', 1)
        if agg > 0.7:
            score += 0.2
            reasons.append("Alta agressão")
        
        # Wick grande (reversão)
        body = abs(bar.get('close', 0) - bar.get('open', 0))
        range_total = bar.get('high', 0) - bar.get('low', 0)
        if range_total > 0 and body / range_total < 0.3:
            score += 0.1
            reasons.append("Possível reversão")
        
        return {
            'score': min(1.0, score),
            'reason': reasons[0] if reasons else "Contexto"
        }
    
    def get_attention_zones(self, heatmap: List[Dict], threshold: float = 0.6) -> List[Dict]:
        """Agrupa barras de alta atenção em zonas"""
        zones = []
        current = None
        
        for point in heatmap:
            if point['importance'] >= threshold:
                if current is None:
                    current = {
                        'start_idx': point['index'],
                        'end_idx': point['index'],
                        'max_importance': point['importance'],
                        'center_price': point['price'],
                        'reasons': [point['reason']]
                    }
                else:
                    current['end_idx'] = point['index']
                    current['max_importance'] = max(current['max_importance'], point['importance'])
                    if point['reason'] not in current['reasons']:
                        current['reasons'].append(point['reason'])
            else:
                if current:
                    zones.append(current)
                    current = None
        
        if current:
            zones.append(current)
        
        return zones
    
    def explain_attention(self, bar_idx: int) -> str:
        """Explica atenção em barra específica"""
        if not self.data or bar_idx >= len(self.data):
            return "Índice inválido"
        
        bar = self.data.iloc[bar_idx].to_dict()
        imp = self._calc_importance(bar, bar_idx, bar_idx)
        
        lines = [
            f"🎯 Atenção na barra {bar_idx}",
            f"Score: {imp['score']*100:.0f}%",
            f"Motivo: {imp['reason']}"
        ]
        
        return "\n".join(lines)