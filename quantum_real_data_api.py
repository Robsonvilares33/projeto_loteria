#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           SIAOL-PRO REAL-TIME API INTEGRATION v1.0                         ║
║                                                                              ║
║  Busca dados REAIS de todas as loterias da Caixa:                           ║
║  • Mega-Sena, Lotofácil, Quina, Lotomania                                   ║
║  • Timemania, Dia de Sorte, +Milionária                                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from collections import Counter
import os

# ============================================================
# API CONFIGURATION
# ============================================================

CAIXA_API_BASE = "https://loterias.caixa.gov.br/"

LOTTERIES = {
    "megasena": {
        "name": "Mega-Sena",
        "url": "https://loterias.caixa.gov.br/api/max MegaSena",
        "numbers": 6,
        "range": (1, 60),
        "color": "🟢"
    },
    "lotofacil": {
        "name": "Lotofácil",
        "url": "https://loterias.caixa.gov.br/api/max Lotofacil",
        "numbers": 15,
        "range": (1, 25),
        "color": "🩷"
    },
    "quina": {
        "name": "Quina",
        "url": "https://loterias.caixa.gov.br/api/max Quina",
        "numbers": 5,
        "range": (1, 80),
        "color": "💙"
    },
    "lotomania": {
        "name": "Lotomania",
        "url": "https://loterias.caixa.gov.br/api/max Lotomania",
        "numbers": 50,
        "range": (0, 99),
        "color": "🟣"
    },
    "timemania": {
        "name": "Timemania",
        "url": "https://loterias.caixa.gov.br/api/max Timemania",
        "numbers": 7,
        "range": (1, 80),
        "color": "⚽"
    },
    "diadesorte": {
        "name": "Dia de Sorte",
        "url": "https://loterias.caixa.gov.br/api/max Diadesorte",
        "numbers": 7,
        "range": (1, 31),
        "color": "☀️"
    },
    "maismilionaria": {
        "name": "+Milionária",
        "url": "https://loterias.caixa.gov.br/api/max Maismilionaria",
        "numbers": 6,
        "range": (1, 50),
        "treasures": 2,
        "treasure_range": (1, 6),
        "color": "💰"
    }
}

# ============================================================
# API CLIENT
# ============================================================

class CaixaAPI:
    """Cliente para API da Caixa"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })

    def fetch_lottery(self, lottery_key: str) -> dict:
        """Busca dados de uma loteria específica"""
        info = LOTTERIES.get(lottery_key)
        if not info:
            return {"error": f"Lottery {lottery_key} not found"}

        try:
            response = self.session.get(info["url"], timeout=10)
            response.raise_for_status()
            data = response.json()

            # Parse response
            result = {
                "lottery": lottery_key,
                "name": info["name"],
                "color": info["color"],
                "timestamp": datetime.now().isoformat(),
                "latest_draw": None,
                "historical_draws": []
            }

            # Extract latest draw
            if data and isinstance(data, (dict, list)):
                if isinstance(data, list):
                    data = data[0] if data else {}

                result["latest_draw"] = self._parse_draw(data, lottery_key)

            return result

        except requests.RequestException as e:
            return {
                "lottery": lottery_key,
                "error": str(e),
                "fallback": True
            }

    def _parse_draw(self, data: dict, lottery_key: str) -> dict:
        """Parse draw data from API response"""
        info = LOTTERIES[lottery_key]

        draw = {
            "contest": data.get("concurso", 0),
            "date": data.get("data", ""),
            "numbers": data.get("listaNumeros", []),
        }

        # Add treasures for +Milionária
        if lottery_key == "maismilionaria":
            draw["treasures"] = data.get("listaTrevos", [])

        return draw

    def fetch_all(self) -> dict:
        """Busca dados de todas as loterias"""
        print("\n" + "═" * 70)
        print("   FETCHING ALL LOTTERY DATA FROM CAIXA API")
        print("═" * 70 + "\n")

        results = {}
        for key, info in LOTTERIES.items():
            print(f"   {info['color']} {info['name']}...", end=" ")
            result = self.fetch_lottery(key)

            if result.get("latest_draw"):
                contest = result["latest_draw"].get("contest", 0)
                print(f"✅ Concurso {contest}")
            elif result.get("error"):
                print(f"⚠️ {result['error'][:30]}")
            else:
                print("❌ No data")

            results[key] = result

        return results

    def fetch_historical(self, lottery_key: str, n_draws: int = 20) -> list:
        """Busca últimos N concursos de uma loteria"""
        info = LOTTERIES.get(lottery_key)
        if not info:
            return []

        draws = []

        try:
            # Get latest contest number
            latest = self.fetch_lottery(lottery_key)
            if not latest.get("latest_draw"):
                return []

            latest_contest = latest["latest_draw"]["contest"]

            # Fetch previous draws
            for i in range(n_draws):
                contest = latest_contest - i
                url = f"https://loterias.caixa.gov.br/api/resultados/loteria/{lottery_key}/concurso/{contest}"

                try:
                    response = self.session.get(url, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            draw = self._parse_draw(data, lottery_key)
                            draw["contest"] = contest
                            draws.append(draw)
                except:
                    continue

        except Exception as e:
            print(f"Error fetching historical: {e}")

        return draws


# ============================================================
# LOTTERY ANALYZER
# ============================================================

class LotteryDataAnalyzer:
    """Analisa dados históricos de loterias"""

    def __init__(self, draws: list, lottery_key: str):
        self.draws = draws
        self.lottery_key = lottery_key
        self.info = LOTTERIES.get(lottery_key, {})

    def analyze_frequency(self) -> dict:
        """Análise de frequência dos números"""
        all_numbers = []
        for draw in self.draws:
            all_numbers.extend(draw.get("numbers", []))

        if not all_numbers:
            return {}

        freq = Counter(all_numbers)
        total = len(all_numbers)

        # Hot numbers (top 20)
        hot = [n for n, _ in freq.most_common(20)]

        # Cold numbers (bottom 10)
        cold = [n for n, _ in freq.most_common()[-10:]]

        # Weighted scores
        max_freq = max(freq.values()) if freq else 1
        weights = {n: c / max_freq for n, c in freq.items()}

        return {
            "hot_numbers": hot,
            "cold_numbers": cold,
            "weights": weights,
            "total_draws": len(self.draws),
            "total_numbers": len(all_numbers),
            "unique_numbers": len(freq)
        }

    def analyze_dezenas(self) -> dict:
        """Análise por dezenas (1-10, 11-20, etc.)"""
        dezenas = {}
        info = self.info

        for draw in self.draws:
            for num in draw.get("numbers", []):
                # Calculate dezena
                if "range" in info:
                    min_val, max_val = info["range"]
                    dezena = (num - min_val) // ((max_val - min_val + 9) // 10)
                else:
                    dezena = (num - 1) // 10

                dezenas[dezena] = dezenas.get(dezena, 0) + 1

        return dezenas

    def get_summary(self) -> dict:
        """Resumo completo da análise"""
        freq = self.analyze_frequency()
        dezenas = self.analyze_dezenas()

        return {
            "lottery": self.lottery_key,
            "name": self.info.get("name", ""),
            "color": self.info.get("color", ""),
            "total_draws": len(self.draws),
            "frequency_analysis": freq,
            "dezenas_analysis": dezenas,
            "hot_numbers": freq.get("hot_numbers", [])[:15],
            "cold_numbers": freq.get("cold_numbers", [])
        }


# ============================================================
# QUANTUM DATA INTEGRATOR
# ============================================================

class QuantumDataIntegrator:
    """Integra dados da API com sistema quântico"""

    def __init__(self):
        self.api = CaixaAPI()
        self.results = {}

    def fetch_and_analyze_all(self) -> dict:
        """Busca e analisa todas as loterias"""
        print("\n" + "╔" + "═" * 68 + "╗")
        print("║" + " " * 15 + "SIAOL-PRO QUANTUM + REAL DATA" + " " * 17 + "║")
        print("╚" + "═" * 68 + "╝")

        # Fetch all lotteries
        all_data = self.api.fetch_all()

        # Analyze each
        analyses = {}
        for key, data in all_data.items():
            if data.get("latest_draw") and data.get("error") is None:
                # Get historical draws
                hist = self.api.fetch_historical(key, 20)

                if hist:
                    analyzer = LotteryDataAnalyzer(hist, key)
                    analyses[key] = analyzer.get_summary()

        self.results = analyses
        return analyses

    def generate_quantum_games_for_lottery(self, lottery_key: str, n_games: int = 33) -> list:
        """Gera jogos quânticos para uma loteria específica"""
        if lottery_key not in self.results:
            return []

        analysis = self.results[lottery_key]
        hot = analysis.get("hot_numbers", [])[:15]
        dezenas = analysis.get("dezenas_analysis", {})

        info = LOTTERIES.get(lottery_key, {})
        n_numbers = info.get("numbers", 15)

        # Import quantum simulator
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        try:
            from quantum_simulator_20_qubits import (
                QuantumSimulator, QuantumAlgorithms, QuantumOps
            )
        except ImportError:
            # Fallback if quantum simulator not available
            return self._generate_fallback_games(hot, n_numbers, n_games)

        games = []
        strategies = ['walk', 'variational', 'entangle']

        for i in range(n_games):
            sim = QuantumSimulator(15)

            # Choose strategy
            strategy = strategies[i % 3]

            if strategy == 'walk':
                circuit = QuantumAlgorithms.quantum_walk(15, 4 + i % 3)
            elif strategy == 'variational':
                circuit = QuantumAlgorithms.variational_form(15, 2)
            else:
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

            # Convert to lottery numbers
            numbers = self._convert_to_lottery(outcome, n_numbers, hot, info)

            games.append({
                "id": i + 1,
                "strategy": strategy,
                "numbers": numbers
            })

        return games

    def _convert_to_lottery(self, outcome: int, n_numbers: int, hot: list, info: dict) -> list:
        """Converte resultado quântico para números da loteria"""
        min_val, max_val = info.get("range", (1, 100))
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

    def _generate_fallback_games(self, hot: list, n_numbers: int, n_games: int) -> list:
        """Fallback se quantum simulator não disponível"""
        import random
        games = []

        for i in range(n_games):
            numbers = hot[:n_numbers].copy()

            while len(numbers) < n_numbers:
                n = random.randint(1, 100)
                if n not in numbers:
                    numbers.append(n)

            games.append({
                "id": i + 1,
                "strategy": "hot_fallback",
                "numbers": sorted(numbers)[:n_numbers]
            })

        return games


# ============================================================
# MAIN
# ============================================================

def main():
    print("\n" + "═" * 70)
    print("   SIAOL-PRO REAL-TIME DATA INTEGRATION")
    print("   Fetching from Caixa API - All Lotteries")
    print("═" * 70)

    integrator = QuantumDataIntegrator()

    # Fetch and analyze all lotteries
    analyses = integrator.fetch_and_analyze_all()

    # Display results
    print("\n" + "═" * 70)
    print("   ANALYSIS RESULTS")
    print("═" * 70)

    for key, analysis in analyses.items():
        info = analysis.get("color", "⚪")
        name = analysis.get("name", key)
        draws = analysis.get("total_draws", 0)
        hot = analysis.get("hot_numbers", [])[:10]

        print(f"\n   {info} {name} ({draws} concursos)")
        print(f"      🔥 Hot: {hot}")

    # Generate quantum games for each lottery
    print("\n" + "═" * 70)
    print("   GENERATING QUANTUM GAMES")
    print("═" * 70)

    all_games = {}
    for key in analyses.keys():
        info = LOTTERIES.get(key, {})
        print(f"\n   {info.get('color', '⚪')} {info.get('name', key)}...")

        games = integrator.generate_quantum_games_for_lottery(key, 11)
        all_games[key] = games
        print(f"      ✅ {len(games)} jogos gerados")

    # Save results
    os.makedirs('output', exist_ok=True)
    os.makedirs('memory', exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {
        "timestamp": datetime.now().isoformat(),
        "lotteries": analyses,
        "quantum_games": all_games
    }

    output_file = f'output/real_data_integration_{timestamp}.json'
    memory_file = 'memory/real_data_latest.json'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    with open(memory_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Summary
    print("\n" + "═" * 70)
    print("   SUMMARY")
    print("═" * 70)
    print(f"\n   📊 Lotteries analyzed: {len(analyses)}")
    print(f"   🎰 Games generated: {sum(len(g) for g in all_games.values())}")
    print(f"   💾 Output: {output_file}")

    print("\n✅ Real-Time Data Integration Complete!")

    return results


if __name__ == "__main__":
    main()