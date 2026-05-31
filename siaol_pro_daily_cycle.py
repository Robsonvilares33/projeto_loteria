#!/usr/bin/env python3
"""
SIAOL-PRO v12.9 - CICLO DIÁRIO COMPLETO (API-ONLY)
Versão standalone para GitHub Actions
Sincroniza dados via API e executa treinamento ML
"""
import os
import sys
import json
import subprocess
import requests
from datetime import datetime

# Configurações - Portable
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOTTERIES = {
    "megasena": {"name": "Mega-Sena", "pick": 6, "range": 60, "api_endpoint": "mega-sena"},
    "lotofacil": {"name": "Lotofácil", "pick": 15, "range": 25, "api_endpoint": "lotofacil"},
    "quina": {"name": "Quina", "pick": 5, "range": 80, "api_endpoint": "quina"}
}

MAX_DRAWS = 500  # Número máximo de sorteios para análise ML

def log_message(message, log_file):
    """Registra mensagem no log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_line)
    print(message)

def api_latest(api_endpoint):
    """Busca o último concurso da API"""
    try:
        r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{api_endpoint}/latest", timeout=15)
        if r.status_code == 200:
            return r.json().get('concurso', 0)
    except Exception as e:
        print(f"   ⚠️ Erro API latest: {e}")
    return 0

def api_contest(api_endpoint, contest):
    """Busca um concurso específico da API"""
    try:
        r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{api_endpoint}/{contest}", timeout=15)
        if r.status_code == 200:
            d = r.json()
            dezenas = d.get('dezenas', [])
            if dezenas:
                nums = sorted([int(x) for x in dezenas])
                if api_endpoint == "mega-sena": max_nums = 6
                elif api_endpoint == "lotofacil": max_nums = 15
                else: max_nums = 5
                if len(nums) >= max_nums:
                    return nums[:max_nums]
    except: pass
    return None

def sync_via_api(lottery_key, config, log_file):
    """Sincroniza dados diretamente da API"""
    print(f"\n  🎰 {config['name']}")
    log_message(f"Sincronizando {config['name']} via API...", log_file)

    latest = api_latest(config["api_endpoint"])
    if not latest:
        print(f"   ⚠️ Não foi possível obter dados da API")
        return {"lottery": lottery_key, "name": config["name"], "total_draws": 0, "api_latest": 0}

    print(f"   📊 Último concurso: {latest}")

    # Buscar últimos N sorteios
    draws = []
    start = max(1, latest - MAX_DRAWS + 1)

    print(f"   🔄 Baixando sorteios {start} a {latest}...")
    for c in range(latest, start - 1, -1):
        nums = api_contest(config["api_endpoint"], c)
        if nums:
            draws.append(nums)
        if len(draws) >= MAX_DRAWS:
            break

    print(f"   ✅ {len(draws)} sorteios carregados")

    # Salvar dados em JSON para o ML
    data_file = os.path.join(OUTPUT_DIR, f"{lottery_key}_data.json")
    with open(data_file, 'w') as f:
        json.dump({"draws": draws, "latest": latest}, f)

    return {
        "lottery": lottery_key,
        "name": config["name"],
        "total_draws": len(draws),
        "api_latest": latest
    }

def run_ml_training(lottery_key):
    """Executa treinamento ML para uma loteria"""
    training_script = os.path.join(PROJECT_DIR, "siaol_pro_ml_v12_3_training.py")

    if os.path.exists(training_script):
        print(f"\n   🌲 Executando treinamento ML para {lottery_key}...")
        result = subprocess.run(
            [sys.executable, training_script, "--lottery", lottery_key],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )

        if result.stdout:
            print(result.stdout[:1000])
        if result.stderr:
            print(f"   ⚠️ Erro ML: {result.stderr[:500]}")

        return result.returncode == 0
    else:
        print(f"   ⚠️ Script de treinamento não encontrado")
        return False

def main():
    """Função principal do ciclo diário"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(OUTPUT_DIR, f"daily_cycle_{timestamp}.log")

    print("\n" + "=" * 68)
    print("║  SIAOL-PRO v12.9 - CICLO DIÁRIO COMPLETO              ║")
    print("║     Sincronização via API + Treinamento ML              ║")
    print("╚" + "=" * 68)
    print(f"  📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  📁 Projeto: {PROJECT_DIR}")
    print(f"  📁 Log: {os.path.basename(log_file)}")

    log_message("=" * 50, log_file)
    log_message("INICIANDO CICLO DIÁRIO", log_file)
    log_message(f"Estratégia: API Only", log_file)
    log_message(f"Data/Hora: {datetime.now().isoformat()}", log_file)
    log_message("=" * 50, log_file)

    # PASSO 1: Sincronização via API
    print(f"\n{'─' * 68}")
    print("  📊 PASSO 1: Sincronização via API")
    print(f"{'─' * 68}")

    update_results = []
    for lottery_key, config in LOTTERIES.items():
        result = sync_via_api(lottery_key, config, log_file)
        update_results.append(result)
        log_message(f"  {config['name']}: {result['total_draws']} sorteios (API: {result['api_latest']})", log_file)

    # PASSO 2: Treinamento ML
    print(f"\n{'─' * 68}")
    print("  🌲 PASSO 2: Treinamento de Machine Learning")
    print(f"{'─' * 68}")

    ml_success = run_ml_training("all")

    # Finalização
    print(f"\n{'=' * 68}")
    print("  ✅ CICLO DIÁRIO CONCLUÍDO")
    print(f"{'=' * 68}")

    summary = {
        "timestamp": timestamp,
        "date": datetime.now().isoformat(),
        "data_updates": update_results,
        "ml_training_success": ml_success
    }

    # Salvar relatório final
    report_path = os.path.join(OUTPUT_DIR, f"daily_report_{timestamp}.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n  📁 Relatório: daily_report_{timestamp}.json")
    print(f"  📁 Log: {os.path.basename(log_file)}")

    log_message("=" * 50, log_file)
    log_message("CICLO DIÁRIO CONCLUÍDO", log_file)
    log_message(f"ML Training: {'Sucesso' if ml_success else 'Falha'}", log_file)
    log_message("=" * 50, log_file)

    return summary

if __name__ == "__main__":
    main()
