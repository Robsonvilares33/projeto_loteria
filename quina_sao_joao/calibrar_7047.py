#!/usr/bin/env python3
"""
Calibração para concurso 7047
Inclui resultados 7045 e 7046
"""

import json
from collections import Counter

# Resultado 7045
RESULTADO_7045 = [12, 13, 17, 54, 71]

# Resultado 7046
RESULTADO_7046 = [2, 12, 37, 68, 76]

def load_history():
    """Carrega histórico"""
    with open("data/quina_history.json", 'r') as f:
        data = json.load(f)
    return data

def calculate_hot_cold(history, recent_count=50):
    """Calcula hot e cold numbers baseado nos últimos N concursos"""
    # Pegar os últimos N concursos
    recent = history[-recent_count:] if len(history) >= recent_count else history

    # Adicionar resultados 7045 e 7046 se ainda não estiverem
    all_results = list(recent)
    if all_results[-1] != RESULTADO_7046:
        all_results.append(RESULTADO_7046)
    if all_results[-1] != RESULTADO_7045 and len(all_results) >= 2:
        # Inserir 7045 antes de 7046
        pass

    # Contar frequência de cada número
    all_numbers = []
    for result in all_results:
        all_numbers.extend(result)

    counter = Counter(all_numbers)

    # Top 15 mais frequentes = HOT
    hot = [num for num, count in counter.most_common(15)]

    # Bottom 15 menos frequentes = COLD
    cold = [num for num, count in counter.most_common()[-15:]]

    return hot, cold

def main():
    print("=" * 70)
    print("CALIBRAÇÃO PARA CONCURSO 7047")
    print("=" * 70)

    # Carregar histórico
    data = load_history()
    history = data['concursos']

    print(f"\n Histórico carregado: {len(history)} concursos")

    # Adicionar resultado 7045 e 7046 se necessário
    if len(history) >= 7045:
        # já tem 7045, verificar se tem 7046
        if history[-1] != RESULTADO_7046:
            history.append(RESULTADO_7046)
            data['total_concursos'] = 7046
            data['last_update'] = '2026-06-10'
    else:
        # Adicionar ambos
        if history[-1] != RESULTADO_7045:
            history.append(RESULTADO_7045)
        history.append(RESULTADO_7046)
        data['total_concursos'] = 7046
        data['last_update'] = '2026-06-10'

    # Calcular hot/cold
    hot, cold = calculate_hot_cold(history, recent_count=50)

    print(f"\n🔥 HOT NUMBERS (Top 15 - Últimos 50 concursos):")
    print(f"   {hot}")

    print(f"\n❄️ COLD NUMBERS (Bottom 15 - Últimos 50 concursos):")
    print(f"   {cold}")

    # Pool de 18 dezenas
    pool_hot = hot[:12]
    pool_cold = cold[:6]
    pool = sorted(pool_hot + pool_cold)

    print(f"\n📊 POOL DE 18 DEZENAS:")
    print(f"   {pool}")

    # Salvar histórico atualizado
    with open("data/quina_history.json", 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Histórico atualizado com concurso 7046")

    # Salvar configuração calibrada
    calibracao = {
        'calibrado_para': 7047,
        'ultimos_resultados': [RESULTADO_7045, RESULTADO_7046],
        'hot_numbers': hot,
        'cold_numbers': cold,
        'pool_18': pool
    }

    with open("memory/calibracao_7047.json", 'w') as f:
        json.dump(calibracao, f, indent=2)

    print(f"✅ Calibração salva para concurso 7047")

    print("\n" + "=" * 70)
    print("AGORA GERE OS JOGOS COM ESTA NOVA CALIBRAÇÃO!")
    print("=" * 70)

if __name__ == "__main__":
    main()