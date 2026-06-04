#!/usr/bin/env python3
"""
SIAOL-PRO LOTOFÁCIL PORTFOLIO GENERATOR
========================================
Sistema de Portfólio com Cercamento Estratégico

FUNCIONALIDADES:
1. Carrega histórico completo de concursos (3.702 concursos)
2. Analisa padrões de frequência (quentes/frios)
3. Estuda co-ocorrências e sequências
4. Gera portfólio com cercamento estratégico
5. Cria jogos otimizados baseados em dados reais

ESTRATÉGIA DE CERCAMENTO:
- Seleciona números baseado em análise estatística
- Gera conjunto de jogos que maximizam cobertura
- Objetivo: cercar o resultado com menor custo possível
"""

import os, json, math, random
from collections import Counter, defaultdict
from itertools import combinations
from datetime import datetime
import pandas as pd

# ============================================================
# CONFIGURAÇÃO
# ============================================================
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
MEMORY_DIR = os.path.join(PROJECT_DIR, "memory")
os.makedirs(MEMORY_DIR, exist_ok=True)

# Lotofácil: 25 números, escolhe 15
LOTOFACIL_RANGE = 25
LOTOFACIL_PICK = 15
TOTAL_COMBINATIONS = 3268760  # C(25,15)

# Arquivos
EXCEL_FILE = os.path.join(DATA_DIR, "Lotofácil.xlsx")
COMBINATIONS_FILE = os.path.join(DATA_DIR, "combinations-15.txt")
HISTORY_FILE = os.path.join(MEMORY_DIR, "lotofacil_history.json")
FREQUENCY_FILE = os.path.join(MEMORY_DIR, "lotofacil_frequency.json")
PATTERNS_FILE = os.path.join(MEMORY_DIR, "lotofacil_patterns.json")


# ============================================================
# CLASSE: ANALISADOR DE HISTÓRICO
# ============================================================
class LotofacilAnalyzer:
    """Analisa histórico completo da Lotofácil"""

    def __init__(self):
        self.draws = []
        self.frequency = {}
        self.delay = {}
        self.cooccurrence = defaultdict(int)
        self.sequences = []
        self.last_20_draws = []

        # Carregar dados
        self.load_history()

    def load_history(self):
        """Carrega histórico do Excel"""
        if not os.path.exists(EXCEL_FILE):
            print(f"   ❌ Arquivo não encontrado: {EXCEL_FILE}")
            return

        print(f"   📊 Carregando histórico de concursos...")

        try:
            df = pd.read_excel(EXCEL_FILE)

            for _, row in df.iterrows():
                concurso = int(row['Concurso'])
                numbers = []

                # Extrair as 15 bolas
                for i in range(1, 16):
                    col = f'Bola{i}'
                    if col in row and pd.notna(row[col]):
                        numbers.append(int(row[col]))

                if len(numbers) == 15:
                    self.draws.append({
                        'concurso': concurso,
                        'date': str(row['Data Sorteio']) if pd.notna(row.get('Data Sorteio')) else '',
                        'numbers': sorted(numbers),
                        'winners_15': row.get('Ganhadores 15 acertos', 0),
                        'prize_15': row.get('Rateio 15 acertos', 0)
                    })

            print(f"   ✅ Carregados {len(self.draws)} concursos")

            # Salvar histórico processado
            self.save_processed_history()

            # Analisar dados
            self.analyze_frequency()
            self.analyze_delay()
            self.analyze_cooccurrence()
            self.analyze_sequences()

        except Exception as e:
            print(f"   ❌ Erro ao carregar: {e}")

    def save_processed_history(self):
        """Salva histórico processado em JSON"""
        with open(HISTORY_FILE, 'w') as f:
            json.dump({
                'total_draws': len(self.draws),
                'last_update': datetime.now().isoformat(),
                'draws': self.draws[-100:]  # Últimos 100 para referência
            }, f, indent=2)

    def analyze_frequency(self):
        """Analisa frequência de cada número"""
        counter = Counter()

        for draw in self.draws:
            for num in draw['numbers']:
                counter[num] += 1

        self.frequency = dict(counter)

        # Salvar
        freq_data = {
            'analysis_date': datetime.now().isoformat(),
            'total_draws': len(self.draws),
            'frequency': self.frequency
        }

        with open(FREQUENCY_FILE, 'w') as f:
            json.dump(freq_data, f, indent=2)

        # Estatísticas
        total = len(self.draws)
        avg_freq = total * 15 / LOTOFACIL_RANGE

        hot = sorted(self.frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        cold = sorted(self.frequency.items(), key=lambda x: x[1])[:10]

        print(f"\n   📈 FREQUÊNCIA ESTATÍSTICA:")
        print(f"      Total de concursos: {total}")
        print(f"      Frequência média: {avg_freq:.1f}")
        print(f"   🔥 TOP 10 QUENTES: {[n for n, _ in hot]}")
        print(f"   ❄️  TOP 10 FRIOS: {[n for n, _ in cold]}")

    def analyze_delay(self):
        """Analisa atraso de cada número (concursos desde última vez)"""
        last_appearance = {n: 0 for n in range(1, LOTOFACIL_RANGE + 1)}

        for i, draw in enumerate(reversed(self.draws)):
            for num in draw['numbers']:
                if last_appearance[num] == 0:
                    last_appearance[num] = len(self.draws) - i

        self.delay = last_appearance

        # Números mais atrasados
        delayed = sorted(self.delay.items(), key=lambda x: x[1], reverse=True)[:10]
        print(f"   ⏰ TOP 10 ATRASADOS: {[n for n, _ in delayed]}")

    def analyze_cooccurrence(self):
        """Analisa quais números saem juntos"""
        pair_count = defaultdict(int)

        for draw in self.draws:
            nums = draw['numbers']
            for i in range(len(nums)):
                for j in range(i + 1, len(nums)):
                    pair = tuple(sorted([nums[i], nums[j]]))
                    pair_count[pair] += 1

        self.cooccurrence = dict(pair_count)

        # Melhores pares
        best_pairs = sorted(pair_count.items(), key=lambda x: x[1], reverse=True)[:10]
        print(f"   🔗 MELHORES PARES: {[(p[0], p[1]) for p, c in best_pairs[:5]]}")

    def analyze_sequences(self):
        """Analisa sequências (números que saem em sequência)"""
        self.sequences = []

        for draw in self.draws:
            nums = draw['numbers']
            # Contar sequências de 2+ números consecutivos
            sorted_nums = sorted(nums)
            max_seq = 1
            current_seq = 1

            for i in range(1, len(sorted_nums)):
                if sorted_nums[i] == sorted_nums[i-1] + 1:
                    current_seq += 1
                    max_seq = max(max_seq, current_seq)
                else:
                    current_seq = 1

            self.sequences.append(max_seq)

        # Estatísticas de sequências
        avg_seq = sum(self.sequences) / len(self.sequences) if self.sequences else 0
        max_seq = max(self.sequences) if self.sequences else 0

        print(f"   📊 SEQUÊNCIAS - Média: {avg_seq:.1f}, Máx: {max_seq}")

        # Salvar padrões
        patterns = {
            'analysis_date': datetime.now().isoformat(),
            'avg_sequence': avg_seq,
            'max_sequence': max_seq,
            'sequence_distribution': dict(Counter(self.sequences))
        }

        with open(PATTERNS_FILE, 'w') as f:
            json.dump(patterns, f, indent=2)

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
        """Retorna números balanceados (quentes + frios + atrasados) sem duplicatas"""
        hot = set(self.get_hot_numbers(8))
        cold = set(self.get_cold_numbers(8))
        delayed = set(self.get_delayed_numbers(8))

        # Combinar estratégias sem duplicatas
        result = list(hot)[:5] + list(delayed)[:5] + list(cold)[:5]

        # Remover duplicatas preservando ordem
        seen = set()
        unique_result = []
        for num in result:
            if num not in seen:
                seen.add(num)
                unique_result.append(num)

        result = unique_result

        # Preencher se necessário com números restantes (sem duplicatas)
        all_nums = set(range(1, LOTOFACIL_RANGE + 1))
        used = set(result)
        remaining = list(all_nums - used)
        random.shuffle(remaining)

        while len(result) < n and remaining:
            result.append(remaining.pop())

        return sorted(set(result))[:n]


# ============================================================
# CLASSE: GERADOR DE CERCAMENTO (PORTFÓLIO)
# ============================================================
class LotofacilCercamento:
    """
    Sistema de Cercamento Estratégico

    Baseado na análise do histórico, gera um conjunto de jogos
    que maximizam a chance de acertar o resultado.
    """

    def __init__(self, analyzer: LotofacilAnalyzer):
        self.analyzer = analyzer
        self.total_combinations = TOTAL_COMBINATIONS

    def generate_strategic_numbers(self, strategy='balanced', n=18):
        """
        Gera números estratégicos baseado na estratégia
        Sem duplicatas
        """
        if strategy == 'hot':
            numbers = self.analyzer.get_hot_numbers(n)
        elif strategy == 'cold':
            numbers = self.analyzer.get_cold_numbers(n)
        elif strategy == 'delayed':
            numbers = self.analyzer.get_delayed_numbers(n)
        elif strategy == 'balanced':
            numbers = self.analyzer.get_balanced_numbers(n)
        else:
            numbers = self.analyzer.get_balanced_numbers(n)

        # Garantir que temos exatamente n números (sem duplicatas)
        numbers = sorted(set(numbers))

        while len(numbers) < n:
            remaining = [x for x in range(1, LOTOFACIL_RANGE + 1) if x not in numbers]
            if remaining:
                numbers.append(random.choice(remaining))
            else:
                break

        return sorted(set(numbers))[:n]

    def generate_cercamento(self, numbers, max_games=33):
        """
        Gera cercamento com números selecionados

        Args:
            numbers: Lista de 15-25 números para cercar
            max_games: Máximo de jogos (padrão 33)

        Returns:
            Lista de jogos e informações de cobertura
        """
        n = len(numbers)

        if n < LOTOFACIL_PICK:
            return {'error': 'Números insuficientes', 'games': []}

        # Calcular todas as combinações possíveis
        all_games = list(combinations(sorted(numbers), LOTOFACIL_PICK))
        total_combinations = len(all_games)

        # Se cabem todos os jogos dentro do limite
        if total_combinations <= max_games:
            return {
                'numbers': numbers,
                'n_numbers': n,
                'total_combinations': total_combinations,
                'games': [list(g) for g in all_games],
                'coverage_percent': (total_combinations / self.total_combinations) * 100,
                'strategy': 'complete'
            }

        # Selecionar jogos mais prováveis baseado em análise
        scored_games = []

        for game in all_games:
            # Calcular pontuação baseada em:
            # 1. Frequência dos números no jogo
            # 2. Atraso dos números
            # 3. Co-ocorrência dos pares

            freq_score = sum(self.analyzer.frequency.get(n, 1) for n in game)
            delay_score = sum(self.analyzer.delay.get(n, 1) for n in game)

            # Co-ocorrência
            cooc_score = 0
            for i in range(len(game)):
                for j in range(i + 1, len(game)):
                    pair = tuple(sorted([game[i], game[j]]))
                    cooc_score += self.analyzer.cooccurrence.get(pair, 0)

            # Score final (ponderado)
            score = freq_score * 0.4 + delay_score * 0.3 + cooc_score * 0.3

            scored_games.append((score, game))

        # Ordenar por pontuação e pegar os top
        scored_games.sort(reverse=True)
        selected_games = [list(g) for _, g in scored_games[:max_games]]

        return {
            'numbers': numbers,
            'n_numbers': n,
            'total_combinations': total_combinations,
            'games_selected': len(selected_games),
            'games': selected_games,
            'coverage_percent': (len(selected_games) / self.total_combinations) * 100,
            'strategy': 'optimized'
        }

    def generate_optimal_cercamento(self, budget_games=33):
        """
        Gera cercamento otimizado dentro do limite de jogos

        Tenta diferentes combinações de números e estratégias
        para encontrar o melhor cercamento possível.
        """
        strategies = ['balanced', 'hot', 'delayed']
        num_options = [15, 16, 17, 18, 19, 20]

        best_result = None
        best_score = 0

        for strategy in strategies:
            for n_nums in num_options:
                numbers = self.generate_strategic_numbers(strategy, n_nums)
                result = self.generate_cercamento(numbers, max_games=budget_games)

                if 'error' in result:
                    continue

                # Calcular score de qualidade
                # Considera: cobertura, diversidade, estratégia
                quality_score = (
                    result['coverage_percent'] * 0.5 +
                    len(set(tuple(g) for g in result['games'])) * 0.3 / budget_games * 100 +
                    (25 - abs(n_nums - 17)) * 2  # Prefere 17 números
                )

                if quality_score > best_score:
                    best_score = quality_score
                    best_result = {
                        **result,
                        'strategy': strategy,
                        'n_numbers': n_nums,
                        'quality_score': quality_score
                    }

        return best_result


# ============================================================
# CLASSE: PORTFÓLIO GERAL
# ============================================================
class LotofacilPortfolio:
    """Gerencia portfólios de jogos"""

    def __init__(self, cercamento: LotofacilCercamento):
        self.cercamento = cercamento
        self.portfolios = {}
        self.portfolios_file = os.path.join(MEMORY_DIR, "lotofacil_portfolios.json")

    def create_portfolio(self, name, strategy='balanced', n_numbers=18, max_games=33):
        """Cria um novo portfólio"""
        numbers = self.cercamento.generate_strategic_numbers(strategy, n_numbers)
        result = self.cercamento.generate_cercamento(numbers, max_games)

        portfolio = {
            'name': name,
            'created': datetime.now().isoformat(),
            'strategy': strategy,
            'numbers': numbers,
            'n_numbers': len(numbers),
            'games': result['games'],
            'total_games': len(result['games']),
            'coverage_percent': result['coverage_percent'],
            'cost': len(result['games']) * 3.00,
            'status': 'active'
        }

        self.portfolios[name] = portfolio
        self.save()

        return portfolio

    def save(self):
        """Salva portfólios em arquivo"""
        with open(self.portfolios_file, 'w') as f:
            json.dump({
                'last_update': datetime.now().isoformat(),
                'portfolios': self.portfolios
            }, f, indent=2)

    def get_summary(self, name):
        """Retorna resumo do portfólio"""
        if name not in self.portfolios:
            return "Portfólio não encontrado"

        p = self.portfolios[name]
        games_preview = [f"{' - '.join(f'{n:02d}' for n in g)}" for g in p['games'][:5]]

        return f"""
╔═══════════════════════════════════════════════════════════╗
║  🎯 PORTFÓLIO: {name:<40}║
╠═══════════════════════════════════════════════════════════╣
║  📊 Números escolhidos: {len(p['numbers'])}                              ║
║  📋 Números: {' '.join(f'{n:02d}' for n in p['numbers'][:10])}{'...' if len(p['numbers']) > 10 else '':<16}║
║  🎰 Total de jogos: {p['total_games']}                                ║
║  💰 Custo total: R$ {p['cost']:.2f}                              ║
║  📈 Cobertura: {p['coverage_percent']:.4f}%                           ║
║  🔥 Estratégia: {p['strategy']:<46}║
╠═══════════════════════════════════════════════════════════╣
║  🎯 PRIMEIROS 5 JOGOS:                                      ║
{chr(10).join(f'║     {i+1:02d}. {g}' for i, g in enumerate(games_preview))}
╚═══════════════════════════════════════════════════════════╝
"""


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================
def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║  🧠 SIAOL-PRO LOTOFÁCIL PORTFOLIO GENERATOR                ║
║  Sistema de Cercamento Estratégico                        ║
╚═══════════════════════════════════════════════════════════╝
    """)

    # 1. Carregar e analisar histórico
    print("\n📊 CARREGANDO E ANALISANDO HISTÓRICO...")
    analyzer = LotofacilAnalyzer()

    if not analyzer.draws:
        print("   ❌ Nenhum dado carregado")
        return

    # 2. Gerar cercamento otimizado
    print("\n🎯 GERANDO CERCAMENTO ESTRATÉGICO...")
    cercamento = LotofacilCercamento(analyzer)

    # Gerar portfólio principal com 33 jogos
    portfolio = LotofacilPortfolio(cercamento)

    print("\n   Gerando portfólios com diferentes estratégias...")

    # Portfólio 1: Balanceado (18 números, 33 jogos)
    p1 = portfolio.create_portfolio("Balanceado-18", strategy='balanced', n_numbers=18, max_games=33)
    print(f"\n   ✅ Portfólio 1: {p1['name']}")
    print(f"      Números: {p1['n_numbers']} | Jogos: {p1['total_games']} | Cobertura: {p1['coverage_percent']:.4f}%")

    # Portfólio 2: Quentes (17 números, 33 jogos)
    p2 = portfolio.create_portfolio("Quentes-17", strategy='hot', n_numbers=17, max_games=33)
    print(f"\n   ✅ Portfólio 2: {p2['name']}")
    print(f"      Números: {p2['n_numbers']} | Jogos: {p2['total_games']} | Cobertura: {p2['coverage_percent']:.4f}%")

    # Portfólio 3: Atrasados (17 números, 33 jogos)
    p3 = portfolio.create_portfolio("Atrasados-17", strategy='delayed', n_numbers=17, max_games=33)
    print(f"\n   ✅ Portfólio 3: {p3['name']}")
    print(f"      Números: {p3['n_numbers']} | Jogos: {p3['total_games']} | Cobertura: {p3['coverage_percent']:.4f}%")

    # Portfólio 4: Cercamento Ótimo (busca melhores números)
    print("\n   🔍 Buscando cercamento ótimo...")
    optimal = cercamento.generate_optimal_cercamento(budget_games=33)
    if optimal:
        p4 = portfolio.create_portfolio(
            f"Otimo-{optimal['n_numbers']}",
            strategy=optimal['strategy'],
            n_numbers=optimal['n_numbers'],
            max_games=33
        )
        print(f"\n   ✅ Portfólio 4 (Ótimo): {p4['name']}")
        print(f"      Números: {p4['n_numbers']} | Jogos: {p4['total_games']} | Cobertura: {p4['coverage_percent']:.4f}%")
        print(f"      Score de Qualidade: {optimal.get('quality_score', 0):.2f}")

    # 3. Mostrar resumo dos portfólios
    print("\n" + "=" * 70)
    print("📋 RESUMO DOS PORTFÓLIOS GERADOS")
    print("=" * 70)

    for name in portfolio.portfolios:
        p = portfolio.portfolios[name]
        print(f"\n   📌 {name}:")
        print(f"      Números: {p['numbers']}")
        print(f"      Jogos: {p['total_games']} | Custo: R$ {p['cost']:.2f} | Cobertura: {p['coverage_percent']:.4f}%")

    # 4. Salvar portfólios
    portfolio.save()
    print(f"\n   💾 Portfólios salvos em: {portfolio.portfolios_file}")

    print("\n" + "=" * 70)
    print("✅ CERCAMENTO ESTRATÉGICO GERADO COM SUCESSO!")
    print("=" * 70)

    # 5. Mostrar portfólio principal em detalhe
    if "Balanceado-18" in portfolio.portfolios:
        print(portfolio.get_summary("Balanceado-18"))


if __name__ == "__main__":
    main()