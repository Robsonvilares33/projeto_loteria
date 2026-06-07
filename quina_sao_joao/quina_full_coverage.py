#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           🧠 QUINA BRAIN v3.1 - COBERTURA 100%                           ║
║                                                                            ║
║  • Opção 1: 56 jogos = R$ 168,00 (100% dezenas)                           ║
║  • Opção 2: 70 jogos = R$ 210,00 (100% + híbrido)                         ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import os
import random
from datetime import datetime
from itertools import combinations
from typing import Dict, List, Tuple

# ============================================
# CONFIGURAÇÕES
# ============================================
QUINA_PRICE = 3.00
MAX_DEZENA = 80

# ============================================
# CLASSE: COBERTURA 100% DEZENAS
# ============================================
class FullCoverageGenerator:
    """Gera portfólios com cobertura 100% de dezenas"""

    def __init__(self):
        self.hot_numbers = []
        self.cold_numbers = []

    def set_numbers(self, hot: List[int], cold: List[int]):
        self.hot_numbers = hot
        self.cold_numbers = cold

    def generate_dezena_pool(self) -> Dict[int, List[int]]:
        """Gera pool de números por dezena"""
        pool = {}
        for d in range(8):
            start = d * 10 + 1
            end = (d + 1) * 10 if d < 7 else 80

            # Prioridade: hot numbers da dezena, depois cold, depois resto
            dezenas_nums = list(range(start, end + 1))

            hot_in_dezena = [n for n in self.hot_numbers if start <= n <= end]
            cold_in_dezena = [n for n in self.cold_numbers if start <= n <= end]

            pool[d] = hot_in_dezena + cold_in_dezena
            if len(pool[d]) < 5:
                pool[d] = dezenas_nums[:10]

        return pool

    def generate_56_games(self) -> List[List[int]]:
        """Gera 56 jogos com cobertura 100% dezenas"""
        print("\n🎰 GERANDO 56 JOGOS (100% DEZENAS)...")

        # Defaults se não configurado
        if not self.hot_numbers:
            self.hot_numbers = [15, 13, 27, 12, 20, 18, 24, 1, 3, 5, 14, 35, 38, 11, 53]
        if not self.cold_numbers:
            self.cold_numbers = [69, 6, 62, 30, 72, 28, 76, 78, 74, 65, 79, 47, 77, 17, 66]

        pool = self.generate_dezena_pool()

        # Selecionar 1 número de cada dezena (8 números)
        selected = []
        for d in range(8):
            nums = pool[d]
            if nums:
                selected.append(nums[0])

        # Gerar todas combinações de 5 dos 8 selecionados
        games = []
        for combo in combinations(selected, 5):
            games.append(sorted(list(combo)))

        # Se menos de 56, completar com variações
        while len(games) < 56:
            # Trocar um número por outro da mesma dezena
            for d in range(8):
                nums = pool[d]
                if len(nums) > 1:
                    new_game = games[-1].copy()
                    # Substituir número da dezena d
                    for i, n in enumerate(new_game):
                        if (n - 1) // 10 == d and len(nums) > 1:
                            new_game[i] = nums[1] if nums[0] != n else nums[1]
                            break
                    new_game = sorted(new_game)
                    if new_game not in games:
                        games.append(new_game)
                        break

        games = games[:56]  # Garantir exatamente 56

        print(f"   ✅ {len(games)} jogos gerados")
        return games

    def generate_70_games(self) -> List[List[int]]:
        """Gera 70 jogos com cobertura 100% + híbrido"""
        print("\n🎰 GERANDO 70 JOGOS (100% + HÍBRIDO)...")

        # Defaults se não configurado
        if not self.hot_numbers:
            self.hot_numbers = [15, 13, 27, 12, 20, 18, 24, 1, 3, 5, 14, 35, 38, 11, 53]
        if not self.cold_numbers:
            self.cold_numbers = [69, 6, 62, 30, 72, 28, 76, 78, 74, 65, 79, 47, 77, 17, 66]

        pool = self.generate_dezena_pool()

        games = []

        # 56 jogos base (100% dezenas)
        selected = []
        for d in range(8):
            nums = pool[d]
            if nums:
                selected.append(nums[0])

        for combo in combinations(selected, 5):
            games.append(sorted(list(combo)))

        # Completar até 70 jogos
        target = 70
        attempts = 0
        max_attempts = 200

        while len(games) < target and attempts < max_attempts:
            attempts += 1

            # Gerar jogo híbrido: 3 hot + 2 cold/momentum
            hot_pool = self.hot_numbers[:15]
            cold_pool = self.cold_numbers[:10]

            dezenas_used = set()
            game = []

            # 3 números quentes
            for _ in range(3):
                available = [n for n in hot_pool if (n-1)//10 not in dezenas_used]
                if available:
                    n = random.choice(available[:8])
                    game.append(n)
                    dezenas_used.add((n-1)//10)

            # 2 números frios
            for _ in range(2):
                available = [n for n in cold_pool if (n-1)//10 not in dezenas_used]
                if available:
                    n = random.choice(available[:6])
                    game.append(n)
                    dezenas_used.add((n-1)//10)

            # Completar se necessário
            while len(game) < 5:
                for n in list(range(1, 81)):
                    if n not in game and (n-1)//10 not in dezenas_used:
                        game.append(n)
                        dezenas_used.add((n-1)//10)
                        break

            game = sorted(game[:5])
            if len(set(game)) == 5 and game not in games:
                games.append(game)

        games = games[:70]

        print(f"   ✅ {len(games)} jogos gerados")
        return games

    def verify_coverage(self, games: List[List[int]]) -> Dict:
        """Verifica cobertura de dezenas"""
        dezenas_covered = set()
        all_nums = set()

        for game in games:
            all_nums.update(game)
            for num in game:
                dezenas_covered.add((num - 1) // 10)

        return {
            "dezenas_covered": len(dezenas_covered),
            "total_dezenas": 8,
            "percentage": round(len(dezenas_covered) / 8 * 100, 1),
            "hot_covered": len([n for n in self.hot_numbers[:15] if n in all_nums]),
            "cold_covered": len([n for n in self.cold_numbers[:10] if n in all_nums])
        }


# ============================================
# FUNÇÃO PRINCIPAL
# ============================================
def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║     🧠 QUINA BRAIN v3.1 - COBERTURA 100%                                  ║
║                                                                            ║
║     • Opção 1: 56 jogos = R$ 168,00                                       ║
║     • Opção 2: 70 jogos = R$ 210,00                                       ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

    # Carregar números atuais
    hot_numbers = [15, 13, 27, 12, 20, 18, 24, 1, 3, 5, 14, 35, 38, 11, 53]
    cold_numbers = [69, 6, 62, 30, 72, 28, 76, 78, 74, 65, 79, 47, 77, 17, 66]

    generator = FullCoverageGenerator()
    generator.set_numbers(hot_numbers, cold_numbers)

    # ============================================
    # OPÇÃO 1: 56 JOGOS
    # ============================================
    print("\n" + "="*70)
    print("📊 OPÇÃO 1: COBERTURA 100% DEZENAS")
    print("="*70)

    games_56 = generator.generate_56_games()
    cost_56 = len(games_56) * QUINA_PRICE
    coverage_56 = generator.verify_coverage(games_56)

    print(f"\n   📊 Jogos: {len(games_56)}")
    print(f"   💰 Custo: R$ {cost_56:.2f}")
    print(f"   🌍 Dezenas: {coverage_56['dezenas_covered']}/8 ({coverage_56['percentage']}%)")
    print(f"   🔥 Hot cobertos: {coverage_56['hot_covered']}/15")
    print(f"   ❄️ Cold cobertos: {coverage_56['cold_covered']}/10")

    # ============================================
    # OPÇÃO 2: 70 JOGOS
    # ============================================
    print("\n" + "="*70)
    print("📊 OPÇÃO 2: COBERTURA 100% + HÍBRIDO")
    print("="*70)

    games_70 = generator.generate_70_games()
    cost_70 = len(games_70) * QUINA_PRICE
    coverage_70 = generator.verify_coverage(games_70)

    print(f"\n   📊 Jogos: {len(games_70)}")
    print(f"   💰 Custo: R$ {cost_70:.2f}")
    print(f"   🌍 Dezenas: {coverage_70['dezenas_covered']}/8 ({coverage_70['percentage']}%)")
    print(f"   🔥 Hot cobertos: {coverage_70['hot_covered']}/15")
    print(f"   ❄️ Cold cobertos: {coverage_70['cold_covered']}/10")

    # ============================================
    # SALVAR RESULTADOS
    # ============================================
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Salvar Opção 1
    result_56 = {
        "option": 1,
        "name": "COBERTURA 100% DEZENAS",
        "games": len(games_56),
        "cost": cost_56,
        "coverage": coverage_56,
        "portfolio": [{"id": i+1, "numbers": g, "strategy": "100%_DEZENA"} for i, g in enumerate(games_56)],
        "generated_at": datetime.now().isoformat()
    }

    with open(f"output/quina_56_games_{timestamp}.json", 'w') as f:
        json.dump(result_56, f, indent=2, ensure_ascii=False)

    with open("memory/quina_56_games_latest.json", 'w') as f:
        json.dump(result_56, f, indent=2, ensure_ascii=False)

    # Salvar Opção 2
    result_70 = {
        "option": 2,
        "name": "COBERTURA 100% + HÍBRIDO",
        "games": len(games_70),
        "cost": cost_70,
        "coverage": coverage_70,
        "portfolio": [{"id": i+1, "numbers": g, "strategy": "HIBRIDO"} for i, g in enumerate(games_70)],
        "generated_at": datetime.now().isoformat()
    }

    with open(f"output/quina_70_games_{timestamp}.json", 'w') as f:
        json.dump(result_70, f, indent=2, ensure_ascii=False)

    with open("memory/quina_70_games_latest.json", 'w') as f:
        json.dump(result_70, f, indent=2, ensure_ascii=False)

    # ============================================
    # ENVIAR PARA TELEGRAM
    # ============================================
    send_to_telegram(result_56, result_70)

    # ============================================
    # RESUMO
    # ============================================
    print("\n" + "="*70)
    print("📊 RESUMO FINAL")
    print("="*70)

    print(f"""
🎯 CONCURSO: 7051
💰 PRÊMIO: R$ 250.000.000
📅 SORTEIO: 28/06/2026

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 OPÇÃO 1: COBERTURA 100% DEZENAS
   🎰 {len(games_56)} jogos
   💰 R$ {cost_56:.2f}
   🌍 Dezenas: 100%

📊 OPÇÃO 2: COBERTURA 100% + HÍBRIDO
   🎰 {len(games_70)} jogos
   💰 R$ {cost_70:.2f}
   🌍 Dezenas: 100%
   🎯 Mais chances de acerto

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 HOT NUMBERS: {hot_numbers[:10]}
❄️ COLD NUMBERS: {cold_numbers[:10]}

💾 Salvo em:
   • output/quina_56_games_*.json
   • output/quina_70_games_*.json
""")
    print("="*70)

    return result_56, result_70


def send_to_telegram(result_56: Dict, result_70: Dict):
    """Envia resultados para Telegram"""
    try:
        import os
        TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

        if not TOKEN or not CHAT_ID:
            # Tentar carregar do arquivo
            env_file = "../.env.telegram"
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        if "BOT_TOKEN" in line:
                            TOKEN = line.split("=")[1].strip()
                        elif "CHAT_ID" in line:
                            CHAT_ID = line.split("=")[1].strip()

        if not TOKEN or not CHAT_ID:
            print("⚠️ Telegram não configurado")
            return

        import requests

        msg = f"""🧠 QUINA BRAIN v3.1 - COBERTURA 100%

🎯 Concurso 7051 | R$ 250.000.000
📅 Sorteio: 28/06/2026

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 OPÇÃO 1: COBERTURA 100%
   🎰 56 jogos
   💰 R$ {result_56['cost']:.2f}
   🌍 Dezenas: 100%
   🔥 Hot: {result_56['coverage']['hot_covered']}/15
   ❄️ Cold: {result_56['coverage']['cold_covered']}/10

📊 OPÇÃO 2: 100% + HÍBRIDO
   🎰 {result_70['games']} jogos
   💰 R$ {result_70['cost']:.2f}
   🌍 Dezenas: 100%
   🎯 +CHANCES DE ACERTO

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 HOT: {', '.join(map(str, [15, 13, 27, 12, 20, 18, 24, 1, 3, 5]))}
❄️ COLD: {', '.join(map(str, [69, 6, 62, 30, 72, 28, 76, 78, 74, 65]))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 SIAOL-PRO v3.1 Full Coverage"""

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        response = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        }, timeout=10)

        if response.status_code == 200:
            print("📱 Enviado para Telegram!")
        else:
            print(f"⚠️ Erro Telegram: {response.status_code}")

    except Exception as e:
        print(f"⚠️ Erro Telegram: {e}")


if __name__ == "__main__":
    main()