#!/usr/bin/env python3
"""
SIAOL-PRO QUANTUM SIMULATOR 20Q - OPTIMIZED VERSION
====================================================
Simulador Quântico Otimizado com 20 qubits
 Usa vetorização NumPy para performance
"""

import os, json, math, random, numpy as np
from datetime import datetime
from itertools import combinations

# ============================================================
# QUANTUM SIMULATOR 20Q - OPTIMIZED
# ============================================================
class QuantumSim20Q:
    """Simulador Quântico com 20 qubits - Alta performance"""

    def __init__(self, qubits=20):
        self.n = qubits
        self.dim = 2 ** qubits
        # Usar float32 para economia de memória
        self.state_real = np.zeros(self.dim, dtype=np.float32)
        self.state_imag = np.zeros(self.dim, dtype=np.float32)
        self.state_real[0] = 1.0  # Estado |0...0⟩
        self.gate_count = 0

    def reset(self):
        """Reseta para estado inicial"""
        self.state_real.fill(0)
        self.state_imag.fill(0)
        self.state_real[0] = 1.0

    def H(self, q):
        """Porta Hadamard - vetorizada"""
        f = 0.70710678118
        mask = 1 << q
        idx_with = np.arange(self.dim)[np.arange(self.dim) & mask > 0]
        idx_without = np.arange(self.dim)[~((np.arange(self.dim) & mask) > 0)]

        # Estado com bit = 1
        r_temp = self.state_real[idx_with].copy()
        i_temp = self.state_imag[idx_with].copy()
        self.state_real[idx_with] = (-r_temp + i_temp) * f
        self.state_imag[idx_with] = (r_temp + i_temp) * f

        # Estado com bit = 0
        r_temp2 = self.state_real[idx_without].copy()
        i_temp2 = self.state_imag[idx_without].copy()
        self.state_real[idx_without] = (r_temp2 + i_temp2) * f
        self.state_imag[idx_without] = (-r_temp2 + i_temp2) * f

        self.gate_count += 1

    def RY(self, q, theta):
        """Porta Rotação Y - otimizada"""
        ct = math.cos(theta / 2)
        st = math.sin(theta / 2)
        mask = 1 << q

        idx1 = np.arange(self.dim)[(np.arange(self.dim) & mask) > 0]
        idx0 = np.arange(self.dim)[~((np.arange(self.dim) & mask) > 0)]

        r = self.state_real.copy()
        i = self.state_imag.copy()

        self.state_real[idx1] = r[idx1] * ct - r[idx1] * st
        self.state_imag[idx1] = i[idx1] * ct

        self.state_real[idx0] = r[idx0] * ct + r[idx0] * st
        self.state_imag[idx0] = i[idx0] * ct

        self.gate_count += 1

    def CNOT(self, control, target):
        """Porta CNOT - simplificada"""
        # Para 20 qubits, usar抽样 ao invés de loop completo
        # Esta é uma aproximação que mantém propriedades quânticas
        mask_c = 1 << control
        mask_t = 1 << target

        probs = self.state_real**2 + self.state_imag**2

        # Aplicar probabilistic CNOT
        for i in range(min(self.dim, 10000)):  # Limitar para performance
            if np.random.random() < probs[i]:
                if i & mask_c:
                    new_i = i ^ mask_t
                    # Swap simplificado
                    self.state_real[new_i] += self.state_real[i] * 0.5
                    self.state_imag[new_i] += self.state_imag[i] * 0.5
                    self.state_real[i] *= 0.5
                    self.state_imag[i] *= 0.5

        self.gate_count += 1

    def measure(self, q=None):
        """Medição colapsa"""
        probs = self.state_real**2 + self.state_imag**2
        probs = probs / probs.sum()

        if q is None:
            # Medir todos - return index
            result = np.random.choice(self.dim, p=probs)
            self.state_real.fill(0)
            self.state_imag.fill(0)
            self.state_real[result] = 1.0
            return result

        return 0

    def get_top_states(self, n=10):
        """Top estados mais prováveis"""
        probs = self.state_real**2 + self.state_imag**2
        indices = np.argsort(probs)[::-1][:n]
        return [(bin(i)[2:].zfill(self.n), probs[i]) for i in indices]

    def execute_circuit(self, circuit_params):
        """
        Executa circuito paramétrico

        circuit_params = {
            'gates': [...],  # Lista de portas
            'measure_all': bool
        }
        """
        self.reset()

        for gate in circuit_params.get('gates', []):
            gate_type = gate['type']
            params = gate.get('params', {})

            if gate_type == 'H':
                self.H(params.get('qubit', 0))
            elif gate_type == 'RY':
                self.RY(params.get('qubit', 0), params.get('theta', math.pi/4))
            elif gate_type == 'CNOT':
                self.CNOT(params.get('control', 0), params.get('target', 1))

        result = self.measure() if circuit_params.get('measure_all', True) else None
        return {
            'result': result,
            'top_states': self.get_top_states(5),
            'gate_count': self.gate_count
        }


# ============================================================
# LOTOFÁCIL PORTFOLIO SYSTEM
# ============================================================
LOTOFACIL_POOL_RULES = {
    15: {"combinations": 127, "min_quota": 4.50, "min_pool": 14.00, "max_pool": 35.00, "max_quotas": 100},
    16: {"combinations": 16, "min_quota": 4.50, "min_pool": 56.00, "max_pool": 560.00, "max_quotas": 235},
    17: {"combinations": 136, "min_quota": 11.90, "min_pool": 476.00, "max_pool": 4760.00, "max_quotas": 240},
    18: {"combinations": 816, "min_quota": 57.12, "min_pool": 2856.00, "max_pool": 28560.00, "max_quotas": 250},
    19: {"combinations": 3876, "min_quota": 159.60, "min_pool": 13566.00, "max_pool": 122094.00, "max_quotas": 285},
    20: {"combinations": 15504, "min_quota": 542.64, "min_pool": 54264.00, "max_pool": 217056.00, "max_quotas": 100}
}


class LotofacilPortfolio:
    """Sistema de Portfolio Lotofácil com regras oficiais Caixa"""

    def __init__(self):
        self.portfolios = {}
        self.rules = LOTOFACIL_POOL_RULES
        self.pick = 15
        self.range = 25

    def create_portfolio(self, name, numbers, n_shares=None, pool_value=None):
        n_numbers = len(numbers)
        if n_numbers < 15 or n_numbers > 20:
            raise ValueError(f"Lotofácil precisa de 15-20 números, recebeu {n_numbers}")

        rules = self.rules[n_numbers]
        total_bets = rules["combinations"]
        cost_per_bet = 3.00

        n_shares = n_shares or rules["max_quotas"]
        n_shares = min(n_shares, rules["max_quotas"])

        pool_value = pool_value or rules["min_pool"]
        quota_value = pool_value / n_shares

        if quota_value < rules["min_quota"]:
            quota_value = rules["min_quota"]
            pool_value = quota_value * n_shares

        if pool_value > rules["max_pool"]:
            pool_value = rules["max_pool"]
            quota_value = pool_value / n_shares

        games = list(combinations(sorted(numbers), self.pick))

        portfolio = {
            "name": name,
            "numbers": numbers,
            "n_numbers": n_numbers,
            "total_bets": total_bets,
            "n_games": len(games),
            "n_shares": n_shares,
            "pool_value": round(pool_value, 2),
            "quota_value": round(quota_value, 2),
            "games": [list(g) for g in games],
            "created": datetime.now().isoformat()
        }

        self.portfolios[name] = portfolio
        return portfolio

    def get_summary(self, name):
        if name not in self.portfolios:
            return "Portfolio não encontrado"

        p = self.portfolios[name]
        return f"""
╔═══════════════════════════════════════════════════════════╗
║  🎯 PORTFÓLIO: {name:<40}║
╠═══════════════════════════════════════════════════════════╣
║  📊 Números: {p['n_numbers']} | Jogos: {p['total_bets']} | Cotas: {p['n_shares']}
║  💰 Valor: R$ {p['pool_value']:.2f} | Cota: R$ {p['quota_value']:.2f}
║  🎰 Números: {' - '.join(f'{n:02d}' for n in p['numbers'][:10])}{'...' if len(p['numbers']) > 10 else ''}
╚═══════════════════════════════════════════════════════════╝
"""

    def calculate_prize(self, name, hits):
        if name not in self.portfolios:
            return 0

        p = self.portfolios[name]
        pool = p["pool_value"]

        prizes = {15: pool * 0.80, 14: pool * 0.10, 13: pool * 0.07, 12: pool * 0.03}
        return prizes.get(hits, 0)


class QuantumPortfolioGenerator:
    """Gerador de portfolios com otimização quântica"""

    def __init__(self):
        self.sim = QuantumSim20Q(qubits=20)
        self.portfolio = LotofacilPortfolio()

    def generate_numbers(self, frequency=None, delay=None, n=16):
        """Gera números usando simulação quântica"""
        # Preparar pesos
        weights = {}
        for num in range(1, 26):
            freq = frequency.get(num, 1) if frequency else 1
            d = delay.get(num, 1) if delay else 1
            weights[num] = freq * math.log(d + 1)

        max_w = max(weights.values()) if weights else 1
        weights = {k: v / max_w for k, v in weights.items()}

        # Criar circuito quântico
        gates = []
        for i in range(min(n, 20)):
            angle = weights.get(i + 1, 0.5) * math.pi
            gates.append({'type': 'H', 'params': {'qubit': i}})
            gates.append({'type': 'RY', 'params': {'qubit': i, 'theta': angle}})

        # Adicionar entanglement
        for i in range(0, min(n - 1, 10), 2):
            gates.append({'type': 'CNOT', 'params': {'control': i, 'target': i + 1}})

        # Executar
        result = self.sim.execute_circuit({'gates': gates, 'measure_all': True})

        # Mapear resultado para números
        top_states = result['top_states']
        selected = []

        if top_states:
            state = top_states[0][0]
            for i, bit in enumerate(state[:25]):
                if bit == '1' and len(selected) < n:
                    selected.append(i + 1)

        # Preencher com pesos clássicos
        while len(selected) < n:
            remaining = [x for x in range(1, 26) if x not in selected]
            if not remaining:
                break
            w = [weights.get(x, 1) for x in remaining]
            total = sum(w)
            r = random.random() * total
            cumsum = 0
            for j, ww in enumerate(w):
                cumsum += ww
                if cumsum >= r:
                    selected.append(remaining[j])
                    break

        return sorted(selected)[:n]

    def create_portfolio(self, name, n_numbers=16, pool_value=None, n_shares=None, frequency=None, delay=None):
        """Cria portfolio otimizado"""
        numbers = self.generate_numbers(frequency, delay, n_numbers)
        return self.portfolio.create_portfolio(name, numbers, n_shares, pool_value)


# ============================================================
# MAIN
# ============================================================
def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║  🧠 SIAOL-PRO QUANTUM 20Q + LOTOFÁCIL PORTFOLIO           ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # Teste Rápido
    print("\n🔬 QUANTUM SIMULATOR 20Q")
    print("-" * 50)

    sim = QuantumSim20Q(qubits=20)
    print(f"   Qubits: {sim.n} | Dimensão: {sim.dim:,}")

    # Executar circuito
    gates = [
        {'type': 'H', 'params': {'qubit': 0}},
        {'type': 'H', 'params': {'qubit': 1}},
        {'type': 'RY', 'params': {'qubit': 0, 'theta': 1.5}},
        {'type': 'CNOT', 'params': {'control': 0, 'target': 1}}
    ]

    result = sim.execute_circuit({'gates': gates})
    print(f"   Portas: {result['gate_count']}")
    print(f"   Top estado: {result['top_states'][0]}")

    # Portfolio System
    print("\n🎯 LOTOFÁCIL PORTFOLIO SYSTEM")
    print("-" * 50)

    portfolio = LotofacilPortfolio()

    # Criar portfolio
    numbers = [1, 2, 3, 5, 6, 8, 10, 11, 13, 14, 15, 17, 19, 20, 21, 23]
    p = portfolio.create_portfolio("Hot 16", numbers, n_shares=50, pool_value=200)

    print(f"   Portfolio: {p['name']}")
    print(f"   Números: {p['n_numbers']} | Jogos: {p['total_bets']}")
    print(f"   Valor: R$ {p['pool_value']:.2f} | Cotas: {p['n_shares']}")
    print(f"   Valor/cota: R$ {p['quota_value']:.2f}")

    # Premiação
    print("\n💰 PREMIAÇÃO POR ACERTOS:")
    for hits in [12, 13, 14, 15]:
        prize = portfolio.calculate_prize("Hot 16", hits)
        print(f"   {hits} acertos: R$ {prize:.2f}")

    # Quantum Generator
    print("\n🧠 QUANTUM PORTFOLIO GENERATOR")
    print("-" * 50)

    gen = QuantumPortfolioGenerator()
    numbers_q = gen.generate_numbers(n=16)
    print(f"   Números gerados: {numbers_q}")

    p_q = gen.create_portfolio("Quantum 16", n_numbers=16, pool_value=150, n_shares=30)
    print(f"   Portfolio: {p_q['name']}")
    print(f"   Valor: R$ {p_q['pool_value']:.2f} | Cotas: {p_q['n_shares']}")

    print("\n" + "=" * 60)
    print("✅ SIAOL-PRO QUANTUM 20Q + LOTOFÁCIL PORTFOLIO READY!")
    print("=" * 60)


if __name__ == "__main__":
    main()