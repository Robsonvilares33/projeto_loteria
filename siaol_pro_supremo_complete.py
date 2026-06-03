#!/usr/bin/env python3
"""
SIAOL-PRO SUPREMO MAX - ULTIMATE EDITION v3
Sistema COMPLETO com relatórios detalhados para Telegram
- Portfólio persistente de jogos
- Previsões para próximos concursos
- Histórico completo
- Notificações automáticas
"""

import os, sys, json, math, random, requests, time
import numpy as np
from datetime import datetime
from collections import Counter
from typing import Dict, List

PROJECT_DIR = os.getcwd()
MEMORY_DIR = os.path.join(PROJECT_DIR, "memory")
os.makedirs(MEMORY_DIR, exist_ok=True)

LOTTERIES = {
    "megasena": {"name": "Mega-Sena", "pick": 6, "range": 60, "premium_hits": [4,5,6], "emoji": "🎰"},
    "lotofacil": {"name": "Lotofácil", "pick": 15, "range": 25, "premium_hits": [13,14,15], "emoji": "🎯"},
    "quina": {"name": "Quina", "pick": 5, "range": 80, "premium_hits": [4,5], "emoji": "🎲"},
    "lotomania": {"name": "Lotomania", "pick": 20, "range": 100, "premium_hits": [17,18,19,20], "emoji": "🎴"}
}
MAX_DRAWS = 100

# ============================================================
# PORTFÓLIO PERSISTENTE
# ============================================================
class Portfolio:
    """Sistema de portfólio persistente de jogos"""

    def __init__(self):
        self.file = os.path.join(MEMORY_DIR, "portfolio.json")
        self.load()

    def load(self):
        if os.path.exists(self.file):
            with open(self.file) as f:
                data = json.load(f)
                self.games = data.get('games', {})
                self.last_update = data.get('last_update', '')
                self.concursos = data.get('concursos', {})
        else:
            self.games = {}
            self.last_update = ''
            self.concursos = {}

    def save(self):
        with open(self.file, 'w') as f:
            json.dump({
                'games': self.games,
                'last_update': datetime.now().isoformat(),
                'concursos': self.concursos
            }, f, indent=2)

    def add_games(self, lottery, games, source, concurso=None):
        """Adiciona jogos ao portfólio"""
        if lottery not in self.games:
            self.games[lottery] = []

        for game in games:
            key = f"{lottery}_{tuple(sorted(game))}"
            exists = any(tuple(sorted(g['numbers'])) == tuple(sorted(game)) for g in self.games[lottery])

            if not exists:
                self.games[lottery].append({
                    'numbers': sorted(game),
                    'source': source,
                    'created_at': datetime.now().isoformat(),
                    'concurso': concurso,
                    'last_checked': concurso,
                    'hits_history': []
                })

        if concurso:
            self.concursos[lottery] = concurso

        self.last_update = datetime.now().isoformat()
        self.save()

    def get_all_games(self, lottery):
        """Retorna todos os jogos de uma loteria"""
        if lottery not in self.games:
            return []
        return self.games[lottery]

    def get_games_as_text(self, lottery, limit=20):
        """Retorna jogos formatados para Telegram"""
        games = self.get_all_games(lottery)
        if not games:
            return "Nenhum jogo no portfólio"

        lines = []
        for i, g in enumerate(games[:limit], 1):
            nums = " - ".join(f"{n:02d}" for n in g['numbers'])
            lines.append(f"{i:02d}. {nums}")

        return "\n".join(lines)

    def update_hits(self, lottery, concurso, resultado):
        """Atualiza histórico de acertos"""
        if lottery not in self.games:
            return

        for game in self.games[lottery]:
            hits = len(set(game['numbers']) & set(resultado))
            if hits > 0:
                game['hits_history'].append({
                    'concurso': concurso,
                    'hits': hits,
                    'date': datetime.now().isoformat()
                })
            game['last_checked'] = concurso

        self.save()

    def get_best_games(self, lottery, min_hits=4, limit=10):
        """Retorna melhores jogos por acertos"""
        games = self.get_all_games(lottery)
        scored = []
        for g in games:
            total_hits = sum(h['hits'] for h in g.get('hits_history', []))
            if total_hits >= min_hits:
                scored.append((total_hits, g))

        scored.sort(reverse=True)
        return [g for _, g in scored[:limit]]

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

    def get_probs(self):
        return np.abs(self.state)**2

# ============================================================
# QUANTUM ENGINE
# ============================================================
class QuantumEngine:
    def __init__(self, qubits=12):
        self.sim = QuantumSimFast(qubits)
        self.qubits = qubits

    def gen_weighted_games(self, config, weights, n_games=8):
        games = []
        all_range = list(range(1, config["range"]+1))

        for _ in range(n_games):
            self.sim.state.fill(0)
            self.sim.state[0] = 1+0j

            max_w = max(list(weights.values())) if weights else 1
            if max_w == 0:
                max_w = 1

            for q in range(min(self.sim.n, 10)):
                if random.random() < 0.7:
                    self.sim.H(q)
                if q < len(all_range):
                    w = weights.get(all_range[q], 1)
                    theta = (w / max_w) * math.pi * 0.5
                    if theta > 0.1:
                        self.sim.RY(q, theta)

            probs_q = self.sim.get_probs()
            selected = self._select(all_range, probs_q, config["pick"])
            if selected:
                games.append(sorted(selected))

        return games

    def gen_quantum_annealing(self, config, weights, n_games=6):
        games = []
        all_range = list(range(1, config["range"]+1))

        for _ in range(n_games):
            self.sim.state.fill(0)
            self.sim.state[0] = 1+0j

            for _ in range(10):
                for q in range(min(self.sim.n, 6)):
                    if random.random() < 0.2:
                        self.sim.H(q)

            probs_q = self.sim.get_probs()
            selected = self._select(all_range, probs_q, config["pick"])
            if selected:
                games.append(sorted(selected))

        return games

    def gen_hybrid(self, config, weights, n_games=4):
        games = []
        all_range = list(range(1, config["range"]+1))

        combined = np.zeros(self.sim.dim)
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

            combined += self.sim.get_probs()

        combined /= 3
        for _ in range(n_games):
            selected = self._select(all_range, combined, config["pick"])
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
# TELEGRAM - SISTEMA COMPLETO DE NOTIFICAÇÕES
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

def format_games_list(games, source_name):
    """Formata lista de jogos para Telegram"""
    lines = [f"📋 <b>JOGOS GERADOS - {source_name}</b>"]
    lines.append("")
    for i, g in enumerate(games, 1):
        nums = " - ".join(f"{n:02d}" for n in g)
        lines.append(f"{i:02d}. {nums}")
    return "\n".join(lines)

def send_complete_report(token, chat_id, lottery, config, games_data, resultado, concurso, is_new_draw=True):
    """Envia relatório COMPLETO para Telegram"""

    # Cabeçalho
    msg = f"""
╔══════════════════════════════════════════╗
║  🧠 SIAOL-PRO SUPREMO MAX - RELATÓRIO   ║
║  {config['emoji']} {config['name']:<32}║
╚══════════════════════════════════════════╝

{'='*42}
{'📅 Data: ' + datetime.now().strftime('%d/%m/%Y %H:%M')}
{'📊 Concurso: ' + str(concurso)}
{'='*42}
"""

    # Resultado oficial
    if resultado:
        res_str = " - ".join(f"{n:02d}" for n in resultado)
        msg += f"""
🔴 <b>RESULTADO OFICIAL</b>
   {res_str}
"""

    # Estatísticas do sorteio
    if games_data.get('stats'):
        stats = games_data['stats']
        msg += f"""
📈 <b>ESTATÍSTICAS DO CICLO</b>
   ⭐ Jogos gerados: {stats.get('games_generated', 0)}
   🎯 Total verificados: {stats.get('games_checked', 0)}
   🏆 Prêmios encontrados: {stats.get('premiums_found', 0)}
"""

    # Jogos criados
    if games_data.get('games'):
        msg += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎰 <b>JOGOS CRIADOS PARA JOGAR</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for src, games in games_data['games']:
            src_emoji = {"Q-WEIGHT": "⚛️", "Q-ANN": "🔬", "Q-HYB": "🌐", "ML": "🤖", "STAT": "📊"}.get(src, "📝")
            msg += f"\n{src_emoji} <b>{src}</b> ({len(games)} jogos)\n"
            for i, g in enumerate(games[:5], 1):  # Limitar a 5 por source
                nums = " - ".join(f"{n:02d}" for n in g)
                msg += f"   {i:02d}. {nums}\n"

    # Previsão para próximo concurso
    if games_data.get('prediction'):
        pred = games_data['prediction']
        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔮 <b>PREVISÃO PARA PRÓXIMO CONCURSO</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Hot Numbers: {' '.join(f"{n:02d}" for n in pred['hot'])}
Cold Numbers: {' '.join(f"{n:02d}" for n in pred['cold'])}
Recomendados: {' '.join(f"{n:02d}" for n in pred['recommended'])}
"""

    # Notificação de prêmio
    if games_data.get('premiums'):
        msg += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆🎉 <b>PREMIOS ENCONTRADOS!</b> 🎉🏆
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for p in games_data['premiums']:
            nums = " - ".join(f"{n:02d}" for n in p['jogo'])
            msg += f"""
✨ <b>{p['hits']} ACERTOS!</b>
   Jogo: {nums}
   Método: {p['source']}
"""

    msg += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ SIAOL-PRO SUPREMO MAX v3
🔬 Quantum + ML + Statistics
"""

    return send_telegram(token, chat_id, msg)

def send_prediction_summary(token, chat_id, lottery, config, prediction_data):
    """Envia resumo de previsão diária"""
    pred = prediction_data

    hot = " - ".join(f"{n:02d}" for n in pred.get('hot_numbers', [])[:10])
    cold = " - ".join(f"{n:02d}" for n in pred.get('cold_numbers', [])[:10])
    rec = " - ".join(f"{n:02d}" for n in pred.get('recommended', [])[:10])

    msg = f"""
╔══════════════════════════════════════════╗
║  🔮 PREVISÃO DIÁRIA - {config['name']:<20}║
║  {datetime.now().strftime('%d/%m/%Y %H:%M')}                       ║
╚══════════════════════════════════════════╝

🔥 <b>NÚMEROS QUENTES</b> (maior frequência)
   {hot}

❄️ <b>NÚMEROS FRIOS</b> (menor frequência)
   {cold}

⭐ <b>RECOMENDADOS PARA JOGAR</b>
   {rec}

💡 <b>STRATÉGIA:</b>
   • Combine 2-3 números quentes
   • Adicione 1-2 números frios
   • Complete com números neutros

🤖 SIAOL-PRO SUPREMO MAX v3
"""

    return send_telegram(token, chat_id, msg)

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
    log("=" * 70)
    log("⚡ SIAOL-PRO SUPREMO MAX v3 - RELATÓRIO COMPLETO")
    log("🔬 Quantum + ML + Statistics + PORTFÓLIO")
    log("=" * 70)

    # Carregar configurações
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

    log(f"📱 Telegram: {'✅ Configurado' if token and chat_id != 'SEU_CHAT_ID' else '❌ Não configurado'}")

    # Carregar memória e portfólio
    memory = SupremeMemory()
    portfolio = Portfolio()

    checkpoint_file = os.path.join(MEMORY_DIR, "checkpoint.json")
    checkpoint = {}
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file) as f:
            checkpoint = json.load(f)

    log(f"🧠 Memória: {len(memory.patterns)} padrões")
    log(f"📁 Portfólio: {sum(len(g) for g in portfolio.games.values())} jogos")

    premium_found = []
    all_lottery_games = {}

    for key, config in LOTTERIES.items():
        log(f"\n{'='*50}")
        log(f"{config['emoji']} {config['name']}")
        log(f"{'='*50}")

        data = sync_lottery(key, config)
        if not data or not data["draws"]:
            log("  ⚠️ Sem dados")
            continue

        latest = data["latest"]
        resultado = data["resultado"]

        # Verificar se é novo concurso
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

        # ========== GERAR JOGOS ==========
        log("  🔬 Quantum Engine...")
        qe = QuantumEngine(qubits=12)

        qw = qe.gen_weighted_games(config, weights, 8)
        qa = qe.gen_quantum_annealing(config, weights, 6)
        qh = qe.gen_hybrid(config, weights, 4)
        log(f"    → Q-WEIGHT: {len(qw)}, Q-ANN: {len(qa)}, Q-HYB: {len(qh)}")

        log("  🤖 ML Predictor...")
        ml = MLPredictor(key)
        ml_games = ml.predict(data["draws"], 8)
        log(f"    → ML: {len(ml_games)}")

        log("  📊 Statistical...")
        stat = StatAnalyzer(config)
        stat_games = ml.predict(data["draws"], 4)
        log(f"    → STAT: {len(stat_games)}")

        # Combinar jogos únicos
        all_games = []
        seen = set()
        sources = [
            ("Q-WEIGHT", qw),
            ("Q-ANN", qa),
            ("Q-HYB", qh),
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

        # Salvar no portfólio
        if is_new:
            for src, games in sources:
                portfolio.add_games(key, games, src, latest)

        # Verificar prêmios
        games_generated = len(all_games)
        games_checked = 0
        premiums_found = []

        for src, game in all_games:
            if resultado:
                games_checked += 1
                hits = len(set(game) & set(resultado))
                memory.remember(key, game, hits, 0)

                if hits in config['premium_hits']:
                    premiums_found.append({'jogo': game, 'hits': hits, 'source': src})

        # Atualizar portfólio com acertos
        if resultado and is_new:
            portfolio.update_hits(key, latest, resultado)

        # Guardar dados para relatório
        all_lottery_games[key] = {
            'config': config,
            'games': sources,
            'resultado': resultado,
            'concurso': latest,
            'is_new': is_new,
            'stats': {
                'games_generated': games_generated,
                'games_checked': games_checked,
                'premiums_found': len(premiums_found)
            },
            'premiums': premiums_found,
            'prediction': {
                'hot': hot_numbers[:10],
                'cold': cold_numbers[:10],
                'recommended': recommended
            }
        }

        # ENVIAR RELATÓRIO COMPLETO PARA TELEGRAM
        if token and chat_id != 'SEU_CHAT_ID' and resultado:
            send_complete_report(
                token, chat_id, key, config,
                all_lottery_games[key], resultado, latest, is_new
            )
            # Também enviar previsão diária
            send_prediction_summary(
                token, chat_id, key, config,
                all_lottery_games[key]['prediction']
            )

        # Atualizar checkpoint
        checkpoint[key] = latest
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f)

    memory.save()

    summary = memory.get_summary()
    elapsed = time.time() - start_time

    # Salvar relatório completo
    report_file = os.path.join(MEMORY_DIR, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'elapsed': elapsed,
            'lotteries': all_lottery_games,
            'memory_summary': summary,
            'portfolio_count': sum(len(g) for g in portfolio.games.values())
        }, f, indent=2, default=str)

    log(f"\n{'='*70}")
    log(f"🧠 CICLO COMPLETO v3")
    log(f"   Padrões: {summary['patterns_count']}")
    log(f"   Prêmios: {summary['premium_count']}")
    log(f"   Portfólio: {sum(len(g) for g in portfolio.games.values())} jogos")
    log(f"   Tempo: {elapsed:.1f}s")
    log(f"   Relatório: {report_file}")
    log(f"{'='*70}")

    # Salvar portfólio
    portfolio.save()

    return 0

if __name__ == "__main__":
    sys.exit(main())
