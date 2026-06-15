#!/usr/bin/env python3
"""Calibração para concurso 7051 - FINAL"""
import json
from collections import Counter
from itertools import combinations

RESULTADOS = [
    [12, 13, 17, 54, 71],  # 7045
    [2, 12, 37, 68, 76],   # 7046
    [6, 11, 26, 50, 61],   # 7047
    [9, 25, 34, 56, 70],   # 7048
    [9, 14, 25, 44, 67],   # 7049
    # 7050 - ACUMULOU
]

def main():
    print("=" * 60)
    print("CALIBRAÇÃO 7051 - CONCURSO FINAL")
    print("Prêmio: R$ 275.000.000 | Sorteio: 28/06/2026")
    print("=" * 60)

    # Carregar histórico
    with open("data/quina_history.json") as f:
        data = json.load(f)
    history = data['concursos']

    # 7050 acumulou - não adiciona números específicos
    data['total_concursos'] = 7049
    data['last_update'] = '2026-06-14'

    # Calcular hot/cold dos últimos 50
    recent = history[-50:]
    all_nums = []
    for r in recent:
        all_nums.extend(r)
    counter = Counter(all_nums)

    hot = [n for n, c in counter.most_common(15)]
    cold = [n for n, c in counter.most_common()[-15:]]

    print(f"\n🔥 HOT: {hot}")
    print(f"\n❄️ COLD: {cold}")

    # Pool amplo
    recent_nums = set()
    for r in RESULTADOS:
        recent_nums.update(r)

    pool = sorted(list(recent_nums) + [n for n in hot if n not in recent_nums])[:25]

    print(f"\n📊 POOL 25 DEZENAS: {pool}")

    # Salvar
    with open("data/quina_history.json", 'w') as f:
        json.dump(data, f, indent=2)

    calibracao = {
        'calibrado_para': 7051,
        'premio': 'R$ 275.000.000',
        'sorteio': '28/06/2026',
        'hot': hot,
        'cold': cold,
        'pool': pool
    }
    with open("memory/calibracao_7051.json", 'w') as f:
        json.dump(calibracao, f, indent=2)

    print("\n🎰 Gerando jogos para concurso 7051...")

    # Gerar jogos
    games_56 = [sorted(list(c)) for c in combinations(pool[:20], 5)][:56]
    games_70 = [sorted(list(c)) for c in combinations(pool[:22], 5)][:70]

    data_56 = {
        "option": 1,
        "name": "CALIBRADO 7051 - FINAL",
        "games": len(games_56),
        "premio": "R$ 275.000.000",
        "portfolio": [{"id": i+1, "numbers": g, "strategy": "7051_FINAL"} for i, g in enumerate(games_56)]
    }
    with open("memory/quina_56_games_latest.json", 'w') as f:
        json.dump(data_56, f, indent=2)

    data_70 = {
        "option": 2,
        "name": "CALIBRADO 7051 - FINAL",
        "games": len(games_70),
        "premio": "R$ 275.000.000",
        "portfolio": [{"id": i+1, "numbers": g, "strategy": "7051_FINAL"} for i, g in enumerate(games_70)]
    }
    with open("memory/quina_70_games_latest.json", 'w') as f:
        json.dump(data_70, f, indent=2)

    print(f"\n✅ 56 jogos gerados para 7051")
    print(f"✅ 70 jogos gerados para 7051")
    print("\n🎯 BOA SORTE NO CONCURSO 7051!")

if __name__ == "__main__":
    main()