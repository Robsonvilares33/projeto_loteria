#!/usr/bin/env python3
"""
Calibração para concurso 7048
Inclui resultados 7045, 7046 e 7047
"""

import json
from collections import Counter

# Resultados recentes
RESULTADO_7045 = [12, 13, 17, 54, 71]
RESULTADO_7046 = [2, 12, 37, 68, 76]
RESULTADO_7047 = [6, 11, 26, 50, 61]

def load_history():
    """Carrega histórico"""
    with open("data/quina_history.json", 'r') as f:
        data = json.load(f)
    return data

def calculate_hot_cold(history, recent_count=50):
    """Calcula hot e cold numbers baseado nos últimos N concursos"""
    recent = history[-recent_count:] if len(history) >= recent_count else history

    # Contar frequência de cada número
    all_numbers = []
    for result in recent:
        all_numbers.extend(result)

    counter = Counter(all_numbers)

    # Top 15 mais frequentes = HOT
    hot = [num for num, count in counter.most_common(15)]

    # Bottom 15 menos frequentes = COLD
    cold = [num for num, count in counter.most_common()[-15:]]

    return hot, cold

def main():
    print("=" * 70)
    print("CALIBRAÇÃO PARA CONCURSO 7048")
    print("=" * 70)

    # Carregar histórico
    data = load_history()
    history = data['concursos']

    print(f"\n Histórico carregado: {len(history)} concursos")

    # Adicionar resultado 7047 se necessário
    if len(history) >= 7047:
        if history[-1] != RESULTADO_7047:
            history.append(RESULTADO_7047)
            data['total_concursos'] = 7047
            data['last_update'] = '2026-06-10'
    else:
        history.append(RESULTADO_7047)
        data['total_concursos'] = 7047
        data['last_update'] = '2026-06-10'

    # Calcular hot/cold
    hot, cold = calculate_hot_cold(history, recent_count=50)

    print(f"\n🔥 HOT NUMBERS (Top 15 - Últimos 50 concursos):")
    print(f"   {hot}")

    print(f"\n❄️ COLD NUMBERS (Bottom 15 - Últimos 50 concursos):")
    print(f"   {cold}")

    # Pool de 18 dezenas - incluir números que saíram nos últimos 3 concursos
    recent_numbers = set()
    for r in [RESULTADO_7045, RESULTADO_7046, RESULTADO_7047]:
        recent_numbers.update(r)

    # Adicionar hot numbers ao pool
    pool_hot = [n for n in hot[:12] if n not in recent_numbers]
    pool_cold = [n for n in cold[:8] if n not in recent_numbers]

    # Completar com números recentes
    pool = sorted(list(recent_numbers) + pool_hot[:8] + pool_cold[:5])[:18]

    print(f"\n📊 POOL DE 18 DEZENAS:")
    print(f"   {pool}")

    # Salvar histórico atualizado
    with open("data/quina_history.json", 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Histórico atualizado com concurso 7047")

    # Salvar configuração calibrada
    calibracao = {
        'calibrado_para': 7048,
        'ultimos_resultados': [RESULTADO_7045, RESULTADO_7046, RESULTADO_7047],
        'hot_numbers': hot,
        'cold_numbers': cold,
        'pool_18': pool
    }

    with open("memory/calibracao_7048.json", 'w') as f:
        json.dump(calibracao, f, indent=2)

    print(f"✅ Calibração salva para concurso 7048")

    print("\n" + "=" * 70)
    print("GERANDO NOVOS JOGOS COM ESTA CALIBRAÇÃO...")
    print("=" * 70)

if __name__ == "__main__":
    main()