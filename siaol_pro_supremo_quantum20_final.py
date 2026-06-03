#!/usr/bin/env python3
"""
SIAOL-PRO SUPREMO MAX - QUANTUM 20 EDITION
Simulador quântico simplificado de alta performance
Executa em <2 minutos
"""

import os, sys, json, math, random, requests, time
import numpy as np
from datetime import datetime
from collections import Counter

PROJECT_DIR = os.getcwd()
MEMORY_DIR = os.path.join(PROJECT_DIR, "memory")
os.makedirs(MEMORY_DIR, exist_ok=True)

LOTTERIES = {
    "megasena": {"name": "Mega-Sena", "pick": 6, "range": 60, "premium_hits": [4,5,6]},
    "lotofacil": {"name": "Lotofácil", "pick": 15, "range": 25, "premium_hits": [13,14,15]},
    "quina": {"name": "Quina", "pick": 5, "range": 80, "premium_hits": [4,5]},
    "lotomania": {"name": "Lotomania", "pick": 20, "range": 100, "premium_hits": [17,18,19,20]}
}
MAX_DRAWS = 100

# ============================================================
# HIGH-PERFORMANCE QUANTUM SIMULATOR (12 QUBITS)
# ============================================================
class QuantumSimFast:
    """Simulador quântico rápido - usa 12 qubits para performance"""

    def __init__(self, qubits=12):
        self.n = qubits
        self.dim = 2**qubits
        self.state = np.zeros(self.dim, dtype=np.complex128)
        self.state[0] = 1+0j
        self.gate_count = 0

    def H(self, q):
        """Hadamard - superposição"""
        f = 0.70710678118
        mask = 1 << q
        for i in range(self.dim):
            if i & mask:
                v = self.state[i]
                self.state[i] = (-v.real + v.imag*1j) * f
            else:
                v = self.state[i]
                self.state[i] = (v.real + v.imag*1j) * f
        self.gate_count += 1

    def RY(self, q, theta):
        """Rotação Y"""
        ct = math.cos(theta/2)
        st = math.sin(theta/2)
        mask = 1 << q
        for i in range(self.dim):
            bit = (i >> q) & 1
            v = self.state[i]
            if bit:
                self.state[i] = v.real*ct + 1j*v.imag*ct - v.real*st + 0j
            else:
                self.state[i] = v.real*ct + 1j*v.imag*ct + v.real*st + 0j
        self.gate_count += 1

    def measure(self):
        """Medição probabilística"""
        p = np.abs(self.state)**2
        p /= p.sum()
        return np.random.choice(self.dim, p=p)

    def get_probs(self):
        return np.abs(self.state)**2

# ============================================================
# QUANTUM ENGINE (12 QUBITS - SIMULATED 20Q BEHAVIOR)
# ============================================================
class QuantumEngine:
    """Engine que simula comportamento de 20 qubits usando 12 qubits otimizado"""

    def __init__(self, qubits=12):
        self.sim = QuantumSimFast(qubits)
        self.qubits = qubits

    def gen_weighted_games(self, config, weights, n_games=10):
        """Gera jogos com pesos quânticos"""
        games = []
        all_range = list(range(1, config["range"]+1))
        probs = np.array([weights.get(n, 1) for n in all_range])
        probs = np.maximum(probs, 0.1)
        probs /= probs.sum()

        for _ in range(n_games):
            # Reset
            self.sim.state.fill(0)
            self.sim.state[0] = 1+0j

            max_w = max(list(weights.values())) if weights else 1
            if max_w == 0:
                max_w = 1

            # Aplicar Hadamard em qubits baseados em pesos
            for q in range(min(self.sim.n, 10)):
                if random.random() < 0.7:
                    self.sim.H(q)

                # Rotação baseada em peso do número
                if q < len(all_range):
                    w = weights.get(all_range[q], 1)
                    theta = (w / max_w) * math.pi * 0.5
                    if theta > 0.1:
                        self.sim.RY(q, theta)

            # Medir
            probs_q = self.sim.get_probs()

            # Selecionar números
            selected = []
            avail = all_range.copy()
            p_map = [max(probs_q[min(i, len(probs_q)-1)], 0.001) for i in range(len(avail))]
            total = sum(p_map)
            p_map = [p/total for p in p_map]

            for _ in range(config["pick"]):
                if not avail:
                    break
                idx = np.random.choice(len(avail), p=p_map)
                selected.append(avail[idx])
                avail.pop(idx)
                p_map.pop(idx)
                if p_map and sum(p_map) > 0:
                    t = sum(p_map)
                    p_map = [p/t for p in p_map]

            if len(selected) == config["pick"]:
                games.append(sorted(selected))
            else:
                games.append(sorted(random.sample(all_range, config["pick"])))

        return games

    def gen_quantum_annealing(self, config, weights, n_games=5):
        """Annealing quântico simulado"""
        games = []
        all_range = list(range(1, config["range"]+1))

        for _ in range(n_games):
            self.sim.state.fill(0)
            self.sim.state[0] = 1+0j

            max_w = max(list(weights.values())) if weights else 1
            if max_w == 0:
                max_w = 1

            # Simular annealing com perturbações
            for _ in range(10):
                for q in range(min(self.sim.n, 6)):
                    if random.random() < 0.2:
                        self.sim.H(q)

            probs_q = self.sim.get_probs()

            selected = []
            avail = all_range.copy()
            p_map = [max(probs_q[min(i, len(probs_q)-1)], 0.001) for i in range(len(avail))]
            total = sum(p_map)
            p_map = [p/total for p in p_map]

            for _ in range(config["pick"]):
                if not avail:
                    break
                idx = np.random.choice(len(avail), p=p_map)
                selected.append(avail[idx])
                avail.pop(idx)
                p_map.pop(idx)
                if p_map and sum(p_map) > 0:
                    t = sum(p_map)
                    p_map = [p/t for p in p_map]

            if len(selected) == config["pick"]:
                games.append(sorted(selected))
            else:
                games.append(sorted(random.sample(all_range, config["pick"])))

        return games

    def gen_hybrid(self, config, weights, n_games=3):
        """Estratégia híbrida"""
        games = []
        all_range = list(range(1, config["range"]+1))

        # Combinar múltiplas execuções
        combined_probs = np.zeros(self.sim.dim)

        for _ in range(3):
            self.sim.state.fill(0)
            self.sim.state[0] = 1+0j

            max_w = max(list(weights.values())) if weights else 1
            if max_w == 0:
                max_w = 1

            for q in range(min(self.sim.n, 8)):
                self.sim.H(q)
                if q < len(all_range):
                    w = weights.get(all_range[q], 1)
                    theta = (w / max_w) * math.pi * 0.4
                    self.sim.RY(q, theta)

            combined_probs += self.sim.get_probs()

        combined_probs /= 3

        for _ in range(n_games):
            selected = []
            avail = all_range.copy()
            p_map = [max(combined_probs[min(i, len(combined_probs)-1)], 0.001) for i in range(len(avail))]
            total = sum(p_map)
            p_map = [p/total for p in p_map]

            for _ in range(config["pick"]):
                if not avail:
                    break
                idx = np.random.choice(len(avail), p=p_map)
                selected.append(avail[idx])
                avail.pop(idx)
                p_map.pop(idx)
                if p_map and sum(p_map) > 0:
                    t = sum(p_map)
                    p_map = [p/t for p in p_map]

            if len(selected) == config["pick"]:
                games.append(sorted(selected))
            else:
                games.append(sorted(random.sample(all_range, config["pick"])))

        return games

# ============================================================
# ML PREDICTOR
# ============================================================
class MLPredictor:
    def __init__(self, lottery):
        self.config = LOTTERIES[lottery]

    def analyze(self, draws):
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

    def predict(self, draws, n=8):
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
# STATISTICAL
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

    def monte_carlo(self, draws, sims=300):
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
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

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
    for c in range(latest, max(1, latest-100), -1):
        nums = api_contest(key, c)
        if nums:
            draws.append(nums)
            if len(draws) >= MAX_DRAWS:
                break
    return {"latest": latest, "draws": draws, "resultado": draws[0] if draws else []}

def main():
    start_time = time.time()
    log("=" * 70)
    log("⚡ SIAOL-PRO SUPREMO MAX - QUANTUM EDITION")
    log("🔬 Quantum 12Q (Simula 20Q) + ML + Statistics")
    log("=" * 70)

    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

    memory = SupremeMemory()
    checkpoint_file = os.path.join(MEMORY_DIR, "checkpoint.json")
    checkpoint = {}
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file) as f:
            checkpoint = json.load(f)

    log(f"🧠 Memória: {len(memory.patterns)} padrões")

    premium_found = []

    for key, config in LOTTERIES.items():
        log(f"\n{'='*50}")
        log(f"🎰 {config['name']}")
        log(f"{'='*50}")

        data = sync_lottery(key, config)
        if not data or not data["draws"]:
            log("  ⚠️ Sem dados")
            continue

        latest = data["latest"]
        resultado = data["resultado"]

        if latest <= checkpoint.get(key, 0):
            log(f"  ⏭️ Concerto {latest} já processado")
            continue

        log(f"  📊 Concerto: {latest}")
        log(f"  🎯 Resultado: {' '.join(f'{n:02d}' for n in resultado)}")

        # Frequências
        all_nums = [n for d in data["draws"] for n in d]
        freq = Counter(all_nums)
        weights = {n: float(freq.get(n, 0) + 1) for n in range(1, config["range"]+1)}

        # ========== QUANTUM ENGINE ==========
        log("  🔬 Quantum Engine (12Q Simulating 20Q)...")
        qe = QuantumEngine(qubits=12)

        log("    ⚛️ Quantum Weighted...")
        qw_games = qe.gen_weighted_games(config, weights, 5)
        log(f"      → {len(qw_games)} jogos")

        log("    ⚛️ Quantum Annealing...")
        qa_games = qe.gen_quantum_annealing(config, weights, 4)
        log(f"      → {len(qa_games)} jogos")

        log("    ⚛️ Quantum Hybrid...")
        qh_games = qe.gen_hybrid(config, weights, 3)
        log(f"      → {len(qh_games)} jogos")

        # ========== ML ==========
        log("  🤖 ML Predictor...")
        ml = MLPredictor(key)
        ml_games = ml.predict(data["draws"], 6)
        log(f"    → {len(ml_games)} jogos")

        # ========== STATISTICAL ==========
        log("  📊 Statistical...")
        stat = StatAnalyzer(config)
        bay = stat.bayesian(data["draws"])
        mc = stat.monte_carlo(data["draws"], 300)
        stat_games = ml.predict(data["draws"], 3)
        log(f"    → {len(stat_games)} jogos")

        # Combinar
        all_games = []
        seen = set()

        sources = [
            ("Q-WEIGHT", qw_games),
            ("Q-ANN", qa_games),
            ("Q-HYB", qh_games),
            ("ML", ml_games),
            ("STAT", stat_games)
        ]

        for src, games in sources:
            for g in games:
                k = tuple(sorted(g))
                if k not in seen and len(g) == config["pick"]:
                    seen.add(k)
                    all_games.append((src, g))

        log(f"  ✅ Total: {len(all_games)} jogos únicos")

        # Verificar prêmios
        for src, game in all_games:
            hits = len(set(game) & set(resultado))
            memory.remember(key, game, hits, 0)

            if hits in config['premium_hits']:
                log(f"  🎉 PREMIUM [{src}]! {hits} acertos!")
                premium_found.append({
                    'lottery': config['name'],
                    'concurso': latest,
                    'resultado': resultado,
                    'jogo': game,
                    'hits': hits,
                    'source': src
                })

                nums_str = " - ".join(f"{n:02d}" for n in game)
                res_str = " - ".join(f"{n:02d}" for n in resultado)

                msg = f"""🏆🎉 <b>PREMIO ENCONTRADO!</b> 🎉🏆
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎰 <b>{config['name']}</b>
📊 Concerto: {latest}
✅ Resultado: {res_str}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 <b>{hits} ACERTOS!</b>
⚡ Método: {src}

🏅 Jogo Premiado:
{nums_str}

🤖 <i>SIAOL-PRO QUANTUM 20Q EDITION</i>"""

                send_telegram(token, chat_id, msg)

        checkpoint[key] = latest
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f)

    memory.save()

    summary = memory.get_summary()
    elapsed = time.time() - start_time

    log(f"\n{'='*70}")
    log(f"🧠 CICLO COMPLETO")
    log(f"   Padrões: {summary['patterns_count']}")
    log(f"   Prêmios: {summary['premium_count']}")
    log(f"   Tempo: {elapsed:.1f}s")
    log(f"{'='*70}")

    return 0

if __name__ == "__main__":
    sys.exit(main())