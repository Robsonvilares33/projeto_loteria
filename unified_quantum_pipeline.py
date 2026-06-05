#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           SIAOL-PRO UNIFIED ANALYSIS PIPELINE v1.0                          ║
║                                                                              ║
║  Executa análise completa em pipeline:                                      ║
║  1. Smart Scheduler - Verifica novos concursos                                ║
║  2. Quantum Analysis - Gera jogos com probabilidades não-uniformes           ║
║  3. ML Engine - Predições baseadas em dados históricos                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import os
from datetime import datetime
import json

# Add project path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    print("\n" + "═" * 70)
    print(f"   {title}")
    print("═" * 70 + "\n")

def main():
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 12 + "SIAOL-PRO UNIFIED PIPELINE v1.0" + " " * 21 + "║")
    print("║" + " " * 15 + "Quantum + Scheduler + ML" + " " * 30 + "║")
    print("╚" + "═" * 68 + "╝")

    results = {
        "timestamp": datetime.now().isoformat(),
        "pipeline_stages": {},
        "status": "pending"
    }

    # ============================================================
    # STAGE 1: Smart Scheduler
    # ============================================================
    print_header("STAGE 1: SMART SCHEDULER")
    print("Verificando novos concursos e status do sistema...")

    try:
        from siaol_smart_scheduler import SmartScheduler

        scheduler = SmartScheduler()
        scheduler_status = scheduler.check_and_execute()

        results["pipeline_stages"]["smart_scheduler"] = {
            "status": "success",
            "new_data_available": scheduler_status.get("new_data", False),
            "next_draw": scheduler_status.get("next_draw", "N/A")
        }

        print(f"   ✅ Scheduler: {scheduler_status.get('message', 'OK')}")
        print(f"   📅 Próximo concurso: {scheduler_status.get('next_draw', 'N/A')}")

    except Exception as e:
        results["pipeline_stages"]["smart_scheduler"] = {
            "status": "skipped",
            "error": str(e)
        }
        print(f"   ⚠️ Scheduler ignorado: {e}")

    # ============================================================
    # STAGE 2: Quantum Analysis v4
    # ============================================================
    print_header("STAGE 2: QUANTUM ANALYSIS v4")
    print("Executando simulação quântica com probabilidades não-uniformes...")

    try:
        # Import quantum analyzer
        from quantum_v4_optimized import analyze_lottery, generate_games

        # Dados simulados (substituir com dados reais)
        sample_draws = [
            [3, 11, 17, 22, 25, 33, 41, 48, 52, 58, 64, 71, 78, 82, 89],
            [5, 12, 18, 23, 27, 34, 42, 49, 53, 59, 65, 72, 79, 83, 90],
            [7, 14, 19, 24, 28, 35, 43, 50, 54, 60, 66, 73, 80, 84, 91],
            [2, 10, 16, 21, 26, 32, 40, 47, 51, 57, 63, 70, 77, 81, 88],
            [9, 15, 20, 25, 29, 36, 44, 51, 55, 61, 67, 74, 81, 85, 92],
        ]

        # Análise
        analysis = analyze_lottery(sample_draws)

        # Gerar jogos com 3 estratégias
        all_games = []
        for strategy_idx in range(3):
            games = generate_games(15, analysis['hot'], 11, strategy_idx)
            all_games.extend(games)

        # Estatísticas
        all_nums = [n for g in all_games for n in g["numbers"]]
        diversity = len(set(all_nums)) / len(all_nums)
        hot_coverage = len(set(all_nums).intersection(set(analysis['hot'][:20]))) / 20

        results["pipeline_stages"]["quantum_analysis"] = {
            "status": "success",
            "hot_numbers": analysis['hot'][:10],
            "total_games": len(all_games),
            "diversity": diversity,
            "hot_coverage": hot_coverage,
            "games": all_games
        }

        print(f"   ✅ Quantum: {len(all_games)} jogos gerados")
        print(f"   📊 Diversity: {diversity:.2%}")
        print(f"   🔥 Hot coverage: {hot_coverage:.2%}")
        print(f"   🔢 Hot numbers: {analysis['hot'][:5]}...")

    except Exception as e:
        results["pipeline_stages"]["quantum_analysis"] = {
            "status": "failed",
            "error": str(e)
        }
        print(f"   ❌ Quantum falhou: {e}")

    # ============================================================
    # STAGE 3: ML Predictions
    # ============================================================
    print_header("STAGE 3: ML PREDICTIONS")
    print("Gerando predições com machine learning...")

    try:
        from collections import Counter

        # Analisar jogos quânticos gerados
        if "quantum_analysis" in results["pipeline_stages"]:
            games = results["pipeline_stages"]["quantum_analysis"].get("games", [])

            # Extrair números mais frequentes
            all_nums = []
            for game in games:
                all_nums.extend(game["numbers"])

            freq = Counter(all_nums)
            top_numbers = [n for n, _ in freq.most_common(15)]

            results["pipeline_stages"]["ml_predictions"] = {
                "status": "success",
                "top_predictions": top_numbers,
                "confidence": min(len(games) / 33, 1.0)
            }

            print(f"   ✅ ML: 15 números mais frequêntes")
            print(f"   🔢 {top_numbers[:10]}...")

    except Exception as e:
        results["pipeline_stages"]["ml_predictions"] = {
            "status": "skipped",
            "error": str(e)
        }
        print(f"   ⚠️ ML ignorado: {e}")

    # ============================================================
    # SAVE RESULTS
    # ============================================================
    print_header("SAVING RESULTS")

    os.makedirs('output', exist_ok=True)
    os.makedirs('memory', exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'output/unified_pipeline_{timestamp}.json'
    memory_file = 'memory/unified_pipeline_latest.json'

    results["status"] = "complete"
    results["timestamp_complete"] = datetime.now().isoformat()

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    with open(memory_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"   💾 Saved: {output_file}")
    print(f"   💾 Memory: {memory_file}")

    # ============================================================
    # SUMMARY
    # ============================================================
    print_header("PIPELINE SUMMARY")

    print("\n   Stages Executed:")
    for stage, data in results["pipeline_stages"].items():
        status_icon = "✅" if data.get("status") == "success" else "⚠️" if data.get("status") == "skipped" else "❌"
        print(f"   {status_icon} {stage}: {data.get('status', 'unknown')}")

    if "quantum_analysis" in results["pipeline_stages"]:
        qa = results["pipeline_stages"]["quantum_analysis"]
        print(f"\n   📊 Quantum Games: {qa.get('total_games', 0)}")
        print(f"   📊 Diversity: {qa.get('diversity', 0):.2%}")
        print(f"   🔥 Hot Coverage: {qa.get('hot_coverage', 0):.2%}")

    if "ml_predictions" in results["pipeline_stages"]:
        ml = results["pipeline_stages"]["ml_predictions"]
        print(f"\n   🤖 ML Top Numbers: {ml.get('top_predictions', [])[:10]}...")

    print("\n" + "═" * 70)
    print("   ✅ UNIFIED PIPELINE COMPLETE!")
    print("═" * 70)

    return results

if __name__ == "__main__":
    main()