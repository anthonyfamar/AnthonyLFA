"""
simulador_arduino.py
Sistema Inteligente de Monitoramento Residencial
Autor: Anthony Famar Gomes — 5° Semestre Ciência da Computação

Simula a leitura de sensores e a lógica embarcada do Arduino em Python.
"""

import random
import time
import math
from datetime import datetime


# ─────────────────────────────────────────────
#  Constantes (equivalente a #define no C/C++)
# ─────────────────────────────────────────────
TEMP_MAX        = 45.0   # °C — limiar de temperatura alta
UMIDADE_MIN     = 20.0   # %  — limiar de umidade baixa
GAS_MAX         = 300    # ppm — limiar de gás perigoso
LUZ_NOITE       = 200    # lux — abaixo disso acende luz automática
INTERVALO_MS    = 1000   # ms entre leituras


# ─────────────────────────────────────────────
#  Classes de Sensor (equivale a structs em C)
# ─────────────────────────────────────────────

class SensorDHT22:
    """Simula o sensor de temperatura e umidade DHT22."""

    def __init__(self, pino: int = 2):
        self.pino = pino
        self._temp_base = 25.0
        self._umidade_base = 60.0

    def ler(self) -> dict:
        """Retorna temperatura (°C) e umidade (%) simulados com ruído."""
        temperatura = round(self._temp_base + random.uniform(-3, 8), 1)
        umidade     = round(self._umidade_base + random.uniform(-10, 10), 1)
        umidade     = max(0.0, min(100.0, umidade))
        return {"temperatura": temperatura, "umidade": umidade}


class SensorPIR:
    """Simula o sensor de presença PIR."""

    def __init__(self, pino: int = 3):
        self.pino = pino

    def ler(self) -> dict:
        """Retorna True se detectar presença (20% de chance a cada leitura)."""
        presenca = random.random() < 0.20
        return {"presenca": presenca}


class SensorMQ2:
    """Simula o sensor de gás/fumaça MQ-2."""

    def __init__(self, pino: int = "A0"):
        self.pino = pino
        self._base = 50  # ppm normal

    def ler(self) -> dict:
        """Retorna concentração de gás em ppm."""
        ppm = round(self._base + random.uniform(0, 400))
        return {"gas_ppm": ppm}


class SensorLDR:
    """Simula o sensor de luminosidade LDR."""

    def __init__(self, pino: int = "A1"):
        self.pino = pino
        self._hora = datetime.now().hour

    def ler(self) -> dict:
        """Retorna luminosidade em lux baseada na hora do dia."""
        hora = datetime.now().hour
        # Simula ciclo dia/noite
        lux_base = 500 * max(0, math.sin(math.pi * (hora - 6) / 12))
        lux = round(lux_base + random.uniform(-50, 50))
        lux = max(0, lux)
        return {"luminosidade_lux": lux}


# ─────────────────────────────────────────────
#  Atuadores
# ─────────────────────────────────────────────

class Atuador:
    """Representa um atuador genérico (LED, buzzer, relé)."""

    def __init__(self, nome: str, pino: int):
        self.nome  = nome
        self.pino  = pino
        self.estado = False

    def ligar(self):
        self.estado = True
        print(f"  [ATUADOR] {self.nome} (pino {self.pino}) → LIGADO")

    def desligar(self):
        self.estado = False
        print(f"  [ATUADOR] {self.nome} (pino {self.pino}) → DESLIGADO")


# ─────────────────────────────────────────────
#  Lógica de Decisão Automatizada
# ─────────────────────────────────────────────

def processar_decisao(dados: dict, atuadores: dict) -> list:
    """
    Analisa os dados dos sensores e aciona os atuadores conforme necessário.
    Equivale ao loop() principal do Arduino com estruturas if/else em C.

    Retorna lista de alertas gerados.
    """
    alertas = []

    # --- Temperatura alta ---
    if dados["temperatura"] > TEMP_MAX:
        alertas.append(f"ALERTA: Temperatura alta ({dados['temperatura']}°C)")
        atuadores["buzzer"].ligar()
        atuadores["ventilador"].ligar()
    else:
        atuadores["buzzer"].desligar()
        atuadores["ventilador"].desligar()

    # --- Umidade baixa ---
    if dados["umidade"] < UMIDADE_MIN:
        alertas.append(f"AVISO: Umidade muito baixa ({dados['umidade']}%)")

    # --- Detecção de presença ---
    if dados["presenca"]:
        alertas.append("ALERTA: Presença detectada!")
        atuadores["led_alarme"].ligar()
    else:
        atuadores["led_alarme"].desligar()

    # --- Gás perigoso ---
    if dados["gas_ppm"] > GAS_MAX:
        alertas.append(f"PERIGO: Gás detectado ({dados['gas_ppm']} ppm)!")
        atuadores["buzzer"].ligar()
        atuadores["exaustor"].ligar()
    else:
        if not dados["temperatura"] > TEMP_MAX:
            atuadores["buzzer"].desligar()
        atuadores["exaustor"].desligar()

    # --- Controle de luz automático ---
    if dados["luminosidade_lux"] < LUZ_NOITE:
        atuadores["led_luz"].ligar()
    else:
        atuadores["led_luz"].desligar()

    return alertas


# ─────────────────────────────────────────────
#  Interface Serial (print para console)
# ─────────────────────────────────────────────

def interface_serial(dados: dict, alertas: list, ciclo: int):
    """Exibe os dados dos sensores no terminal — simula Serial.print() do Arduino."""
    linha = "─" * 55
    print(f"\n{linha}")
    print(f"  📡 MONITORAMENTO RESIDENCIAL — Ciclo #{ciclo:04d}")
    print(f"  🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(linha)
    print(f"  🌡  Temperatura  : {dados['temperatura']:>6.1f} °C")
    print(f"  💧 Umidade      : {dados['umidade']:>6.1f} %")
    print(f"  👁  Presença     : {'SIM ⚠' if dados['presenca'] else 'NÃO  '}")
    print(f"  🔥 Gás (MQ-2)   : {dados['gas_ppm']:>6d} ppm")
    print(f"  💡 Luminosidade : {dados['luminosidade_lux']:>6d} lux")
    print(linha)
    if alertas:
        for alerta in alertas:
            print(f"  ⚠  {alerta}")
    else:
        print("  ✅ Todos os parâmetros normais.")
    print(linha)


# ─────────────────────────────────────────────
#  Setup e Loop (equivale ao Arduino)
# ─────────────────────────────────────────────

def setup():
    """Inicializa sensores e atuadores — equivale ao setup() do Arduino."""
    print("=" * 55)
    print("  SISTEMA DE MONITORAMENTO RESIDENCIAL")
    print("  Autor: Anthony Famar Gomes")
    print("  Inicializando componentes...")
    print("=" * 55)

    sensores = {
        "dht22"   : SensorDHT22(pino=2),
        "pir"     : SensorPIR(pino=3),
        "mq2"     : SensorMQ2(pino="A0"),
        "ldr"     : SensorLDR(pino="A1"),
    }

    atuadores = {
        "buzzer"     : Atuador("Buzzer",        pino=8),
        "led_alarme" : Atuador("LED Alarme",    pino=9),
        "led_luz"    : Atuador("LED Luz",       pino=10),
        "ventilador" : Atuador("Ventilador",    pino=11),
        "exaustor"   : Atuador("Exaustor",      pino=12),
    }

    print("  ✅ Setup concluído. Iniciando monitoramento...\n")
    return sensores, atuadores


def loop(sensores: dict, atuadores: dict, ciclos: int = 10):
    """
    Loop principal de monitoramento — equivale ao loop() do Arduino.
    Executa `ciclos` iterações com intervalo de INTERVALO_MS ms.
    """
    for ciclo in range(1, ciclos + 1):
        # Leitura de todos os sensores
        dados = {}
        dados.update(sensores["dht22"].ler())
        dados.update(sensores["pir"].ler())
        dados.update(sensores["mq2"].ler())
        dados.update(sensores["ldr"].ler())

        # Processamento e tomada de decisão
        alertas = processar_decisao(dados, atuadores)

        # Exibição na interface serial
        interface_serial(dados, alertas, ciclo)

        # Aguarda próximo ciclo
        time.sleep(INTERVALO_MS / 1000)


# ─────────────────────────────────────────────
#  Ponto de entrada
# ─────────────────────────────────────────────

if __name__ == "__main__":
    sensores, atuadores = setup()
    loop(sensores, atuadores, ciclos=5)
    print("\n  Sistema encerrado.")
