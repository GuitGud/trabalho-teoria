# Subconjunto soma (Subset Sum)

**Teoria da Computação · Equipe 4 · Prof. Daniel Bezerra**

Israel Erlich, Luís Augusto, Theo Moura e Guilherme Rabelo  
Apresentação em 30/11/2026

O problema de decisão recebe uma lista de inteiros não negativos e um alvo e responde se alguma seleção de posições soma exatamente o alvo. Cada posição pode ser usada uma vez. Valores repetidos representam posições distintas e o subconjunto vazio soma zero.

| Algoritmo | Python | C++ | Tempo no pior caso | Espaço auxiliar |
| --- | --- | --- | --- | --- |
| Força bruta por máscaras | `src/subset_sum.py` | `src/subset_sum.cpp` | Θ(n · 2ⁿ) | Θ(n + 1) |
| Programação dinâmica em uma dimensão | `src/subset_sum.py` | `src/subset_sum.cpp` | Θ((n + 1)(S + 1)) | Θ(S + 1) |

Em força bruta com solução na primeira máscara possível, o melhor caso custa Θ(n + 1). A programação dinâmica visita toda a faixa de somas para cada item. Sua dependência do valor numérico de S caracteriza tempo pseudopolinomial.

## Contribuições e validação

As etapas atribuídas a cada integrante e os campos para registrar `VALIDADO` estão em [CONTRIBUICOES.md](CONTRIBUICOES.md). Cada integrante registra sua própria validação em commit.

## Relatório

O relatório da entrega está em [relatorio/relatorio.pdf](relatorio/relatorio.pdf). O texto fica em `relatorio/relatorio.md` e o PDF é gerado com Pandoc e XeLaTeX:

```bash
cd relatorio
pandoc metadados.yaml relatorio.md -o relatorio.pdf --pdf-engine=xelatex
```

## Reprodução

Use Python 3.10 ou superior e um compilador com suporte a C++17 no PATH (GCC ou Clang). Para usar outro executável, passe `--cxx caminho` aos scripts que compilam.

```bash
python -m pip install -r requirements.txt
python tests/testar.py
python scripts/medir.py
python scripts/variar_alvo.py
python scripts/medir_memoria.py
python scripts/limite.py
python scripts/analisar.py
```

O teste usa 172 entradas com respostas de um oráculo por combinações e compara as quatro implementações. O benchmark principal compila C++, gera `dados/entradas.tsv`, registra o ambiente e verifica todas as respostas com um oráculo independente. Para gerar só o TSV, rode `python scripts/gerar_entradas.py`. A busca da fronteira de 60 segundos se baseia nas medições principais e leva alguns minutos. `analisar.py` roda por último porque usa os resultados de todos os outros scripts.

### Execução avulsa

```bash
python src/executar.py dados/entradas.tsv python.csv ambos
g++ -std=c++17 -O2 -DNDEBUG -Wall -Wextra -pedantic src/subset_sum.cpp -o subset_sum
./subset_sum dados/entradas.tsv cpp.csv ambos
```

No PowerShell, compile com `-o subset_sum.exe` e execute `./subset_sum.exe`. O terceiro argumento pode ser `forca_bruta`, `pd` ou `ambos`. Um quarto argumento opcional escolhe a medida: `tempo` (padrão) ou `memoria`.

No modo `tempo`, a saída inclui o identificador do caso, o cenário, `n`, o alvo, o algoritmo, a repetição, a resposta (0 ou 1), o tempo médio por chamada em nanossegundos e o número de chamadas cronometradas juntas naquela amostra. No modo `memoria`, as duas últimas colunas são substituídas pelo pico de bytes alocados durante a chamada.

O formato TSV usa as colunas `caso`, `cenario`, `n`, `alvo`, `repeticoes` e `valores`. A última coluna contém os valores separados por espaço e fica vazia quando n = 0. A interface comum exige que a soma dos valores caiba em 63 bits não negativos e que a tabela caiba na memória disponível quando a PD for executada.

### Experimento

- Seis tamanhos em progressão aproximadamente geométrica, com n = 8, 10, 12, 15, 18, 22 e S = 20n + 1.
- Um caso de melhor e um de pior caso da força bruta para cada n, ambos com 15 amostras. As mesmas 15 entradas aleatórias por n são executadas uma vez por implementação. A semente principal é 20261123.
- A medição cobre a chamada de cada algoritmo, incluindo alocação das estruturas auxiliares. Cada execução lê o lote antes do cronômetro, aquece cada algoritmo por 500 ms e grava a resposta após a medição.
- Chamadas mais rápidas que 1 ms são cronometradas em lote: o número de chamadas dobra até o lote atingir pelo menos 1 ms, e a amostra registra o tempo do lote dividido pelo número de chamadas. Isso mantém as leituras acima da resolução do relógio. O lote de calibração é descartado, exceto quando uma única chamada dura 1 s ou mais: nesse caso ela já conta como a primeira amostra.
- `variar_alvo.py` mantém n = 13 e a lista fixa, com oito alvos ímpares de 65 a 1.048.577 (4ᵏ + 1). Isso isola o efeito de S.
- `medir_memoria.py` mede o pico de memória auxiliar em duas varreduras: n de 16 a 65.536 com S = 100 fixo, e S de 65 a 1.048.577 com n = 13 fixo. Em Python a leitura vem do `tracemalloc`. Em C++ vem de um alocador contador usado pelos vetores auxiliares dos dois algoritmos.
- `limite.py` consulta uma família de pior caso definida pelo mesmo prefixo de valores pares. Faz uma sondagem por n, marca tempos acima de 60 s e interrompe processos que superem 61,5 s de relógio externo.

## Resultados

| Arquivo | Conteúdo |
| --- | --- |
| `resultados/ambiente.json` | Hardware, sistema, versões, flags e relógios |
| `resultados/medicoes_*.csv` | 1.080 leituras do experimento principal |
| `resultados/alvo_*.csv` | 480 leituras com n fixo |
| `resultados/memoria_*.csv` | 900 leituras de pico de memória |
| `resultados/resumo.csv`, `resumo_alvo.csv` e `resumo_memoria.csv` | Médias e desvios padrão amostrais |
| `resultados/limite.csv` | Maior n observado dentro do orçamento em cada linguagem e sondagens vizinhas |
| `resultados/tabelas.md` | Tabelas de comparação usadas no relatório |
| `resultados/graficos/*.png` | Tempo nos três cenários, curva teórica, razão T/f, variação de S e memória |

![Pior caso: tempo medido, curva teórica e maior n viável em 60 s](resultados/graficos/tempos_pior_caso.png)

![Pico de memória auxiliar ao variar n e S](resultados/graficos/memoria.png)

## Referências

- BEZERRA, Daniel. *Teoria da Computação: Projeto de Complexidade*. Enunciado, 2026.
- MIT OpenCourseWare. *6.006 Introduction to Algorithms. Lecture 18: Pseudopolynomial*. 2020. [Notas de aula](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/f62798df9d8020e1c92130bd76a26f20_MIT6_006S20_lec18.pdf).
- MIT OpenCourseWare. *6.006 Introduction to Algorithms. Lecture 19: Complexity*. 2020. [Notas de aula](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/fda666a4db1dc65b3d71be08115502bd_MIT6_006S20_lec19.pdf).
- KARP, Richard M. *Reducibility Among Combinatorial Problems*. 1972, p. 85–103. [DOI](https://doi.org/10.1007/978-1-4684-2001-2_9).
