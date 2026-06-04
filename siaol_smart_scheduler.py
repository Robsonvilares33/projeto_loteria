#!/usr/bin/env python3
"""
SIAOL-PRO SMART SCHEDULER v3.0 - APRENDIZADO INTELIGENTE
=========================================================
Sistema que:
1. Detecta SE HÁ NOVOS SORTEIOS para aprender
2. Sincroniza apenas quando necessário
3. Executa backtesting apenas quando há novos dados
4. Otimiza recursos computacionais

FLUXO DE APRENDIZADO:
- Verifica novos resultados da API
- Se há novos dados → Sincroniza → Aprende → Atualiza pesos
- Se não há novos dados → Modo espera (não faz nada pesado)
"""

import os, json, time, datetime
from datetime import datetime as dt
import requests

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(PROJECT_DIR, "memory")
DATA_DIR = os.path.join(PROJECT_DIR, "data")
os.makedirs(MEMORY_DIR, exist_ok=True)

# Configuração de dias de sorteio
DRAW_SCHEDULE = {
    0: ['lotofacil', 'quina'],           # Segunda
    1: ['lotofacil', 'quina'],           # Terça
    2: ['lotofacil', 'megasena', 'quina', 'lotomania'],  # Quarta
    3: ['lotofacil', 'quina'],           # Quinta
    4: ['lotofacil', 'quina'],           # Sexta
    5: ['lotofacil', 'megasena', 'quina', 'lotomania'],  # Sábado
    6: []                                  # Domingo
}

# Arquivo de controle de aprendizado
STATE_FILE = os.path.join(MEMORY_DIR, "smart_learning_state.json")


class SmartLearningScheduler:
    """Escalonador que só aprende quando há novos dados"""

    def __init__(self):
        self.state = self.load_state()
        self.now = dt.now()
        self.weekday = self.now.weekday()
        self.hour = self.now.hour

    def load_state(self):
        """Carrega estado do aprendizado"""
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE) as f:
                    return json.load(f)
            except:
                pass
        return {
            'last_sync': None,
            'last_concursos': {},
            'learning_history': []
        }

    def save_state(self):
        """Salva estado do aprendizado"""
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)

    def check_api_for_new_draws(self, lottery):
        """Checa API da Caixa para novos sorteios"""
        lottery_codes = {
            'lotofacil': 'lf',
            'megasena': 'ms',
            'quina': 'gn',
            'lotomania': 'lm'
        }

        code = lottery_codes.get(lottery, lottery)

        try:
            url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena"
            if lottery == 'lotofacil':
                url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil"
            elif lottery == 'quina':
                url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/quina"
            elif lottery == 'lotomania':
                url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotomania"

            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                latest = data.get('numero', 0)
                return latest
        except:
            pass

        # Fallback: checar último concurso known
        return self.state.get('last_concursos', {}).get(lottery, 0)

    def has_new_data(self, lottery):
        """Verifica se há novos dados para a lottery"""
        current_concurso = self.check_api_for_new_draws(lottery)
        last_known = self.state.get('last_concursos', {}).get(lottery, 0)

        return current_concurso > last_known

    def run_full_learning_cycle(self, lottery):
        """Executa ciclo completo de aprendizado para uma lottery"""
        print(f"\n   🧠 Aprendendo {lottery}...")

        try:
            # 1. Sincronizar dados
            print(f"      📥 Sincronizando resultados...")
            os.system(f"cd {PROJECT_DIR} && python3 siaol_complete_database.py --sync > /dev/null 2>&1")

            # 2. Obter novo concurso
            current = self.check_api_for_new_draws(lottery)
            if current > self.state.get('last_concursos', {}).get(lottery, 0):
                print(f"      ✅ Novo concurso detectado: {current}")

                # 3. Executar backtesting e atualizar pesos
                print(f"      📊 Atualizando pesos e estratégia...")
                os.system(f"cd {PROJECT_DIR} && python3 siaol_multi_portfolio.py > /dev/null 2>&1")

                # 4. Marcar como aprendido
                if 'last_concursos' not in self.state:
                    self.state['last_concursos'] = {}
                self.state['last_concursos'][lottery] = current

                # 5. Registrar no histórico
                self.state['learning_history'].append({
                    'timestamp': dt.now().isoformat(),
                    'lottery': lottery,
                    'concurso': current,
                    'action': 'learned'
                })
                self.state['learning_history'] = self.state['learning_history'][-50:]

                print(f"      ✅ Aprendizado completo!")
                return True
            else:
                print(f"      💤 Sem novos dados - nada a aprender")
                return False

        except Exception as e:
            print(f"      ❌ Erro: {e}")
            return False

    def run_idle_mode(self):
        """Modo espera - não faz nada pesado"""
        print(f"\n   💤 Modo espera ativo")
        print(f"      Próximo sorteio: {self.get_next_draw_info()}")
        print(f"      Executará aprendizado quando novo resultado estiver disponível")

    def get_next_draw_info(self):
        """Retorna info do próximo sorteio"""
        for i in range(1, 8):
            next_day = (self.weekday + i) % 7
            if DRAW_SCHEDULE.get(next_day):
                next_date = self.now + datetime.timedelta(days=i)
                days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
                lotteries = ', '.join(DRAW_SCHEDULE[next_day])
                return f"{days[next_day]} ({next_date.strftime('%d/%m')}) - {lotteries}"
        return "N/A"

    def determine_action(self):
        """Determina o que fazer"""
        # Verificar loterias do dia
        today_lotteries = DRAW_SCHEDULE.get(self.weekday, [])

        if not today_lotteries:
            return "idle", []

        # Verificar se há novos dados
        new_data_available = []
        for lottery in today_lotteries:
            if self.has_new_data(lottery):
                new_data_available.append(lottery)

        if new_data_available:
            return "learn", new_data_available

        # Se é horário de pós-sorteio (21h-22h) e ainda não sincronizou hoje
        if 21 <= self.hour < 23:
            return "sync_check", today_lotteries

        return "idle", []


def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║  🧠 SIAOL-PRO SMART SCHEDULER v3.0                        ║
║  Aprendizado Inteligente - Só aprende quando há novos dados║
╚═══════════════════════════════════════════════════════════╝
    """)

    scheduler = SmartLearningScheduler()

    # Mostrar status
    print(f"\n📅 Hoje: {scheduler.now.strftime('%A, %d/%m/%Y')}")
    print(f"🕐 Horário: {scheduler.now.strftime('%H:%M')}")

    today_lotteries = DRAW_SCHEDULE.get(scheduler.weekday, [])
    if today_lotteries:
        print(f"🎰 Loterias hoje: {', '.join(today_lotteries)}")
    else:
        print(f"🎰 Hoje não há sorteios")

    # Determinar ação
    action, lotteries = scheduler.determine_action()

    print(f"\n🔍 Verificando necessidade de aprendizado...")

    if action == "learn":
        print(f"\n🚀 EXECUTANDO CICLO DE APRENDIZADO")
        print(f"   Loterias com novos dados: {', '.join(lotteries)}")

        learned_count = 0
        for lottery in lotteries:
            if scheduler.run_full_learning_cycle(lottery):
                learned_count += 1

        print(f"\n   ✅ Aprendizado concluído: {learned_count}/{len(lotteries)}")

    elif action == "sync_check":
        print(f"\n🔄 Verificando sincronização...")
        # Forçar sync uma vez
        for lottery in lotteries:
            if scheduler.has_new_data(lottery):
                scheduler.run_full_learning_cycle(lottery)
                break
        else:
            scheduler.run_idle_mode()

    else:
        scheduler.run_idle_mode()

    # Salvar estado
    scheduler.save_state()
    scheduler.state['last_sync'] = scheduler.now.isoformat()

    print("\n" + "="*60)
    print("✅ Ciclo inteligente concluído")
    print(f"   Próximo aprendizado: Quando houver novos resultados")
    print("="*60)

    return 0


if __name__ == "__main__":
    exit(main())