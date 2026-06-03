#!/usr/bin/env python3
"""
SIAOL-PRO SUPREMO MAX - ULTIMATE EDITION v4
Sistema AUTO-EVOLUTIVO com Consciência Temporal

FUNCIONALIDADES:
- Consciência temporal (data, dia da semana, sazonalidade)
- Auto-aprendizado com backtests contínuos
- Sistema quântico auto-evolutivo
- Backtesting e otimização de parâmetros
- Notificações inteligentes por dia de sorteio
"""

import os, sys, json, math, random, requests, time
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List

PROJECT_DIR = os.getcwd()
MEMORY_DIR = os.path.join(PROJECT_DIR, "memory")
os.makedirs(MEMORY_DIR, exist_ok=True)

LOTTERIES = {
    "megasena": {
        "name": "Mega-Sena", "pick": 6, "range": 60,
        "premium_hits": [4,5,6], "emoji": "🎰",
        "draw_days": [3, 5],  # Quarta e sábado
        "draw_times": ["20:00"]
    },
    "lotofacil": {
        "name": "Lotofácil", "pick": 15, "range": 25,
        "premium_hits": [13,14,15], "emoji": "🎯",
        "draw_days": [1, 2, 3, 4, 5, 6],  # Segunda a sábado
        "draw_times": ["20:00"]
    },
    "quina": {
        "name": "Quina", "pick": 5, "range": 80,
        "premium_hits": [4,5], "emoji": "🎲",
        "draw_days": [1, 2, 3, 4, 5, 6],  # Segunda a sábado
        "draw_times": ["20:00"]
    },
    "lotomania": {
        "name": "Lotomania", "pick": 20, "range": 100,
        "premium_hits": [17,18,19,20], "emoji": "🎴",
        "draw_days": [2, 4, 6],  # Terça, quinta, sábado
        "draw_times": ["20:00"]
    }
}
MAX_DRAWS = 100

# ============================================================
# TEMPORAL CONSCIOUSNESS (CONSCIÊNCIA TEMPORAL)
# ============================================================
class TemporalConsciousness:
    """Sistema de consciência temporal"""

    WEEKDAYS = {
        0: "Segunda-feira",
        1: "Terça-feira",
        2: "Quarta-feira",
        3: "Quinta-feira",
        4: "Sexta-feira",
        5: "Sábado",
        6: "Domingo"
    }

    def __init__(self):
        self.now = datetime.now()
        self.date = self.now.strftime("%d/%m/%Y")
        self.time = self.now.strftime("%H:%M:%S")
        self.weekday = self.now.weekday()
        self.weekday_name = self.WEEKDAYS[self.weekday]
        self.day_of_year = self.now.timetuple().tm_yday
        self.week_of_year = self.now.isocalendar()[1]
        self.month = self.now.month
        self.year = self.now.year

    def is_draw_day(self, lottery):
        """Verifica se é dia de sorteio"""
        return self.weekday in LOTTERIES[lottery]["draw_days"]

    def get_next_draw(self, lottery):
        """Retorna próximo sorteio"""
        days = LOTTERIES[lottery]["draw_days"]
        current = self.weekday

        for i in range(1, 8):
            next_day = (current + i) % 7
            if next_day in days:
                next_date = self.now + timedelta(days=i)
                return {
                    'day': self.WEEKDAYS[next_day],
                    'date': next_date.strftime("%d/%m/%Y"),
                    'time': LOTTERIES[lottery]["draw_times"][0]
                }
        return None

    def get_season(self):
        """Retorna estação do ano"""
        if self.month in [12, 1, 2]:
            return "Verão"
        elif self.month in [3, 4, 5]:
            return "Outono"
        elif self.month in [6, 7, 8]:
            return "Inverno"
        else:
            return "Primavera"

    def get_temporal_weights(self):
        """Retorna pesos baseados em sazonalidade"""
        weights = {}

        # Peso do dia da semana
        if self.weekday in [5, 6]:  # Fim de semana
            weights['weekend'] = 1.2
        else:
            weights['weekend'] = 1.0

        # Peso mensal (início vs fim)
        if self.now.day <= 10:
            weights['month_phase'] = 'inicio'
        elif self.now.day >= 20:
            weights['month_phase'] = 'fim'
        else:
            weights['month_phase'] = 'meio'

        # Estação
        weights['season'] = self.get_season()

        return weights

    def format_status(self):
        """Formata status temporal"""
        return f"""
╔═══════════════════════════════════════════════════════════╗
║  🕐 CONSCIÊNCIA TEMPORAL                                ║
╠═══════════════════════════════════════════════════════════╣
║  📅 Data: {self.date:<50}║
║  🕐 Hora: {self.time:<50}║
║  📆 Dia: {self.weekday_name:<50}║
║  🌡️  Estação: {self.get_season():<48}║
║  📅 Mês/Dia: {f"{self.month}/{self.day_of_year}":<46}║
╚═══════════════════════════════════════════════════════════╝
"""

# ============================================================
# EVOLUTIONARY MEMORY (MEMÓRIA EVOLUTIVA)
# ============================================================
class EvolutionaryMemory:
    """Sistema de memória que aprende e evolui"""

    def __init__(self):
        self.file = os.path.join(MEMORY_DIR, "evolutionary_memory.json")
        self.load()

    def load(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                data = json.load(f)
                self.best_patterns = data.get('best_patterns', {})
                self.strategy_scores = data.get('strategy_scores', {})
                self.evolution_history = data.get('evolution_history', [])
                self.backtest_results = data.get('backtest_results', {})
                self.parameters = data.get('parameters', {})
        else:
            self.best_patterns = {}
            self.strategy_scores = {}
            self.evolution_history = []
            self.backtest_results = {}
            self.parameters = self._get_default_parameters()

    def _get_default_parameters(self):
        """Parâmetros padrão que evoluem"""
        return {
            'quantum_weight': 0.4,
            'ml_weight': 0.3,
            'stat_weight': 0.3,
            'hot_weight': 0.5,
            'cold_weight': 0.3,
            'annealing_steps': 15,
            'monte_carlo_sims': 500,
            'generation_rounds': 10
        }

    def save(self):
        with open(self.file, 'w') as f:
            json.dump({
                'best_patterns': self.best_patterns,
                'strategy_scores': self.strategy_scores,
                'evolution_history': self.evolution_history[-100:],  # Manter últimos 100
                'backtest_results': self.backtest_results,
                'parameters': self.parameters,
                'last_update': datetime.now().isoformat()
            }, f, indent=2)

    def record_result(self, lottery, strategy, hits, game):
        """Registra resultado para evolução"""
        key = f"{lottery}_{strategy}"

        if key not in self.strategy_scores:
            self.strategy_scores[key] = {'total_hits': 0, 'games': 0, 'best_hits': 0}

        self.strategy_scores[key]['total_hits'] += hits
        self.strategy_scores[key]['games'] += 1
        if hits > self.strategy_scores[key]['best_hits']:
            self.strategy_scores[key]['best_hits'] = hits

        # Registrar padrão se for bom
        if hits >= 4:
            pattern_key = f"{lottery}_{tuple(sorted(game))}"
            if pattern_key not in self.best_patterns:
                self.best_patterns[pattern_key] = {
                    'numbers': game,
                    'lottery': lottery,
                    'strategy': strategy,
                    'hits': hits,
                    'times_won': 1
                }
            else:
                self.best_patterns[pattern_key]['times_won'] += 1
                self.best_patterns[pattern_key]['hits'] = max(hits, self.best_patterns[pattern_key]['hits'])

    def evolve_parameters(self):
        """Evolui parâmetros baseado nos resultados"""
        # Analisar quais estratégias estão funcionando melhor
        best_strategies = sorted(
            self.strategy_scores.items(),
            key=lambda x: x[1]['total_hits'] / max(x[1]['games'], 1),
            reverse=True
        )

        if best_strategies:
            top_strategy = best_strategies[0][0]
            strategy_type = top_strategy.split('_')[1] if '_' in top_strategy else 'quantum'

            # Ajustar pesos
            if 'quantum' in strategy_type:
                self.parameters['quantum_weight'] = min(0.6, self.parameters['quantum_weight'] + 0.02)
                self.parameters['ml_weight'] = max(0.2, self.parameters['ml_weight'] - 0.01)
            elif 'ml' in strategy_type:
                self.parameters['ml_weight'] = min(0.5, self.parameters['ml_weight'] + 0.02)
                self.parameters['quantum_weight'] = max(0.2, self.parameters['quantum_weight'] - 0.01)

            # Ajustar simulações
            if len(self.backtest_results) > 50:
                recent_avg = np.mean([r['hits'] for r in list(self.backtest_results.values())[-50:]])
                if recent_avg < 3:
                    self.parameters['monte_carlo_sims'] = min(1000, self.parameters['monte_carlo_sims'] + 50)
                    self.parameters['annealing_steps'] = min(25, self.parameters['annealing_steps'] + 2)

        # Registrar evolução
        self.evolution_history.append({
            'timestamp': datetime.now().isoformat(),
            'parameters': self.parameters.copy(),
            'best_strategies': [(k, v) for k, v in best_strategies[:3]]
        })

        self.save()

    def get_best_parameters(self):
        """Retorna melhores parâmetros atuais"""
        return self.parameters

    def run_backtest(self, lottery, draws, n_games=50):
        """Executa backtesting dos jogos"""
        results = []

        for i, draw in enumerate(draws[:20]):  # Testar últimos 20
            if i == 0:
                continue  # Pular o mais recente

            historical = draws[i+1:]
            if len(historical) < 10:
                continue

            # Gerar jogos baseado no histórico
            all_nums = [n for d in historical for n in d]
            freq = Counter(all_nums)
            weights = {n: float(freq.get(n, 0) + 1) for n in range(1, LOTTERIES[lottery]["range"]+1)}

            # Simular geração
            games = []
            for _ in range(n_games):
                game = sorted(random.sample(list(weights.keys()), LOTTERIES[lottery]["pick"]))
                games.append(game)

            # Verificar acertos
            for game in games:
                hits = len(set(game) & set(draw))
                results.append({'expected': draw, 'game': game, 'hits': hits})

        # Salvar resultados
        self.backtest_results[f"{lottery}_{datetime.now().isoformat()}"] = {
            'results': results,
            'avg_hits': np.mean([r['hits'] for r in results]) if results else 0
        }

        self.save()
        return results

# ============================================================
# QUANTUM SIMULATOR (12 QUBITS)
# ============================================================
class QuantumSimFast:
    def __init__(self, qubits=12):
        self.n = qubits
        self.dim = 2**qubits
        self.state = np.zeros(self.dim, dtype=np.complex128)
        self.state[0] = 1+0j
        self.gate_count = 0

    def H(self, q):
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

    def CNOT(self, control, target):
        """Porta CNOT - Emaranhamento quântico"""
        mask_control = 1 << control
        mask_target = 1 << target
        for i in range(self.dim):
            if i & mask_control:  # Control qubit is 1
                if i & mask_target:  # Target is 1 -> flip to 0
                    self.state[i] = 0
                    self.state[i ^ mask_target] += self.state[i - mask_target] if i >= mask_target else 0
                else:  # Target is 0 -> flip to 1
                    new_i = i | mask_target
                    temp = self.state[i]
                    self.state[i] = 0
                    self.state[new_i] += temp
        self.gate_count += 1

    def measure(self, q):
        """Medição de um qubit - colapsa para 0 ou 1"""
        probs = np.zeros(2)
        mask = 1 << q
        for i in range(self.dim):
            if i & mask:
                probs[1] += np.abs(self.state[i])**2
            else:
                probs[0] += np.abs(self.state[i])**2
        # Normalizar
        total = probs[0] + probs[1]
        if total > 0:
            probs /= total
        return 0 if random.random() < probs[0] else 1

    def get_probs(self):
        return np.abs(self.state)**2

# ============================================================
# QUANTUM ENGINE (AUTO-EVOLUTIVO)
# ============================================================
class QuantumEngine:
    def __init__(self, qubits=12, params=None):
        self.sim = QuantumSimFast(qubits)
        self.qubits = qubits
        self.params = params or {
            'quantum_weight': 0.4,
            'annealing_steps': 15
        }

    def gen_evolutionary_games(self, config, weights, temporal, n_games=10):
        """Gera jogos com evolução temporal"""
        games = []
        all_range = list(range(1, config["range"]+1))

        # Ajustar pesos baseado na consciência temporal
        temp_weights = temporal.get_temporal_weights()

        for _ in range(n_games):
            self.sim.state.fill(0)
            self.sim.state[0] = 1+0j

            max_w = max(list(weights.values())) if weights else 1
            if max_w == 0:
                max_w = 1

            # Aplicar superposição com pesos temporais
            for q in range(min(self.sim.n, 10)):
                if random.random() < 0.7 * temp_weights.get('weekend', 1):
                    self.sim.H(q)

                if q < len(all_range):
                    w = weights.get(all_range[q], 1)
                    # Ajustar peso por fase do mês
                    if temp_weights.get('month_phase') == 'inicio':
                        w *= 1.1
                    elif temp_weights.get('month_phase') == 'fim':
                        w *= 0.9

                    theta = (w / max_w) * math.pi * 0.5
                    if theta > 0.1:
                        self.sim.RY(q, theta)

            # Annealing com parâmetros evoluídos
            for _ in range(self.params.get('annealing_steps', 15)):
                for q in range(min(self.sim.n, 6)):
                    if random.random() < 0.2:
                        self.sim.H(q)

            probs_q = self.sim.get_probs()
            selected = self._select(all_range, probs_q, config["pick"])
            if selected:
                games.append(sorted(selected))

        return games

    def _select(self, all_range, probs, count):
        selected = []
        avail = all_range.copy()
        p_map = [max(probs[min(i, len(probs)-1)], 0.001) for i in range(len(avail))]
        total = sum(p_map)
        p_map = [p/total for p in p_map]

        for _ in range(count):
            if not avail:
                break
            idx = np.random.choice(len(avail), p=p_map)
            selected.append(avail[idx])
            avail.pop(idx)
            p_map.pop(idx)
            if p_map and sum(p_map) > 0:
                t = sum(p_map)
                p_map = [p/t for p in p_map]

        return selected if len(selected) == count else None

# ============================================================
# ML PREDICTOR
# ============================================================
class MLPredictor:
    def __init__(self, lottery):
        self.config = LOTTERIES[lottery]

    def analyze(self, draws, temporal=None):
        all_nums = [n for d in draws for n in d]
        freq = Counter(all_nums)
        recent = draws[:15]
        recent_nums = [n for d in recent for n in d]
        recent_freq = Counter(recent_nums)

        scores = {}
        for num in range(1, self.config["range"]+1):
            f = freq.get(num, 0) / max(len(all_nums), 1)
            r = recent_freq.get(num, 0) / max(len(recent_nums), 1)

            # Hot/Cold analysis
            hots = [n for n, c in freq.most_common(10)]
            colds = [n for n, c in freq.most_common()[-10:]]
            hot_score = 1.2 if num in hots else 0.8
            cold_score = 1.1 if num in colds else 0.9

            scores[num] = f*0.3 + r*0.4 + hot_score*0.15 + cold_score*0.15

        return scores

    def predict(self, draws, n=10):
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

    def monte_carlo(self, draws, sims=500):
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

    def fft_analysis(self, draws, top_n=10):
        """Análise FFT para detectar ciclos ocultos nos sorteios"""
        if len(draws) < 20:
            return {}

        n_range = self.config["range"]
        time_series = np.zeros((n_range, len(draws)))

        # Criar série temporal: 1 se número apareceu, 0 se não
        for t, draw in enumerate(draws):
            for num in draw:
                if 1 <= num <= n_range:
                    time_series[num - 1, t] = 1

        # Para cada número, calcular FFT e encontrar ciclos dominantes
        fft_scores = {}
        for num in range(1, n_range + 1):
            signal = time_series[num - 1]

            # FFT
            fft_result = np.fft.fft(signal)
            freqs = np.fft.fftfreq(len(signal))

            # Encontrar frequências dominantes (excluindo DC e muito baixas)
            magnitudes = np.abs(fft_result)
            magnitudes[0] = 0  # Remover componente DC

            # Encontrar pico de frequência
            if len(magnitudes) > 1:
                dominant_freq_idx = np.argmax(magnitudes[1:]) + 1
                dominant_freq = abs(freqs[dominant_freq_idx]) if dominant_freq_idx < len(freqs) else 0

                # Calcular período (ciclos por quantidade de concursos)
                if dominant_freq > 0:
                    period = int(1 / dominant_freq) if dominant_freq != 0 else 0
                else:
                    period = 0

                # Score baseado na magnitude e regularidade
                fft_scores[num] = {
                    'magnitude': float(magnitudes[dominant_freq_idx]) if dominant_freq_idx < len(magnitudes) else 0,
                    'period': period,
                    'regularity': float(magnitudes[dominant_freq_idx]) / max(sum(magnitudes), 1) if sum(magnitudes) > 0 else 0
                }
            else:
                fft_scores[num] = {'magnitude': 0, 'period': 0, 'regularity': 0}

        # Ordenar por magnitude de ciclo
        sorted_by_cycle = sorted(fft_scores.items(), key=lambda x: x[1]['magnitude'], reverse=True)

        return {
            'top_cyclics': [n for n, s in sorted_by_cycle[:top_n]],
            'cycles_detected': sum(1 for n, s in fft_scores.items() if s['magnitude'] > 2),
            'avg_period': np.mean([s['period'] for s in fft_scores.values() if s['period'] > 0]) if fft_scores else 0
        }

# ============================================================
# PORTFÓLIO PERSISTENTE
# ============================================================
class Portfolio:
    def __init__(self):
        self.file = os.path.join(MEMORY_DIR, "portfolio.json")
        self.load()

    def load(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                data = json.load(f)
                self.games = data.get('games', {})
                self.last_update = data.get('last_update', '')
        else:
            self.games = {}
            self.last_update = ''

    def save(self):
        with open(self.file, 'w') as f:
            json.dump({
                'games': self.games,
                'last_update': datetime.now().isoformat()
            }, f, indent=2)

    def add_games(self, lottery, games, source, concurso=None):
        if lottery not in self.games:
            self.games[lottery] = []

        for game in games:
            exists = any(tuple(sorted(g['numbers'])) == tuple(sorted(game)) for g in self.games[lottery])
            if not exists:
                self.games[lottery].append({
                    'numbers': sorted(game),
                    'source': source,
                    'created_at': datetime.now().isoformat(),
                    'concurso': concurso
                })

        self.last_update = datetime.now().isoformat()
        self.save()

    def get_all_games(self, lottery):
        return self.games.get(lottery, [])

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
# TELEGRAM
# ============================================================
def send_telegram(token, chat_id, msg):
    if not token or chat_id == 'SEU_CHAT_ID':
        return False
    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                        data={'chat_id': chat_id, 'text': msg, 'parse_mode': 'HTML'}, timeout=15)
        return r.status_code == 200
    except:
        return False

# ============================================================
# MAIN
# ============================================================
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

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

    # Inicializar consciência temporal
    temporal = TemporalConsciousness()
    evolution = EvolutionaryMemory()

    log("=" * 70)
    log("⚡ SIAOL-PRO SUPREMO MAX v4 - AUTO-EVOLUTIVO")
    log(temporal.format_status())
    log("=" * 70)

    # Carregar configurações
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
    log(f"📱 Telegram: {'✅ Configurado' if token and chat_id != 'SEU_CHAT_ID' else '⚠️ Não configurado'}")

    # Carregar memória
    portfolio = Portfolio()
    checkpoint_file = os.path.join(MEMORY_DIR, "checkpoint.json")
    checkpoint = {}
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file) as f:
            checkpoint = json.load(f)

    # Obter parâmetros evoluídos
    params = evolution.get_best_parameters()

    # Status do sistema
    log(f"\n🧠 Evolução: {len(evolution.evolution_history)} ciclos")
    log(f"📊 Estratégias: {len(evolution.strategy_scores)}")
    log(f"💾 Parâmetros: {params}")

    # Executar backtest se houver dados suficientes
    if len(evolution.backtest_results) < 20:
        log("\n🔬 Executando backtest inicial...")
        for key, config in LOTTERIES.items():
            data = sync_lottery(key, config)
            if data and data["draws"]:
                evolution.run_backtest(key, data["draws"], n_games=30)

    premium_found = []

    for key, config in LOTTERIES.items():
        is_draw_today = temporal.is_draw_day(key)
        next_draw = temporal.get_next_draw(key)

        log(f"\n{'='*50}")
        log(f"{config['emoji']} {config['name']}")
        if is_draw_today:
            log(f"   🎯 HOJE É DIA DE SORTEIO!")
        else:
            log(f"   📅 Próximo: {next_draw['day']} ({next_draw['date']})")
        log(f"{'='*50}")

        data = sync_lottery(key, config)
        if not data or not data["draws"]:
            log("  ⚠️ Sem dados")
            continue

        latest = data["latest"]
        resultado = data["resultado"]
        is_new = latest > checkpoint.get(key, 0)

        log(f"  📊 Concerto: {latest} {'(NOVO!)' if is_new else '(já processado)'}")
        if is_new and resultado:
            log(f"  🎯 Resultado: {' '.join(f'{n:02d}' for n in resultado)}")

        # Frequências
        all_nums = [n for d in data["draws"] for n in d]
        freq = Counter(all_nums)
        weights = {n: float(freq.get(n, 0) + 1) for n in range(1, config["range"]+1)}

        # Previsão
        hot_numbers = [n for n, c in freq.most_common(15) if n <= config["range"]]
        cold_numbers = [n for n, c in freq.most_common()[-15:] if n <= config["range"]]
        recommended = hot_numbers[:config["pick"]]

        # ========== ANÁLISE FFT - CICLOS OCULTOS ==========
        log("  📡 FFT Analysis (Ciclos Ocultos)...")
        stat = StatAnalyzer(config)
        fft_result = stat.fft_analysis(data["draws"], top_n=10)
        if fft_result:
            log(f"     📊 Ciclos detectados: {fft_result.get('cycles_detected', 0)}")
            log(f"     📈 Top ciclícos: {fft_result.get('top_cyclics', [])[:5]}")
            # Ajustar pesos baseado em ciclos detectados
            for num in fft_result.get('top_cyclics', [])[:5]:
                if num in weights:
                    weights[num] *= 1.15  # Bônus de 15% para números cíclicos

        # ========== GERAR JOGOS COM SISTEMA EVOLUTIVO ==========
        log("  🔬 Quantum Engine (Auto-Evolutivo)...")
        qe = QuantumEngine(qubits=12, params=params)

        # Gerar jogos com consciência temporal
        quantum_games = qe.gen_evolutionary_games(config, weights, temporal, n_games=8)

        # ML
        log("  🤖 ML Predictor...")
        ml = MLPredictor(key)
        ml_games = ml.predict(data["draws"], 6)

        # Statistical
        log("  📊 Statistical...")
        stat = StatAnalyzer(config)
        stat_games = ml.predict(data["draws"], 4)

        # FFT-enhanced games (reprocess with cyclics)
        log("  📡 FFT-enhanced predictions...")
        fft_games = []
        if fft_result and fft_result.get('top_cyclics'):
            cyclics = fft_result['top_cyclics'][:config["pick"]]
            other_nums = [n for n in range(1, config["range"]+1) if n not in cyclics]
            for _ in range(4):
                game = sorted(cyclics + random.sample(other_nums, config["pick"] - len(cyclics)))
                if len(game) == config["pick"]:
                    fft_games.append(game)

        # Combinar
        all_games = []
        seen = set()
        sources = [
            ("Q-EVO", quantum_games),
            ("ML", ml_games),
            ("STAT", stat_games),
            ("FFT", fft_games)  # Nova fonte baseada em ciclos
        ]

        for src, games in sources:
            for g in games:
                k = tuple(sorted(g))
                if k not in seen and len(g) == config["pick"]:
                    seen.add(k)
                    all_games.append((src, g))

        log(f"  ✅ Total: {len(all_games)} jogos únicos")

        # Salvar no portfólio - SEMPRE adicionar (evita duplicatas automaticamente)
        for src, games in sources:
            if games:
                portfolio.add_games(key, games, src, latest)

        # Registrar resultados para evolução
        for src, game in all_games:
            if resultado:
                hits = len(set(game) & set(resultado))
                evolution.record_result(key, src, hits, game)

        # Verificar prêmios
        premiums = []
        for src, game in all_games:
            if resultado:
                hits = len(set(game) & set(resultado))
                if hits in config['premium_hits']:
                    premiums.append({'jogo': game, 'hits': hits, 'source': src})

        if premiums:
            log(f"  🎉 PREMIUMS: {len(premiums)}")

        # ========== ENVIAR RELATÓRIO COMPLETO ==========
        if token and chat_id != 'SEU_CHAT_ID':
            res_str = " - ".join(f"{n:02d}" for n in resultado) if resultado else "N/A"

            msg = f"""
╔═══════════════════════════════════════════════════════════╗
║  🧠 SIAOL-PRO SUPREMO MAX v4 - AUTO-EVOLUTIVO           ║
║  {config['emoji']} {config['name']:<48}║
╚═══════════════════════════════════════════════════════════╝

{temporal.format_status()}

📊 CONCURSO: {latest}
🎯 RESULTADO: {res_str}

{'🎉 PREMIOS ENCONTRADOS!' if premiums else '✅ SEM PREMIOS NESTE CICLO'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 NÚMEROS QUENTES (base temporal)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{' '.join(f'{n:02d}' for n in hot_numbers[:10])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❄️ NÚMEROS FRIOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{' '.join(f'{n:02d}' for n in cold_numbers[:10])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ RECOMENDADOS PARA PRÓXIMO JOGO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{' '.join(f'{n:02d}' for n in recommended)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎰 JOGOS GERADOS ({len(all_games)})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

            for i, (src, game) in enumerate(all_games[:10], 1):
                nums = " - ".join(f"{n:02d}" for n in game)
                msg += f"{i:02d}. {nums} [{src}]\n"

            msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 PRÓXIMO SORTEIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Dia: {next_draw['day']}
Data: {next_draw['date']}
Hora: {next_draw['time']}

{'⚠️ ATENÇÃO: HOJE É DIA DE SORTEIO!' if is_draw_today else ''}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 STATUS EVOLUTIVO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ciclos: {len(evolution.evolution_history)}
Estratégias: {len(evolution.strategy_scores)}
Melhor parâmetro: quantum={params['quantum_weight']:.2f}

⚡ SIAOL-PRO v4 AUTO-EVOLUTIVO
🔬 Quantum + ML + Temporal Consciousness
"""

            send_telegram(token, chat_id, msg)

        checkpoint[key] = latest
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f)

    # Evoluir parâmetros
    evolution.evolve_parameters()

    portfolio.save()

    elapsed = time.time() - start_time

    log(f"\n{'='*70}")
    log(f"✅ CICLO COMPLETO v4 - AUTO-EVOLUTIVO")
    log(f"   🕐 {temporal.weekday_name} - {temporal.date}")
    log(f"   🌡️  {temporal.get_season()}")
    log(f"   🧠 Ciclos de evolução: {len(evolution.evolution_history)}")
    log(f"   📊 Tempo: {elapsed:.1f}s")
    log(f"{'='*70}")

    return 0

if __name__ == "__main__":
    sys.exit(main())