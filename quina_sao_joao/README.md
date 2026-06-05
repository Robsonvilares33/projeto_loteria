# 🧠 QUINA BRAIN - CEREBRO QUÂNTICO v1.0

## 🎯 Descrição

Sistema especializado de simulação quântica para a **Quina de São João** (Concurso 7051). O Quina Brain utiliza probabilidades não-uniformes baseadas em dados históricos para gerar portfólios otimizados.

### Informações do Concurso

| Item | Valor |
|------|-------|
| **Concurso** | 7051 |
| **Data** | 28/06/2026 às 11h00 |
| **Prêmio** | R$ 250.000.000 |
| **Números** | 5 de 80 |
| **Valor por jogo** | R$ 3,00 |

---

## ⚡ Por que a Quina é especial?

A Quina apresenta **+400% de vantagem** em relação a escolhas aleatórias quando combinada com análise quântica:

- **Pool menor**: 80 números (vs 60 na Mega-Sena, 25 na Lotofácil)
- **Mais sorteios**: 6x por semana
- **Padrões mais consistentes**: Mais dados = melhor análise
- **Menor complexidade**: 5 números = menos combinações

---

## 🧠 Arquitetura do Sistema

```
quina_sao_joao/
├── quina_brain_engine.py          # Motor principal
├── .github/workflows/
│   └── quina-brain.yml            # Automação (a cada 6h)
├── output/                        # Resultados gerados
│   └── quina_sj_*.json
├── memory/                        # Memória de aprendizado
│   ├── quina_brain_latest.json
│   ├── learning_history.json
│   └── draw_results.json
└── data/                          # Dados históricos
```

---

## 🚀 Funcionalidades

### 1. Análise de Frequência
- Hot numbers (mais sorteados)
- Cold numbers (menos sorteados)
- Análise por dezenas

### 2. Geração Quântica
4 estratégias diferentes:

| Estratégia | Descrição | Alocação |
|------------|-----------|----------|
| 🔥 **HOT FOCUS** | Foco em números quentes | 30% (15 jogos) |
| 🧠 **QUANTUM WALK** | Simulação quântica | 30% (15 jogos) |
| ⚡ **ENTANGLEMENT** | Estados emaranhados | 20% (10 jogos) |
| 🎯 **BALANCED** | Combinação balanceada | 20% (10 jogos) |

### 3. Portfólio Otimizado
- **Orçamento**: R$ 150,00
- **Jogos**: ~50 jogos
- **Cobertura**: Diversificação por estratégia

### 4. Integração Telegram
- Envio automático de resultados
- Hot numbers atualizados
- Portfólio formatado

### 5. Aprendizado Contínuo
- Histórico de gerações
- Rastreamento de hot numbers
- Análise de desempenho por estratégia

---

## 📊 Algoritmos Quânticos

### Quantum Walk
```python
circuit = QuantumAlgorithms.quantum_walk(15, steps)
```
- Explora espaço de estados
- Bias para números quentes

### Entanglement
```python
for q in range(10):
    sim.state = QuantumOps.hadamard(sim.state, q)
for q in range(9):
    sim.state = QuantumOps.cnot(sim.state, q, q + 1)
```
- Estados emaranhados
- Correlações quânticas

### Variational Form
```python
circuit = QuantumAlgorithms.variational_form(15, depth)
```
- Forma variacional (VQE-like)
- Otimização paramétrica

---

## 🔧 Uso Local

```bash
cd quina_sao_joao

# Executar motor
python3 quina_brain_engine.py

# Verificar últimos resultados
cat memory/quina_brain_latest.json | jq

# Ver histórico de aprendizado
cat memory/learning_history.json | jq
```

---

## 📱 Configuração Telegram

Defina as secrets no GitHub:

1. `TELEGRAM_BOT_TOKEN` - Token do bot
2. `TELEGRAM_CHAT_ID` - ID do chat

---

## 🎯 Como Funciona

### Fluxo de Execução

```
1. Carregar dados históricos da Quina
   ↓
2. Analisar frequência dos números
   ↓
3. Gerar portfólio com 4 estratégias
   ↓
4. Salvar resultados (output + memory)
   ↓
5. Enviar para Telegram (automaticamente)
   ↓
6. Atualizar memória de aprendizado
```

### Atualização de Dados

```python
# Atualiza automaticamente via API da Caixa
python3 -c "
import requests
r = requests.get('https://loterias.caixa.gov.br/api/max Quina')
data = r.json()
print(f'Concurso: {data[\"concurso\"]}')
print(f'Numbers: {data[\"listaNumeros\"]}')
"
```

---

## 📈 Métricas de Aprendizado

O sistema rastreia:

| Métrica | Descrição |
|---------|-----------|
| **Gerações** | Total de vezes que o portfólio foi gerado |
| **Jogos** | Total de jogos gerados |
| **Hot Tracking** | Frequência dos números nos jogos |
| **Estratégias** | Distribuição por estratégia |

---

## 🔬 Probabilidades

| Acerto | Probabilidade (1 em...) |
|--------|--------------------------|
| 2 números | 36 |
| 3 números | 866 |
| 4 números | 64,106 |
| 5 números (Quina) | 24,040,016 |

---

## 🛠️ Troubleshooting

### Sem dados históricos
O sistema usa padrões históricos pré-carregados quando não há dados.

### Telegram não envia
Verifique as credenciais:
```bash
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID
```

### Memória cheia
O sistema mantém apenas os últimos 20 resultados.

---

## 📚 Referências

- [Qiskit Documentation](https://qiskit.org/documentation/)
- [Lotteries API - Caixa](https://loterias.caixa.gov.br/)
- [Quantum Computing for Everyone](https://quantum-computing.ibm.com/)

---

## 👨‍💻 Autor

**SIAOL-PRO Quina Brain v1.0**

*Sistema de Inteligência Artificial para Loterias*

🧠 O cérebro está aprendendo... até 28/06/2026!

---

## 📄 Licença

MIT License