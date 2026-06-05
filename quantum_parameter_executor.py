#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           SIAOL-PRO QUANTUM PARAMETER EXECUTOR v2.1                         ║
║                    MINIMAL VERSION - FAST EXECUTION                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
import json
import math
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quantum_simulator_20_qubits import (
    QuantumSimulator, QuantumAlgorithms, QuantumOps
)

def format_binary(idx: int, n_qubits: int) -> str:
    return format(idx, f'0{n_qubits}b')

def main():
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║     SIAOL-PRO QUANTUM PARAMETER EXECUTOR v2.1              ║")
    print("╚════════════════════════════════════════════════════════════╝")

    os.makedirs('output', exist_ok=True)
    os.makedirs('memory', exist_ok=True)

    results = {
        "timestamp": datetime.now().isoformat(),
        "parameter_sweeps": {},
        "games": [],
        "summary": {}
    }

    # 1. Qubit Size Sweep (fast)
    print("\n📊 [1/4] Qubit Size Sweep...")
    qubit_results = []
    for n_qubits in [10, 12, 15]:
        sim = QuantumSimulator(n_qubits)
        for q in range(n_qubits):
            sim.state = QuantumOps.hadamard(sim.state, q)
        measure = sim.measure(300)
        qubit_results.append({
            "value": n_qubits,
            "entropy": measure["entropy"],
            "top_probability": measure["most_probable_prob"]
        })
        print(f"   {n_qubits} qubits: entropy={measure['entropy']:.4f}, prob={measure['most_probable_prob']:.6f}")
    results["parameter_sweeps"]["qubit_sizes"] = qubit_results

    # 2. Walk Steps Sweep (fast)
    print("\n🚶 [2/4] Quantum Walk Steps Sweep...")
    walk_results = []
    n_qubits = 12
    for steps in [3, 4, 5]:
        sim = QuantumSimulator(n_qubits)
        circuit = QuantumAlgorithms.quantum_walk(n_qubits, steps)
        sim.apply(circuit)
        measure = sim.measure(300)
        walk_results.append({
            "value": steps,
            "entropy": measure["entropy"],
            "top_probability": measure["most_probable_prob"]
        })
        print(f"   steps={steps}: entropy={measure['entropy']:.4f}, prob={measure['most_probable_prob']:.6f}")
    results["parameter_sweeps"]["walk_steps"] = walk_results

    # 3. Variational Depth Sweep (fast)
    print("\n⚡ [3/4] Variational Depth Sweep...")
    var_results = []
    for depth in [2, 3]:
        sim = QuantumSimulator(12)
        circuit = QuantumAlgorithms.variational_form(12, depth)
        sim.apply(circuit)
        measure = sim.measure(300)
        var_results.append({
            "value": depth,
            "gates": len(circuit.gates),
            "entropy": measure["entropy"],
            "top_probability": measure["most_probable_prob"]
        })
        print(f"   depth={depth}: entropy={measure['entropy']:.4f}, prob={measure['most_probable_prob']:.6f}")
    results["parameter_sweeps"]["variational_depth"] = var_results

    # 4. Rotation Angles Sweep (fast)
    print("\n🔄 [4/4] Rotation Angles Sweep...")
    rot_results = []
    for angle in [0.5, 1.0, math.pi/4]:
        sim = QuantumSimulator(10)
        for q in range(10):
            sim.state = QuantumOps.hadamard(sim.state, q)
            sim.state = QuantumOps.rotation_y(sim.state, q, angle)
        measure = sim.measure(300)
        rot_results.append({
            "value": angle,
            "entropy": measure["entropy"],
            "top_probability": measure["most_probable_prob"]
        })
        print(f"   angle={angle:.4f}: entropy={measure['entropy']:.4f}, prob={measure['most_probable_prob']:.6f}")
    results["parameter_sweeps"]["rotation_angles"] = rot_results

    # Generate 33 Games
    print("\n🎰 Generating 33 quantum games...")
    strategies = ['walk_3', 'walk_4', 'variational_2', 'variational_3']

    for i in range(33):
        n_qubits = 15
        sim = QuantumSimulator(n_qubits)

        # Select strategy
        idx = i % 4
        if idx == 0:
            circuit = QuantumAlgorithms.quantum_walk(n_qubits, 3)
        elif idx == 1:
            circuit = QuantumAlgorithms.quantum_walk(n_qubits, 4)
        elif idx == 2:
            circuit = QuantumAlgorithms.variational_form(n_qubits, 2)
        else:
            circuit = QuantumAlgorithms.variational_form(n_qubits, 3)

        state = circuit.execute()
        outcome = state.measure()
        binary = format_binary(outcome, n_qubits)

        # Convert to lottery numbers
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
            numbers.append(n if n not in numbers else (numbers[-1] + 11) % 100 + 1)
            numbers = sorted(set(numbers))

        results["games"].append({
            "id": i + 1,
            "strategy": strategies[idx],
            "numbers": numbers
        })

        if i < 3:
            print(f"   Game {i+1}: {numbers[:10]}... ({strategies[idx]})")

    # Find best configuration
    best_configs = {}
    for param_name, sweep_results in results["parameter_sweeps"].items():
        if sweep_results:
            best = max(sweep_results, key=lambda x: x.get("top_probability", 0))
            best_configs[param_name] = best

    results["summary"]["best_configurations"] = best_configs

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'output/quantum_parameter_results_{timestamp}.json'
    memory_file = 'memory/quantum_latest_results.json'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    with open(memory_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Summary
    print("\n" + "═" * 60)
    print("   PARAMETER EXECUTION SUMMARY")
    print("═" * 60)
    print("\n   BEST CONFIGURATIONS:")
    for param, config in best_configs.items():
        print(f"   • {param}: value={config.get('value', config.get('depth', config.get('steps', 'N/A')))}, prob={config['top_probability']:.6f}")
    print(f"\n   Games Generated: {len(results['games'])}")
    print(f"   Results: {output_file}")
    print("\n✅ Quantum Parameter Execution Complete!")

if __name__ == "__main__":
    main()