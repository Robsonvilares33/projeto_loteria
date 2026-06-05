#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           SIAOL-PRO QUANTUM v4.2 - OPTIMIZED                                  ║
║                                                                              ║
║  • Probabilidades não-uniformes (bias para hot numbers)                       ║
║  • Performance otimizada para execução rápida                                ║
║  • 33 jogos com estratégias diversificadas                                    ║
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


def analyze_lottery(draws):
    """Analisa dados históricos"""
    all_nums = []
    for draw in draws:
        all_nums.extend(draw)

    freq = Counter(all_nums)
    max_freq = max(freq.values()) if freq else 1

    hot = [n for n, _ in sorted(freq.items(), key=lambda x: -x[1])[:20]]

    dezenas = {}
    for num in all_nums:
        d = (num - 1) // 10
        dezenas[d] = dezenas.get(d, 0) + 1

    return {"hot": hot, "dezenas": dezenas}


def generate_games(n_qubits, hot, n_games=33, strategy_idx=0):
    """Gera jogos quânticos com bias"""
    games = []
    strategies = [
        ('quantum_walk_biased', 3),
        ('entanglement_biased', 4),
        ('variational_biased', 3)
    ]

    strat_name, default_steps = strategies[strategy_idx % 3]

    for i in range(n_games):
        sim = QuantumSimulator(n_qubits)

        if strategy_idx % 3 == 0:  # Walk
            steps = default_steps + (i % 3)
            for s in range(steps):
                for q in range(n_qubits):
                    sim.state = QuantumOps.hadamard(sim.state, q)
                    sim.state = QuantumOps.rotation_y(sim.state, q, np.pi / (2 ** (s + 2)))
                for q in range(min(n_qubits - 1, 3 + i % 4)):
                    sim.state = QuantumOps.cnot(sim.state, q, q + 1)

        elif strategy_idx % 3 == 1:  # Entanglement
            for q in range(n_qubits):
                sim.state = QuantumOps.hadamard(sim.state, q)
            for q in range(n_qubits - 1):
                sim.state = QuantumOps.cnot(sim.state, q, q + 1)
            if i % 2 == 0:
                sim.state = QuantumOps.cz(sim.state, 0, n_qubits - 1)

        else:  # Variational
            circuit = QuantumAlgorithms.variational_form(n_qubits, 2)
            sim.apply(circuit)

        outcome = sim.state.measure()
        binary = format_binary(outcome, n_qubits)

        numbers = []
        for j in range(0, n_qubits - 6, 7):
            if j + 7 <= n_qubits:
                num = int(binary[j:j+7], 2)
                if 1 <= num <= 100:
                    numbers.append(num)

        numbers = sorted(set(numbers))[:15]
        while len(numbers) < 15:
            for h in hot:
                if h not in numbers and len(numbers) < 15:
                    numbers.append(h)
                    break
            else:
                n = (outcome + len(numbers)) % 100 + 1
                if n not in numbers:
                    numbers.append(n)
        numbers = sorted(numbers)

        games.append({"id": i + 1, "strategy": strat_name, "numbers": numbers})

    return games


def main():
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║        SIAOL-PRO QUANTUM v4.2 - OPTIMIZED                 ║")
    print("║        Non-Uniform Probabilities + Hot Numbers            ║")
    print("╚════════════════════════════════════════════════════════════╝")

    os.makedirs('output', exist_ok=True)
    os.makedirs('memory', exist_ok=True)

    # Dados simulados (substituir com dados reais)
    sample_draws = [
        [3, 11, 17, 22, 25, 33, 41, 48, 52, 58, 64, 71, 78, 82, 89],
        [5, 12, 18, 23, 27, 34, 42, 49, 53, 59, 65, 72, 79, 83, 90],
        [7, 14, 19, 24, 28, 35, 43, 50, 54, 60, 66, 73, 80, 84, 91],
        [2, 10, 16, 21, 26, 32, 40, 47, 51, 57, 63, 70, 77, 81, 88],
    ]

    # Análise
    analysis = analyze_lottery(sample_draws)
    print(f"\n📊 Hot numbers: {analysis['hot'][:10]}")
    print(f"📊 Dezenas: {dict(sorted(analysis['dezenas'].items()))}")

    # Gerar jogos com 3 estratégias
    print("\n🎰 Generating quantum games...")

    all_games = []
    for strategy_idx in range(3):
        games = generate_games(15, analysis['hot'], 11, strategy_idx)
        all_games.extend(games)
        print(f"   Strategy {strategy_idx + 1}: {len(games)} games")

    # Estatísticas
    all_nums = [n for g in all_games for n in g["numbers"]]
    diversity = len(set(all_nums)) / len(all_nums)
    hot_coverage = len(set(all_nums).intersection(set(analysis['hot'][:20]))) / 20

    # Salvar
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {
        "timestamp": timestamp,
        "hot_numbers": analysis['hot'],
        "dezenas_pattern": analysis['dezenas'],
        "statistics": {
            "total_games": len(all_games),
            "diversity": diversity,
            "hot_coverage": hot_coverage
        },
        "games": all_games
    }

    output_file = f'output/quantum_v4_{timestamp}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    memory_file = 'memory/quantum_v4_latest.json'
    with open(memory_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "═" * 60)
    print("   RESULTS")
    print("═" * 60)
    print(f"\n   Total games: {len(all_games)}")
    print(f"   Diversity: {diversity:.2%}")
    print(f"   Hot coverage: {hot_coverage:.2%}")
    print(f"\n   Output: {output_file}")
    print("\n✅ Quantum v4.2 Complete!")


if __name__ == "__main__":
    main()