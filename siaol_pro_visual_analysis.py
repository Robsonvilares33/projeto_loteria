#!/usr/bin/env python3
"""
SIAOL-PRO v12.9 - ANÁLISE VISUAL
Gera gráficos e visualizações para o ciclo diário
"""
import os
import json
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime

# Config
OUTPUT_DIR = "/workspace/projeto_loteria/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOTTERIES = {
    "megasena": {"name": "Mega-Sena", "pick": 6, "range": 60, "api_endpoint": "megasena"},
    "lotofacil": {"name": "Lotofácil", "pick": 15, "range": 25, "api_endpoint": "lotofacil"},
    "quina": {"name": "Quina", "pick": 5, "range": 80, "api_endpoint": "quina"}
}

def fetch_recent_draws(api_endpoint, count=100):
    """Busca últimos sorteios da API"""
    draws = []
    try:
        # Buscar último
        r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{api_endpoint}/latest", timeout=10)
        if r.status_code == 200:
            latest = r.json().get('concurso', 0)
            # Buscar anteriores
            for c in range(latest, max(latest - count, 0), -1):
                r2 = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{api_endpoint}/{c}", timeout=5)
                if r2.status_code == 200:
                    data = r2.json()
                    dezenas = data.get('dezenas', [])
                    if dezenas:
                        nums = sorted([int(d) for d in dezenas[:10] if d.isdigit()])
                        draws.append(nums)
                if len(draws) >= count:
                    break
    except Exception as e:
        print(f"Erro buscando {api_endpoint}: {e}")
    return draws

def plot_frequency_chart(draws, config, filename):
    """Gera gráfico de frequência"""
    if not draws:
        return None

    all_nums = []
    for d in draws:
        all_nums.extend(d)

    freq = Counter(all_nums)

    # Preparar dados
    numbers = list(range(1, config['range'] + 1))
    frequencies = [freq.get(n, 0) for n in numbers]
    expected = len(all_nums) / config['range']

    # Criar figura
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ['#FF6B6B' if f > expected * 1.1 else '#4ECDC4' if f < expected * 0.9 else '#95A5A6'
              for f in frequencies]

    bars = ax.bar(numbers, frequencies, color=colors, edgecolor='white', linewidth=0.5)

    ax.axhline(y=expected, color='#E74C3C', linestyle='--', linewidth=2, label=f'Esperado: {expected:.1f}')

    ax.set_xlabel('Número', fontsize=12)
    ax.set_ylabel('Frequência', fontsize=12)
    ax.set_title(f'{config["name"]} - Frequência (últimos {len(draws)} sorteios)', fontsize=14, fontweight='bold')

    # Destacar top 5
    top5 = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
    for n, f in top5:
        if n <= config['range']:
            bars[n-1].set_edgecolor('#2C3E50')
            bars[n-1].set_linewidth(2)

    ax.legend()
    ax.set_xlim(0, config['range'] + 1)

    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close()

    return filepath

def plot_evolution_chart(draws, config, filename):
    """Gera gráfico de evolução temporal"""
    if len(draws) < 10:
        return None

    fig, ax = plt.subplots(figsize=(12, 6))

    # Calcular média móvel (últimos 10 sorteios)
    avg_by_draw = []
    for i in range(10, len(draws)):
        window = draws[i-10:i]
        all_nums = [n for d in window for n in d]
        freq = Counter(all_nums)
        avg = sum(freq.values()) / len(freq) if freq else 0
        avg_by_draw.append(avg)

    ax.plot(range(10, len(draws)), avg_by_draw, color='#3498DB', linewidth=2, marker='o', markersize=3)

    ax.set_xlabel('Concurso (últimos)', fontsize=12)
    ax.set_ylabel('Números Únicos (média móvel 10)', fontsize=12)
    ax.set_title(f'{config["name"]} - Evolução da Diversidade', fontsize=14, fontweight='bold')

    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close()

    return filepath

def plot_hot_cold_pie(draws, config, filename):
    """Gráfico de pizza: quente vs frio vs neutro"""
    if not draws:
        return None

    all_nums = []
    for d in draws:
        all_nums.extend(d)

    freq = Counter(all_nums)
    total = len(all_nums) / config['range']

    hot = sum(1 for n, c in freq.items() if c > total * 1.1)
    cold = sum(1 for n, c in freq.items() if c < total * 0.9)
    neutral = config['range'] - hot - cold

    fig, ax = plt.subplots(figsize=(8, 8))

    sizes = [hot, neutral, cold]
    labels = [f'Quentes\n({hot})', f'Neutros\n({neutral})', f'Frios\n({cold})']
    colors = ['#FF6B6B', '#95A5A6', '#4ECDC4']
    explode = (0.05, 0, 0.05)

    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
           shadow=True, startangle=90, textprops={'fontsize': 11})

    ax.set_title(f'{config["name"]} - Distribuição Quente/Frio/Neutro', fontsize=14, fontweight='bold')

    filepath = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close()

    return filepath

def generate_summary_report(draws, config):
    """Gera relatório resumido"""
    if not draws:
        return {}

    all_nums = []
    for d in draws:
        all_nums.extend(d)

    freq = Counter(all_nums)
    total = len(all_nums) / config['range']

    hot = [n for n, c in freq.items() if c > total * 1.1][:10]
    cold = [n for n, c in freq.items() if c < total * 0.9][-10:]

    return {
        "lottery": config["name"],
        "draws_analyzed": len(draws),
        "hot_numbers": hot,
        "cold_numbers": sorted(cold),
        "expected_frequency": round(total, 2),
        "timestamp": datetime.now().isoformat()
    }

def main():
    print("=" * 60)
    print("SIAOL-PRO - GERAÇÃO DE ANÁLISE VISUAL")
    print("=" * 60)

    reports = []

    for key, config in LOTTERIES.items():
        print(f"\n📊 Processando {config['name']}...")

        # Buscar dados
        draws = fetch_recent_draws(config['api_endpoint'], count=100)
        print(f"   ✅ {len(draws)} sorteios carregados")

        if draws:
            # Gerar gráficos
            print("   📈 Gerando gráficos...")

            f1 = plot_frequency_chart(draws, config, f"freq_{key}.png")
            if f1:
                print(f"      ✅ Frequência: {os.path.basename(f1)}")

            f2 = plot_evolution_chart(draws, config, f"evolution_{key}.png")
            if f2:
                print(f"      ✅ Evolução: {os.path.basename(f2)}")

            f3 = plot_hot_cold_pie(draws, config, f"hotcold_{key}.png")
            if f3:
                print(f"      ✅ Pizza: {os.path.basename(f3)}")

            # Gerar relatório
            report = generate_summary_report(draws, config)
            reports.append(report)

            print(f"   🔥 Top 5 quentes: {report['hot_numbers'][:5]}")
            print(f"   ❄️ Top 5 frios: {report['cold_numbers'][:5]}")

    # Salvar relatório geral
    summary = {
        "generated_at": datetime.now().isoformat(),
        "lotteries": reports
    }

    summary_file = os.path.join(OUTPUT_DIR, "visual_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✅ Análise visual concluída!")
    print(f"📁 Relatório: {summary_file}")
    print(f"📁 Gráficos: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()