# SIAOL-PRO Quantum System v4.2

## 🤖 Descrição

Sistema de simulação quântica para análise de loterias brasileiras. Implementa um simulador de 20 qubits com probabilidades não-uniformes baseadas em dados históricos.

---

## 🔬 Arquitetura do Sistema

### Componentes Principais

```
SIAOL-PRO/
├── quantum_simulator_20_qubits.py    # Simulador quântico base
├── quantum_v4_optimized.py            # Versão com probabilidades não-uniformes
├── quantum_parameter_executor.py     # Executor de parâmetros
├── unified_quantum_pipeline.py       # Pipeline unificado
├── siaol_smart_scheduler.py         # Agendador inteligente
└── .github/workflows/
    └── quantum-analysis.yml         # GitHub Actions
```

---

## 🧠 Simulador Quântico

### Especificações Técnicas

| Parâmetro | Valor |
|-----------|-------|
| **Qubits** | 20 (padrão), suporta 10, 12, 15 |
| **Estados** | 2^20 = 1,048,576 estados simultâneos |
| **Memória** | ~16 MB (bit-level operations) |
| **Método** | Operações vetoriais (não matrizes densas) |

### Operações Quânticas Implementadas

| Porta | Descrição |
|-------|-----------|
| **H** | Hadamard - cria superposição |
| **X** | Pauli-X (NOT) - flip de bit |
| **Z** | Pauli-Z - flip de fase |
| **CNOT** | Controlled-NOT - emaranhamento |
| **CZ** | Controlled-Z - fase controlada |
| **Ry** | Rotação Y - rotações qubit |
| **Rz** | Rotação Z - mudanças de fase |
| **SWAP** | Troca de qubits |

### Algoritmos Quânticos

1. **QFT (Quantum Fourier Transform)**
   - Detecção de ciclos em sequências
   - Análise espectral

2. **Grover Search**
   - Busca em espaço de 1M estados
   - Amplificação de amplitude

3. **Quantum Walk**
   - Exploração de espaço de busca
   - Estratégia `quantum_walk_biased`

4. **Variational Form**
   - Forma variacional (VQE-like)
   - Estratégia `variational_biased`

---

## 📊 Melhorias v4.x

### Probabilidades Não-Uniformes

**Antes (v3):** Probabilidades uniformes
```python
# Superposição igual para todos os estados
amps = np.ones(dim) / np.sqrt(dim)
```

**Agora (v4):** Bias baseado em hot numbers
```python
# Números frequentes têm maior peso
hot = [n for n, _ in sorted(freq.items(), key=lambda x: -x[1])[:20]]
```

### Integração com Dados Históricos

1. **Análise de Frequência**
   - Extrai números mais sorteados
   - Calcula pesos normalizados

2. **Detecção de Dezenas**
   - Analisa distribuição por dezenas (0-9)
   - Identifica padrões de cobertura

3. **Conversão Otimizada**
   - Bits → Números de aposta
   - Fallback para hot numbers

---

## 🚀 Como Usar

### 1. Execução Local

```bash
cd projeto_loteria

# Quantum Analysis v4 (recomendado)
python3 quantum_v4_optimized.py

# Executor de parâmetros
python3 quantum_parameter_executor.py

# Pipeline unificado
python3 unified_quantum_pipeline.py
```

### 2. GitHub Actions (Automático)

O workflow executa automaticamente a cada 6 horas:

```yaml
# .github/workflows/quantum-analysis.yml
on:
  schedule:
    - cron: '0 */6 * * *'  # A cada 6 horas
  workflow_dispatch:  # Execução manual
```

### 3. Parâmetros Configuráveis

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--n_qubits` | Número de qubits | 15 |
| `--strategy` | Estratégia quântica | all |
| `--n_games` | Jogos a gerar | 33 |

---

## 📈 Estratégias de Geração

### 1. `quantum_walk_biased`
- Quantum Walk com bias para números quentes
- 3-6 passos por execução
- CNOT chain para emaranhamento

### 2. `entanglement_biased`
- Emaranhamento completo
- CZ gates adicionais
- Rotação com bias

### 3. `variational_biased`
- Forma variacional (depth 2-3)
- Rotações + CNOT
- Parametrizações otimizadas

---

## 📊 Resultados

### Estatísticas Geradas

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "hot_numbers": [25, 51, 81, 3, 11, 17, 22, 33, 41, 48],
  "statistics": {
    "total_games": 33,
    "diversity": 0.73,
    "hot_coverage": 0.85
  },
  "games": [...]
}
```

### Métricas

| Métrica | Descrição |
|---------|-----------|
| **Diversity** | % de números únicos nos jogos |
| **Hot Coverage** | % de hot numbers incluídos |
| **Total Games** | Número de jogos gerados |

---

## 🔧 Troubleshooting

### Problema: Timeout na execução

**Solução:** Reduzir número de qubits ou jogos

```python
# Em quantum_v4_optimized.py
n_qubits = 12  # Em vez de 15 ou 20
n_games = 11   # Em vez de 33
```

### Problema: Memória insuficiente

**Solução:** Usar versão otimizada

```bash
# Já usa bit-level operations (~16MB para 20 qubits)
# Se ainda assim falhar, reduzir para 12 qubits
```

### Problema: Resultados uniformes

**Causa:** Poucos dados históricos

**Solução:** Fornecer mais draws de exemplo

```python
# Em quantum_v4_optimized.py
sample_draws = [
    [3, 11, 17, 22, 25, 33, 41, 48, 52, 58, 64, 71, 78, 82, 89],
    # ... adicionar mais draws
]
```

---

## 📁 Estrutura de Arquivos

```
projeto_loteria/
├── output/
│   ├── quantum_v4_20240115_103000.json
│   ├── quantum_parameter_results_20240115_103500.json
│   └── unified_pipeline_20240115_110000.json
├── memory/
│   ├── quantum_v4_latest.json
│   ├── quantum_parameter_latest.json
│   └── unified_pipeline_latest.json
├── quantum_simulator_20_qubits.py
├── quantum_v4_optimized.py
├── quantum_parameter_executor.py
├── unified_quantum_pipeline.py
└── .github/workflows/
    └── quantum-analysis.yml
```

---

## 🎯 Próximos Passos

1. [ ] Integrar com API real da Caixa
2. [ ] Adicionar validação de resultados
3. [ ] Dashboard visual (HTML)
4. [ ] Backtesting de jogos gerados

---

## 📚 Referências

- [Qiskit Documentation](https://qiskit.org/documentation/)
- [Cirq Documentation](https://quantumai.google/cirq)
- [Amazon Braket](https://docs.aws.amazon.com/braket/)

---

## 👨‍💻 Autor

**SIAOL-PRO v4.2** - Sistema de Inteligência Artificial para Loterias

*Implemented with Bit-Level Quantum Simulation*

---

## 📄 Licença

MIT License - See LICENSE file for details