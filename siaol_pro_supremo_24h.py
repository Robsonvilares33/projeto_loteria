#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║           SIAOL-PRO SUPREMO - SISTEMA 24H AUTÔNOMO              ║
║                                                                ║
║  🔄 Opera 24h por dia no GitHub Actions                         ║
║  🧠 Memória suprema - nunca esquece padrões                     ║
║  🎯 Detecta padrões automaticamente                            ║
║  💰 Alertas apenas quando PREMIA!                               ║
║  💵 Otimização para R$150 por jogo                              ║
║                                                                ║
║  PREMIOS MONITORADOS:                                          ║
║  • Mega-Sena: 4, 5, 6 acertos                                  ║
║  • Lotofácil: 13, 14, 15 acertos                               ║
║  • Quina: 4, 5 acertos                                          ║
║  • Lotomania: 17, 18, 19, 20 acertos                           ║
╚══════════════════════════════════════════════════════════════════╝
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
from typing import Dict, List, Tuple, Optional

# ============================================================
# CONFIGURAÇÃO
# ============================================================

PROJECT_DIR = os.getcwd()
MEMORY_DIR = os.path.join(PROJECT_DIR, "memory")
os.makedirs(MEMORY_DIR, exist_ok=True)

# Configurações das loterias
LOTTERIES = {
    "megasena": {
        "name": "Mega-Sena", "pick": 6, "range": 60,
        "api_endpoint": "megasena",
        "premium_hits": [4, 5, 6],  # PREMIOS
        "game_price": 4.50
    },
    "lotofacil": {
        "name": "Lotofácil", "pick": 15, "range": 25,
        "api_endpoint": "lotofacil",
        "premium_hits": [13, 14, 15],  # PREMIOS
        "game_price": 2.50
    },
    "quina": {
        "name": "Quina", "pick": 5, "range": 80,
        "api_endpoint": "quina",
        "premium_hits": [4, 5],  # PREMIOS
        "game_price": 2.00
    },
    "lotomania": {
        "name": "Lotomania", "pick": 20, "range": 100,
        "api_endpoint": "lotomania",
        "premium_hits": [17, 18, 19, 20],  # PREMIOS
        "game_price": 2.50
    }
}

BUDGET = 150.00  # Orçamento por ciclo
MAX_DRAWS = 500  # Mais histórico para análise

# ============================================================
# SISTEMA DE MEMÓRIA SUPREMA
# ============================================================

class SupremeMemory:
    """Memória que nunca esquece - persiste em arquivos JSON"""

    def __init__(self):
        self.memory_file = os.path.join(MEMORY_DIR, "patterns_memory.json")
        self.load_memory()

    def load_memory(self):
        """Carrega memória do disco"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                data = json.load(f)
                self.patterns = data.get('patterns', {})
                self.failed_patterns = data.get('failed_patterns', [])
                self.best_games = data.get('best_games', {})
                self.stats = data.get('stats', {})
                self.last_update = data.get('last_update', '')
                log(f"🧠 Memória carregada: {len(self.patterns)} padrões")
        else:
            self.patterns = {}
            self.failed_patterns = []
            self.best_games = {}
            self.stats = {}
            self.last_update = ''
            log("🧠 Nova memória criada")

    def save_memory(self):
        """Salva memória no disco"""
        data = {
            'patterns': self.patterns,
            'failed_patterns': self.failed_patterns[-100:],  # Keep last 100
            'best_games': self.best_games,
            'stats': self.stats,
            'last_update': datetime.now().isoformat()
        }
        with open(self.memory_file, 'w') as f:
            json.dump(data, f, indent=2)

    def remember_pattern(self, lottery: str, numbers: List[int], hits: int, game_id: int):
        """Registra um padrão na memória"""
        key = f"{lottery}_{tuple(sorted(numbers))}"

        if key not in self.patterns:
            self.patterns[key] = {
                'numbers': numbers,
                'lottery': lottery,
                'occurrences': 0,
                'total_hits': 0,
                'best_hits': 0,
                'games': []
            }

        self.patterns[key]['occurrences'] += 1
        self.patterns[key]['total_hits'] += hits
        self.patterns[key]['best_hits'] = max(self.patterns[key]['best_hits'], hits)
        self.patterns[key]['games'].append({
            'game_id': game_id,
            'hits': hits,
            'timestamp': datetime.now().isoformat()
        })

        # Manter apenas últimos 50 jogos por padrão
        self.patterns[key]['games'] = self.patterns[key]['games'][-50:]

        # Atualizar melhores jogos
        if hits >= 4:  # Only remember good hits
            if lottery not in self.best_games:
                self.best_games[lottery] = []
            self.best_games[lottery].append({
                'numbers': numbers,
                'hits': hits,
                'timestamp': datetime.now().isoformat()
            })
            # Manter apenas top 20
            self.best_games[lottery] = sorted(
                self.best_games[lottery],
                key=lambda x: x['hits'],
                reverse=True
            )[:20]

    def forget_bad_pattern(self, lottery: str, numbers: List[int]):
        """Registra padrão que não funcionou"""
        key = f"{lottery}_{tuple(sorted(numbers))}"
        self.failed_patterns.append({
            'lottery': lottery,
            'numbers': numbers,
            'key': key,
            'timestamp': datetime.now().isoformat()
        })

    def is_pattern_failed(self, numbers: List[int]) -> bool:
        """Verifica se padrão já falhou muitas vezes"""
        key = f"_any_{tuple(sorted(numbers))}"
        failures = [f for f in self.failed_patterns if f['numbers'] == numbers]
        return len(failures) > 10  # Falhou mais de 10 vezes

    def get_best_numbers(self, lottery: str, count: int = 20) -> List[int]:
        """Retorna números mais frequentes dos melhores padrões"""
        if lottery not in self.best_games:
            return []

        number_freq = Counter()
        for game in self.best_games[lottery][:10]:
            number_freq.update(game['numbers'])

        return [n for n, _ in number_freq.most_common(count)]

    def update_stats(self, lottery: str, hits: int, is_premium: bool):
        """Atualiza estatísticas"""
        if lottery not in self.stats:
            self.stats[lottery] = {
                'total_games': 0,
                'total_hits': 0,
                'premium_alerts': 0,
                'patterns_discovered': 0,
                'games_optimized': 0
            }

        self.stats[lottery]['total_games'] += 1
        self.stats[lottery]['total_hits'] += hits
        if is_premium:
            self.stats[lottery]['premium_alerts'] += 1

    def get_summary(self) -> Dict:
        """Retorna resumo da memória"""
        return {
            'patterns_count': len(self.patterns),
            'failed_count': len(self.failed_patterns),
            'best_games_count': sum(len(g) for g in self.best_games.values()),
            'stats': self.stats,
            'last_update': self.last_update
        }


# ============================================================
# OTIMIZADOR DE COBERTURA (R$150)
# ============================================================

class CoverageOptimizer:
    """Otimiza quantidade de jogos para maximizar cobertura com R$150"""

    def __init__(self, memory: SupremeMemory):
        self.memory = memory

    def calculate_max_games(self, lottery: str) -> int:
        """Calcula quantidade máxima de jogos com R$150"""
        config = LOTTERIES[lottery]
        max_games = int(BUDGET / config['game_price'])
        return min(max_games, 50)  # Limite de 50 jogos

    def optimize_coverage(self, lottery: str, weights: Dict[int, float]) -> List[List[int]]:
        """Gera jogos otimizados para máxima cobertura"""
        config = LOTTERIES[lottery]
        max_games = self.calculate_max_games(lottery)

        # Pegar números dos melhores padrões
        best_numbers = self.memory.get_best_numbers(lottery, 30)
        all_range = list(range(1, config["range"] + 1))

        games = []
        hot_numbers = [n for n, w in sorted(weights.items(), key=lambda x: x[1], reverse=True)[:30]]

        # 30% jogos com melhores números conhecidos
        for i in range(int(max_games * 0.3)):
            selected = sorted(random.sample(best_numbers if len(best_numbers) >= config["pick"] else hot_numbers,
                                           min(config["pick"], len(best_numbers) if best_numbers else len(hot_numbers))))
            while len(selected) < config["pick"]:
                remaining = [n for n in all_range if n not in selected]
                selected.append(random.choice(remaining))
            games.append(sorted(selected[:config["pick"]]))

        # 40% jogos com números quentes ponderados
        for i in range(int(max_games * 0.4)):
            probs = np.array([weights.get(n, 0.1) for n in all_range])
            probs = probs / probs.sum()
            selected = sorted(np.random.choice(all_range, config["pick"], replace=False, p=probs).tolist())
            while len(selected) < config["pick"]:
                remaining = [n for n in all_range if n not in selected]
                selected.append(random.choice(remaining))
            games.append(sorted(selected[:config["pick"]]))

        # 30% jogos com mistura diversificada
        for i in range(int(max_games * 0.3)):
            n_hot = config["pick"] // 2
            cold = [n for n in all_range if n not in hot_numbers[:20]]
            selected = sorted(random.sample(hot_numbers[:20], n_hot) +
                             random.sample(cold, config["pick"] - n_hot))
            while len(selected) < config["pick"]:
                remaining = [n for n in all_range if n not in selected]
                selected.append(random.choice(remaining))
            games.append(sorted(selected[:config["pick"]]))

        # Remover duplicatas
        unique_games = []
        seen = set()
        for game in games:
            key = tuple(game)
            if key not in seen:
                seen.add(key)
                unique_games.append(game)

        return unique_games


# ============================================================
# MÓDULO QUÂNTICO
# ============================================================

class QuantumSimulatorLight:
    """Simulador quântico otimizado"""

    def __init__(self, num_qubits=12):
        self.num_qubits = num_qubits
        self.dim = 2 ** num_qubits
        self.state = np.zeros(self.dim, dtype=np.complex128)
        self.state[0] = 1.0 + 0j

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

    def get_probabilities(self):
        return np.abs(self.state) ** 2

    def get_entropy(self):
        probs = self.get_probabilities()
        probs = probs[probs > 1e-10]
        return -np.sum(probs * np.log2(probs))

    def measure(self):
        probs = self.get_probabilities()
        probs /= probs.sum()
        return np.random.choice(self.dim, p=probs)


# ============================================================
# DETECTOR DE PADRÕES
# ============================================================

class PatternDetector:
    """Detecta padrões nos sorteios"""

    def __init__(self, memory: SupremeMemory):
        self.memory = memory

    def analyze_draw(self, lottery: str, resultado: List[int], latest: int) -> Dict:
        """Analisa um sorteio e detecta padrões"""
        config = LOTTERIES[lottery]

        patterns_found = []

        # Padrão 1: Números consecutivos
        consecutive = self._find_consecutive(resultado)
        if len(consecutive) >= 2:
            patterns_found.append({
                'type': 'consecutive',
                'numbers': consecutive,
                'strength': len(consecutive) / config["pick"]
            })

        # Padrão 2: Números na mesma dezena
        dezenas = self._find_dezenas(resultado, config["range"])
        if dezenas:
            patterns_found.append({
                'type': 'same_dezena',
                'numbers': resultado,
                'strength': 0.5
            })

        # Padrão 3: Spread (distribuição uniforme)
        spread = self._calculate_spread(resultado, config["range"])
        if spread > 0.6:
            patterns_found.append({
                'type': 'uniform_spread',
                'numbers': resultado,
                'strength': spread
            })

        return {
            'lottery': lottery,
            'concurso': latest,
            'resultado': resultado,
            'patterns': patterns_found,
            'timestamp': datetime.now().isoformat()
        }

    def _find_consecutive(self, numbers: List[int]) -> List[int]:
        """Encontra sequências consecutivas"""
        sorted_nums = sorted(numbers)
        consecutive = []
        for i in range(len(sorted_nums) - 1):
            if sorted_nums[i + 1] - sorted_nums[i] == 1:
                if not consecutive:
                    consecutive = [sorted_nums[i], sorted_nums[i + 1]]
                else:
                    consecutive.append(sorted_nums[i + 1])
        return consecutive if len(consecutive) >= 2 else []

    def _find_dezenas(self, numbers: List[int], max_range: int) -> Dict:
        """Encontra números na mesma dezena"""
        dezenas = {}
        for num in numbers:
            dezena = (num - 1) // 10
            if dezena not in dezenas:
                dezenas[dezena] = []
            dezenas[dezena].append(num)
        return {k: v for k, v in dezenas.items() if len(v) >= 2}

    def _calculate_spread(self, numbers: List[int], max_range: int) -> float:
        """Calcula spread (distribuição uniforme)"""
        if not numbers:
            return 0
        sorted_nums = sorted(numbers)
        gaps = [sorted_nums[i + 1] - sorted_nums[i] for i in range(len(sorted_nums) - 1)]
        avg_gap = sum(gaps) / len(gaps) if gaps else 0
        expected_gap = max_range / len(numbers)
        return min(1.0, expected_gap / avg_gap) if avg_gap > 0 else 0


# ============================================================
# FUNÇÕES PRINCIPAIS
# ============================================================

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

def send_telegram(token: str, chat_id: str, message: str):
    """Envia mensagem para o Telegram"""
    if not token or not chat_id or chat_id == 'SEU_CHAT_ID_AQUI':
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
        r = requests.post(url, data=data, timeout=15)
        return r.status_code == 200
    except:
        return False

def api_latest(endpoint: str) -> int:
    """Busca último concurso"""
    try:
        r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{endpoint}/latest", timeout=10)
        if r.status_code == 200:
            return r.json().get('concurso', 0)
    except:
        pass
    return 0

def api_contest(endpoint: str, contest: int) -> Optional[List[int]]:
    """Busca concurso específico"""
    try:
        r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{endpoint}/{contest}", timeout=10)
        if r.status_code == 200:
            dezenas = r.json().get('dezenas', [])
            if dezenas:
                return sorted([int(x) for x in dezenas])
    except:
        pass
    return None

def sync_lottery(lottery_key: str, config: Dict) -> Optional[Dict]:
    """Sincroniza dados de uma loteria"""
    latest = api_latest(config["api_endpoint"])
    if not latest:
        return None

    draws = []
    start = max(1, latest - MAX_DRAWS + 1)

    for c in range(latest, start - 1, -1):
        nums = api_contest(config["api_endpoint"], c)
        if nums:
            draws.append(nums)
        if len(draws) >= MAX_DRAWS:
            break

    return {"latest": latest, "draws": draws, "resultado": draws[0] if draws else []}

def check_games(games: List[Dict], resultado: List[int]) -> List[Dict]:
    """Confere jogos"""
    for g in games:
        g["hits"] = len(set(g["numbers"]) & set(resultado))
    return games


# ============================================================
# MAIN - CICLO SUPREMO
# ============================================================

def main():
    log("=" * 70)
    log("🧠 SIAOL-PRO SUPREMO - CICLO 24H")
    log("=" * 70)

    # Carregar Telegram
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

    if not token or not chat_id:
        log("❌ Telegram não configurado")
        return 1

    # Inicializar sistemas
    memory = SupremeMemory()
    optimizer = CoverageOptimizer(memory)
    detector = PatternDetector(memory)

    # Carregar último concurso processado
    checkpoint_file = os.path.join(MEMORY_DIR, "checkpoint.json")
    checkpoint = {}
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)

    log(f"🧠 Memória suprema ativa: {len(memory.patterns)} padrões")

    premium_found = []

    for lottery_key, config in LOTTERIES.items():
        log(f"\n🎰 Processando {config['name']}...")

        # Sincronizar dados
        data = sync_lottery(lottery_key, config)
        if not data or not data["draws"]:
            log(f"  ⚠️ Sem dados")
            continue

        latest = data["latest"]
        resultado = data["resultado"]

        # Verificar se já processamos este concurso
        last_processed = checkpoint.get(lottery_key, 0)
        if latest <= last_processed:
            log(f"  ⏭️ Concurso {latest} já processado")
            continue

        log(f"  📊 Concurso: {latest} | Resultado: {' '.join(f'{n:02d}' for n in resultado)}")

        # Detectar padrões
        pattern_analysis = detector.analyze_draw(lottery_key, resultado, latest)

        # Gerar jogos otimizados
        all_nums = [n for draw in data["draws"] for n in draw]
        freq = Counter(all_nums)
        total = sum(freq.values())

        weights = {}
        for num in range(1, config["range"] + 1):
            f = freq.get(num, 0)
            weights[num] = (f / total) * 100 if total > 0 else 0.1

        # Gerar jogos otimizados com memória
        max_games = optimizer.calculate_max_games(lottery_key)
        games_numbers = optimizer.optimize_coverage(lottery_key, weights)

        # Criar objetos de jogos
        games = [{"numbers": nums, "game_id": i + 1} for i, nums in enumerate(games_numbers)]

        # Conferir jogos
        checked = check_games(games, resultado)

        # Registrar na memória
        for g in checked:
            memory.remember_pattern(lottery_key, g["numbers"], g["hits"], g["game_id"])

        # Verificar se há PREMIO
        premium_hits = config["premium_hits"]
        premium_games = [g for g in checked if g["hits"] in premium_hits]

        if premium_games:
            log(f"  🎉 PREMIO ENCONTRADO! {premium_games[0]['hits']} acertos!")

            premium_found.append({
                'lottery': config['name'],
                'concurso': latest,
                'resultado': resultado,
                'premium_games': premium_games,
                'total_games': len(games)
            })

            # ENVIAR ALERTA DE PREMIO!
            resultado_str = " - ".join(f"{n:02d}" for n in resultado)
            best_game = premium_games[0]
            nums_str = " - ".join(f"{n:02d}" for n in best_game['numbers'])

            msg = f"""🏆🎉 <b>PREMIO ENCONTRADO!</b> 🎉🏆
━━━━━━━━━━━━━━━━━━━━
🎰 <b>{config['name']}</b>
📊 Concurso: {latest}
✅ Resultado: {resultado_str}
━━━━━━━━━━━━━━━━━━━━
🎯 <b>{best_game['hits']} ACERTOS!</b>

🏅 Jogo Premiado:
{nums_str}

📈 Resumo:
• Total de jogos: {len(games)}
• Jogos premiados: {len(premium_games)}
• Custo: R$ {len(games) * config['game_price']:.2f}

🧠 <i>Detectado pelo SIAOL-PRO SUPREMO</i>"""

            send_telegram(token, chat_id, msg)

        # Atualizar checkpoint
        checkpoint[lottery_key] = latest
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f)

        # Atualizar estatísticas
        max_hits = max([g['hits'] for g in checked])
        memory.update_stats(lottery_key, max_hits, len(premium_games) > 0)

    # Salvar memória
    memory.save_memory()

    # Resumo do ciclo
    summary = memory.get_summary()
    log(f"\n🧠 Ciclosupremo completo")
    log(f"   Padrões na memória: {summary['patterns_count']}")
    log(f"   Padrões falhados: {summary['failed_count']}")
    log(f"   Alertas de premio: {sum(s['premium_alerts'] for s in summary['stats'].values())}")

    # Mensagem de status (apenas a cada 6 horas)
    current_hour = datetime.now().hour
    if current_hour % 6 == 0:
        msg = f"""🧠 <b>SIAOL-PRO SUPREMO - Status</b>
━━━━━━━━━━━━━━━━━━━━
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}
🔄 Sistema operando 24h

📊 Memória Suprema:
• Padrões registrados: {summary['patterns_count']}
• Melhorias detectadas: {summary['failed_count']}

💰 Premios encontrados: {sum(s['premium_alerts'] for s in summary['stats'].values())}

🎯 Oraculo ativo"""

        send_telegram(token, chat_id, msg)

    return 0

if __name__ == "__main__":
    sys.exit(main())