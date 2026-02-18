"""
LocalNarrativeGenerator - Gera narrativas em português
"""

import random
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class NarrativeContext:
    bar: Dict
    prediction: Dict
    absorption: Dict
    retest: Dict
    execution: Dict
    route: Dict

class LocalNarrativeGenerator:
    """Gera explicações em linguagem natural"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Templates de frases"""
        return {
            'high_confidence': [
                "Estou {confidence}% confiante de que o preço vai {direction}.",
                "O modelo indica forte probabilidade de {direction} ({confidence}%).",
                "Sinais técnicos alinhados para {direction}."
            ],
            'medium_confidence': [
                "Há indícios de {direction}, mas com incerteza ({confidence}%).",
                "O cenário favorece {direction}, mas aguardo confirmação."
            ],
            'absorption_broken': [
                "A absorção foi rompida! O nível {price} agora está limpo.",
                "Superamos a resistência em {price}. Não há mais oferta ali."
            ],
            'absorption_active': [
                "Identifiquei absorção em {price} - {side} defendendo.",
                "Volume sendo absorvido em {price}, criando {side}."
            ],
            'retest_success': [
                "Reteste do nível {price} bem-sucedido. {direction} confirmada.",
                "Toque no nível rompido e reversão. Setup clássico."
            ],
            'execution_aggressive': [
                "Execução agressiva ({ratio}%). Participantes ansiosos.",
                "Market orders dominando. Pressão {side} intensa."
            ],
            'execution_passive': [
                "Execução passiva dominante. Acumulação silenciosa.",
                "Limit orders prevalecendo. Movimento planejado."
            ]
        }
    
    def generate_narrative(self, context: NarrativeContext) -> str:
        """Gera narrativa completa"""
        parts = []
        
        # Predição
        pred = context.prediction
        conf = int(pred.get('confidence', 0.5) * 100)
        direction = "subir" if pred.get('direction') == 'UP' else "cair" if pred.get('direction') == 'DOWN' else "ficar lateral"
        
        tmpl = random.choice(self.templates['high_confidence'] if conf > 70 else self.templates['medium_confidence'])
        parts.append(tmpl.format(confidence=conf, direction=direction))
        
        # Absorção
        if context.absorption:
            if context.absorption.get('broken'):
                tmpl = random.choice(self.templates['absorption_broken'])
                parts.append(tmpl.format(price=context.absorption.get('price', 0)))
            else:
                tmpl = random.choice(self.templates['absorption_active'])
                side = "resistência" if context.absorption.get('side') == 'ASK' else "suporte"
                parts.append(tmpl.format(price=context.absorption.get('price', 0), side=side))
        
        # Execução
        if context.execution:
            agg = int(context.execution.get('aggressive_ratio', 0.5) * 100)
            if agg > 60:
                tmpl = random.choice(self.templates['execution_aggressive'])
                side = "compradora" if context.execution.get('pressure', 0) > 0 else "vendedora"
                parts.append(tmpl.format(ratio=agg, side=side))
            elif agg < 40:
                parts.append(random.choice(self.templates['execution_passive']))
        
        return "\n\n".join(parts)
    
    def explain_prediction(self, prediction, features: Dict) -> str:
        """Explica predição"""
        lines = ["🧠 Por que a IA decidiu assim:"]
        
        # Top features
        top = sorted(prediction.features_importance.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for feat, imp in top:
            val = features.get(feat, 0)
            expl = self._explain_feature(feat, val)
            lines.append(f"  • {expl} ({imp*100:.0f}%)")
        
        if prediction.confidence > 0.8:
            lines.append(f"\nAlta confiança ({prediction.confidence*100:.0f}%) - múltiplos sinais alinhados.")
        
        return "\n".join(lines)
    
    def _explain_feature(self, feature: str, value: float) -> str:
        """Explica feature"""
        explanations = {
            'delta_ratio': f"Desequilíbrio de {value*100:.0f}% entre compra e venda",
            'volume_zscore': f"Volume {'acima' if value > 0 else 'abaixo'} da média",
            'aggressive_ratio': f"{'Alta' if value > 0.6 else 'Baixa'} agressão ({value*100:.0f}%)",
            'imbalance': f"Imbalance de {value*100:.0f}%",
            'speed': f"Velocidade {'rápida' if value > 50 else 'moderada'}"
        }
        return explanations.get(feature, f"{feature}: {value:.3f}")