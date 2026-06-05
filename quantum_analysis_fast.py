#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           SIAOL-PRO QUANTUM ANALYSIS v1.0 - FAST MODE                        ║
║                                                                              ║
║  Análise rápida com 20 qubits                                                ║
║  • QFT, Grover, Quantum Walk                                                ║
║  • Gera 33 jogos diversificados                                              ║
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
    QuantumSimulator, QuantumCircuit, QuantumAlgorithms
)

def format_binary(idx: int, n_qubits: int) -> str:
    return format(idx, f'0{n_qubits}b')

def main():
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "SIAOL-PRO QUANTUM ANALYSIS v1.0" + " " * 17 + "║")
    print("║" + " " * 18 + "20 Qubit Parameter Execution" + " " * 18 + "║")
    print("╚" + "═" * 68 + "╝")

    n_qubits = 20
    print(f"\n🧠 Initializing {n_qubits} qubit quantum simulator...")
    print(f"   States: {2**n_qubits:,}")
    print(f"   Memory: ~{(2**n_qubits) * 16 / 1024 / 1024:.1f} MB")

    results = {
        "timestamp": datetime.now().isoformat(),
        "n_qubits": n_qubits,
        "analyses": {},
        "games": []
    }

    # 1. QFT Analysis
    print("\n📊 [1/4] QFT Analysis...")
    sim = QuantumSimulator(n_qubits)
    circuit = QuantumAlgorithms.qft(n_qubits)
    sim.apply(circuit)
    qft_measure = sim.measure(500)
    results["analyses"]["qft"] = {
        "entropy": qft_measure["entropy"],
        "top_probability": qft_measure["most_probable_prob"],
        "top_state": qft_measure["most_probable_binary"],
        "total_gates": qft_measure["total_gates"]
    }
    print(f"   Entropy: {qft_measure['entropy']:.4f} | Top Prob: {qft_measure['most_probable_prob']:.4f}")

    # 2. Grover Search
    print("\n🔍 [2/4] Grover Search...")
    sim.reset()
    target = [1, 2, 3, 4, 5, 10, 20]
    pattern = sum((num % 128) << (i * 7) for i, num in enumerate(target[:3])) % (2 ** n_qubits)
    circuit = QuantumAlgorithms.grover_search(n_qubits, [pattern], n_iterations=2)
    sim.apply(circuit)
    grover_measure = sim.measure(500)
    results["analyses"]["grover"] = {
        "entropy": grover_measure["entropy"],
        "top_probability": grover_measure["most_probable_prob"],
        "top_state": grover_measure["most_probable_binary"],
        "iterations": 2
    }
    print(f"   Entropy: {grover_measure['entropy']:.4f} | Top Prob: {grover_measure['most_probable_prob']:.4f}")

    # 3. Quantum Walk
    print("\n🚶 [3/4] Quantum Walk...")
    sim.reset()
    circuit = QuantumAlgorithms.quantum_walk(n_qubits, n_steps=5)
    sim.apply(circuit)
    walk_measure = sim.measure(500)
    results["analyses"]["walk"] = {
        "entropy": walk_measure["entropy"],
        "top_probability": walk_measure["most_probable_prob"],
        "top_5_states": [
            {"binary": format_binary(idx, n_qubits), "prob": prob}
            for idx, prob in walk_measure["top_states"][:5]
        ]
    }
    print(f"   Entropy: {walk_measure['entropy']:.4f} | Top Prob: {walk_measure['most_probable_prob']:.4f}")

    # 4. Variational Form
    print("\n⚡ [4/4] Variational Form...")
    sim.reset()
    circuit = QuantumAlgorithms.variational_form(n_qubits, depth=3)
    sim.apply(circuit)
    var_measure = sim.measure(500)
    results["analyses"]["variational"] = {
        "entropy": var_measure["entropy"],
        "top_probability": var_measure["most_probable_prob"],
        "gates": len(circuit.gates)
    }
    print(f"   Entropy: {var_measure['entropy']:.4f} | Top Prob: {var_measure['most_probable_prob']:.4f}")

    # Generate 33 Games
    print("\n🎰 Generating 33 quantum games...")
    strategies = ['walk', 'variational', 'grover', 'qft']
    games = []

    for i in range(33):
        sim.reset()
        strategy = strategies[i % len(strategies)]

        if strategy == 'walk':
            circuit = QuantumAlgorithms.quantum_walk(n_qubits, 4 + i % 3)
        elif strategy == 'variational':
            circuit = QuantumAlgorithms.variational_form(n_qubits, 2 + i % 3)
        elif strategy == 'grover':
            pattern = (i * 17) % (2 ** n_qubits)
            circuit = QuantumAlgorithms.grover_search(n_qubits, [pattern], n_iterations=1 + i % 3)
        else:  # qft
            circuit = QuantumAlgorithms.qft(n_qubits)
            for j in range(i % 3):
                sim.state = QuantumCircuit(n_qubits).H(i % n_qubits).execute(sim.state)

        state = circuit.execute() if strategy != 'qft' or i % 3 == 0 else sim.state
        outcome = state.measure()

        # Convert to lottery numbers
        binary = format_binary(outcome, n_qubits)
        numbers = []
        for j in range(0, n_qubits - 6, 7):
            if j + 7 <= n_qubits:
                num = int(binary[j:j+7], 2)
                if 1 <= num <= 100:
                    numbers.append(num)

        # Ensure 15 numbers
        while len(numbers) < 15:
            numbers.append((i * 7 + len(numbers)) % 100 + 1)
        numbers = sorted(set(numbers))[:15]
        while len(numbers) < 15:
            numbers.append((numbers[-1] % 100) + 1)
            numbers = sorted(set(numbers))

        games.append({
            "game": i + 1,
            "strategy": strategy,
            "numbers": numbers,
            "hash": hash(tuple(numbers)) % 1000000
        })

    results["games"] = games

    # Save results
    os.makedirs('output', exist_ok=True)
    output_file = f'output/quantum_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Summary
    print("\n" + "═" * 70)
    print("   SUMMARY")
    print("═" * 70)
    print(f"\n   QFT:          entropy={results['analyses']['qft']['entropy']:.4f}")
    print(f"   Grover:       entropy={results['analyses']['grover']['entropy']:.4f}")
    print(f"   Quantum Walk: entropy={results['analyses']['walk']['entropy']:.4f}")
    print(f"   Variational:  entropy={results['analyses']['variational']['entropy']:.4f}")
    print(f"\n   Games Generated: {len(games)}")
    print(f"   Results: {output_file}")

    print("\n✅ Quantum Analysis Complete!")

if __name__ == "__main__":
    main()