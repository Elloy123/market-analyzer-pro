"""
AbsorptionAnalyzer - Analisa absorções e desfechos
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class AbsorptionOutcome(Enum):
    ABSORPTION_HELD = "ABSORPTION_HELD"
    ABSORPTION_BROKEN = "ABSORPTION_BROKEN"
    PARTIAL_FILL = "PARTIAL_FILL"

@dataclass
class AbsorptionZone:
    start_idx: int
    end_idx: int
    price_level: float
    side: str  # 'ASK' ou 'BID'
    total_volume: float
    absorbed_volume: float
    absorption_ratio: float
    outcome: AbsorptionOutcome
    confidence_clear: float

class AbsorptionAnalyzer:
    """Analisa zonas de absorção"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.zones = []
    
    def identify_zones(self, lookback: int = 50) -> List[AbsorptionZone]:
        """Identifica zonas de absorção"""
        self.zones = []
        i = 0
        
        while i < len(self.data) - 3:
            absorption = self._detect_pattern(i)
            
            if absorption:
                outcome, end_idx = self._determine_outcome(absorption['start'])
                
                zone = AbsorptionZone(
                    start_idx=absorption['start'],
                    end_idx=end_idx,
                    price_level=absorption['price'],
                    side=absorption['side'],
                    total_volume=absorption['volume'],
                    absorbed_volume=absorption['absorbed'],
                    absorption_ratio=absorption['ratio'],
                    outcome=outcome,
                    confidence_clear=self._calc_clear_confidence(absorption, outcome, end_idx)
                )
                
                self.zones.append(zone)
                i = end_idx + 1
            else:
                i += 1
        
        return self.zones
    
    def _detect_pattern(self, start: int) -> Optional[Dict]:
        """Detecta padrão de absorção"""
        if start >= len(self.data) - 3:
            return None
        
        window = self.data.iloc[start:start+5]
        
        avg_vol = self.data['volume'].rolling(20).mean().iloc[start] if start > 0 else window['volume'].mean()
        total_vol = window['volume'].sum()
        
        if total_vol < avg_vol * 1.5:
            return None
        
        price_range = window['high'].max() - window['low'].min()
        efficiency = price_range / (total_vol + 1e-10)
        
        if efficiency > 0.001:
            return None
        
        total_delta = window['delta'].sum()
        ratio = 1 - (abs(total_delta) / total_vol)
        
        if ratio < 0.3:
            return None
        
        side = 'ASK' if window['close'].iloc[-1] >= window['high'].iloc[:-1].max() * 0.99 else 'BID'
        
        return {
            'start': start,
            'price': window['high'].max() if side == 'ASK' else window['low'].min(),
            'side': side,
            'volume': total_vol,
            'absorbed': total_vol * ratio,
            'ratio': ratio
        }
    
    def _determine_outcome(self, start: int) -> Tuple[AbsorptionOutcome, int]:
        """Determina desfecho"""
        absorption = self.data.iloc[start]
        high, low = absorption['high'], absorption['low']
        
        for i in range(start + 1, min(start + 15, len(self.data))):
            bar = self.data.iloc[i]
            
            if bar['close'] > high * 1.001 and bar['delta'] > bar['volume'] * 0.5:
                return AbsorptionOutcome.ABSORPTION_BROKEN, i
            elif bar['close'] < low * 0.999 and bar['delta'] < -bar['volume'] * 0.5:
                return AbsorptionOutcome.ABSORPTION_BROKEN, i
            
            # Rejeição
            if (absorption['delta'] > 0 and bar['delta'] < -bar['volume'] * 0.3) or \
               (absorption['delta'] < 0 and bar['delta'] > bar['volume'] * 0.3):
                return AbsorptionOutcome.ABSORPTION_HELD, i
        
        return AbsorptionOutcome.PARTIAL_FILL, start + 5
    
    def _calc_clear_confidence(self, absorption: Dict, outcome: AbsorptionOutcome, end: int) -> float:
        """Confiança de que nível está limpo"""
        if outcome != AbsorptionOutcome.ABSORPTION_BROKEN:
            return 0.0
        
        confidence = 0.5
        
        # Volume no rompimento
        breakout = self.data.iloc[end]
        avg_vol = self.data['volume'].mean()
        if breakout['volume'] > avg_vol * 1.5:
            confidence += 0.2
        
        # Delta forte
        if abs(breakout['delta']) > breakout['volume'] * 0.7:
            confidence += 0.2
        
        # Sem reteste imediato
        if end + 3 < len(self.data):
            post = self.data.iloc[end+1:end+4]
            retested = any(
                abs(b['close'] - absorption['price']) < abs(absorption['price'] * 0.001)
                for _, b in post.iterrows()
            )
            if not retested:
                confidence += 0.1
        
        return min(1.0, confidence)
    
    def check_current_level(self, idx: int) -> Dict:
        """Verifica se preço atual está próximo de zona"""
        if not self.zones:
            self.identify_zones()
        
        price = self.data.iloc[idx]['close']
        nearby = []
        
        for zone in self.zones:
            dist = abs(price - zone.price_level) / zone.price_level
            if dist < 0.001:
                nearby.append({
                    'price': zone.price_level,
                    'side': zone.side,
                    'distance_pips': dist * 10000,
                    'outcome': zone.outcome.value,
                    'is_clear': zone.outcome == AbsorptionOutcome.ABSORPTION_BROKEN,
                    'confidence': zone.confidence_clear
                })
        
        return {
            'current_price': price,
            'nearby': nearby,
            'in_zone': len(nearby) > 0
        }