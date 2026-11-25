"""Compila C++ e registra os tempos do experimento principal."""

import argparse
import csv
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import get_clock_info

from gerar_entradas import RAIZ, REPETICOES, SEMENTE, TAMANHOS, casos_experimento, escrever_tsv

FLAGS = ("-std=c++17", "-O2", "-DNDEBUG", "-Wall", "-Wextra", "-pedantic")
PYTHON = [sys.executable, str(RAIZ / "src/executar.py")]
EXECUTAVEL = RAIZ / "build" / ("subset_sum.exe" if os.name == "nt" else "subset_sum")


def compilar(compilador):
    EXECUTAVEL.parent.mkdir(exist_ok=True)
    subprocess.run(
        [compilador, *FLAGS, str(RAIZ / "src/subset_sum.cpp"), "-o", str(EXECUTAVEL)],
        check=True,
    )
    return [str(EXECUTAVEL)]


def nome_cpu():
    if os.name == "nt":
        import winreg

        subchave = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subchave) as chave:
            return winreg.QueryValueEx(chave, "ProcessorNameString")[0].strip()
    proc = Path("/proc/cpuinfo")
    if proc.is_file():
        for linha in proc.read_text(encoding="utf-8").splitlines():
            if linha.startswith("model name"):
                return linha.split(":", 1)[1].strip()
    if sys.platform == "darwin":
        return subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"], check=True, capture_output=True, text=True,
        ).stdout.strip()
    return platform.processor() or platform.machine()


def ram_bytes():
    if os.name == "nt":
        import ctypes

        class Memoria(ctypes.Structure):
            _fields_ = [("length", ctypes.c_uint32), ("load", ctypes.c_uint32)] + [
                (nome, ctypes.c_uint64) for nome in (
                    "total_phys", "avail_phys", "total_page", "avail_page",
                    "total_virtual", "avail_virtual", "avail_extended",
                )
            ]

        memoria = Memoria()
        memoria.length = ctypes.sizeof(memoria)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memoria)):
            return memoria.total_phys
        return None
    try:
        return os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    except (AttributeError, ValueError, OSError):
        return None


def registrar_ambiente(caminho, compilador):
    versao_cpp = subprocess.run(
        [compilador, "--version"], check=True, capture_output=True, text=True,
    ).stdout.splitlines()[0]
    ambiente = {
        "utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sistema": platform.platform(),
        "arquitetura": platform.machine(),
        "cpu": nome_cpu(),
        "processadores_logicos": os.cpu_count(),
        "ram_bytes": ram_bytes(),
        "python": f"{platform.python_implementation()} {platform.python_version()}",
        "flags_python": [],
        "compilador": versao_cpp,
        "flags_cpp": list(FLAGS),
        "relogios": {
            "python": "time.perf_counter_ns",
            "cpp": "QueryPerformanceCounter" if os.name == "nt" else "std::chrono::steady_clock",
            "resolucao_nominal_python_ns": get_clock_info("perf_counter").resolution * 1e9,
        },
        "n": TAMANHOS,
        "semente": SEMENTE,
        "repeticoes_por_grupo": REPETICOES,
        "aquecimento_ms_por_algoritmo": 500,
        "lote_minimo_ns": 1_000_000,
        "memoria": {
            "python": "tracemalloc, pico de bytes alocados durante a chamada",
            "cpp": "alocador contador nos vetores auxiliares, pico de bytes alocados durante a chamada",
        },
    }
    caminho.write_text(json.dumps(ambiente, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ler_csv(caminho):
    with caminho.open(encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def indexar_respostas(linhas):
    respostas = {}
    for linha in linhas:
        chave = (linha["caso"], linha["algoritmo"], int(linha["repeticao"]))
        if chave in respostas:
            raise ValueError(f"leitura duplicada: {chave}")
        respostas[chave] = int(linha["resposta"])
    return respostas


def verificar_respostas(dados, casos):
    esperadas = {}
    for identificador, _, alvo, repeticoes, valores in casos:
        # Oráculo independente baseado em operações sobre um conjunto de bits.
        faixa = (1 << (alvo + 1)) - 1
        somas = 1
        for valor in valores:
            if valor <= alvo:
                somas = (somas | somas << valor) & faixa
        resultado = somas >> alvo
        for algoritmo in ("forca_bruta", "pd"):
            for repeticao in range(1, repeticoes + 1):
                esperadas[(identificador, algoritmo, repeticao)] = resultado
    for linguagem, linhas in dados.items():
        if indexar_respostas(linhas) != esperadas:
            raise ValueError(f"respostas ausentes, excedentes ou divergentes em {linguagem}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cxx", default=os.getenv("CXX", "g++"), help="compilador C++17 (GCC ou Clang)")
    parser.add_argument("--dados", type=Path, default=RAIZ / "dados")
    parser.add_argument("--saida", type=Path, default=RAIZ / "resultados")
    args = parser.parse_args()
    args.saida.mkdir(parents=True, exist_ok=True)
    entradas = args.dados / "entradas.tsv"
    casos = list(casos_experimento())
    escrever_tsv(entradas, casos)
    comandos = {"cpp": compilar(args.cxx), "python": PYTHON}
    registrar_ambiente(args.saida / "ambiente.json", args.cxx)

    dados = {}
    for linguagem, comando in comandos.items():
        destino = args.saida / f"medicoes_{linguagem}.csv"
        print(f"Medindo {linguagem}...", flush=True)
        subprocess.run([*comando, str(entradas), str(destino), "ambos"], check=True)
        dados[linguagem] = ler_csv(destino)
    verificar_respostas(dados, casos)
    total = sum(map(len, dados.values()))
    print(f"{total} medições verificadas em {len(casos)} entradas.", flush=True)


if __name__ == "__main__":
    main()
