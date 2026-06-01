#!/usr/bin/env python3
"""
SIAOL-PRO v12.9 - ANÁLISE COM IA (MINIMAX)
Usa modelo MiniMax para gerar insights inteligentes
"""
import os
import json
import requests
from datetime import datetime
from collections import Counter

# Config
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
OUTPUT_DIR = "/workspace/projeto_loteria/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOTTERIES = {
    "megasena": {"name": "Mega-Sena", "pick": 6, "range": 60, "api_endpoint": "megasena"},
    "lotofacil": {"name": "Lotofácil", "pick": 15, "range": 25, "api_endpoint": "lotofacil"},
    "quina": {"name": "Quina", "pick": 5, "range": 80, "api_endpoint": "quina"}
}

def fetch_recent_draws(api_endpoint, count=50):
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

def analyze_with_minimax(lottery_name, draws, hot_numbers, cold_numbers):
    """Gera análise inteligente usando MiniMax API"""
    if not MINIMAX_API_KEY:
        return None

    if len(draws) < 10:
        return None

    all_nums = []
    for d in draws:
        all_nums.extend(d)

    freq = Counter(all_nums)

    stats = {
        "total_draws": len(draws),
        "most_frequent": freq.most_common(5),
        "least_frequent": freq.most_common()[-5:],
        "recent_pattern": [d for d in draws[:3]]
    }

    prompt = f"""Você é um especialista em análise de loterias brasileiras. Analise os dados da {lottery_name}:

DADOS:
- Últimos {len(draws)} sorteios
- Números mais frequentes: {stats['most_frequent']}
- Números menos frequentes: {stats['least_frequent']}
- Últimos 3 sorteios: {stats['recent_pattern']}

Sua tarefa:
1. Identificar padrões ocultos nos últimos sorteios
2. Sugerir estratégia de jogos baseada nos dados
3. Listar 5 números com maior probabilidade para HOJE
4. Analisar se há padrão de sequência ou distribuição

Responda em PORTUGUÊS, de forma direta. Máximo 250 palavras."""

    try:
        response = requests.post(
            "https://api.minimax.chat/v1/text/chatcompletion_pro?GroupId=__",
            headers={
                "Authorization": f"Bearer {MINIMAX_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "abab6.5-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return result.get('choices', [{}])[0].get('messages', [{}])[0].get('text', '')
        else:
            return None
    except:
        return None

def main():
    print("=" * 60)
    print("SIAOL-PRO - ANÁLISE COM INTELIGÊNCIA ARTIFICIAL (MINIMAX)")
    print("=" * 60)

    if not MINIMAX_API_KEY:
        print("\n⚠️ AVISO: MINIMAX_API_KEY não configurada!")
        return

    print(f"\n🤖 Usando MiniMax API")

    all_analyses = {}

    for key, config in LOTTERIES.items():
        print(f"\n📊 Analisando {config['name']}...")

        draws = fetch_recent_draws(config['api_endpoint'], count=50)
        if not draws:
            continue

        print(f"   ✅ {len(draws)} sorteios carregados")

        all_nums = []
        for d in draws:
            all_nums.extend(d)

        freq = Counter(all_nums)
        expected = len(all_nums) / config['range']

        hot = [n for n, c in freq.items() if c > expected * 1.1][:10]
        cold = [n for n, c in freq.items() if c < expected * 0.9][-10:]

        print(f"   🔥 Quentes: {hot[:5]}")
        print(f"   ❄️ Frios: {cold[:5]}")

        print(f"   🤖 Gerando insights com IA...")
        ai_analysis = analyze_with_minimax(config['name'], draws, hot, cold)

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

            with open(os.path.join(OUTPUT_DIR, f"minimax_analysis_{key}.json"), 'w') as f:
                json.dump(all_analyses[key], f, indent=2, ensure_ascii=False)

    if all_analyses:
        summary = {
            "generated_at": datetime.now().isoformat(),
            "model": "minimax-abab6.5",
            "analyses": all_analyses
        }

        with open(os.path.join(OUTPUT_DIR, "minimax_analyses_summary.json"), 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Análises salvas em: output/")

if __name__ == "__main__":
    main()
