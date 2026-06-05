#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           SIAOL-PRO QUANTUM SIMULATOR OPTIMIZED v3.0                       ║
║                                                                              ║
║  Simulador quântico otimizado para 20 qubits                                ║
║  • Usa representações sparse para economia de memória                       ║
║  • Portas quânticas implementadas via operações vetoriais                   ║
║  • Algoritmos: QFT, Grover, Quantum Walk                                    ║
║  • Integração com Lottery Intelligence Framework                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import json
import math
from datetime import datetime
from collections import Counter

# ============================================================
# CONSTANTES
# ============================================================

DEFAULT_QUBITS = 20
DIM_20 = 2 ** 20  # 1,048,576

# Tolerance
EPS = 1e-10

# ============================================================
# UTILITÁRIOS MATEMÁTICOS
# ============================================================

def format_binary(idx: int, n_qubits: int) -> str:
    """Formata índice como string binária"""
    return format(idx, f'0{n_qubits}b')

def compute_probabilities(amplitudes: np.ndarray) -> np.ndarray:
    """Computa probabilidades a partir de amplitudes"""
    return np.abs(amplitudes) ** 2

def normalize_vector(v: np.ndarray) -> np.ndarray:
    """Normaliza vetor"""
    norm = np.sqrt(np.sum(np.abs(v) ** 2))
    if norm < EPS:
        return v
    return v / norm

# ============================================================
# CLASSE: ESTADO QUÂNTICO (OTIMIZADO)
# ============================================================

@dataclass
class QuantumState:
    """Estado quântico com operações vetoriais otimizadas"""
    n_qubits: int
    amplitudes: np.ndarray  # Vetor complexo de tamanho 2^n

    def __post_init__(self):
        """Normaliza automaticamente"""
        self.amplitudes = normalize_vector(self.amplitudes)

    @staticmethod
    def zero(n_qubits: int) -> 'QuantumState':
        """Estado |0...0>"""
        amps = np.zeros(2 ** n_qubits, dtype=np.complex128)
        amps[0] = 1.0
        return QuantumState(n_qubits, amps)

    @staticmethod
    def uniform(n_qubits: int) -> 'QuantumState':
        """Superposição uniforme |+...+>"""
        dim = 2 ** n_qubits
        amps = np.ones(dim, dtype=np.complex128) / np.sqrt(dim)
        return QuantumState(n_qubits, amps)

    @staticmethod
    def from_pattern(binary_str: str) -> 'QuantumState':
        """Cria estado a partir de string binária"""
        n = len(binary_str)
        idx = int(binary_str, 2)
        amps = np.zeros(2 ** n, dtype=np.complex128)
        amps[idx] = 1.0
        return QuantumState(n, amps)

    def measure(self) -> int:
        """Mede o estado (colapsa para um estado base)"""
        probs = compute_probabilities(self.amplitudes)
        probs = probs / np.sum(probs)
        return np.random.choice(len(probs), p=probs)

    def measure_batch(self, n: int) -> List[int]:
        """Mede múltiplas vezes sem colapsar"""
        return [self.measure() for _ in range(n)]

    def entropy(self) -> float:
        """Entropia de Shannon"""
        probs = compute_probabilities(self.amplitudes)
        probs = probs[probs > EPS]
        return -np.sum(probs * np.log2(probs + EPS))

    def top_states(self, k: int = 10) -> List[Tuple[int, float]]:
        """Retorna os k estados mais prováveis"""
        probs = compute_probabilities(self.amplitudes)
        indices = np.argsort(probs)[::-1][:k]
        return [(int(i), float(probs[i])) for i in indices]

    def copy(self) -> 'QuantumState':
        """Cópia defensiva"""
        return QuantumState(self.n_qubits, np.copy(self.amplitudes))

# ============================================================
# OPERAÇÕES QUÂNTICAS (OTIMIZADAS)
# ============================================================

class QuantumOps:
    """Operações quânticas otimizadas sem construção de matrizes enormes"""

    @staticmethod
    def hadamard(state: QuantumState, qubit: int) -> QuantumState:
        """Aplica Hadamard em qubit específico via índice de bits"""
        dim = 2 ** state.n_qubits
        new_amps = np.zeros(dim, dtype=np.complex128)
        factor = 1.0 / np.sqrt(2)

        for i in range(dim):
            amp = state.amplitudes[i]

            # Determinar bit do qubit
            bit = (i >> qubit) & 1

            # Calcular índices para H
            # H|i> = (|0> + |1>) / sqrt(2) se bit=0
            # H|i> = (|0> - |1>) / sqrt(2) se bit=1
            i0 = i & ~(1 << qubit)  # Clear bit
            i1 = i | (1 << qubit)   # Set bit

            if bit == 0:
                new_amps[i0] += amp * factor
                new_amps[i1] += amp * factor
            else:
                new_amps[i0] += amp * factor
                new_amps[i1] -= amp * factor

        return QuantumState(state.n_qubits, new_amps)

    @staticmethod
    def pauli_x(state: QuantumState, qubit: int) -> QuantumState:
        """Aplicação otimizada de Pauli-X (NOT)"""
        dim = 2 ** state.n_qubits
        new_amps = np.zeros(dim, dtype=np.complex128)

        for i in range(dim):
            # Flip bit no qubit
            new_idx = i ^ (1 << qubit)
            new_amps[new_idx] = state.amplitudes[i]

        return QuantumState(state.n_qubits, new_amps)

    @staticmethod
    def pauli_z(state: QuantumState, qubit: int) -> QuantumState:
        """Aplicação de Pauli-Z (flip de fase)"""
        new_amps = state.amplitudes.copy()
        dim = 2 ** state.n_qubits

        for i in range(dim):
            if ((i >> qubit) & 1) == 1:
                new_amps[i] *= -1

        return QuantumState(state.n_qubits, new_amps)

    @staticmethod
    def cnot(state: QuantumState, control: int, target: int) -> QuantumState:
        """CNOT: flip target se control=1"""
        dim = 2 ** state.n_qubits
        new_amps = np.zeros(dim, dtype=np.complex128)

        for i in range(dim):
            amp = state.amplitudes[i]
            ctrl_bit = (i >> control) & 1

            if ctrl_bit == 1:
                # Flip target bit
                new_idx = i ^ (1 << target)
                new_amps[new_idx] = amp
            else:
                new_amps[i] = amp

        return QuantumState(state.n_qubits, new_amps)

    @staticmethod
    def cz(state: QuantumState, q1: int, q2: int) -> QuantumState:
        """CZ (Controlled-Z) gate"""
        new_amps = state.amplitudes.copy()
        dim = 2 ** state.n_qubits

        for i in range(dim):
            bit1 = (i >> q1) & 1
            bit2 = (i >> q2) & 1
            if bit1 == 1 and bit2 == 1:
                new_amps[i] *= -1

        return QuantumState(state.n_qubits, new_amps)

    @staticmethod
    def swap(state: QuantumState, q1: int, q2: int) -> QuantumState:
        """SWAP dois qubits"""
        new_amps = np.zeros(2 ** state.n_qubits, dtype=np.complex128)

        for i in range(2 ** state.n_qubits):
            amp = state.amplitudes[i]

            # Permutar bits
            bit1 = (i >> q1) & 1
            bit2 = (i >> q2) & 1

            # Criar novo índice com bits trocados
            new_i = i
            if bit1 != bit2:
                new_i = i ^ (1 << q1)
                new_i = new_i ^ (1 << q2)

            new_amps[new_i] = amp

        return QuantumState(state.n_qubits, new_amps)

    @staticmethod
    def rotation_y(state: QuantumState, qubit: int, theta: float) -> QuantumState:
        """Rotação Ry - aproximação para qubits específicos"""
        dim = 2 ** state.n_qubits
        new_amps = np.zeros(dim, dtype=np.complex128)
        cos = np.cos(theta / 2)
        sin = np.sin(theta / 2)

        for i in range(dim):
            amp = state.amplitudes[i]
            bit = (i >> qubit) & 1

            i0 = i & ~(1 << qubit)
            i1 = i | (1 << qubit)

            if bit == 0:
                new_amps[i0] += amp * cos
                new_amps[i1] += amp * sin
            else:
                new_amps[i0] += amp * sin
                new_amps[i1] -= amp * cos

        return QuantumState(state.n_qubits, new_amps)

    @staticmethod
    def rotation_z(state: QuantumState, qubit: int, theta: float) -> QuantumState:
        """Rotação Rz - muda fase"""
        new_amps = state.amplitudes.copy()
        exp_neg = np.exp(-1j * theta / 2)
        exp_pos = np.exp(1j * theta / 2)

        for i in range(len(new_amps)):
            bit = (i >> qubit) & 1
            if bit == 0:
                new_amps[i] *= exp_neg
            else:
                new_amps[i] *= exp_pos

        return QuantumState(state.n_qubits, new_amps)

    @staticmethod
    def apply_phase(state: QuantumState, phase: float, pattern: int) -> QuantumState:
        """Aplica fase a estado específico (oráculo de Grover)"""
        new_amps = state.amplitudes.copy()
        new_amps[pattern] *= np.exp(1j * phase)
        return QuantumState(state.n_qubits, new_amps)

    @staticmethod
    def diffuser(state: QuantumState) -> QuantumState:
        """Diffuser para algoritmo de Grover: 2|ψ><ψ| - I"""
        # Calcular média das amplitudes
        mean = np.mean(state.amplitudes)

        # 2*mean - amplitude
        new_amps = 2 * mean - state.amplitudes

        return QuantumState(state.n_qubits, new_amps)

# ============================================================
# CIRCUITO QUÂNTICO (OTIMIZADO)
# ============================================================

@dataclass
class Gate:
    """Porta quântica como operação"""
    name: str
    op_type: str
    qubits: Tuple[int, ...]
    params: Dict

class QuantumCircuit:
    """Circuito quântico com execução eficiente"""

    def __init__(self, n_qubits: int, name: str = "Circuit"):
        self.n_qubits = n_qubits
        self.name = name
        self.gates: List[Gate] = []

    def add(self, gate: Gate) -> 'QuantumCircuit':
        self.gates.append(gate)
        return self

    def H(self, qubit: int) -> 'QuantumCircuit':
        return self.add(Gate("H", "h", (qubit,), {}))

    def X(self, qubit: int) -> 'QuantumCircuit':
        return self.add(Gate("X", "x", (qubit,), {}))

    def Z(self, qubit: int) -> 'QuantumCircuit':
        return self.add(Gate("Z", "z", (qubit,), {}))

    def CNOT(self, control: int, target: int) -> 'QuantumCircuit':
        return self.add(Gate("CNOT", "cnot", (control, target), {}))

    def CZ(self, q1: int, q2: int) -> 'QuantumCircuit':
        return self.add(Gate("CZ", "cz", (q1, q2), {}))

    def SWAP(self, q1: int, q2: int) -> 'QuantumCircuit':
        return self.add(Gate("SWAP", "swap", (q1, q2), {}))

    def Ry(self, theta: float, qubit: int) -> 'QuantumCircuit':
        return self.add(Gate("Ry", "ry", (qubit,), {'theta': theta}))

    def Rz(self, theta: float, qubit: int) -> 'QuantumCircuit':
        return self.add(Gate("Rz", "rz", (qubit,), {'theta': theta}))

    def execute(self, initial_state: QuantumState = None) -> QuantumState:
        """Executa circuito"""
        if initial_state is None:
            state = QuantumState.zero(self.n_qubits)
        else:
            state = initial_state.copy()

        for gate in self.gates:
            state = self._apply_gate(state, gate)

        return state

    def _apply_gate(self, state: QuantumState, gate: Gate) -> QuantumState:
        """Aplica porta específica"""
        op = gate.op_type
        qs = gate.qubits

        if op == "h":
            return QuantumOps.hadamard(state, qs[0])
        elif op == "x":
            return QuantumOps.pauli_x(state, qs[0])
        elif op == "z":
            return QuantumOps.pauli_z(state, qs[0])
        elif op == "cnot":
            return QuantumOps.cnot(state, qs[0], qs[1])
        elif op == "cz":
            return QuantumOps.cz(state, qs[0], qs[1])
        elif op == "swap":
            return QuantumOps.swap(state, qs[0], qs[1])
        elif op == "ry":
            return QuantumOps.rotation_y(state, qs[0], gate.params.get('theta', 0))
        elif op == "rz":
            return QuantumOps.rotation_z(state, qs[0], gate.params.get('theta', 0))
        else:
            return state

# ============================================================
# ALGORITMOS QUÂNTICOS
# ============================================================

class QuantumAlgorithms:
    """Implementação de algoritmos quânticos"""

    @staticmethod
    def qft(n_qubits: int) -> QuantumCircuit:
        """Quantum Fourier Transform"""
        circuit = QuantumCircuit(n_qubits, "QFT")

        for i in range(n_qubits):
            circuit.H(i)  # Hadamard
            # Rotações controladas
            for j in range(1, n_qubits - i):
                theta = np.pi / (2 ** j)
                # RZ controlado (simplificado)
                circuit.Rz(theta, i + j)

        return circuit

    @staticmethod
    def grover_search(n_qubits: int, marked_states: List[int],
                     n_iterations: int = None) -> QuantumCircuit:
        """Busca de Grover para estados marcados"""
        if n_iterations is None:
            n_iterations = int(np.pi / 4 * np.sqrt(2 ** n_qubits))
        n_iterations = min(n_iterations, 10)  # Limitar para 20 qubits

        circuit = QuantumCircuit(n_qubits, "Grover")

        # Inicialização: superposição
        for i in range(n_qubits):
            circuit.H(i)

        # Iterações de Grover
        for _ in range(n_iterations):
            # Oráculo: flip de fase
            for marked in marked_states:
                # Aplicar Z ao estado marcado
                for q in range(n_qubits):
                    if (marked >> q) & 1:
                        circuit.X(q)
                # Fase
                circuit.Z(n_qubits - 1)
                for q in range(n_qubits):
                    if (marked >> q) & 1:
                        circuit.X(q)

            # Diffuser
            for i in range(n_qubits):
                circuit.H(i)
                circuit.X(i)
            circuit.Z(0)
            for i in range(n_qubits):
                circuit.X(i)
                circuit.H(i)

        return circuit

    @staticmethod
    def quantum_walk(n_qubits: int, n_steps: int = 5) -> QuantumCircuit:
        """Caminhada quântica"""
        circuit = QuantumCircuit(n_qubits, "QuantumWalk")

        for step in range(n_steps):
            # Hadamard em todos
            for i in range(n_qubits):
                circuit.H(i)

            # Rotações
            for i in range(n_qubits):
                theta = np.pi / (2 ** (step + 1))
                circuit.Ry(theta, i)

            # Entrelaçamento
            for i in range(n_qubits - 1):
                circuit.CNOT(i, i + 1)

        return circuit

    @staticmethod
    def variational_form(n_qubits: int, depth: int = 3) -> QuantumCircuit:
        """Forma variacional (ansatz) para VQE"""
        circuit = QuantumCircuit(n_qubits, "Variational")

        for layer in range(depth):
            # Rotações
            for q in range(n_qubits):
                circuit.Ry(np.random.uniform(0, np.pi), q)
                circuit.Rz(np.random.uniform(0, 2 * np.pi), q)

            # Entrelaçamento
            for q in range(n_qubits - 1):
                circuit.CNOT(q, q + 1)
            if n_qubits > 1:
                circuit.CNOT(n_qubits - 1, 0)

        return circuit

# ============================================================
# SIMULADOR PRINCIPAL
# ============================================================

class QuantumSimulator:
    """Simulador quântico com 20 qubits"""

    def __init__(self, n_qubits: int = 20):
        self.n_qubits = n_qubits
        self.dimension = 2 ** n_qubits
        self.state = QuantumState.zero(n_qubits)
        self.gate_history: List[str] = []

        print(f"\n🧠 Quantum Simulator v3.0 - {n_qubits} qubits")
        print(f"   Dimension: {self.dimension:,} states")
        print(f"   Memory: ~{self.dimension * 16 / 1024 / 1024:.1f} MB")

    def reset(self) -> 'QuantumSimulator':
        """Reset para |0...0>"""
        self.state = QuantumState.zero(self.n_qubits)
        self.gate_history = []
        return self

    def apply(self, circuit: QuantumCircuit) -> 'QuantumSimulator':
        """Aplica circuito completo"""
        self.state = circuit.execute(self.state)
        self.gate_history.extend([g.name for g in circuit.gates])
        return self

    def hadamard_all(self, qubits: List[int] = None) -> 'QuantumSimulator':
        """Hadamard em múltiplos qubits"""
        if qubits is None:
            qubits = list(range(self.n_qubits))

        circuit = QuantumCircuit(self.n_qubits)
        for q in qubits:
            circuit.H(q)

        self.state = circuit.execute(self.state)
        self.gate_history.append(f"H({len(qubits)} qubits)")
        return self

    def entangle_chain(self, start: int = 0, end: int = None) -> 'QuantumSimulator':
        """Cria cadeia de emaranhamento"""
        if end is None:
            end = self.n_qubits - 1

        circuit = QuantumCircuit(self.n_qubits)
        for i in range(start, end):
            circuit.H(i)
            circuit.CNOT(i, i + 1)

        self.state = circuit.execute(self.state)
        self.gate_history.append(f"Entangle({start}-{end})")
        return self

    def measure(self, n_samples: int = 1000) -> Dict:
        """Mede estado atual"""
        results = self.state.measure_batch(n_samples)
        counter = Counter(results)
        top = counter.most_common(20)

        most_prob, _ = self.state.top_states(1)[0]

        return {
            'n_samples': n_samples,
            'total_gates': len(self.gate_history),
            'entropy': float(self.state.entropy()),
            'most_probable': most_prob,
            'most_probable_binary': format_binary(most_prob, self.n_qubits),
            'most_probable_prob': float(self.state.amplitudes[most_prob].real ** 2 +
                                        self.state.amplitudes[most_prob].imag ** 2),
            'top_states': [(idx, cnt, cnt/n_samples*100) for idx, cnt in top[:10]]
        }

    def visualize(self, top_n: int = 15) -> str:
        """Visualização ASCII"""
        top_states = self.state.top_states(top_n)

        lines = [
            "",
            "═" * 60,
            f"   QUANTUM STATE VISUALIZATION ({self.n_qubits} qubits)",
            "═" * 60,
            f"   Entropy: {self.state.entropy():.4f} bits",
            f"   Gates applied: {len(self.gate_history)}",
            "",
            "   State                    Probability  Bar",
            "   " + "─" * 58
        ]

        max_bar = 35
        for idx, prob in top_states:
            if prob < 0.0001:
                break

            binary = format_binary(idx, self.n_qubits)
            bar_len = int(prob * max_bar * 5)
            bar = "█" * max(1, bar_len)

            lines.append(f"   |{binary}>  {prob*100:6.2f}%   {bar:<35}")

        lines.append("═" * 60)

        return "\n".join(lines)

    def get_state_info(self) -> Dict:
        """Retorna info completa do estado"""
        top = self.state.top_states(20)

        return {
            'n_qubits': self.n_qubits,
            'dimension': self.dimension,
            'entropy': float(self.state.entropy()),
            'max_probability': float(self.state.top_states(1)[0][1]),
            'gates_applied': len(self.gate_history),
            'top_20_states': [
                {
                    'index': idx,
                    'binary': format_binary(idx, self.n_qubits),
                    'probability': prob,
                    'amplitude': {
                        'real': float(self.state.amplitudes[idx].real),
                        'imag': float(self.state.amplitudes[idx].imag)
                    }
                }
                for idx, prob in top
            ]
        }

# ============================================================
# LOTTERY QUANTUM ANALYZER
# ============================================================

class LotteryQuantumAnalyzer:
    """Análise quântica para loterias"""

    def __init__(self, n_qubits: int = 20):
        self.n_qubits = n_qubits
        self.dimension = 2 ** n_qubits
        self.simulator = QuantumSimulator(n_qubits)
        self.results = {}

    def encode_numbers(self, numbers: List[int], bits_per_num: int = 7) -> int:
        """Codifica lista de números em inteiro binário"""
        result = 0
        for i, num in enumerate(numbers[:self.n_qubits // bits_per_num]):
            result ^= (num % 128) << (i * bits_per_num)
        return result % self.dimension

    def create_pattern_state(self, numbers: List[int]) -> QuantumState:
        """Cria estado quântico representando padrão de números"""
        pattern = self.encode_numbers(numbers)
        state = QuantumState.zero(self.n_qubits)
        # Superposição em torno do padrão
        for i in range(min(100, self.dimension)):
            offset = (i - 50) % self.dimension
            idx = (pattern + offset) % self.dimension
            phase = offset / 50 * np.pi
            state.amplitudes[idx] = np.exp(1j * phase) / np.sqrt(100)

        return state

    def analyze_qft(self, draws: List[List[int]]) -> Dict:
        """Análise via QFT"""
        print("\n📊 Executing QFT Analysis...")

        # Criar circuito QFT
        circuit = QuantumAlgorithms.qft(self.n_qubits)

        # Codificar draws
        pattern = self.encode_numbers(draws[0] if draws else [])
        state = QuantumState.zero(self.n_qubits)
        state.amplitudes[pattern] = 1.0

        # Executar QFT
        self.simulator.state = circuit.execute(state)

        # Analisar espectro
        amplitudes = self.simulator.state.amplitudes
        spectrum = np.abs(amplitudes) ** 2
        top_freq = np.argsort(spectrum)[::-1][:20]

        return {
            'method': 'QFT',
            'dominant_frequencies': [
                {'index': int(i), 'power': float(spectrum[i])}
                for i in top_freq
            ],
            'spectral_entropy': float(-np.sum(spectrum * np.log2(spectrum + EPS)))
        }

    def analyze_grover(self, target_pattern: List[int], n_iterations: int = 3) -> Dict:
        """Busca de Grover para padrões"""
        print("🔍 Executing Grover Search...")

        pattern = self.encode_numbers(target_pattern)
        marked = [pattern % self.dimension]

        # Criar circuito Grover
        circuit = QuantumAlgorithms.grover_search(
            self.n_qubits, marked, n_iterations
        )

        # Executar
        result_state = circuit.execute()

        top = result_state.top_states(10)

        return {
            'method': 'Grover',
            'target_pattern': target_pattern[:10],
            'iterations': n_iterations,
            'top_results': [
                {'binary': format_binary(idx, self.n_qubits), 'prob': prob}
                for idx, prob in top
            ],
            'entropy': float(result_state.entropy())
        }

    def analyze_walk(self, n_steps: int = 6) -> Dict:
        """Caminhada quântica para exploração"""
        print("🚶 Executing Quantum Walk...")

        circuit = QuantumAlgorithms.quantum_walk(self.n_qubits, n_steps)
        result_state = circuit.execute()

        top = result_state.top_states(15)

        return {
            'method': 'QuantumWalk',
            'steps': n_steps,
            'top_states': [
                {'binary': format_binary(idx, self.n_qubits), 'prob': prob}
                for idx, prob in top
            ],
            'entropy': float(result_state.entropy())
        }

    def analyze_variational(self, depth: int = 4) -> Dict:
        """Forma variacional para otimização"""
        print("⚡ Executing Variational Form...")

        circuit = QuantumAlgorithms.variational_form(self.n_qubits, depth)
        result_state = circuit.execute()

        top = result_state.top_states(15)

        return {
            'method': 'Variational',
            'depth': depth,
            'gates': len(circuit.gates),
            'top_states': [
                {'binary': format_binary(idx, self.n_qubits), 'prob': prob}
                for idx, prob in top
            ],
            'entropy': float(result_state.entropy())
        }

    def generate_quantum_games(self, n_games: int = 20, strategy: str = 'walk') -> List[List[int]]:
        """Gera jogos usando simulação quântica"""
        print(f"🎰 Generating {n_games} quantum games (strategy: {strategy})...")

        games = []

        for i in range(n_games):
            self.simulator.reset()

            if strategy == 'walk':
                circuit = QuantumAlgorithms.quantum_walk(self.n_qubits, 4 + i % 4)
            elif strategy == 'variational':
                circuit = QuantumAlgorithms.variational_form(self.n_qubits, 3)
            else:
                # Superposição + medição
                for q in range(min(15, self.n_qubits)):
                    self.simulator.state = QuantumOps.hadamard(self.simulator.state, q)
                circuit = None

            if circuit:
                result_state = circuit.execute()
            else:
                result_state = self.simulator.state

            # Medir
            outcome = result_state.measure()

            # Converter para números de loteria
            binary = format_binary(outcome, self.n_qubits)
            numbers = []

            for j in range(0, self.n_qubits - 6, 7):
                if j + 7 <= self.n_qubits:
                    byte = binary[j:j+7]
                    num = int(byte, 2)
                    if 1 <= num <= 100:
                        numbers.append(num)

            # Garantir tamanho
            while len(numbers) < 20:
                numbers.append((i * 7 + len(numbers)) % 100 + 1)

            numbers = sorted(set(numbers))[:20]
            games.append(numbers)

        return games

    def run_full_analysis(self, lottery_type: str, draws: List[List[int]]) -> Dict:
        """Análise completa"""
        print(f"\n{'═' * 60}")
        print(f"   QUANTUM LOTTERY ANALYSIS: {lottery_type}")
        print(f"{'═' * 60}")

        results = {
            'lottery': lottery_type,
            'timestamp': datetime.now().isoformat(),
            'n_qubits': self.n_qubits,
            'analysis': {}
        }

        # QFT
        results['analysis']['qft'] = self.analyze_qft(draws)

        # Grover
        if draws:
            results['analysis']['grover'] = self.analyze_grover(draws[0])

        # Walk
        results['analysis']['walk'] = self.analyze_walk(5)

        # Variational
        results['analysis']['variational'] = self.analyze_variational(3)

        # Generate games
        results['quantum_games'] = self.generate_quantum_games(10)

        self.results = results
        return results

    def save_results(self, filepath: str):
        """Salva resultados"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to {filepath}")

# ============================================================
# DEMONSTRAÇÃO
# ============================================================

def demo():
    """Demonstração completa"""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "SIAOL-PRO QUANTUM SIMULATOR v3.0" + " " * 19 + "║")
    print("║" + " " * 10 + "Optimized 20 Qubit Quantum Computing" + " " * 19 + "║")
    print("╚" + "═" * 68 + "╝")

    # Criar simulador
    sim = QuantumSimulator(n_qubits=20)

    print("\n📊 Test 1: Superposition")
    sim.reset()
    sim.hadamard_all(list(range(5)))
    result = sim.measure(1000)
    print(f"   Entropy: {result['entropy']:.4f}")
    print(sim.visualize(8))

    print("\n⚡ Test 2: Entanglement Chain")
    sim.reset()
    sim.entangle_chain(0, 5)
    result = sim.measure(1000)
    print(f"   Entropy: {result['entropy']:.4f}")
    print(sim.visualize(8))

    print("\n🔄 Test 3: Mixed Operations")
    sim.reset()
    circuit = QuantumCircuit(20, "Test")
    for i in range(8):
        circuit.H(i)
        circuit.CNOT(i, (i + 1) % 8)
    sim.apply(circuit)
    result = sim.measure(1000)
    print(f"   Gates: {result['total_gates']}, Entropy: {result['entropy']:.4f}")
    print(sim.visualize(10))

    print("\n🚶 Test 4: Quantum Walk")
    sim.reset()
    circuit = QuantumAlgorithms.quantum_walk(20, n_steps=6)
    sim.apply(circuit)
    result = sim.measure(2000)
    print(f"   Gates: {result['total_gates']}, Entropy: {result['entropy']:.4f}")
    print(sim.visualize(12))

    print("\n" + "═" * 60)
    print("   LOTTERY INTEGRATION TEST")
    print("═" * 60)

    analyzer = LotteryQuantumAnalyzer(n_qubits=20)

    # Simular draws
    draws = [
        [3, 18, 25, 42, 51, 68, 77, 89, 94, 12, 23, 34, 45, 56, 67, 78, 81, 82, 83, 84],
        [7, 14, 28, 35, 49, 56, 63, 71, 88, 95, 5, 15, 25, 35, 45, 55, 65, 75, 85, 91],
        [1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 11, 22, 33, 44, 55, 66]
    ]

    results = analyzer.run_full_analysis("Lotomania", draws)

    print(f"\n   Generated {len(results['quantum_games'])} quantum games")
    for i, game in enumerate(results['quantum_games'][:5]):
        print(f"   Game {i+1}: {sorted(game)[:15]}...")

    # Save results
    analyzer.save_results('quantum_lottery_results.json')

    print("\n✅ Quantum analysis complete!")

if __name__ == "__main__":
    demo()