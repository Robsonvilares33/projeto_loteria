#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           SIAOL-PRO QUANTUM SIMULATOR v4.0 - ENHANCED                       ║
║                                                                              ║
║  Melhorias:                                                                  ║
║  • Probabilidades não-uniformes (bias para patterns de loteria)             ║
║  • Integração com dados históricos                                           ║
║  • Conversão otimizada de bits para números de aposta                        ║
║  • Performance otimizada para 20 qubits                                      ║
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
    QuantumSimulator, QuantumCircuit, QuantumAlgorithms, QuantumOps, QuantumState
)

def format_binary(idx: int, n_qubits: int) -> str:
    return format(idx, f'0{n_qubits}b')

# ============================================================
# LOTTERY DATA INTEGRATOR
# ============================================================

class LotteryDataIntegrator:
    """Integra dados históricos para bias quântico"""

    def __init__(self):
        self.lottery_weights = {}
        self.hot_numbers = {}
        self.patterns = {}

    def load_historical_data(self, draws: list) -> dict:
        """Analisa dados históricos e extrai patterns"""
        if not draws:
            return {}

        all_numbers = []
        for draw in draws:
            all_numbers.extend(draw)

        # Frequência dos números
        freq = Counter(all_numbers)
        total = sum(freq.values())

        # Normalizar pesos (números mais frequentes = maior peso)
        max_freq = max(freq.values()) if freq else 1
        weights = {}
        for num, count in freq.items():
            weights[num] = count / max_freq

        self.lottery_weights = weights
        self.hot_numbers = [k for k, v in sorted(weights.items(), key=lambda x: -x[1])[:20]]

        # Extrair patterns de dezenas
        dezenas = {}
        for draw in draws:
            for num in draw:
                dezena = (num - 1) // 10
                dezenas[dezena] = dezenas.get(dezena, 0) + 1

        self.patterns = dezenas

        return {
            "hot_numbers": self.hot_numbers,
            "weights": weights,
            "dezenas": self.patterns
        }

    def get_number_weight(self, num: int) -> float:
        """Retorna peso de um número baseado em histórico"""
        return self.lottery_weights.get(num, 0.5)


# ============================================================
# BIASED QUANTUM STATE
# ============================================================

class BiasedQuantumState(QuantumState):
    """Estado quântico com bias para patterns de loteria"""

    @staticmethod
    def from_lottery_bias(n_qubits: int, integrator: LotteryDataIntegrator) -> 'BiasedQuantumState':
        """Cria estado com bias baseado em dados históricos"""
        dim = 2 ** n_qubits
        amps = np.ones(dim, dtype=np.complex128) * (1.0 / np.sqrt(dim))

        # Aplicar bias baseado em números quentes
        hot = integrator.hot_numbers[:10]
        for i in range(dim):
            # Verificar se o estado contém números quentes
            binary = format_binary(i, n_qubits)
            score = 0.0

            for j in range(0, n_qubits - 6, 7):
                if j + 7 <= n_qubits:
                    num = int(binary[j:j+7], 2)
                    if 1 <= num <= 100:
                        score += integrator.get_number_weight(num)

            # Aumentar amplitude de estados com números quentes
            bias = 1.0 + score * 0.5
            amps[i] *= np.sqrt(bias)

        # Normalizar
        norm = np.sqrt(np.sum(np.abs(amps) ** 2))
        amps = amps / norm

        return BiasedQuantumState(n_qubits, amps)


# ============================================================
# ENHANCED QUANTUM OPERATIONS
# ============================================================

class EnhancedQuantumOps:
    """Operações quânticas melhoradas com bias"""

    @staticmethod
    def hadamard_with_bias(state: QuantumState, qubit: int, bias_strength: float = 0.1) -> QuantumState:
        """Hadamard com bias leve para estados preferido"""
        dim = 2 ** state.n_qubits
        new_amps = np.zeros(dim, dtype=np.complex128)
        factor = 1.0 / np.sqrt(2)

        for i in range(dim):
            amp = state.amplitudes[i]
            bit = (i >> qubit) & 1
            i0 = i & ~(1 << qubit)
            i1 = i | (1 << qubit)

            # Aplicar bias
            bias = 1.0 + bias_strength if bit == 0 else 1.0 - bias_strength

            if bit == 0:
                new_amps[i0] += amp * factor * np.sqrt(bias)
                new_amps[i1] += amp * factor / np.sqrt(bias)
            else:
                new_amps[i0] += amp * factor / np.sqrt(bias)
                new_amps[i1] -= amp * factor * np.sqrt(bias)

        return QuantumState(state.n_qubits, new_amps)

    @staticmethod
    def rotation_with_lottery_bias(state: QuantumState, qubit: int, theta: float,
                                   hot_numbers: list) -> QuantumState:
        """Rotação com bias para números quentes"""
        dim = 2 ** state.n_qubits
        new_amps = np.zeros(dim, dtype=np.complex128)
        cos = np.cos(theta / 2)
        sin = np.sin(theta / 2)

        for i in range(dim):
            amp = state.amplitudes[i]
            bit = (i >> qubit) & 1
            i0 = i & ~(1 << qubit)
            i1 = i | (1 << qubit)

            # Verificar se estado contém números quentes
            binary = format_binary(i, state.n_qubits)
            bias_factor = 1.0

            for j in range(0, state.n_qubits - 6, 7):
                if j + 7 <= state.n_qubits:
                    num = int(binary[j:j+7], 2)
                    if num in hot_numbers[:10]:
                        bias_factor *= 1.2

            if bit == 0:
                new_amps[i0] += amp * cos
                new_amps[i1] += amp * sin * bias_factor
            else:
                new_amps[i0] += amp * sin / bias_factor
                new_amps[i1] -= amp * cos

        return QuantumState(state.n_qubits, new_amps)


# ============================================================
# ENHANCED QUANTUM ANALYZER
# ============================================================

class EnhancedQuantumAnalyzer:
    """Analisador quântico melhorado com integração de loteria"""

    def __init__(self, n_qubits: int = 20):
        self.n_qubits = n_qubits
        self.simulator = QuantumSimulator(n_qubits)
        self.integrator = LotteryDataIntegrator()
        self.results = {}

    def analyze_with_lottery_data(self, draws: list, strategy: str = 'biased_walk') -> dict:
        """Análise quântica com bias baseado em dados históricos"""
        print(f"\n📊 Analyzing with {len(draws)} historical draws...")

        # Carregar dados históricos
        data_info = self.integrator.load_historical_data(draws)
        print(f"   Hot numbers: {data_info.get('hot_numbers', [])[:10]}")
        print(f"   Patterns: {len(data_info.get('patterns', {}))} dezenas")

        results = {
            "strategy": strategy,
            "data_info": data_info,
            "games": []
        }

        # Escolher estratégia
        if strategy == 'biased_walk':
            results["games"] = self._biased_quantum_walk(data_info)
        elif strategy == 'pattern_search':
            results["games"] = self._pattern_based_search(data_info)
        elif strategy == 'entanglement_boost':
            results["games"] = self._entanglement_boost(data_info)
        else:
            results["games"] = self._standard_quantum_games(data_info)

        self.results = results
        return results

    def _biased_quantum_walk(self, data_info: dict) -> list:
        """Quantum Walk com bias de loteria"""
        print("\n🚶 Executing Biased Quantum Walk...")
        games = []
        hot = data_info.get('hot_numbers', [])[:10]

        for i in range(33):
            sim = QuantumSimulator(self.n_qubits)

            # Estado inicial com bias
            if i == 0:
                state = BiasedQuantumState.from_lottery_bias(self.n_qubits, self.integrator)
                sim.state = state

            # Quantum walk com rotações biasadas
            steps = 3 + (i % 4)
            for step in range(steps):
                for q in range(self.n_qubits):
                    sim.state = QuantumOps.hadamard(sim.state, q)

                    # Aplicar rotação com bias
                    angle = np.pi / (2 ** (step + 1))
                    sim.state = EnhancedQuantumOps.rotation_with_lottery_bias(
                        sim.state, q, angle, hot
                    )

                # CNOT chain para emaranhamento
                for q in range(self.n_qubits - 1):
                    sim.state = QuantumOps.cnot(sim.state, q, q + 1)

            # Medir
            outcome = sim.state.measure()
            numbers = self._convert_to_lottery_numbers(outcome, size=15)

            games.append({
                "id": i + 1,
                "strategy": "biased_walk",
                "numbers": numbers
            })

            if i < 5:
                print(f"   Game {i+1}: {numbers[:10]}...")

        return games

    def _pattern_based_search(self, data_info: dict) -> list:
        """Busca baseada em patterns de dezenas"""
        print("\n🔍 Executing Pattern-Based Search...")
        games = []
        dezenas = data_info.get('patterns', {})

        for i in range(33):
            sim = QuantumSimulator(self.n_qubits)

            # Criar estado com bias de dezenas
            dim = 2 ** self.n_qubits
            amps = np.ones(dim, dtype=np.complex128) / np.sqrt(dim)

            # Bias baseado em dezenas
            for idx in range(dim):
                binary = format_binary(idx, self.n_qubits)
                dezena_score = 0

                for j in range(0, self.n_qubits - 6, 7):
                    if j + 7 <= self.n_qubits:
                        num = int(binary[j:j+7], 2)
                        if 1 <= num <= 100:
                            d = (num - 1) // 10
                            dezena_score += dezenas.get(d, 0)

                bias = 1.0 + dezena_score * 0.1
                amps[idx] *= np.sqrt(bias)

            # Normalizar
            norm = np.sqrt(np.sum(np.abs(amps) ** 2))
            amps = amps / norm

            sim.state = QuantumState(self.n_qubits, amps)

            # Operações quânticas
            for q in range(self.n_qubits):
                sim.state = EnhancedQuantumOps.hadamard_with_bias(sim.state, q, 0.15)

            for q in range(self.n_qubits - 1):
                sim.state = QuantumOps.cnot(sim.state, q, q + 1)

            # Medir
            outcome = sim.state.measure()
            numbers = self._convert_to_lottery_numbers(outcome, size=15)

            games.append({
                "id": i + 1,
                "strategy": "pattern_search",
                "numbers": numbers
            })

        return games

    def _entanglement_boost(self, data_info: dict) -> list:
        """Entanglement boost para explorar correlações"""
        print("\n🔗 Executing Entanglement Boost...")
        games = []
        hot = data_info.get('hot_numbers', [])[:15]

        for i in range(33):
            sim = QuantumSimulator(self.n_qubits)

            # Hadamard em todos
            for q in range(self.n_qubits):
                sim.state = EnhancedQuantumOps.hadamard_with_bias(sim.state, q, 0.2)

            # Entanglement com bias
            for q in range(self.n_qubits - 1):
                sim.state = QuantumOps.cnot(sim.state, q, q + 1)

            # CZ entre qubits distantes
            for q in range(0, self.n_qubits - 3, 4):
                sim.state = QuantumOps.cz(sim.state, q, q + 3)

            # Medir
            outcome = sim.state.measure()
            numbers = self._convert_to_lottery_numbers(outcome, size=15)

            games.append({
                "id": i + 1,
                "strategy": "entanglement_boost",
                "numbers": numbers
            })

        return games

    def _standard_quantum_games(self, data_info: dict) -> list:
        """Jogos quânticos padrão (fallback)"""
        print("\n⚡ Executing Standard Quantum Games...")
        games = []

        for i in range(33):
            sim = QuantumSimulator(self.n_qubits)
            circuit = QuantumAlgorithms.quantum_walk(self.n_qubits, 4)
            sim.apply(circuit)

            outcome = sim.state.measure()
            numbers = self._convert_to_lottery_numbers(outcome, size=15)

            games.append({
                "id": i + 1,
                "strategy": "standard",
                "numbers": numbers
            })

        return games

    def _convert_to_lottery_numbers(self, outcome: int, size: int = 15) -> list:
        """Conversão otimizada de bits para números de aposta"""
        binary = format_binary(outcome, self.n_qubits)
        numbers = []

        # Extrair números dos bits
        for j in range(0, self.n_qubits - 6, 7):
            if j + 7 <= self.n_qubits:
                num = int(binary[j:j+7], 2)
                if 1 <= num <= 100:
                    numbers.append(num)

        # Garantir tamanho válido
        while len(numbers) < size:
            numbers.append((outcome + len(numbers)) % 100 + 1)

        # Remover duplicatas e limitar
        numbers = sorted(set(numbers))[:size]

        # Preencher se necessário
        hot = self.integrator.hot_numbers
        for num in hot:
            if len(numbers) >= size:
                break
            if num not in numbers:
                numbers.append(num)

        numbers = sorted(numbers)[:size]

        # Garantir exatamente 'size' números
        while len(numbers) < size:
            n = (numbers[-1] % 100) + 1
            if n not in numbers:
                numbers.append(n)
            else:
                numbers.append((numbers[-1] + 7) % 100 + 1)
            numbers = sorted(set(numbers))

        return numbers

    def run_comparison(self, draws: list) -> dict:
        """Executa todas as estratégias e compara"""
        print("\n" + "=" * 60)
        print("   STRATEGY COMPARISON")
        print("=" * 60)

        strategies = ['biased_walk', 'pattern_search', 'entanglement_boost']
        results = {}

        for strategy in strategies:
            print(f"\n📊 Testing: {strategy}")
            res = self.analyze_with_lottery_data(draws, strategy)

            # Calcular diversidade
            all_nums = []
            for game in res["games"]:
                all_nums.extend(game["numbers"])
            diversity = len(set(all_nums)) / (len(res["games"]) * 15)

            results[strategy] = {
                "games_count": len(res["games"]),
                "diversity": diversity,
                "hot_number_coverage": self._calc_hot_coverage(res["games"])
            }

            print(f"   Diversity: {diversity:.2%}")
            print(f"   Hot coverage: {results[strategy]['hot_number_coverage']:.2%}")

        return results


    def _calc_hot_coverage(self, games: list) -> float:
        """Calcula cobertura de números quentes"""
        hot = set(self.integrator.hot_numbers[:20])
        covered = set()

        for game in games:
            covered.update(game["numbers"])

        if not hot:
            return 0.0

        return len(hot.intersection(covered)) / len(hot)


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 12 + "SIAOL-PRO QUANTUM v4.0 - ENHANCED" + " " * 16 + "║")
    print("║" + " " * 10 + "Probabilidades não-uniformes + Dados históricos" + " " * 6 + "║")
    print("╚" + "═" * 68 + "╝")

    os.makedirs('output', exist_ok=True)
    os.makedirs('memory', exist_ok=True)

    # Carregar dados históricos (simular draws)
    print("\n📂 Loading historical lottery data...")
    # Simulando draws históricos (substituir com dados reais)
    sample_draws = [
        [3, 11, 17, 22, 25, 33, 41, 48, 52, 58, 64, 71, 78, 82, 89],
        [5, 12, 18, 23, 27, 34, 42, 49, 53, 59, 65, 72, 79, 83, 90],
        [7, 14, 19, 24, 28, 35, 43, 50, 54, 60, 66, 73, 80, 84, 91],
        [2, 10, 16, 21, 26, 32, 40, 47, 51, 57, 63, 70, 77, 81, 88],
        [9, 15, 20, 25, 29, 36, 44, 51, 55, 61, 67, 74, 81, 85, 92],
    ]

    analyzer = EnhancedQuantumAnalyzer(n_qubits=20)

    # Executar comparação de estratégias
    comparison = analyzer.run_comparison(sample_draws)

    # Executar estratégia final
    print("\n" + "=" * 60)
    print("   FINAL GAMES (Biased Walk Strategy)")
    print("=" * 60)

    final_results = analyzer.analyze_with_lottery_data(sample_draws, 'biased_walk')

    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'output/quantum_enhanced_{timestamp}.json'
    memory_file = 'memory/quantum_enhanced_latest.json'

    full_results = {
        "timestamp": timestamp,
        "comparison": comparison,
        "final_games": final_results["games"]
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_results, f, indent=2, ensure_ascii=False)

    with open(memory_file, 'w', encoding='utf-8') as f:
        json.dump(full_results, f, indent=2, ensure_ascii=False)

    # Resumo
    print("\n" + "═" * 60)
    print("   SUMMARY")
    print("═" * 60)

    print("\n   Strategy Comparison:")
    for strategy, stats in comparison.items():
        print(f"   • {strategy}:")
        print(f"     - Diversity: {stats['diversity']:.2%}")
        print(f"     - Hot coverage: {stats['hot_number_coverage']:.2%}")

    print(f"\n   Total games generated: {len(final_results['games'])}")
    print(f"   Output: {output_file}")

    print("\n✅ Enhanced Quantum Analysis Complete!")

    return full_results


if __name__ == "__main__":
    results = main()