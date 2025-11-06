# Mini "Compilador" de Texto
# Autor: Anthony
# Objetivo: Ler letras e palavras e mostrar informações sobre elas (ASCII, Hexadecimal, Tipo etc.)

def analisar_texto(texto):
    print("\n=== ANÁLISE DE TEXTO ===")
    print(f"Entrada: \"{texto}\"\n")

    palavras = texto.split()
    print(f"Total de palavras: {len(palavras)}")
    print(f"Total de caracteres (sem espaços): {len(texto.replace(' ', ''))}\n")

    print("--- ANÁLISE DE CADA CARACTERE ---")
    for i, c in enumerate(texto):
        if c.strip() == "":
            continue  # ignora espaços
        tipo = "Letra" if c.isalpha() else "Número" if c.isdigit() else "Símbolo"
        print(f"[{i}] '{c}' → Tipo: {tipo} | ASCII: {ord(c)} | Hex: {hex(ord(c))}")

    print("\n--- ANÁLISE DE PALAVRAS ---")
    for i, palavra in enumerate(palavras, start=1):
        hexa = ' '.join(hex(ord(c)) for c in palavra)
        print(f"{i}. \"{palavra}\" → Tamanho: {len(palavra)} | Hexadecimal: {hexa}")


if __name__ == "__main__":
    texto = input("Digite uma frase ou palavra: ")
    analisar_texto(texto)