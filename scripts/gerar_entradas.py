"""Gera casos determinísticos para o estudo experimental de Subset Sum."""

import argparse
import csv
import random
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SEMENTE = 20261123
TAMANHOS = (8, 10, 12, 15, 18, 22)
REPETICOES = 15
N_ALVO = 13
ALVOS = tuple(4**k + 1 for k in range(3, 11))
TAMANHOS_MEMORIA = tuple(4**k for k in range(2, 9))
ALVO_MEMORIA = 100
CABECALHO = ("caso", "cenario", "n", "alvo", "repeticoes", "valores")


def alvo_para(n):
    return 20 * n + 1


def piores_valores(n, rng):
    return tuple(2 * rng.randint(11, 20) for _ in range(n))


def escrever_tsv(caminho, casos):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo, delimiter="\t", lineterminator="\n")
        escritor.writerow(CABECALHO)
        for identificador, cenario, alvo, repeticoes, valores in casos:
            escritor.writerow((
                identificador, cenario, len(valores), alvo, repeticoes,
                " ".join(map(str, valores)),
            ))


def casos_experimento():
    rng = random.Random(SEMENTE)
    for n in TAMANHOS:
        alvo = alvo_para(n)
        melhor = (alvo,) + tuple(rng.randint(1, 39) for _ in range(n - 1))
        yield f"n{n:02d}-melhor", "melhor", alvo, REPETICOES, melhor
        yield f"n{n:02d}-pior", "pior", alvo, REPETICOES, piores_valores(n, rng)
        for i in range(1, REPETICOES + 1):
            valores = tuple(rng.randint(1, 39) for _ in range(n))
            yield f"n{n:02d}-aleatorio-{i:02d}", "aleatorio", alvo, 1, valores


def caso_limite(n):
    rng = random.Random(SEMENTE + 1)
    return f"limite-{n}", "limite", alvo_para(n), 1, piores_valores(n, rng)


def casos_alvo(cenario="variar_alvo"):
    valores = caso_limite(N_ALVO)[4]
    for alvo in ALVOS:
        yield f"alvo-{alvo}", cenario, alvo, REPETICOES, valores


def casos_memoria():
    rng = random.Random(SEMENTE + 3)
    for n in TAMANHOS_MEMORIA:
        valores = (ALVO_MEMORIA,) + tuple(rng.randint(1, 39) for _ in range(n - 1))
        yield f"memoria-n{n}", "memoria_n", ALVO_MEMORIA, REPETICOES, valores
    yield from casos_alvo("memoria_s")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, default=RAIZ / "dados/entradas.tsv")
    args = parser.parse_args()
    escrever_tsv(args.saida, casos_experimento())
    print(f"Entradas gravadas em {args.saida}")


if __name__ == "__main__":
    main()
