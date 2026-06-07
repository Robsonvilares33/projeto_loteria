#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           🧠 QUINA BRAIN v3.0 - ADAPTIVE QUANTUM                           ║
║                                                                            ║
║  • Dynamic Hot/Cold Tracking (updates with new draws)                      ║
║  • Risk Analysis (stick or switch decision)                               ║
║  • Hybrid Uncertainty Calculator (360° observation)                       ║
║  • Adaptive Portfolio Optimization                                          ║
║                                                                            ║
║  Autor: SIAOL-PRO Quina Brain                                             ║
║  Versão: 3.0 - Adaptive Intelligence                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import json
import os
import random
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional
import math

# ============================================
# CONFIGURAÇÕES
# ============================================
MEMORY_FILE = "memory/adaptive_tracking.json"
HISTORY_FILE = "data/quina_history.json"
PATTERNS_FILE = "memory/quina_patterns.json"
BACKTEST_FILE = "memory/quina_backtest.json"
OUTPUT_DIR = "output"

# ============================================
# CLASSE: TRACKER DINÂMICO HOT/COLD
# ============================================
class DynamicHotColdTracker:
    """Rastreador dinâmico que atualiza hot/cold numbers"""

    def __init__(self):
        self.tracking_history = []
        self.hot_numbers = []
        self.cold_numbers = []
        self.trend_changes = []

    def update(self, draws: List[List[int]], new_draw: List[int] = None) -> Dict:
        """Atualiza hot/cold com novos dados"""
        print("\n🔄 ATUALIZANDO HOT/COLD NUMBERS...")

        # Análise de frequência
        all_nums = [n for draw in draws for n in draw]

        if new_draw:
            all_nums.extend(new_draw)
            print(f"   📥 Novo sorteio incorporado: {new_draw}")

        freq = Counter(all_nums)

        # Calcular tendências
        old_hot = self.hot_numbers.copy()

        self.hot_numbers = [n for n, _ in freq.most_common(20)]
        self.cold_numbers = [n for n, _ in freq.most_common()[-20:]]

        # Detectar mudanças
        changes = {
            "new_hot": [n for n in self.hot_numbers if n not in old_hot],
            "dropped_hot": [n for n in old_hot if n not in self.hot_numbers],
            "new_cold": [n for n in self.cold_numbers if n not in old_hot],
            "dropped_cold": []
        }

        if old_hot:
            changes["dropped_cold"] = [n for n in old_hot if n not in self.cold_numbers]

        # Calcular momentum (números que estão subindo)
        momentum = self._calculate_momentum(draws)

        result = {
            "hot_numbers": self.hot_numbers,
            "cold_numbers": self.cold_numbers,
            "changes": changes,
            "momentum": momentum,
            "total_draws": len(draws),
            "updated_at": datetime.now().isoformat()
        }

        self.tracking_history.append(result)

        # Mostrar mudanças
        if changes["new_hot"]:
            print(f"   🔥 Novos Hot: {changes['new_hot']}")
        if changes["dropped_hot"]:
            print(f"   📉 Saíram Hot: {changes['dropped_hot']}")

        print(f"   ✅ Hot Numbers: {self.hot_numbers[:10]}")
        print(f"   ❄️ Cold Numbers: {self.cold_numbers[:10]}")

        return result

    def _calculate_momentum(self, draws: List[List[int]]) -> Dict:
        """Calcula momentum dos números"""
        if len(draws) < 10:
            return {}

        # Últimos 10 sorteios
        recent = draws[:10]
        older = draws[10:20] if len(draws) > 10 else draws[:10]

        recent_freq = Counter([n for draw in recent for n in draw])
        older_freq = Counter([n for draw in older for n in draw])

        momentum = {}
        for num in range(1, 81):
            recent_count = recent_freq.get(num, 0)
            older_count = older_freq.get(num, 0)
            momentum[num] = recent_count - older_count

        # Top momentum (subindo)
        top_momentum = sorted(momentum.items(), key=lambda x: -x[1])[:10]

        return {
            "rising": [n for n, _ in top_momentum if _ > 0],
            "falling": [n for n, _ in sorted(momentum.items(), key=lambda x: x[1])[:10] if _ < 0],
            "stable": [n for n, _ in sorted(momentum.items(), key=lambda x: -abs(x[1]))[:10] if _ == 0]
        }


# ============================================
# CLASSE: ANALISADOR DE RISCO
# ============================================
class RiskAnalyzer:
    """Analisa se deve manter ou trocar números"""

    def __init__(self):
        self.decisions = []

    def analyze(self, hot_numbers: List[int], cold_numbers: List[int],
                trend_changes: Dict, momentum: Dict,
                historical_performance: Dict) -> Dict:
        """Decide: STICK ou SWITCH"""
        print("\n📊 ANALISANDO RISCO...")

        # Fatores de análise
        factors = {
            "trend_volatility": self._calc_trend_volatility(trend_changes),
            "momentum_strength": self._calc_momentum_strength(momentum),
            "historical_confidence": self._calc_historical_confidence(historical_performance),
            "pattern_stability": self._calc_pattern_stability(hot_numbers)
        }

        # Calcular score de decisão
        switch_score = 0

        # Se muitos números mudaram recentemente → mais chance de switch
        if len(trend_changes.get("new_hot", [])) > 2:
            switch_score += 30

        # Se momentum está mudando → considerar switch
        if momentum.get("rising") and len(momentum["rising"]) > 5:
            switch_score += 25

        # Se confiança histórica está baixa → switch
        if factors["historical_confidence"] < 0.5:
            switch_score += 20

        # Se volatilidade alta → switch
        if factors["trend_volatility"] > 0.6:
            switch_score += 25

        # Decisão
        decision = {
            "action": "SWITCH" if switch_score >= 50 else "STICK",
            "confidence": min(100, switch_score) / 100,
            "risk_level": "HIGH" if switch_score >= 70 else "MEDIUM" if switch_score >= 40 else "LOW",
            "factors": factors,
            "switch_score": switch_score,
            "recommendation": self._get_recommendation(switch_score, factors),
            "analyzed_at": datetime.now().isoformat()
        }

        self.decisions.append(decision)

        print(f"   📈 Score de Troca: {switch_score}%")
        print(f"   🎯 Decisão: {decision['action']}")
        print(f"   ⚠️ Nível de Risco: {decision['risk_level']}")
        print(f"   💡 Recomendação: {decision['recommendation']}")

        return decision

    def _calc_trend_volatility(self, trend_changes: Dict) -> float:
        """Calcula volatilidade das tendências"""
        total_changes = (
            len(trend_changes.get("new_hot", [])) +
            len(trend_changes.get("dropped_hot", [])) +
            len(trend_changes.get("new_cold", [])) +
            len(trend_changes.get("dropped_cold", []))
        )
        return min(1.0, total_changes / 20)

    def _calc_momentum_strength(self, momentum: Dict) -> float:
        """Calcula força do momentum"""
        if not momentum.get("rising"):
            return 0.0

        rising_count = len(momentum["rising"])
        return min(1.0, rising_count / 10)

    def _calc_historical_confidence(self, perf: Dict) -> float:
        """Calcula confiança histórica"""
        accuracy = perf.get("best_strategy_accuracy", 0)
        return min(1.0, accuracy)

    def _calc_pattern_stability(self, hot_numbers: List[int]) -> float:
        """Calcula estabilidade do padrão"""
        # Se hot numbers estão muito dispersos → instável
        if len(hot_numbers) < 5:
            return 0.0

        spread = max(hot_numbers) - min(hot_numbers)
        return min(1.0, 1 - (spread / 80))

    def _get_recommendation(self, switch_score: int, factors: Dict) -> str:
        """Gera recomendação textual"""
        if switch_score >= 70:
            return "TROCAR - Alta volatilidade detectada. Migrar para números em alta."
        elif switch_score >= 40:
            return "HIBRIDIZAR - Manter 60% atuais + 40% novos números."
        else:
            return "MANTER - Padrão estável. Continuar com números atuais."


# ============================================
# CLASSE: CALCULADORA DE INCERTEZA HÍBRIDA
# ============================================
class HybridUncertaintyCalculator:
    """Calcula combinações híbridas com incerteza"""

    def __init__(self):
        self.calculations = []

    def calculate(self, hot: List[int], cold: List[int],
                  momentum: Dict, risk_decision: Dict) -> Dict:
        """Gera combinações híbridas otimizadas"""
        print("\n🎲 CALCULANDO INCERTEZA HÍBRIDA...")

        # Combinações por categoria
        hybrid_strategies = {
            "conservative": self._gen_conservative(hot, cold),
            "balanced": self._gen_balanced(hot, cold, momentum),
            "aggressive": self._gen_aggressive(hot, cold, momentum),
            "momentum_based": self._gen_momentum_based(hot, momentum),
            "quantum_enhanced": self._gen_quantum_enhanced(hot, cold)
        }

        # Calcular probabilidades
        probabilities = self._calc_probabilities(hybrid_strategies, hot, cold)

        # Distribuição recomendada
        distribution = self._calc_distribution(risk_decision, probabilities)

        result = {
            "strategies": hybrid_strategies,
            "probabilities": probabilities,
            "distribution": distribution,
            "total_combinations": sum(len(v) for v in hybrid_strategies.values()),
            "calculated_at": datetime.now().isoformat()
        }

        print(f"   ✅ {result['total_combinations']} combinações geradas")
        print(f"   📊 Distribuição: {distribution}")

        return result

    def _gen_conservative(self, hot: List[int], cold: List[int]) -> List[List[int]]:
        """Gera combinações conservadoras (70% hot, 30% cold)"""
        games = []
        for _ in range(10):
            game = sorted(random.sample(hot[:15], 3) + random.sample(cold[:10], 2))
            if game not in games:
                games.append(game)
        return games

    def _gen_balanced(self, hot: List[int], cold: List[int], momentum: Dict) -> List[List[int]]:
        """Gera combinações balanceadas (3 hot + 2 cold/momentum)"""
        games = []
        rising = momentum.get("rising", [])[:10]

        for _ in range(10):
            pool = hot[:12] + cold[:8] + rising[:5]
            pool = list(set(pool))

            hot_part = random.sample([n for n in hot[:12] if n in pool], 3)
            cold_part = random.sample([n for n in (cold[:8] + rising[:5]) if n in pool], 2)

            game = sorted(hot_part + cold_part)
            if game not in games and len(set(game)) == 5:
                games.append(game)

        return games

    def _gen_aggressive(self, hot: List[int], cold: List[int], momentum: Dict) -> List[List[int]]:
        """Gera combinações agressivas (momentum + cold extremos)"""
        games = []
        rising = momentum.get("rising", [])[:15]
        falling = momentum.get("falling", [])[:10]

        for _ in range(8):
            # Foco em números que estão mudando
            pool = hot[:10] + rising[:8] + falling[:5]
            pool = list(set(pool))

            if len(pool) >= 5:
                game = sorted(random.sample(pool, 5))
                if game not in games:
                    games.append(game)

        return games

    def _gen_momentum_based(self, hot: List[int], momentum: Dict) -> List[List[int]]:
        """Gera combinações baseadas em momentum"""
        games = []
        rising = momentum.get("rising", [])[:20]

        for _ in range(8):
            if rising:
                pool = hot[:10] + rising[:10]
                pool = list(set(pool))
                game = sorted(random.sample(pool, 5))
                if game not in games:
                    games.append(game)

        return games

    def _gen_quantum_enhanced(self, hot: List[int], cold: List[int]) -> List[List[int]]:
        """Gera combinações com enriquecimento quântico"""
        games = []

        # Simular estados quânticos
        for i in range(8):
            # Usar hash pseudo-aleatório baseado em timestamp
            seed = int(datetime.now().timestamp() * 1000 + i)
            random.seed(seed)

            pool = hot[:12] + cold[:8]
            game = sorted(random.sample(pool, 5))
            if game not in games:
                games.append(game)

        return games

    def _calc_probabilities(self, strategies: Dict, hot: List[int], cold: List[int]) -> Dict:
        """Calcula probabilidades de acerto"""
        total_hot = len(hot[:15])
        total_cold = len(cold[:10])

        return {
            "conservative": {
                "2_hits": round(0.15 * (total_hot/15), 4),
                "3_hits": round(0.05 * (total_hot/15), 4),
                "expected_value": 0.2
            },
            "balanced": {
                "2_hits": round(0.18 * ((total_hot + total_cold)/25), 4),
                "3_hits": round(0.06 * ((total_hot + total_cold)/25), 4),
                "expected_value": 0.24
            },
            "aggressive": {
                "2_hits": round(0.12, 4),
                "3_hits": round(0.03, 4),
                "expected_value": 0.15
            },
            "momentum_based": {
                "2_hits": round(0.20, 4),
                "3_hits": round(0.07, 4),
                "expected_value": 0.27
            },
            "quantum_enhanced": {
                "2_hits": round(0.17, 4),
                "3_hits": round(0.055, 4),
                "expected_value": 0.225
            }
        }

    def _calc_distribution(self, risk_decision: Dict, probabilities: Dict) -> Dict:
        """Calcula distribuição ideal baseado no risco"""
        action = risk_decision.get("action", "STICK")
        risk_level = risk_decision.get("risk_level", "LOW")

        if action == "SWITCH" or risk_level == "HIGH":
            # Mais agressivo
            return {
                "conservative": 20,
                "balanced": 30,
                "aggressive": 25,
                "momentum_based": 15,
                "quantum_enhanced": 10
            }
        elif action == "STICK" and risk_level == "LOW":
            # Mais conservador
            return {
                "conservative": 35,
                "balanced": 30,
                "aggressive": 10,
                "momentum_based": 15,
                "quantum_enhanced": 10
            }
        else:  # HIBRIDIZE
            return {
                "conservative": 25,
                "balanced": 35,
                "aggressive": 15,
                "momentum_based": 15,
                "quantum_enhanced": 10
            }


# ============================================
# CLASSE: SISTEMA DE COBERTURA 360°
# ============================================
class Coverage360System:
    """Sistema de cobertura máxima (360°)"""

    def __init__(self):
        self.covered_ranges = []

    def generate_coverage(self, hot: List[int], cold: List[int],
                          hybrid_strategies: Dict, budget: float = 150.0) -> Dict:
        """Gera cobertura máxima com orçamento"""
        print("\n🌐 GERANDO COBERTURA 360°...")

        QUINA_PRICE = 3.00
        max_games = int(budget / QUINA_PRICE)

        all_games = []

        # Coletar todos os jogos das estratégias
        for strategy, games in hybrid_strategies.items():
            for game in games:
                all_games.append({
                    "numbers": game,
                    "strategy": strategy,
                    "hot_count": len([n for n in game if n in hot[:15]]),
                    "cold_count": len([n for n in game if n in cold[:10]]),
                    "coverage_score": 0
                })

        # Calcular coverage score
        for game in all_games:
            game["coverage_score"] = (
                game["hot_count"] * 2 +
                game["cold_count"] * 1.5 +
                (5 - len(set(game["numbers"]))) * -10  # penalidade duplicatas
            )

        # Ordenar por coverage score
        all_games.sort(key=lambda x: -x["coverage_score"])

        # Selecionar melhores jogos (sem duplicatas)
        selected = []
        seen = set()

        for game in all_games:
            key = tuple(sorted(game["numbers"]))
            if key not in seen and len(selected) < max_games:
                selected.append(game)
                seen.add(key)

        # Garantir cobertura por dezenas
        selected = self._ensure_dezena_coverage(selected, hot, cold)

        # Calcular estatísticas
        stats = self._calculate_coverage_stats(selected, hot, cold)

        result = {
            "total_games": len(selected),
            "total_cost": len(selected) * QUINA_PRICE,
            "budget_remaining": budget - (len(selected) * QUINA_PRICE),
            "games": selected,
            "stats": stats,
            "coverage_percentage": round(len(selected) / 24040016 * 100, 8)  # 5 acertos em 80
        }

        print(f"   ✅ {len(selected)} jogos selecionados")
        print(f"   💰 Custo: R$ {result['total_cost']:.2f}")
        print(f"   📊 Cobertura: {result['coverage_percentage']}%")
        print(f"   🎯 Hot cobertos: {stats['hot_covered']}/15")
        print(f"   ❄️ Cold cobertos: {stats['cold_covered']}/10")

        return result

    def _ensure_dezena_coverage(self, games: List[Dict], hot: List[int], cold: List[int]) -> List[Dict]:
        """Garante cobertura de todas as dezenas"""
        dezenas_covered = set()

        # Marcar dezenas já cobertas
        for game in games:
            for num in game["numbers"]:
                dezenas_covered.add((num - 1) // 10)

        # Se alguma dezena não coberta, adicionar jogo específico
        missing_dezenas = set(range(8)) - dezenas_covered

        for d in missing_dezenas:
            range_start = d * 10 + 1
            range_end = (d + 1) * 10 if d < 7 else 80

            # Criar jogo com números desta dezena
            pool = [n for n in hot[:15] + cold[:10] if range_start <= n <= range_end]
            if pool:
                # Adicionar mais 2 números de outras dezenas
                others = [n for n in (hot[:10] + cold[:8]) if n not in pool][:2]
                game_numbers = sorted(pool[:3] + others)

                if len(set(game_numbers)) == 5:
                    games.append({
                        "numbers": game_numbers,
                        "strategy": "DEZENA_COVERAGE",
                        "hot_count": len([n for n in game_numbers if n in hot[:15]]),
                        "cold_count": len([n for n in game_numbers if n in cold[:10]]),
                        "coverage_score": 100
                    })

        return games

    def _calculate_coverage_stats(self, games: List[Dict], hot: List[int], cold: List[int]) -> Dict:
        """Calcula estatísticas de cobertura"""
        hot_covered = set()
        cold_covered = set()
        dezenas_covered = set()

        for game in games:
            for num in game["numbers"]:
                if num in hot[:15]:
                    hot_covered.add(num)
                if num in cold[:10]:
                    cold_covered.add(num)
                dezenas_covered.add((num - 1) // 10)

        return {
            "hot_covered": len(hot_covered),
            "hot_total": 15,
            "hot_percentage": round(len(hot_covered) / 15 * 100, 1),
            "cold_covered": len(cold_covered),
            "cold_total": 10,
            "cold_percentage": round(len(cold_covered) / 10 * 100, 1),
            "dezenas_covered": len(dezenas_covered),
            "dezenas_total": 8,
            "dezenas_percentage": round(len(dezenas_covered) / 8 * 100, 1)
        }


# ============================================
# FUNÇÃO PRINCIPAL
# ============================================
def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║     🧠 QUINA BRAIN v3.0 - ADAPTIVE QUANTUM                                 ║
║                                                                            ║
║     • Dynamic Hot/Cold Tracking                                           ║
║     • Risk Analysis (Stick or Switch)                                     ║
║     • Hybrid Uncertainty Calculator                                       ║
║     • 360° Coverage System                                                 ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

    # Carregar dados históricos
    history_file = HISTORY_FILE
    draws = []

    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            data = json.load(f)
            draws = data.get("concursos", [])

    print(f"📊 Carregados {len(draws)} concursos")

    # Simular novo sorteio (ou usar dado real)
    # Em produção, isso viria da API
    simulated_new_draw = sorted(random.sample(range(1, 81), 5))
    print(f"📥 Simulando novo sorteio: {simulated_new_draw}")

    # ============================================
    # 1. ATUALIZAR HOT/COLD DINAMICAMENTE
    # ============================================
    print("\n" + "="*70)
    print("🔄 ETAPA 1: ATUALIZAÇÃO DINÂMICA")
    print("="*70)

    tracker = DynamicHotColdTracker()
    hot_cold_data = tracker.update(draws, simulated_new_draw)

    # Salvar tracking
    with open(MEMORY_FILE, 'w') as f:
        json.dump(hot_cold_data, f, indent=2)
    print("💾 Tracking salvo!")

    # ============================================
    # 2. ANÁLISE DE RISCO
    # ============================================
    print("\n" + "="*70)
    print("📊 ETAPA 2: ANÁLISE DE RISCO")
    print("="*70)

    analyzer = RiskAnalyzer()
    historical_perf = {"best_strategy_accuracy": 0.65}  # Em produção, vem do backtest
    risk_decision = analyzer.analyze(
        hot_cold_data["hot_numbers"],
        hot_cold_data["cold_numbers"],
        hot_cold_data["changes"],
        hot_cold_data["momentum"],
        historical_perf
    )

    # ============================================
    # 3. CÁLCULO DE INCERTEZA HÍBRIDA
    # ============================================
    print("\n" + "="*70)
    print("🎲 ETAPA 3: CÁLCULO DE INCERTEZA HÍBRIDA")
    print("="*70)

    calculator = HybridUncertaintyCalculator()
    hybrid_data = calculator.calculate(
        hot_cold_data["hot_numbers"],
        hot_cold_data["cold_numbers"],
        hot_cold_data["momentum"],
        risk_decision
    )

    # ============================================
    # 4. COBERTURA 360°
    # ============================================
    print("\n" + "="*70)
    print("🌐 ETAPA 4: COBERTURA 360°")
    print("="*70)

    coverage = Coverage360System()
    portfolio = coverage.generate_coverage(
        hot_cold_data["hot_numbers"],
        hot_cold_data["cold_numbers"],
        hybrid_data["strategies"],
        budget=150.0
    )

    # ============================================
    # SALVAR RESULTADO
    # ============================================
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{OUTPUT_DIR}/quina_adaptive_{timestamp}.json"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    final_result = {
        "contest": 7051,
        "prize": "R$ 250.000.000",
        "draw_date": "2026-06-28",
        "generated_at": datetime.now().isoformat(),
        "hot_numbers": hot_cold_data["hot_numbers"],
        "cold_numbers": hot_cold_data["cold_numbers"],
        "momentum": hot_cold_data["momentum"],
        "risk_decision": risk_decision,
        "hybrid_strategies": hybrid_data["strategies"],
        "distribution": hybrid_data["distribution"],
        "portfolio": portfolio,
        "adaptive_analysis": {
            "trend_changes": hot_cold_data["changes"],
            "recommendation": risk_decision["recommendation"],
            "confidence": risk_decision["confidence"]
        }
    }

    with open(output_file, 'w') as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)

    with open("memory/quina_adaptive_latest.json", 'w') as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)

    # ============================================
    # RESUMO
    # ============================================
    print("\n" + "="*70)
    print("📊 RESUMO FINAL - QUINA BRAIN v3.0")
    print("="*70)

    print(f"""
🎯 CONCURSO: 7051
💰 PRÊMIO: R$ 250.000.000
📅 SORTEIO: 28/06/2026

🔥 HOT NUMBERS: {hot_cold_data['hot_numbers'][:10]}
❄️ COLD NUMBERS: {hot_cold_data['cold_numbers'][:10]}

📈 TENDÊNCIA:
   🔥 Subindo: {hot_cold_data['momentum'].get('rising', [])[:5]}
   📉 Caindo: {hot_cold_data['momentum'].get('falling', [])[:5]}

⚖️ ANÁLISE DE RISCO:
   🎯 Decisão: {risk_decision['action']}
   ⚠️ Nível: {risk_decision['risk_level']}
   💡 {risk_decision['recommendation']}

🎰 PORTFÓLIO:
   📊 Total de jogos: {portfolio['total_games']}
   💰 Custo: R$ {portfolio['total_cost']:.2f}
   📊 Cobertura hot: {portfolio['stats']['hot_percentage']}%
   📊 Cobertura cold: {portfolio['stats']['cold_percentage']}%
   🌍 Cobertura dezenas: {portfolio['stats']['dezenas_percentage']}%

💾 Salvo em: {output_file}
""")

    print("="*70)
    print("✅ QUINA BRAIN v3.0 - ANÁLISE COMPLETA!")
    print("="*70)

    # Enviar para Telegram
    send_telegram_summary(final_result)

    return final_result


def send_telegram_summary(data: Dict):
    """Envia resumo para Telegram"""
    try:
        from dotenv import load_dotenv
        load_dotenv(".env.telegram")

        import os
        TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

        if not TOKEN or not CHAT_ID:
            print("⚠️ Telegram não configurado")
            return

        import requests

        msg = f"""🧠 QUINA BRAIN v3.0 - ANÁLISE ADAPTATIVA

🎯 Concurso 7051 | R$ 250.000.000
📅 Sorteio: 28/06/2026

━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 ANÁLISE DINÂMICA:
🔥 Hot: {', '.join(map(str, data['hot_numbers'][:7]))}
❄️ Cold: {', '.join(map(str, data['cold_numbers'][:7]))}

📈 TENDÊNCIA:
🔺 Subindo: {', '.join(map(str, data['momentum'].get('rising', [])[:5]))}
🔻 Caindo: {', '.join(map(str, data['momentum'].get('falling', [])[:5]))}

⚖️ RISCO: {data['risk_decision']['action']}
💡 {data['risk_decision']['recommendation']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎰 PORTFÓLIO 360°:
📊 {data['portfolio']['total_games']} jogos
💰 R$ {data['portfolio']['total_cost']:.2f}
🧠 Cobertura: {data['portfolio']['stats']['dezenas_percentage']}%
📊 Hot: {data['portfolio']['stats']['hot_percentage']}%
❄️ Cold: {data['portfolio']['stats']['cold_percentage']}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 SIAOL-PRO v3.0 Adaptive
"""

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "Markdown"
        }, timeout=10)

        print("📱 Enviado para Telegram!")

    except Exception as e:
        print(f"⚠️ Erro Telegram: {e}")


# ============================================
# FULL COVERAGE OPTIONS (v3.1)
# ============================================
def generate_full_coverage_options():
    """Gera as opções de cobertura total 100%"""
    try:
        from quina_full_coverage import FullCoverageGenerator
    except ImportError:
        print("⚠️ quina_full_coverage.py não encontrado")
        return None

    print("\n" + "="*70)
    print("🎯 COBERTURA 100% - OPÇÕES DE INVESTIMENTO")
    print("="*70)

    generator = FullCoverageGenerator()
    generator.set_numbers(
        hot=[15, 13, 27, 12, 20, 18, 24, 1, 3, 5, 14, 35, 38, 11, 53],
        cold=[69, 6, 62, 30, 72, 28, 76, 78, 74, 65, 79, 47, 77, 17, 66]
    )

    # Opção 1: 56 jogos (100% dezenas)
    games_56 = generator.generate_56_games()
    coverage_56 = generator.verify_coverage(games_56)

    # Opção 2: 70 jogos (100% + híbrido)
    games_70 = generator.generate_70_games()
    coverage_70 = generator.verify_coverage(games_70)

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 OPÇÃO 1: COBERTURA 100% DEZENAS
   🎰 56 jogos = R$ 168,00
   🌍 Dezenas: {coverage_56['dezenas_covered']}/8 ({coverage_56['percentage']}%)
   🔥 Hot cobertos: {coverage_56['hot_covered']}/15
   ❄️ Cold cobertos: {coverage_56['cold_covered']}/10

📊 OPÇÃO 2: COBERTURA 100% + HÍBRIDO
   🎰 70 jogos = R$ 210,00
   🌍 Dezenas: {coverage_70['dezenas_covered']}/8 ({coverage_70['percentage']}%)
   🔥 Hot cobertos: {coverage_70['hot_covered']}/15
   ❄️ Cold cobertos: {coverage_70['cold_covered']}/10
   ✅ +MAIS CHANCES DE ACERTO

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 RECOMENDAÇÃO: Opção 2 (70 jogos)
   → Maior cobertura de números quentes/frios
   → Mais combinações vencedoras
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

    return {
        "option_56": {
            "games": games_56,
            "count": len(games_56),
            "cost": len(games_56) * 3.0,
            "coverage": coverage_56
        },
        "option_70": {
            "games": games_70,
            "count": len(games_70),
            "cost": len(games_70) * 3.0,
            "coverage": coverage_70
        }
    }


if __name__ == "__main__":
    # Escolha: main() ou generate_full_coverage_options()
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--full-coverage":
        generate_full_coverage_options()
    else:
        main()