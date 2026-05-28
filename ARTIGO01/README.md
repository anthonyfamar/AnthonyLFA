# 🏠 Sistema Inteligente de Monitoramento Residencial com Arduino e ARM

> Projeto desenvolvido para a disciplina de Arquitetura de Computadores — 5º Semestre de Ciência da Computação  
> **Autor:** Anthony Famar Gomes

---

## 📌 Descrição

Este projeto consiste no desenvolvimento de um **sistema embarcado inteligente de monitoramento residencial**, utilizando Arduino, arquitetura ARM e conceitos introdutórios de Inteligência Artificial. O sistema realiza leitura de sensores (temperatura, presença, luminosidade e gás), processa as informações, toma decisões automatizadas e exibe os dados em uma interface serial.

A simulação do fluxo ARM e toda a lógica de processamento foram implementadas em **Python**, tornando o projeto portátil e de fácil reprodução.

---

## 🎯 Objetivos

- Compreender a arquitetura de microcontroladores Arduino
- Desenvolver algoritmos embarcados em Python (equivalente a C)
- Aplicar conceitos de arquitetura ARM (pipeline, registradores, fetch-decode-execute)
- Integrar sensores e atuadores ao Arduino (simulado via Python)
- Implementar lógica de decisão automatizada com IA básica
- Publicar o projeto completo no GitHub

---

## 🗂️ Estrutura do Repositório

```
📦 monitoramento-residencial/
├── 📄 README.md
├── 📁 src/
│   ├── 🐍 simulador_arduino.py        # Simulação dos sensores e lógica embarcada
│   ├── 🐍 simulador_arm.py            # Simulação do pipeline ARM (fetch-decode-execute)
│   ├── 🐍 ia_decisao.py               # Módulo de Inteligência Artificial (regras + ML básico)
│   └── 🐍 monitor_serial.py           # Interface de monitoramento serial
├── 📁 docs/
│   └── 📄 documentacao.pdf            # Documentação completa do projeto
├── 📁 imagens/
│   └── 📷 diagrama_sistema.png        # Diagrama do sistema
└── 📁 testes/
    └── 🐍 test_sensores.py            # Testes unitários
```

---

## ⚙️ Tecnologias Utilizadas

| Tecnologia | Finalidade |
|---|---|
| Python 3.x | Linguagem principal (simulação embarcada) |
| Arduino (conceitual) | Plataforma de hardware alvo |
| Arquitetura ARM | Base teórica e simulação de pipeline |
| Scikit-learn | IA básica para detecção de anomalias |
| Matplotlib | Visualização dos dados dos sensores |
| ReportLab | Geração de documentação em PDF |

---

## 🚀 Como Executar

### Pré-requisitos

```bash
pip install matplotlib scikit-learn numpy
```

### Execução

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/monitoramento-residencial.git
cd monitoramento-residencial

# Executar o simulador principal
python src/simulador_arduino.py

# Executar a simulação ARM
python src/simulador_arm.py

# Executar a interface de monitoramento
python src/monitor_serial.py
```

---

## 🔌 Sensores Simulados

| Sensor | Variável Monitorada | Limiar de Alerta |
|---|---|---|
| DHT22 | Temperatura e Umidade | Temp > 35°C |
| PIR | Presença / Movimento | Detecção = ALERTA |
| MQ-2 | Gás / Fumaça | > 300 ppm |
| LDR | Luminosidade | < 200 lux (noite) |

---

## 🧠 Inteligência Artificial

O módulo de IA utiliza um classificador baseado em **regras lógicas** combinado com um modelo de **Isolation Forest** (scikit-learn) para detecção de anomalias nos dados dos sensores. O sistema aprende padrões normais e identifica situações de risco automaticamente.

---

## 🖥️ Simulação ARM

O arquivo `simulador_arm.py` demonstra o ciclo clássico de um processador ARM:

1. **Fetch** — Busca a instrução na memória
2. **Decode** — Decodifica o opcode e os operandos
3. **Execute** — Executa a operação (ADD, MOV, CMP, B, LDR, STR)
4. **Write Back** — Escreve o resultado no banco de registradores

---

## 📊 Resultados Esperados

- Sistema funcional com leitura contínua de sensores
- Alertas automáticos em caso de anomalia
- Visualização gráfica dos dados em tempo real
- Demonstração do pipeline ARM com rastreamento de registradores
- Documentação técnica completa em PDF

---

## 👨‍💻 Autor

**Anthony Famar Gomes**  
5º Semestre — Ciência da Computação  

---

## 📄 Licença

Este projeto é de uso acadêmico. Todos os direitos reservados ao autor.
