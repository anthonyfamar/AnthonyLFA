"""
simulador_arm.py
Simulação do Pipeline de Processador ARM (Fetch → Decode → Execute → Write Back)
Autor: Anthony Famar Gomes — 5° Semestre Ciência da Computação

Demonstra o ciclo de instrução de um processador ARM com banco de registradores,
memória simulada e suporte aos opcodes: MOV, ADD, SUB, CMP, B, BEQ, BNE, LDR, STR, AND, ORR.
"""

from dataclasses import dataclass, field
from typing import Optional
import time


# ─────────────────────────────────────────────
#  Estruturas de dados
# ─────────────────────────────────────────────

@dataclass
class Instrucao:
    """Representa uma instrução ARM decodificada."""
    opcode   : str
    dest     : Optional[str] = None
    op1      : Optional[str] = None
    op2      : Optional[str] = None
    label    : Optional[str] = None
    original : str = ""


@dataclass
class EstadoPipeline:
    """Estado completo do pipeline em um dado ciclo."""
    pc       : int
    fetch    : str
    decoded  : Optional[Instrucao]
    execute  : str
    flags    : dict


# ─────────────────────────────────────────────
#  Processador ARM Simulado
# ─────────────────────────────────────────────

class ProcessadorARM:
    """
    Simula um processador ARM simplificado com:
    - 16 registradores (R0–R15, onde R15 = PC)
    - Banco de memória de 256 palavras
    - Flags CPSR: Z (Zero), N (Negativo), C (Carry), V (Overflow)
    - Pipeline de 4 estágios: Fetch → Decode → Execute → Write Back
    """

    NUM_REGS = 16
    MEM_SIZE = 256

    def __init__(self):
        # Banco de registradores (R0–R15)
        self.regs    : list[int] = [0] * self.NUM_REGS
        # Memória de dados (palavras de 32 bits)
        self.memoria : list[int] = [0] * self.MEM_SIZE
        # Flags do CPSR
        self.flags   : dict[str, bool] = {"Z": False, "N": False, "C": False, "V": False}
        # Program Counter
        self.pc      : int = 0
        # Programa carregado (lista de strings)
        self.programa: list[str] = []
        # Tabela de labels para desvios
        self.labels  : dict[str, int] = {}
        # Histórico de execução
        self.historico: list[EstadoPipeline] = []

    @property
    def R(self):
        """Alias para o banco de registradores."""
        return self.regs

    # ── Carregamento do programa ──────────────────

    def carregar_programa(self, instrucoes: list[str]):
        """
        Carrega um programa (lista de strings assembly ARM) na memória de instruções.
        Resolve labels automaticamente.
        """
        self.programa = []
        self.labels   = {}
        linha_real    = 0

        for linha in instrucoes:
            linha = linha.strip()
            if not linha or linha.startswith(";"):
                continue
            if linha.endswith(":"):
                self.labels[linha[:-1]] = linha_real
            else:
                self.programa.append(linha)
                linha_real += 1

        self.pc = 0
        print(f"  ✅ Programa carregado: {len(self.programa)} instruções")
        if self.labels:
            print(f"  📌 Labels: {self.labels}")

    # ── Estágio 1: FETCH ─────────────────────────

    def fetch(self) -> Optional[str]:
        """Busca a instrução apontada pelo PC na memória de instruções."""
        if self.pc >= len(self.programa):
            return None
        instrucao = self.programa[self.pc]
        return instrucao

    # ── Estágio 2: DECODE ────────────────────────

    def decode(self, instrucao_raw: str) -> Instrucao:
        """Decodifica a instrução ARM em opcode + operandos."""
        partes = instrucao_raw.replace(",", " ").split()
        opcode = partes[0].upper()

        inst = Instrucao(opcode=opcode, original=instrucao_raw)

        if opcode in ("MOV", "MVN"):
            inst.dest, inst.op1 = partes[1], partes[2]
        elif opcode in ("ADD", "SUB", "AND", "ORR", "EOR"):
            inst.dest, inst.op1, inst.op2 = partes[1], partes[2], partes[3]
        elif opcode in ("CMP", "TST"):
            inst.op1, inst.op2 = partes[1], partes[2]
        elif opcode in ("B", "BEQ", "BNE", "BGT", "BLT", "BLE", "BGE"):
            inst.label = partes[1]
        elif opcode in ("LDR", "STR"):
            inst.dest = partes[1]
            inst.op1  = partes[2].strip("[]")
        elif opcode == "NOP":
            pass

        return inst

    # ── Estágio 3: EXECUTE + WRITE BACK ──────────

    def _resolver_operando(self, op: str) -> int:
        """Resolve um operando: registrador (R0-R15) ou imediato (#N)."""
        if op.startswith("#"):
            return int(op[1:])
        idx = int(op[1:])  # Rx → índice
        return self.regs[idx]

    def _atualizar_flags(self, resultado: int):
        """Atualiza as flags CPSR com base no resultado."""
        self.flags["Z"] = resultado == 0
        self.flags["N"] = resultado < 0
        self.flags["C"] = resultado > 0xFFFFFFFF
        self.flags["V"] = resultado > 2**31 - 1 or resultado < -(2**31)

    def execute(self, inst: Instrucao) -> str:
        """Executa a instrução decodificada e retorna descrição da operação."""
        op = inst.opcode
        resultado_str = ""

        if op == "NOP":
            resultado_str = "NOP — nenhuma operação"
            self.pc += 1

        elif op == "MOV":
            val = self._resolver_operando(inst.op1)
            dest_idx = int(inst.dest[1:])
            self.regs[dest_idx] = val
            resultado_str = f"{inst.dest} ← {val}"
            self.pc += 1

        elif op == "MVN":
            val = ~self._resolver_operando(inst.op1) & 0xFFFFFFFF
            dest_idx = int(inst.dest[1:])
            self.regs[dest_idx] = val
            resultado_str = f"{inst.dest} ← NOT {inst.op1} = {val}"
            self.pc += 1

        elif op == "ADD":
            a   = self._resolver_operando(inst.op1)
            b   = self._resolver_operando(inst.op2)
            res = a + b
            dest_idx = int(inst.dest[1:])
            self.regs[dest_idx] = res
            self._atualizar_flags(res)
            resultado_str = f"{inst.dest} ← {a} + {b} = {res}"
            self.pc += 1

        elif op == "SUB":
            a   = self._resolver_operando(inst.op1)
            b   = self._resolver_operando(inst.op2)
            res = a - b
            dest_idx = int(inst.dest[1:])
            self.regs[dest_idx] = res
            self._atualizar_flags(res)
            resultado_str = f"{inst.dest} ← {a} - {b} = {res}"
            self.pc += 1

        elif op == "AND":
            a   = self._resolver_operando(inst.op1)
            b   = self._resolver_operando(inst.op2)
            res = a & b
            dest_idx = int(inst.dest[1:])
            self.regs[dest_idx] = res
            resultado_str = f"{inst.dest} ← {a} AND {b} = {res}"
            self.pc += 1

        elif op == "ORR":
            a   = self._resolver_operando(inst.op1)
            b   = self._resolver_operando(inst.op2)
            res = a | b
            dest_idx = int(inst.dest[1:])
            self.regs[dest_idx] = res
            resultado_str = f"{inst.dest} ← {a} OR {b} = {res}"
            self.pc += 1

        elif op == "CMP":
            a   = self._resolver_operando(inst.op1)
            b   = self._resolver_operando(inst.op2)
            res = a - b
            self._atualizar_flags(res)
            resultado_str = f"CMP {inst.op1}({a}) vs {inst.op2}({b}) → flags={self.flags}"
            self.pc += 1

        elif op == "B":
            dest = self.labels.get(inst.label, self.pc)
            resultado_str = f"Desvio incondicional → {inst.label} (PC={dest})"
            self.pc = dest

        elif op == "BEQ":
            if self.flags["Z"]:
                dest = self.labels.get(inst.label, self.pc)
                resultado_str = f"BEQ: Z=1, desvio para {inst.label} (PC={dest})"
                self.pc = dest
            else:
                resultado_str = f"BEQ: Z=0, sem desvio"
                self.pc += 1

        elif op == "BNE":
            if not self.flags["Z"]:
                dest = self.labels.get(inst.label, self.pc)
                resultado_str = f"BNE: Z=0, desvio para {inst.label} (PC={dest})"
                self.pc = dest
            else:
                resultado_str = f"BNE: Z=1, sem desvio"
                self.pc += 1

        elif op == "LDR":
            addr = self._resolver_operando(inst.op1)
            val  = self.memoria[addr % self.MEM_SIZE]
            dest_idx = int(inst.dest[1:])
            self.regs[dest_idx] = val
            resultado_str = f"{inst.dest} ← MEM[{addr}] = {val}"
            self.pc += 1

        elif op == "STR":
            val  = self._resolver_operando(inst.dest)
            addr = self._resolver_operando(inst.op1)
            self.memoria[addr % self.MEM_SIZE] = val
            resultado_str = f"MEM[{addr}] ← {val}"
            self.pc += 1

        else:
            resultado_str = f"Instrução desconhecida: {op}"
            self.pc += 1

        return resultado_str

    # ── Execução do pipeline completo ────────────

    def executar_programa(self, max_ciclos: int = 100, verbose: bool = True):
        """Executa o programa instrução por instrução mostrando cada estágio do pipeline."""
        ciclo = 0
        print("\n" + "═" * 60)
        print("  SIMULAÇÃO ARM — PIPELINE DE 4 ESTÁGIOS")
        print("═" * 60)

        while self.pc < len(self.programa) and ciclo < max_ciclos:
            ciclo += 1
            pc_atual = self.pc

            # FETCH
            raw = self.fetch()
            if raw is None:
                break

            # DECODE
            inst = self.decode(raw)

            # EXECUTE + WRITE BACK
            resultado = self.execute(inst)

            # Registrar estado
            estado = EstadoPipeline(
                pc      = pc_atual,
                fetch   = raw,
                decoded = inst,
                execute = resultado,
                flags   = self.flags.copy()
            )
            self.historico.append(estado)

            if verbose:
                print(f"\n  Ciclo {ciclo:02d} | PC={pc_atual}")
                print(f"  ┌ FETCH   : {raw}")
                print(f"  ├ DECODE  : opcode={inst.opcode} dest={inst.dest} op1={inst.op1} op2={inst.op2}")
                print(f"  ├ EXECUTE : {resultado}")
                print(f"  └ FLAGS   : Z={int(self.flags['Z'])} N={int(self.flags['N'])} C={int(self.flags['C'])} V={int(self.flags['V'])}")
                print(f"  Regs: { {f'R{i}': self.regs[i] for i in range(8)} }")

        print(f"\n  ✅ Programa finalizado em {ciclo} ciclos.")
        print("═" * 60)


# ─────────────────────────────────────────────
#  Programa de exemplo: lógica de sensor
# ─────────────────────────────────────────────

PROGRAMA_SENSOR = [
    "; Programa ARM — Lógica de Monitoramento Residencial",
    "; R0 = temperatura lida, R1 = limiar (35), R2 = resultado alarme",
    "MOV R0, #38",        # Temperatura lida = 38°C
    "MOV R1, #35",        # Limiar = 35°C
    "MOV R2, #0",         # Alarme desligado
    "CMP R0, R1",         # Compara temperatura com limiar
    "BLE fim",            # Se temp <= 35, pula para fim
    "MOV R2, #1",         # Acende alarme
    "ADD R3, R0, R1",     # R3 = soma (demonstração ADD)
    "SUB R4, R0, R1",     # R4 = diferença (quanto passou do limiar)
    "STR R2, [R5]",       # Salva estado do alarme na memória
    "fim:",
    "MOV R6, #255",       # Marca fim do programa
]


if __name__ == "__main__":
    cpu = ProcessadorARM()
    cpu.regs[5] = 10  # Endereço de memória para o alarme

    cpu.carregar_programa(PROGRAMA_SENSOR)
    cpu.executar_programa(verbose=True)

    print("\n  Estado final da memória [0–15]:")
    print(" ", cpu.memoria[:16])
