"""Executa e mede os dois algoritmos em Python sobre lotes TSV."""

import argparse
import csv
import sys
from pathlib import Path
from time import perf_counter_ns

from subset_sum import forca_bruta, programacao_dinamica

ALGORITMOS = {"forca_bruta": forca_bruta, "pd": programacao_dinamica}
ENTRADA = ("caso", "cenario", "n", "alvo", "repeticoes", "valores")
SAIDA = ("caso", "cenario", "n", "alvo", "algoritmo", "repeticao", "resposta", "tempo_ns")
MAX_SOMA = (1 << 63) - 1


def inteiro(texto):
    if not texto or not texto.isascii() or not texto.isdecimal():
        raise ValueError(f"inteiro não negativo esperado: {texto!r}")
    return int(texto)


def ler_entradas(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        leitor = csv.reader(arquivo, delimiter="\t")
        if tuple(next(leitor, ())) != ENTRADA:
            raise ValueError("cabeçalho TSV inválido")
        casos = []
        for caso, cenario, n, alvo, repeticoes, dados in leitor:
            n, alvo, repeticoes = map(inteiro, (n, alvo, repeticoes))
            valores = tuple(map(inteiro, dados.split()))
            if len(valores) != n or repeticoes < 1 or not caso or not cenario:
                raise ValueError(f"entrada inválida no caso {caso!r}")
            if sum(valores) > MAX_SOMA or alvo >= min(MAX_SOMA + 1, sys.maxsize):
                raise ValueError(f"entrada fora dos limites numéricos no caso {caso!r}")
            casos.append((caso, cenario, n, alvo, repeticoes, valores))
        return casos


def executar(casos, algoritmos, escritor):
    escritor.writerow(SAIDA)
    for algoritmo in algoritmos:
        funcao = ALGORITMOS[algoritmo]
        for _ in range(5):
            funcao((3, 5, 9), 8)
        for caso, cenario, n, alvo, repeticoes, valores in casos:
            for repeticao in range(1, repeticoes + 1):
                inicio = perf_counter_ns()
                resposta = funcao(valores, alvo)
                tempo = perf_counter_ns() - inicio
                escritor.writerow((caso, cenario, n, alvo, algoritmo, repeticao, int(resposta), tempo))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", type=Path)
    parser.add_argument("saida", type=Path)
    parser.add_argument("algoritmo", choices=(*ALGORITMOS, "ambos"))
    args = parser.parse_args()
    algoritmos = ALGORITMOS if args.algoritmo == "ambos" else (args.algoritmo,)
    try:
        casos = ler_entradas(args.entrada)
        with args.saida.open("w", encoding="utf-8", newline="") as arquivo:
            executar(casos, algoritmos, csv.writer(arquivo))
    except (OSError, ValueError, MemoryError) as erro:
        parser.exit(1, f"Erro: {erro or 'memória insuficiente'}\n")


if __name__ == "__main__":
    main()
