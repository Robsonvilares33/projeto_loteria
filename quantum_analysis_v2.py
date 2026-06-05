#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           SIAOL-PRO QUANTUM ANALYSIS v1.1 - OPTIMIZED                       ║
║                                                                              ║
║  Análise rápida com 20 qubits - OTIMIZADO                                    ║
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
    QuantumSimulator, QuantumCircuit, QuantumAlgorithms, QuantumOps
)

def format_binary(idx: int, n_qubits: int) -> str:
    return format(idx, f'0{n_qubits}b')

def main():
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "SIAOL-PRO QUANTUM ANALYSIS v1.1" + " " * 17 + "║")
    print("║" + " " * 18 + "20 Qubit Parameter Execution" + " " * 18 + "║")
    print("╚" + "═" * 68 + "╝")

    n_qubits = 20
    print(f"\n🧠 Initializing {n_qubits} qubit quantum simulator...")
    print(f"   States: {2**n_qubits:,}")

    results = {
        "timestamp": datetime.now().isoformat(),
        "n_qubits": n_qubits,
        "methods": {}
    }

    # 1. Superposition Test
    print("\n📊 [1/3] Superposition + Entanglement...")
    sim = QuantumSimulator(n_qubits)

    # Hadamard on all qubits
    for q in range(n_qubits):
        sim.state = QuantumOps.hadamard(sim.state, q)

    # Create entanglement chain
    for q in range(n_qubits - 1):
        sim.state = QuantumOps.cnot(sim.state, q, q + 1)

    measure = sim.measure(1000)
    results["methods"]["superposition_entangle"] = {
        "entropy": measure["entropy"],
        "top_probability": measure["most_probable_prob"],
        "top_state": measure["most_probable_binary"]
    }
    print(f"   Entropy: {measure['entropy']:.4f} | Top Prob: {measure['most_probable_prob']:.6f}")

    # 2. Quantum Walk
    print("\n🚶 [2/3] Quantum Walk...")
    sim.reset()
    circuit = QuantumAlgorithms.quantum_walk(n_qubits, n_steps=4)
    sim.apply(circuit)
    measure = sim.measure(1000)
    results["methods"]["quantum_walk"] = {
        "entropy": measure["entropy"],
        "top_probability": measure["most_probable_prob"],
        "top_5_states": [
            {"binary": format_binary(idx, n_qubits), "prob": float(prob)}
            for idx, prob in measure["top_states"][:5]
        ]
    }
    print(f"   Entropy: {measure['entropy']:.4f} | Top Prob: {measure['most_probable_prob']:.6f}")

    # 3. Variational Form
    print("\n⚡ [3/3] Variational Form...")
    sim.reset()
    circuit = QuantumAlgorithms.variational_form(n_qubits, depth=2)
    sim.apply(circuit)
    measure = sim.measure(1000)
    results["methods"]["variational"] = {
        "entropy": measure["entropy"],
        "top_probability": measure["most_probable_prob"],
        "gates": len(circuit.gates)
    }
    print(f"   Entropy: {measure['entropy']:.4f} | Top Prob: {measure['most_probable_prob']:.6f}")

    # Generate 33 Games with different strategies
    print("\n🎰 Generating 33 quantum games...")
    games = []
    strategies = ['walk', 'variational', 'superposition']

    for i in range(33):
        sim.reset()
        strategy = strategies[i % len(strategies)]

        if strategy == 'walk':
            circuit = QuantumAlgorithms.quantum_walk(n_qubits, 3 + i % 3)
            state = circuit.execute()
        elif strategy == 'variational':
            circuit = QuantumAlgorithms.variational_form(n_qubits, 2)
            state = circuit.execute()
        else:
            # Superposition with rotations
            for q in range(n_qubits):
                sim.state = QuantumOps.hadamard(sim.state, q)
                if i % 2 == 0:
                    sim.state = QuantumOps.rotation_y(sim.state, q, 0.5)
            state = sim.state

        outcome = state.measure()
        binary = format_binary(outcome, n_qubits)

        # Convert to lottery numbers (15 numbers)
        numbers = []
        for j in range(0, n_qubits - 6, 7):
            if j + 7 <= n_qubits:
                num = int(binary[j:j+7], 2)
                if 1 <= num <= 100:
                    numbers.append(num)

        # Ensure 15 valid numbers
        while len(numbers) < 15:
            numbers.append((i * 7 + len(numbers)) % 100 + 1)
        numbers = sorted(set(numbers))[:15]
        while len(numbers) < 15:
            n = (numbers[-1] % 100) + 1
            if n not in numbers:
                numbers.append(n)
            else:
                numbers.append((numbers[-1] + 1) % 100 + 1)
            numbers = sorted(set(numbers))

        games.append({
            "id": i + 1,
            "strategy": strategy,
            "numbers": numbers
        })

        if i < 5 or i % 10 == 9:
            print(f"   Game {i+1}: {numbers[:10]}... ({strategy})")

    results["games"] = games

    # Find best method
    best_method = max(results["methods"].items(), key=lambda x: x[1]["top_probability"])
    results["best_method"] = {
        "name": best_method[0],
        "top_probability": best_method[1]["top_probability"]
    }

    # Save results
    os.makedirs('output', exist_ok=True)
    output_file = f'output/quantum_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Summary
    print("\n" + "═" * 70)
    print("   RESULTS SUMMARY")
    print("═" * 70)
    print(f"\n   Best Method: {results['best_method']['name']}")
    print(f"   Top Probability: {results['best_method']['top_probability']:.6f}")
    print(f"   Games Generated: {len(games)}")
    print(f"   Output: {output_file}")
    print("\n✅ Quantum Analysis Complete!")

if __name__ == "__main__":
    main()