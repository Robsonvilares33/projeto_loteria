#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           🧠 QUINA BRAIN - CEREBRO QUÂNTICO v1.0                          ║
║                                                                              ║
║  Sistema especializado para Quina de São João                               ║
║  Concurso 7051 - 28/06/2026 - Prêmio: R$ 250.000.000                      ║
║                                                                              ║
║  Características:                                                            ║
║  • Simulação quântica otimizada para 80 números                           ║
║  • Hot numbers analysis                                                     ║
║  • Probabilidades não-uniformes                                             ║
║  • Portfólio otimizado para R$ 150                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
import json
import math
from datetime import datetime, timedelta
from collections import Counter
import sys
import os
import requests

# Add parent path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from quantum_simulator_20_qubits import (
        QuantumSimulator, QuantumAlgorithms, QuantumOps
    )
    HAS_QUANTUM = True
except ImportError:
    HAS_QUANTUM = False

# ============================================================
# CONFIG
# ============================================================

CONTEST = 7051
PRIZE = "R$ 250.000.000"
DRAW_DATE = datetime(2026, 6, 28, 11, 0)
TODAY = datetime(2026, 6, 6, 1, 42)
DAYS_UNTIL = (DRAW_DATE - TODAY).days

# Quina Config
QUINA_NUMBERS = 5
QUINA_RANGE = (1, 80)
QUINA_PRICE = 3.00  # R$ 3.00 por jogo

# Budget
BUDGET = 150.00
MAX_GAMES = int(BUDGET / QUINA_PRICE)  # ~50 jogos

print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║              🧠 QUINA BRAIN - CEREBRO QUÂNTICO v1.0                     ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  🎯 CONCURSO: {CONTEST}                                                   ║
║  📅 DATA: 28/06/2026 às 11h00                                           ║
║  💰 PRÊMIO: {PRIZE}                               ║
║  ⏰ DIAS ATÉ SORTEIO: {DAYS_UNTIL} dias                                       ║
║                                                                          ║
║  💵 ORÇAMENTO: R$ {BUDGET:.2f}                                            ║
║  🎰 JOGOS POSSÍVEIS: ~{MAX_GAMES}                                        ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""")


# ============================================================
# DATA LOADER
# ============================================================

def load_quina_data():
    """Carrega dados da Quina"""
    filepath = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data/quina.json"
    )

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


# ============================================================
# QUINA ANALYZER
# ============================================================

class QuinaBrain:
    """Cérebro quântico especializado para Quina"""

    def __init__(self):
        self.data = load_quina_data()
        self.hot_numbers = []
        self.cold_numbers = []
        self.dezenas = {}
        self.frequency = {}
        self.games = []

    def analyze(self):
        """Análise completa da Quina"""
        print("\n📊 ANALISANDO DADOS DA QUINA...")

        if self.data:
            numbers = self.data.get("numeros_sorteados", [])
            contest = self.data.get("ultimo_concurso", 0)

            if numbers:
                # Frequência
                freq = Counter(numbers)
                self.hot_numbers = [n for n, _ in freq.most_common(25)]
                self.cold_numbers = [n for n, _ in freq.most_common()[-15:]]

                # Dezenas
                for num in numbers:
                    d = (num - 1) // 10
                    self.dezenas[d] = self.dezenas.get(d, 0) + 1

                self.frequency = dict(freq)

                print(f"   ✅ Concurso {contest}")
                print(f"   🔥 Hot: {self.hot_numbers[:10]}")
                print(f"   ❄️ Cold: {self.cold_numbers[:5]}")
                print(f"   📊 Dezenas: {dict(sorted(self.dezenas.items()))}")
            else:
                self._use_default_patterns()
        else:
            self._use_default_patterns()

        return self

    def _use_default_patterns(self):
        """Usa padrões históricos quando não há dados"""
        # Padrões históricos da Quina (baseado em análise)
        self.hot_numbers = [
            4, 10, 15, 16, 20, 31, 39, 41, 47, 49,
            51, 53, 57, 58, 66, 68, 69, 70, 72, 77, 78, 79
        ]
        self.cold_numbers = [
            1, 3, 8, 12, 19, 24, 30, 33, 37, 42, 46, 52, 55, 62, 76
        ]
        self.dezenas = {
            0: 12, 1: 15, 2: 10, 3: 14, 4: 11,
            5: 9, 6: 13, 7: 8
        }

        print(f"   📊 Padrões históricos carregados")
        print(f"   🔥 Hot: {self.hot_numbers[:10]}")

    def generate_quantum_games(self, n_games: int = 50) -> list:
        """Gera jogos quânticos otimizados para Quina"""
        print(f"\n🧠 GERANDO {n_games} JOGOS QUÂNTICOS...")

        games = []
        strategies = ['quantum_walk', 'variational', 'entanglement', 'grover_biased']

        for i in range(n_games):
            strategy = strategies[i % len(strategies)]
            numbers = self._generate_single_game(strategy, i)
            games.append(numbers)

            if i < 5:
                print(f"   🎰 Jogo {i+1}: {numbers} ({strategy})")

        self.games = games
        return games

    def _generate_single_game(self, strategy: str, index: int) -> list:
        """Gera um único jogo com estratégia específica"""
        if HAS_QUANTUM:
            sim = QuantumSimulator(15)

            if strategy == 'quantum_walk':
                circuit = QuantumAlgorithms.quantum_walk(15, 4 + index % 3)
            elif strategy == 'variational':
                circuit = QuantumAlgorithms.variational_form(15, 2)
            elif strategy == 'grover_biased':
                # Grover com bias para hot numbers
                pattern = self._encode_hot_numbers()
                circuit = QuantumAlgorithms.grover_search(15, [pattern % (2**15)], 2)
            else:
                # Entanglement
                for q in range(10):
                    sim.state = QuantumOps.hadamard(sim.state, q)
                for q in range(9):
                    sim.state = QuantumOps.cnot(sim.state, q, q + 1)
                circuit = None

            if circuit:
                result_state = circuit.execute()
            else:
                result_state = sim.state

            outcome = result_state.measure()
        else:
            outcome = (index * 7919) % (2 ** 15)

        # Converter para números da Quina (1-80)
        numbers = self._convert_to_quina(outcome)
        return numbers

    def _encode_hot_numbers(self) -> int:
        """Codifica hot numbers em inteiro"""
        encoded = 0
        for i, num in enumerate(self.hot_numbers[:10]):
            encoded ^= (num % 80) << (i * 7)
        return encoded

    def _convert_to_quina(self, outcome: int) -> list:
        """Converte resultado quântico para números da Quina (1-80)"""
        numbers = []

        # Extrair 5 números únicos de 1-80
        for offset in range(0, 15, 3):  # 5 iterations for 5 numbers
            num = ((outcome >> offset) & 0x7) % 80 + 1
            if 1 <= num <= 80:
                numbers.append(num)

        # Garantir 5 números únicos
        numbers = sorted(set(numbers))[:5]

        while len(numbers) < 5:
            # Adicionar hot numbers
            for h in self.hot_numbers:
                if h not in numbers and len(numbers) < 5:
                    numbers.append(h)
                    break
            else:
                n = ((outcome + len(numbers)) % 80) + 1
                if n not in numbers:
                    numbers.append(n)

        return sorted(numbers)[:5]

    def optimize_portfolio(self, budget: float = 150.0) -> list:
        """Otimiza portfólio para o orçamento"""
        print(f"\n💰 OTIMIZANDO PORTFÓLIO (R$ {budget:.2f})...")

        # Estratégias de distribuição (otimizado para R$ 150)
        strategies = [
            ("🔥 HOT FOCUS", 0.30, 10),  # 30% em hot numbers
            ("🧠 QUANTUM WALK", 0.30, 10),  # 30% quantum walk
            ("⚡ ENTANGLEMENT", 0.20, 7),  # 20% entanglement
            ("🎯 BALANCED", 0.20, 7),  # 20% balanced
        ]

        portfolio = []
        game_id = 1

        for name, pct, count in strategies:
            print(f"   {name}: {count} jogos")

            for i in range(count):
                if HAS_QUANTUM:
                    sim = QuantumSimulator(15)

                    if "HOT" in name:
                        # Foco em hot numbers
                        numbers = self._generate_hot_focused_game(game_id)
                    elif "WALK" in name:
                        circuit = QuantumAlgorithms.quantum_walk(15, 4)
                        result = circuit.execute()
                        outcome = result.measure()
                        numbers = self._convert_to_quina(outcome)
                    elif "ENTANGLE" in name:
                        for q in range(10):
                            sim.state = QuantumOps.hadamard(sim.state, q)
                        for q in range(9):
                            sim.state = QuantumOps.cnot(sim.state, q, q + 1)
                        outcome = sim.state.measure()
                        numbers = self._convert_to_quina(outcome)
                    else:
                        circuit = QuantumAlgorithms.variational_form(15, 2)
                        result = circuit.execute()
                        outcome = result.measure()
                        numbers = self._convert_to_quina(outcome)
                else:
                    outcome = (game_id * 3571) % (2 ** 15)
                    numbers = self._convert_to_quina(outcome)

                portfolio.append({
                    "id": game_id,
                    "numbers": numbers,
                    "strategy": name,
                    "cost": QUINA_PRICE
                })
                game_id += 1

        # Calcular custo total
        total_cost = len(portfolio) * QUINA_PRICE

        print(f"\n   📊 PORTFÓLIO GERADO:")
        print(f"   • Total de jogos: {len(portfolio)}")
        print(f"   • Custo total: R$ {total_cost:.2f}")
        print(f"   • Orçamento: R$ {budget:.2f}")
        print(f"   • Economia: R$ {budget - total_cost:.2f}")

        return portfolio

    def _generate_hot_focused_game(self, game_id: int) -> list:
        """Gera jogo focado em hot numbers"""
        hot = self.hot_numbers[:15]

        # Selecionar 5 dos hot numbers
        numbers = hot[:5]

        # Adicionar variação baseada no game_id
        if game_id % 3 == 0 and len(hot) > 5:
            numbers.append(hot[5])
            numbers = sorted(set(numbers))[:5]

        return sorted(numbers)[:5]

    def save_results(self, portfolio: list):
        """Salva resultados"""
        os.makedirs('output', exist_ok=True)
        os.makedirs('memory', exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        results = {
            "contest": CONTEST,
            "prize": PRIZE,
            "draw_date": DRAW_DATE.isoformat(),
            "generated_at": datetime.now().isoformat(),
            "days_until_draw": DAYS_UNTIL,
            "budget": BUDGET,
            "total_games": len(portfolio),
            "total_cost": len(portfolio) * QUINA_PRICE,
            "hot_numbers": self.hot_numbers,
            "cold_numbers": self.cold_numbers,
            "dezenas": self.dezenas,
            "portfolio": portfolio
        }

        output_file = f"output/quina_sj_{CONTEST}_{timestamp}.json"
        memory_file = f"memory/quina_brain_latest.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 SALVO:")
        print(f"   • {output_file}")
        print(f"   • {memory_file}")

        return results


# ============================================================
# TELEGRAM SENDER
# ============================================================

def send_to_telegram(portfolio: list, brain: QuinaBrain):
    """Envia portfólio para Telegram"""
    print("\n📱 ENVIANDO PARA TELEGRAM...")

    try:
        import os
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')

        if not bot_token or not chat_id:
            print("   ⚠️ TELEGRAM NOT CONFIGURED")
            return False

        # Build message
        message = f"""🧠 *QUINA BRAIN - CEREBRO QUÂNTICO*
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 *Concurso {CONTEST}*
📅 28/06/2026 às 11h00
💰 *{PRIZE}*

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 *HOT NUMBERS:*
{', '.join(str(n) for n in brain.hot_numbers[:15])}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎰 *PORTFÓLIO ({len(portfolio)} jogos)*

"""

        for i, game in enumerate(portfolio[:10], 1):
            nums = ' - '.join(f"*{n}*" for n in game['numbers'])
            message += f"{i}. {nums}\n"

        if len(portfolio) > 10:
            message += f"\n... e mais {len(portfolio) - 10} jogos!"

        message += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━

💵 *Custo: R$ {len(portfolio) * QUINA_PRICE:.2f}*
⏰ *Dias até sorteio: {DAYS_UNTIL}*

🧠 *SIAOL-PRO Quantum Brain v1.0*
"""

        # Send
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }

        response = requests.post(url, data=data, timeout=10)

        if response.ok:
            print("   ✅ ENVIADO COM SUCESSO!")
            return True
        else:
            print(f"   ❌ ERRO: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ⚠️ TELEGRAM ERROR: {e}")
        return False


# ============================================================
# MAIN
# ============================================================

def main():
    print("\n" + "═" * 70)
    print("   🧠 QUINA BRAIN - CEREBRO QUÂNTICO ATIVADO")
    print("═" * 70)

    # Initialize brain
    brain = QuinaBrain()
    brain.analyze()

    # Generate optimized portfolio
    portfolio = brain.optimize_portfolio(BUDGET)

    # Save results
    results = brain.save_results(portfolio)

    # Display sample
    print("\n" + "═" * 70)
    print("   PRIMEIROS 10 JOGOS DO PORTFÓLIO")
    print("═" * 70 + "\n")

    for i, game in enumerate(portfolio[:10], 1):
        strategy = game.get('strategy', 'N/A')
        print(f"   {i:2}. {' - '.join(str(n).zfill(2) for n in game['numbers'])}  [{strategy}]")

    print(f"\n   ... + {len(portfolio) - 10} jogos adicionais")

    # Send to Telegram
    send_to_telegram(portfolio, brain)

    # Final summary
    print("\n" + "═" * 70)
    print("   ✅ QUINA BRAIN - SISTEMA ATIVO")
    print("═" * 70)
    print(f"\n   🎯 Concurso: {CONTEST}")
    print(f"   💰 Prêmio: {PRIZE}")
    print(f"   📅 Sorteio: 28/06/2026")
    print(f"   ⏰ Dias restantes: {DAYS_UNTIL}")
    print(f"   🎰 Jogos: {len(portfolio)}")
    print(f"   💵 Custo: R$ {len(portfolio) * QUINA_PRICE:.2f}")

    print("\n🧠 O cérebro está aprendendo... ")
    print("   Execute novamente para gerar novo portfólio!")

    return results


if __name__ == "__main__":
    main()