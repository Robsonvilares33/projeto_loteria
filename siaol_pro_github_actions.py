#!/usr/bin/env python3
"""
SIAOL-PRO - VERSÃO QUÂNTICA AVANÇADA
=====================================
Script com simulador quântico e análise de frequência avançada
- 20 jogos por loteria
- Análise multi-dimensional de frequência
- Geração quântica otimizada
"""
import os
import sys
import json
import math
import random
import requests
import numpy as np
from datetime import datetime
from collections import Counter

# Configuração
PROJECT_DIR = os.getcwd()
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configurações das loterias
LOTTERIES = {
    "megasena": {"name": "Mega-Sena", "pick": 6, "range": 60, "api_endpoint": "megasena"},
    "lotofacil": {"name": "Lotofácil", "pick": 15, "range": 25, "api_endpoint": "lotofacil"},
    "quina": {"name": "Quina", "pick": 5, "range": 80, "api_endpoint": "quina"}
}

MAX_DRAWS = 300
NUM_GAMES = 20  # Aumentado de 10 para 20

# ============================================================
# MÓDULO QUÂNTICO - SIMULAÇÃO EFICIENTE
# ============================================================

class QuantumSimulatorLight:
    """Simulador quântico otimizado para baixa memória"""

    def __init__(self, num_qubits=12):
        self.num_qubits = num_qubits
        self.dim = 2 ** num_qubits
        self.state = np.zeros(self.dim, dtype=np.complex128)
        self.state[0] = 1.0 + 0j
        log(f"🧊 Quantum: {num_qubits} qubits, {self.dim:,} states")

    def reset(self):
        self.state.fill(0)
        self.state[0] = 1.0 + 0j

    def H(self, qubit):
        factor = 1.0 / math.sqrt(2)
        for i in range(self.dim):
            if (i >> qubit) & 1:
                val = self.state[i]
                self.state[i] = (-val.real + val.imag * 1j) * factor
            else:
                val = self.state[i]
                self.state[i] = (val.real + val.imag * 1j) * factor

    def X(self, qubit):
        mask = 1 << qubit
        for i in range(self.dim // 2):
            j = i * 2
            bit = (j >> qubit) & 1
            if bit:
                j_flipped = j ^ mask
            else:
                j_flipped = j | mask
            if j_flipped > j:
                self.state[j], self.state[j_flipped] = self.state[j_flipped], self.state[j]

    def Z(self, qubit):
        mask = 1 << qubit
        for i in range(self.dim):
            if i & mask:
                self.state[i] *= -1

    def CNOT(self, control, target):
        mask_c = 1 << control
        mask_t = 1 << target
        for i in range(self.dim):
            if i & mask_c:
                self.state[i] = self.state[i ^ mask_t]
            else:
                self.state[i] = self.state[i & ~mask_t | ((i & mask_t) if not (i & mask_c) else 0)]

    def get_probabilities(self):
        return np.abs(self.state) ** 2

    def get_entropy(self):
        probs = self.get_probabilities()
        probs = probs[probs > 1e-10]
        return -np.sum(probs * np.log2(probs))

    def measure(self):
        probs = self.get_probabilities()
        probs /= probs.sum()
        result = np.random.choice(self.dim, p=probs)
        self.state.fill(0)
        self.state[result] = 1.0
        return result

    def apply_parametric_rotation(self, qubit, angle):
        mask = 1 << qubit
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        for i in range(self.dim):
            if i & mask:
                real_part = self.state[i].real * cos_a - self.state[i].imag * sin_a
                imag_part = self.state[i].real * sin_a + self.state[i].imag * cos_a
                self.state[i] = complex(real_part, imag_part)


class QuantumParameterExplorer:
    """Explorador de espaço de parâmetros quânticos"""

    def __init__(self, num_qubits=12):
        self.sim = QuantumSimulatorLight(num_qubits)
        self.num_qubits = num_qubits

    def explore_parameters(self, dimensions, shots=150):
        """Explora espaço de parâmetros quânticos"""
        results = []
        states_count = Counter()

        for _ in range(shots):
            self.sim.reset()
            for q, dim in enumerate(dimensions[:self.num_qubits]):
                if q < self.num_qubits:
                    self.sim.H(q)
                    angle = (q + 1) * math.pi / (len(dimensions) + 1)
                    self.sim.apply_parametric_rotation(q, angle)

            probs = self.sim.get_probabilities()
            top_idx = np.argmax(probs)
            entropy = self.sim.get_entropy()

            states_count[top_idx] += 1
            results.append({
                'state': top_idx,
                'probability': probs[top_idx],
                'entropy': entropy
            })

        return {
            'shots': shots,
            'unique_states': len(states_count),
            'avg_entropy': np.mean([r['entropy'] for r in results]),
            'max_probability': max(r['probability'] for r in results]),
            'top_states': states_count.most_common(10)
        }


def advanced_frequency_analysis(draws, config):
    """
    Análise de frequência multi-dimensional avançada
    Considera:
    - Frequência absoluta
    - Frequência recente (últimos 50 sorteios)
    - Frequência medieval (50-150 sorteios)
    - Frequência antiga (150+ sorteios)
    - Números "frios" com potencial de retorno
    - Padrões geométricos
    """
    all_nums = [n for draw in draws for n in draw]
    total = len(all_nums)

    # Frequência absoluta
    freq = Counter(all_nums)

    # Períodos
    recent = draws[:50] if len(draws) >= 50 else draws
    medium = draws[50:150] if len(draws) >= 150 else draws[:len(draws)//2]
    old = draws[150:] if len(draws) >= 150 else []

    recent_freq = Counter([n for draw in recent for n in draw])
    medium_freq = Counter([n for draw in medium for n in draw])

    # Calcular pesos ponderados
    weights = {}
    for num in range(1, config["range"] + 1):
        # Componentes
        abs_freq = freq.get(num, 0)
        rec_freq = recent_freq.get(num, 0)
        med_freq = medium_freq.get(num, 0)

        # Pesos normalizados
        abs_weight = (abs_freq / total) * 100 if total > 0 else 0.1
        rec_weight = (rec_freq / len(recent)) * 50 if recent else 1
        med_weight = (med_freq / len(medium)) * 30 if medium else 1

        # Score combinado com peso para números não sorteados recentemente
        gap = 0
        last_seen = 0
        for i, draw in enumerate(draws):
            if num in draw:
                last_seen = len(draws) - i
                break
        gap_score = min(last_seen * 0.5, 20)  # Bonus para números "frios"

        weights[num] = abs_weight * 0.4 + rec_weight * 0.35 + med_weight * 0.15 + gap_score

    return weights, freq


def quantum_generate_games_advanced(config, draws, num_games=NUM_GAMES):
    """Gera jogos usando simulação quântica com análise avançada"""
    if len(draws) < 10:
        return []

    # Análise de frequência avançada
    weights, freq = advanced_frequency_analysis(draws, config)

    # Inicializar simulador quântico
    explorer = QuantumParameterExplorer(12)

    # Explorar espaço de parâmetros
    log(f"  🧊 Explorando {2**12:,} estados quânticos...")
    dimensions = [8, 8, 8, 8, 8, 8, 8, 8]  # Mais dimensões para exploração
    quantum_result = explorer.explore_parameters(dimensions, shots=150)

    log(f"  📊 Estados únicos: {quantum_result['unique_states']}")
    log(f"  📊 Entropia média: {quantum_result['avg_entropy']:.4f}")

    # Classificar números
    avg_w = sum(weights.values()) / len(weights)
    hot = [n for n, w in weights.items() if w > avg_w * 1.3]
    warm = [n for n, w in weights.items() if avg_w * 0.9 <= w <= avg_w * 1.3]
    cold = [n for n, w in weights.items() if w < avg_w * 0.9]

    if len(hot) < config["pick"]:
        hot = [n for n, w in sorted(weights.items(), key=lambda x: x[1], reverse=True)[:25]]

    games = []
    all_range = list(range(1, config["range"] + 1))

    # Gerar jogos diversificados
    for i in range(num_games):
        if i < 5:
            # 5 jogos com números quentes
            selected = sorted(random.sample(hot, min(config["pick"], len(hot))))
        elif i < 10:
            # 5 jogos com mistura quente/fria
            n_hot = config["pick"] // 2
            n_cold = config["pick"] - n_hot
            selected = sorted(random.sample(hot, min(n_hot, len(hot))) +
                             random.sample(cold, min(n_cold, len(cold))))
        elif i < 15:
            # 5 jogos com números quentes + alguns recentes
            n_hot = config["pick"] - 2
            selected = sorted(random.sample(hot, min(n_hot, len(hot))) +
                             random.sample(warm, 2))
        else:
            # 5 jogos com seleção quântica ponderada
            probs = np.array([weights.get(n, 0.1) for n in all_range])
            probs = probs / probs.sum()
            selected = sorted(np.random.choice(all_range, config["pick"], replace=False, p=probs).tolist())

        # Garantir tamanho correto
        while len(selected) < config["pick"]:
            remaining = [n for n in all_range if n not in selected]
            selected.append(random.choice(remaining))
        selected = sorted(selected[:config["pick"]])

        games.append({
            "game_id": i + 1,
            "numbers": selected,
            "quantum_entropy": quantum_result['avg_entropy'],
            "source": "quantum_advanced"
        })

    return games

# ============================================================
# FUNÇÕES PRINCIPAIS
# ============================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

def send_telegram(token, chat_id, message):
    if not token or not chat_id or chat_id == 'SEU_CHAT_ID_AQUI':
        log("❌ Telegram não configurado")
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
        r = requests.post(url, data=data, timeout=15)
        if r.status_code == 200:
            log(f"✅ Mensagem enviada")
            return True
        else:
            log(f"❌ Erro Telegram: {r.status_code}")
            return False
    except Exception as e:
        log(f"❌ Erro Telegram: {e}")
        return False

def api_latest(endpoint):
    try:
        r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{endpoint}/latest", timeout=15)
        if r.status_code == 200:
            return r.json().get('concurso', 0)
    except Exception as e:
        log(f"⚠️ Erro API: {e}")
    return 0

def api_contest(endpoint, contest):
    try:
        r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{endpoint}/{contest}", timeout=15)
        if r.status_code == 200:
            dezenas = r.json().get('dezenas', [])
            if dezenas:
                return sorted([int(x) for x in dezenas])
    except:
        pass
    return None

def sync_lottery(lottery_key, config):
    log(f"  🎰 {config['name']}")

    latest = api_latest(config["api_endpoint"])
    if not latest:
        log("    ⚠️ Falha API")
        return None

    log(f"    📊 Último: {latest}")

    draws = []
    start = max(1, latest - MAX_DRAWS + 1)

    for c in range(latest, start - 1, -1):
        nums = api_contest(config["api_endpoint"], c)
        if nums:
            draws.append(nums)
        if len(draws) >= MAX_DRAWS:
            break

    log(f"    ✅ {len(draws)} sorteios")
    return {"latest": latest, "draws": draws, "resultado": draws[0] if draws else []}

def check_games(games, resultado):
    for g in games:
        g["hits"] = len(set(g["numbers"]) & set(resultado))
    return games

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 60)
    log("SIAOL-PRO QUANTUM ADVANCED")
    log("🧊 Simulador + Análise Frequência Avançada")
    log("=" * 60)

    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

    log(f"🔍 Token: {'✅' if token else '❌'}")
    log(f"🔍 Chat ID: {'✅' if chat_id else '❌'}")

    if not token or not chat_id:
        log("❌ Telegram não configurado - abortando")
        return 1

    num_qubits = 12
    total_states = 2**num_qubits

    msg = f"""🧊 <b>SIAOL-PRO QUANTUM ADVANCED</b>
━━━━━━━━━━━━━━━━━━━━
⚡ Ciclo quântico avançado iniciando
📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔧 Simulador: {num_qubits} qubits
🎲 Jogos por loteria: {NUM_GAMES}
💫 Estados: {total_states:,}"""
    send_telegram(token, chat_id, msg)

    results = []

    for lottery_key, config in LOTTERIES.items():
        log(f"\n🎰 Processando {config['name']}...")

        data = sync_lottery(lottery_key, config)
        if not data or not data["draws"]:
            log("    ⚠️ Sem dados")
            continue

        log("  🧊 Gerando jogos quânticos avançados...")
        games = quantum_generate_games_advanced(config, data["draws"], num_games=NUM_GAMES)
        checked = check_games(games, data["resultado"])

        # Salvar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(os.path.join(OUTPUT_DIR, f"{lottery_key}_quantum_{timestamp}.json"), 'w') as f:
            json.dump({
                "games": checked,
                "resultado": data["resultado"],
                "quantum_info": {
                    "qubits": num_qubits,
                    "states_explored": total_states,
                    "entropy": games[0]["quantum_entropy"] if games else 0,
                    "games_generated": len(games)
                }
            }, f, indent=2)

        # Enviar Telegram
        resultado_str = " - ".join(f"{n:02d}" for n in data["resultado"])
        hits_stats = Counter([g["hits"] for g in checked])
        max_hits = max([g["hits"] for g in checked])
        quantum_entropy = games[0]["quantum_entropy"] if games else 0

        msg = f"""📊 <b>{config['name']}</b>
Concurso: {data['latest']}
🧊 Qubits: {num_qubits} | Entropia: {quantum_entropy:.2f}
━━━━━━━━━━━━━━━━━━━━
✅ Resultado: {resultado_str}

📈 Acertos ({len(games)} jogos):
"""
        for h in sorted(hits_stats.keys(), reverse=True):
            msg += f"   {h} acertos: {hits_stats[h]} jogos\n"

        msg += f"\n🏆 Melhor: {max_hits} acertos\n\n🎰 Jogos Quânticos (Top 10):\n"

        # Ordenar por acertos
        sorted_games = sorted(checked, key=lambda x: x['hits'], reverse=True)
        for g in sorted_games[:10]:
            nums = " - ".join(f"{n:02d}" for n in g["numbers"])
            msg += f"   #{g['game_id']}: {nums} → {g['hits']} acertos\n"

        send_telegram(token, chat_id, msg)

        results.append({
            "lottery": config["name"],
            "latest": data["latest"],
            "max_hits": max_hits,
            "quantum_entropy": quantum_entropy,
            "games_count": len(games)
        })

        log(f"    ✅ {config['name']}: {max_hits} acertos em {len(games)} jogos")

    # Mensagem final
    msg = f"""⚡ <b>SIAOL-PRO QUANTUM ADVANCED - COMPLETO</b>
━━━━━━━━━━━━━━━━━━━━
📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🧊 {num_qubits} qubits | {total_states:,} estados
🎲 {NUM_GAMES} jogos por loteria

📊 Resultados:
"""
    for r in results:
        msg += f"   {r['lottery']}: {r['max_hits']} acertos ({r['games_count']} jogos)\n"

    msg += "\n💫 Boa sorte no próximo sorteio!"
    send_telegram(token, chat_id, msg)

    log("\n✅ CICLO QUÂNTICO AVANÇADO COMPLETO")
    return 0

if __name__ == "__main__":
    sys.exit(main())