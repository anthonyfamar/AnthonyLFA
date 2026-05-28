from flask import Flask, jsonify, send_file
import time
from src.simulador_arduino import SensorDHT22, SensorPIR, SensorMQ2, SensorLDR, Atuador, processar_decisao
from src.ia_decisao import MotorIA
from src.simulador_arm import ProcessadorARM, PROGRAMA_SENSOR

app = Flask(__name__)

# --- Setup Global do Sistema ---
sensores = {
    "dht22": SensorDHT22(pino=2),
    "pir": SensorPIR(pino=3),
    "mq2": SensorMQ2(pino="A0"),
    "ldr": SensorLDR(pino="A1"),
}
atuadores = {
    "buzzer": Atuador("Buzzer", pino=8),
    "led_alarme": Atuador("LED Alarme", pino=9),
    "led_luz": Atuador("LED Luz", pino=10),
    "ventilador": Atuador("Ventilador", pino=11),
    "exaustor": Atuador("Exaustor", pino=12),
}
ia = MotorIA()
cpu = ProcessadorARM()
cpu.carregar_programa(PROGRAMA_SENSOR)

@app.route('/')
def index():
    # Retorna o seu dashboard HTML
    return send_file('dashboard.html')

@app.route('/api/tick')
def get_tick():
    """Executa 1 ciclo do sistema e retorna os dados em JSON para o Dashboard"""
    
    # 1. Leitura de Sensores
    dados = {}
    dados.update(sensores["dht22"].ler())
    dados.update(sensores["pir"].ler())
    dados.update(sensores["mq2"].ler())
    dados.update(sensores["ldr"].ler())

    # 2. Lógica Embarcada (Atuadores)
    alertas = processar_decisao(dados, atuadores)
    
    # 3. Inteligência Artificial
    relatorio = ia.analisar(dados)

    # 4. Simulação ARM (Atualiza valores de memória/registradores com base nos sensores)
    cpu.regs[0] = int(dados["temperatura"])
    cpu.regs[1] = 35 # Limiar de temperatura
    cpu.pc = 0
    
    # Executa até a comparação (CMP) para atualizar as flags na simulação para o frontend
    instrucao_atual = ""
    for _ in range(6): 
        raw = cpu.fetch()
        if not raw: break
        inst = cpu.decode(raw)
        res = cpu.execute(inst)
        instrucao_atual = raw
        if "CMP" in raw: break 

    # --- Formatação para o Frontend ---
    estado_atuadores = {nome: at.estado for nome, at in atuadores.items()}
    regras_formatadas = [{"id": r["id"], "msg": r["descricao"], "risk": r["risco"]} for r in relatorio["regras_disparadas"]]

    return jsonify({
        "sensores": dados,
        "atuadores": estado_atuadores,
        "ia": {
            "topRisk": relatorio["nivel_risco"],
            "anomaly": relatorio["anomalia_ml"]["anomalia"],
            "fired": regras_formatadas
        },
        "arm": {
            "fetch": instrucao_atual,
            "regs": cpu.regs[:8],
            "z": cpu.flags.get("Z", False),
            "n": cpu.flags.get("N", False)
        }
    })

if __name__ == '__main__':
    print("🚀 Servidor iniciado! Acesse http://127.0.0.1:5000")
    app.run(debug=True, port=5000)