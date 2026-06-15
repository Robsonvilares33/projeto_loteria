#!/usr/bin/env python3
"""
CALIBRAÇÃO FINAL PARA QUINA 7051 - CONCURSO ESPECIAL
Premio: R$ 275.000.000 | Sorteio: 28/06/2026

Pool EQUILIBRADO combinando:
- Numeros quentes recentes
- Resultado 7050 (24, 36, 61, 66, 74)
- Numeros maduros para sair
- Distribuicao por dezenas
"""

import json
from collections import Counter
from itertools import combinations
import random

RESULTADO_7050 = [24, 36, 61, 66, 74]

def main():
    print("=" * 70)
    print("CALIBRAÇÃO FINAL - QUINA 7051")
    print("Premio: R$ 275.000.000 | Sorteio: 28/06/2026")
    print("=" * 70)

    # Carregar historico
    with open("data/quina_history.json") as f:
        data = json.load(f)
    history = data['concursos']

    # Frequencia recentes (ultimos 50)
    recent = history[-50:]
    freq_recent = Counter()
    for r in recent:
        freq_recent.update(r)

    # Frequencia total
    freq_all = Counter()
    for r in history:
        freq_all.update(r)

    print("\n🔥 NUMEROS QUENTES (Ultimos 50):")
    for n, c in freq_recent.most_common(15):
        print(f"   {n}: {c}x")

    # Pool EQUILIBRADO
    pool = set()

    # 1. Numeros do resultado 7050 (24, 36, 61, 66, 74)
    for n in RESULTADO_7050:
        pool.add(n)

    # 2. Numeros mais quentes
    for n, c in freq_recent.most_common(12):
        pool.add(n)

    # 3. Numeros que apareceram 1x nos ultimos 20 (maduros)
    recent_20 = history[-20:]
    freq_20 = Counter()
    for r in recent_20:
        freq_20.update(r)
    for n, c in freq_20.items():
        if c == 1 and n not in pool:
            pool.add(n)

    # 4. Garantir diversidade de dezenas
    pool_list = sorted(list(pool))
    dezenas_presentes = set((n-1)//10 for n in pool_list)

    # Adicionar um numero de cada dezena ausente
    all_present = list(range(1, 81))
    for n in all_present:
        dz = (n-1)//10
        if dz not in dezenas_presentes and len(pool) < 30:
            pool.add(n)

    # Ordenar e limitar a 25-30 dezenas
    pool = sorted(list(pool))[:28]

    print(f"\n📊 POOL EQUILIBRADO ({len(pool)} dezenas):")
    print(f"   {pool}")

    # Verificar distribuicao
    dezenas_count = Counter((n-1)//10 for n in pool)
    print(f"\n📊 DISTRIBUICAO POR DEZENA:")
    for dz in sorted(dezenas_count.keys()):
        start = dz * 10 + 1
        end = (dz + 1) * 10 if dz < 7 else 80
        nums_in_dz = [n for n in pool if dz*10 < n <= end]
        print(f"   {start:2d}-{end:2d}: {dezenas_count[dz]}x - {nums_in_dz}")

    print("\n🎰 Gerando jogos...")

    # Gerar 56 jogos mecanicos
    games_56 = [sorted(list(c)) for c in combinations(pool, 5)][:56]
    games_70 = [sorted(list(c)) for c in combinations(pool, 5)][:70]

    print(f"✅ 56 jogos gerados")
    print(f"✅ 70 jogos gerados")

    # Salvar
    data_56 = {
        "option": 1,
        "name": "POOL EQUILIBRADO 7051",
        "premio": "R$ 275.000.000",
        "sorteio": "28/06/2026",
        "resultado_7050": RESULTADO_7050,
        "pool": pool,
        "portfolio": [{"id": i+1, "numbers": g} for i, g in enumerate(games_56)]
    }
    with open("memory/quina_56_games_latest.json", 'w') as f:
        json.dump(data_56, f, indent=2)

    data_70 = {
        "option": 2,
        "name": "POOL EQUILIBRADO 7051",
        "premio": "R$ 275.000.000",
        "sorteio": "28/06/2026",
        "resultado_7050": RESULTADO_7050,
        "pool": pool,
        "portfolio": [{"id": i+1, "numbers": g} for i, g in enumerate(games_70)]
    }
    with open("memory/quina_70_games_latest.json", 'w') as f:
        json.dump(data_70, f, indent=2)

    # Mostrar jogos
    print("\n" + "=" * 70)
    print("PRIMEIROS 30 JOGOS:")
    print("=" * 70)
    for i, g in enumerate(games_56[:30], 1):
        odd = sum(1 for n in g if n % 2 == 1)
        low = sum(1 for n in g if n <= 40)
        dz = [(n-1)//10 for n in g]
        print(f"  {i:2d}. {g} | ímpar:{odd} | baixo:{low} | dz:{dz}")

    print("\n" + "=" * 70)
    print("🎯 BOA SORTE! CONCURSO 7051 - 28/06/2026")
    print("Premio: R$ 275.000.000")
    print("=" * 70)

if __name__ == "__main__":
    main()