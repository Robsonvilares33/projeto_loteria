#!/usr/bin/env python3
"""
SIAOL-PRO v12.3 - CICLO COMPLETO DE ML COM BACKTESTING REAL
Gera jogos específicos por loteria, avalia acertos e treina modelos
"""
import sys
sys.path.insert(0, '/workspace/projeto_loteria')
import os
import json
import random
import math
from datetime import datetime
from collections import Counter
import numpy as np

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Configuração das loterias com quantidade correta de números
LOTTERY_CONFIG = {
    "megasena": {
        "name": "Mega-Sena",
        "pick": 6,
        "range": 60,
        "games_to_train": 15,  # 10-20 jogos
        "prizes": {3: "terno", 4: "quadra", 5: "quina", 6: "sena"}
    },
    "lotofacil": {
        "name": "Lotofácil",
        "pick": 15,
        "range": 25,
        "games_to_train": 15,  # 10-20 jogos
        "prizes": {11: "onze pontos", 12: "doze pontos", 13: "treze pontos", 14: "quatorze pontos", 15: "quinze pontos"}
    },
    "quina": {
        "name": "Quina",
        "pick": 5,
        "range": 80,
        "games_to_train": 15,  # 10-20 jogos
        "prizes": {2: "duque", 3: "terno", 4: "quadra", 5: "quina"}
    },
    "lotomania": {
        "name": "Lotomania",
        "pick": 50,
        "range": 100,
        "games_to_train": 15,  # 10-20 jogos
        "prizes": {16: "dezesseis pontos", 17: "dezessete pontos", 18: "dezoito pontos", 19: "dezenove pontos", 20: "vinte pontos"}
    }
}

OUTPUT_DIR = "/workspace/projeto_loteria/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class LotteryDataLoader:
    """Carrega dados históricos do projeto"""

    def __init__(self, project_dir="/workspace/projeto_loteria"):
        self.project_dir = project_dir

    def load_megasena_excel(self, max_draws=2000):
        excel_path = os.path.join(self.project_dir, "mega_sena_asloterias_ate_concurso_2937_sorteio.xlsx")
        if not os.path.exists(excel_path):
            return None
        try:
            import pandas as pd
            df = pd.read_excel(excel_path, header=6)
            df = df.dropna(subset=['Concurso'])
            draws = []
            for _, row in df.iterrows():
                numbers = []
                for col in ['bola 1', 'bola 2', 'bola 3', 'bola 4', 'bola 5', 'bola 6']:
                    if col in df.columns and pd.notna(row[col]):
                        try:
                            num = int(row[col])
                            if 1 <= num <= 60:
                                numbers.append(num)
                        except:
                            pass
                if len(numbers) == 6:
                    draws.append(sorted(numbers))
            if len(draws) > max_draws:
                draws = draws[-max_draws:]
            return draws if len(draws) > 50 else None
        except Exception as e:
            print(f"   Erro ao carregar Excel: {e}")
            return None

    def load_lotofacil_txt(self, max_draws=500):
        txt_path = os.path.join(self.project_dir, "lotofacil-resultados-1-3576.txt")
        if not os.path.exists(txt_path):
            return None
        try:
            draws = []
            with open(txt_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('-')
                    if len(parts) >= 2:
                        nums_str = parts[1].strip().replace(',', ' ')
                        numbers = [int(n.strip()) for n in nums_str.split() if n.strip().isdigit()]
                        if 15 <= len(numbers) <= 20:
                            draws.append(sorted(numbers[:15]))
            if len(draws) > max_draws:
                draws = draws[-max_draws:]
            return draws if len(draws) > 50 else None
        except Exception as e:
            print(f"   Erro ao carregar TXT: {e}")
            return None

    def load_quina_txt(self, max_draws=2000):
        txt_path = os.path.join(self.project_dir, "quina-resultados-1-6916.txt")
        if not os.path.exists(txt_path):
            return None
        try:
            draws = []
            with open(txt_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('-')
                    if len(parts) >= 2:
                        nums_str = parts[1].strip().replace(',', ' ')
                        numbers = [int(n.strip()) for n in nums_str.split() if n.strip().isdigit()]
                        if 5 <= len(numbers) <= 10:
                            draws.append(sorted(numbers[:5]))
            if len(draws) > max_draws:
                draws = draws[-max_draws:]
            return draws if len(draws) > 50 else None
        except Exception as e:
            print(f"   Erro ao carregar TXT: {e}")
            return None

    def load_lotomania_txt(self, max_draws=500):
        txt_path = os.path.join(self.project_dir, "lotomania-resultados-1-2869.txt")
        if not os.path.exists(txt_path):
            return None
        try:
            draws = []
            with open(txt_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('-')
                    if len(parts) >= 2:
                        numbers = [int(n.strip()) for n in parts[1].split() if n.strip().isdigit()]
                        if 50 <= len(numbers) <= 100:
                            draws.append(sorted(numbers[:50]))
            if len(draws) > max_draws:
                draws = draws[-max_draws:]
            return draws if len(draws) > 50 else None
        except Exception as e:
            print(f"   Erro ao carregar TXT: {e}")
            return None

def count_hits(game, draw):
    """Conta quantos números acertou"""
    return len(set(game) & set(draw))

def evaluate_game(game, historical_draws, config, last_n=100):
    """Avalia um jogo contra os últimos N sorteios"""
    recent_draws = historical_draws[-last_n:] if len(historical_draws) > last_n else historical_draws

    results = {
        "total_evaluated": len(recent_draws),
        "hits_distribution": Counter(),
        "best_hit": 0,
        "prizes_won": Counter()
    }

    for draw in recent_draws:
        hits = count_hits(game, draw)
        results["hits_distribution"][hits] += 1
        if hits > results["best_hit"]:
            results["best_hit"] = hits
        # Verificar prêmios
        for min_hits, prize_name in config["prizes"].items():
            if hits >= min_hits:
                results["prizes_won"][prize_name] += 1

    return results

def generate_frequency_based_games(config, historical_draws, n_games):
    """Gera jogos baseado em frequência histórica"""
    counter = Counter()
    for draw in historical_draws:
        counter.update(draw)

    # Ordenar números por frequência
    most_common = counter.most_common()

    games = []
    # Jogo com números mais frequentes
    top_numbers = [num for num, _ in most_common[:config["pick"]]]
    games.append(sorted(top_numbers))

    # Gerar jogos variando entre frequentes e menos frequentes
    for i in range(n_games - 1):
        # Mistura entre números quentes e frios
        hot = [num for num, _ in most_common[:20]]
        cold = [num for num, _ in most_common[-20:]]

        # Proporção variável
        hot_count = config["pick"] - 4 + (i % 5)
        cold_count = config["pick"] - hot_count

        game = sorted(random.sample(hot, min(hot_count, len(hot))) +
                     random.sample(cold, min(cold_count, len(cold))))

        # Completar se necessário
        if len(game) < config["pick"]:
            all_nums = list(range(1, config["range"] + 1))
            available = [n for n in all_nums if n not in game]
            game.extend(random.sample(available, config["pick"] - len(game)))

        games.append(sorted(game[:config["pick"]]))

    return games

def generate_ml_based_games(config, historical_draws, n_games, predictions):
    """Gera jogos baseado em previsões ML"""
    if not predictions:
        return generate_frequency_based_games(config, historical_draws, n_games)

    # Ordenar números por probabilidade predita
    sorted_numbers = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
    top_numbers = [num for num, _ in sorted_numbers[:config["pick"] + 10]]

    games = []
    for i in range(n_games):
        # Variar um pouco os jogos
        start = i * 2
        game = sorted(top_numbers[start:start + config["pick"]])

        if len(game) < config["pick"]:
            available = [n for n in range(1, config["range"] + 1) if n not in game]
            game.extend(random.sample(available, config["pick"] - len(game)))

        games.append(sorted(game))

    return games

def train_prediction_model(historical_draws, config):
    """Treina modelo para prever números"""
    if not SKLEARN_AVAILABLE or len(historical_draws) < 100:
        return None

    # Preparar features
    X = []
    y = []

    for i in range(len(historical_draws) - 10):
        # Features dos últimos 10 sorteios
        window = historical_draws[i:i+10]

        for num in range(1, config["range"] + 1):
            # Features: frequência do número, posição média, etc.
            features = []
            freq = sum(1 for draw in window if num in draw)
            features.append(freq / 10)  # Frequência normalizada
            features.append(sum(1 for draw in window if num not in draw) / 10)  # Ausência
            features.append(num / config["range"])  # Posição normalizada
            features.append(sum(1 for draw in window if num > max(draw) - 10))  # Proximidade ao fim
            features.append(sum(1 for draw in window if num < min(draw) + 10))  # Proximidade ao início

            X.append(features)
            # Se foi sorteado no próximo sorteio
            y.append(1 if num in historical_draws[i+10] else 0)

    X = np.array(X)
    y = np.array(y)

    # Treinar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    rf = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42, n_jobs=-1)
    rf.fit(X_scaled, y)

    return rf, scaler

def predict_numbers(rf, scaler, config, historical_draws):
    """Gera previsões de probabilidade para cada número"""
    if rf is None:
        return {}

    predictions = {}
    window = historical_draws[-10:] if len(historical_draws) >= 10 else historical_draws

    for num in range(1, config["range"] + 1):
        features = []
        freq = sum(1 for draw in window if num in draw)
        features.append(freq / 10)
        features.append(sum(1 for draw in window if num not in draw) / 10)
        features.append(num / config["range"])

        # Calcular máximo e mínimo do window
        max_val = max(max(draw) for draw in window) if window else config["range"]
        min_val = min(min(draw) for draw in window) if window else 1

        features.append(sum(1 for draw in window if num > max_val - 10))
        features.append(sum(1 for draw in window if num < min_val + 10))

        features_scaled = scaler.transform([features])
        prob = rf.predict_proba(features_scaled)[0][1] if hasattr(rf, 'predict_proba') else 0.5
        predictions[num] = prob

    return predictions

def process_lottery(lottery_key, config, data_loader):
    """Processa uma loteria com avaliação real"""
    print(f"\n{'='*68}")
    print(f"  {config['name'].upper()} - {config['pick']} números por jogo")
    print(f"{'='*68}")

    # Carregar dados históricos
    print(f"📊 Carregando dados históricos...")

    if lottery_key == "megasena":
        real_draws = data_loader.load_megasena_excel(max_draws=500)
    elif lottery_key == "lotofacil":
        real_draws = data_loader.load_lotofacil_txt(max_draws=500)
    elif lottery_key == "quina":
        real_draws = data_loader.load_quina_txt(max_draws=500)
    elif lottery_key == "lotomania":
        real_draws = data_loader.load_lotomania_txt(max_draws=500)
    else:
        real_draws = None

    if not real_draws or len(real_draws) < 50:
        print(f"   Erro: Dados insuficientes")
        return None

    print(f"   ✅ Carregados {len(real_draws)} sorteios")

    # Treinar modelo
    print(f"🌲 Treinando modelo preditivo...")
    rf, scaler = train_prediction_model(real_draws, config)

    # Gerar previsões
    predictions = predict_numbers(rf, scaler, config, real_draws) if rf else {}

    # Gerar jogos (10-20 jogos conforme configurado)
    n_games = config["games_to_train"]
    print(f"🎯 Gerando {n_games} jogos...")

    if predictions:
        games = generate_ml_based_games(config, real_draws, n_games, predictions)
    else:
        games = generate_frequency_based_games(config, real_draws, n_games)

    # Avaliar cada jogo com backtesting
    print(f"📊 Avaliando acertos de cada jogo...")

    evaluated_games = []
    for i, game in enumerate(games):
        results = evaluate_game(game, real_draws, config, last_n=100)

        # Calcular score de performance
        score = 0
        for hits, count in results["hits_distribution"].items():
            if hits >= 3:  # Pelo menos terno/duque
                score += hits * count

        evaluated_games.append({
            "game_number": i + 1,
            "numbers": game,
            "evaluation": results,
            "performance_score": score
        })

        print(f"   Jogo {i+1}: {game}")
        print(f"      - Melhor acerto: {results['best_hit']} números")
        print(f"      - Distribuição: {dict(results['hits_distribution'])}")
        if results["prizes_won"]:
            print(f"      - Prêmios: {dict(results['prizes_won'])}")

    # Ordenar por performance
    evaluated_games.sort(key=lambda x: x["performance_score"], reverse=True)

    # Treinar modelo com os melhores resultados
    print(f"🔄 Aprimorando modelo com resultados...")

    # Análise de números que performaram melhor
    good_numbers = Counter()
    for eg in evaluated_games[:5]:  # Top 5 jogos
        good_numbers.update(eg["numbers"])

    best_numbers = [num for num, _ in good_numbers.most_common(20)]

    # Gerar jogos refinados
    refined_games = []
    for i in range(n_games):
        variation = i % 3
        if variation == 0:
            game = sorted(best_numbers[:config["pick"]])
        elif variation == 1:
            game = sorted(random.sample(best_numbers[:15], config["pick"]))
        else:
            game = sorted(random.sample(range(1, config["range"] + 1), config["pick"]))

        refined_games.append(game)

    # Avaliar jogos refinados
    refined_evaluated = []
    for i, game in enumerate(refined_games):
        results = evaluate_game(game, real_draws, config, last_n=100)
        score = sum(h * c for h, c in results["hits_distribution"].items() if h >= 3)
        refined_evaluated.append({
            "game_number": i + 1,
            "numbers": game,
            "evaluation": results,
            "performance_score": score
        })

    refined_evaluated.sort(key=lambda x: x["performance_score"], reverse=True)

    # Selecionar melhores jogos finais
    final_games = refined_evaluated[:n_games]

    print(f"\n  📈 RESULTADO DO TREINAMENTO:")
    print(f"     Total de jogos avaliados: {len(evaluated_games) + len(refined_evaluated)}")
    print(f"     Melhores jogos selecionados: {n_games}")

    # Calcular estatísticas gerais
    total_hits = Counter()
    for eg in final_games:
        total_hits.update(eg["evaluation"]["hits_distribution"])

    avg_hits = sum(h*c for h, c in total_hits.items()) / sum(total_hits.values())

    print(f"     Média de acertos: {avg_hits:.2f}")
    print(f"     Melhor jogo: {final_games[0]['numbers']} ({final_games[0]['evaluation']['best_hit']} acertos)")

    return {
        "lottery": lottery_key,
        "name": config["name"],
        "pick": config["pick"],
        "games_trained": n_games,
        "total_draws_analyzed": len(real_draws),
        "final_games": final_games,
        "all_evaluated_games": evaluated_games + refined_evaluated,
        "top_predictions": best_numbers[:config["pick"] + 5],
        "avg_hits": avg_hits,
        "total_hits_distribution": dict(total_hits)
    }

def main():
    """Função principal"""
    print("\n" + "=" * 68)
    print("║  SIAOL-PRO v12.3 - ML COM BACKTESTING E AVALIAÇÃO REAL   ║")
    print("║        Sistema de Aprendizado com Avaliação de Acertos  ║")
    print("╚" + "=" * 68)
    print(f"  Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Jogos por loteria: 10-20 (conforme configuração)")
    print(f"  Avaliação: Backtesting vs últimos 100 sorteios")

    data_loader = LotteryDataLoader()

    results = []
    for lottery_key, config in LOTTERY_CONFIG.items():
        result = process_lottery(lottery_key, config, data_loader)
        if result:
            results.append(result)

    print(f"\n{'='*68}")
    print("  ✅ CICLO COMPLETO FINALIZADO")
    print(f"{'='*68}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Salvar relatório detalhado
    for result in results:
        filename = f"ml_training_{result['lottery']}_{timestamp}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\n{result['name']}:")
        print(f"   - Jogos treinados: {result['games_trained']}")
        print(f"   - Números por jogo: {result['pick']}")
        print(f"   - Média de acertos: {result['avg_hits']:.2f}")
        print(f"   - Arquivo: {filename}")

    # Salvar relatório final consolidado
    final_report = {
        "timestamp": timestamp,
        "date": datetime.now().isoformat(),
        "lotteries_processed": len(results),
        "results": results
    }

    report_path = os.path.join(OUTPUT_DIR, f"training_report_{timestamp}.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)

    print(f"\n  📁 Arquivo consolidado: training_report_{timestamp}.json")

if __name__ == "__main__":
    main()