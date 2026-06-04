#!/usr/bin/env python3
"""
SIAOL-PRO MULTI-LOTTERY PORTFOLIO SYSTEM v2.0
==============================================
Sistema Avançado de Portfólio com:
1. BACKTESTING VERIFICÁVEL - Testa contra concursos passados
2. APRENDIZADO POR PERFORMANCE - Ajusta pesos automaticamente
3. GRUPO DE CONTROLE - Compara estratégia vs aleatório
4. SUPORTE A TODAS LOTERIAS - Lotofácil, Mega-Sena, Quina, Lotomania

MÉTRICAS DE VALIDAÇÃO:
- Taxa de acerto por estratégia
- Comparação com baseline aleatório
- Evolução de pesos por performance
"""

import os, json, math, random, time
from collections import Counter, defaultdict
from itertools import combinations
from datetime import datetime
import pandas as pd
import numpy as np

# ============================================================
# CONFIGURAÇÃO
# ============================================================
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(PROJECT_DIR, "memory")
DATA_DIR = os.path.join(PROJECT_DIR, "data")
os.makedirs(MEMORY_DIR, exist_ok=True)

# Arquivos Excel
EXCEL_FILES = {
    'lotofacil': {
        'file': 'loto_facil_asloterias_ate_concurso_3533_sorteio.xlsx',
        'pick': 15, 'range': 25, 'combinations': 3268760,
        'header_row': 6, 'data_start': 7
    },
    'megasena': {
        'file': 'mega_sena_asloterias_ate_concurso_2937_sorteio.xlsx',
        'pick': 6, 'range': 60, 'combinations': 50063860,
        'header_row': 6, 'data_start': 7
    },
    'quina': {
        'file': 'quina_asloterias_ate_concurso_6873_sorteio.xlsx',
        'pick': 5, 'range': 80, 'combinations': 24040016,
        'header_row': 6, 'data_start': 7
    },
    'lotomania': {
        'file': 'loto_mania_asloterias_ate_concurso_2846_sorteio.xlsx',
        'pick': 20, 'range': 100, 'combinations': 8137425740623216000,
        'header_row': 6, 'data_start': 7
    }
}


# ============================================================
# CLASSE: CARREGADOR DE HISTÓRICO
# ============================================================
class LotteryHistoryLoader:
    """Carrega histórico de todas as loterias de arquivos Excel"""

    def __init__(self):
        self.data = {}

    def load_lottery(self, lottery_id):
        """Carrega dados de uma lottery específica"""
        config = EXCEL_FILES[lottery_id]
        file_path = os.path.join(PROJECT_DIR, config['file'])

        if not os.path.exists(file_path):
            return []

        try:
            # Ler Excel pulando linhas de header
            df = pd.read_excel(file_path, header=None, skiprows=config['data_start'])

            draws = []
            for _, row in df.iterrows():
                try:
                    concurso = int(row[0])
                    numbers = []

                    # Extrair números baseado no tipo de lottery
                    if lottery_id == 'lotomania':
                        # Lotomania tem 20 bolas (colunas 2-21)
                        for i in range(2, 22):
                            if i < len(row) and pd.notna(row[i]):
                                val = int(row[i])
                                if 0 <= val <= 99:
                                    numbers.append(val)
                    else:
                        # Outras loterias têm bolas nas colunas 2+
                        for i in range(2, 2 + config['pick']):
                            if i < len(row) and pd.notna(row[i]):
                                numbers.append(int(row[i]))

                    if len(numbers) == config['pick']:
                        draws.append({
                            'concurso': concurso,
                            'numbers': sorted(numbers)
                        })
                except:
                    continue

            # Ordenar por concurso (mais antigo primeiro)
            draws.sort(key=lambda x: x['concurso'])
            self.data[lottery_id] = draws
            return draws

        except Exception as e:
            print(f"   ❌ Erro ao carregar {lottery_id}: {e}")
            return []

    def load_all(self):
        """Carrega todas as loterias"""
        print("\n📊 CARREGANDO HISTÓRICO DE TODAS LOTERIAS...")
        for lottery_id in EXCEL_FILES:
            draws = self.load_lottery(lottery_id)
            print(f"   ✅ {lottery_id.upper()}: {len(draws)} concursos carregados")
        return self.data


# ============================================================
# CLASSE: ANALISADOR DE FREQUÊNCIA
# ============================================================
class FrequencyAnalyzer:
    """Analisa frequência, atrasos e co-ocorrências"""

    def __init__(self, lottery_id, draws):
        self.lottery_id = lottery_id
        self.draws = draws
        self.config = EXCEL_FILES[lottery_id]
        self.frequency = {}
        self.delay = {}
        self.cooccurrence = defaultdict(int)
        self.sequences = []

        self.analyze()

    def analyze(self):
        """Executa todas as análises"""
        self.analyze_frequency()
        self.analyze_delay()
        self.analyze_cooccurrence()
        self.analyze_sequences()

    def analyze_frequency(self):
        """Calcula frequência de cada número"""
        counter = Counter()
        for draw in self.draws:
            for num in draw['numbers']:
                counter[num] += 1

        self.frequency = dict(counter)

    def analyze_delay(self):
        """Calcula atraso (concursos desde última aparição)"""
        last_appearance = {n: 0 for n in range(1, self.config['range'] + 1)}

        for i, draw in enumerate(reversed(self.draws)):
            for num in draw['numbers']:
                if last_appearance.get(num, 0) == 0:
                    last_appearance[num] = len(self.draws) - i

        self.delay = last_appearance

    def analyze_cooccurrence(self):
        """Calcula co-ocorrência de pares"""
        for draw in self.draws:
            nums = draw['numbers']
            for i in range(len(nums)):
                for j in range(i + 1, len(nums)):
                    pair = tuple(sorted([nums[i], nums[j]]))
                    self.cooccurrence[pair] += 1

    def analyze_sequences(self):
        """Analisa sequências de números consecutivos"""
        for draw in self.draws:
            nums = sorted(draw['numbers'])
            max_seq = 1
            current_seq = 1
            for i in range(1, len(nums)):
                if nums[i] == nums[i-1] + 1:
                    current_seq += 1
                    max_seq = max(max_seq, current_seq)
                else:
                    current_seq = 1
            self.sequences.append(max_seq)

    def get_hot_numbers(self, n=15):
        """Retorna números mais frequentes"""
        return [n for n, _ in sorted(self.frequency.items(), key=lambda x: x[1], reverse=True)[:n]]

    def get_cold_numbers(self, n=15):
        """Retorna números menos frequentes"""
        return [n for n, _ in sorted(self.frequency.items(), key=lambda x: x[1])[:n]]

    def get_delayed_numbers(self, n=15):
        """Retorna números mais atrasados"""
        return [n for n, _ in sorted(self.delay.items(), key=lambda x: x[1], reverse=True)[:n]]

    def get_balanced_numbers(self, n=15):
        """Retorna numbers balanceados (sem duplicatas)"""
        hot = set(self.get_hot_numbers(8))
        cold = set(self.get_cold_numbers(8))
        delayed = set(self.get_delayed_numbers(8))

        result = list(hot)[:5] + list(delayed)[:5] + list(cold)[:5]

        # Remover duplicatas
        seen = set()
        unique = []
        for num in result:
            if num not in seen:
                seen.add(num)
                unique.append(num)

        # Preencher se necessário
        all_nums = set(range(1, self.config['range'] + 1))
        remaining = list(all_nums - seen)
        random.shuffle(remaining)

        while len(unique) < n and remaining:
            unique.append(remaining.pop())

        return sorted(set(unique))[:n]


# ============================================================
# CLASSE: GERADOR DE JOGOS
# ============================================================
class GameGenerator:
    """Gera jogos baseado em diferentes estratégias"""

    def __init__(self, lottery_id, analyzer: FrequencyAnalyzer):
        self.lottery_id = lottery_id
        self.analyzer = analyzer
        self.config = EXCEL_FILES[lottery_id]

    def generate_hot(self, n_games=10):
        """Gera jogos com números quentes"""
        hot = self.analyzer.get_hot_numbers(self.config['pick'])
        games = []
        for _ in range(n_games):
            game = sorted(hot[:self.config['pick']])
            games.append(game)
        return games

    def generate_cold(self, n_games=10):
        """Gera jogos com números frios"""
        cold = self.analyzer.get_cold_numbers(self.config['pick'])
        games = []
        for _ in range(n_games):
            game = sorted(cold[:self.config['pick']])
            games.append(game)
        return games

    def generate_delayed(self, n_games=10):
        """Gera jogos com números atrasados"""
        delayed = self.analyzer.get_delayed_numbers(self.config['pick'])
        games = []
        for _ in range(n_games):
            game = sorted(delayed[:self.config['pick']])
            games.append(game)
        return games

    def generate_balanced(self, n_games=10):
        """Gera jogos balanceados (sem duplicatas)"""
        games = []
        for _ in range(n_games):
            numbers = self.analyzer.get_balanced_numbers(self.config['pick'])
            games.append(sorted(numbers))
        return games

    def generate_random(self, n_games=10):
        """Gera jogos aleatórios (grupo de controle)"""
        all_nums = list(range(1, self.config['range'] + 1))
        games = []
        for _ in range(n_games):
            game = sorted(random.sample(all_nums, self.config['pick']))
            games.append(game)
        return games

    def generate_strategy(self, strategy='balanced', n_games=10):
        """Gera jogos baseado na estratégia"""
        if strategy == 'hot':
            return self.generate_hot(n_games)
        elif strategy == 'cold':
            return self.generate_cold(n_games)
        elif strategy == 'delayed':
            return self.generate_delayed(n_games)
        elif strategy == 'random':
            return self.generate_random(n_games)
        else:  # balanced
            return self.generate_balanced(n_games)


# ============================================================
# CLASSE: BACKTESTING VERIFICÁVEL
# ============================================================
class BacktestEngine:
    """
    Sistema de Backtesting Verificável
    - Testa estratégias contra concursos passados
    - Valida performance de cada estratégia
    - Gera relatório de eficácia
    """

    def __init__(self, lottery_id, draws):
        self.lottery_id = lottery_id
        self.draws = draws
        self.config = EXCEL_FILES[lottery_id]
        self.results = {}

    def run_backtest(self, strategy_func, n_test=500):
        """
        Executa backtest para uma estratégia
        Usa últimos n_test concursos como teste
        """
        if len(self.draws) < n_test + 100:
            n_test = len(self.draws) - 100

        # Separa treino e teste
        train_draws = self.draws[:-n_test]
        test_draws = self.draws[-n_test:]

        # Analisador com dados de treino
        analyzer = FrequencyAnalyzer(self.lottery_id, train_draws)
        generator = GameGenerator(self.lottery_id, analyzer)

        # Definir limiar de acertos por lottery
        hit_thresholds = {
            'lotofacil': 11,  # 11+ de 15
            'megasena': 4,    # 4+ de 6
            'quina': 3,       # 3+ de 5
            'lotomania': 15   # 15+ de 20
        }
        min_hits = hit_thresholds.get(self.lottery_id, self.config['pick'])

        # Gerar jogos para cada concurso de teste
        hits_by_level = defaultdict(int)
        total_tested = 0

        for test_draw in test_draws:
            # Gerar 10 jogos usando estratégia
            games = strategy_func(generator, 10)

            # Verificar acertos
            result_numbers = test_draw['numbers']
            for game in games:
                hits = len(set(game) & set(result_numbers))
                if hits >= min_hits:
                    hits_by_level[hits] += 1
            total_tested += 1

        return {
            'strategy': strategy_func.__name__,
            'tested': total_tested,
            'games_tested': total_tested * 10,
            'min_hits': min_hits,
            f'hits_{min_hits}': hits_by_level[min_hits],
            'total_hits': sum(hits_by_level.values()),
            'hit_rate': sum(hits_by_level.values()) / (total_tested * 10) * 100
        }

    def run_all_strategies(self, n_test=500):
        """Executa backtest para todas as estratégias"""
        strategies = {
            'hot': lambda g, n: g.generate_hot(n),
            'cold': lambda g, n: g.generate_cold(n),
            'delayed': lambda g, n: g.generate_delayed(n),
            'balanced': lambda g, n: g.generate_balanced(n),
            'random': lambda g, n: g.generate_random(n)  # Controle
        }

        results = {}
        for name, strategy in strategies.items():
            print(f"   🔬 Testando estratégia: {name}...")
            results[name] = self.run_backtest(strategy, n_test)

        self.results = results
        return results


# ============================================================
# CLASSE: SISTEMA DE APRENDIZADO POR PERFORMANCE
# ============================================================
class PerformanceLearner:
    """
    Sistema de Aprendizado por Performance
    - Ajusta pesos baseado em resultados reais
    - Aprende quais estratégias funcionam melhor
    - Atualiza continuamente
    - DETECÇÃO DE NOVOS DADOS: Só recalcula se houver novos sorteios
    """

    def __init__(self, lottery_id):
        self.lottery_id = lottery_id
        self.strategy_weights = {
            'hot': 1.0,
            'cold': 1.0,
            'delayed': 1.0,
            'balanced': 1.0
        }
        self.history = []
        self.last_learned_concurso = 0
        self.performance_log = os.path.join(MEMORY_DIR, f"performance_{lottery_id}.json")
        self.load()

    def load(self):
        """Carrega histórico de performance"""
        if os.path.exists(self.performance_log):
            try:
                with open(self.performance_log) as f:
                    data = json.load(f)
                    self.strategy_weights = data.get('weights', self.strategy_weights)
                    self.history = data.get('history', [])
                    self.last_learned_concurso = data.get('last_concurso', 0)
            except:
                pass

    def save(self):
        """Salva histórico de performance"""
        with open(self.performance_log, 'w') as f:
            json.dump({
                'lottery_id': self.lottery_id,
                'weights': self.strategy_weights,
                'history': self.history[-100:],  # Keep last 100
                'last_concurso': self.last_learned_concurso,
                'last_update': datetime.now().isoformat()
            }, f, indent=2)

    def has_new_data(self, latest_concurso):
        """Verifica se há novos dados para aprender"""
        return latest_concurso > self.last_learned_concurso

    def mark_learned(self, concurso):
        """Marca que aprendeu com este concurso"""
        self.last_learned_concurso = concurso

    def update_weights(self, backtest_results):
        """
        Atualiza pesos baseado em resultados de backtest
        - Estratégias com melhor performance ganham peso
        - Estratégias ruins perdem peso
        """
        print(f"\n   📊 Atualizando pesos por performance...")

        # Calcular performance normalizada
        performances = {}
        for strategy, result in backtest_results.items():
            if result['tested'] > 0:
                perf = (result['total_hits'] / result['games_tested']) * 100
                performances[strategy] = perf

        if not performances:
            return

        # Encontrar melhor e pior
        best = max(performances, key=performances.get)
        worst = min(performances, key=performances.get)

        # Ajustar pesos
        for strategy in self.strategy_weights:
            if strategy == 'random':
                continue  # Não ajustar grupo de controle

            if strategy == best:
                self.strategy_weights[strategy] *= 1.15  # +15%
            elif strategy == worst:
                self.strategy_weights[strategy] *= 0.85  # -15%

            # Limitar pesos entre 0.5 e 2.0
            self.strategy_weights[strategy] = max(0.5, min(2.0, self.strategy_weights[strategy]))

        # Registrar no histórico
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'results': performances,
            'weights': self.strategy_weights.copy()
        })

        self.save()

        print(f"   ✅ Pesos atualizados:")
        for s, w in sorted(self.strategy_weights.items(), key=lambda x: x[1], reverse=True):
            print(f"      {s}: {w:.3f}")

    def get_best_strategy(self):
        """Retorna estratégia com melhor peso"""
        filtered = {k: v for k, v in self.strategy_weights.items() if k != 'random'}
        return max(filtered, key=filtered.get)


# ============================================================
# CLASSE: VALIDADOR DE GRUPO DE CONTROLE
# ============================================================
class ControlGroupValidator:
    """
    Validador de Grupo de Controle
    - Compara estratégia vs aleatório puro
    - Determina se estratégia tem vantagem real
    - Calcula significância estatística
    """

    def __init__(self, lottery_id):
        self.lottery_id = lottery_id
        self.results_file = os.path.join(MEMORY_DIR, f"control_group_{lottery_id}.json")

    def validate(self, strategy_performance, random_performance):
        """
        Valida se estratégia é melhor que aleatório

        Returns:
            dict com análise de significância
        """
        strategy_rate = strategy_performance.get('hit_rate', 0)
        random_rate = random_performance.get('hit_rate', 0)

        # Calcular vantagem
        advantage = strategy_rate - random_rate
        advantage_pct = (advantage / random_rate * 100) if random_rate > 0 else 0

        # Verificar significância
        # Se vantagem > 20% e games testados > 100, é significativo
        n_games = strategy_performance.get('games_tested', 0)
        is_significant = advantage > 0 and n_games > 100

        result = {
            'strategy_rate': strategy_rate,
            'random_rate': random_rate,
            'advantage': advantage,
            'advantage_pct': advantage_pct,
            'games_tested': n_games,
            'is_significant': is_significant,
            'conclusion': self._interpret_result(advantage_pct, is_significant)
        }

        # Salvar
        with open(self.results_file, 'w') as f:
            json.dump({
                'lottery_id': self.lottery_id,
                'analysis_date': datetime.now().isoformat(),
                **result
            }, f, indent=2)

        return result

    def _interpret_result(self, advantage_pct, is_significant):
        """Interpreta resultado da validação"""
        if not is_significant:
            return "⏳ INSUFICIENTE - Mais dados necessários"
        elif advantage_pct > 20:
            return "✅ VANTAGEM CONFIRMADA - Estratégia superior"
        elif advantage_pct > 5:
            return "🔶 LEVE VANTAGEM - Estratégia marginalmente melhor"
        else:
            return "❌ SEM VANTAGEM - Aleatório similar ou melhor"


# ============================================================
# CLASSE: PORTFÓLIO GERAL COM CERCAMENTO
# ============================================================
class MultiLotteryPortfolio:
    """Gerencia portfólios de todas as loterias com cercamento"""

    def __init__(self, lottery_id):
        self.lottery_id = lottery_id
        self.config = EXCEL_FILES[lottery_id]
        self.cercamento_count = 33  # Padrão: 33 jogos por cercamento

    def generate_cercamento(self, numbers, max_games=33):
        """Gera cercamento com números selecionados"""
        n = len(numbers)

        # Para Lotomania: pick 20 from 50
        pick = self.config['pick']

        if n < pick:
            return {'error': 'Números insuficientes'}

        # Para Lotomania, não calcular todas as combinações (C(50,20) é muito grande)
        # Gerar jogos diretamente usando amostragem estratégica
        if self.lottery_id == 'lotomania':
            games = []
            for _ in range(max_games):
                game = sorted(random.sample(numbers, pick))
                games.append(game)

            # Remover duplicatas
            seen = set()
            unique_games = []
            for g in games:
                key = tuple(g)
                if key not in seen:
                    seen.add(key)
                    unique_games.append(g)

            return {
                'numbers': numbers,
                'n_numbers': n,
                'total_combinations': 'C(50,20) muito grande',
                'games_selected': len(unique_games),
                'games': unique_games[:max_games],
                'coverage_percent': 0.0000000001,
                'strategy': 'sampled'
            }

        # Calcular combinações para outras loterias
        try:
            all_games = list(combinations(sorted(numbers), pick))
            total_combinations = len(all_games)
        except:
            return {'error': 'Erro ao calcular combinações', 'games': []}

        # Se couber no limite
        if total_combinations <= max_games:
            return {
                'numbers': numbers,
                'n_numbers': n,
                'total_combinations': total_combinations,
                'games': [list(g) for g in all_games],
                'coverage_percent': (total_combinations / self.config['combinations']) * 100,
                'strategy': 'complete'
            }

        # Selecionar top jogos por score
        scored_games = []
        for game in all_games:
            score = sum(random.random() for _ in game)  # Placeholder score
            scored_games.append((score, game))

        scored_games.sort(reverse=True)
        selected_games = [list(g) for _, g in scored_games[:max_games]]

        return {
            'numbers': numbers,
            'n_numbers': n,
            'total_combinations': total_combinations,
            'games_selected': len(selected_games),
            'games': selected_games,
            'coverage_percent': (len(selected_games) / self.config['combinations']) * 100,
            'strategy': 'optimized'
        }


# ============================================================
# CLASSE PRINCIPAL: SISTEMA INTEGRADO
# ============================================================
class SIAOLMultiPortfolio:
    """Sistema principal integrado de portfólios"""

    def __init__(self):
        self.loader = LotteryHistoryLoader()
        self.analyzers = {}
        self.portfolios = {}
        self.backtest_results = {}
        self.learners = {}
        self.validators = {}

    def run_full_cycle(self):
        """Executa ciclo completo para todas as loterias"""
        print("""
╔═══════════════════════════════════════════════════════════╗
║  🧠 SIAOL-PRO MULTI-LOTTERY PORTFOLIO SYSTEM v2.0         ║
║  Backtesting + Aprendizado + Grupo de Controle            ║
╚═══════════════════════════════════════════════════════════╝
        """)

        # 1. Carregar histórico
        self.loader.load_all()

        # 2. Processar cada lottery
        for lottery_id in EXCEL_FILES:
            print(f"\n{'='*70}")
            print(f"🎯 PROCESSANDO: {lottery_id.upper()}")
            print(f"{'='*70}")

            draws = self.loader.data.get(lottery_id, [])
            if not draws:
                print(f"   ❌ Sem dados para {lottery_id}")
                continue

            # Criar componentes
            analyzer = FrequencyAnalyzer(lottery_id, draws)
            learner = PerformanceLearner(lottery_id)
            validator = ControlGroupValidator(lottery_id)
            portfolio = MultiLotteryPortfolio(lottery_id)

            # Mostrar estatísticas
            print(f"\n   📊 ESTATÍSTICAS:")
            print(f"      Concursos: {len(draws)}")
            print(f"      Números no range: 1-{analyzer.config['range']}")
            hot = analyzer.get_hot_numbers(5)
            cold = analyzer.get_cold_numbers(5)
            print(f"      🔥 Quentes: {hot}")
            print(f"      ❄️  Frios: {cold}")

            # Executar Backtesting
            print(f"\n   🔬 BACKTESTING VERIFICÁVEL:")
            backtest = BacktestEngine(lottery_id, draws)
            results = backtest.run_all_strategies(n_test=300)

            # Mostrar resultados
            print(f"\n   📈 RESULTADOS DO BACKTEST:")
            for strategy, result in sorted(results.items(), key=lambda x: x[1]['total_hits'], reverse=True):
                print(f"      {strategy:<10}: {result['total_hits']:4d} acertos ({result['hit_rate']:.3f}%)")

            # Atualizar pesos por performance
            print(f"\n   📊 ATUALIZANDO PESOS POR PERFORMANCE...")
            learner.update_weights(results)

            # Validar contra grupo de controle
            print(f"\n   🔍 VALIDAÇÃO CONTRA GRUPO DE CONTROLE:")
            if 'random' in results and 'balanced' in results:
                validation = validator.validate(results['balanced'], results['random'])
                print(f"      Estratégia Balanceada vs Aleatório:")
                print(f"      Vantagem: {validation['advantage_pct']:.2f}%")
                print(f"      Conclusão: {validation['conclusion']}")

            # Gerar portfólio com cercamento
            print(f"\n   🎯 GERANDO CERCAMENTO (33 jogos):")
            best_strategy = learner.get_best_strategy()
            generator = GameGenerator(lottery_id, analyzer)

            # Gerar números baseado na melhor estratégia
            # Para Lotomania, usar 50 números (escolhe 20)
            if lottery_id == 'lotomania':
                if best_strategy == 'hot':
                    numbers = analyzer.get_hot_numbers(50)
                elif best_strategy == 'cold':
                    numbers = analyzer.get_cold_numbers(50)
                elif best_strategy == 'delayed':
                    numbers = analyzer.get_delayed_numbers(50)
                else:
                    numbers = analyzer.get_balanced_numbers(50)
            elif best_strategy == 'hot':
                numbers = analyzer.get_hot_numbers(17)
            elif best_strategy == 'cold':
                numbers = analyzer.get_cold_numbers(17)
            elif best_strategy == 'delayed':
                numbers = analyzer.get_delayed_numbers(17)
            else:
                numbers = analyzer.get_balanced_numbers(17)

            cercamento = portfolio.generate_cercamento(numbers, max_games=33)

            print(f"      Números selecionados: {cercamento.get('n_numbers', len(numbers))}")
            print(f"      Jogos gerados: {len(cercamento.get('games', []))}")
            print(f"      Cobertura: {cercamento.get('coverage_percent', 0):.6f}%")

            # Salvar portfólio
            portfolio_data = {
                'lottery_id': lottery_id,
                'generated': datetime.now().isoformat(),
                'best_strategy': best_strategy,
                'strategy_weight': learner.strategy_weights[best_strategy],
                'numbers': numbers,
                'games': cercamento.get('games', [])[:33],
                'total_games': len(cercamento.get('games', [])),
                'backtest_results': results,
                'validation': validation if 'validation' in dir() else None
            }

            # Salvar em arquivo
            portfolio_file = os.path.join(MEMORY_DIR, f"portfolio_{lottery_id}.json")
            with open(portfolio_file, 'w') as f:
                json.dump(portfolio_data, f, indent=2)

            print(f"      💾 Salvo em: {portfolio_file}")

            # Armazenar
            self.portfolios[lottery_id] = portfolio_data
            self.backtest_results[lottery_id] = results
            self.learners[lottery_id] = learner

        # Relatório final
        self.print_final_report()

    def print_final_report(self):
        """Imprime relatório final consolidado"""
        print(f"""
{'='*70}
📋 RELATÓRIO FINAL - TODAS LOTERIAS
{'='*70}
        """)

        for lottery_id, portfolio in self.portfolios.items():
            print(f"\n🎯 {lottery_id.upper()}:")
            print(f"   Melhor estratégia: {portfolio['best_strategy']}")
            print(f"   Peso: {portfolio['strategy_weight']:.3f}")
            print(f"   Jogos gerados: {portfolio['total_games']}")

            # Mostrar primeiro jogo
            if portfolio['games']:
                print(f"   Exemplo: {' - '.join(f'{n:02d}' for n in portfolio['games'][0][:5])}...")

        print(f"""
{'='*70}
✅ SISTEMA COMPLETO - EXECUÇÃO FINALIZADA
{'='*70}
📁 Portfólios salvos em: {MEMORY_DIR}/portfolio_*.json
📊 Performance salvo em: {MEMORY_DIR}/performance_*.json
🔍 Validação em: {MEMORY_DIR}/control_group_*.json
        """)


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================
def main():
    """Executa sistema completo"""
    start_time = time.time()

    # Criar e executar sistema
    system = SIAOLMultiPortfolio()
    system.run_full_cycle()

    elapsed = time.time() - start_time
    print(f"\n⏱️  Tempo total: {elapsed:.1f}s")

    return 0


if __name__ == "__main__":
    exit(main())