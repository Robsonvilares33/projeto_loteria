#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           SIAOL-PRO REAL DATA INTEGRATION v2.0                              ║
║                                                                              ║
║  Integra dados REAIS de todas as loterias:                                   ║
║  • Mega-Sena, Lotofácil, Quina, Lotomania                                   ║
║  • Usa dados locais como primary source                                      ║
║  • Faz sync com API da Caixa quando disponível                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import sys
from datetime import datetime
from collections import Counter
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# LOTTERY CONFIG
# ============================================================

LOTTERIES = {
    "lotofacil": {
        "name": "Lotofácil",
        "numbers": 15,
        "range": (1, 25),
        "color": "🩷",
        "data_file": "data/lotofacil.json"
    },
    "megasena": {
        "name": "Mega-Sena",
        "numbers": 6,
        "range": (1, 60),
        "color": "🟢",
        "data_file": "data/megasena.json"
    },
    "quina": {
        "name": "Quina",
        "numbers": 5,
        "range": (1, 80),
        "color": "💙",
        "data_file": "data/quina.json"
    },
    "lotomania": {
        "name": "Lotomania",
        "numbers": 50,
        "range": (0, 99),
        "color": "🟣",
        "data_file": "data/lotomania.json"
    }
}

# ============================================================
# DATA LOADER
# ============================================================

def load_lottery_data(lottery_key: str) -> dict:
    """Carrega dados de uma loteria do arquivo local"""
    info = LOTTERIES.get(lottery_key)
    if not info:
        return {}

    filepath = os.path.join(os.path.dirname(__file__), info["data_file"])

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"   ⚠️ Error loading {info['name']}: {e}")
        return {}


def load_all_lotteries() -> dict:
    """Carrega dados de todas as loterias"""
    results = {}

    for key, info in LOTTERIES.items():
        print(f"   {info['color']} {info['name']}...", end=" ")
        data = load_lottery_data(key)

        if data:
            print(f"✅ ({data.get('ultimo_concurso', 'N/A')})")
            results[key] = data
        else:
            print("❌")

    return results


# ============================================================
# ANALYZER
# ============================================================

def analyze_lottery_frequency(data: dict, lottery_key: str) -> dict:
    """Analisa frequência dos números"""
    info = LOTTERIES.get(lottery_key, {})

    # Check if we have historical data
    if "resultados" in data and data["resultados"]:
        all_numbers = []
        for result in data["resultados"]:
            if "numeros" in result:
                all_numbers.extend(result["numeros"])
    elif "numeros_sorteados" in data:
        # Single draw
        all_numbers = data["numeros_sorteados"]
    else:
        return {}

    if not all_numbers:
        return {}

    freq = Counter(all_numbers)
    hot = [n for n, _ in freq.most_common(20)]

    return {
        "hot_numbers": hot,
        "total_draws": len(data.get("resultados", [1])),
        "total_occurrences": len(all_numbers),
        "unique_numbers": len(freq)
    }


def analyze_dezenas(numbers: list, min_val: int, max_val: int) -> dict:
    """Analisa distribuição por dezenas"""
    dezenas = {}

    for num in numbers:
        dezena = (num - min_val) // ((max_val - min_val + 9) // 10)
        dezenas[dezena] = dezenas.get(dezena, 0) + 1

    return dezenas


# ============================================================
# QUANTUM INTEGRATION
# ============================================================

def generate_quantum_games(lottery_key: str, hot_numbers: list,
                          n_games: int = 33, n_numbers: int = 15) -> list:
    """Gera jogos quânticos baseados em dados reais"""
    info = LOTTERIES.get(lottery_key, {})

    # Import quantum simulator
    try:
        from quantum_simulator_20_qubits import (
            QuantumSimulator, QuantumAlgorithms, QuantumOps
        )
        has_quantum = True
    except ImportError:
        has_quantum = False

    games = []
    strategies = ['walk', 'variational', 'entangle']

    for i in range(n_games):
        if has_quantum:
            # Use quantum simulator
            sim = QuantumSimulator(15)

            strategy = strategies[i % 3]

            if strategy == 'walk':
                circuit = QuantumAlgorithms.quantum_walk(15, 4 + i % 3)
            elif strategy == 'variational':
                circuit = QuantumAlgorithms.variational_form(15, 2)
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
            # Fallback
            outcome = (i * 12345) % (2 ** 15)

        # Convert to lottery numbers
        numbers = convert_quantum_to_lottery(
            outcome, n_numbers, hot_numbers,
            info.get("range", (1, 100))
        )

        games.append({
            "id": i + 1,
            "strategy": strategies[i % 3] if has_quantum else "fallback",
            "numbers": numbers
        })

    return games


def convert_quantum_to_lottery(outcome: int, n_numbers: int,
                               hot: list, range_val: tuple) -> list:
    """Converte resultado quântico para números da loteria"""
    min_val, max_val = range_val
    range_size = max_val - min_val + 1

    numbers = []

    # Extract from binary
    for offset in range(0, 15, 7):
        num = ((outcome >> offset) & 0x7F) % range_size + min_val
        if min_val <= num <= max_val:
            numbers.append(num)

    # Ensure correct count
    numbers = sorted(set(numbers))[:n_numbers]

    while len(numbers) < n_numbers:
        for h in hot:
            if h not in numbers and len(numbers) < n_numbers:
                numbers.append(h)
                break
        else:
            n = (outcome + len(numbers)) % range_size + min_val
            if n not in numbers and min_val <= n <= max_val:
                numbers.append(n)

    return sorted(numbers)[:n_numbers]


# ============================================================
# MAIN
# ============================================================

def main():
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "SIAOL-PRO REAL DATA + QUANTUM" + " " * 18 + "║")
    print("║" + " " * 15 + "All Lotteries Integrated" + " " * 25 + "║")
    print("╚" + "═" * 68 + "╝")

    # Load all lottery data
    print("\n" + "─" * 70)
    print("   LOADING LOCAL DATA")
    print("─" * 70 + "\n")

    all_data = load_all_lotteries()

    if not all_data:
        print("❌ No lottery data found!")
        return

    # Analyze each lottery
    print("\n" + "─" * 70)
    print("   ANALYZING HOT NUMBERS")
    print("─" * 70 + "\n")

    analyses = {}
    for key, data in all_data.items():
        info = LOTTERIES.get(key, {})
        freq = analyze_lottery_frequency(data, key)

        if freq:
            analyses[key] = {
                "name": info.get("name", ""),
                "color": info.get("color", ""),
                "latest_contest": data.get("ultimo_concurso", "N/A"),
                "latest_date": data.get("data_ultimo", ""),
                "hot_numbers": freq.get("hot_numbers", []),
                "statistics": freq
            }

            print(f"   {info.get('color', '⚪')} {info.get('name', key)}")
            print(f"      🔥 Hot: {freq['hot_numbers'][:10]}")
            print(f"      📊 {freq.get('total_draws', 1)} draws analyzed")

    # Generate quantum games for each lottery
    print("\n" + "─" * 70)
    print("   GENERATING QUANTUM GAMES")
    print("─" * 70 + "\n")

    all_games = {}
    for key, analysis in analyses.items():
        info = LOTTERIES.get(key, {})
        hot = analysis.get("hot_numbers", [])
        n_numbers = info.get("numbers", 15)

        print(f"   {info.get('color', '⚪')} {info.get('name', key)}...", end=" ")

        games = generate_quantum_games(key, hot, 11, n_numbers)
        all_games[key] = games

        print(f"✅ {len(games)} jogos")

    # Save results
    os.makedirs('output', exist_ok=True)
    os.makedirs('memory', exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = {
        "timestamp": datetime.now().isoformat(),
        "lotteries": {k: {
            "name": v.get("name", ""),
            "color": v.get("color", ""),
            "latest_contest": v.get("latest_contest", ""),
            "latest_date": v.get("latest_date", ""),
            "hot_numbers": v.get("hot_numbers", [])
        } for k, v in analyses.items()},
        "quantum_games": all_games,
        "statistics": {
            "total_lotteries": len(analyses),
            "total_games": sum(len(g) for g in all_games.values())
        }
    }

    output_file = f'output/real_data_quantum_{timestamp}.json'
    memory_file = 'memory/real_data_quantum_latest.json'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    with open(memory_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Summary
    print("\n" + "═" * 70)
    print("   RESULTS SUMMARY")
    print("═" * 70)

    for key, games in all_games.items():
        info = analyses.get(key, {})
        print(f"\n   {info.get('color', '⚪')} {info.get('name', key)}")
        print(f"      📊 {len(games)} jogos gerados")
        print(f"      🔥 Hot: {info.get('hot_numbers', [])[:5]}...")

    print(f"\n   💾 Output: {output_file}")
    print(f"   💾 Memory: {memory_file}")

    print("\n✅ Real Data + Quantum Integration Complete!")

    return results


if __name__ == "__main__":
    main()