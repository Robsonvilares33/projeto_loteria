#!/usr/bin/env python3
"""Calibração para concurso 7049"""
import json
from collections import Counter

# Resultados recentes
RESULTADOS = [
    [12, 13, 17, 54, 71],  # 7045
    [2, 12, 37, 68, 76],   # 7046
    [6, 11, 26, 50, 61],   # 7047
    [9, 25, 34, 56, 70],   # 7048
]

def main():
    print("CALIBRAÇÃO 7049")
    print("=" * 50)

    # Carregar histórico
    with open("data/quina_history.json") as f:
        data = json.load(f)
    history = data['concursos']

    # Adicionar 7048 se necessário
    if len(history) >= 7048:
        if history[-1] != RESULTADOS[3]:
            history.append(RESULTADOS[3])
    else:
        history.extend(RESULTADOS)
    data['total_concursos'] = 7048
    data['last_update'] = '2026-06-11'

    # Calcular hot/cold dos últimos 50
    recent = history[-50:]
    all_nums = []
    for r in recent:
        all_nums.extend(r)
    counter = Counter(all_nums)

    hot = [n for n, c in counter.most_common(15)]
    cold = [n for n, c in counter.most_common()[-15:]]

    print(f"\nHOT: {hot}")
    print(f"\nCOLD: {cold}")

    # Pool amplo com números recentes + hot
    recent_nums = set()
    for r in RESULTADOS:
        recent_nums.update(r)

    # Incluir todos os números que apareceram nos últimos 4 concursos
    pool = sorted(list(recent_nums) + [n for n in hot if n not in recent_nums])[:25]

    print(f"\nPOOL 25 DEZENAS: {pool}")

    # Salvar
    with open("data/quina_history.json", 'w') as f:
        json.dump(data, f, indent=2)

    calibracao = {
        'calibrado_para': 7049,
        'hot': hot,
        'cold': cold,
        'pool': pool
    }
    with open("memory/calibracao_7049.json", 'w') as f:
        json.dump(calibracao, f, indent=2)

    print("\nGerando jogos...")

    # Gerar 56 jogos
    from itertools import combinations
    games_56 = [sorted(list(c)) for c in combinations(pool[:20], 5)][:56]
    games_70 = [sorted(list(c)) for c in combinations(pool[:22], 5)][:70]

    data_56 = {
        "option": 1,
        "name": "CALIBRADO 7049",
        "games": len(games_56),
        "portfolio": [{"id": i+1, "numbers": g, "strategy": "7049"} for i, g in enumerate(games_56)]
    }
    with open("memory/quina_56_games_latest.json", 'w') as f:
        json.dump(data_56, f, indent=2)

    data_70 = {
        "option": 2,
        "name": "CALIBRADO 7049",
        "games": len(games_70),
        "portfolio": [{"id": i+1, "numbers": g, "strategy": "7049"} for i, g in enumerate(games_70)]
    }
    with open("memory/quina_70_games_latest.json", 'w') as f:
        json.dump(data_70, f, indent=2)

    print(f"56 jogos gerados")
    print(f"70 jogos gerados")
    print("OK!")

if __name__ == "__main__":
    main()