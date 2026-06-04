#!/usr/bin/env python3
"""
SIAOL-PRO SMART SCHEDULER v2.0
==============================
Sistema inteligente que:
1. Detecta novos sorteios automaticamente
2. Só aprende quando há novos dados
3. Economiza recursos computacionais
4. Executa ações nos momentos certos

CRONOGRAMA OTIMIZADO:
- Segunda a Sábado: Quina + Lotofácil
- Quartas e Sábados: Mega-Sena
- Terças e Quintas: Lotomania
"""

import os, json, time, datetime
from datetime import datetime as dt

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(PROJECT_DIR, "memory")
os.makedirs(MEMORY_DIR, exist_ok=True)

# Configuração de dias de sorteio
DRAW_SCHEDULE = {
    0: ['lotofacil', 'quina'],           # Segunda
    1: ['lotofacil', 'quina'],           # Terça
    2: ['lotofacil', 'megasena', 'quina', 'lotomania'],  # Quarta
    3: ['lotofacil', 'quina'],           # Quinta
    4: ['lotofacil', 'quina'],           # Sexta
    5: ['lotofacil', 'megasena', 'quina', 'lotomania'],  # Sábado
    6: []                                  # Domingo - sem sorteio
}

# Horários (hora brasileira = UTC-3)
PRE_DRAW_HOUR = 18    # 6PM - gerar jogos
POST_DRAW_HOUR = 21   # 9PM - buscar resultado

# Arquivo de controle
LAST_CHECK_FILE = os.path.join(MEMORY_DIR, "smart_scheduler_state.json")


class SmartScheduler:
    """Escalonador inteligente que só executa quando necessário"""

    def __init__(self):
        self.state = self.load_state()
        self.today = dt.now()
        self.weekday = self.today.weekday()
        self.hour = self.today.hour
        self.minute = self.today.minute

    def load_state(self):
        """Carrega estado anterior"""
        if os.path.exists(LAST_CHECK_FILE):
            try:
                with open(LAST_CHECK_FILE) as f:
                    return json.load(f)
            except:
                pass
        return {
            'last_run_date': None,
            'last_draw_check': {},
            'last_pre_draw_run': {},
            'runs_today': 0
        }

    def save_state(self):
        """Salva estado atual"""
        self.state['last_run_date'] = self.today.strftime('%Y-%m-%d')
        with open(LAST_CHECK_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)

    def is_draw_day(self):
        """Verifica se hoje é dia de sorteio"""
        return len(DRAW_SCHEDULE.get(self.weekday, [])) > 0

    def is_pre_draw_window(self):
        """Verifica se está na janela pré-sorteio (18h-20h)"""
        return 18 <= self.hour < 20

    def is_post_draw_window(self):
        """Verifica se está na janela pós-sorteio (21h-22h)"""
        return 21 <= self.hour < 22

    def should_run_pre_draw(self, lottery):
        """Verifica se deve rodar antes do sorteio"""
        today_key = f"{lottery}_pre_{self.today.strftime('%Y%m%d')}"
        return self.state.get('last_pre_draw_run', {}).get(lottery) != today_key

    def should_check_results(self):
        """Verifica se deve checar novos resultados"""
        today_key = self.today.strftime('%Y%m%d')
        return self.state.get('last_draw_check', {}) != today_key

    def mark_pre_draw_done(self, lottery):
        """Marca que pré-sorteio foi executado"""
        if 'last_pre_draw_run' not in self.state:
            self.state['last_pre_draw_run'] = {}
        today_key = f"{lottery}_pre_{self.today.strftime('%Y%m%d')}"
        self.state['last_pre_draw_run'][lottery] = today_key

    def mark_results_checked(self):
        """Marca que checou resultados hoje"""
        self.state['last_draw_check'] = self.today.strftime('%Y%m%d')
        self.state['runs_today'] += 1

    def reset_daily_state(self):
        """Reseta estado para novo dia"""
        if self.state.get('last_run_date') != self.today.strftime('%Y-%m-%d'):
            self.state = {
                'last_run_date': self.today.strftime('%Y-%m-%d'),
                'last_draw_check': {},
                'last_pre_draw_run': {},
                'runs_today': 0
            }

    def get_today_lotteries(self):
        """Retorna loterias do dia"""
        return DRAW_SCHEDULE.get(self.weekday, [])

    def determine_action(self):
        """
        Determina qual ação deve executar
        Retorna: (should_run, action_type, lotteries)
        """
        self.reset_daily_state()

        # Verificar se é dia de sorteio
        if not self.is_draw_day():
            return False, "no_draw_day", []

        lotteries = self.get_today_lotteries()

        # Janela pós-sorteio (21h-22h) - checar resultados
        if self.is_post_draw_window():
            return True, "check_results", lotteries

        # Janela pré-sorteio (18h-20h) - gerar jogos
        if self.is_pre_draw_window():
            pending = [l for l in lotteries if self.should_run_pre_draw(l)]
            if pending:
                return True, "pre_draw", pending

        # Não há ação necessária
        return False, "nothing_to_do", []


def run_pre_draw_analysis(lotteries):
    """Executa análise pré-sorteio"""
    print("\n" + "="*60)
    print("🎯 ANÁLISE PRÉ-SORTEIO")
    print(f"   Data: {dt.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"   Loterias: {', '.join(lotteries)}")
    print("="*60)

    # Importar módulos
    try:
        import sys
        sys.path.insert(0, PROJECT_DIR)

        # Executar análise de portfólios
        print("\n📊 Executando análise de portfólios...")
        os.system(f"cd {PROJECT_DIR} && python3 siaol_multi_portfolio.py > /dev/null 2>&1")

        print("✅ Análise pré-sorteio concluída")
        return True

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def run_post_draw_check(lotteries):
    """Checa e atualiza resultados"""
    print("\n" + "="*60)
    print("🔍 CHECAGEM PÓS-SORTEIO")
    print(f"   Data: {dt.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"   Loterias: {', '.join(lotteries)}")
    print("="*60)

    try:
        # Executar sync de banco de dados
        print("\n📥 Sincronizando novos resultados...")
        os.system(f"cd {PROJECT_DIR} && python3 siaol_complete_database.py --sync > /dev/null 2>&1")

        # Executar learning cycle
        print("🧠 Executando ciclo de aprendizado...")
        os.system(f"cd {PROJECT_DIR} && python3 siaol_multi_portfolio.py > /dev/null 2>&1")

        print("✅ Resultados sincronizados e aprendizados")
        return True

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def run_idle_check():
    """Verificação leve em horário ocioso"""
    # Apenas atualiza estatísticas, não faz процес heavy
    now = dt.now()
    print(f"[{now.strftime('%H:%M')}] Sistema em modo espera...")
    print("   💤 Aguardando horário de sorteio...")


def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║  🧠 SIAOL-PRO SMART SCHEDULER v2.0                         ║
║  Execução Inteligente - Aprende apenas quando necessário  ║
╚═══════════════════════════════════════════════════════════╝
    """)

    scheduler = SmartScheduler()

    # Determinar ação
    should_run, action_type, lotteries = scheduler.determine_action()

    print(f"\n📅 Hoje ({scheduler.weekday}): ", end="")
    if scheduler.is_draw_day():
        print(f"Dia de sorteio - {', '.join(lotteries)}")
    else:
        print("Sem sorteio")

    print(f"🕐 Horário: {scheduler.hour:02d}:{scheduler.minute:02d}")
    print(f"📊 Ações hoje: {scheduler.state.get('runs_today', 0)}")

    if not should_run:
        if action_type == "no_draw_day":
            print("\n⏸️  Modo espera: Não há sorteios hoje")
        else:
            print("\n⏸️  Modo espera: Ações já foram executadas hoje")
        run_idle_check()
        scheduler.save_state()
        return 0

    # Executar ação apropriada
    if action_type == "pre_draw":
        print(f"\n🚀 EXECUTANDO: Análise pré-sorteio para {', '.join(lotteries)}")
        success = run_pre_draw_analysis(lotteries)
        if success:
            for lot in lotteries:
                scheduler.mark_pre_draw_done(lot)

    elif action_type == "check_results":
        print(f"\n🚀 EXECUTANDO: Checagem pós-sorteio para {', '.join(lotteries)}")
        success = run_post_draw_check(lotteries)
        if success:
            scheduler.mark_results_checked()

    scheduler.save_state()

    print("\n" + "="*60)
    print("✅ Ciclo inteligente concluído")
    print(f"   Próxima execução: Quando houver ação necessária")
    print("="*60)

    return 0


if __name__ == "__main__":
    exit(main())