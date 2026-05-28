"""
monitor_serial.py
Interface de Monitoramento Serial — Dashboard em Terminal
Autor: Anthony Famar Gomes — 5° Semestre Ciência da Computação

Integra o simulador Arduino + IA e exibe um dashboard completo no terminal.
"""

import sys
import time
import random
from datetime import datetime

# Importa os módulos do projeto
try:
    from simulador_arduino import (
        SensorDHT22, SensorPIR, SensorMQ2, SensorLDR,
        Atuador, processar_decisao, TEMP_MAX, GAS_MAX, LUZ_NOITE
    )
    from ia_decisao import MotorIA, NivelRisco
    MODULOS_OK = True
except ImportError:
    MODULOS_OK = False


# ─────────────────────────────────────────────
#  Cores para terminal (ANSI)
# ─────────────────────────────────────────────

class Cor:
    VERDE   = "\033[92m"
    AMARELO = "\033[93m"
    VERMELHO= "\033[91m"
    AZUL    = "\033[94m"
    CIANO   = "\033[96m"
    RESET   = "\033[0m"
    NEGRITO = "\033[1m"


def colorir(texto: str, cor: str) -> str:
    return f"{cor}{texto}{Cor.RESET}"


def cor_para_risco(nivel: str) -> str:
    mapa = {
        NivelRisco.NORMAL  : Cor.VERDE,
        NivelRisco.BAIXO   : Cor.CIANO,
        NivelRisco.MEDIO   : Cor.AMARELO,
        NivelRisco.ALTO    : Cor.VERMELHO,
        NivelRisco.CRITICO : Cor.VERMELHO,
    }
    return mapa.get(nivel, Cor.RESET)


# ─────────────────────────────────────────────
#  Dashboard
# ─────────────────────────────────────────────

def desenhar_barra(valor: float, minv: float, maxv: float, largura: int = 20) -> str:
    """Gera uma barra de progresso ASCII."""
    proporcao = max(0.0, min(1.0, (valor - minv) / (maxv - minv)))
    preenchido = int(proporcao * largura)
    barra = "█" * preenchido + "░" * (largura - preenchido)
    return f"[{barra}]"


def exibir_dashboard(dados: dict, relatorio_ia: dict, ciclo: int, atuadores: dict):
    """Exibe o dashboard completo no terminal."""
    nivel = relatorio_ia["nivel_risco"]
    cor   = cor_para_risco(nivel)

    print(f"\n{Cor.NEGRITO}{'═'*62}{Cor.RESET}")
    print(f"{Cor.NEGRITO}  🏠 MONITOR RESIDENCIAL INTELIGENTE   Ciclo #{ciclo:04d}{Cor.RESET}")
    print(f"  {Cor.CIANO}{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Cor.RESET}")
    print(f"{'─'*62}")

    # Sensores
    temp  = dados["temperatura"]
    umid  = dados["umidade"]
    gas   = dados["gas_ppm"]
    lux   = dados["luminosidade_lux"]
    pres  = dados["presenca"]

    cor_temp = Cor.VERMELHO if temp > TEMP_MAX else Cor.VERDE
    cor_gas  = Cor.VERMELHO if gas > GAS_MAX   else Cor.VERDE
    cor_pres = Cor.AMARELO  if pres            else Cor.VERDE

    print(f"  🌡  Temperatura  : {colorir(f'{temp:5.1f}°C', cor_temp)} {desenhar_barra(temp, 0, 50)}")
    print(f"  💧 Umidade      : {Cor.AZUL}{umid:5.1f}%  {Cor.RESET}{desenhar_barra(umid, 0, 100)}")
    print(f"  🔥 Gás          : {colorir(f'{gas:5d}ppm', cor_gas)} {desenhar_barra(gas, 0, 500)}")
    print(f"  💡 Luminosidade : {Cor.CIANO}{lux:5d}lux{Cor.RESET} {desenhar_barra(lux, 0, 1000)}")
    print(f"  👁  Presença     : {colorir('SIM ⚠', Cor.AMARELO) if pres else colorir('NÃO  ', Cor.VERDE)}")

    print(f"{'─'*62}")

    # Estado dos atuadores
    print("  ATUADORES:")
    for nome, at in atuadores.items():
        estado_str = colorir("● ON ", Cor.VERDE) if at.estado else colorir("○ OFF", Cor.RESET)
        print(f"    {estado_str}  {at.nome}")

    print(f"{'─'*62}")

    # Análise de IA
    print(f"  IA — Nível de Risco: {colorir(nivel, cor)}")
    print(f"  ML — {relatorio_ia['anomalia_ml']['classificacao']}")

    if relatorio_ia["regras_disparadas"]:
        print("  Alertas:")
        for r in relatorio_ia["regras_disparadas"]:
            print(f"    ⚠  [{r['id']}] {r['descricao']}")
    else:
        print(f"  {Cor.VERDE}✅ Sistema em condições normais.{Cor.RESET}")

    print(f"{Cor.NEGRITO}{'═'*62}{Cor.RESET}")


# ─────────────────────────────────────────────
#  Loop principal do monitor
# ─────────────────────────────────────────────

def iniciar_monitor(ciclos: int = 8, intervalo: float = 1.5):
    """Inicia o monitor serial integrado."""
    if not MODULOS_OK:
        print("  ❌ Erro ao importar módulos. Execute a partir do diretório src/.")
        return

    # Setup
    sensores = {
        "dht22": SensorDHT22(pino=2),
        "pir"  : SensorPIR(pino=3),
        "mq2"  : SensorMQ2(pino="A0"),
        "ldr"  : SensorLDR(pino="A1"),
    }
    atuadores = {
        "buzzer"     : Atuador("Buzzer",     pino=8),
        "led_alarme" : Atuador("LED Alarme", pino=9),
        "led_luz"    : Atuador("LED Luz",    pino=10),
        "ventilador" : Atuador("Ventilador", pino=11),
        "exaustor"   : Atuador("Exaustor",   pino=12),
    }
    ia = MotorIA()

    for ciclo in range(1, ciclos + 1):
        # Leitura de sensores
        dados = {}
        dados.update(sensores["dht22"].ler())
        dados.update(sensores["pir"].ler())
        dados.update(sensores["mq2"].ler())
        dados.update(sensores["ldr"].ler())

        # Decisão automatizada
        processar_decisao(dados, atuadores)

        # Análise IA
        relatorio = ia.analisar(dados)

        # Dashboard
        exibir_dashboard(dados, relatorio, ciclo, atuadores)

        time.sleep(intervalo)

    print("\n  Monitor encerrado.")


if __name__ == "__main__":
    ciclos = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    iniciar_monitor(ciclos=ciclos)
