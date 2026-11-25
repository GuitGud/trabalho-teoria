"""Mede o pico de memória auxiliar dos dois algoritmos nas duas linguagens."""

import argparse
import os
import subprocess
from pathlib import Path

from gerar_entradas import RAIZ, casos_memoria, escrever_tsv
from medir import PYTHON, compilar, ler_csv, verificar_respostas


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cxx", default=os.getenv("CXX", "g++"))
    parser.add_argument("--dados", type=Path, default=RAIZ / "dados")
    parser.add_argument("--saida", type=Path, default=RAIZ / "resultados")
    args = parser.parse_args()
    args.saida.mkdir(parents=True, exist_ok=True)
    entradas = args.dados / "entradas_memoria.tsv"
    casos = list(casos_memoria())
    escrever_tsv(entradas, casos)

    medicoes = {}
    for linguagem, comando in (("cpp", compilar(args.cxx)), ("python", PYTHON)):
        saida = args.saida / f"memoria_{linguagem}.csv"
        print(f"Medindo memória em {linguagem}...", flush=True)
        subprocess.run([*comando, str(entradas), str(saida), "ambos", "memoria"], check=True)
        medicoes[linguagem] = ler_csv(saida)
    verificar_respostas(medicoes, casos)
    print(f"{sum(map(len, medicoes.values()))} leituras de memória verificadas em {len(casos)} entradas.")


if __name__ == "__main__":
    main()
