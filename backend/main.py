"""
Market Analyzer Pro - Servidor Principal
Adaptado do MT5 Bridge Server v7 com análise de contexto integrada
"""

import asyncio
import json
import os
import sys
import time
import math
import random
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List
from dataclasses import asdict
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

# MT5
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False

try:
    import websockets
except ImportError:
    print("❌ websockets não instalado")
    sys.exit(1)

# Imports locais
from orchestrator import AnalysisOrchestrator

# ==========================================
# LOGGING
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ==========================================
# CONFIGURAÇÃO DE SÍMBOLOS (igual seu git)
# ==========================================
SYM_CFG = {
    'BTCUSD':  {'dig': 2, 'base': 97000.0,  'mult': 1.0,     'bv': 5.0,  'delta_th': 200,  'step': 10.0},
    'XAUUSD':  {'dig': 2, 'base': 2900.0,   'mult': 50.0,    'bv': 10.0, 'delta_th': 100,   'step': 0.50},
    'EURUSD':  {'dig': 5, 'base': 1.0450,   'mult': 100000.0,'bv': 5.0,  'delta_th': 50,    'step': 0.0001},
    'GBPUSD':  {'dig': 5, 'base': 1.2550,   'mult': 100000.0,'bv': 5.0,  'delta_th': 60,    'step': 0.0001},
    'USTEC':   {'dig': 2, 'base': 21500.0,  'mult': 2.0,     'bv': 10.0, 'delta_th': 150,   'step': 1.0},
    'US100':   {'dig': 2, 'base': 21500.0,  'mult': 2.0,     'bv': 10.0, 'delta_th': 150,   'step': 1.0},
    'NAS100':  {'dig': 2, 'base': 21500.0,  'mult': 2.0,     'bv': 10.0, 'delta_th': 150,   'step': 1.0},
}

def gcfg(symbol):
    return SYM_CFG.get(symbol.upper(), {'dig': 5, 'base': 1.0, 'mult': 1000.0, 'bv': 5.0, 'delta_th': 500, 'step': 0.0001})

# ==========================================
# MT5 CREDENTIALS
# ==========================================
MT5_CONFIG = {
    "login": 0,  # Configure
    "password": "",  # Configure
    "server": "",
    "timeout": 60000,
}

# ==========================================
# CLASSES BASE (do seu código)
# ==========================================
class VolumeCalculator:
    """Calcula volume sintético e infere side"""
    def __init__(self):
        self.last_bid = {}
        self.last_ask = {}
        self.last_mid = {}
        self._init = {}
        self.weight_mode = 'price_weighted'
    
    def calc(self, symbol, bid, ask):
        mid = (bid + ask) / 2
        spread = ask - bid
        config = gcfg(symbol)
        
        if symbol not in self._init:
            self.last_bid[symbol] = bid
            self.last_ask[symbol] = ask
            self.last_mid[symbol] = mid
            self._init[symbol] = True
            return mid, 1.0, 0.0, 'buy', spread
        
        price_change = mid - self.last_mid[symbol]
        bid_change = bid - self.last_bid[symbol]
        ask_change = ask - self.last_ask[symbol]
        
        # Side inference
        if ask_change > 0 and abs(bid_change) < abs(ask_change) * 0.3:
            side = 'buy'
        elif bid_change < 0 and abs(ask_change) < abs(bid_change) * 0.3:
            side = 'sell'
        elif bid_change > 0 and ask_change > 0:
            side = 'buy'
        elif bid_change < 0 and ask_change < 0:
            side = 'sell'
        else:
            side = 'buy' if price_change >= 0 else 'sell'
        
        # Volume calculation
        if self.weight_mode == 'equal':
            vol = 1.0
        elif self.weight_mode == 'price_weighted':
            move = abs(price_change)
            vol = 1.0 + min(move * config['mult'], 10.0)
        else:
            vol = 1.0
        
        self.last_bid[symbol] = bid
        self.last_ask[symbol] = ask
        self.last_mid[symbol] = mid
        
        return mid, round(vol, 2), price_change, side, spread
    
    def reset(self, symbol=None):
        if symbol:
            for d in (self.last_bid, self.last_ask, self.last_mid, self._init):
                d.pop(symbol, None)
        else:
            for d in (self.last_bid, self.last_ask, self.last_mid, self._init):
                d.clear()

class MT5Connector:
    """Conexão com MT5"""
    def __init__(self):
        self.connected = False
    
    def init(self):
        if not MT5_AVAILABLE:
            return False
        
        try:
            if not mt5.initialize(**MT5_CONFIG):
                if not mt5.initialize():
                    return False
            
            self.connected = True
            acc = mt5.account_info()
            if acc:
                logger.info(f"✅ MT5: {acc.login} | {acc.server}")
            return True
        except Exception as e:
            logger.error(f"❌ MT5: {e}")
            return False
    
    def shutdown(self):
        if self.connected:
            mt5.shutdown()
            self.connected = False
    
    def get_tick(self, symbol):
        if not self.connected:
            return None
        try:
            return mt5.symbol_info_tick(symbol)
        except:
            return None

# ==========================================
# GLOBAL STATE
# ==========================================
connected_clients = set()
mt5_conn = MT5Connector()
vc = VolumeCalculator()
orchestrator = None
current_symbol = "XAUUSD"
active_symbols = ["XAUUSD", "EURUSD", "GBPUSD"]
tick_count = 0

# ==========================================
# WEBSOCKET HANDLER
# ==========================================
async def broadcast(msg):
    if not connected_clients:
        return
    data = json.dumps(msg)
    dead = set()
    for ws in connected_clients:
        try:
            await ws.send(data)
        except:
            dead.add(ws)
    connected_clients.difference_update(dead)

async def handle_client(ws, path=None):
    global current_symbol, orchestrator
    
    connected_clients.add(ws)
    logger.info(f"👤 Cliente conectado ({len(connected_clients)})")
    
    # Envia estado inicial
    await ws.send(json.dumps({
        'type': 'connected',
        'data': {
            'mt5_connected': mt5_conn.connected,
            'symbol': current_symbol,
            'symbols': active_symbols,
        }
    }))
    
    try:
        async for msg in ws:
            try:
                data = json.loads(msg)
                action = data.get('type') or data.get('action', '')
                
                # Switch symbol
                if action == 'switch_symbol':
                    sym = data.get('symbol', 'XAUUSD').upper()
                    if sym in SYM_CFG:
                        current_symbol = sym
                        vc.reset(sym)
                        if orchestrator:
                            orchestrator.symbol = sym
                        if mt5_conn.connected:
                            mt5_conn.enable_symbol(sym)
                        await ws.send(json.dumps({
                            'type': 'symbol_changed',
                            'symbol': sym,
                            'config': gcfg(sym),
                        }))
                
                # Análise de região
                elif action == 'analyze_region':
                    if orchestrator:
                        result = orchestrator.analyze_region(
                            data.get('start_idx', 0),
                            data.get('end_idx', 0)
                        )
                        await ws.send(json.dumps({
                            'type': 'region_analysis',
                            'data': result
                        }))
                
                # Heatmap de atenção
                elif action == 'attention_heatmap':
                    if orchestrator:
                        result = orchestrator.get_attention_heatmap(
                            data.get('center_idx', 0),
                            data.get('window', 20)
                        )
                        await ws.send(json.dumps({
                            'type': 'attention_heatmap',
                            'data': result
                        }))
                
                # Análise de rota
                elif action == 'route_analysis':
                    if orchestrator:
                        result = orchestrator.get_route_analysis(
                            data.get('target_idx', 0)
                        )
                        await ws.send(json.dumps({
                            'type': 'route_analysis',
                            'data': result
                        }))
                
                # Feedback para IA
                elif action == 'ai_feedback':
                    if orchestrator:
                        orchestrator.feedback(
                            data.get('predicted', 'NEUTRAL'),
                            data.get('actual', 'NEUTRAL')
                        )
                        await ws.send(json.dumps({
                            'type': 'feedback_received',
                            'status': 'ok'
                        }))
                
                # Ping
                elif action in ('ping', 'pong'):
                    await ws.send(json.dumps({'type': 'pong'}))
                    
            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.discard(ws)
        logger.info(f"👤 Desconectado ({len(connected_clients)})")

# ==========================================
# MAIN LOOPS
# ==========================================
async def mt5_poll_loop():
    global tick_count, orchestrator
    
    last_time = 0
    
    while True:
        if not mt5_conn.connected or not connected_clients:
            await asyncio.sleep(0.5)
            continue
        
        try:
            tick = mt5_conn.get_tick(current_symbol)
            
            if tick and tick.time != last_time:
                last_time = tick.time
                tick_count += 1
                
                if tick.bid > 0 and tick.ask > 0:
                    config = gcfg(current_symbol)
                    mid, vol, pc, side, spread = vc.calc(current_symbol, tick.bid, tick.ask)
                    
                    tick_data = {
                        'symbol': current_symbol,
                        'price': round(mid, config['dig']),
                        'bid': round(tick.bid, config['dig']),
                        'ask': round(tick.ask, config['dig']),
                        'volume_synthetic': round(vol, 2),
                        'side': side,
                        'timestamp': int(time.time() * 1000),
                        'spread': round(spread, config['dig']),
                        'price_change': round(pc, config['dig']),
                        'delta': vol if side == 'buy' else -vol,  # Simplificado
                        'volume': vol,
                        'aggressive_buy': vol if side == 'buy' else 0,
                        'aggressive_sell': vol if side == 'sell' else 0,
                    }
                    
                    # Atualiza orchestrator
                    if orchestrator:
                        orchestrator.update_data(tick_data)
                        analysis = orchestrator.analyze_current()
                        
                        # Envia tick + análise
                        await broadcast({
                            'type': 'tick',
                            'data': {
                                **tick_data,
                                'analysis': {
                                    'bar_type': analysis.bar_type,
                                    'execution_style': analysis.execution_style,
                                    'aggressive_ratio': analysis.aggressive_ratio,
                                    'ai_prediction': analysis.ai_prediction,
                                    'setup': analysis.setup,
                                    'narrative': analysis.narrative
                                }
                            }
                        })
                    else:
                        await broadcast({'type': 'tick', 'data': tick_data})
                    
                    if tick_count % 100 == 0:
                        logger.info(f"📊 #{tick_count} | {current_symbol} {mid:.{config['dig']}f}")
            
            await asyncio.sleep(0.03)
            
        except Exception as e:
            logger.error(f"❌ Poll: {e}")
            await asyncio.sleep(1)

async def simulation_loop():
    """Modo simulação quando MT5 offline"""
    global tick_count, orchestrator
    
    prices = {s: c['base'] for s, c in SYM_CFG.items()}
    n = 0
    
    while True:
        if mt5_conn.connected or not connected_clients:
            await asyncio.sleep(1)
            continue
        
        try:
            n += 1
            config = gcfg(current_symbol)
            bp = prices.get(current_symbol, config['base'])
            
            # Simula movimento
            nf = bp * 0.00005
            bp += math.sin(n / 300) * nf * 0.3 + (random.random() - 0.5) * nf
            prices[current_symbol] = bp
            
            sp = bp * 0.00008
            bid, ask = bp - sp / 2, bp + sp / 2
            mid, vol, pc, side, spread = vc.calc(current_symbol, bid, ask)
            tick_count += 1
            
            tick_data = {
                'symbol': current_symbol,
                'price': round(mid, config['dig']),
                'bid': round(bid, config['dig']),
                'ask': round(ask, config['dig']),
                'volume_synthetic': round(vol, 2),
                'side': side,
                'timestamp': int(time.time() * 1000),
                'spread': round(spread, config['dig']),
                'price_change': round(pc, config['dig']),
                'delta': vol if side == 'buy' else -vol,
                'volume': vol,
                'aggressive_buy': vol if side == 'buy' else 0,
                'aggressive_sell': vol if side == 'sell' else 0,
            }
            
            if orchestrator:
                orchestrator.update_data(tick_data)
                analysis = orchestrator.analyze_current()
                
                await broadcast({
                    'type': 'tick',
                    'data': {
                        **tick_data,
                        'analysis': {
                            'bar_type': analysis.bar_type,
                            'execution_style': analysis.execution_style,
                            'aggressive_ratio': analysis.aggressive_ratio,
                            'ai_prediction': analysis.ai_prediction,
                            'setup': analysis.setup,
                            'narrative': analysis.narrative
                        }
                    }
                })
            else:
                await broadcast({'type': 'tick', 'data': tick_data})
            
            await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"❌ Sim: {e}")
            await asyncio.sleep(1)

# ==========================================
# HTTP SERVER
# ==========================================
def start_http_server(port=8001):
    base = os.path.dirname(os.path.abspath(__file__))
    
    # Procura frontend
    for candidate in [
        os.path.join(base, "..", "frontend"),
        os.path.join(base, "frontend"),
    ]:
        if os.path.exists(os.path.join(candidate, "index.html")):
            os.chdir(candidate)
            break
    
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass
        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            super().end_headers()
    
    httpd = HTTPServer(("localhost", port), QuietHandler)
    logger.info(f"🌐 Frontend: http://localhost:{port}")
    httpd.serve_forever()

# ==========================================
# MAIN
# ==========================================
async def main():
    global orchestrator
    
    print("\n" + "=" * 60)
    print("  🚀 Market Analyzer Pro - IA Integrada")
    print("=" * 60)
    
    # Inicializa orchestrator
    orchestrator = AnalysisOrchestrator()
    logger.info("✅ AnalysisOrchestrator inicializado")
    
    # Conecta MT5
    if MT5_AVAILABLE:
        mt5_conn.init()
    
    # HTTP server
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    
    # WebSocket
    logger.info(f"📡 WebSocket: ws://localhost:8766")
    server = await websockets.serve(handle_client, "localhost", 8766)
    
    # Loops
    await asyncio.gather(
        server.wait_closed(),
        mt5_poll_loop(),
        simulation_loop()
    )

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())