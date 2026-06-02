#!/usr/bin/env python3
"""
SIAOL-PRO - VERSÃO OTIMIZADA PARA GITHUB ACTIONS
=================================================
Script simplificado para rodar no GitHub Actions
- Usa variáveis de ambiente diretamente
- Mínimo de dependências
- Logging detalhado
"""
import os
import sys
import json
import math
import random
import requests
from datetime import datetime
from collections import Counter

# Configuração
PROJECT_DIR = "/workspace/projeto_loteria"
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configurações das loterias
LOTTERIES = {
    "megasena": {"name": "Mega-Sena", "pick": 6, "range": 60, "api_endpoint": "megasena"},
    "lotofacil": {"name": "Lotofácil", "pick": 15, "range": 25, "api_endpoint": "lotofacil"},
    "quina": {"name": "Quina", "pick": 5, "range": 80, "api_endpoint": "quina"}
}

MAX_DRAWS = 300  # Reduzido para ser mais rápido

# ============================================================
# FUNÇÕES
# ============================================================

def log(msg):
    """Log com timestamp"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

def send_telegram(token, chat_id, message):
    """Envia mensagem para o Telegram"""
    if not token or not chat_id or chat_id == 'SEU_CHAT_ID_AQUI':
        log("❌ Telegram não configurado")
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
        r = requests.post(url, data=data, timeout=15)
        if r.status_code == 200:
            log(f"✅ Mensagem enviada")
            return True
        else:
            log(f"❌ Erro Telegram: {r.status_code}")
            return False
    except Exception as e:
        log(f"❌ Erro Telegram: {e}")
        return False

def api_latest(endpoint):
    """Busca último concurso"""
    try:
        r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{endpoint}/latest", timeout=15)
        if r.status_code == 200:
            return r.json().get('concurso', 0)
    except Exception as e:
        log(f"⚠️ Erro API: {e}")
    return 0

def api_contest(endpoint, contest):
    """Busca concurso específico"""
    try:
        r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{endpoint}/{contest}", timeout=15)
        if r.status_code == 200:
            dezenas = r.json().get('dezenas', [])
            if dezenas:
                return sorted([int(x) for x in dezenas])
    except:
        pass
    return None

def sync_lottery(lottery_key, config):
    """Sincroniza dados de uma loteria"""
    log(f"  🎰 {config['name']}")

    latest = api_latest(config["api_endpoint"])
    if not latest:
        log("    ⚠️ Falha API")
        return None

    log(f"    📊 Último: {latest}")

    draws = []
    start = max(1, latest - MAX_DRAWS + 1)

    for c in range(latest, start - 1, -1):
        nums = api_contest(config["api_endpoint"], c)
        if nums:
            draws.append(nums)
        if len(draws) >= MAX_DRAWS:
            break

    log(f"    ✅ {len(draws)} sorteios")
    return {"latest": latest, "draws": draws, "resultado": draws[0] if draws else []}

def generate_games(config, draws, num_games=10):
    """Gera jogos baseados em frequência"""
    if len(draws) < 10:
        return []

    all_nums = [n for draw in draws for n in draw]
    freq = Counter(all_nums)
    total = sum(freq.values())

    weights = {}
    for num in range(1, config["range"] + 1):
        f = freq.get(num, 0)
        weights[num] = (f / total) * 100 if total > 0 else 0.1

    avg_w = sum(weights.values()) / len(weights)
    hot = [n for n, w in weights.items() if w > avg_w * 1.2]
    if len(hot) < 6:
        hot = [n for n, w in sorted(weights.items(), key=lambda x: x[1], reverse=True)[:20]]

    games = []
    all_range = list(range(1, config["range"] + 1))

    for i in range(num_games):
        if i < len(hot) // 2:
            selected = sorted(random.sample(hot, min(config["pick"], len(hot))))
        else:
            selected = sorted(random.sample(all_range, config["pick"]))

        games.append({
            "game_id": i + 1,
            "numbers": selected,
            "hits": len(set(selected) & set(draws[0])) if draws else 0
        })

    return games

def check_games(games, resultado):
    """Confere jogos"""
    for g in games:
        g["hits"] = len(set(g["numbers"]) & set(resultado))
    return games

# ============================================================
# MAIN
# ============================================================

def main():
    log("=" * 50)
    log("SIAOL-PRO - GitHub Actions")
    log("=" * 50)

    # Carregar Telegram
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

    log(f"🔍 Token: {'✅' if token else '❌'}")
    log(f"🔍 Chat ID: {'✅' if chat_id else '❌'}")

    if not token or not chat_id:
        log("❌ Telegram não configurado - abortando")
        return 1

    # Enviar mensagem inicial
    msg = f"""🤖 <b>SIAOL-PRO - INICIANDO</b>
━━━━━━━━━━━━━━━━━━━━
✅ Ciclo iniciando no GitHub Actions
📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔧 Status: Processando..."""
    send_telegram(token, chat_id, msg)

    results = []

    for lottery_key, config in LOTTERIES.items():
        log(f"\n🎰 Processando {config['name']}...")

        data = sync_lottery(lottery_key, config)
        if not data or not data["draws"]:
            log("    ⚠️ Sem dados")
            continue

        games = generate_games(config, data["draws"], num_games=10)
        checked = check_games(games, data["resultado"])

        # Salvar
        with open(os.path.join(OUTPUT_DIR, f"{lottery_key}_github.json"), 'w') as f:
            json.dump({"games": checked, "resultado": data["resultado"]}, f, indent=2)

        # Enviar Telegram
        resultado_str = " - ".join(f"{n:02d}" for n in data["resultado"])
        hits_stats = Counter([g["hits"] for g in checked])
        max_hits = max([g["hits"] for g in checked])

        msg = f"""📊 <b>{config['name']}</b>
Concurso: {data['latest']}
━━━━━━━━━━━━━━━━━━━━
✅ Resultado: {resultado_str}

📈 Acertos:
"""
        for h in sorted(hits_stats.keys(), reverse=True):
            msg += f"   {h} acertos: {hits_stats[h]} jogos\n"

        msg += f"\n🏆 Melhor: {max_hits} acertos\n\n🎰 Jogos:\n"

        for g in checked[:5]:
            nums = " - ".join(f"{n:02d}" for n in g["numbers"])
            msg += f"   #{g['game_id']}: {nums} → {g['hits']} acertos\n"

        send_telegram(token, chat_id, msg)

        results.append({
            "lottery": config["name"],
            "latest": data["latest"],
            "max_hits": max_hits
        })

        log(f"    ✅ {config['name']}: {max_hits} acertos")

    # Mensagem final
    msg = f"""✅ <b>SIAOL-PRO - COMPLETO</b>
━━━━━━━━━━━━━━━━━━━━
📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 Resultados:
"""
    for r in results:
        msg += f"   {r['lottery']}: {r['max_hits']} acertos\n"

    msg += "\n🍀 Boa sorte no próximo sorteio!"
    send_telegram(token, chat_id, msg)

    log("\n✅ CICLO COMPLETO")
    return 0

if __name__ == "__main__":
    sys.exit(main())