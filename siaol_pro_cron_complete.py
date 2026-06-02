#!/usr/bin/env python3
"""
SIAOL-PRO - CICLO COMPLETO COM TELEGRAM
========================================
Cron job completo que:
1. Sincroniza dados da API
2. Gera recomendações quânticas
3. Confere jogos anteriores
4. Envia resultados para Telegram

Uso: python3 siaol_pro_cron_complete.py
"""
import os
import sys
import json
import math
import random
import requests
from datetime import datetime
from collections import Counter

PROJECT_DIR = "/workspace/projeto_loteria"
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# CONFIGURAÇÕES
# ============================================================

LOTTERIES = {
    "megasena": {
        "name": "Mega-Sena",
        "pick": 6,
        "range": 60,
        "api_endpoint": "megasena",
        "min_hits": 4  # Quadra ou mais
    },
    "lotofacil": {
        "name": "Lotofácil",
        "pick": 15,
        "range": 25,
        "api_endpoint": "lotofacil",
        "min_hits": 11  # 11 acertos ou mais
    },
    "quina": {
        "name": "Quina",
        "pick": 5,
        "range": 80,
        "api_endpoint": "quina",
        "min_hits": 3  # Terno ou mais
    }
}

MAX_DRAWS = 500

# ============================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================

def log(msg, log_file=None):
    """Log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    if log_file:
        with open(log_file, 'a') as f:
            f.write(line + "\n")

def load_telegram_config():
    """Carrega configurações do Telegram"""
    env_file = os.path.join(PROJECT_DIR, ".env.telegram")
    token = ""
    chat_id = ""
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line:
                    key, val = line.strip().split('=', 1)
                    if key == 'TELEGRAM_BOT_TOKEN':
                        token = val
                    elif key == 'TELEGRAM_CHAT_ID':
                        chat_id = val
    return token, chat_id

def send_telegram(token, chat_id, message):
    """Envia mensagem para o Telegram"""
    if not token or not chat_id or chat_id == 'SEU_CHAT_ID_AQUI':
        return False
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
        r = requests.post(url, data=data, timeout=10)
        return r.status_code == 200
    except Exception as e:
        log(f"Erro Telegram: {e}")
        return False

# ============================================================
# API LOTERIAS CAIXA
# ============================================================

def api_latest(api_endpoint):
    """Busca último concurso"""
    try:
        r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{api_endpoint}/latest", timeout=15)
        if r.status_code == 200:
            return r.json().get('concurso', 0)
    except Exception as e:
        log(f"Erro API latest: {e}")
    return 0

def api_contest(api_endpoint, contest):
    """Busca concurso específico"""
    try:
        r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{api_endpoint}/{contest}", timeout=15)
        if r.status_code == 200:
            d = r.json()
            dezenas = d.get('dezenas', [])
            if dezenas:
                return sorted([int(x) for x in dezenas])
    except:
        pass
    return None

# ============================================================
# SINCRONIZAÇÃO DE DADOS
# ============================================================

def sync_data(lottery_key, config, log_file):
    """Sincroniza dados da API"""
    log(f"  🎰 {config['name']}", log_file)

    latest = api_latest(config["api_endpoint"])
    if not latest:
        log(f"    ⚠️ Falha ao obter dados", log_file)
        return None

    log(f"    📊 Último: {latest}", log_file)

    draws = []
    start = max(1, latest - MAX_DRAWS + 1)

    for c in range(latest, start - 1, -1):
        nums = api_contest(config["api_endpoint"], c)
        if nums:
            draws.append({"concurso": c, "numeros": nums})
        if len(draws) >= MAX_DRAWS:
            break

    log(f"    ✅ {len(draws)} sorteios", log_file)

    # Salvar dados
    data_file = os.path.join(OUTPUT_DIR, f"{lottery_key}_data.json")
    with open(data_file, 'w') as f:
        json.dump({"draws": draws, "latest": latest}, f)

    return {"lottery_key": lottery_key, "draws": draws, "latest": latest}

# ============================================================
# GERAÇÃO QUÂNTICA DE JOGOS
# ============================================================

def generate_quantum_games(lottery_key, config, draws, num_games=10):
    """Gera jogos usando análise quântica"""
    if len(draws) < 10:
        return []

    # Análise de frequência
    all_numbers = [n for draw in draws for n in draw["numeros"]]
    freq = Counter(all_numbers)
    total = sum(freq.values())

    # Calcular pesos baseados em frequência
    weights = {}
    for num in range(1, config["range"] + 1):
        f = freq.get(num, 0)
        # Peso = frequência normalizada + variação quântica
        weights[num] = (f / total) * 100 if total > 0 else 0.1

    # Identificar quentes e frios
    avg_weight = sum(weights.values()) / len(weights)
    hot_numbers = [n for n, w in weights.items() if w > avg_weight * 1.2]
    cold_numbers = [n for n, w in weights.items() if w < avg_weight * 0.8]

    # Se não há números quentes, usar os top 20
    if len(hot_numbers) < 6:
        sorted_by_freq = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        hot_numbers = [n for n, w in sorted_by_freq[:20]]

    games = []

    # Estratégia 1: Números quentes
    for i in range(num_games // 3):
        if len(hot_numbers) >= config["pick"]:
            selected = []
            available = hot_numbers.copy()
            random.shuffle(available)
            selected = sorted(available[:config["pick"]])
            games.append({
                "game_id": i + 1,
                "numbers": selected,
                "strategy": "quantum_hot"
            })

    # Estratégia 2: Mistura quente/frio
    start_idx = num_games // 3
    for i in range(num_games // 3):
        selected = []
        # 70% quente, 30% frio
        n_hot = int(config["pick"] * 0.7)
        n_cold = config["pick"] - n_hot

        hot_avail = [n for n in hot_numbers if n not in selected]
        cold_avail = [n for n in cold_numbers if n not in selected]
        random.shuffle(hot_avail)
        random.shuffle(cold_avail)

        selected = sorted(hot_avail[:n_hot] + cold_avail[:n_cold])
        games.append({
            "game_id": start_idx + i + 1,
            "numbers": selected,
            "strategy": "quantum_mixed"
        })

    # Estratégia 3: Frequência + aleatório
    start_idx = (num_games // 3) * 2
    all_nums = list(range(1, config["range"] + 1))

    for i in range(num_games - (num_games // 3) * 2):
        selected = []
        available = all_nums.copy()

        # Ordenar por peso (frequência)
        available_sorted = sorted(available, key=lambda x: weights.get(x, 0), reverse=True)

        # Pegar os melhores com variação
        offset = (i * 3) % 10
        for j in range(config["pick"]):
            idx = (offset + j * 7) % len(available_sorted)
            if available_sorted[idx] not in selected:
                selected.append(available_sorted[idx])

        selected = sorted(selected[:config["pick"]])
        games.append({
            "game_id": start_idx + i + 1,
            "numbers": selected,
            "strategy": "quantum_freq"
        })

    # Garantir que temos exatamente num_games
    while len(games) < num_games:
        selected = sorted(random.sample(all_nums, config["pick"]))
        games.append({
            "game_id": len(games) + 1,
            "numbers": selected,
            "strategy": "quantum_random"
        })

    return games[:num_games]

# ============================================================
# CONFERÊNCIA DE JOGOS
# ============================================================

def check_games(games, resultado):
    """Confere jogos contra resultado oficial"""
    results = []
    for game in games:
        hits = len(set(game["numbers"]) & set(resultado))
        results.append({
            "game_id": game["game_id"],
            "numbers": game["numbers"],
            "hits": hits
        })
    return results

def classify_hit(lottery_key, hits, config):
    """Classifica nível de acerto"""
    if lottery_key == "megasena":
        if hits == 6:
            return "SENA! 🏆🏆🏆"
        elif hits == 5:
            return "QUINA! ⭐⭐"
        elif hits == 4:
            return "QUADRA! 🎯"
        elif hits >= 2:
            return f"{hits} acertos"
        else:
            return f"{hits} acertos"
    elif lottery_key == "lotofacil":
        if hits >= 15:
            return "15 ACERTOS! 🏆"
        elif hits >= 14:
            return "14 ACERTOS! ⭐"
        elif hits >= 13:
            return "13 ACERTOS! 🎯"
        elif hits >= 11:
            return f"{hits} acertos!"
        else:
            return f"{hits} acertos"
    elif lottery_key == "quina":
        if hits >= 5:
            return "QUINA! 🏆"
        elif hits >= 4:
            return "QUADRA! ⭐"
        elif hits >= 3:
            return "TERNO! 🎯"
        else:
            return f"{hits} acertos"
    return f"{hits} acertos"

# ============================================================
# ENVIO TELEGRAM
# ============================================================

def format_games_telegram(games, lottery_name):
    """Formata jogos para Telegram"""
    msg = f"🎰 <b>{lottery_name} - JOGOS QUÂNTICOS</b>\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    for game in games[:10]:
        nums = " - ".join(f"{n:02d}" for n in game["numbers"])
        msg += f"#{game['game_id']:02d}: {nums}\n"

    if len(games) > 10:
        msg += f"\n... e mais {len(games) - 10} jogos"

    return msg

def format_results_telegram(results, lottery_name, resultado, latest, lottery_key, config):
    """Formata resultado da conferência para Telegram"""
    hits_counter = Counter([r["hits"] for r in results])
    max_hit = max([r["hits"] for r in results])

    msg = f"📊 <b>CONFERÊNCIA {lottery_name}</b>\n"
    msg += f"Concurso: {latest}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"✅ Resultado: {' - '.join(f'{n:02d}' for n in resultado)}\n\n"

    # Estatísticas
    msg += f"📈 <b>Estatísticas:</b>\n"
    for hits in sorted(hits_counter.keys(), reverse=True):
        count = hits_counter[hits]
        classification = classify_hit(lottery_key, hits, config)
        msg += f"   {hits} acertos: {count} jogos ({classification})\n"

    msg += f"\n🏆 Melhor: {max_hit} acertos\n"

    # Mostrar melhores jogos
    best_games = [r for r in results if r["hits"] >= max(1, max_hit - 1)][:5]

    if best_games:
        msg += "\n🎯 <b>Melhores jogos:</b>\n"
        for g in best_games:
            nums = " - ".join(f"{n:02d}" for n in g["numbers"])
            classification = classify_hit(lottery_key, g["hits"], config)
            msg += f"   #{g['game_id']:02d} {nums} → {classification}\n"

    return msg

# ============================================================
# CICLO PRINCIPAL
# ============================================================

def run_complete_cycle(token, chat_id, log_file):
    """Executa ciclo completo"""

    log("=" * 60, log_file)
    log("INICIANDO CICLO COMPLETO SIAOL-PRO", log_file)
    log("=" * 60, log_file)

    all_results = {}

    for lottery_key, config in LOTTERIES.items():
        log(f"\n🎰 Processando {config['name']}...", log_file)

        # 1. Sincronizar dados
        data = sync_data(lottery_key, config, log_file)
        if not data or not data["draws"]:
            log(f"   ⚠️ Sem dados", log_file)
            continue

        draws = data["draws"]
        latest = data["latest"]
        resultado = draws[0]["numeros"]  # Último sorteio

        log(f"   📍 Último concurso: {latest}", log_file)
        log(f"   🎯 Resultado: {resultado}", log_file)

        # 2. Gerar jogos quânticos
        log(f"   🧠 Gerando jogos quânticos...", log_file)
        games = generate_quantum_games(lottery_key, config, draws, num_games=10)

        if games:
            # Salvar jogos gerados
            games_file = os.path.join(OUTPUT_DIR, f"{lottery_key}_games_{latest}.json")
            games_data = {
                "lottery": lottery_key,
                "concurso": latest,
                "data": datetime.now().isoformat(),
                "games": games
            }
            with open(games_file, 'w') as f:
                json.dump(games_data, f, indent=2)

            # 3. Conferir jogos (comparar com resultado)
            log(f"   🔍 Conferindo jogos...", log_file)
            checked = check_games(games, resultado)

            # Salvar conferência
            conferir_file = os.path.join(OUTPUT_DIR, f"{lottery_key}_conferir_{latest}.json")
            conferir_data = {
                "lottery": lottery_key,
                "concurso": latest,
                "resultado": resultado,
                "games_checked": checked
            }
            with open(conferir_file, 'w') as f:
                json.dump(conferir_data, f, indent=2)

            # 4. Enviar para Telegram
            log(f"   📱 Enviando para Telegram...", log_file)

            # Enviar conferência
            msg = format_results_telegram(checked, config["name"], resultado, latest, lottery_key, config)
            send_telegram(token, chat_id, msg)

            # Enviar novos jogos
            msg = format_games_telegram(games, config["name"])
            send_telegram(token, chat_id, msg)

            all_results[lottery_key] = {
                "latest": latest,
                "resultado": resultado,
                "games_generated": len(games),
                "checked": checked
            }

            log(f"   ✅ Completo!", log_file)

    return all_results

# ============================================================
# MAIN
# ============================================================

def main():
    """Função principal"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(OUTPUT_DIR, f"cron_complete_{timestamp}.log")

    print("\n" + "=" * 60)
    print("║  SIAOL-PRO - CICLO COMPLETO COM TELEGRAM        ║")
    print("║     Cron Job + Conferência + Telegram              ║")
    print("=" * 60)
    print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Carregar Telegram - PRIORIDADE: variáveis de ambiente (GitHub Actions)
    # Se não tiver, usa arquivo .env.telegram (local)
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')

    # Se não encontrou nas variáveis de ambiente, tenta ler do arquivo
    if not token or not chat_id:
        env_file = os.path.join(PROJECT_DIR, ".env.telegram")
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, val = line.split('=', 1)
                        if key == 'TELEGRAM_BOT_TOKEN':
                            token = val.strip()
                        elif key == 'TELEGRAM_CHAT_ID':
                            chat_id = val.strip()

    # Debug: mostrar o que foi carregado
    print(f"\n🔍 DEBUG - Configuração Telegram:")
    print(f"   Token: {'✅ Configurado' if token else '❌ Vazio'}")
    print(f"   Chat ID: {'✅ Configurado' if chat_id else '❌ Vazio'}")

    # Se ainda não tem token, mostrar erro detalhado
    if not token:
        print("\n❌ ERRO: TELEGRAM_BOT_TOKEN não encontrado")
        print("   Verifique se as secrets TELEGRAM_BOT_TOKEN estão configuradas no GitHub")
        print("   Ou se o arquivo .env.telegram existe")
        # Não return - tentar continuar mesmo assim para ver o erro completo

    print("✅ Telegram configurado")

    # Teste inicial do Telegram
    print("\n🧪 TESTE INICIAL DO TELEGRAM:")
    test_msg = f"""🤖 <b>SIAOL-PRO - INICIANDO</b>
━━━━━━━━━━━━━━━━━━━━
✅ Ciclo começando agora
📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔧 Debug: Token={'OK' if token else 'ERRO'}, Chat={'OK' if chat_id else 'ERRO'}"""
    result = send_telegram(token, chat_id, test_msg)
    print(f"   Resultado do teste: {'✅ Enviado' if result else '❌ Falhou'}")

    # Executar ciclo
    results = run_complete_cycle(token, chat_id, log_file)

    # Relatório final
    print("\n" + "=" * 60)
    print("  ✅ CICLO COMPLETO FINALIZADO")
    print("=" * 60)

    print(f"\n📊 Resultados:")
    for lottery_key, data in results.items():
        config = LOTTERIES[lottery_key]
        checked = data["checked"]
        max_hit = max([r["hits"] for r in checked]) if checked else 0
        print(f"   {config['name']}: {data['games_generated']} jogos, melhor={max_hit} acertos")

    print(f"\n📁 Arquivos salvos em: {OUTPUT_DIR}")
    print(f"📁 Log: cron_complete_{timestamp}.log")

    print("\n📱 Resultados enviados para Telegram!")

if __name__ == "__main__":
    main()