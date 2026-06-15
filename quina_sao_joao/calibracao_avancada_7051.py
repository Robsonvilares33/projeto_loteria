#!/usr/bin/env python3
"""
CALIBRAÇÃO AVANÇADA PARA QUINA 7051 - CONCURSO ESPECIAL
Premio: R$ 275.000.000 | Sorteio: 28/06/2026

Utiliza toda a inteligencia disponivel:
- Frequencia absoluta
- Frequencia por dezena
- Padroes ímpar/par
- Padroes baixo/alto
- Distancia entre numeros
- Numeros que nao saem há muito tempo
- Densidade de combinacoes
"""

import json
from collections import Counter
from itertools import combinations
from datetime import datetime
import random

# Todos os resultados dos ultimos concursos
RESULTADOS = {
    7045: [12, 13, 17, 54, 71],
    7046: [2, 12, 37, 68, 76],
    7047: [6, 11, 26, 50, 61],
    7048: [9, 25, 34, 56, 70],
    7049: [9, 14, 25, 44, 67],
    7050: [24, 36, 61, 66, 74],  # RESULTADO REAL
}

def analyze_all_concursos():
    """Analise completa de todos os concursos"""
    with open("data/quina_history.json") as f:
        data = json.load(f)
    return data['concursos']

def calculate_frequency_all(history):
    """Frequencia absoluta de todos os numeros"""
    all_nums = []
    for r in history:
        all_nums.extend(r)
    return Counter(all_nums)

def calculate_frequency_recent(history, n=50):
    """Frequencia nos ultimos N concursos"""
    recent = history[-n:]
    all_nums = []
    for r in recent:
        all_nums.extend(r)
    return Counter(all_nums)

def analyze_patterns(numbers):
    """Analisa padroes de uma combinacao"""
    odd = sum(1 for n in numbers if n % 2 == 1)
    even = len(numbers) - odd

    low = sum(1 for n in numbers if n <= 40)
    high = len(numbers) - low

    # Distribuicao por dezena
    dezenas = [(n-1)//10 for n in numbers]

    # Distancias entre numeros
    sorted_nums = sorted(numbers)
    distances = [sorted_nums[i+1] - sorted_nums[i] for i in range(len(sorted_nums)-1)]

    return {
        'odd': odd, 'even': even,
        'low': low, 'high': high,
        'dezenas': dezenas,
        'distances': distances,
        'sum': sum(numbers)
    }

def get_numbers_by_dozens(history):
    """Agrupa numeros por dezena"""
    by_dozens = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}
    for r in history:
        for n in r:
            dz = (n-1)//10
            if dz in by_dozens:
                by_dozens[dz].append(n)
    return by_dozens

def find_missing_numbers(history, n=10):
    """Numeros que nao aparecem ha muito tempo"""
    all_in_history = set()
    for r in history:
        all_in_history.update(r)

    # Encontrar quando cada numero apareceu por ultimo
    last_appearance = {}
    for i, r in enumerate(history):
        for n in r:
            last_appearance[n] = i

    # Numeros ausentes (nao apareceu nos ultimos N)
    missing = []
    for n in range(1, 81):
        if n not in all_in_history or last_appearance.get(n, -1) < len(history) - n:
            if n not in all_in_history:
                missing.append((n, 9999))  # Nunca apareceu
            else:
                missing.append((n, len(history) - last_appearance[n]))

    # Ordenar por tempo desde ultima aparicao
    missing.sort(key=lambda x: -x[1])
    return missing[:20]

def generate_advanced_pool(history):
    """Gera pool avan ado usando multiplas estrategias"""

    # 1. Frequencia recente (ultimos 50)
    freq_recent = calculate_frequency_recent(history, 50)

    # 2. Frequencia total
    freq_all = calculate_frequency_all(history)

    # 3. Numeros faltantes
    missing = find_missing_numbers(history, 20)

    # 4. Padroes dos ultimos resultados
    recent_patterns = [analyze_patterns(RESULTADOS[i]) for i in sorted(RESULTADOS.keys())[-5:]]

    # 5. Numeros por dezena
    by_dozens = get_numbers_by_dozens(history[-50:])

    pool = set()

    # ESTRATEGIA 1: Numeros mais frequentes recentemente
    for num, count in freq_recent.most_common(12):
        pool.add(num)

    # ESTRATEGIA 2: Numeros que estao para sair (quase maduros)
    # Numeros que apareceram 1-2x nos ultimos 20
    recent_20 = history[-20:]
    freq_20 = Counter()
    for r in recent_20:
        freq_20.update(r)

    for num, count in freq_20.items():
        if count == 1:  # Apareceu uma vez nos ultimos 20
            pool.add(num)

    # ESTRATEGIA 3: Numeros que nao aparecem ha muito tempo
    # Mas ainda estao no universo quente
    for num, absence in missing[:8]:
        if num in freq_recent or num in freq_all:
            pool.add(num)

    # ESTRATEGIA 4: Numeros de dezenas que estao "quentes"
    hot_dezenas = []
    for dz, nums in by_dozens.items():
        if len(nums) >= 10:  # Dezena ativa
            hot_dezenas.append(dz)

    for dz in hot_dezenas:
        start = dz * 10 + 1
        end = (dz + 1) * 10 if dz < 7 else 80
        # Adicionar numeros quentes dessa dezena
        dz_freq = {n: freq_recent.get(n, 0) for n in range(start, end+1)}
        top_dz = sorted(dz_freq.items(), key=lambda x: -x[1])[:2]
        for n, f in top_dz:
            if f > 0:
                pool.add(n)

    # ESTRATEGIA 5: Numeros que apareceram no resultado anterior
    for n in RESULTADOS[7050]:
        pool.add(n)

    # Limitar a 25 numeros
    pool = sorted(list(pool))[:25]

    return pool, freq_recent, missing

def generate_smart_games(pool, count=56, history=None):
    """Gera jogos inteligentes baseados em analise"""
    games = []

    # Analisar padroes winners historicos
    patterns = []
    for r in history[-100:]:
        patterns.append(analyze_patterns(r))

    # Padrao medio de winners
    avg_odd = sum(p['odd'] for p in patterns) / len(patterns)
    avg_low = sum(p['low'] for p in patterns) / len(patterns)

    # Gerar jogos com diferentes estrategias
    random.seed(42)

    # 1. Jogos com padrao similar aos winners
    for _ in range(count // 3):
        attempts = 0
        while attempts < 100:
            game = sorted(random.sample(pool, 5))
            pattern = analyze_patterns(game)

            # Verificar se segue padrao de winners
            odd_diff = abs(pattern['odd'] - avg_odd)
            low_diff = abs(pattern['low'] - avg_low)

            # Aceitar se estiver proximo do padrao
            if odd_diff <= 1 and low_diff <= 1:
                if game not in games:
                    games.append(game)
                    break
            attempts += 1

    # 2. Completar com combinacoes mecanicas
    while len(games) < count:
        for combo in combinations(pool, 5):
            game = sorted(list(combo))
            if game not in games:
                games.append(game)
                if len(games) >= count:
                    break
        break

    return games[:count]

def main():
    print("=" * 70)
    print("CALIBRAÇÃO AVANÇADA - QUINA 7051")
    print("Premio: R$ 275.000.000 | Sorteio: 28/06/2026")
    print("=" * 70)

    # Carregar historico completo
    history = analyze_all_concursos()
    print(f"\nTotal de concursos: {len(history)}")

    # Analise do resultado 7050
    print("\n" + "=" * 50)
    print("ANALISE DO RESULTADO 7050: 24, 36, 61, 66, 74")
    print("=" * 50)
    pattern_7050 = analyze_patterns(RESULTADOS[7050])
    print(f"Ímpares: {pattern_7050['odd']} | Pares: {pattern_7050['even']}")
    print(f"Baixos (1-40): {pattern_7050['low']} | Altos (41-80): {pattern_7050['high']}")
    print(f"Dezenas: {pattern_7050['dezenas']}")
    print(f"Distâncias: {pattern_7050['distances']}")
    print(f"Soma: {pattern_7050['sum']}")

    # Gerar pool avan ado
    print("\n" + "=" * 50)
    print("GERANDO POOL INTELIGENTE")
    print("=" * 50)

    pool, freq_recent, missing = generate_advanced_pool(history)

    print(f"\n🔥 Frequencia Recente (Top 15):")
    for n, c in freq_recent.most_common(15):
        print(f"   {n}: {c}x")

    print(f"\n❄️ Numeros Ausentes (Top 10):")
    for n, a in missing[:10]:
        status = "NUNCA" if a == 9999 else f"{a} concursos"
        print(f"   {n}: {status}")

    print(f"\n📊 POOL INTELIGENTE ({len(pool)} dezenas):")
    print(f"   {pool}")

    # Analise por dezena
    by_dozens = get_numbers_by_dozens(history[-50:])
    print(f"\n📊 ATIVIDADE POR DEZENA (ultimos 50):")
    for dz, nums in sorted(by_dozens.items()):
        start = dz * 10 + 1
        end = (dz + 1) * 10 if dz < 7 else 80
        print(f"   {start:2d}-{end:2d}: {len(nums)}x - {sorted(set(nums))[:5]}...")

    # Gerar jogos
    print("\n" + "=" * 50)
    print("GERANDO JOGOS INTELIGENTES")
    print("=" * 50)

    games_56 = generate_smart_games(pool, 56, history)
    games_70 = generate_smart_games(pool, 70, history)

    print(f"\n✅ 56 jogos gerados")
    print(f"✅ 70 jogos gerados")

    # Salvar
    data_56 = {
        "option": 1,
        "name": "CALIBRADO AVANCADO 7051",
        "premio": "R$ 275.000.000",
        "sorteio": "28/06/2026",
        "analise": {
            "resultado_7050": RESULTADOS[7050],
            "pool_size": len(pool),
            "hot_numbers": [n for n, c in freq_recent.most_common(10)]
        },
        "games": len(games_56),
        "portfolio": [{"id": i+1, "numbers": g, "strategy": "AVANCADO"} for i, g in enumerate(games_56)]
    }

    with open("memory/quina_56_games_latest.json", 'w') as f:
        json.dump(data_56, f, indent=2)

    data_70 = {
        "option": 2,
        "name": "CALIBRADO AVANCADO 7051",
        "premio": "R$ 275.000.000",
        "sorteio": "28/06/2026",
        "analise": {
            "resultado_7050": RESULTADOS[7050],
            "pool_size": len(pool),
            "hot_numbers": [n for n, c in freq_recent.most_common(10)]
        },
        "games": len(games_70),
        "portfolio": [{"id": i+1, "numbers": g, "strategy": "AVANCADO"} for i, g in enumerate(games_70)]
    }

    with open("memory/quina_70_games_latest.json", 'w') as f:
        json.dump(data_70, f, indent=2)

    # Salvar calibracao
    calibracao = {
        "calibrado_para": 7051,
        "premio": "R$ 275.000.000",
        "resultado_7050": RESULTADOS[7050],
        "pool": pool,
        "freq_recent": dict(freq_recent.most_common(20)),
        "missing": [(n, a) for n, a in missing[:20]],
        "hot_numbers": [n for n, c in freq_recent.most_common(15)]
    }

    with open("memory/calibracao_avancada_7051.json", 'w') as f:
        json.dump(calibracao, f, indent=2)

    # Atualizar historico
    with open("data/quina_history.json") as f:
        data = json.load(f)
    data['concursos'].append(RESULTADOS[7050])
    data['total_concursos'] = 7050
    data['last_update'] = '2026-06-14'
    with open("data/quina_history.json", 'w') as f:
        json.dump(data, f, indent=2)

    print("\n" + "=" * 70)
    print("PRIMEIROS 20 JOGOS (56):")
    print("=" * 70)
    for i, g in enumerate(games_56[:20], 1):
        odd = sum(1 for n in g if n % 2 == 1)
        print(f"  {i:2d}. {g} (ímpares: {odd})")

    print("\n" + "=" * 70)
    print("🎯 BOA SORTE NO CONCURSO 7051!")
    print("Premio: R$ 275.000.000 | 28/06/2026")
    print("=" * 70)

if __name__ == "__main__":
    main()