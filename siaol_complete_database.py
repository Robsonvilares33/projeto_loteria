#!/usr/bin/env python3
"""
SIAOL-PRO COMPLETE DATABASE - Banco de Dados Completo de Loterias
====================================================================
Este módulo gerencia:
1. Banco de dados de TODOS os sorteios históricos
2. Sistema de FREQUÊNCIA e ATRASO
3. Matriz de CO-OCORRÊNCIA
4. Análise de PADRÕES
5. Portfólios por quantidade de números

Loterias suportadas:
- Mega-Sena (60 números, 6 por jogo)
- Lotofácil (25 números, 15 por jogo)
- Quina (80 números, 5 por jogo)
- Lotomania (100 números, 50 por jogo)
"""

import os, json, time, requests, random
from collections import Counter
from datetime import datetime
from itertools import combinations
import math

# ============================================================
# CONFIGURAÇÃO
# ============================================================
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(PROJECT_DIR, "database")

# APIs da Caixa
APIS = {
    "megasena": "mega-sena",
    "lotofacil": "lotofacil",
    "quina": "quina",
    "lotomania": "lotomania"
}

# Configurações das loterias
LOTTERY_CONFIG = {
    "megasena": {
        "name": "Mega-Sena",
        "range": 60,
        "pick": 6,
        "cost": 5.00,
        "premium_hits": [6, 5, 4],
        "emoji": "🎰"
    },
    "lotofacil": {
        "name": "Lotofácil",
        "range": 25,
        "pick": 15,
        "cost": 3.00,
        "premium_hits": [15, 14, 13, 12, 11],
        "emoji": "🎯"
    },
    "quina": {
        "name": "Quina",
        "range": 80,
        "pick": 5,
        "cost": 2.50,
        "premium_hits": [5, 4, 3],
        "emoji": "🎲"
    },
    "lotomania": {
        "name": "Lotomania",
        "range": 100,
        "pick": 50,
        "cost": 3.00,
        "premium_hits": [20, 19, 18, 17, 16, 15, 0],
        "emoji": "🎴"
    }
}

# ============================================================
# CLASSE: BANCO DE DADOS COMPLETO
# ============================================================
class LotteryDatabase:
    """Banco de dados completo de sorteios históricos"""

    def __init__(self, lottery_type):
        self.type = lottery_type
        self.config = LOTTERY_CONFIG[lottery_type]
        self.dir = os.path.join(DATABASE_DIR, lottery_type)
        os.makedirs(self.dir, exist_ok=True)

        # Arquivos do banco de dados
        self.all_draws_file = os.path.join(self.dir, "all_draws.json")
        self.frequency_file = os.path.join(self.dir, "frequency.json")
        self.delay_file = os.path.join(self.dir, "delay.json")
        self.cooccurrence_file = os.path.join(self.dir, "cooccurrence.json")
        self.statistics_file = os.path.join(self.dir, "statistics.json")
        self.summary_file = os.path.join(self.dir, "summary.json")

        # Carregar dados
        self.draws = self.load_draws()
        self.frequency = self.load_frequency()
        self.delay = self.load_delay()
        self.cooccurrence = self.load_cooccurrence()

    # ----------------------------------------------------------
    # CARREGAMENTO DE DADOS
    # ----------------------------------------------------------
    def load_draws(self):
        """Carrega todos os sorteios do banco de dados"""
        if os.path.exists(self.all_draws_file):
            with open(self.all_draws_file) as f:
                data = json.load(f)
                return data.get("draws", [])
        return []

    def load_frequency(self):
        """Carrega frequência de cada número"""
        if os.path.exists(self.frequency_file):
            with open(self.frequency_file) as f:
                return json.load(f)
        return {}

    def load_delay(self):
        """Carrega atrasos de cada número"""
        if os.path.exists(self.delay_file):
            with open(self.delay_file) as f:
                return json.load(f)
        return {}

    def load_cooccurrence(self):
        """Carrega matriz de co-ocorrência"""
        if os.path.exists(self.cooccurrence_file):
            with open(self.cooccurrence_file) as f:
                return json.load(f)
        return {}

    # ----------------------------------------------------------
    # SINCRONIZAÇÃO COM APIs
    # ----------------------------------------------------------
    def sync_from_api(self, max_retries=50):
        """Sincroniza sorteios da API da Caixa"""
        print(f"  📡 Sincronizando {self.config['name']}...")

        # Tentar múltiplas APIs
        endpoints = [
            f"https://loteriascaixa-api.herokuapp.com/api/{APIS[self.type]}/latest",
            f"https://servicebus2.caixa.gov.br/portaldeloterias/api/{APIS[self.type]}"
        ]

        latest_concurso = 0
        for url in endpoints:
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    latest_concurso = data.get("concurso") or data.get("numero") or 0
                    if latest_concurso:
                        break
            except:
                pass

        # Se API falhou, usar dados locais
        if not latest_concurso:
            print(f"     ⚠️ API indisponível - carregando dados locais...")
            self.load_local_or_demo()
            return len(self.draws)

        # Carregar concursos existentes
        existing = set(d["concurso"] for d in self.draws)
        missing = [c for c in range(max(existing) + 1 if existing else 1, latest_concurso + 1)]

        if not missing:
            print(f"     ✅ Já atualizado: {len(self.draws)} sorteios")
            return len(self.draws)

        # Baixar novos concursos
        new_draws = []
        for i, concurso in enumerate(missing[:max_retries]):
            for base_url in endpoints:
                try:
                    url = base_url.replace("latest", str(concurso))
                    r = requests.get(url, timeout=5)
                    if r.status_code == 200:
                        data = r.json()
                        numbers = data.get("listaDezenas") or data.get("dezenas") or []
                        if numbers and len(numbers) >= self.config["pick"]:
                            new_draws.append({
                                "concurso": data.get("concurso") or concurso,
                                "date": data.get("dataApuracao", ""),
                                "numbers": [int(n) for n in numbers[:self.config["pick"]]],
                                "premium_hits": {}
                            })
                            break
                except:
                    pass

            if (i + 1) % 10 == 0:
                print(f"     📥 {i+1}/{min(len(missing), max_retries)}...")

        # Mesclar e ordenar
        all_draws = {d["concurso"]: d for d in self.draws}
        for d in new_draws:
            all_draws[d["concurso"]] = d

        self.draws = sorted(all_draws.values(), key=lambda x: x["concurso"])

        # Salvar
        self.save_draws()
        if self.draws:
            self.calculate_frequency()
            self.calculate_delay()
            self.calculate_cooccurrence()
            self.calculate_statistics()

        print(f"     ✅ Sincronizado: {len(self.draws)} sorteios ({len(new_draws)} novos)")
        return len(new_draws)

    def load_local_or_demo(self):
        """Carrega dados locais ou gera demonstração"""
        local_files = [
            f"data/{self.type}_draws.json",
            f"data/{self.type}.json",
            f"memory/{self.type}_data.json"
        ]

        for f in local_files:
            path = os.path.join(PROJECT_DIR, f)
            if os.path.exists(path):
                try:
                    with open(path) as file:
                        data = json.load(file)
                        if "draws" in data:
                            self.draws = data["draws"]
                        elif "resultados" in data:
                            self.draws = data["resultados"]
                        elif "concurso" in data:
                            self.draws = [{
                                "concurso": data.get("concurso", 1),
                                "date": data.get("data", ""),
                                "numbers": data.get("numeros_sorteados") or data.get("dezenas", [])
                            }]
                        if self.draws:
                            print(f"     📁 Carregados {len(self.draws)} de {f}")
                            self.calculate_frequency()
                            self.calculate_delay()
                            self.calculate_cooccurrence()
                            return
                except:
                    pass

        # Gerar dados de demonstração
        print(f"     ⚠️ Gerando dados de demonstração...")
        self.generate_demo_data()
        self.calculate_frequency()
        self.calculate_delay()
        self.calculate_cooccurrence()
        self.calculate_statistics()

    def generate_demo_data(self):
        """Gera dados de demonstração realistas"""
        self.draws = []
        n_range = self.config["range"]
        pick = self.config["pick"]

        weights = {n: max(0.5, (n_range - n + 20) / n_range * 3) for n in range(1, n_range + 1)}

        for i in range(300):
            concurso = 2714 + i
            numbers = []
            remaining = list(range(1, n_range + 1))
            w_remaining = [weights[n] for n in remaining]

            for _ in range(pick):
                total_w = sum(w_remaining)
                r = random.random() * total_w
                cumsum = 0
                for j, w in enumerate(w_remaining):
                    cumsum += w
                    if cumsum >= r:
                        numbers.append(remaining[j])
                        w_remaining[j] = 0
                        break

            self.draws.append({
                "concurso": concurso,
                "date": f"2024-{(i // 30) + 1:02d}-{(i % 30) + 1:02d}",
                "numbers": sorted(numbers),
                "premium_hits": {}
            })

        print(f"     📊 Gerados {len(self.draws)} concursos de demonstração")

    # ----------------------------------------------------------
    # SALVAMENTO DE DADOS
    # ----------------------------------------------------------
    def save_draws(self):
        """Salva todos os sorteios"""
        with open(self.all_draws_file, 'w') as f:
            json.dump({
                "lottery": self.type,
                "total_draws": len(self.draws),
                "last_update": datetime.now().isoformat(),
                "draws": self.draws
            }, f, indent=2)

    # ----------------------------------------------------------
    # ANÁLISE: FREQUÊNCIA
    # ----------------------------------------------------------
    def calculate_frequency(self):
        """Calcula frequência de cada número"""
        counter = Counter()
        for draw in self.draws:
            for num in draw["numbers"]:
                counter[num] += 1

        self.frequency = dict(counter)
        self.save_frequency()
        return self.frequency

    def save_frequency(self):
        """Salva frequência"""
        with open(self.frequency_file, 'w') as f:
            json.dump(self.frequency, f, indent=2)

    def get_hot_numbers(self, n=15):
        """Retorna números mais frequentes"""
        return [n for n, _ in sorted(self.frequency.items(), key=lambda x: x[1], reverse=True)[:n]]

    def get_cold_numbers(self, n=15):
        """Retorna números menos frequentes"""
        return [n for n, _ in sorted(self.frequency.items(), key=lambda x: x[1])[:n]]

    # ----------------------------------------------------------
    # ANÁLISE: ATRASO
    # ----------------------------------------------------------
    def calculate_delay(self):
        """Calcula atraso de cada número (concursos desde última vez)"""
        n_range = self.config["range"]
        last_appearance = {n: 0 for n in range(1, n_range + 1)}

        for i, draw in enumerate(reversed(self.draws)):
            for num in draw["numbers"]:
                if last_appearance[num] == 0:
                    last_appearance[num] = len(self.draws) - i

        self.delay = last_appearance
        self.save_delay()
        return self.delay

    def save_delay(self):
        """Salva atrasos"""
        with open(self.delay_file, 'w') as f:
            json.dump(self.delay, f, indent=2)

    def get_delayed_numbers(self, n=15):
        """Retorna números mais atrasados"""
        return [n for n, _ in sorted(self.delay.items(), key=lambda x: x[1], reverse=True)[:n]]

    def get_overdue_numbers(self, threshold=None):
        """Retorna números que estão atrasados além da média"""
        if not self.frequency:
            return []

        n_range = self.config["range"]
        avg_interval = len(self.draws) / n_range if self.draws else 1

        if threshold is None:
            threshold = avg_interval * 1.5

        return [n for n in range(1, n_range + 1)
                if self.delay.get(n, 0) > threshold]

    # ----------------------------------------------------------
    # ANÁLISE: CO-OCORRÊNCIA
    # ----------------------------------------------------------
    def calculate_cooccurrence(self):
        """Calcula matriz de co-ocorrência (quais números saem juntos)"""
        pair_count = Counter()

        for draw in self.draws:
            nums = sorted(draw["numbers"])
            for pair in combinations(nums, 2):
                pair_count[pair] += 1

        # Converter para formato legível
        self.cooccurrence = {
            f"{p[0]}-{p[1]}": count
            for p, count in pair_count.items()
        }
        self.save_cooccurrence()
        return self.cooccurrence

    def save_cooccurrence(self):
        """Salva matriz de co-ocorrência"""
        with open(self.cooccurrence_file, 'w') as f:
            json.dump(self.cooccurrence, f, indent=2)

    def get_best_pairs(self, n=10):
        """Retorna melhores pares de números"""
        sorted_pairs = sorted(self.cooccurrence.items(), key=lambda x: x[1], reverse=True)
        return [(pair.split("-"), count) for pair, count in sorted_pairs[:n]]

    # ----------------------------------------------------------
    # ANÁLISE: ESTATÍSTICAS
    # ----------------------------------------------------------
    def calculate_statistics(self):
        """Calcula estatísticas gerais"""
        if not self.draws:
            return {}

        all_numbers = [n for draw in self.draws for n in draw["numbers"]]
        sums = [sum(draw["numbers"]) for draw in self.draws]

        stats = {
            "total_draws": len(self.draws),
            "first_draw": self.draws[0]["date"] if self.draws else None,
            "last_draw": self.draws[-1]["date"] if self.draws else None,
            "number_range": self.config["range"],
            "numbers_per_draw": self.config["pick"],
            "total_numbers_drawn": len(all_numbers),
            "unique_numbers": len(set(all_numbers)),
            "most_common_sum": sum(sums) / len(sums) if sums else 0,
            "sum_range": (min(sums), max(sums)) if sums else (0, 0),
            "avg_frequency": sum(self.frequency.values()) / len(self.frequency) if self.frequency else 0
        }

        with open(self.statistics_file, 'w') as f:
            json.dump(stats, f, indent=2)

        return stats

    # ----------------------------------------------------------
    # GERAÇÃO DE COBERTURA/PORTFÓLIO
    # ----------------------------------------------------------
    def generate_coverage(self, numbers, games_per_combination=1):
        """
        Gera cobertura de jogos para um conjunto de números

        Args:
            numbers: Lista de números escolhidos (ex: 15 números)
            games_per_combination: Quantos jogos por combinação

        Returns:
            Lista de jogos (cada jogo = pick números)
        """
        pick = self.config["pick"]
        n_range = self.config["range"]

        # Validar números
        numbers = [n for n in numbers if 1 <= n <= n_range]
        if len(numbers) < pick:
            return []

        # Gerar todas as combinações possíveis
        all_games = list(combinations(sorted(numbers), pick))

        # Calcular custo
        total_combinations = len(all_games)
        cost_per_game = self.config["cost"]

        print(f"     📊 Cobertura: {len(numbers)} números → {total_combinations} jogos")
        print(f"     💰 Custo total: R$ {total_combinations * cost_per_game:.2f}")

        # Retornar jogos (pode limitar para não exceder memória)
        return [list(game) for game in all_games]

    def generate_optimal_coverage(self, numbers, budget):
        """
        Gera cobertura otimizada dentro do orçamento

        Args:
            numbers: Lista de números escolhidos
            budget: Orçamento máximo em reais

        Returns:
            Lista de jogos otimizados
        """
        pick = self.config["pick"]
        cost_per_game = self.config["cost"]
        max_games = int(budget / cost_per_game)

        # Se cabem todos os jogos
        all_combinations = list(combinations(sorted(numbers), pick))
        if len(all_combinations) <= max_games:
            return [list(game) for game in all_combinations]

        # Selecionar jogos mais prováveis baseado em frequência
        scored_games = []
        for combo in all_combinations:
            score = sum(self.frequency.get(n, 1) for n in combo)
            scored_games.append((score, combo))

        # Ordenar por pontuação e pegar os top
        scored_games.sort(reverse=True)
        return [list(game) for _, game in scored_games[:max_games]]

    # ----------------------------------------------------------
    # RESUMO
    # ----------------------------------------------------------
    def get_summary(self):
        """Retorna resumo do banco de dados"""
        hot = self.get_hot_numbers(5)
        cold = self.get_cold_numbers(5)
        delayed = self.get_delayed_numbers(5)

        summary = {
            "lottery": self.config["name"],
            "total_draws": len(self.draws),
            "last_update": datetime.now().isoformat(),
            "hot_numbers": hot,
            "cold_numbers": cold,
            "delayed_numbers": delayed,
            "total_combinations_possible": math.comb(self.config["range"], self.config["pick"]),
            "coverage_options": self._get_coverage_options()
        }

        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        return summary

    def _get_coverage_options(self):
        """Retorna opções de cobertura com custos"""
        n_range = self.config["range"]
        pick = self.config["pick"]
        cost = self.config["cost"]

        options = []
        for n in range(pick, min(pick + 10, n_range + 1)):
            combinations_count = math.comb(n, pick)
            total_cost = combinations_count * cost
            options.append({
                "numbers": n,
                "combinations": combinations_count,
                "cost": total_cost,
                "coverage_percent": (combinations_count / math.comb(n_range, pick)) * 100
            })

        return options

    def print_summary(self):
        """Imprime resumo do banco de dados"""
        hot = self.get_hot_numbers(5)
        cold = self.get_cold_numbers(5)
        delayed = self.get_delayed_numbers(5)
        stats = self.calculate_statistics()

        print(f"\n{'='*60}")
        print(f"📊 {self.config['emoji']} {self.config['name'].upper()}")
        print(f"{'='*60}")
        print(f"   Total de sorteios: {len(self.draws)}")
        print(f"   Primeiro sorteio: {self.draws[0]['date'] if self.draws else 'N/A'}")
        print(f"   Último sorteio: {self.draws[-1]['date'] if self.draws else 'N/A'}")
        print(f"\n   🔥 NÚMEROS QUENTES: {hot}")
        print(f"   ❄️  NÚMEROS FRIOS: {cold}")
        print(f"   ⏰ NÚMEROS ATRASADOS: {delayed}")
        print(f"\n   📈 Combinações possíveis: {math.comb(self.config['range'], self.config['pick']):,}")
        print(f"{'='*60}\n")


# ============================================================
# SINCRONIZAÇÃO COMPLETA DE TODAS AS LOTERIAS
# ============================================================
def sync_all_databases():
    """Sincroniza banco de dados de todas as loterias"""
    print("\n" + "="*60)
    print("📡 SINCRONIZANDO BANCO DE DADOS COMPLETO")
    print("="*60 + "\n")

    databases = {}
    for lottery_type in LOTTERY_CONFIG.keys():
        print(f"\n🎯 {LOTTERY_CONFIG[lottery_type]['name']}:")
        db = LotteryDatabase(lottery_type)
        db.sync_from_api()
        db.print_summary()
        databases[lottery_type] = db

    return databases


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SIAOL-PRO Complete Database")
    parser.add_argument("--sync", "-s", action="store_true", help="Sincronizar banco de dados")
    parser.add_argument("--lottery", "-l", choices=["megasena", "lotofacil", "quina", "lotomania"],
                      help="Loteria específica")
    parser.add_argument("--coverage", "-c", type=int, help="Gerar cobertura com N números")
    parser.add_argument("--budget", "-b", type=float, help="Orçamento para cobertura")

    args = parser.parse_args()

    if args.sync:
        sync_all_databases()
    elif args.lottery:
        db = LotteryDatabase(args.lottery)
        db.sync_from_api()
        db.print_summary()

        if args.coverage:
            # Gerar cobertura de exemplo
            hot = db.get_hot_numbers(args.coverage)
            print(f"\n🎯 Cobertura com {len(hot)} números mais quentes:")
            print(f"   Números: {hot}")

            if args.budget:
                games = db.generate_optimal_coverage(hot, args.budget)
                print(f"   Jogos gerados: {len(games)}")
            else:
                games = db.generate_coverage(hot)
                print(f"   Total de jogos: {len(games)}")
    else:
        # Mostrar resumo de todos
        for lottery_type in LOTTERY_CONFIG.keys():
            db = LotteryDatabase(lottery_type)
            db.print_summary()
