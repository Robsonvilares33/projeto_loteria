#!/usr/bin/env python3
"""
SIAOL-PRO LOTTERY RULES - Regras Oficiais da Caixa
===================================================
Banco de dados completo com todas as regras oficiais das loterias:

LOTERIAS SUPORTADAS:
1. Mega-Sena (60 números, 6 por jogo)
2. Lotofácil (25 números, 15 por jogo)
3. Quina (80 números, 5 por jogo)
4. Lotomania (100 números, 50 por jogo)

FONTE: https://loterias.caixa.gov.br/
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import time
import math

# ============================================================
# ESTRUTURAS DE DADOS
# ============================================================

@dataclass
class PrizeTier:
    """Faixa de premiação"""
    name: str
    hits: int
    probability: str  # "1 em X"
    probability_value: float  # Valor numérico
    pool_share: float  # Percentual do premio
    fixed_value: Optional[float] = None  # Valor fixo (se houver)


@dataclass
class PoolRules:
    """Regras de bolão (pool betting)"""
    min_cotas: int
    max_cotas: int
    min_cota_value: float
    min_pool_value: float
    max_pool_value: float


@dataclass
class LotteryRules:
    """Regras completas de uma loteria"""
    id: str
    name: str
    emoji: str
    range_min: int
    range_max: int
    pick_min: int
    pick_max: int
    bet_price: float
    draw_days: List[int]  # 0=segunda, 6=domingo
    draw_time: str
    location: str

    # Custo por quantidade de números (para apostas multiples)
    multiple_bet_costs: Dict[int, float]

    # Faixas de premiação
    prize_tiers: List[PrizeTier]

    # Regras de bolão
    pool_rules: PoolRules

    # Valor mínimo da aposta
    min_bet: float

    # Probabilidade de acerto (para aposta mínima)
    min_bet_probability: str


# ============================================================
# REGRAS OFICIAIS DA CAIXA
# ============================================================

# Calculate combinations for probability
def calc_probability(n, k, total_n, total_k):
    """Calcula probabilidade de acertar k números"""
    favorable = math.comb(n, k) * math.comb(total_n - n, total_k - k)
    total = math.comb(total_n, total_k)
    return favorable / total


# LOTOFÁCIL
LOTOFACIL_RULES = LotteryRules(
    id="lotofacil",
    name="Lotofácil",
    emoji="🎯",
    range_min=1,
    range_max=25,
    pick_min=15,
    pick_max=20,
    bet_price=3.00,
    draw_days=[0, 1, 2, 3, 4, 5],  # Segunda a sábado
    draw_time="20:00",
    location="Espaço da Sorte, Av. Paulista, 750 - São Paulo",

    multiple_bet_costs={
        15: 3.00,
        16: 48.00,
        17: 408.00,
        18: 2448.00,
        19: 11628.00,
        20: 38760.00  # Atualizado com valor correto
    },

    prize_tiers=[
        PrizeTier("15 acertos", 15, "1 em 3,268,760", 1/3268760, 0.62, None),
        PrizeTier("14 acertos", 14, "1 em 21,791", 1/21791, 0.13, None),
        PrizeTier("13 acertos", 13, "1 em 691", 1/691, 0.0, 30.00),
        PrizeTier("12 acertos", 12, "1 em 59", 1/59, 0.0, 12.00),
        PrizeTier("11 acertos", 11, "1 em 11", 1/11, 0.0, 6.00)
    ],

    pool_rules=PoolRules(
        min_cotas=2,
        max_cotas=100,
        min_cota_value=4.00,
        min_pool_value=12.00,
        max_pool_value=float('inf')
    ),

    min_bet=3.00,
    min_bet_probability="1 em 3,268,760 (15 acertos)"
)


# QUINA
QUINA_RULES = LotteryRules(
    id="quina",
    name="Quina",
    emoji="🎲",
    range_min=1,
    range_max=80,
    pick_min=5,
    pick_max=15,
    bet_price=2.50,
    draw_days=[0, 1, 2, 3, 4, 5],  # Segunda a sábado (exceto domingos/feriados)
    draw_time="20:00",
    location="Espaço da Sorte, Av. Paulista, 750 - São Paulo",

    multiple_bet_costs={
        5: 2.50,
        6: 15.00,
        7: 52.50,
        8: 140.00,
        9: 315.00,
        10: 630.00,
        11: 1155.00,
        12: 1980.00,
        13: 3217.50,
        14: 5005.00,
        15: 7507.50
    },

    prize_tiers=[
        PrizeTier("5 acertos (Quina)", 5, "1 em 24,040,016", 1/24040016, 0.35, None),
        PrizeTier("4 acertos (Quadra)", 4, "1 em 64,106", 1/64106, 0.15, None),
        PrizeTier("3 acertos (Terno)", 3, "1 em 866", 1/866, 0.10, None),
        PrizeTier("2 acertos (Duque)", 2, "1 em 36", 1/36, 0.10, None)
    ],

    pool_rules=PoolRules(
        min_cotas=2,
        max_cotas=50,
        min_cota_value=3.00,
        min_pool_value=10.00,
        max_pool_value=float('inf')
    ),

    min_bet=2.50,
    min_bet_probability="1 em 24,040,016"
)


# MEGA-SENA
MEGASENA_RULES = LotteryRules(
    id="megasena",
    name="Mega-Sena",
    emoji="🎰",
    range_min=1,
    range_max=60,
    pick_min=6,
    pick_max=20,
    bet_price=5.00,
    draw_days=[1, 3, 5],  # Terça, quinta, sábado
    draw_time="20:00",
    location="Espaço da Sorte, Av. Paulista, 750 - São Paulo",

    multiple_bet_costs={
        6: 5.00,
        7: 35.00,
        8: 140.00,
        9: 420.00,
        10: 1050.00,
        11: 2310.00,
        12: 4620.00,
        13: 8580.00,
        14: 15015.00,
        15: 25025.00,
        16: 40040.00,
        17: 61880.00,
        18: 92820.00,
        19: 135660.00,
        20: 193800.00
    },

    prize_tiers=[
        PrizeTier("6 acertos (Sena)", 6, "1 em 50,063,860", 1/50063860, 0.35, None),
        PrizeTier("5 acertos (Quina)", 5, "1 em 154,518", 1/154518, 0.19, None),
        PrizeTier("4 acertos (Quadra)", 4, "1 em 2,332", 1/2332, 0.19, None)
    ],

    pool_rules=PoolRules(
        min_cotas=2,
        max_cotas=100,
        min_cota_value=5.00,
        min_pool_value=10.00,
        max_pool_value=float('inf')
    ),

    min_bet=5.00,
    min_bet_probability="1 em 50,063,860 (6 acertos)"
)


# LOTOMANIA
LOTOMANIA_RULES = LotteryRules(
    id="lotomania",
    name="Lotomania",
    emoji="🎴",
    range_min=0,
    range_max=99,  # 00 a 99
    pick_min=50,
    pick_max=50,  # Sempre 50 números
    bet_price=3.00,
    draw_days=[0, 2, 4],  # Segunda, quarta, sexta
    draw_time="20:00",
    location="Espaço da Sorte, Av. Paulista, 750 - São Paulo",

    multiple_bet_costs={
        50: 3.00  # Sempre 50 números
    },

    prize_tiers=[
        PrizeTier("20 acertos", 20, "1 em 11,372,635", 1/11372635, 0.45, None),
        PrizeTier("19 acertos", 19, "1 em 352,551", 1/352551, 0.16, None),
        PrizeTier("18 acertos", 18, "1 em 24,235", 1/24235, 0.10, None),
        PrizeTier("17 acertos", 17, "1 em 2,776", 1/2776, 0.07, None),
        PrizeTier("16 acertos", 16, "1 em 472", 1/472, 0.07, None),
        PrizeTier("15 acertos", 15, "1 em 112", 1/112, 0.07, None),
        PrizeTier("0 acertos", 0, "1 em 11,372,635", 1/11372635, 0.08, None)
    ],

    pool_rules=PoolRules(
        min_cotas=2,
        max_cotas=100,
        min_cota_value=5.00,
        min_pool_value=10.00,
        max_pool_value=float('inf')
    ),

    min_bet=3.00,
    min_bet_probability="1 em 11,372,635 (20 acertos)"
)


# ============================================================
# REGISTRO DE TODAS AS LOTERIAS
# ============================================================

ALL_LOTTERIES = {
    "lotofacil": LOTOFACIL_RULES,
    "quina": QUINA_RULES,
    "megasena": MEGASENA_RULES,
    "lotomania": LOTOMANIA_RULES
}


# ============================================================
# CLASSE: CALCULADORA DE PROBABILIDADES
# ============================================================

class LotteryCalculator:
    """Calculadora de probabilidades e custos"""

    @staticmethod
    def calculate_combinations(n_range: int, pick: int, selected: int) -> int:
        """Calcula número de combinações possíveis"""
        return math.comb(n_range, pick)

    @staticmethod
    def calculate_probability(n_range: int, pick: int, hits: int, selected: int) -> float:
        """
        Calcula probabilidade de acertar 'hits' números

        Args:
            n_range: Range de números (ex: 60 para Mega-Sena)
            pick: Números sorteados (ex: 6)
            hits: Quantos quer acertar
            selected: Quantos números apostou
        """
        if selected < hits:
            return 0.0

        # C(n,k) * C(N-n, K-k) / C(N,K)
        favorable = math.comb(selected, hits) * math.comb(n_range - selected, pick - hits)
        total = math.comb(n_range, pick)

        return favorable / total

    @staticmethod
    def calculate_bet_cost(rules: LotteryRules, n_selected: int) -> float:
        """Calcula custo da aposta"""
        if n_selected in rules.multiple_bet_costs:
            return rules.multiple_bet_costs[n_selected]

        # Calcular custo baseado em combinações
        base_cost = rules.bet_price
        combos = math.comb(n_selected, rules.pick_min) / math.comb(rules.pick_min, rules.pick_min)
        return base_cost * math.comb(n_selected, rules.pick_min)

    @staticmethod
    def calculate_pool_shares(total_value: float, rules: LotteryRules, winners: Dict[int, int]) -> Dict[int, float]:
        """
        Calcula distribuição de prêmio por faixa

        Args:
            total_value: Valor total do prêmio
            rules: Regras da loteria
            winners: Dicionário {hits: qtd_ganhadores}
        """
        result = {}

        for tier in rules.prize_tiers:
            hits = tier.hits
            share = tier.pool_share
            winners_count = winners.get(hits, 0)

            if winners_count > 0:
                result[hits] = (total_value * share) / winners_count
            else:
                result[hits] = 0.0

        return result


# ============================================================
# CLASSE: RELATÓRIO DE REGRAS
# ============================================================

class LotteryReport:
    """Gera relatórios detalhados das regras"""

    @staticmethod
    def generate_full_report(lottery_id: str) -> str:
        """Gera relatório completo de uma loteria"""
        if lottery_id not in ALL_LOTTERIES:
            return f"Loteria '{lottery_id}' não encontrada"

        rules = ALL_LOTTERIES[lottery_id]
        calc = LotteryCalculator()

        # Dias de sorteio
        day_names = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        draw_days = [day_names[d] for d in rules.draw_days]

        report = f"""
╔═══════════════════════════════════════════════════════════════════════╗
║  {rules.emoji} {rules.name.upper():<58}║
╠═══════════════════════════════════════════════════════════════════════╣
║  📋 IDENTIFICAÇÃO                                                    ║
║     ID: {rules.id:<56}║
║     Números: {rules.range_min:02d} a {rules.range_max:02d} ({rules.range_max} números)                      ║
║     Escolha: {rules.pick_min} a {rules.pick_max} números por aposta                    ║
║     Valor mínimo: R$ {rules.min_bet:.2f}{" " * (53 - len(f"R$ {rules.min_bet:.2f}"))}║
║     Probabilidade (mínima): {rules.min_bet_probability:<40}║
╠═══════════════════════════════════════════════════════════════════════╣
║  📅 SORTEIOS                                                          ║
║     Dias: {', '.join(draw_days):<52}║
║     Horário: {rules.draw_time} (Brasília){" " * 42}║
║     Local: {rules.location:<53}║
╠═══════════════════════════════════════════════════════════════════════╣
║  💰 CUSTO DAS APOSTAS MÚLTIPLAS                                        ║"""

        for n_select, cost in sorted(rules.multiple_bet_costs.items()):
            combos = math.comb(n_select, rules.pick_min)
            prob = calc.calculate_probability(rules.range_max, rules.pick_min, rules.pick_min, n_select)
            prob_str = f"1 em {int(1/prob):,}" if prob > 0 else "N/A"
            report += f"\n║     {n_select:02d} números: R$ {cost:>10.2f} | {combos:>6} jogos | {prob_str:<20}║"

        report += f"""
╠═══════════════════════════════════════════════════════════════════════╣
║  🏆 PREMIAÇÃO                                                         ║"""

        for tier in rules.prize_tiers:
            fixed_str = f" (Fixo: R$ {tier.fixed_value:.2f})" if tier.fixed_value else ""
            report += f"\n║     {tier.name:<25} | {tier.probability:<20} | {tier.pool_share*100:>5.1f}%{fixed_str:<15}║"

        report += f"""
╠═══════════════════════════════════════════════════════════════════════╣
║  🎯 REGRAS DE BOLÃO                                                   ║
║     Cotas: {rules.pool_rules.min_cotas} a {rules.pool_rules.max_cotas}{" " * 49}║
║     Valor mínimo da cota: R$ {rules.pool_rules.min_cota_value:.2f}{" " * 41}║
║     Valor mínimo do bolão: R$ {rules.pool_rules.min_pool_value:.2f}{" " * 41}║
╠═══════════════════════════════════════════════════════════════════════╣
║  📊 ESTATÍSTICAS                                                      ║"""

        total_combinations = math.comb(rules.range_max, rules.pick_min)
        report += f"""
║     Total de combinações: {total_combinations:>25,}║
║     Chance de acerto (aposta mínima): 1 em {total_combinations:,}║
╚═══════════════════════════════════════════════════════════════════════╝
"""

        return report

    @staticmethod
    def generate_all_lotteries_report() -> str:
        """Gera relatório de todas as loterias"""
        report = """
╔═══════════════════════════════════════════════════════════════════════╗
║           🏆 SIAOL-PRO - REGRAS OFICIAIS DA CAIXA 🏆                   ║
╚═══════════════════════════════════════════════════════════════════════╝
"""

        for lottery_id in ALL_LOTTERIES:
            report += LotteryReport.generate_full_report(lottery_id)
            report += "\n"

        return report


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def main():
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        # Relatório de todas as loterias
        print(LotteryReport.generate_all_lotteries_report())
    elif len(sys.argv) > 1 and sys.argv[1] in ALL_LOTTERIES:
        # Relatório de uma loteria específica
        print(LotteryReport.generate_full_report(sys.argv[1]))
    else:
        # Relatório rápido
        print("""
╔═══════════════════════════════════════════════════════════════════════╗
║           🏆 SIAOL-PRO - REGRAS OFICIAIS DA CAIXA 🏆                   ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║   LOTERIAS DISPONÍVEIS:                                               ║
║                                                                       ║
║   1. lotofacil  - Lotofácil (25 números, 15 escolha)                 ║
║   2. quina      - Quina (80 números, 5 escolha)                       ║
║   3. megasena   - Mega-Sena (60 números, 6 escolha)                   ║
║   4. lotomania  - Lotomania (100 números, 50 escolha)                 ║
║                                                                       ║
║   USO:                                                                ║
║     python3 siaol_lottery_rules.py --all                               ║
║     python3 siaol_lottery_rules.py lotofacil                           ║
║     python3 siaol_lottery_rules.py quina                               ║
║     python3 siaol_lottery_rules.py megasena                            ║
║     python3 siaol_lottery_rules.py lotomania                           ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
        """)


if __name__ == "__main__":
    main()