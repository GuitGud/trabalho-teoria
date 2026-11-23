"""Mede o efeito do alvo S com lista fixa e sempre sem solução."""

import argparse
import os
import subprocess
from pathlib import Path

from gerar_entradas import RAIZ, REPETICOES, caso_limite, escrever_tsv
from medir import PYTHON, compilar, ler_csv, verificar_respostas

N = 13
ALVOS = (65, 129, 257, 513, 1025, 2049, 4097, 8193)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cxx", default=os.getenv("CXX", "g++"))
    parser.add_argument("--dados", type=Path, default=RAIZ / "dados")
    parser.add_argument("--saida", type=Path, default=RAIZ / "resultados")
    args = parser.parse_args()
    args.saida.mkdir(parents=True, exist_ok=True)
    entradas = args.dados / "entradas_alvo.tsv"
    valores = caso_limite(N)[4]
    casos = [(f"alvo-{alvo}", "variar_alvo", alvo, REPETICOES, valores) for alvo in ALVOS]
    escrever_tsv(entradas, casos)

    medicoes = {}
    for linguagem, comando in (("cpp", compilar(args.cxx)), ("python", PYTHON)):
        saida = args.saida / f"alvo_{linguagem}.csv"
        subprocess.run([*comando, str(entradas), str(saida), "ambos"], check=True)
        medicoes[linguagem] = ler_csv(saida)
    verificar_respostas(medicoes, casos)
    print(f"{sum(map(len, medicoes.values()))} medições verificadas com n = {N} fixo.")


if __name__ == "__main__":
    main()
