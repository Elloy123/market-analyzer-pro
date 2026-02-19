"""
Tick Velocity Engine
Analisa velocidade de chegada de ticks e micro-estrutura
"""

import time
from typing import Dict, List, Optional
from collections import deque
import numpy as np

class TickVelocityEngine:
    """Analisa velocidade e padrões de chegada de ticks"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.tick_times: deque = deque(maxlen=window_size)
        self.velocities: deque = deque(maxlen=window_size)
        self.last_tick_time = 0
        
    def process_tick(self, tick: Dict) -> Dict:
        """Processa tick e retorna métricas de velocidade"""
        current_time = tick.get('timestamp', time.time() * 1000) / 1000  # em segundos
        
        if self.last_tick_time > 0:
            delta_time = current_time - self.last_tick_time
            velocity = 1.0 / delta_time if delta_time > 0 else 0
            
            self.velocities.append(velocity)
            self.tick_times.append(current_time)
        
        self.last_tick_time = current_time
        
        return {
            'velocity': self.get_current_velocity(),
            'acceleration': self.get_acceleration(),
            'burst_detected': self.is_burst(),
            'avg_interval': self.get_average_interval()
        }
    
    def get_current_velocity(self) -> float:
        """Ticks por segundo"""
        if len(self.velocities) < 2:
            return 0.0
        return np.mean(list(self.velocities)[-10:])
    
    def get_acceleration(self) -> float:
        """Mudança na velocidade"""
        if len(self.velocities) < 5:
            return 0.0
        recent = list(self.velocities)[-5:]
        previous = list(self.velocities)[-10:-5] if len(self.velocities) >= 10 else [recent[0]]
        
        return (np.mean(recent) - np.mean(previous)) / max(np.mean(previous), 0.001)
    
    def is_burst(self, threshold: float = 2.0) -> bool:
        """Detecta explosão de atividade"""
        if len(self.velocities) < 10:
            return False
        
        recent = np.mean(list(self.velocities)[-5:])
        baseline = np.mean(list(self.velocities)[:-5]) if len(self.velocities) > 5 else recent
        
        return recent > baseline * threshold
    
    def get_average_interval(self) -> float:
        """Intervalo médio entre ticks em ms"""
        if len(self.tick_times) < 2:
            return 0.0
        
        intervals = np.diff(list(self.tick_times))
        return np.mean(intervals) * 1000  # em ms
    
    def reset(self):
        self.tick_times.clear()
        self.velocities.clear()
        self.last_tick_time = 0