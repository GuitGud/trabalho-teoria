"""Verifica a fronteira de 60 segundos da força bruta em uma família de pior caso."""

import argparse
import csv
import os
import statistics
import subprocess
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory

from gerar_entradas import RAIZ, TAMANHOS, caso_limite, escrever_tsv
from medir import PYTHON, compilar, ler_csv

LIMITE_S = 60
TOLERANCIA_PROCESSO_S = 1.5
CAMPOS = ("linguagem", "n", "alvo", "status", "tempo_s", "limite_s")


def estimar_n(base, tempo_base):
    n = base
    while tempo_base * (n / base) * 2 ** (n - base) <= LIMITE_S:
        n += 1
    return n - 1


def medir_ponto(linguagem, comando, n, diretorio):
    entrada = diretorio / "limite.tsv"
    saida = diretorio / "limite.csv"
    caso = caso_limite(n)
    escrever_tsv(entrada, [caso])
    try:
        subprocess.run(
            [*comando, str(entrada), str(saida), "forca_bruta"],
            check=True, timeout=LIMITE_S + TOLERANCIA_PROCESSO_S,
        )
    except subprocess.TimeoutExpired:
        tempo = None
        status = "interrompido"
    else:
        linha, = ler_csv(saida)
        if linha["caso"] != caso[0] or linha["resposta"] != "0":
            raise ValueError(f"resultado inesperado no caso {caso[0]} em {linguagem}")
        tempo = int(linha["tempo_ns"]) / 1e9
        status = "viavel" if tempo <= LIMITE_S else "acima"
    return {
        "linguagem": linguagem, "n": n, "alvo": caso[2], "status": status,
        "tempo_s": "" if tempo is None else f"{tempo:.9f}", "limite_s": LIMITE_S,
    }


def localizar_fronteira(linguagem, comando, estimativa, pasta, escritor, arquivo):
    sondagens = {}

    def sondar(n):
        if n not in sondagens:
            print(f"Limite {linguagem}: n={n}...", flush=True)
            linha = medir_ponto(linguagem, comando, n, pasta)
            sondagens[n] = linha["status"] == "viavel"
            escritor.writerow(linha)
            arquivo.flush()
            print(f"  {linha['status']} {linha['tempo_s']}", flush=True)
        return sondagens[n]

    n = max(1, estimativa)
    if sondar(n):
        while sondar(n + 1):
            n += 1
    else:
        while n > 0 and not sondar(n):
            n -= 1
    print(f"Fronteira observada de {linguagem}: {n} / {n + 1}.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cxx", default=os.getenv("CXX", "g++"))
    parser.add_argument("--resultados", type=Path, default=RAIZ / "resultados")
    parser.add_argument("--linguagem", choices=("ambas", "python", "cpp"), default="ambas")
    args = parser.parse_args()
    linguagens = ("python", "cpp") if args.linguagem == "ambas" else (args.linguagem,)
    comandos = {"python": PYTHON}
    if "cpp" in linguagens:
        comandos["cpp"] = compilar(args.cxx)
    base = max(TAMANHOS)
    estimativas = defaultdict(int)
    for linguagem in linguagens:
        linhas = ler_csv(args.resultados / f"medicoes_{linguagem}.csv")
        tempos = [
            int(linha["tempo_ns"]) / 1e9 for linha in linhas
            if linha["algoritmo"] == "forca_bruta" and linha["cenario"] == "pior" and int(linha["n"]) == base
        ]
        estimativas[linguagem] = estimar_n(base, statistics.median(tempos))

    nome = "limite.csv" if args.linguagem == "ambas" else f"limite_{args.linguagem}.csv"
    with TemporaryDirectory(prefix="subset-sum-") as temp:
        with (args.resultados / nome).open("w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS)
            escritor.writeheader()
            for linguagem in linguagens:
                localizar_fronteira(
                    linguagem, comandos[linguagem], estimativas[linguagem],
                    Path(temp), escritor, arquivo,
                )


if __name__ == "__main__":
    main()
