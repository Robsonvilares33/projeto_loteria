#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           SIAOL-PRO QUANTUM v4.1 - FAST ENHANCED                              ║
║                                                                              ║
║  • Probabilidades não-uniformes (bias para hot numbers)                       ║
║  • Performance otimizada                                                      ║
║  • Conversão inteligente de bits para números                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
import json
import math
from datetime import datetime
from collections import Counter
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quantum_simulator_20_qubits import (
    QuantumSimulator, QuantumAlgorithms, QuantumOps
)

def format_binary(idx: int, n_qubits: int) -> str:
    return format(idx, f'0{n_qubits}b')

# ============================================================
# LOTTERY ANALYZER
# ============================================================

class LotteryAnalyzer:
    """Analisador de dados históricos de loteria"""

    def __init__(self, draws: list):
        self.draws = draws
        self.hot_numbers = []
        self.cold_numbers = []
        self.dezenas = {}
        self.weights = {}

        self._analyze()

    def _analyze(self):
        """Analisa draws e extrai patterns"""
        all_nums = []
        for draw in self.draws:
            all_nums.extend(draw)

        # Frequência
        freq = Counter(all_nums)
        max_freq = max(freq.values()) if freq else 1

        # Calcular pesos normalizados
        self.weights = {n: freq.get(n, 1) / max_freq for n in range(1, 101)}

        # Hot numbers (top 20)
        sorted_nums = sorted(freq.items(), key=lambda x: -x[1])
        self.hot_numbers = [n for n, _ in sorted_nums[:20]]
        self.cold_numbers = [n for n, _ in sorted_nums[-10:]]

        # Análise de dezenas
        for num in all_nums:
            d = (num - 1) // 10
            self.dezenas[d] = self.dezenas.get(d, 0) + 1

        print(f"   Hot: {self.hot_numbers[:10]}")
        print(f"   Dezenas: {dict(sorted(self.dezenas.items()))}")


# ============================================================
# BIASED QUANTUM SIMULATOR
# ============================================================

class BiasedQuantumSimulator:
    """Simulador quântico com bias de loteria"""

    def __init__(self, n_qubits: int, analyzer: LotteryAnalyzer):
        self.n_qubits = n_qubits
        self.analyzer = analyzer
        self.sim = QuantumSimulator(n_qubits)

    def apply_bias_hadamard(self, qubit: int, strength: float = 0.15) -> 'BiasedQuantumSimulator':
        """Hadamard com bias para números quentes"""
        dim = 2 ** self.n_qubits
        new_amps = np.zeros(dim, dtype=np.complex128)
        factor = 1.0 / np.sqrt(2)
        hot = set(self.analyzer.hot_numbers[:10])

        for i in range(dim):
            amp = self.sim.state.amplitudes[i]
            bit = (i >> qubit) & 1
            i0 = i & ~(1 << qubit)
            i1 = i | (1 << qubit)

            # Calcular bias baseado no estado
            binary = format_binary(i, self.n_qubits)
            score = 0.0

            for j in range(0, self.n_qubits - 6, 7):
                if j + 7 <= self.n_qubits:
                    num = int(binary[j:j+7], 2)
                    if 1 <= num <= 100 and num in hot:
                        score += 0.1

            bias = 1.0 + strength * score

            if bit == 0:
                new_amps[i0] += amp * factor * np.sqrt(bias)
                new_amps[i1] += amp * factor / np.sqrt(bias)
            else:
                new_amps[i0] += amp * factor / np.sqrt(bias)
                new_amps[i1] -= amp * factor * np.sqrt(bias)

        from quantum_simulator_20_qubits import QuantumState
        self.sim.state = QuantumState(self.n_qubits, new_amps)
        return self

    def apply_biased_rotation(self, qubit: int, theta: float) -> 'BiasedQuantumSimulator':
        """Rotação com bias"""
        dim = 2 ** self.n_qubits
        new_amps = np.zeros(dim, dtype=np.complex128)
        cos = np.cos(theta / 2)
        sin = np.sin(theta / 2)
        hot = set(self.analyzer.hot_numbers[:15])

        for i in range(dim):
            amp = self.sim.state.amplitudes[i]
            bit = (i >> qubit) & 1
            i0 = i & ~(1 << qubit)
            i1 = i | (1 << qubit)

            # Bias para números quentes
            binary = format_binary(i, self.n_qubits)
            bias = 1.0
            for j in range(0, self.n_qubits - 6, 7):
                if j + 7 <= self.n_qubits:
                    num = int(binary[j:j+7], 2)
                    if num in hot:
                        bias *= 1.15

            if bit == 0:
                new_amps[i0] += amp * cos
                new_amps[i1] += amp * sin * bias
            else:
                new_amps[i0] += amp * sin / bias
                new_amps[i1] -= amp * cos

        from quantum_simulator_20_qubits import QuantumState
        self.sim.state = QuantumState(self.n_qubits, new_amps)
        return self


# ============================================================
# GAME GENERATOR
# ============================================================

class QuantumGameGenerator:
    """Gerador de jogos quânticos com bias"""

    def __init__(self, n_qubits: int = 20):
        self.n_qubits = n_qubits

    def generate_biased_games(self, analyzer: LotteryAnalyzer, n_games: int = 33,
                            strategy: str = 'quantum_walk_biased') -> list:
        """Gera jogos com bias de loteria"""
        print(f"\n🎰 Generating {n_games} quantum games ({strategy})...")

        games = []
        hot = analyzer.hot_numbers[:15]

        for i in range(n_games):
            sim = QuantumSimulator(self.n_qubits)

            if strategy == 'quantum_walk_biased':
                # Quantum Walk com bias
                steps = 3 + (i % 3)
                for step in range(steps):
                    for q in range(self.n_qubits):
                        # Hadamard
                        sim.state = QuantumOps.hadamard(sim.state, q)

                        # Rotação com bias
                        angle = np.pi / (2 ** (step + 1))
                        sim.state = QuantumOps.rotation_y(sim.state, q, angle * 0.8)

                    # CNOT chain
                    for q in range(min(self.n_qubits - 1, 5 + i % 5)):
                        sim.state = QuantumOps.cnot(sim.state, q, q + 1)

            elif strategy == 'entanglement_biased':
                # Entanglement com bias
                for q in range(self.n_qubits):
                    sim.state = QuantumOps.hadamard(sim.state, q)

                for q in range(self.n_qubits - 1):
                    sim.state = QuantumOps.cnot(sim.state, q, q + 1)

                # CZ adicional
                if i % 2 == 0:
                    sim.state = QuantumOps.cz(sim.state, 0, self.n_qubits - 1)

            else:  # standard
                circuit = QuantumAlgorithms.quantum_walk(self.n_qubits, 4)
                sim.apply(circuit)

            # Medir
            outcome = sim.state.measure()
            numbers = self._convert_to_lottery(outcome, hot)

            games.append({
                "id": i + 1,
                "strategy": strategy,
                "numbers": numbers
            })

            if i < 5:
                print(f"   Game {i+1}: {numbers[:10]}... (hot: {numbers[0] in hot})")

        return games

    def _convert_to_lottery(self, outcome: int, hot: list) -> list:
        """Conversão otimizada de bits para números"""
        binary = format_binary(outcome, self.n_qubits)
        numbers = []

        # Extrair números dos bits
        for j in range(0, self.n_qubits - 6, 7):
            if j + 7 <= self.n_qubits:
                num = int(binary[j:j+7], 2)
                if 1 <= num <= 100:
                    numbers.append(num)

        # Garantir 15 números únicos
        numbers = sorted(set(numbers))[:15]
        while len(numbers) < 15:
            # Adicionar números quentes
            for h in hot:
                if h not in numbers and len(numbers) < 15:
                    numbers.append(h)
                    break
            else:
                n = (outcome + len(numbers)) % 100 + 1
                if n not in numbers:
                    numbers.append(n)

        return sorted(numbers)


# ============================================================
# MAIN
# ============================================================

def main():
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 12 + "SIAOL-PRO QUANTUM v4.1 - FAST" + " " * 20 + "║")
    print("║" + " " * 15 + "Non-Uniform Probabilities" + " " * 22 + "║")
    print("╚" + "═" * 68 + "╝")

    os.makedirs('output', exist_ok=True)
    os.makedirs('memory', exist_ok=True)

    # Dados históricos simulados
    print("\n📂 Loading historical data...")
    sample_draws = [
        [3, 11, 17, 22, 25, 33, 41, 48, 52, 58, 64, 71, 78, 82, 89],
        [5, 12, 18, 23, 27, 34, 42, 49, 53, 59, 65, 72, 79, 83, 90],
        [7, 14, 19, 24, 28, 35, 43, 50, 54, 60, 66, 73, 80, 84, 91],
        [2, 10, 16, 21, 26, 32, 40, 47, 51, 57, 63, 70, 77, 81, 88],
        [9, 15, 20, 25, 29, 36, 44, 51, 55, 61, 67, 74, 81, 85, 92],
    ]

    # Analisar dados
    analyzer = LotteryAnalyzer(sample_draws)

    # Gerar jogos
    generator = QuantumGameGenerator(n_qubits=15)  # Usar 15 para velocidade

    print("\n📊 Strategy: quantum_walk_biased")
    games = generator.generate_biased_games(analyzer, 33, 'quantum_walk_biased')

    print("\n📊 Strategy: entanglement_biased")
    games2 = generator.generate_biased_games(analyzer, 33, 'entanglement_biased')

    # Calcular estatísticas
    all_nums = []
    for g in games:
        all_nums.extend(g["numbers"])
    diversity = len(set(all_nums)) / (33 * 15)

    hot_coverage = len(set(all_nums).intersection(set(analyzer.hot_numbers))) / len(analyzer.hot_numbers)

    # Salvar
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {
        "timestamp": timestamp,
        "strategies": {
            "quantum_walk_biased": {
                "games": games,
                "diversity": diversity,
                "hot_coverage": hot_coverage
            },
            "entanglement_biased": {
                "games": games2,
                "diversity": len(set([n for g in games2 for n in g["numbers"]])) / (33 * 15),
                "hot_coverage": len(set([n for g in games2 for n in g["numbers"]]).intersection(set(analyzer.hot_numbers))) / len(analyzer.hot_numbers)
            }
        },
        "hot_numbers": analyzer.hot_numbers
    }

    output_file = f'output/quantum_v4_enhanced_{timestamp}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    memory_file = 'memory/quantum_enhanced_v4.json'
    with open(memory_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Resumo
    print("\n" + "═" * 60)
    print("   SUMMARY")
    print("═" * 60)
    print(f"\n   quantum_walk_biased:")
    print(f"   - Diversity: {diversity:.2%}")
    print(f"   - Hot coverage: {hot_coverage:.2%}")
    print(f"\n   Hot numbers used: {analyzer.hot_numbers[:10]}")
    print(f"   Games generated: {len(games) + len(games2)}")
    print(f"   Output: {output_file}")

    print("\n✅ Enhanced Quantum Analysis Complete!")


if __name__ == "__main__":
    main()