#!/usr/bin/env python3
"""
SIAOL-PRO v12.9 - ANÁLISE COM IA (GROQ)
Usa modelo Llama para gerar insights inteligentes
"""
import os
import sys
import json
import requests
from datetime import datetime
from collections import Counter

# Config
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
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
        r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{api_endpoint}/latest", timeout=10)
        if r.status_code == 200:
            latest = r.json().get('concurso', 0)
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
    except:
        pass
    return draws

def analyze_with_groq(lottery_name, draws, hot_numbers, cold_numbers):
    """Gera análise inteligente usando Groq API"""
    if not GROQ_API_KEY:
        return None

    if len(draws) < 20:
        return None

    # Preparar dados
    all_nums = []
    for d in draws:
        all_nums.extend(d)

    freq = Counter(all_nums)
    total = len(all_nums)

    # Estatísticas
    stats = {
        "total_draws": len(draws),
        "most_frequent": freq.most_common(5),
        "least_frequent": freq.most_common()[-5:],
        "recent_pattern": [d for d in draws[:5]]
    }

    # Prompt para IA
    prompt = f"""Você é um especialista em análise de loterias. Analise os dados da {lottery_name}:

DADOS:
- Últimos {len(draws)} sorteios
- Números mais frequentes: {stats['most_frequent']}
- Números menos frequentes: {stats['least_frequent']}
- Último sorteio: {draws[0] if draws else 'N/A'}

Sua tarefa:
1. Identificar padrões ocultos
2. Sugerir estratégia de jogos
3. Dar insights únicos que outros não veriam
4. Listar 5 números com maior probabilidade para HOJE

Responda em PORTUGUÊS, de forma direta e útil. Máximo 300 palavras."""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 500
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"   ⚠️ Groq API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"   ⚠️ Erro: {e}")
        return None

def main():
    print("=" * 60)
    print("SIAOL-PRO - ANÁLISE COM INTELIGÊNCIA ARTIFICIAL")
    print("=" * 60)

    if not GROQ_API_KEY:
        print("\n⚠️ AVISO: GROQ_API_KEY não configurada!")
        print("   Configure a variável de ambiente para usar IA.")
        print("   No GitHub: Settings > Secrets > Actions")
        print("   Adicione: GROQ_API_KEY = sua_chave")
        return

    print(f"\n🤖 Usando Groq API (Llama 3.1)")

    all_analyses = {}

    for key, config in LOTTERIES.items():
        print(f"\n📊 Analisando {config['name']}...")

        draws = fetch_recent_draws(config['api_endpoint'], count=100)
        if not draws:
            print(f"   ⚠️ Sem dados")
            continue

        print(f"   ✅ {len(draws)} sorteios carregados")

        # Análise estatística
        all_nums = []
        for d in draws:
            all_nums.extend(d)

        freq = Counter(all_nums)
        expected = len(all_nums) / config['range']

        hot = [n for n, c in freq.items() if c > expected * 1.1][:10]
        cold = [n for n, c in freq.items() if c < expected * 0.9][-10:]

        print(f"   🔥 Quentes: {hot[:5]}")
        print(f"   ❄️ Frios: {cold[:5]}")

        # Análise com IA
        print(f"   🤖 Gerando insights com IA...")
        ai_analysis = analyze_with_groq(config['name'], draws, hot, cold)

        if ai_analysis:
            print(f"   ✅ Análise IA gerada!")
            all_analyses[key] = {
                "name": config['name'],
                "draws": len(draws),
                "hot_numbers": hot,
                "cold_numbers": cold,
                "ai_insights": ai_analysis,
                "timestamp": datetime.now().isoformat()
            }

            # Salvar análise individual
            with open(os.path.join(OUTPUT_DIR, f"ai_analysis_{key}.json"), 'w') as f:
                json.dump(all_analyses[key], f, indent=2)

    # Salvar resumo geral
    if all_analyses:
        summary = {
            "generated_at": datetime.now().isoformat(),
            "model": "groq-llama-3.1-8b-instant",
            "analyses": all_analyses
        }

        with open(os.path.join(OUTPUT_DIR, "ai_analyses_summary.json"), 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Análises salvas em: output/")
        print("\n📋 RESUMO DAS ANÁLISES IA:")
        print("-" * 60)
        for key, data in all_analyses.items():
            print(f"\n🎰 {data['name']}:")
            print(data['ai_insights'][:500] + "..." if len(data['ai_insights']) > 500 else data['ai_insights'])

if __name__ == "__main__":
    main()
