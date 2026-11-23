"""Compara as quatro implementa��es com um or�culo por combina��es."""

import argparse
import os
import random
import subprocess
import sys
from itertools import combinations
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from gerar_entradas import SEMENTE, escrever_tsv
from medir import PYTHON, compilar, indexar_respostas, ler_csv

FIXOS = {
    "vazio_alvo_zero": ((), 0, 1),
    "vazio_alvo_positivo": ((), 1, 0),
    "zero_com_positivos": ((0, 4, 9), 0, 1),
    "um_item_uso_unico": ((4,), 8, 0),
    "repetidos_usam_posicoes_distintas": ((4, 4), 8, 1),
    "repetidos_sem_reutilizacao": ((4, 4), 12, 0),
    "exemplo": ((3, 5, 9, 12), 14, 1),
    "paridade": ((6, 10, 14), 15, 0),
    "alvo_acima_da_soma": ((1, 2, 3), 7, 0),
    "inteiro_grande": ((2**40, 3), 3, 1),
    "varios_zeros": ((0, 0, 8), 8, 1),
    "primeiro_item": ((7, 1, 3), 7, 1),
}


def oraculo(valores, alvo):
    return int(any(
        sum(selecao) == alvo
        for tamanho in range(len(valores) + 1)
        for selecao in combinations(valores, tamanho)
    ))


def gerar_casos():
    for identificador, (valores, alvo, esperado) in FIXOS.items():
        if oraculo(valores, alvo) != esperado:
            raise AssertionError(f"caso fixo incorreto: {identificador}")
        yield f"fixo-{identificador}", alvo, valores, esperado
    rng = random.Random(SEMENTE + 2)
    for i in range(160):
        valores = tuple(rng.randint(0, 35) for _ in range(rng.randint(0, 11)))
        alvo = rng.randint(0, sum(valores) + 8)
        yield f"aleatorio-{i:03d}", alvo, valores, oraculo(valores, alvo)


def testar(comando, destino, casos):
    entrada = destino / "testes.tsv"
    saida = destino / "testes.csv"
    escrever_tsv(entrada, [(id_caso, "teste", alvo, 1, valores)
                          for id_caso, alvo, valores, _ in casos])
    subprocess.run([*comando, str(entrada), str(saida), "ambos"], check=True)
    obtidas = indexar_respostas(ler_csv(saida))
    esperadas = {
        (id_caso, algoritmo, 1): resposta
        for id_caso, _, _, resposta in casos
        for algoritmo in ("forca_bruta", "pd")
    }
    if obtidas != esperadas:
        divergencias = [chave for chave, valor in esperadas.items() if obtidas.get(chave) != valor]
        raise AssertionError(f"diverg�ncias ou registros extras em {comando[0]}: {divergencias[:10]}")

    escrever_tsv(entrada, [("negativo", "teste", 1, 1, (-1, 2))])
    execucao = subprocess.run([*comando, str(entrada), str(saida), "ambos"], capture_output=True)
    if execucao.returncode != 1:
        raise AssertionError("a interface deveria rejeitar valores negativos")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cxx", default=os.getenv("CXX", "g++"))
    args = parser.parse_args()
    casos = list(gerar_casos())
    with TemporaryDirectory(prefix="subset-sum-testes-") as temp:
        for comando in (compilar(args.cxx), PYTHON):
            testar(comando, Path(temp), casos)
    print(f"OK: {len(casos)} casos, {len(casos) * 4} decis�es e rejei��o de entrada negativa nas duas interfaces.")


if __name__ == "__main__":
    main()
