#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           🧠 QUINA BRAIN v3.2 - QUANTUM OPTIMIZER                       ║
║                                                                            ║
║  • Executor de Parâmetros Quânticos                                      ║
║  • QAOA (Quantum Approximate Optimization Algorithm)                      ║
║  • VQE (Variational Quantum Eigensolver)                                 ║
║  • Sweep de Parâmetros Automático                                        ║
║                                                                            ║
║  Autor: SIAOL-PRO v3.2 Quantum Brain                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
import json
import math
import random
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from itertools import combinations
import os

# ============================================
# CONFIGURAÇÕES
# ============================================
QUINA_PRICE = 3.00
MAX_DEZENA = 80
N_QUBITS = 20
DIM = 2 ** N_QUBITS

# ============================================
# CONSTANTES QUÂNTICAS
# ============================================
PI = math.pi
SQRT2 = math.sqrt(2)
SQRT_HALF = 1 / SQRT2

# ============================================
# UTILITÁRIOS MATEMÁTICOS
# ============================================
def normalize(v: np.ndarray) -> np.ndarray:
    """Normaliza vetor de estado"""
    norm = np.linalg.norm(v)
    if norm < 1e-10:
        return v
    return v / norm

def format_binary(idx: int, n_qubits: int) -> str:
    """Formata índice como string binária"""
    return format(idx, f'0{n_qubits}b')

# ============================================
# PORTAS QUÂNTICAS (NUMPY)
# ============================================
class QuantumGates:
    """Portas quânticas fundamentais"""

    @staticmethod
    def hadamard(state: np.ndarray, qubit: int, n_qubits: int) -> np.ndarray:
        """Porta Hadamard"""
        H = np.array([[SQRT_HALF, SQRT_HALF], [SQRT_HALF, -SQRT_HALF]], dtype=complex)
        new_state = state.copy()
        for i in range(len(state)):
            if (i >> qubit) & 1:
                new_state[i] = SQRT_HALF * state[i] + SQRT_HALF * state[i ^ (1 << qubit)]
            else:
                new_state[i] = SQRT_HALF * state[i] + SQRT_HALF * state[i ^ (1 << qubit)]
        return normalize(new_state)

    @staticmethod
    def pauli_x(state: np.ndarray, qubit: int) -> np.ndarray:
        """Porta Pauli-X (NOT)"""
        new_state = state.copy()
        for i in range(len(state)):
            new_state[i] = state[i ^ (1 << qubit)]
        return new_state

    @staticmethod
    def pauli_z(state: np.ndarray, qubit: int) -> np.ndarray:
        """Porta Pauli-Z"""
        new_state = state.copy()
        for i in range(len(state)):
            if (i >> qubit) & 1:
                new_state[i] = -state[i]
        return new_state

    @staticmethod
    def cnot(state: np.ndarray, control: int, target: int, n_qubits: int) -> np.ndarray:
        """Porta CNOT (Controlled-NOT)"""
        new_state = state.copy()
        for i in range(len(state)):
            if (i >> control) & 1:
                new_state[i] = state[i ^ (1 << target)]
        return new_state

    @staticmethod
    def rotation_y(state: np.ndarray, qubit: int, theta: float) -> np.ndarray:
        """Rotação em torno do eixo Y"""
        cos_t = math.cos(theta / 2)
        sin_t = math.sin(theta / 2)
        new_state = state.copy()
        for i in range(len(state)):
            if (i >> qubit) & 1:
                new_state[i] = -sin_t * state[i ^ (1 << qubit)] + cos_t * state[i]
            else:
                new_state[i] = cos_t * state[i] + sin_t * state[i ^ (1 << qubit)]
        return normalize(new_state)

    @staticmethod
    def rotation_z(state: np.ndarray, qubit: int, theta: float) -> np.ndarray:
        """Rotação em torno do eixo Z"""
        new_state = state.copy()
        for i in range(len(state)):
            if (i >> qubit) & 1:
                new_state[i] = state[i] * np.exp(-1j * theta / 2)
            else:
                new_state[i] = state[i] * np.exp(1j * theta / 2)
        return new_state

    @staticmethod
    def tgate(state: np.ndarray, qubit: int) -> np.ndarray:
        """Porta T"""
        new_state = state.copy()
        for i in range(len(state)):
            if (i >> qubit) & 1:
                new_state[i] = state[i] * np.exp(1j * PI / 4)
        return new_state

# ============================================
# SIMULADOR QUÂNTICO BÁSICO
# ============================================
class QuantumSimulator:
    """Simulador quântico otimizado"""

    def __init__(self, n_qubits: int = 10):
        self.n_qubits = n_qubits
        self.dim = 2 ** n_qubits
        self.state = np.zeros(self.dim, dtype=complex)
        self.state[0] = 1.0  # Estado |0...0>

    def apply_hadamard_all(self):
        """Aplica Hadamard em todos os qubits"""
        for q in range(self.n_qubits):
            self.state = QuantumGates.hadamard(self.state, q, self.n_qubits)
        self.state = normalize(self.state)

    def apply_cnot_chain(self):
        """Aplica CNOT em cadeia"""
        for q in range(self.n_qubits - 1):
            self.state = QuantumGates.cnot(self.state, q, q + 1, self.n_qubits)

    def measure(self, shots: int = 1000) -> Dict:
        """Mede o estado quântico"""
        probs = np.abs(self.state) ** 2
        results = np.random.choice(self.dim, size=shots, p=probs)

        counts = {}
        for r in results:
            counts[r] = counts.get(r, 0) + 1

        entropy = -sum(p * math.log2(p) for p in probs if p > 0)

        most_prob = max(probs)
        most_prob_idx = np.argmax(probs)

        return {
            "counts": counts,
            "entropy": entropy,
            "max_probability": most_prob,
            "most_probable_state": format_binary(most_prob_idx, self.n_qubits),
            "shots": shots
        }

# ============================================
# ALGORITMO QAOA
# ============================================
class QAOAOptimizer:
    """
    Quantum Approximate Optimization Algorithm
    Resolve problemas de otimização combinatória
    """

    def __init__(self, n_qubits: int = 10, p: int = 2):
        self.n_qubits = n_qubits
        self.p = p  # Profundidade do circuito
        self.gamma = [random.uniform(0, 2 * PI) for _ in range(p)]
        self.beta = [random.uniform(0, PI) for _ in range(p)]

    def cost_function(self, bitstring: int) -> float:
        """Função de custo - maximize matching in graph"""
        # Problema: Maximizar soma de bits adjacentes
        cost = 0
        for i in range(self.n_qubits - 1):
            if ((bitstring >> i) & 1) and ((bitstring >> (i + 1)) & 1):
                cost += 1
        return cost

    def build_circuit(self) -> List[Tuple[str, int, float]]:
        """Constrói circuito QAOA"""
        gates = []

        # Camada de mistura inicial
        for q in range(self.n_qubits):
            gates.append(('H', q, 0))

        # Camadas QAOA
        for layer in range(self.p):
            # Unitário de custo C(gamma)
            for i in range(self.n_qubits - 1):
                # Rz gates acoplados
                gates.append(('Rz', i, self.gamma[layer]))
                gates.append(('Rz', i + 1, self.gamma[layer]))
                gates.append(('CNOT', i, i + 1, 0))

            # Unitário de mistura B(beta)
            for q in range(self.n_qubits):
                gates.append(('Rx', q, self.beta[layer]))

        return gates

    def optimize_parameters(self, iterations: int = 50) -> Dict:
        """Otimiza parâmetros gamma e beta"""
        best_cost = float('-inf')
        best_params = (self.gamma.copy(), self.beta.copy())

        for _ in range(iterations):
            # Calcular custo médio
            sim = QuantumSimulator(self.n_qubits)

            # Aplicar circuito simplificado
            sim.apply_hadamard_all()

            for layer in range(self.p):
                # Aplicar rotações
                for q in range(self.n_qubits):
                    sim.state = QuantumGates.rotation_z(sim.state, q, self.gamma[layer])
                    sim.state = QuantumGates.rotation_y(sim.state, q, self.beta[layer])

            # Medir
            result = sim.measure(shots=500)

            # Calcular custo
            total_cost = 0
            for state_idx, count in result['counts'].items():
                cost = self.cost_function(state_idx)
                total_cost += cost * count

            avg_cost = total_cost / result['shots']

            # Atualizar melhor
            if avg_cost > best_cost:
                best_cost = avg_cost
                best_params = (self.gamma.copy(), self.beta.copy())

            # Perturbar parâmetros
            self.gamma = [g + random.uniform(-0.1, 0.1) for g in self.gamma]
            self.beta = [b + random.uniform(-0.1, 0.1) for b in self.beta]

        return {
            "best_cost": best_cost,
            "best_gamma": best_params[0],
            "best_beta": best_params[1]
        }

    def generate_samples(self, shots: int = 100) -> List[int]:
        """Gera amostras do circuito otimizado"""
        sim = QuantumSimulator(self.n_qubits)
        sim.apply_hadamard_all()

        for layer in range(self.p):
            for q in range(self.n_qubits):
                sim.state = QuantumGates.rotation_z(sim.state, q, self.gamma[layer])
                sim.state = QuantumGates.rotation_y(sim.state, q, self.beta[layer])

        result = sim.measure(shots=shots)
        return list(result['counts'].keys())

# ============================================
# ALGORITMO VQE (RÁPIDO)
# ============================================
class VQEEigensolver:
    """
    Variational Quantum Eigensolver - Versão Rápida
    """

    def __init__(self, n_qubits: int = 5):
        self.n_qubits = n_qubits
        self.dim = 2 ** n_qubits
        self.params = [random.uniform(0, PI) for _ in range(n_qubits)]

    def ansatz_fast(self) -> np.ndarray:
        """Ansatz simples sem matrizes grandes"""
        state = np.zeros(self.dim, dtype=complex)
        state[0] = 1.0

        for q in range(self.n_qubits):
            theta = self.params[q % len(self.params)]
            state = QuantumGates.rotation_y(state, q, theta)

        return normalize(state)

    def energy_fast(self) -> float:
        """Energia calculada via simulação"""
        state = self.ansatz_fast()
        probs = np.abs(state) ** 2

        # Energia: média ponderada de estados
        energy = 0
        for i, p in enumerate(probs):
            # Count bits
            bits = bin(i).count('1')
            energy += p * bits

        return energy

    def optimize(self, iterations: int = 10) -> Dict:
        """Otimização rápida"""
        best_energy = float('inf')
        best_params = self.params.copy()

        for _ in range(iterations):
            e = self.energy_fast()

            if e < best_energy:
                best_energy = e
                best_params = self.params.copy()

            # Perturbação aleatória
            self.params = [p + random.uniform(-0.2, 0.2) for p in self.params]

        return {
            "min_energy": best_energy,
            "optimal_params": best_params
        }

    def get_solution(self) -> np.ndarray:
        """Retorna estado otimizado"""
        self.params = self.optimize(10)["optimal_params"]
        return self.ansatz_fast()

# ============================================
# EXECUTOR DE PARÂMETROS
# ============================================
class ParameterSweeper:
    """Executa sweep de parâmetros quânticos"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "qubit_sweep": [],
            "walk_sweep": [],
            "rotation_sweep": [],
            "qaoa_sweep": [],
            "vqe_sweep": []
        }

    def sweep_qubit_sizes(self, sizes: List[int] = [8, 10, 12]) -> Dict:
        """Sweep de número de qubits"""
        print("\n🔬 SWEEP: Tamanho de Qubits")

        for n in sizes:
            sim = QuantumSimulator(n)
            sim.apply_hadamard_all()

            if n <= 12:
                sim.apply_cnot_chain()

            result = sim.measure(shots=500)

            entry = {
                "n_qubits": n,
                "entropy": result["entropy"],
                "max_prob": result["max_probability"]
            }
            self.results["qubit_sweep"].append(entry)

            print(f"   {n} qubits: entropia={result['entropy']:.4f}, prob={result['max_probability']:.6f}")

        return self.results["qubit_sweep"]

    def sweep_walk_steps(self, steps_list: List[int] = [2, 3, 4]) -> Dict:
        """Sweep de passos do Quantum Walk"""
        print("\n🚶 SWEEP: Passos do Quantum Walk")

        for steps in steps_list:
            sim = QuantumSimulator(10)
            sim.apply_hadamard_all()

            # Quantum Walk simulado
            for _ in range(steps):
                for q in range(10):
                    sim.state = QuantumGates.rotation_y(sim.state, q, 0.5)
                sim.apply_cnot_chain()

            result = sim.measure(shots=500)

            entry = {
                "steps": steps,
                "entropy": result["entropy"],
                "max_prob": result["max_probability"]
            }
            self.results["walk_sweep"].append(entry)

            print(f"   {steps} passos: entropia={result['entropy']:.4f}")

        return self.results["walk_sweep"]

    def sweep_rotations(self, angles: List[float] = [0.3, 0.5, 0.7, PI/4]) -> Dict:
        """Sweep de ângulos de rotação"""
        print("\n🔄 SWEEP: Ângulos de Rotação")

        for angle in angles:
            sim = QuantumSimulator(10)
            for q in range(10):
                sim.state = QuantumGates.hadamard(sim.state, q, 10)
                sim.state = QuantumGates.rotation_y(sim.state, q, angle)

            result = sim.measure(shots=500)

            entry = {
                "angle": angle,
                "entropy": result["entropy"],
                "max_prob": result["max_probability"]
            }
            self.results["rotation_sweep"].append(entry)

            print(f"   θ={angle:.3f}: entropia={result['entropy']:.4f}")

        return self.results["rotation_sweep"]

    def run_qaoa(self, depth: int = 2) -> Dict:
        """Executa QAOA e retorna resultados"""
        print(f"\n⚡ SWEEP: QAOA (depth={depth})")

        qaoa = QAOAOptimizer(n_qubits=10, p=depth)
        optimal = qaoa.optimize_parameters(iterations=30)

        samples = qaoa.generate_samples(shots=100)

        entry = {
            "depth": depth,
            "best_cost": optimal["best_cost"],
            "best_gamma": optimal["best_gamma"],
            "best_beta": optimal["best_beta"],
            "samples": samples[:10]
        }
        self.results["qaoa_sweep"].append(entry)

        print(f"   Custo ótimo: {optimal['best_cost']:.4f}")
        return entry

    def run_vqe(self) -> Dict:
        """Executa VQE e retorna resultados"""
        print("\n📊 SWEEP: VQE Eigensolver")

        vqe = VQEEigensolver(n_qubits=10)
        result = vqe.optimize(iterations=30)

        entry = {
            "min_energy": result["min_energy"],
            "optimal_params": result["optimal_params"][:5]
        }
        self.results["vqe_sweep"].append(entry)

        print(f"   Energia mínima: {result['min_energy']:.6f}")
        return entry

    def get_optimal_params(self) -> Dict:
        """Retorna parâmetros ótimos encontrados"""
        best_qubit = max(self.results["qubit_sweep"], key=lambda x: x["max_prob"])
        best_walk = max(self.results["walk_sweep"], key=lambda x: x["max_prob"])
        best_rot = max(self.results["rotation_sweep"], key=lambda x: x["max_prob"])

        return {
            "best_qubits": best_qubit["n_qubits"],
            "best_walk_steps": best_walk["steps"],
            "best_rotation_angle": best_rot["angle"]
        }

# ============================================
# GERADOR DE JOGOS QUÂNTICOS
# ============================================
class QuantumGameGenerator:
    """Gera jogos Quina usando algoritmos quânticos"""

    def __init__(self):
        self.hot_numbers = [15, 13, 27, 12, 20, 18, 24, 1, 3, 5, 14, 35, 38, 11, 53]
        self.cold_numbers = [69, 6, 62, 30, 72, 28, 76, 78, 74, 65]

    def generate_qaoa_games(self, n_games: int = 10) -> List[List[int]]:
        """Gera jogos usando QAOA"""
        print(f"\n🎰 GERANDO {n_games} JOGOS VIA QAOA...")

        qaoa = QAOAOptimizer(n_qubits=10, p=2)
        qaoa.optimize_parameters(iterations=50)

        samples = qaoa.generate_samples(shots=n_games * 10)

        games = []
        for sample in samples[:n_games]:
            # Mapear bits para números Quina
            bitstring = format(sample, '010b')
            game = []

            # Usar bits para selecionar números
            for i, bit in enumerate(bitstring):
                if bit == '1' and len(game) < 5:
                    if i < len(self.hot_numbers):
                        game.append(self.hot_numbers[i])

            # Completar se necessário
            while len(game) < 5:
                for n in self.hot_numbers + self.cold_numbers:
                    if n not in game:
                        game.append(n)
                        break

            games.append(sorted(game[:5]))

        return games

    def generate_vqe_games(self, n_games: int = 10) -> List[List[int]]:
        """Gera jogos usando VQE"""
        print(f"\n🎰 GERANDO {n_games} JOGOS VIA VQE...")

        vqe = VQEEigensolver(n_qubits=10)
        optimal_state = vqe.get_solution()

        games = []
        n = len(optimal_state)
        top_indices = np.argsort(np.abs(optimal_state))[-n_games:]

        for idx in top_indices:
            bitstring = format(idx, '010b')
            game = []

            for i, bit in enumerate(bitstring):
                if bit == '1' and len(game) < 5:
                    if i < len(self.hot_numbers):
                        game.append(self.hot_numbers[i])

            while len(game) < 5:
                for n in self.hot_numbers + self.cold_numbers:
                    if n not in game:
                        game.append(n)
                        break

            games.append(sorted(game[:5]))

        return games

    def generate_hybrid_games(self, n_games: int = 20) -> List[List[int]]:
        """Gera jogos híbridos (QAOA + VQE + Hot/Cold)"""
        print(f"\n🎰 GERANDO {n_games} JOGOS HÍBRIDOS...")

        qaoa_games = self.generate_qaoa_games(n_games // 3)
        vqe_games = self.generate_vqe_games(n_games // 3)

        # Hot/Cold games
        hot_games = []
        for _ in range(n_games // 3):
            game = sorted(random.sample(self.hot_numbers[:10], 3) +
                         random.sample(self.cold_numbers[:5], 2))
            hot_games.append(game)

        all_games = qaoa_games + vqe_games + hot_games
        return all_games[:n_games]

# ============================================
# FUNÇÃO PRINCIPAL
# ============================================
def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║     🧠 QUINA BRAIN v3.2 - QUANTUM OPTIMIZER                              ║
║                                                                            ║
║     • Executor de Parâmetros                                              ║
║     • QAOA Algorithm                                                     ║
║     • VQE Eigensolver                                                    ║
║     • Geração Otimizada de Jogos                                         ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

    sweeper = ParameterSweeper()
    game_gen = QuantumGameGenerator()

    # 1. Sweep de parâmetros
    print("\n" + "="*70)
    print("🔬 PARTE 1: SWEEP DE PARÂMETROS")
    print("="*70)

    sweeper.sweep_qubit_sizes([8, 10, 12])
    sweeper.sweep_walk_steps([2, 3, 4])
    sweeper.sweep_rotations([0.3, 0.5, 0.7])

    # 2. QAOA
    print("\n" + "="*70)
    print("⚡ PARTE 2: QAOA OPTIMIZATION")
    print("="*70)

    sweeper.run_qaoa(depth=2)

    # 3. VQE
    print("\n" + "="*70)
    print("📊 PARTE 3: VQE EIGENSOLVER")
    print("="*70)

    sweeper.run_vqe()

    # 4. Parâmetros ótimos
    optimal = sweeper.get_optimal_params()
    print(f"\n🎯 PARÂMETROS ÓTIMOS:")
    print(f"   Qubits: {optimal['best_qubits']}")
    print(f"   Walk Steps: {optimal['best_walk_steps']}")
    print(f"   Rotation: {optimal['best_rotation_angle']:.4f}")

    # 5. Gerar jogos
    print("\n" + "="*70)
    print("🎰 PARTE 4: GERAÇÃO DE JOGOS QUÂNTICOS")
    print("="*70)

    qaoa_games = game_gen.generate_qaoa_games(5)
    vqe_games = game_gen.generate_vqe_games(5)
    hybrid_games = game_gen.generate_hybrid_games(10)

    print(f"\n📋 JOGOS QAOA:")
    for i, g in enumerate(qaoa_games, 1):
        print(f"   {i}. {g}")

    print(f"\n📋 JOGOS VQE:")
    for i, g in enumerate(vqe_games, 1):
        print(f"   {i}. {g}")

    print(f"\n📋 JOGOS HÍBRIDOS:")
    for i, g in enumerate(hybrid_games, 1):
        print(f"   {i}. {g}")

    # 6. Salvar resultados
    output_file = f"output/quantum_optimizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("output", exist_ok=True)

    def convert_to_native(obj):
        """Converte tipos numpy para Python native"""
        if isinstance(obj, dict):
            return {k: convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_native(i) for i in obj]
        elif isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "parameters": convert_to_native(optimal),
            "sweep_results": convert_to_native(sweeper.results),
            "games": {
                "qaoa": convert_to_native(qaoa_games),
                "vqe": convert_to_native(vqe_games),
                "hybrid": convert_to_native(hybrid_games)
            }
        }, f, indent=2)

    print(f"\n💾 Salvo em: {output_file}")

    print("\n" + "="*70)
    print("✅ QUINA BRAIN v3.2 - QUANTUM OPTIMIZER COMPLETO!")
    print("="*70)

    return sweeper.results


if __name__ == "__main__":
    main()
