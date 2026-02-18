"""
OrderFlowPredictor - Modelo XGBoost para predição direcional
"""

import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class PredictionResult:
    direction: str  # 'UP', 'DOWN', 'NEUTRAL'
    confidence: float
    probability_up: float
    probability_down: float
    expected_return: float
    features_importance: Dict[str, float]
    model_version: str

class OrderFlowPredictor:
    """
    Preditor de direção baseado em order flow
    """
    
    def __init__(self, model_path: str = "models/orderflow_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'delta_ratio', 'volume_zscore', 'aggressive_ratio',
            'imbalance', 'speed', 'delta_acceleration', 'volume_profile',
            'bid_ask_ratio', 'range_efficiency', 'tick_intensity'
        ]
        self.is_trained = False
        self.data = None
        
        self.load()
    
    def _engineer_features(self, bar: Dict, context: List[Dict] = None) -> np.ndarray:
        """Extrai features de order flow"""
        features = {}
        
        volume = bar.get('volume', 1)
        delta = bar.get('delta', 0)
        
        # Básicas
        features['delta_ratio'] = delta / volume
        features['aggressive_ratio'] = (bar.get('aggressive_buy', 0) + bar.get('aggressive_sell', 0)) / volume
        features['imbalance'] = abs(delta) / volume
        
        # Velocidade
        duration = bar.get('duration_ms', 1000)
        ticks = bar.get('tick_count', 1)
        features['speed'] = ticks / (duration / 1000) if duration > 0 else 0
        features['tick_intensity'] = ticks / volume
        
        # Eficiência
        range_p = bar.get('high', 0) - bar.get('low', 0)
        features['range_efficiency'] = abs(delta) / (range_p * volume + 1e-10)
        
        # Book
        bid_d = bar.get('bid_depth', 1)
        ask_d = bar.get('ask_depth', 1)
        features['bid_ask_ratio'] = bid_d / (ask_d + 1e-10)
        
        # Contexto
        if context and len(context) >= 3:
            recent = context[-3:]
            volumes = [b.get('volume', 0) for b in recent]
            deltas = [b.get('delta', 0) for b in recent]
            
            features['volume_zscore'] = (volume - np.mean(volumes)) / (np.std(volumes) + 1e-10)
            features['delta_acceleration'] = deltas[-1] - deltas[-2] if len(deltas) >= 2 else 0
            features['volume_profile'] = 1 if volume > np.mean(volumes) else 0
        else:
            features['volume_zscore'] = 0
            features['delta_acceleration'] = 0
            features['volume_profile'] = 0
        
        return np.array([features.get(f, 0) for f in self.feature_names]).reshape(1, -1)
    
    def train(self, historical_data: pd.DataFrame, retrain: bool = False) -> bool:
        """Treina modelo com dados históricos"""
        if self.is_trained and not retrain:
            return True
        
        print("🧠 Treinando OrderFlowPredictor...")
        
        df = historical_data.copy()
        
        # Target: direção próxima barra
        df['next_return'] = df['close'].shift(-1) / df['close'] - 1
        df['target'] = np.where(
            df['next_return'] > 0.0001, 1,
            np.where(df['next_return'] < -0.0001, 0, 2)
        )
        
        df = df[:-1].dropna()
        
        if len(df) < 100:
            print(f"⚠️ Poucos dados: {len(df)}")
            return False
        
        # Features
        X, y = [], []
        
        for i in range(len(df) - 3):
            bar = df.iloc[i].to_dict()
            context = [df.iloc[i+j].to_dict() for j in range(3)]
            
            feat = self._engineer_features(bar, context)
            X.append(feat[0])
            y.append(int(df.iloc[i]['target']))
        
        X, y = np.array(X), np.array(y)
        
        # Split
        split = int(len(X) * 0.8)
        X_train, X_val = X[:split], X[split:]
        y_train, y_val = y[:split], y[split:]
        
        # Normaliza
        X_train_s = self.scaler.fit_transform(X_train)
        X_val_s = self.scaler.transform(X_val)
        
        # Treina
        self.model = XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            objective='multi:softprob',
            num_class=3,
            eval_metric='mlogloss'
        )
        
        self.model.fit(
            X_train_s, y_train,
            eval_set=[(X_val_s, y_val)],
            early_stopping_rounds=10,
            verbose=False
        )
        
        acc = self.model.score(X_val_s, y_val)
        print(f"✅ Acurácia: {acc:.2%}")
        
        self.is_trained = True
        self.data = historical_data
        self.save()
        
        return True
    
    def predict(self, bar: Dict, context: List[Dict] = None) -> PredictionResult:
        """Faz predição para uma barra"""
        if not self.is_trained:
            return PredictionResult('NEUTRAL', 0.33, 0.33, 0.33, 0, {}, 'untrained')
        
        X = self._engineer_features(bar, context)
        X_s = self.scaler.transform(X)
        
        proba = self.model.predict_proba(X_s)[0]
        
        prob_up, prob_down, prob_neutral = proba[1], proba[0], proba[2]
        
        if prob_up > prob_down and prob_up > prob_neutral:
            direction, confidence = 'UP', prob_up
        elif prob_down > prob_up and prob_down > prob_neutral:
            direction, confidence = 'DOWN', prob_down
        else:
            direction, confidence = 'NEUTRAL', prob_neutral
        
        expected = (prob_up - prob_down) * 0.001
        
        importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        return PredictionResult(
            direction, confidence, prob_up, prob_down,
            expected, importance, '1.0-local'
        )
    
    def save(self):
        """Salva modelo"""
        if self.model:
            os.makedirs(os.path.dirname(self.model_path) or '.', exist_ok=True)
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names
            }, self.model_path)
    
    def load(self):
        """Carrega modelo"""
        if os.path.exists(self.model_path):
            try:
                data = joblib.load(self.model_path)
                self.model = data['model']
                self.scaler = data['scaler']
                self.feature_names = data['feature_names']
                self.is_trained = True
                print(f"📂 Modelo carregado")
                return True
            except Exception as e:
                print(f"Erro ao carregar: {e}")
        return False
    
    def online_learning(self, bar: Dict, actual_outcome: str):
        """Feedback para aprendizado"""
        feedback_file = "models/feedback_buffer.csv"
        
        row = {**bar, 'actual': actual_outcome}
        
        if os.path.exists(feedback_file):
            df = pd.read_csv(feedback_file)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        else:
            df = pd.DataFrame([row])
        
        df.to_csv(feedback_file, index=False)
        
        if len(df) % 50 == 0:
            print(f"🔄 {len(df)} feedbacks acumulados")