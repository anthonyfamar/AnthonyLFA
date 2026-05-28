"""
ia_decisao.py
Módulo de Inteligência Artificial para Monitoramento Residencial
Autor: Anthony Famar Gomes — 5° Semestre Ciência da Computação

Implementa:
  1. Sistema baseado em regras (Rule-Based System)
  2. Detecção de anomalias com Isolation Forest (scikit-learn)
  3. Histórico e classificação de riscos
"""

import random
from datetime import datetime
from collections import deque

try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    SKLEARN_DISPONIVEL = True
except ImportError:
    SKLEARN_DISPONIVEL = False
    print("  ⚠  scikit-learn não instalado. Usando apenas sistema de regras.")


# ─────────────────────────────────────────────
#  Níveis de risco
# ─────────────────────────────────────────────

class NivelRisco:
    NORMAL  = "NORMAL"
    BAIXO   = "BAIXO"
    MEDIO   = "MÉDIO"
    ALTO    = "ALTO"
    CRITICO = "CRÍTICO"


# ─────────────────────────────────────────────
#  Sistema Baseado em Regras
# ─────────────────────────────────────────────

class SistemaRegras:
    """
    Motor de inferência baseado em regras (Forward Chaining).
    Cada regra tem condição (função lambda) e ação (descrição + nível de risco).
    """

    def __init__(self):
        self.regras = [
            {
                "id"       : "R01",
                "descricao": "Temperatura crítica",
                "condicao" : lambda d: d["temperatura"] > 40,
                "risco"    : NivelRisco.CRITICO,
                "acao"     : "Acionar todos os alarmes. Verificar incêndio.",
            },
            {
                "id"       : "R02",
                "descricao": "Temperatura alta",
                "condicao" : lambda d: 35 < d["temperatura"] <= 40,
                "risco"    : NivelRisco.ALTO,
                "acao"     : "Ligar ventilador. Emitir alerta.",
            },
            {
                "id"       : "R03",
                "descricao": "Gás perigoso detectado",
                "condicao" : lambda d: d["gas_ppm"] > 300,
                "risco"    : NivelRisco.CRITICO,
                "acao"     : "Abrir exaustor. Soar alarme. Notificar emergência.",
            },
            {
                "id"       : "R04",
                "descricao": "Gás em nível de atenção",
                "condicao" : lambda d: 150 < d["gas_ppm"] <= 300,
                "risco"    : NivelRisco.MEDIO,
                "acao"     : "Aumentar ventilação. Monitorar continuamente.",
            },
            {
                "id"       : "R05",
                "descricao": "Presença detectada à noite",
                "condicao" : lambda d: d["presenca"] and d["luminosidade_lux"] < 100,
                "risco"    : NivelRisco.ALTO,
                "acao"     : "Acionar alarme de intrusão. Ligar câmeras.",
            },
            {
                "id"       : "R06",
                "descricao": "Presença detectada",
                "condicao" : lambda d: d["presenca"],
                "risco"    : NivelRisco.BAIXO,
                "acao"     : "Registrar evento. Ligar iluminação.",
            },
            {
                "id"       : "R07",
                "descricao": "Umidade baixa",
                "condicao" : lambda d: d["umidade"] < 20,
                "risco"    : NivelRisco.MEDIO,
                "acao"     : "Ligar umidificador. Alertar usuário.",
            },
            {
                "id"       : "R08",
                "descricao": "Luminosidade baixa (noite)",
                "condicao" : lambda d: d["luminosidade_lux"] < 200,
                "risco"    : NivelRisco.NORMAL,
                "acao"     : "Ligar iluminação automática.",
            },
        ]

    def inferir(self, dados: dict) -> list[dict]:
        """Executa o motor de inferência e retorna todas as regras disparadas."""
        disparadas = []
        for regra in self.regras:
            try:
                if regra["condicao"](dados):
                    disparadas.append({
                        "id"       : regra["id"],
                        "descricao": regra["descricao"],
                        "risco"    : regra["risco"],
                        "acao"     : regra["acao"],
                    })
            except Exception:
                pass
        return disparadas


# ─────────────────────────────────────────────
#  Detecção de Anomalias com ML
# ─────────────────────────────────────────────

class DetectorAnomalias:
    """
    Usa Isolation Forest para detectar leituras anômalas nos sensores.
    O modelo é treinado com dados normais gerados na inicialização.
    """

    def __init__(self, contaminacao: float = 0.1):
        self.treinado = False
        self.modelo   = None
        self.contaminacao = contaminacao

        if SKLEARN_DISPONIVEL:
            self._treinar_com_dados_normais()

    def _gerar_dados_normais(self, n: int = 200) -> np.ndarray:
        """Gera amostras de condições normais para treinar o modelo."""
        dados = []
        for _ in range(n):
            temp  = random.gauss(25, 3)
            umid  = random.gauss(60, 8)
            gas   = random.gauss(50, 20)
            lux   = random.gauss(400, 100)
            dados.append([temp, umid, gas, lux])
        return np.array(dados)

    def _treinar_com_dados_normais(self):
        """Treina o Isolation Forest com dados de condição normal."""
        X_treino = self._gerar_dados_normais(300)
        self.modelo = IsolationForest(
            contamination=self.contaminacao,
            random_state=42,
            n_estimators=100
        )
        self.modelo.fit(X_treino)
        self.treinado = True

    def classificar(self, dados: dict) -> dict:
        """
        Classifica uma leitura como NORMAL ou ANOMALIA.
        Retorna score de anomalia e classificação.
        """
        if not SKLEARN_DISPONIVEL or not self.treinado:
            return {"anomalia": False, "score": 0.0, "classificacao": "N/A (sem sklearn)"}

        X = np.array([[
            dados["temperatura"],
            dados["umidade"],
            dados["gas_ppm"],
            dados["luminosidade_lux"]
        ]])

        pred  = self.modelo.predict(X)[0]       # 1 = normal, -1 = anomalia
        score = self.modelo.score_samples(X)[0] # Mais negativo = mais anômalo

        anomalia = pred == -1
        return {
            "anomalia"      : anomalia,
            "score"         : round(float(score), 4),
            "classificacao" : "⚠ ANOMALIA" if anomalia else "✅ NORMAL",
        }


# ─────────────────────────────────────────────
#  Motor de IA Principal
# ─────────────────────────────────────────────

class MotorIA:
    """
    Orquestra o sistema de regras e a detecção de anomalias.
    Mantém histórico das últimas leituras e gera relatório de risco.
    """

    PRIORIDADE_RISCO = {
        NivelRisco.NORMAL  : 0,
        NivelRisco.BAIXO   : 1,
        NivelRisco.MEDIO   : 2,
        NivelRisco.ALTO    : 3,
        NivelRisco.CRITICO : 4,
    }

    def __init__(self):
        self.regras    = SistemaRegras()
        self.detector  = DetectorAnomalias()
        self.historico = deque(maxlen=50)

    def analisar(self, dados: dict) -> dict:
        """
        Analisa os dados dos sensores com todas as técnicas de IA disponíveis.
        Retorna um relatório completo.
        """
        # Sistema de regras
        regras_disparadas = self.regras.inferir(dados)

        # Detecção de anomalias
        anomalia = self.detector.classificar(dados)

        # Nível de risco geral (pior regra disparada)
        if regras_disparadas:
            nivel_geral = max(
                regras_disparadas,
                key=lambda r: self.PRIORIDADE_RISCO.get(r["risco"], 0)
            )["risco"]
        else:
            nivel_geral = NivelRisco.NORMAL

        relatorio = {
            "timestamp"        : datetime.now().isoformat(),
            "dados"            : dados,
            "nivel_risco"      : nivel_geral,
            "regras_disparadas": regras_disparadas,
            "anomalia_ml"      : anomalia,
        }

        self.historico.append(relatorio)
        return relatorio

    def exibir_relatorio(self, relatorio: dict):
        """Exibe o relatório de IA no console."""
        print("\n  ┌─── ANÁLISE DE IA ───────────────────────")
        print(f"  │ Nível de Risco : {relatorio['nivel_risco']}")
        print(f"  │ ML (Anomalia)  : {relatorio['anomalia_ml']['classificacao']}")
        if relatorio["regras_disparadas"]:
            print(f"  │ Regras ativas  :")
            for r in relatorio["regras_disparadas"]:
                print(f"  │   [{r['id']}] {r['descricao']} → {r['acao']}")
        else:
            print(f"  │ Regras ativas  : Nenhuma")
        print("  └─────────────────────────────────────────")


# ─────────────────────────────────────────────
#  Demonstração
# ─────────────────────────────────────────────

if __name__ == "__main__":
    ia = MotorIA()

    cenarios = [
        {"temperatura": 24.5, "umidade": 65.0, "presenca": False, "gas_ppm": 45,  "luminosidade_lux": 450},
        {"temperatura": 38.1, "umidade": 55.0, "presenca": False, "gas_ppm": 60,  "luminosidade_lux": 300},
        {"temperatura": 27.0, "umidade": 60.0, "presenca": True,  "gas_ppm": 320, "luminosidade_lux": 80},
        {"temperatura": 42.5, "umidade": 15.0, "presenca": True,  "gas_ppm": 450, "luminosidade_lux": 50},
    ]

    print("=" * 55)
    print("  DEMONSTRAÇÃO — MÓDULO DE INTELIGÊNCIA ARTIFICIAL")
    print("=" * 55)

    for i, cenario in enumerate(cenarios, 1):
        print(f"\n  Cenário {i}: {cenario}")
        relatorio = ia.analisar(cenario)
        ia.exibir_relatorio(relatorio)
