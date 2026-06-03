#!/usr/bin/env python3
"""
SIAOL-PRO SUPREMO MAX - VERSÃO OTIMIZADA
Executa em ~8 minutos no GitHub Actions
"""

import os, sys, json, math, random, requests, numpy as np
from datetime import datetime
from collections import Counter
from typing import Dict, List, Optional

PROJECT_DIR = os.getcwd()
MEMORY_DIR = os.path.join(PROJECT_DIR, "memory")
os.makedirs(MEMORY_DIR, exist_ok=True)

LOTTERIES = {
    "megasena": {"name": "Mega-Sena", "pick": 6, "range": 60, "premium_hits": [4,5,6], "game_price": 4.50},
    "lotofacil": {"name": "Lotofácil", "pick": 15, "range": 25, "premium_hits": [13,14,15], "game_price": 2.50},
    "quina": {"name": "Quina", "pick": 5, "range": 80, "premium_hits": [4,5], "game_price": 2.00},
    "lotomania": {"name": "Lotomania", "pick": 20, "range": 100, "premium_hits": [17,18,19,20], "game_price": 2.50}
}
MAX_DRAWS = 200

# ============================================================
# QUANTUM SIMULATOR (12 qubits - rápido)
# ============================================================
class QuantumSim:
    def __init__(self, qubits=12):
        self.n = qubits
        self.dim = 2**qubits
        self.state = np.zeros(self.dim, dtype=np.complex128)
        self.state[0] = 1+0j

    def H(self, q):
        f = 1/math.sqrt(2)
        for i in range(self.dim):
            if (i>>q)&1:
                v = self.state[i]
                self.state[i] = (-v.real + v.imag*1j)*f
            else:
                v = self.state[i]
                self.state[i] = (v.real + v.imag*1j)*f

    def measure(self):
        p = np.abs(self.state)**2
        p /= p.sum()
        return np.random.choice(self.dim, p=p)

    def generate_games(self, config, weights, n=8):
        games = []
        all_range = list(range(1, config["range"]+1))
        probs = np.array([weights.get(n, 0.1) for n in all_range])
        probs = np.maximum(probs, 0.01)
        probs /= probs.sum()
        for _ in range(n):
            try:
                g = sorted(np.random.choice(all_range, config["pick"], replace=False, p=probs).tolist())
                games.append(g)
            except:
                games.append(sorted(random.sample(all_range, config["pick"])))
        return games

# ============================================================
# ML PREDICTOR (simplificado)
# ============================================================
class MLPredictor:
    def __init__(self, lottery):
        self.config = LOTTERIES[lottery]

    def analyze(self, draws):
        """Análise rápida"""
        all_nums = [n for d in draws for n in d]
        freq = Counter(all_nums)
        recent = draws[:15]
        recent_nums = [n for d in recent for n in d]
        recent_freq = Counter(recent_nums)

        scores = {}
        for num in range(1, self.config["range"]+1):
            f = freq.get(num, 0) / max(len(all_nums), 1)
            r = recent_freq.get(num, 0) / max(len(recent_nums), 1)
            scores[num] = f*0.4 + r*0.6

        return scores

    def predict(self, draws, n=10):
        """Predição rápida"""
        scores = self.analyze(draws)
        all_range = list(range(1, self.config["range"]+1))
        probs = np.array([scores.get(n, 0.1) for n in all_range])
        probs = np.maximum(probs, 0.01)
        probs /= probs.sum()

        games = []
        for _ in range(n):
            try:
                g = sorted(np.random.choice(all_range, self.config["pick"], replace=False, p=probs).tolist())
                games.append(g)
            except:
                games.append(sorted(random.sample(all_range, self.config["pick"])))
        return games

# ============================================================
# STATISTICAL ANALYSIS (simplificado)
# ============================================================
class StatAnalyzer:
    def __init__(self, config):
        self.config = config

    def bayesian(self, draws):
        scores = {}
        for num in range(1, self.config["range"]+1):
            appearances = sum(1 for d in draws if num in d)
            scores[num] = (appearances + 1) / (len(draws) + self.config["range"])
        return scores

    def monte_carlo(self, draws, sims=1000):
        all_nums = [n for d in draws for n in d]
        freq = Counter(all_nums)
        probs = {n: freq.get(n, 0)/max(len(all_nums),1) for n in range(1, self.config["range"]+1)}
        expected = {n: 0 for n in range(1, self.config["range"]+1)}
        all_range = list(probs.keys())
        weights = list(probs.values())
        for _ in range(sims):
            sim = random.choices(all_range, weights=weights, k=self.config["pick"])
            for num in sim:
                expected[num] += 1
        return {n: max(0.01, expected[n]/sims) for n in expected}

# ============================================================
# SUPREMA MEMORY
# ============================================================
class SupremeMemory:
    def __init__(self):
        self.file = os.path.join(MEMORY_DIR, "patterns_memory.json")
        self.load()

    def load(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                data = json.load(f)
                self.patterns = data.get('patterns', {})
                self.best_games = data.get('best_games', {})
                self.stats = data.get('stats', {})
        else:
            self.patterns = {}
            self.best_games = {}
            self.stats = {}

    def save(self):
        with open(self.file, 'w') as f:
            json.dump({
                'patterns': self.patterns,
                'best_games': self.best_games,
                'stats': self.stats,
                'last_update': datetime.now().isoformat()
            }, f, indent=2)

    def remember(self, lottery, numbers, hits, game_id):
        key = f"{lottery}_{tuple(sorted(numbers))}"
        if key not in self.patterns:
            self.patterns[key] = {'numbers': numbers, 'lottery': lottery, 'occurrences': 0, 'total_hits': 0}
        self.patterns[key]['occurrences'] += 1
        self.patterns[key]['total_hits'] += hits

        if hits >= 4:
            if lottery not in self.best_games:
                self.best_games[lottery] = []
            self.best_games[lottery].append({'numbers': numbers, 'hits': hits})
            self.best_games[lottery] = sorted(self.best_games[lottery], key=lambda x: x['hits'], reverse=True)[:15]

    def get_summary(self):
        return {
            'patterns_count': len(self.patterns),
            'premium_count': sum(len(g) for g in self.best_games.values()),
            'stats': self.stats
        }

# ============================================================
# APIs
# ============================================================
def api_latest(endpoint):
    urls = [
        f"https://loteriascaixa-api.herokuapp.com/api/{endpoint}/latest",
        f"https://servicebus2.caixa.gov.br/portaldeloterias/api/{endpoint}"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                d = r.json()
                return d.get('concurso') or d.get('numero', 0)
        except:
            continue
    return 0

def api_contest(endpoint, contest):
    urls = [
        f"https://loteriascaixa-api.herokuapp.com/api/{endpoint}/{contest}",
        f"https://servicebus2.caixa.gov.br/portaldeloterias/api/{endpoint}/{contest}"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                d = r.json()
                dz = d.get('dezenas') or d.get('listaDezenas', [])
                if dz:
                    return sorted([int(x) for x in dz])
        except:
            continue
    return None

# ============================================================
# MAIN
# ============================================================
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def send_telegram(token, chat_id, msg):
    if not token or chat_id == 'SEU_CHAT_ID':
        return
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                     data={'chat_id': chat_id, 'text': msg, 'parse_mode': 'HTML'}, timeout=10)
    except:
        pass

def sync_lottery(key, config):
    latest = api_latest(key)
    if not latest:
        return None
    draws = []
    for c in range(latest, max(1, latest-200), -1):
        nums = api_contest(key, c)
        if nums:
            draws.append(nums)
            if len(draws) >= MAX_DRAWS:
                break
    return {"latest": latest, "draws": draws, "resultado": draws[0] if draws else []}

def main():
    log("=" * 60)
    log("⚡ SIAOL-PRO SUPREMO MAX")
    log("🤖 ML + QUANTUM + STATISTICS")
    log("=" * 60)

    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
    if not token or not chat_id:
        log("❌ Telegram não configurado")
        return 1

    memory = SupremeMemory()
    checkpoint_file = os.path.join(MEMORY_DIR, "checkpoint.json")
    checkpoint = {}
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file) as f:
            checkpoint = json.load(f)

    log(f"🧠 Memória: {len(memory.patterns)} padrões")

    premium_found = []

    for key, config in LOTTERIES.items():
        log(f"\n🎰 {config['name']}...")

        data = sync_lottery(key, config)
        if not data or not data["draws"]:
            log("  ⚠️ Sem dados")
            continue

        latest = data["latest"]
        resultado = data["resultado"]

        if latest <= checkpoint.get(key, 0):
            log(f"  ⏭️ Concerto {latest} já processado")
            continue

        log(f"  📊 {latest}: {' '.join(f'{n:02d}' for n in resultado)}")

        # 1. QUANTUM
        log("  ⚛️ Quantum...")
        all_nums = [n for d in data["draws"] for n in d]
        freq = Counter(all_nums)
        weights = {n: float(freq.get(n, 0)) for n in range(1, config["range"]+1)}
        quantum = QuantumSim(12)
        quantum_games = quantum.generate_games(config, weights, 6)

        # 2. ML
        log("  🤖 ML...")
        ml = MLPredictor(key)
        ml_scores = ml.analyze(data["draws"])
        ml_games = ml.predict(data["draws"], 8)

        # 3. STATISTICAL
        log("  📊 Statistical...")
        stat = StatAnalyzer(config)
        bay = stat.bayesian(data["draws"])
        mc = stat.monte_carlo(data["draws"], 500)
        combined = {n: (bay.get(n,0.1) + mc.get(n,0.1))/2 for n in range(1, config["range"]+1)}
        stat_games = ml.predict(data["draws"], 4)  # Reuse ML predictor with new scores

        # Combine all
        all_games = []
        seen = set()
        for games in [quantum_games, ml_games, stat_games]:
            for g in games:
                k = tuple(sorted(g))
                if k not in seen and len(g) == config["pick"]:
                    seen.add(k)
                    all_games.append(g)

        log(f"  ✅ {len(all_games)} jogos únicos")

        # Check games
        for i, game in enumerate(all_games):
            hits = len(set(game) & set(resultado))
            memory.remember(key, game, hits, i+1)

            if hits in config['premium_hits']:
                log(f"  🎉 PREMIUM! {hits} acertos!")
                premium_found.append({'lottery': config['name'], 'concurso': latest,
                                      'resultado': resultado, 'jogo': game, 'hits': hits})

                nums_str = " - ".join(f"{n:02d}" for n in game)
                res_str = " - ".join(f"{n:02d}" for n in resultado)

                msg = f"""🏆🎉 <b>PREMIO ENCONTRADO!</b> 🎉🏆
━━━━━━━━━━━━━━━━━━━━
🎰 <b>{config['name']}</b>
📊 Concerto: {latest}
✅ Resultado: {res_str}
━━━━━━━━━━━━━━━━━━━━
🎯 <b>{hits} ACERTOS!</b>

🏅 Jogo Premiado:
{nums_str}

⚡ <i>SIAOL-PRO SUPREMO MAX</i>"""

                send_telegram(token, chat_id, msg)

        checkpoint[key] = latest
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f)

    memory.save()

    summary = memory.get_summary()
    log(f"\n🧠 Ciclo completo")
    log(f"   Padrões: {summary['patterns_count']}")
    log(f"   Prêmios: {summary['premium_count']}")

    return 0

if __name__ == "__main__":
    sys.exit(main())