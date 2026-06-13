#!/usr/bin/env python3
"""
Gerador de jogos calibrado para concurso 7048
"""

import json
import os
from itertools import combinations
from datetime import datetime

# Pool de 18 dezenas calibradas
POOL_18 = [2, 6, 11, 12, 13, 14, 17, 18, 19, 21, 23, 26, 28, 29, 37, 42, 48, 50]

def generate_games(pool, count=56):
    """Gera jogos com cobertura 100% dezenas"""
    dezenas_pool = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}

    for num in pool:
        dezena = (num - 1) // 10
        if dezena in dezenas_pool:
            dezenas_pool[dezena].append(num)

    # Selecionar 5 números de cada dezena disponível
    selected = []
    for d in range(8):
        nums = dezenas_pool[d]
        if nums:
            selected.append(nums[0])

    # Se temos mais de 5 selecionados, gerar combinações
    if len(selected) >= 5:
        games = []
        for combo in combinations(selected, 5):
            games.append(sorted(list(combo)))
        if len(games) >= count:
            return games[:count]

    # Se não gerou jogos suficientes, usar pool direto
    games = []
    for combo in combinations(pool, 5):
        games.append(sorted(list(combo)))
        if len(games) >= count:
            break

    return games[:count]

def main():
    print("GERADOR DE JOGOS - CALIBRADO 7048")
    print(f"Pool: {POOL_18}")

    games_56 = generate_games(POOL_18, 56)
    games_70 = generate_games(POOL_18, 70)

    print(f"56 jogos gerados")
    print(f"70 jogos gerados")

    os.makedirs("memory", exist_ok=True)

    data_56 = {
        "option": 1,
        "name": f"CALIBRADO 7048 - {datetime.now().strftime('%Y-%m-%d')}",
        "games": len(games_56),
        "cost": len(games_56) * 3.0,
        "portfolio": [
            {"id": i+1, "numbers": game, "strategy": "CALIBRADO_7048"}
            for i, game in enumerate(games_56)
        ]
    }

    with open("memory/quina_56_games_latest.json", 'w') as f:
        json.dump(data_56, f, indent=2)

    data_70 = {
        "option": 2,
        "name": f"CALIBRADO 7048 - {datetime.now().strftime('%Y-%m-%d')}",
        "games": len(games_70),
        "cost": len(games_70) * 3.0,
        "portfolio": [
            {"id": i+1, "numbers": game, "strategy": "CALIBRADO_7048"}
            for i, game in enumerate(games_70)
        ]
    }

    with open("memory/quina_70_games_latest.json", 'w') as f:
        json.dump(data_70, f, indent=2)

    print("Jogos salvos!")

if __name__ == "__main__":
    main()