"""Executa e mede os dois algoritmos em Python sobre lotes TSV."""

import argparse
import csv
import sys
import tracemalloc
from pathlib import Path
from time import perf_counter_ns

from subset_sum import forca_bruta, programacao_dinamica

ALGORITMOS = {"forca_bruta": forca_bruta, "pd": programacao_dinamica}
ENTRADA = ("caso", "cenario", "n", "alvo", "repeticoes", "valores")
SAIDA = ("caso", "cenario", "n", "alvo", "algoritmo", "repeticao", "resposta")
MEDIDAS = {"tempo": ("tempo_ns", "chamadas"), "memoria": ("pico_bytes",)}
MAX_SOMA = (1 << 63) - 1
LOTE_MINIMO_NS = 1_000_000
CHAMADA_LONGA_NS = 1_000_000_000
AQUECIMENTO_NS = 500_000_000
csv.field_size_limit(2**31 - 1)


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


def cronometrar(funcao, valores, alvo, chamadas):
    resposta = False
    inicio = perf_counter_ns()
    for _ in range(chamadas):
        resposta = funcao(valores, alvo)
    return resposta, perf_counter_ns() - inicio


def medir_tempo(funcao, valores, alvo, repeticoes):
    chamadas = 1
    resposta, tempo = cronometrar(funcao, valores, alvo, chamadas)
    while tempo < LOTE_MINIMO_NS:
        chamadas *= 2
        resposta, tempo = cronometrar(funcao, valores, alvo, chamadas)
    for repeticao in range(repeticoes):
        if repeticao or tempo < CHAMADA_LONGA_NS:
            resposta, tempo = cronometrar(funcao, valores, alvo, chamadas)
        yield resposta, f"{tempo / chamadas:.3f}", chamadas


def medir_memoria(funcao, valores, alvo, repeticoes):
    for _ in range(repeticoes):
        tracemalloc.start()
        try:
            resposta = funcao(valores, alvo)
            pico = tracemalloc.get_traced_memory()[1]
        finally:
            tracemalloc.stop()
        yield resposta, pico


def executar(casos, algoritmos, medida, escritor):
    escritor.writerow(SAIDA + MEDIDAS[medida])
    medir = medir_tempo if medida == "tempo" else medir_memoria
    for algoritmo in algoritmos:
        funcao = ALGORITMOS[algoritmo]
        inicio = perf_counter_ns()
        while perf_counter_ns() - inicio < AQUECIMENTO_NS:
            funcao((3, 5, 9), 8)
        for caso, cenario, n, alvo, repeticoes, valores in casos:
            for repeticao, (resposta, *leitura) in enumerate(medir(funcao, valores, alvo, repeticoes), 1):
                escritor.writerow((caso, cenario, n, alvo, algoritmo, repeticao, int(resposta), *leitura))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", type=Path)
    parser.add_argument("saida", type=Path)
    parser.add_argument("algoritmo", choices=(*ALGORITMOS, "ambos"))
    parser.add_argument("medida", choices=tuple(MEDIDAS), nargs="?", default="tempo")
    args = parser.parse_args()
    algoritmos = ALGORITMOS if args.algoritmo == "ambos" else (args.algoritmo,)
    try:
        casos = ler_entradas(args.entrada)
        with args.saida.open("w", encoding="utf-8", newline="") as arquivo:
            executar(casos, algoritmos, args.medida, csv.writer(arquivo))
    except (OSError, ValueError, MemoryError) as erro:
        parser.exit(1, f"Erro: {erro or 'memória insuficiente'}\n")


if __name__ == "__main__":
    main()
