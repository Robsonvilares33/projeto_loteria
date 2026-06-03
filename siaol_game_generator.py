#!/usr/bin/env python3
"""
SIAOL-PRO GAME GENERATOR - Gerador de Jogos Estratégicos
=========================================================
Sistema de geração de jogos com cobertura otimizada

FUNCIONALIDADES:
- Geração baseada em frequência, atraso e co-ocorrência
- Cobertura estratégica (cercado) de números escolhidos
- Portfólios por quantidade de números
- Análise de padrões geométricos
- Sistema de confiança probabilística
"""

import os, json, math, random
from itertools import combinations
from collections import Counter
from datetime import datetime
import sys

# Importar módulos existentes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(PROJECT_DIR, "database")

# ============================================================
# CONFIGURAÇÃO DE LOTERIAS
# ============================================================
LOTTERY_CONFIG = {
    "megasena": {
        "name": "Mega-Sena",
        "range": 60,
        "pick": 6,
        "cost": 5.00,
        "premium_hits": [4, 5, 6],
        "emoji": "🎰",
        "combination_costs": {
            8: 28.00,   # 28 jogos
            9: 84.00,   # 84 jogos
            10: 210.00, # 210 jogos
            11: 462.00, # 462 jogos
            12: 924.00, # 924 jogos
            13: 1716.00,# 1716 jogos
            14: 3003.00,# 3003 jogos
            15: 5005.00 # 5005 jogos
        }
    },
    "lotofacil": {
        "name": "Lotofácil",
        "range": 25,
        "pick": 15,
        "cost": 3.00,
        "premium_hits": [11, 12, 13, 14, 15],
        "emoji": "🎯",
        "combination_costs": {
            16: 16 * 3.00,   # 16 jogos
            17: 136 * 3.00,  # 136 jogos
            18: 816 * 3.00,  # 816 jogos
            19: 3876 * 3.00, # 3876 jogos
            20: 15504 * 3.00,# 15504 jogos
            21: 54264 * 3.00 # 54264 jogos
        }
    },
    "quina": {
        "name": "Quina",
        "range": 80,
        "pick": 5,
        "cost": 2.50,
        "premium_hits": [3, 4, 5],
        "emoji": "🎲",
        "combination_costs": {
            7: 21 * 2.50,    # 21 jogos
            8: 56 * 2.50,    # 56 jogos
            9: 126 * 2.50,   # 126 jogos
            10: 252 * 2.50,  # 252 jogos
            11: 462 * 2.50,  # 462 jogos
            12: 792 * 2.50,  # 792 jogos
            13: 1287 * 2.50, # 1287 jogos
            14: 2002 * 2.50, # 2002 jogos
            15: 3003 * 2.50  # 3003 jogos
        }
    },
    "lotomania": {
        "name": "Lotomania",
        "range": 100,
        "pick": 20,
        "cost": 3.00,
        "premium_hits": [15, 16, 17, 18, 19, 20, 0],
        "emoji": "🎴",
        "combination_costs": {
            22: 116280 * 3.00, # 116280 jogos
            23: 451095 * 3.00, # 451095 jogos
            24: 1345964 * 3.00,# 1345964 jogos
            25: 3312840 * 3.00 # 3312840 jogos
        }
    }
}

# ============================================================
# CLASSE: GERADOR DE JOGOS ESTRATÉGICOS
# ============================================================
class StrategicGameGenerator:
    """Gerador de jogos com estratégias avançadas"""

    def __init__(self, lottery_type):
        self.type = lottery_type
        self.config = LOTTERY_CONFIG[lottery_type]
        self.load_database()

    def load_database(self):
        """Carrega banco de dados da loteria"""
        self.db_dir = os.path.join(DATABASE_DIR, self.type)
        self.draws_file = os.path.join(self.db_dir, "all_draws.json")
        self.freq_file = os.path.join(self.db_dir, "frequency.json")
        self.delay_file = os.path.join(self.db_dir, "delay.json")
        self.cooc_file = os.path.join(self.db_dir, "cooccurrence.json")

        self.draws = []
        self.frequency = {}
        self.delay = {}
        self.cooccurrence = {}

        if os.path.exists(self.draws_file):
            with open(self.draws_file) as f:
                data = json.load(f)
                self.draws = data.get("draws", [])

        if os.path.exists(self.freq_file):
            with open(self.freq_file) as f:
                self.frequency = json.load(f)

        if os.path.exists(self.delay_file):
            with open(self.delay_file) as f:
                self.delay = json.load(f)

        if os.path.exists(self.cooc_file):
            with open(self.cooc_file) as f:
                self.cooccurrence = json.load(f)

    # ----------------------------------------------------------
    # ANÁLISE DE NÚMEROS
    # ----------------------------------------------------------
    def get_hot_numbers(self, n=15):
        """Retorna números mais quentes (frequentes)"""
        if not self.frequency:
            return list(range(1, min(n+1, self.config["range"]+1)))
        return [int(n) for n, _ in sorted(self.frequency.items(), key=lambda x: x[1], reverse=True)[:n]]

    def get_cold_numbers(self, n=15):
        """Retorna números mais frios (pouco frequentes)"""
        if not self.frequency:
            return list(range(max(1, self.config["range"]-n+1), self.config["range"]+1))
        return [int(n) for n, _ in sorted(self.frequency.items(), key=lambda x: x[1])[:n]]

    def get_delayed_numbers(self, n=15):
        """Retorna números mais atrasados"""
        if not self.delay:
            return self.get_cold_numbers(n)
        return [int(n) for n, _ in sorted(self.delay.items(), key=lambda x: x[1], reverse=True)[:n]]

    def get_balanced_numbers(self, n=15):
        """Retorna números balanceados (quentes + frios + atrasados)"""
        hot = set(self.get_hot_numbers(10))
        cold = set(self.get_cold_numbers(10))
        delayed = set(self.get_delayed_numbers(10))

        # Combinar estratégias sem duplicatas
        result = list(hot)[:5] + list(delayed)[:5] + list(cold)[:5]

        # Preencher se necessário com números restantes
        all_nums = set(range(1, self.config["range"]+1))
        used = set(result)
        remaining = list(all_nums - used)
        random.shuffle(remaining)

        while len(result) < n and remaining:
            result.append(remaining.pop())

        return result[:n]

    # ----------------------------------------------------------
    # GERAÇÃO DE JOGOS POR ESTRATÉGIA
    # ----------------------------------------------------------
    def generate_by_frequency(self, n_games=5):
        """Gera jogos baseados em frequência"""
        hot = self.get_hot_numbers(20)
        games = []

        for _ in range(n_games):
            game = sorted(random.sample(hot, self.config["pick"]))
            games.append(game)

        return games

    def generate_by_delay(self, n_games=5):
        """Gera jogos baseados em atraso"""
        delayed = self.get_delayed_numbers(20)
        games = []

        for _ in range(n_games):
            game = sorted(random.sample(delayed, self.config["pick"]))
            games.append(game)

        return games

    def generate_balanced(self, n_games=5):
        """Gera jogos balanceados"""
        balanced = self.get_balanced_numbers(20)
        games = []

        for _ in range(n_games):
            game = sorted(random.sample(balanced, self.config["pick"]))
            games.append(game)

        return games

    def generate_mixed(self, n_games=10):
        """Gera jogos mistos (várias estratégias)"""
        games = []
        strategies = [
            ("FREQUENCY", self.generate_by_frequency(3)),
            ("DELAY", self.generate_by_delay(3)),
            ("BALANCED", self.generate_balanced(4))
        ]

        for name, strategy_games in strategies:
            for game in strategy_games:
                games.append((name, game))

        return games

    # ----------------------------------------------------------
    # COBERTURA ESTRATÉGICA (CERCADO)
    # ----------------------------------------------------------
    def generate_coverage(self, numbers, max_games=None, budget=None):
        """
        Gera cobertura (cercado) para números escolhidos

        Args:
            numbers: Lista de números para cobrir
            max_games: Máximo de jogos (se não especificado, gera todos)
            budget: Orçamento máximo em reais

        Returns:
            Lista de jogos e informações de cobertura
        """
        pick = self.config["pick"]
        cost = self.config["cost"]

        # Calcular todas as combinações possíveis
        all_combinations = list(combinations(sorted(numbers), pick))
        total_combinations = len(all_combinations)

        # Calcular custo total
        total_cost = total_combinations * cost

        # Limitar por orçamento ou máximo de jogos
        if budget:
            max_by_budget = int(budget / cost)
            if total_combinations > max_by_budget:
                # Selecionar combinações mais prováveis
                games = self._select_best_combinations(all_combinations, max_by_budget)
            else:
                games = [list(c) for c in all_combinations]
        elif max_games and total_combinations > max_games:
            games = self._select_best_combinations(all_combinations, max_games)
        else:
            games = [list(c) for c in all_combinations]

        return {
            "numbers": numbers,
            "total_combinations": total_combinations,
            "games_generated": len(games),
            "total_cost": len(games) * cost,
            "coverage_percent": (len(games) / total_combinations * 100) if total_combinations > 0 else 0,
            "games": games
        }

    def _select_best_combinations(self, combinations_list, max_games):
        """Seleciona melhores combinações baseado em frequência"""
        if not self.frequency:
            return [list(c) for c in combinations_list[:max_games]]

        # Pontuar cada combinação pela soma das frequências
        scored = []
        for combo in combinations_list:
            score = sum(self.frequency.get(str(n), self.frequency.get(n, 1)) for n in combo)
            scored.append((score, combo))

        # Ordenar por pontuação e pegar os top
        scored.sort(reverse=True)
        return [list(c) for _, c in scored[:max_games]]

    # ----------------------------------------------------------
    # SISTEMA DE CONFIANÇA
    # ----------------------------------------------------------
    def calculate_confidence(self, game):
        """Calcula confiança de um jogo (0-100%)"""
        if not self.frequency or not self.delay:
            return 50.0  # Confiança média se não há dados

        # Fatores de confiança
        hot_count = sum(1 for n in game if n in self.get_hot_numbers(15))
        delayed_count = sum(1 for n in game if n in self.get_delayed_numbers(15))

        # Calcular baseado em hitting stats
        total_draws = len(self.draws) if self.draws else 1
        expected_hits = (self.config["pick"] * total_draws) / self.config["range"]

        # Score final
        score = (hot_count * 0.4 + delayed_count * 0.4 + (self.config["pick"] - hot_count - delayed_count) * 0.2)
        confidence = min(100, (score / self.config["pick"]) * 100)

        return round(confidence, 1)

    def rank_games(self, games):
        """Rank games por confiança"""
        ranked = []
        for game in games:
            conf = self.calculate_confidence(game)
            ranked.append((conf, game))

        ranked.sort(reverse=True)
        return ranked

    # ----------------------------------------------------------
    # RELATÓRIO COMPLETO
    # ----------------------------------------------------------
    def generate_report(self):
        """Gera relatório completo da loteria"""
        hot = self.get_hot_numbers(10)
        cold = self.get_cold_numbers(10)
        delayed = self.get_delayed_numbers(10)
        balanced = self.get_balanced_numbers(10)

        # Estatísticas
        stats = {
            "lottery": self.config["name"],
            "total_draws": len(self.draws),
            "hot_numbers": hot,
            "cold_numbers": cold,
            "delayed_numbers": delayed,
            "balanced_numbers": balanced,
            "total_combinations": math.comb(self.config["range"], self.config["pick"])
        }

        return stats

    def print_report(self):
        """Imprime relatório detalhado"""
        stats = self.generate_report()

        print(f"\n{'='*60}")
        print(f"📊 RELATÓRIO {stats['lottery']} - SIAOL-PRO GAME GENERATOR")
        print(f"{'='*60}")
        print(f"   Total de sorteios analisados: {stats['total_draws']}")
        print(f"   Total de combinações possíveis: {stats['total_combinations']:,}")

        print(f"\n   🔥 NÚMEROS QUENTES:")
        print(f"      {' '.join(f'{n:02d}' for n in stats['hot_numbers'])}")

        print(f"\n   ❄️  NÚMEROS FRIOS:")
        print(f"      {' '.join(f'{n:02d}' for n in stats['cold_numbers'])}")

        print(f"\n   ⏰ NÚMEROS ATRASADOS:")
        print(f"      {' '.join(f'{n:02d}' for n in stats['delayed_numbers'])}")

        print(f"\n   ⚖️  NÚMEROS BALANCEADOS:")
        print(f"      {' '.join(f'{n:02d}' for n in stats['balanced_numbers'])}")

        print(f"\n{'='*60}")

        # Mostrar custos de cobertura
        print(f"\n💰 CUSTOS DE COBERTURA (CERCADO):")
        for nums, cost in self.config["combination_costs"].items():
            games = math.comb(nums, self.config["pick"])
            coverage = (games / stats['total_combinations']) * 100
            print(f"   {nums} números → {games:,} jogos = R$ {cost:.2f} ({coverage:.4f}% cobertura)")

        print(f"{'='*60}\n")

        return stats


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================
def main():
    import argparse

    parser = argparse.ArgumentParser(description="SIAOL-PRO Game Generator")
    parser.add_argument("--lottery", "-l", choices=["megasena", "lotofacil", "quina", "lotomania"],
                       help="Tipo de loteria")
    parser.add_argument("--games", "-g", type=int, default=5, help="Número de jogos")
    parser.add_argument("--coverage", "-c", type=int, help="Gerar cobertura com N números")
    parser.add_argument("--budget", "-b", type=float, help="Orçamento máximo")
    parser.add_argument("--report", "-r", action="store_true", help="Gerar relatório")

    args = parser.parse_args()

    if args.lottery:
        gen = StrategicGameGenerator(args.lottery)

        if args.report or not args.coverage:
            gen.print_report()

        if args.coverage:
            print(f"\n🎯 COBERTURA COM {args.coverage} NÚMEROS:\n")

            # Cobertura com números quentes
            hot = gen.get_hot_numbers(args.coverage)
            cov_hot = gen.generate_coverage(hot, budget=args.budget)
            print(f"   🔥 Números quentes ({args.coverage}):")
            print(f"      {hot}")
            print(f"      Jogos: {cov_hot['games_generated']} | Custo: R$ {cov_hot['total_cost']:.2f}")
            print(f"      Cobertura: {cov_hot['coverage_percent']:.4f}%\n")

            # Cobertura com números atrasados
            delayed = gen.get_delayed_numbers(args.coverage)
            cov_delayed = gen.generate_coverage(delayed, budget=args.budget)
            print(f"   ⏰ Números atrasados ({args.coverage}):")
            print(f"      {delayed}")
            print(f"      Jogos: {cov_delayed['games_generated']} | Custo: R$ {cov_delayed['total_cost']:.2f}")
            print(f"      Cobertura: {cov_delayed['coverage_percent']:.4f}%\n")

            # Cobertura com números balanceados
            balanced = gen.get_balanced_numbers(args.coverage)
            cov_balanced = gen.generate_coverage(balanced, budget=args.budget)
            print(f"   ⚖️  Números balanceados ({args.coverage}):")
            print(f"      {balanced}")
            print(f"      Jogos: {cov_balanced['games_generated']} | Custo: R$ {cov_balanced['total_cost']:.2f}")
            print(f"      Cobertura: {cov_balanced['coverage_percent']:.4f}%\n")

        elif args.games:
            print(f"\n🎰 JOGOS GERADOS ({args.games}):\n")
            games = gen.generate_mixed(args.games)
            for i, (strategy, game) in enumerate(games, 1):
                conf = gen.calculate_confidence(game)
                nums = " - ".join(f"{n:02d}" for n in game)
                print(f"   {i:02d}. [{strategy}] {nums} (Confiança: {conf}%)")

    else:
        # Mostrar relatório de todas as loterias
        for lottery in LOTTERY_CONFIG.keys():
            gen = StrategicGameGenerator(lottery)
            gen.print_report()


if __name__ == "__main__":
    main()