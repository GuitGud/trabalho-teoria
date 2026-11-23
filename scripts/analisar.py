"""Resume as medi��es e produz gr�ficos vetoriais com ReportLab."""

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

from reportlab.graphics import renderSVG
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing, Line, String
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib.colors import HexColor

from gerar_entradas import RAIZ, REPETICOES
from medir import ler_csv

SERIES = (
    ("forca_bruta", "python", "For�a bruta, Python", "#A64428"),
    ("forca_bruta", "cpp", "For�a bruta, C++", "#A64428"),
    ("pd", "python", "PD, Python", "#006B67"),
    ("pd", "cpp", "PD, C++", "#006B67"),
)
CAMPOS = ("cenario", "n", "alvo", "algoritmo", "linguagem", "amostras", "media_ns", "desvio_ns")
TEXTO = HexColor("#223047")
GRADE = HexColor("#DDE5EE")
EIXO = HexColor("#65748A")


def agregar(pasta, prefixo):
    tempos = defaultdict(list)
    for linguagem in ("python", "cpp"):
        for linha in ler_csv(pasta / f"{prefixo}_{linguagem}.csv"):
            chave = (linha["cenario"], int(linha["n"]), int(linha["alvo"]), linha["algoritmo"], linguagem)
            tempos[chave].append(int(linha["tempo_ns"]))

    linhas = []
    for chave, medidas in sorted(tempos.items()):
        if len(medidas) != REPETICOES:
            raise ValueError(f"esperadas {REPETICOES} amostras em {chave}")
        linhas.append(dict(zip(CAMPOS, (*chave, len(medidas), statistics.mean(medidas), statistics.stdev(medidas)))))
    return linhas


def funcao_teorica(algoritmo, n, alvo):
    if algoritmo == "forca_bruta":
        return n * 2**n
    return (n + 1) * (alvo + 1)


def curvas(linhas, eixo_x, normalizar=False):
    resultado = []
    for algoritmo, linguagem, _, _ in SERIES:
        dados = sorted(
            (linha for linha in linhas if linha["algoritmo"] == algoritmo and linha["linguagem"] == linguagem),
            key=lambda linha: linha[eixo_x],
        )
        if normalizar:
            razoes = [linha["media_ns"] / funcao_teorica(algoritmo, linha["n"], linha["alvo"])
                      for linha in dados]
            ordenadas = [razao / razoes[-1] for razao in razoes]
        else:
            ordenadas = [math.log10(linha["media_ns"] / 1000) for linha in dados]
        resultado.append([(math.log2(linha[eixo_x]), y) for linha, y in zip(dados, ordenadas)])
    return resultado


def pt(texto):
    return str(texto).replace(".", ",")


def grafico(linhas, eixo_x, normalizar=False):
    largura, altura = 486, 224
    desenho = Drawing(largura, altura)
    plot = LinePlot()
    plot.x, plot.y, plot.width, plot.height = 49, 49, 416, 140
    plot.data = curvas(linhas, eixo_x, normalizar)
    xs = [x for x, _ in plot.data[0]]
    ys = [y for curva in plot.data for _, y in curva]
    plot.xValueAxis.valueMin, plot.xValueAxis.valueMax = xs[0] - 0.075, xs[-1] + 0.075
    plot.xValueAxis.valueSteps = xs
    plot.xValueAxis.labelTextFormat = lambda x: str(round(2**x))
    plot.xValueAxis.labels.dy = -6
    if normalizar:
        passo = 0.5 if max(ys) - min(ys) < 3 else 1
        abaixo = math.floor((min(ys) - 0.04) / passo)
        acima = math.ceil((max(ys) + 0.04) / passo)
        ticks = [i * passo for i in range(abaixo, acima + 1)]
        plot.yValueAxis.labelTextFormat = lambda y: pt(f"{y:g}")
    else:
        ticks = list(range(math.floor(min(ys)), math.ceil(max(ys)) + 1))
        plot.yValueAxis.labelTextFormat = lambda y: pt(f"{10**y:g}")
    plot.yValueAxis.valueMin, plot.yValueAxis.valueMax = ticks[0], ticks[-1]
    plot.yValueAxis.valueSteps = ticks
    plot.yValueAxis.labels.dx = -5
    plot.yValueAxis.visibleGrid = True
    plot.yValueAxis.gridStrokeColor = GRADE
    plot.yValueAxis.gridStrokeWidth = 0.6
    for eixo in (plot.xValueAxis, plot.yValueAxis):
        eixo.strokeColor = EIXO
        eixo.strokeWidth = 0.75
        eixo.labels.fillColor = TEXTO
        eixo.labels.fontName = "Helvetica"
        eixo.labels.fontSize = 8.2

    for i, (_, linguagem, rotulo, cor_hex) in enumerate(SERIES):
        cor = HexColor(cor_hex)
        estilo = plot.lines[i]
        estilo.strokeColor, estilo.strokeWidth = cor, 1.65
        estilo.strokeDashArray = None if linguagem == "python" else [4, 2.5]
        estilo.symbol = makeMarker("FilledCircle" if linguagem == "python" else "FilledDiamond")
        estilo.symbol.size = 4.2
        estilo.symbol.fillColor = estilo.symbol.strokeColor = cor

        x, y = (26, 154, 282, 387)[i], 9
        desenho.add(Line(x, y + 3, x + 18, y + 3, strokeColor=cor,
                         strokeWidth=1.6, strokeDashArray=estilo.strokeDashArray))
        desenho.add(String(x + 23, y, rotulo, fontSize=8.5, fillColor=TEXTO))

    desenho.add(plot)
    desenho.add(String(49, 204, "Raz�o normalizada (n = 19: 1)" if normalizar else "Tempo m�dio (�s, escala logar�tmica)",
                       fontName="Helvetica-Bold", fontSize=9, fillColor=TEXTO))
    rotulo_x = "n (escala logar�tmica)" if eixo_x == "n" else "S (escala logar�tmica)"
    desenho.add(String(257, 21, rotulo_x, textAnchor="middle", fontSize=8.5, fillColor=TEXTO))
    return desenho


def escrever_csv(caminho, linhas):
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(linhas)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resultados", type=Path, default=RAIZ / "resultados")
    args = parser.parse_args()
    pasta = args.resultados
    principal = agregar(pasta, "medicoes")
    contraste_alvo = agregar(pasta, "alvo")
    escrever_csv(pasta / "resumo.csv", principal)
    escrever_csv(pasta / "resumo_alvo.csv", contraste_alvo)
    pior = [linha for linha in principal if linha["cenario"] == "pior"]
    graficos = {
        "tempos_pior_caso": grafico(pior, "n"),
        "teoria_e_medicao": grafico(pior, "n", normalizar=True),
        "efeito_do_alvo": grafico(contraste_alvo, "alvo"),
    }
    destino = pasta / "graficos"
    destino.mkdir(exist_ok=True)
    for nome, desenho in graficos.items():
        renderSVG.drawToFile(desenho, str(destino / f"{nome}.svg"))
    print(f"{len(principal)} grupos principais, {len(contraste_alvo)} grupos de alvos e {len(graficos)} gr�ficos gravados.")


if __name__ == "__main__":
    main()
