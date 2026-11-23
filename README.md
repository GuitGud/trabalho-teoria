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

## Reprodução

Use Python 3.10 ou superior e GCC/G++ com suporte a C++17 no PATH. Para usar outro executável G++, passe `--cxx caminho` aos scripts que compilam.

```bash
python -m pip install -r requirements.txt
python tests/testar.py
python scripts/medir.py
python scripts/variar_alvo.py
python scripts/analisar.py
python scripts/limite.py
```

O teste usa 172 entradas com respostas de um oráculo por combinações e compara as quatro implementações. O benchmark principal compila C++, gera `dados/entradas.tsv`, registra o ambiente e verifica todas as respostas com um oráculo independente. Para gerar só o TSV, rode `python scripts/gerar_entradas.py`. A busca da fronteira de 60 segundos se baseia nas medições principais e pode levar alguns minutos.

### Execução avulsa

```bash
python src/executar.py dados/entradas.tsv python.csv ambos
g++ -std=c++17 -O2 -DNDEBUG -Wall -Wextra -pedantic src/subset_sum.cpp -o subset_sum
./subset_sum dados/entradas.tsv cpp.csv ambos
```

No PowerShell, compile com `-o subset_sum.exe` e execute `./subset_sum.exe`. A última opção pode ser `forca_bruta`, `pd` ou `ambos`. A saída inclui o identificador do caso, o algoritmo, a repetição, a resposta (0 ou 1) e a duração em nanossegundos. O formato TSV usa as colunas `caso`, `cenario`, `n`, `alvo`, `repeticoes` e `valores`. A última coluna contém os valores separados por espaço e fica vazia quando n = 0. A interface comum exige que a soma dos valores caiba em 63 bits não negativos e que a tabela caiba na memória disponível quando a PD for executada.

### Experimento

- Seis tamanhos em progressão aproximadamente geométrica, com n = 3, 4, 6, 9, 13, 19 e S = 20n + 1.
- Um caso de melhor e um de pior caso da força bruta para cada n, ambos executados 15 vezes. As mesmas 15 entradas aleatórias por n são executadas uma vez por implementação. A semente principal é 20261123.
- A medição cobre a chamada de cada algoritmo, incluindo alocação das estruturas auxiliares. Cada execução lê o lote antes do cronômetro, faz cinco rodadas curtas por algoritmo e grava a resposta após a medição.
- `variar_alvo.py` mantém n = 13 e a lista fixa, alternando entre oito alvos ímpares. Isso isola o efeito de S.
- `limite.py` consulta uma família de pior caso definida pelo mesmo prefixo de valores pares. Faz uma sondagem por n, marca tempos acima de 60 s e interrompe processos que superem 61,5 s de relógio externo.

## Resultados

| Arquivo | Conteúdo |
| --- | --- |
| `resultados/ambiente.json` | Hardware, sistema, versões, flags e relógios |
| `resultados/medicoes_*.csv` | 1.080 leituras do experimento principal |
| `resultados/alvo_*.csv` | 480 leituras com n fixo |
| `resultados/resumo.csv` e `resultados/resumo_alvo.csv` | Médias e desvios padrão amostrais em nanossegundos |
| `resultados/limite.csv` | Maior n observado dentro do orçamento em cada linguagem e sondagens vizinhas |
| `resultados/graficos/*.svg` | Comparações do tempo, da curva teórica e da variação de S |

![Tempos médios no pior caso em escala logarítmica](resultados/graficos/tempos_pior_caso.svg)

## Referências

- BEZERRA, Daniel. *Teoria da Computação — Projeto de Complexidade*. Enunciado, 2026.
- MIT OpenCourseWare. *6.006 Introduction to Algorithms. Lecture 18: Pseudopolynomial*. 2020. [Notas de aula](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/f62798df9d8020e1c92130bd76a26f20_MIT6_006S20_lec18.pdf).
- MIT OpenCourseWare. *6.006 Introduction to Algorithms. Lecture 19: Complexity*. 2020. [Notas de aula](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/fda666a4db1dc65b3d71be08115502bd_MIT6_006S20_lec19.pdf).
- KARP, Richard M. *Reducibility Among Combinatorial Problems*. 1972, p. 85–103. [DOI](https://doi.org/10.1007/978-1-4684-2001-2_9).
