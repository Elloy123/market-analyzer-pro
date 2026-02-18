"""
RegionAnalyzer - Analisa regiões selecionadas manualmente
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class RegionPattern(Enum):
    ACCUMULATION = "ACCUMULATION"
    DISTRIBUTION = "DISTRIBUTION"
    BREAKOUT_PREP = "BREAKOUT_PREP"
    LIQUIDITY_SWEEP = "LIQUIDITY_SWEEP"
    CONSOLIDATION = "CONSOLIDATION"
    REVERSAL_SETUP = "REVERSAL_SETUP"
    TREND_CONTINUATION = "TREND_CONTINUATION"

@dataclass
class RegionAnalysis:
    start_idx: int
    end_idx: int
    start_price: float
    end_price: float
    pattern: RegionPattern
    confidence: float
    narrative: str
    key_levels: List[Dict]
    volume_profile: Dict
    delta_profile: Dict
    prediction: str
    recommendation: str

class RegionAnalyzer:
    """Analisa região selecionada do gráfico"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def analyze_region(self, start_idx: int, end_idx: int) -> RegionAnalysis:
        """Analisa região específica"""
        if start_idx < 0 or end_idx >= len(self.data) or start_idx >= end_idx:
            raise ValueError("Índices inválidos")
        
        region = self.data.iloc[start_idx:end_idx+1]
        
        # Análises
        pattern, confidence = self._identify_pattern(region)
        key_levels = self._find_key_levels(region)
        volume_profile = self._analyze_volume(region)
        delta_profile = self._analyze_delta(region)
        prediction = self._predict(region, pattern)
        
        narrative = self._generate_narrative(region, pattern, key_levels, volume_profile, delta_profile)
        
        return RegionAnalysis(
            start_idx=start_idx,
            end_idx=end_idx,
            start_price=region.iloc[0]['open'],
            end_price=region.iloc[-1]['close'],
            pattern=pattern,
            confidence=confidence,
            narrative=narrative,
            key_levels=key_levels,
            volume_profile=volume_profile,
            delta_profile=delta_profile,
            prediction=prediction['direction'],
            recommendation=prediction['recommendation']
        )
    
    def _identify_pattern(self, region: pd.DataFrame) -> Tuple[RegionPattern, float]:
        """Identifica padrão da região"""
        price_change = (region.iloc[-1]['close'] - region.iloc[0]['open']) / region.iloc[0]['open']
        total_range = region['high'].max() - region['low'].min()
        total_volume = region['volume'].sum()
        total_delta = region['delta'].sum()
        
        # Volume por preço
        volume_at_high = region[region['high'] > region['high'].quantile(0.8)]['volume'].sum()
        volume_at_low = region[region['low'] < region['low'].quantile(0.2)]['volume'].sum()
        
        # Acumulação
        if abs(price_change) < 0.001 and total_delta > total_volume * 0.2 and volume_at_low > volume_at_high * 1.5:
            return RegionPattern.ACCUMULATION, 0.75
        
        # Distribuição
        if abs(price_change) < 0.001 and total_delta < -total_volume * 0.2 and volume_at_high > volume_at_low * 1.5:
            return RegionPattern.DISTRIBUTION, 0.75
        
        # Breakout prep
        first = region.iloc[:len(region)//2]
        second = region.iloc[len(region)//2:]
        if (first['high'].max() - first['low'].min()) > (second['high'].max() - second['low'].min()) * 1.3:
            if second['volume'].mean() > first['volume'].mean() * 1.3:
                return RegionPattern.BREAKOUT_PREP, 0.7
        
        # Liquidity sweep
        wick = total_range / abs(price_change) if price_change != 0 else 10
        if wick > 3 and region['volume'].max() > region['volume'].mean() * 2.5:
            return RegionPattern.LIQUIDITY_SWEEP, 0.8
        
        # Reversão
        price_dir = 1 if price_change > 0 else -1
        delta_dir = 1 if total_delta > 0 else -1
        if price_dir != delta_dir and abs(total_delta) > total_volume * 0.3:
            return RegionPattern.REVERSAL_SETUP, 0.7
        
        # Continuação
        if price_dir == delta_dir:
            return RegionPattern.TREND_CONTINUATION, 0.8
        
        return RegionPattern.CONSOLIDATION, 0.5
    
    def _find_key_levels(self, region: pd.DataFrame) -> List[Dict]:
        """Encontra níveis chave"""
        levels = []
        
        # Máxima
        max_idx = region['high'].idxmax()
        levels.append({
            'type': 'RESISTANCE',
            'price': region.loc[max_idx, 'high'],
            'strength': 'HIGH' if region.loc[max_idx, 'volume'] > region['volume'].mean() * 1.5 else 'MEDIUM'
        })
        
        # Mínima
        min_idx = region['low'].idxmin()
        levels.append({
            'type': 'SUPPORT',
            'price': region.loc[min_idx, 'low'],
            'strength': 'HIGH' if region.loc[min_idx, 'volume'] > region['volume'].mean() * 1.5 else 'MEDIUM'
        })
        
        # POC
        poc = (region['close'] * region['volume']).sum() / region['volume'].sum()
        levels.append({'type': 'POC', 'price': poc, 'context': 'Maior negociação'})
        
        return levels
    
    def _analyze_volume(self, region: pd.DataFrame) -> Dict:
        """Analisa volume"""
        return {
            'total': region['volume'].sum(),
            'avg': region['volume'].mean(),
            'trend': 'INCREASING' if region['volume'].iloc[-3:].mean() > region['volume'].iloc[:3].mean() else 'DECREASING',
            'aggressive': (region['aggressive_buy'].sum() + region['aggressive_sell'].sum()) / region['volume'].sum()
        }
    
    def _analyze_delta(self, region: pd.DataFrame) -> Dict:
        """Analisa delta"""
        total = region['delta'].sum()
        return {
            'total': total,
            'trend': 'BUYING' if total > 0 else 'SELLING',
            'strength': abs(total) / region['volume'].sum(),
            'divergence': self._check_divergence(region)
        }
    
    def _check_divergence(self, region: pd.DataFrame) -> Optional[str]:
        """Verifica divergência"""
        price_change = region.iloc[-1]['close'] - region.iloc[0]['open']
        delta_sum = region['delta'].sum()
        
        if price_change > 0 and delta_sum < 0:
            return "BEARISH_DIVERGENCE"
        elif price_change < 0 and delta_sum > 0:
            return "BULLISH_DIVERGENCE"
        return None
    
    def _predict(self, region: pd.DataFrame, pattern: RegionPattern) -> Dict:
        """Prediz baseado no padrão"""
        last = region.iloc[-1]
        
        predictions = {
            RegionPattern.ACCUMULATION: {
                'direction': 'UP',
                'recommendation': 'Preparar compra. Romper máxima da região.'
            },
            RegionPattern.DISTRIBUTION: {
                'direction': 'DOWN',
                'recommendation': 'Preparar venda. Romper mínima da região.'
            },
            RegionPattern.BREAKOUT_PREP: {
                'direction': 'UP' if region['delta'].iloc[-3:].mean() > 0 else 'DOWN',
                'recommendation': 'Aguardar rompimento com volume.'
            },
            RegionPattern.LIQUIDITY_SWEEP: {
                'direction': 'REVERSE',
                'recommendation': 'Possível armadilha. Aguardar confirmação.'
            },
            RegionPattern.REVERSAL_SETUP: {
                'direction': 'UP' if region['delta'].sum() > 0 else 'DOWN',
                'recommendation': 'Setup de reversão. Entrar na direção do delta.'
            },
            RegionPattern.TREND_CONTINUATION: {
                'direction': 'UP' if last['close'] > region.iloc[0]['open'] else 'DOWN',
                'recommendation': 'Continuação de tendência.'
            },
            RegionPattern.CONSOLIDATION: {
                'direction': 'NEUTRAL',
                'recommendation': 'Aguardar rompimento da região.'
            }
        }
        
        return predictions.get(pattern, predictions[RegionPattern.CONSOLIDATION])
    
    def _generate_narrative(self, region, pattern, levels, vol, delta) -> str:
        """Gera narrativa"""
        lines = [
            f"📊 REGIÃO: {len(region)} barras",
            f"Variação: {((region.iloc[-1]['close'] / region.iloc[0]['open']) - 1) * 100:.2f}%",
            "",
            f"🔍 Padrão: {pattern.value.replace('_', ' ')}",
            "",
            "🎯 Níveis:",
        ]
        
        for lvl in levels:
            lines.append(f"   {lvl['type']}: {lvl['price']:.5f}")
        
        lines.extend([
            "",
            f"📈 Volume: {vol['total']:.0f} ({vol['trend']})",
            f"⚡ Delta: {delta['total']:+.0f} ({delta['trend']})"
        ])
        
        if delta['divergence']:
            lines.append(f"⚠️ Divergência: {delta['divergence']}")
        
        return "\n".join(lines)