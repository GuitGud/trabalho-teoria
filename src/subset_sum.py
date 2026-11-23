"""Algoritmos de decisão para Subset Sum com inteiros não negativos."""

from collections.abc import Sequence


def forca_bruta(valores: Sequence[int], alvo: int) -> bool:
    """Enumera máscaras em ordem binária e recalcula a soma de cada uma."""
    n = len(valores)
    mascara = bytearray(n)

    while True:
        soma = 0
        for escolhido, valor in zip(mascara, valores):
            if escolhido:
                soma += valor
        if soma == alvo:
            return True

        i = 0
        while i < n and mascara[i]:
            mascara[i] = 0
            i += 1
        if i == n:
            return False
        mascara[i] = 1


def programacao_dinamica(valores: Sequence[int], alvo: int) -> bool:
    """Atualiza a tabela de somas alcançáveis de trás para frente."""
    alcancavel = bytearray(alvo + 1)
    alcancavel[0] = 1

    for valor in valores:
        for soma in range(alvo, -1, -1):
            if soma >= valor and alcancavel[soma - valor]:
                alcancavel[soma] = 1

    return bool(alcancavel[alvo])
