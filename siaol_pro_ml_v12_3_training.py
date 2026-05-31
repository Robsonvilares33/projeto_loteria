#!/usr/bin/env python3
"""
SIAOL-PRO v12.3 - TREINAMENTO ML SIMPLIFICADO
Versão standalone para GitHub Actions
"""
import os
import sys
import json
import random
import argparse
from datetime import datetime
from collections import Counter

# Configurações
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOTTERY_CONFIG = {
    "megasena": {"name": "Mega-Sena", "pick": 6, "range": 60},
    "lotofacil": {"name": "Lotofácil", "pick": 15, "range": 25},
    "quina": {"name": "Quina", "pick": 5, "range": 80}
}

def load_json_data(lottery_key):
    """Carrega dados do arquivo JSON criado pelo daily cycle"""
    data_file = os.path.join(OUTPUT_DIR, f"{lottery_key}_data.json")
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    return None

def frequency_analysis(draws, config):
    """Análise de frequência dos números"""
    all_numbers = []
    for draw in draws:
        all_numbers.extend(draw)
    freq = Counter(all_numbers)
    return freq.most_common()

def hot_numbers(freq, top_n=15):
    """Números mais frequentes (quentes)"""
    return [num for num, _ in freq[:top_n]]

def cold_numbers(freq, total_range, bottom_n=15):
    """Números menos frequentes (frios)"""
    all_nums = set(range(1, total_range + 1))
    hot = set([num for num, _ in freq[:15]])
    cold = all_nums - hot
    return list(sorted(cold))[:bottom_n]

def generate_ml_based_games(draws, config, num_games=10):
    """Gera jogos baseados em análise estatística simples"""
    pick = config["pick"]
    total_range = config["range"]

    if len(draws) < 10:
        # Dados insuficientes, gerar jogos aleatórios
        return [[random.sample(range(1, total_range + 1), pick) for _ in range(num_games)]]

    # Frequência
    freq = frequency_analysis(draws, config)
    hot = hot_numbers(freq, 20)
    cold = cold_numbers(freq, total_range, 15)

    games = []
    # Jogo com números quentes
    if len(hot) >= pick:
        games.append(sorted(random.sample(hot, pick)))

    # Jogo com mistura quente/frio
    half = pick // 2
    mixed = random.sample(hot, half) + random.sample(cold, pick - half)
    games.append(sorted(mixed))

    # Jogo com números médios (não mais quentes nem mais frios)
    all_sorted = [n for n, _ in sorted(freq.items(), key=lambda x: x[1])]
    mid_start = len(all_sorted) // 3
    mid_end = len(all_sorted) * 2 // 3
    mid_nums = all_sorted[mid_start:mid_end]
    if len(mid_nums) >= pick:
        games.append(sorted(random.sample(mid_nums, pick)))

    # Jogos extras aleatórios balanceados
    for _ in range(num_games - 3):
        games.append(sorted(random.sample(range(1, total_range + 1), pick)))

    return games[:num_games]

def evaluate_games(games, recent_draws, config):
    """Avalia jogos contra sorteios recentes"""
    pick = config["pick"]
    results = []

    for i, game in enumerate(games):
        hits_list = []
        for draw in recent_draws[:5]:  # Comparar com últimos 5 sorteios
            hits = len(set(game) & set(draw))
            hits_list.append(hits)

        avg_hits = sum(hits_list) / len(hits_list) if hits_list else 0
        max_hits = max(hits_list) if hits_list else 0

        results.append({
            "game_id": i + 1,
            "numbers": game,
            "avg_hits": round(avg_hits, 2),
            "max_hits": max_hits
        })

    return results

def train_lottery(lottery_key, config):
    """Executa treinamento para uma loteria"""
    print(f"\n  🎯 Treinando {config['name']}...")

    data = load_json_data(lottery_key)
    if not data or not data.get('draws'):
        print(f"     ⚠️ Sem dados para {lottery_key}")
        return None

    draws = data['draws']
    print(f"     📊 {len(draws)} sorteios carregados")

    # Análise de frequência
    freq = frequency_analysis(draws, config)
    hot_nums = hot_numbers(freq, 20)
    cold_nums = cold_numbers(freq, config['range'], 15)

    print(f"     🔥 Números quentes: {hot_nums[:10]}")
    print(f"     ❄️ Números frios: {cold_nums[:10]}")

    # Gerar jogos
    games = generate_ml_based_games(draws, config, num_games=10)
    print(f"     🎰 {len(games)} jogos gerados")

    # Avaliar
    results = evaluate_games(games, draws, config)

    # Melhor jogo
    best = max(results, key=lambda x: x['avg_hits'])
    print(f"     ✅ Melhor jogo: {best['numbers']} (média: {best['avg_hits']})")

    # Salvar resultado
    result = {
        "lottery": lottery_key,
        "name": config["name"],
        "latest": data.get('latest', 0),
        "total_draws": len(draws),
        "hot_numbers": hot_nums[:15],
        "cold_numbers": cold_nums[:15],
        "generated_games": results,
        "best_game": best,
        "timestamp": datetime.now().isoformat()
    }

    output_file = os.path.join(OUTPUT_DIR, f"ml_result_{lottery_key}.json")
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    return result

def main():
    parser = argparse.ArgumentParser(description='SIAOL-PRO ML Training')
    parser.add_argument('--lottery', default='all', help='Lottery to train (megasena, lotofacil, quina, or all)')
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("║  SIAOL-PRO v12.3 - TREINAMENTO ML                  ║")
    print("╚" + "=" * 60)

    lotteries = LOTTERY_CONFIG if args.lottery == 'all' else {args.lottery: LOTTERY_CONFIG.get(args.lottery)}

    if not lotteries:
        print(f"  ❌ Loteria '{args.lottery}' não reconhecida")
        return

    results = {}
    for key, config in lotteries.items():
        result = train_lottery(key, config)
        if result:
            results[key] = result

    # Salvar resumo geral
    summary = {
        "timestamp": datetime.now().isoformat(),
        "results": {k: {"name": v["name"], "latest": v["latest"]} for k, v in results.items()}
    }

    summary_file = os.path.join(OUTPUT_DIR, "ml_training_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n  ✅ Treinamento concluído!")
    print(f"  📁 Resultados salvos em: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
