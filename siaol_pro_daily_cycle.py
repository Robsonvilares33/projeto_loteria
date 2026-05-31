#!/usr/bin/env python3
"""
SIAOL-PRO v12.9 - CICLO DIÁRIO COMPLETO (COM SYNC HÍBRIDO)
Atualiza dados históricos E executa treinamento ML
Estratégia: API -> Excel -> TXT (sincronização automática)
"""
import sys
sys.path.insert(0, '/workspace/projeto_loteria')
import os
import json
import subprocess
import requests
from datetime import datetime
from collections import Counter, OrderedDict

# Configurações
PROJECT_DIR = "/workspace/projeto_loteria"
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOTTERIES = {
    "megasena": {
        "name": "Mega-Sena",
        "pick": 6,
        "range": 60,
        "api_endpoint": "mega-sena",
        "file_txt": "megasena-resultados-1-2954.txt",
        "file_excel": "mega_sena_asloterias_ate_concurso_2937_sorteio.xlsx"
    },
    "lotofacil": {
        "name": "Lotofácil",
        "pick": 15,
        "range": 25,
        "api_endpoint": "lotofacil",
        "file_txt": "lotofacil-resultados-1-3576.txt",
        "file_excel": "loto_facil_asloterias_ate_concurso_3533_sorteio.xlsx"
    },
    "quina": {
        "name": "Quina",
        "pick": 5,
        "range": 80,
        "api_endpoint": "quina",
        "file_txt": "quina-resultados-1-6916.txt",
        "file_excel": "quina_asloterias_ate_concurso_6873_sorteio.xlsx"
    }
}

MAX_API_CALLS = 30  # Limite de chamadas API para sincronização incremental

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
        r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{api_endpoint}/latest", timeout=10)
        if r.status_code == 200:
            return r.json().get('concurso', 0)
    except: pass
    return 0

def api_contest(api_endpoint, contest):
    """Busca um concurso específico da API"""
    try:
        r = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/{api_endpoint}/{contest}", timeout=10)
        if r.status_code == 200:
            d = r.json()
            # API retorna 'dezenas' como array de strings
            dezenas = d.get('dezenas', [])
            if dezenas:
                nums = sorted([int(x) for x in dezenas])
                # Determinar quantidade baseado na loteria
                if api_endpoint == "mega-sena": max_nums = 6
                elif api_endpoint == "lotofacil": max_nums = 15
                else: max_nums = 5  # quina
                if len(nums) >= max_nums:
                    return nums[:max_nums]
    except: pass
    return None

def load_excel(path, pick):
    """Carrega dados do Excel (pula header nas primeiras 5 linhas)"""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        draws = OrderedDict()
        # Pular header: dados começam na row 6
        for row in ws.iter_rows(min_row=6, values_only=True):
            if row and row[0] and isinstance(row[0], (int, float)):
                contest = int(row[0])
                numbers = []
                for val in row[1:pick+2]:
                    if val and isinstance(val, (int, float)):
                        n = int(val)
                        if 1 <= n <= 100:
                            numbers.append(n)
                if len(numbers) >= pick:
                    draws[contest] = sorted(numbers[:pick])
        wb.close()
        return draws
    except Exception as e:
        print(f"   ⚠️ Erro lendo Excel: {e}")
        return OrderedDict()

def load_txt(path, pick):
    """Carrega dados do TXT"""
    draws = OrderedDict()
    if not os.path.exists(path):
        return draws
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if '-' not in line:
                continue
            parts = line.strip().split('-')
            if len(parts) >= 2:
                try:
                    c = int(parts[0].strip())
                    nums = [int(n) for n in parts[1].replace(',', ' ').split() if n.strip().isdigit()]
                    if len(nums) >= pick:
                        draws[c] = sorted(nums[:pick])
                except:
                    pass
    return draws

def save_txt(path, draws, pick):
    """Salva dados no TXT"""
    with open(path, 'w', encoding='utf-8') as f:
        for c in sorted(draws.keys()):
            f.write(f"{c} - {', '.join(str(n) for n in draws[c])}\n")

def sync_lottery(lottery_key, config):
    """Sincronização híbrida: Excel + API -> TXT"""
    txt_path = os.path.join(PROJECT_DIR, config["file_txt"])
    exc_path = os.path.join(PROJECT_DIR, config["file_excel"])

    # 1. Carregar TXT atual
    local = load_txt(txt_path, config["pick"])
    local_latest = max(local.keys()) if local else 0

    # 2. Carregar Excel
    excel = load_excel(exc_path, config["pick"])
    excel_latest = max(excel.keys()) if excel else 0

    # 3. API check
    api_latest_val = api_latest(config["api_endpoint"])

    # 4. Estratégia: usar base mais recente
    merged = OrderedDict()
    if excel_latest > local_latest:
        merged.update(excel)
    else:
        merged.update(local)

    # 5. Complementar com API (máx MAX_API_CALLS)
    if api_latest_val > max(merged.keys()):
        missing = api_latest_val - max(merged.keys())
        calls = min(missing, MAX_API_CALLS)
        start = max(merged.keys()) + 1
        for c in range(start, start + calls):
            nums = api_contest(config["api_endpoint"], c)
            if nums:
                merged[c] = nums

    # 6. Salvar resultado final
    save_txt(txt_path, merged, config["pick"])
    final_latest = max(merged.keys())

    return {
        "lottery": lottery_key,
        "name": config["name"],
        "local_latest": local_latest,
        "excel_latest": excel_latest,
        "api_latest": api_latest_val,
        "final_latest": final_latest,
        "total_draws": len(merged),
        "updated": final_latest > local_latest
    }

def update_lottery_data(lottery_key, config, log_file):
    """Atualiza dados usando sincronização híbrida"""
    print(f"   🔄 Sincronizando {config['name']}...")

    result = sync_lottery(lottery_key, config)

    if result["updated"]:
        print(f"   ✅ Sincronizado: {result['final_latest']} ({result['total_draws']} sorteios)")
    else:
        print(f"   ℹ️ Dados já atualizados: {result['final_latest']}")

    return result

def load_historical_draws(lottery_key, config):
    """Carrega sorteios históricos de um arquivo"""
    file_path = os.path.join(PROJECT_DIR, config["file_txt"])

    if not os.path.exists(file_path):
        return []

    draws = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('-')
            if len(parts) >= 2:
                try:
                    nums_str = parts[1].strip().replace(',', ' ')
                    numbers = [int(n.strip()) for n in nums_str.split() if n.strip().isdigit()]
                    if len(numbers) >= config["pick"]:
                        draws.append(sorted(numbers[:config["pick"]]))
                except:
                    pass

    return draws[-500:] if len(draws) > 500 else draws

def run_ml_training():
    """Executa o script de treinamento ML"""
    training_script = os.path.join(PROJECT_DIR, "siaol_pro_ml_v12_3_training.py")

    if os.path.exists(training_script):
        print(f"\n   🌲 Executando treinamento ML...")
        result = subprocess.run(
            [sys.executable, training_script],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )

        # Print output to see any errors
        if result.stdout:
            print(result.stdout[:2000])
        if result.stderr:
            print(f"   ⚠️ Erro ML: {result.stderr[:500]}")

        if result.returncode == 0:
            print(f"   ✅ Treinamento ML concluído com sucesso")
            return True
        else:
            print(f"   ⚠️ Erro no treinamento ML")
            return False
    else:
        print(f"   ⚠️ Script de treinamento não encontrado")
        return False

def main():
    """Função principal do ciclo diário"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(OUTPUT_DIR, f"daily_cycle_{timestamp}.log")

    print("\n" + "=" * 68)
    print("║  SIAOL-PRO v12.9 - CICLO DIÁRIO COMPLETO              ║")
    print("║     Sincronização Híbrida + Treinamento ML            ║")
    print("╚" + "=" * 68)
    print(f"  📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  📁 Log: {os.path.basename(log_file)}")

    log_message("=" * 50, log_file)
    log_message("INICIANDO CICLO DIÁRIO", log_file)
    log_message(f"Estratégia: Excel + API -> TXT", log_file)
    log_message(f"Data/Hora: {datetime.now().isoformat()}", log_file)
    log_message("=" * 50, log_file)

    # PASSO 1: Sincronização híbrida dos dados
    print(f"\n{'─' * 68}")
    print("  📊 PASSO 1: Sincronização Híbrida de Dados")
    print(f"{'─' * 68}")

    update_results = []
    for lottery_key, config in LOTTERIES.items():
        print(f"\n  🎰 {config['name']}")
        log_message(f"Sincronizando {config['name']}...", log_file)

        sync_result = update_lottery_data(lottery_key, config, log_file)
        update_results.append(sync_result)

        log_message(f"  {config['name']}: {sync_result['total_draws']} sorteios (final: {sync_result['final_latest']})", log_file)

    # PASSO 2: Executar treinamento ML
    print(f"\n{'─' * 68}")
    print("  🌲 PASSO 2: Treinamento de Machine Learning")
    print(f"{'─' * 68}")

    ml_success = run_ml_training()

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
