"""Resume as medições e produz tabelas e gráficos com Matplotlib."""

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from gerar_entradas import ALVO_MEMORIA, N_ALVO, RAIZ, REPETICOES, alvo_para
from medir import ler_csv

CORES = {"forca_bruta": "#A64428", "pd": "#006B67"}
TRACOS = {"python": ("-", "o"), "cpp": ("--", "D")}
NOMES = {"forca_bruta": "Força bruta", "pd": "PD", "python": "Python", "cpp": "C++"}
SERIES = [(algoritmo, linguagem) for algoritmo in CORES for linguagem in TRACOS]
CHAVE = ("cenario", "n", "alvo", "algoritmo", "linguagem")
CENARIOS = {"melhor": "melhor caso", "aleatorio": "aleatório", "pior": "pior caso"}
TITULOS = {"melhor": "de melhor caso", "aleatorio": "aleatório", "pior": "de pior caso"}
LIMITE_S = 60

plt.rcParams.update({
    "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#DDE5EE", "grid.linewidth": 0.6,
    "legend.frameon": False, "figure.dpi": 200, "savefig.bbox": "tight",
})


def agregar(pasta, prefixo, campo):
    leituras = defaultdict(list)
    for linguagem in ("python", "cpp"):
        for linha in ler_csv(pasta / f"{prefixo}_{linguagem}.csv"):
            chave = (linha["cenario"], int(linha["n"]), int(linha["alvo"]), linha["algoritmo"], linguagem)
            leituras[chave].append(float(linha[campo]))

    linhas = []
    for chave, medidas in sorted(leituras.items()):
        if len(medidas) != REPETICOES:
            raise ValueError(f"esperadas {REPETICOES} amostras em {chave}")
        linhas.append({
            **dict(zip(CHAVE, chave)), "amostras": len(medidas),
            "media": statistics.mean(medidas), "desvio": statistics.stdev(medidas),
        })
    return linhas


def escrever_csv(caminho, linhas, unidade):
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow((*CHAVE, "amostras", f"media_{unidade}", f"desvio_{unidade}"))
        for linha in linhas:
            escritor.writerow((*(linha[campo] for campo in CHAVE), linha["amostras"], linha["media"], linha["desvio"]))


def ler_limite(pasta):
    return [
        {"linguagem": linha["linguagem"], "n": int(linha["n"]), "status": linha["status"],
         "tempo_s": float(linha["tempo_s"]) if linha["tempo_s"] else None}
        for linha in ler_csv(pasta / "limite.csv")
    ]


def fronteira(limite):
    resultado = {}
    for linguagem in TRACOS:
        linhas = [linha for linha in limite if linha["linguagem"] == linguagem]
        viavel = max((linha for linha in linhas if linha["status"] == "viavel"), key=lambda linha: linha["n"])
        acima = min(linha["n"] for linha in linhas if linha["status"] != "viavel")
        resultado[linguagem] = (viavel, acima)
    return resultado


def passos(algoritmo, n, alvo):
    if algoritmo == "forca_bruta":
        return n * 2**n
    return (n + 1) * (alvo + 1)


def bytes_teoricos(algoritmo, n, alvo):
    return n if algoritmo == "forca_bruta" else alvo + 1


def serie(linhas, algoritmo, linguagem, cenario=None):
    return sorted(
        (linha for linha in linhas if linha["algoritmo"] == algoritmo and linha["linguagem"] == linguagem
         and cenario in (None, linha["cenario"])),
        key=lambda linha: (linha["n"], linha["alvo"]),
    )


def rotulo(algoritmo, linguagem):
    return f"{NOMES[algoritmo]}, {NOMES[linguagem]}"


def tracar(eixo, dados, eixo_x, algoritmo, linguagem, escala=1e-9, texto=None, **estilo):
    traco, marcador = TRACOS[linguagem]
    estilo = {"color": CORES[algoritmo], "linestyle": traco, "marker": marcador, **estilo}
    eixo.errorbar(
        [linha[eixo_x] for linha in dados], [linha["media"] * escala for linha in dados],
        yerr=[linha["desvio"] * escala for linha in dados], markersize=4, linewidth=1.4,
        capsize=2.5, label=texto or rotulo(algoritmo, linguagem), **estilo,
    )


def salvar(figura, destino, nome):
    figura.savefig(destino / f"{nome}.png")
    plt.close(figura)


def grafico_pior_caso(pior, limite, destino):
    figura, eixo = plt.subplots(figsize=(7, 4))
    viaveis = {linguagem: viavel for linguagem, (viavel, _) in fronteira(limite).items()}
    for algoritmo, linguagem in SERIES:
        dados = serie(pior, algoritmo, linguagem)
        tracar(eixo, dados, "n", algoritmo, linguagem)
        ultimo = dados[-1]
        fim = viaveis[linguagem]["n"] + 1 if algoritmo == "forca_bruta" else ultimo["n"]
        constante = ultimo["media"] * 1e-9 / passos(algoritmo, ultimo["n"], ultimo["alvo"])
        ns = range(dados[0]["n"], fim + 1)
        eixo.plot(ns, [constante * passos(algoritmo, n, alvo_para(n)) for n in ns],
                  color=CORES[algoritmo], linestyle=":", linewidth=0.9)
    for linguagem, linha in viaveis.items():
        eixo.plot(linha["n"], linha["tempo_s"], marker=TRACOS[linguagem][1], markersize=6,
                  markerfacecolor="white", color=CORES["forca_bruta"], linestyle="none")
        eixo.annotate(f"{NOMES[linguagem]}: n = {linha['n']}", (linha["n"], linha["tempo_s"]),
                      textcoords="offset points", xytext=(0, -15), ha="center", fontsize=8)
    eixo.plot([], [], marker="o", markersize=6, markerfacecolor="white", color=CORES["forca_bruta"],
              linestyle="none", label="Maior n viável em 60 s (1 execução)")
    eixo.axhline(LIMITE_S, color="#65748A", linewidth=0.8)
    eixo.annotate("limite de 60 s", (pior[0]["n"], LIMITE_S), textcoords="offset points",
                  xytext=(0, 4), fontsize=8, color="#65748A")
    eixo.plot([], [], color="#65748A", linestyle=":", linewidth=0.9, label="Curva teórica c · f(n)")
    eixo.set_yscale("log")
    eixo.set_ylim(top=LIMITE_S * 8)
    eixo.set_xlabel("n (itens), com S = 20n + 1")
    eixo.set_ylabel("Tempo médio por chamada (s)")
    eixo.set_title("Pior caso: tempo medido, curva teórica e maior n viável em 60 s", loc="left")
    eixo.legend(fontsize=8, loc="center left", bbox_to_anchor=(1.01, 0.5))
    salvar(figura, destino, "tempos_pior_caso")


def grafico_cenarios(principal, destino):
    figura, eixos = plt.subplots(1, 2, figsize=(9, 3.8), sharey=True)
    figura.suptitle("Tempo médio por cenário: melhor caso, aleatório e pior caso", x=0.07, ha="left", y=1.02, fontsize=11)
    marcadores = {"melhor": "v", "aleatorio": "s", "pior": "^"}
    for eixo, linguagem in zip(eixos, TRACOS):
        for cenario, nome in CENARIOS.items():
            tracar(eixo, serie(principal, "forca_bruta", linguagem, cenario), "n", "forca_bruta", linguagem,
                   texto=f"Força bruta, {nome}", marker=marcadores[cenario], linestyle="-",
                   alpha={"melhor": 0.55, "aleatorio": 0.8, "pior": 1}[cenario])
            tracar(eixo, serie(principal, "pd", linguagem, cenario), "n", "pd", linguagem,
                   texto=f"PD, {nome}", marker=marcadores[cenario], linestyle="-",
                   alpha={"melhor": 0.55, "aleatorio": 0.8, "pior": 1}[cenario])
        eixo.set_yscale("log")
        eixo.set_xlabel("n (itens), com S = 20n + 1")
        eixo.set_title(NOMES[linguagem], loc="left")
    eixos[0].set_ylabel("Tempo médio por chamada (s)")
    figura.legend(*eixos[1].get_legend_handles_labels(), fontsize=8, ncol=3,
                  loc="upper center", bbox_to_anchor=(0.5, 0.02))
    salvar(figura, destino, "cenarios")


def grafico_razao(pior, alvos, destino):
    figura, eixos = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
    for algoritmo, linguagem in SERIES:
        dados = serie(pior, algoritmo, linguagem)
        traco, marcador = TRACOS[linguagem]
        eixos[0].plot([linha["n"] for linha in dados],
                      [linha["media"] / passos(algoritmo, linha["n"], linha["alvo"]) for linha in dados],
                      color=CORES[algoritmo], linestyle=traco, marker=marcador, markersize=4,
                      label=rotulo(algoritmo, linguagem))
    for linguagem, (traco, marcador) in TRACOS.items():
        dados = serie(alvos, "pd", linguagem)
        eixos[1].plot([linha["alvo"] for linha in dados],
                      [linha["media"] / passos("pd", linha["n"], linha["alvo"]) for linha in dados],
                      color=CORES["pd"], linestyle=traco, marker=marcador, markersize=4,
                      label=rotulo("pd", linguagem))
    eixos[0].set_xlabel("n (pior caso, S = 20n + 1)")
    eixos[0].set_title("T / f, com f = n · 2ⁿ e f = (n + 1)(S + 1)", loc="left")
    eixos[1].set_xscale("log")
    eixos[1].set_xlabel(f"S (n = {N_ALVO} fixo)")
    eixos[1].set_title("T / ((n + 1)(S + 1)) da PD", loc="left")
    eixos[0].set_ylabel("ns por passo teórico")
    for eixo in eixos:
        eixo.set_yscale("log")
        eixo.legend(fontsize=8)
    salvar(figura, destino, "teoria_e_medicao")


def grafico_alvo(alvos, destino):
    figura, eixo = plt.subplots(figsize=(7, 4))
    for algoritmo, linguagem in SERIES:
        tracar(eixo, serie(alvos, algoritmo, linguagem), "alvo", algoritmo, linguagem)
    base = serie(alvos, "pd", "cpp")
    eixo.plot([linha["alvo"] for linha in base],
              [base[-1]["media"] * 1e-9 * linha["alvo"] / base[-1]["alvo"] for linha in base],
              color="#65748A", linestyle=":", linewidth=0.9, label="Inclinação 1 (linear em S)")
    eixo.set_xscale("log")
    eixo.set_yscale("log")
    eixo.set_xlabel(f"S (alvo), com n = {N_ALVO} fixo e instância sem solução")
    eixo.set_ylabel("Tempo médio por chamada (s)")
    eixo.set_title("Efeito do alvo: a PD cresce com S, a força bruta não", loc="left")
    eixo.legend(ncol=2, fontsize=8)
    salvar(figura, destino, "efeito_do_alvo")


def grafico_memoria(memoria, destino):
    figura, eixos = plt.subplots(1, 2, figsize=(9, 3.8), sharey=True)
    paineis = (
        ("memoria_n", "n", f"n (itens), com S = {ALVO_MEMORIA} fixo"),
        ("memoria_s", "alvo", f"S (alvo), com n = {N_ALVO} fixo"),
    )
    for eixo, (cenario, eixo_x, legenda) in zip(eixos, paineis):
        for algoritmo, linguagem in SERIES:
            dados = serie(memoria, algoritmo, linguagem, cenario)
            tracar(eixo, dados, eixo_x, algoritmo, linguagem, escala=1)
            if linguagem == "cpp":
                eixo.plot([linha[eixo_x] for linha in dados],
                          [bytes_teoricos(algoritmo, linha["n"], linha["alvo"]) for linha in dados],
                          color="#223047", linestyle=":", linewidth=1.1, zorder=4)
        eixo.set_xscale("log")
        eixo.set_yscale("log")
        eixo.set_xlabel(legenda)
    eixos[0].plot([], [], color="#223047", linestyle=":", linewidth=1.1, label="Teórico: n bytes e S + 1 bytes (coincide com C++)")
    eixos[0].set_ylim(bottom=8)
    eixos[0].set_ylabel("Pico de memória auxiliar (bytes)")
    eixos[0].set_title("Memória ao variar n", loc="left")
    eixos[1].set_title("Memória ao variar S", loc="left")
    eixos[0].legend(fontsize=8)
    salvar(figura, destino, "memoria")


def pt(valor):
    if abs(valor) >= 1000:
        return inteiro(valor)
    casas = 2 if abs(valor) < 10 else 1 if abs(valor) < 100 else 0
    return f"{valor:.{casas}f}".replace(".", ",")


def inteiro(valor):
    return f"{valor:,.0f}".replace(",", ".")


def tempo(linha):
    media = linha["media"]
    fator, unidade = next(
        (fator, unidade) for limite, fator, unidade in
        ((1e3, 1, "ns"), (1e6, 1e3, "µs"), (1e9, 1e6, "ms"), (float("inf"), 1e9, "s"))
        if media < limite
    )
    return f"{pt(media / fator)} ± {pt(linha['desvio'] / fator)} {unidade}"


def tabela(titulo, cabecalho, linhas):
    partes = [f"**{titulo}**", "", "| " + " | ".join(cabecalho) + " |",
              "|" + "|".join(["---:"] * len(cabecalho)) + "|"]
    partes += ["| " + " | ".join(map(str, linha)) + " |" for linha in linhas]
    return "\n".join(partes) + "\n"


def indice(linhas):
    return {tuple(linha[campo] for campo in CHAVE): linha for linha in linhas}


def instancias_aleatorias(pasta, dados):
    respostas = {
        linha["caso"]: linha["resposta"] for linha in ler_csv(pasta / "medicoes_cpp.csv")
        if linha["algoritmo"] == "pd"
    }
    contagem = defaultdict(lambda: [0, 0, 0])
    with (dados / "entradas.tsv").open(encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo, delimiter="\t"):
            if linha["cenario"] == "aleatorio":
                grupo = contagem[int(linha["n"])]
                grupo[0] += 1
                grupo[1] += sum(map(int, linha["valores"].split())) < int(linha["alvo"])
                grupo[2] += respostas[linha["caso"]] == "0"
    return sorted(contagem.items())


def escrever_tabelas(caminho, principal, alvos, memoria, limite, aleatorias):
    por_chave = indice(principal + alvos + memoria)
    tamanhos = sorted({(linha["n"], linha["alvo"]) for linha in principal})
    series = [rotulo(*item) for item in SERIES]
    blocos = []

    for cenario, nome in TITULOS.items():
        blocos.append(tabela(
            f"Tempo por chamada no cenário {nome} (média ± desvio padrão amostral, {REPETICOES} amostras)",
            ("n", "S", *series),
            [(n, alvo, *(tempo(por_chave[cenario, n, alvo, a, l]) for a, l in SERIES)) for n, alvo in tamanhos],
        ))

    blocos.append(tabela(
        "Razão $T / f$ no pior caso, em ns por passo teórico ($f = n \\cdot 2^n$ na força bruta e $f = (n + 1)(S + 1)$ na PD)",
        ("n", "S", *series),
        [(n, alvo, *(pt(por_chave["pior", n, alvo, a, l]["media"] / passos(a, n, alvo)) for a, l in SERIES))
         for n, alvo in tamanhos],
    ))

    limites = fronteira(limite)
    viaveis = {linguagem: viavel for linguagem, (viavel, _) in limites.items()}
    blocos.append(tabela(
        "Custo por máscara no pior caso da força bruta, $T / 2^n$ em ns (as duas últimas linhas vêm da busca do limite de 60 s, com uma execução)",
        ("n", "Python", "C++"),
        [(n, *(pt(por_chave["pior", n, alvo, "forca_bruta", l]["media"] / 2**n) for l in TRACOS))
         for n, alvo in tamanhos]
        + [(linha["n"], *(pt(linha["tempo_s"] * 1e9 / 2**linha["n"]) if l == linguagem else "" for l in TRACOS))
           for linguagem, linha in sorted(viaveis.items(), key=lambda item: item[1]["n"])],
    ))

    ns = [n for n, _ in tamanhos]
    inclinacao, intercepto = statistics.linear_regression(
        ns, [por_chave["pior", n, alvo, "forca_bruta", "python"]["media"] / 2**n for n, alvo in tamanhos])
    blocos.append(
        f"Ajuste por mínimos quadrados do custo por máscara em Python, de n = {ns[0]} a {ns[-1]}: "
        f"$T / 2^n \\approx {pt(intercepto)} + {pt(inclinacao)}\\,n$ ns, que prevê "
        f"{pt(intercepto + inclinacao * viaveis['python']['n'])} ns em n = {viaveis['python']['n']}.\n"
    )
    blocos.append(tabela(
        "Instâncias do cenário aleatório por tamanho: quantas têm soma total abaixo do alvo e quantas não têm solução",
        ("n", "Instâncias", "Soma total < S", "Sem solução"),
        [(n, *grupo) for n, grupo in aleatorias],
    ))

    def razao(n, alvo, numerador, denominador):
        return pt(por_chave[("pior", n, alvo, *numerador)]["media"] / por_chave[("pior", n, alvo, *denominador)]["media"])

    blocos.append(tabela(
        "Comparações no pior caso: quantas vezes um tempo médio é maior que o outro",
        ("n", "Força bruta: Python / C++", "PD: Python / C++", "Python: força bruta / PD", "C++: força bruta / PD"),
        [(n, razao(n, alvo, ("forca_bruta", "python"), ("forca_bruta", "cpp")),
          razao(n, alvo, ("pd", "python"), ("pd", "cpp")),
          razao(n, alvo, ("forca_bruta", "python"), ("pd", "python")),
          razao(n, alvo, ("forca_bruta", "cpp"), ("pd", "cpp"))) for n, alvo in tamanhos],
    ))

    lista_alvos = sorted({linha["alvo"] for linha in alvos})
    blocos.append(tabela(
        f"Efeito do alvo com n = {N_ALVO} fixo e instância sem solução (média ± desvio padrão amostral, {REPETICOES} amostras)",
        ("S", *series, "PD Python: ns por passo", "PD C++: ns por passo"),
        [(inteiro(alvo), *(tempo(por_chave["variar_alvo", N_ALVO, alvo, a, l]) for a, l in SERIES),
          *(pt(por_chave["variar_alvo", N_ALVO, alvo, "pd", l]["media"] / passos("pd", N_ALVO, alvo)) for l in TRACOS))
         for alvo in lista_alvos],
    ))

    blocos.append(tabela(
        "Maior n da força bruta que termina em até 60 s no pior caso (uma execução por n)",
        ("Linguagem", "Maior n viável", "Tempo medido", "Primeiro n fora do limite"),
        [(NOMES[linguagem], viavel["n"], f"{pt(viavel['tempo_s'])} s", acima)
         for linguagem, (viavel, acima) in limites.items()],
    ))

    def pico(cenario, n, alvo):
        return [inteiro(por_chave[cenario, n, alvo, a, l]["media"]) for a, l in SERIES]

    constante = all(linha["desvio"] == 0 for linha in memoria)
    nota = f"valores idênticos nas {REPETICOES} repetições" if constante else f"média de {REPETICOES} amostras"
    blocos.append(tabela(
        f"Pico de memória auxiliar em bytes ao variar n, com S = {ALVO_MEMORIA} fixo ({nota})",
        ("n", "Teórico força bruta (n)", "Teórico PD (S + 1)", *series),
        [(inteiro(n), inteiro(n), inteiro(ALVO_MEMORIA + 1), *pico("memoria_n", n, ALVO_MEMORIA))
         for n in sorted({linha["n"] for linha in memoria if linha["cenario"] == "memoria_n"})],
    ))
    blocos.append(tabela(
        f"Pico de memória auxiliar em bytes ao variar S, com n = {N_ALVO} fixo ({nota})",
        ("S", "Teórico força bruta (n)", "Teórico PD (S + 1)", *series),
        [(inteiro(alvo), N_ALVO, inteiro(alvo + 1), *pico("memoria_s", N_ALVO, alvo))
         for alvo in sorted({linha["alvo"] for linha in memoria if linha["cenario"] == "memoria_s"})],
    ))
    caminho.write_text("\n".join(blocos), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resultados", type=Path, default=RAIZ / "resultados")
    parser.add_argument("--dados", type=Path, default=RAIZ / "dados")
    args = parser.parse_args()
    pasta = args.resultados
    principal = agregar(pasta, "medicoes", "tempo_ns")
    alvos = agregar(pasta, "alvo", "tempo_ns")
    memoria = agregar(pasta, "memoria", "pico_bytes")
    limite = ler_limite(pasta)
    escrever_csv(pasta / "resumo.csv", principal, "ns")
    escrever_csv(pasta / "resumo_alvo.csv", alvos, "ns")
    escrever_csv(pasta / "resumo_memoria.csv", memoria, "bytes")
    escrever_tabelas(pasta / "tabelas.md", principal, alvos, memoria, limite, instancias_aleatorias(pasta, args.dados))

    destino = pasta / "graficos"
    destino.mkdir(exist_ok=True)
    pior = [linha for linha in principal if linha["cenario"] == "pior"]
    grafico_pior_caso(pior, limite, destino)
    grafico_cenarios(principal, destino)
    grafico_razao(pior, alvos, destino)
    grafico_alvo(alvos, destino)
    grafico_memoria(memoria, destino)
    print(f"{len(principal)} grupos principais, {len(alvos)} de alvo, {len(memoria)} de memória, "
          "5 gráficos e 11 tabelas gravados.")


if __name__ == "__main__":
    main()
