#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           🧠 QUINA BRAIN v3.3 - BACKTEST ENGINE                            ║
║                                                                            ║
║  • Backtest com 56 jogos (100% dezenas)                                    ║
║  • Backtest com 70 jogos (100% + híbrido)                                  ║
║  • Treinamento progressivo até Concurso 7051                               ║
║  • Análise de probabilidade 3, 4, 5 acertos                                 ║
║                                                                            ║
║  Prêmio: R$ 250.000.000 | Sorteio: 28/06/2026                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import os
import random
from datetime import datetime
from itertools import combinations
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# ============================================
# CONFIGURAÇÕES
# ============================================
QUINA_PRICE = 3.00
MAX_DEZENA = 80
TARGET_CONTEST = 7051

# Hot/Cold Numbers (7046 concursos - após calibração 7047)
HOT_NUMBERS = [55, 29, 12, 48, 2, 53, 56, 14, 23, 42, 74, 35, 49, 24, 15]
COLD_NUMBERS = [19, 28, 71, 21, 67, 18, 8, 69, 6, 62, 43, 51, 59, 79, 46]


# ============================================
# CLASSE: COBERTURA 100% (56 JOGOS)
# ============================================
class FullCoverage56:
    """Gera 56 jogos com cobertura 100% dezenas"""

    def __init__(self, hot_numbers: List[int], cold_numbers: List[int]):
        self.hot_numbers = hot_numbers
        self.cold_numbers = cold_numbers

    def generate_games(self) -> List[List[int]]:
        """Gera 56 jogos com cobertura 100% dezenas"""
        pool = self._generate_dezena_pool()

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

        # Completar até 56 jogos
        while len(games) < 56:
            for d in range(8):
                nums = pool[d]
                if len(nums) > 1:
                    new_game = games[-1].copy()
                    for i, n in enumerate(new_game):
                        if (n - 1) // 10 == d and len(nums) > 1:
                            new_game[i] = nums[1] if nums[0] != n else nums[1]
                            break
                    new_game = sorted(new_game)
                    if new_game not in games:
                        games.append(new_game)
                        break

        return games[:56]

    def _generate_dezena_pool(self) -> Dict[int, List[int]]:
        """Gera pool de números por dezena"""
        pool = {}
        for d in range(8):
            start = d * 10 + 1
            end = (d + 1) * 10 if d < 7 else 80

            hot_in_dezena = [n for n in self.hot_numbers if start <= n <= end]
            cold_in_dezena = [n for n in self.cold_numbers if start <= n <= end]

            pool[d] = hot_in_dezena + cold_in_dezena
            if len(pool[d]) < 5:
                pool[d] = list(range(start, end + 1))[:10]

        return pool


# ============================================
# CLASSE: COBERTURA 100% + HÍBRIDO (70 JOGOS)
# ============================================
class FullCoverage70:
    """Gera 70 jogos com cobertura 100% + híbrido"""

    def __init__(self, hot_numbers: List[int], cold_numbers: List[int]):
        self.hot_numbers = hot_numbers
        self.cold_numbers = cold_numbers

    def generate_games(self) -> List[List[int]]:
        """Gera 70 jogos com cobertura 100% + híbrido"""
        pool = self._generate_dezena_pool()
        games = []

        # 56 jogos base (100% dezenas)
        selected = []
        for d in range(8):
            nums = pool[d]
            if nums:
                selected.append(nums[0])

        for combo in combinations(selected, 5):
            games.append(sorted(list(combo)))

        # Completar até 70 jogos com híbrido
        target = 70
        attempts = 0
        max_attempts = 200

        while len(games) < target and attempts < max_attempts:
            attempts += 1

            # 3 hot + 2 cold
            hot_pool = self.hot_numbers[:15]
            cold_pool = self.cold_numbers[:10]

            dezenas_used = set()
            game = []

            # 3 números quentes
            for _ in range(3):
                available = [n for n in hot_pool if (n - 1) // 10 not in dezenas_used]
                if available:
                    n = random.choice(available[:8])
                    game.append(n)
                    dezenas_used.add((n - 1) // 10)

            # 2 números frios
            for _ in range(2):
                available = [n for n in cold_pool if (n - 1) // 10 not in dezenas_used]
                if available:
                    n = random.choice(available[:6])
                    game.append(n)
                    dezenas_used.add((n - 1) // 10)

            # Completar se necessário
            while len(game) < 5:
                for n in list(range(1, 81)):
                    if n not in game and (n - 1) // 10 not in dezenas_used:
                        game.append(n)
                        dezenas_used.add((n - 1) // 10)
                        break

            game = sorted(game[:5])
            if len(set(game)) == 5 and game not in games:
                games.append(game)

        return games[:70]

    def _generate_dezena_pool(self) -> Dict[int, List[int]]:
        """Gera pool de números por dezena"""
        pool = {}
        for d in range(8):
            start = d * 10 + 1
            end = (d + 1) * 10 if d < 7 else 80

            hot_in_dezena = [n for n in self.hot_numbers if start <= n <= end]
            cold_in_dezena = [n for n in self.cold_numbers if start <= n <= end]

            pool[d] = hot_in_dezena + cold_in_dezena
            if len(pool[d]) < 5:
                pool[d] = list(range(start, end + 1))[:10]

        return pool


# ============================================
# CLASSE: BACKTEST ENGINE
# ============================================
class QuinaBacktestEngine:
    """Engine de backtest para Quina Brain"""

    def __init__(self):
        self.history = []
        self.results_56 = []  # Resultados com 56 jogos
        self.results_70 = []  # Resultados com 70 jogos
        self.current_hot = HOT_NUMBERS.copy()
        self.current_cold = COLD_NUMBERS.copy()

    def load_history(self, history_file: str):
        """Carrega histórico de concursos"""
        with open(history_file, 'r') as f:
            data = json.load(f)
            # Estrutura: {"concursos": [[n1,n2,n3,n4,n5], ...]}
            self.history = data.get('concursos', [])
            print(f"📚 Carregados {len(self.history)} concursos")

    def calculate_hits(self, games: List[List[int]], result: List[int]) -> Dict[int, int]:
        """Calcula acertos de cada jogo"""
        hits = {3: 0, 4: 0, 5: 0}
        for game in games:
            match = len(set(game) & set(result))
            if match >= 3:
                hits[match] += 1
        return hits

    def update_hot_cold(self, result: List[int]):
        """Atualiza hot/cold baseado no resultado - NÃO remove números"""
        # Aumenta frequência dos números que saíram
        for num in result:
            if num not in self.current_hot:
                self.current_hot.append(num)
            if num not in self.current_cold and num not in self.current_hot:
                self.current_cold.append(num)

        # Manter listas ordenadas (max 15 cada)
        if len(self.current_hot) > 15:
            self.current_hot = self.current_hot[:15]
        if len(self.current_cold) > 15:
            self.current_cold = self.current_cold[:15]

    def run_backtest(self, start_index: int = 0, end_index: int = 7046) -> Dict:
        """Executa backtest nos concursos"""
        print("\n" + "="*70)
        print("🔬 BACKTEST: 56 JOGOS vs 70 JOGOS")
        print("="*70)

        total_56 = {3: 0, 4: 0, 5: 0, 'cost': 0}
        total_70 = {3: 0, 4: 0, 5: 0, 'cost': 0}

        contests_tested = 0

        for i, result in enumerate(self.history):
            if i < start_index or i >= end_index:
                continue

            # result é um array [n1, n2, n3, n4, n5]
            if not isinstance(result, list) or len(result) != 5:
                continue

            contests_tested += 1

            # Testar 56 jogos
            gen56 = FullCoverage56(self.current_hot, self.current_cold)
            games56 = gen56.generate_games()
            hits56 = self.calculate_hits(games56, result)
            total_56[3] += hits56[3]
            total_56[4] += hits56[4]
            total_56[5] += hits56[5]
            total_56['cost'] += len(games56) * QUINA_PRICE

            # Testar 70 jogos
            gen70 = FullCoverage70(self.current_hot, self.current_cold)
            games70 = gen70.generate_games()
            hits70 = self.calculate_hits(games70, result)
            total_70[3] += hits70[3]
            total_70[4] += hits70[4]
            total_70[5] += hits70[5]
            total_70['cost'] += len(games70) * QUINA_PRICE

            # Atualizar hot/cold
            self.update_hot_cold(result)

        # Calcular percentuais
        if contests_tested > 0:
            pct_56 = {
                'hit_3': round(total_56[3] / (contests_tested * 56) * 100, 2),
                'hit_4': round(total_56[4] / contests_tested * 100, 2),
                'hit_5': round(total_56[5] / contests_tested * 100, 4),
                'total_cost': total_56['cost'],
                'contests': contests_tested
            }
            pct_70 = {
                'hit_3': round(total_70[3] / (contests_tested * 70) * 100, 2),
                'hit_4': round(total_70[4] / contests_tested * 100, 2),
                'hit_5': round(total_70[5] / contests_tested * 100, 4),
                'total_cost': total_70['cost'],
                'contests': contests_tested
            }
        else:
            pct_56 = {'hit_3': 0, 'hit_4': 0, 'hit_5': 0, 'total_cost': 0, 'contests': 0}
            pct_70 = {'hit_3': 0, 'hit_4': 0, 'hit_5': 0, 'total_cost': 0, 'contests': 0}

        return {
            '56_games': {'totals': total_56, 'percentages': pct_56},
            '70_games': {'totals': total_70, 'percentages': pct_70},
            'current_hot': self.current_hot,
            'current_cold': self.current_cold
        }

    def generate_progressive_games(self) -> List[Dict]:
        """Gera jogos progressivos até o concurso 7051"""
        print("\n" + "="*70)
        print("🎯 GERAÇÃO PROGRESSIVA DE JOGOS")
        print("="*70)

        # Primeiro, rodar backtest histórico completo
        backtest = self.run_backtest(start_index=0, end_index=len(self.history))

        print(f"""
📊 RESULTADOS DO BACKTEST (7046 concursos):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 OPÇÃO 1: 56 JOGOS (R$ 168,00)
   💰 Custo total: R$ {backtest['56_games']['percentages']['total_cost']:,.2f}
   🎯 3 acertos: {backtest['56_games']['percentages']['hit_3']}% por jogo
   🎯 4 acertos: {backtest['56_games']['percentages']['hit_4']}% por concurso
   🎯 5 acertos: {backtest['56_games']['percentages']['hit_5']}% por concurso

📋 OPÇÃO 2: 70 JOGOS (R$ 210,00)
   💰 Custo total: R$ {backtest['70_games']['percentages']['total_cost']:,.2f}
   🎯 3 acertos: {backtest['70_games']['percentages']['hit_3']}% por jogo
   🎯 4 acertos: {backtest['70_games']['percentages']['hit_4']}% por concurso
   🎯 5 acertos: {backtest['70_games']['percentages']['hit_5']}% por concurso
""")

        # Gerar jogos para concursos futuros (7047 a 7051)
        # 7045 e 7046 já aconteceram, começamos do 7047
        games_schedule = []

        # Detectar último concurso no histórico
        if len(self.history) >= 7046:
            last_contest = 7046  # 7046 já foi realizado
        elif len(self.history) >= 7045:
            last_contest = 7045
        else:
            last_contest = len(self.history)  # Fallback

        # Mostrar apenas 5 concursos futuros (7047, 7048, 7049, 7050, 7051)
        future_concourses = []
        for c in range(7047, 7052):  # 7047 a 7051
            future_concourses.append(c)

        for next_contest in future_concourses:
            days_until = (datetime(2026, 6, 28) - datetime.now()).days
            days_until = max(1, days_until)

            gen56 = FullCoverage56(self.current_hot, self.current_cold)
            gen70 = FullCoverage70(self.current_hot, self.current_cold)

            games56 = gen56.generate_games()
            games70 = gen70.generate_games()

            contest_info = {
                'contest': next_contest,
                'days_until': days_until,
                'generated_at': datetime.now().isoformat(),
                'hot_numbers': self.current_hot.copy(),
                'cold_numbers': self.current_cold.copy(),
                'option_56': {
                    'games': games56,
                    'cost': len(games56) * QUINA_PRICE,
                    'strategy': 'COBERTURA_100_PORCENTO'
                },
                'option_70': {
                    'games': games70,
                    'cost': len(games70) * QUINA_PRICE,
                    'strategy': 'COBERTURA_100_HIBRIDO'
                }
            }

            games_schedule.append(contest_info)

            print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎰 CONCURSO {next_contest}
📅 Faltam {days_until} dias para o sorteio principal (28/06/2026)

📋 OPÇÃO 1: 56 JOGOS (R$ {contest_info['option_56']['cost']:.2f})
   🎯 3 acertos: {backtest['56_games']['percentages']['hit_3']}% de probabilidade
   🎯 4 acertos: {backtest['56_games']['percentages']['hit_4']}% de probabilidade
   🎯 5 acertos: {backtest['56_games']['percentages']['hit_5']}% de probabilidade

📋 OPÇÃO 2: 70 JOGOS (R$ {contest_info['option_70']['cost']:.2f})
   🎯 3 acertos: {backtest['70_games']['percentages']['hit_3']}% de probabilidade
   🎯 4 acertos: {backtest['70_games']['percentages']['hit_4']}% de probabilidade
   🎯 5 acertos: {backtest['70_games']['percentages']['hit_5']}% de probabilidade

🔥 HOT: {self.current_hot[:10]}
❄️ COLD: {self.current_cold[:10]}
""")

        return games_schedule

    def save_results(self, games_schedule: List[Dict], backtest: Dict):
        """Salva resultados"""
        os.makedirs("memory", exist_ok=True)
        os.makedirs("output", exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Salvar jogos programados
        output_file = f"output/quina_backtest_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump({
                'backtest_results': backtest,
                'games_schedule': games_schedule,
                'generated_at': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)

        # Salvar latest
        with open("memory/quina_backtest_latest.json", 'w') as f:
            json.dump({
                'backtest_results': backtest,
                'games_schedule': games_schedule,
                'generated_at': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)

        # Salvar jogos para concurso 7051 (final)
        final_games = [g for g in games_schedule if g['contest'] == TARGET_CONTEST]
        if final_games:
            with open("memory/quina_final_7051.json", 'w') as f:
                json.dump(final_games[0], f, indent=2, ensure_ascii=False)

        return output_file


# ============================================
# FUNÇÃO PRINCIPAL
# ============================================
def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║     🧠 QUINA BRAIN v3.3 - BACKTEST ENGINE                                  ║
║                                                                            ║
║     • Backtest completo (7045 concursos)                                   ║
║     • Opção 1: 56 jogos (R$ 168)                                           ║
║     • Opção 2: 70 jogos (R$ 210)                                           ║
║     • Geração progressiva até concurso 7051                                ║
║     • Análise de probabilidade 3, 4, 5 acertos                              ║
║                                                                            ║
║     Prêmio: R$ 250.000.000 | Sorteio: 28/06/2026                          ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

    # Inicializar engine
    engine = QuinaBacktestEngine()

    # Carregar histórico
    history_file = "data/quina_history.json"
    if os.path.exists(history_file):
        engine.load_history(history_file)
    else:
        print("❌ Arquivo de histórico não encontrado!")
        return

    # Gerar jogos progressivos
    games_schedule = engine.generate_progressive_games()

    # Obter resultados do backtest
    backtest = engine.run_backtest(start_index=0, end_index=len(engine.history))

    # Salvar resultados
    output_file = engine.save_results(games_schedule, backtest)

    # Calcular probabilidade final
    prob_56 = backtest['56_games']['percentages']
    prob_70 = backtest['70_games']['percentages']

    print("""
======================================================================
🎯 PROBABILIDADES CALCULADAS (Backtest 7045 concursos)
======================================================================

📊 OPÇÃO 1: 56 JOGOS (R$ 168,00)
   🎯 3 acertos: {:.2f}% por jogo
   🎯 4 acertos: {:.2f}% por concurso
   🎯 5 acertos: {:.4f}% por concurso

📊 OPÇÃO 2: 70 JOGOS (R$ 210,00)
   🎯 3 acertos: {:.2f}% por jogo
   🎯 4 acertos: {:.2f}% por concurso
   🎯 5 acertos: {:.4f}% por concurso

💡 COMPARATIVO:
   Opção 2 tem {:.1f}% mais chances de 3 acertos
   Opção 2 tem {:.1f}% mais chances de 4 acertos
   Opção 2 tem {:.1f}% mais chances de 5 acertos

======================================================================
✅ RESULTADOS SALVOS EM: {}
======================================================================
""".format(
        prob_56['hit_3'], prob_56['hit_4'], prob_56['hit_5'],
        prob_70['hit_3'], prob_70['hit_4'], prob_70['hit_5'],
        prob_70['hit_3'] - prob_56['hit_3'],
        prob_70['hit_4'] - prob_56['hit_4'],
        prob_70['hit_5'] - prob_56['hit_5'],
        output_file
    ))

    # Enviar para Telegram
    send_telegram_summary(games_schedule, prob_56, prob_70)

    return games_schedule, backtest


def send_telegram_summary(games_schedule: List[Dict], prob_56: Dict, prob_70: Dict):
    """Envia resumo para Telegram"""
    try:
        import os
        import requests

        TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

        if not TOKEN or not CHAT_ID:
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

        # Preparar jogos do concurso 7051
        final = [g for g in games_schedule if g['contest'] == 7051][0] if games_schedule else None

        msg = f"""🧠 QUINA BRAIN v3.3 - BACKTEST COMPLETO

🎯 Concurso 7051 | R$ 250.000.000
📅 Sorteio: 28/06/2026

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 BACKTEST (7046 concursos):

📋 OPÇÃO 1: 56 JOGOS (R$ 168)
   🎯 3 acertos: {prob_56['hit_3']}%/jogo
   🎯 4 acertos: {prob_56['hit_4']}%/concurso
   🎯 5 acertos: {prob_56['hit_5']}%/concurso

📋 OPÇÃO 2: 70 JOGOS (R$ 210)
   🎯 3 acertos: {prob_70['hit_3']}%/jogo
   🎯 4 acertos: {prob_70['hit_4']}%/concurso
   🎯 5 acertos: {prob_70['hit_5']}%/concurso

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 CONCURSOS FUTUROS (7047 a 7051):
"""

        for g in games_schedule[:5]:
            msg += f"   Concurso {g['contest']}: {g['days_until']} dias\n"

        if final:
            msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎰 JOGOS FINAIS (Concurso 7051):

📋 56 JOGOS:
"""
            for i, game in enumerate(final['option_56']['games'][:5], 1):
                msg += f"   {i}. {game}\n"
            msg += f"   ... +{len(final['option_56']['games'])-5} jogos\n"

            msg += f"""
📋 70 JOGOS:
"""
            for i, game in enumerate(final['option_70']['games'][:5], 1):
                msg += f"   {i}. {game}\n"
            msg += f"   ... +{len(final['option_70']['games'])-5} jogos\n"

        msg += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 HOT: {games_schedule[0]['hot_numbers'][:10]}
❄️ COLD: {games_schedule[0]['cold_numbers'][:10]}

🧠 SIAOL-PRO v3.3 Backtest Engine"""

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        response = requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        }, timeout=10)

        if response.status_code == 200:
            print("📱 Relatório enviado para Telegram!")
        else:
            print(f"⚠️ Erro Telegram: {response.status_code}")

    except Exception as e:
        print(f"⚠️ Erro Telegram: {e}")


if __name__ == "__main__":
    main()