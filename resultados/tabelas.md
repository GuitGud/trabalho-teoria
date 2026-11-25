**Tempo por chamada no cenário de melhor caso (média ± desvio padrão amostral, 15 amostras)**

| n | S | Força bruta, Python | Força bruta, C++ | PD, Python | PD, C++ |
|---:|---:|---:|---:|---:|---:|
| 8 | 161 | 473 ± 6,84 ns | 24,1 ± 1,01 ns | 21,2 ± 0,15 µs | 611 ± 8,61 ns |
| 10 | 201 | 520 ± 8,70 ns | 26,2 ± 0,32 ns | 34,0 ± 0,29 µs | 905 ± 13,9 ns |
| 12 | 241 | 575 ± 6,65 ns | 27,2 ± 0,39 ns | 52,8 ± 0,19 µs | 1,37 ± 0,02 µs |
| 15 | 301 | 624 ± 11,2 ns | 31,5 ± 1,19 ns | 91,2 ± 0,77 µs | 2,00 ± 0,02 µs |
| 18 | 361 | 685 ± 12,8 ns | 34,8 ± 0,53 ns | 147 ± 1,00 µs | 3,13 ± 0,03 µs |
| 22 | 441 | 756 ± 8,88 ns | 37,5 ± 0,77 ns | 229 ± 1,26 µs | 4,08 ± 0,13 µs |

**Tempo por chamada no cenário aleatório (média ± desvio padrão amostral, 15 amostras)**

| n | S | Força bruta, Python | Força bruta, C++ | PD, Python | PD, C++ |
|---:|---:|---:|---:|---:|---:|
| 8 | 161 | 67,5 ± 17,0 µs | 1,42 ± 0,36 µs | 24,1 ± 0,45 µs | 622 ± 26,1 ns |
| 10 | 201 | 295 ± 60,0 µs | 6,82 ± 1,48 µs | 38,7 ± 0,65 µs | 968 ± 41,4 ns |
| 12 | 241 | 1,34 ± 0,20 ms | 42,8 ± 11,5 µs | 57,4 ± 1,03 µs | 1,38 ± 0,04 µs |
| 15 | 301 | 10,5 ± 4,14 ms | 749 ± 326 µs | 98,7 ± 1,72 µs | 2,12 ± 0,06 µs |
| 18 | 361 | 93,3 ± 33,5 ms | 7,14 ± 2,55 ms | 153 ± 1,54 µs | 3,00 ± 0,08 µs |
| 22 | 441 | 1,48 ± 0,74 s | 101 ± 50,8 ms | 241 ± 4,29 µs | 4,36 ± 0,15 µs |

**Tempo por chamada no cenário de pior caso (média ± desvio padrão amostral, 15 amostras)**

| n | S | Força bruta, Python | Força bruta, C++ | PD, Python | PD, C++ |
|---:|---:|---:|---:|---:|---:|
| 8 | 161 | 74,3 ± 1,48 µs | 1,58 ± 0,04 µs | 22,3 ± 0,33 µs | 597 ± 6,00 ns |
| 10 | 201 | 323 ± 3,34 µs | 7,84 ± 0,08 µs | 36,4 ± 0,58 µs | 933 ± 8,33 ns |
| 12 | 241 | 1,44 ± 0,02 ms | 52,0 ± 4,72 µs | 52,9 ± 0,79 µs | 1,47 ± 0,03 µs |
| 15 | 301 | 13,0 ± 0,09 ms | 1,00 ± 0,07 ms | 91,4 ± 1,28 µs | 2,33 ± 0,02 µs |
| 18 | 361 | 121 ± 2,93 ms | 8,91 ± 0,14 ms | 141 ± 1,08 µs | 2,95 ± 0,05 µs |
| 22 | 441 | 2,16 ± 0,00 s | 145 ± 0,72 ms | 222 ± 6,18 µs | 4,32 ± 0,04 µs |

**Razão $T / f$ no pior caso, em ns por passo teórico ($f = n \cdot 2^n$ na força bruta e $f = (n + 1)(S + 1)$ na PD)**

| n | S | Força bruta, Python | Força bruta, C++ | PD, Python | PD, C++ |
|---:|---:|---:|---:|---:|---:|
| 8 | 161 | 36,3 | 0,77 | 15,3 | 0,41 |
| 10 | 201 | 31,5 | 0,77 | 16,4 | 0,42 |
| 12 | 241 | 29,3 | 1,06 | 16,8 | 0,47 |
| 15 | 301 | 26,5 | 2,04 | 18,9 | 0,48 |
| 18 | 361 | 25,6 | 1,89 | 20,5 | 0,43 |
| 22 | 441 | 23,4 | 1,57 | 21,8 | 0,42 |

**Custo por máscara no pior caso da força bruta, $T / 2^n$ em ns (as duas últimas linhas vêm da busca do limite de 60 s, com uma execução)**

| n | Python | C++ |
|---:|---:|---:|
| 8 | 290 | 6,16 |
| 10 | 315 | 7,66 |
| 12 | 352 | 12,7 |
| 15 | 398 | 30,6 |
| 18 | 461 | 34,0 |
| 22 | 516 | 34,6 |
| 26 | 606 |  |
| 30 |  | 36,9 |

Ajuste por mínimos quadrados do custo por máscara em Python, de n = 8 a 22: $T / 2^n \approx 153 + 16,6\,n$ ns, que prevê 585 ns em n = 26.

**Instâncias do cenário aleatório por tamanho: quantas têm soma total abaixo do alvo e quantas não têm solução**

| n | Instâncias | Soma total < S | Sem solução |
|---:|---:|---:|---:|
| 8 | 15 | 8 | 13 |
| 10 | 15 | 7 | 11 |
| 12 | 15 | 10 | 12 |
| 15 | 15 | 8 | 9 |
| 18 | 15 | 8 | 9 |
| 22 | 15 | 6 | 7 |

**Comparações no pior caso: quantas vezes um tempo médio é maior que o outro**

| n | Força bruta: Python / C++ | PD: Python / C++ | Python: força bruta / PD | C++: força bruta / PD |
|---:|---:|---:|---:|---:|
| 8 | 47,1 | 37,4 | 3,33 | 2,64 |
| 10 | 41,2 | 39,0 | 8,87 | 8,41 |
| 12 | 27,7 | 36,0 | 27,3 | 35,3 |
| 15 | 13,0 | 39,2 | 143 | 430 |
| 18 | 13,6 | 47,8 | 858 | 3.026 |
| 22 | 14,9 | 51,3 | 9.756 | 33.662 |

**Efeito do alvo com n = 13 fixo e instância sem solução (média ± desvio padrão amostral, 15 amostras)**

| S | Força bruta, Python | Força bruta, C++ | PD, Python | PD, C++ | PD Python: ns por passo | PD C++: ns por passo |
|---:|---:|---:|---:|---:|---:|---:|
| 65 | 3,07 ± 0,03 ms | 137 ± 9,23 µs | 12,3 ± 0,15 µs | 400 ± 6,19 ns | 13,3 | 0,43 |
| 257 | 3,05 ± 0,03 ms | 136 ± 9,50 µs | 61,8 ± 0,85 µs | 1,56 ± 0,04 µs | 17,1 | 0,43 |
| 1.025 | 3,05 ± 0,04 ms | 131 ± 0,73 µs | 312 ± 7,44 µs | 5,45 ± 0,04 µs | 21,7 | 0,38 |
| 4.097 | 3,06 ± 0,04 ms | 144 ± 15,4 µs | 1,35 ± 0,04 ms | 20,6 ± 0,10 µs | 23,5 | 0,36 |
| 16.385 | 3,05 ± 0,03 ms | 132 ± 18,0 µs | 5,14 ± 0,07 ms | 81,4 ± 1,10 µs | 22,4 | 0,35 |
| 65.537 | 3,07 ± 0,03 ms | 142 ± 1,65 µs | 20,9 ± 0,39 ms | 325 ± 5,85 µs | 22,8 | 0,35 |
| 262.145 | 3,08 ± 0,03 ms | 138 ± 4,07 µs | 82,1 ± 0,60 ms | 1,29 ± 0,01 ms | 22,4 | 0,35 |
| 1.048.577 | 3,06 ± 0,03 ms | 130 ± 3,45 µs | 328 ± 1,81 ms | 5,15 ± 0,02 ms | 22,4 | 0,35 |

**Maior n da força bruta que termina em até 60 s no pior caso (uma execução por n)**

| Linguagem | Maior n viável | Tempo medido | Primeiro n fora do limite |
|---:|---:|---:|---:|
| Python | 26 | 40,6 s | 27 |
| C++ | 30 | 39,6 s | 31 |

**Pico de memória auxiliar em bytes ao variar n, com S = 100 fixo (valores idênticos nas 15 repetições)**

| n | Teórico força bruta (n) | Teórico PD (S + 1) | Força bruta, Python | Força bruta, C++ | PD, Python | PD, C++ |
|---:|---:|---:|---:|---:|---:|---:|
| 16 | 16 | 101 | 233 | 16 | 302 | 101 |
| 64 | 64 | 101 | 281 | 64 | 302 | 101 |
| 256 | 256 | 101 | 473 | 256 | 302 | 101 |
| 1.024 | 1.024 | 101 | 1.269 | 1.024 | 302 | 101 |
| 4.096 | 4.096 | 101 | 4.341 | 4.096 | 302 | 101 |
| 16.384 | 16.384 | 101 | 16.629 | 16.384 | 302 | 101 |
| 65.536 | 65.536 | 101 | 65.781 | 65.536 | 302 | 101 |

**Pico de memória auxiliar em bytes ao variar S, com n = 13 fixo (valores idênticos nas 15 repetições)**

| S | Teórico força bruta (n) | Teórico PD (S + 1) | Força bruta, Python | Força bruta, C++ | PD, Python | PD, C++ |
|---:|---:|---:|---:|---:|---:|---:|
| 65 | 13 | 66 | 294 | 13 | 267 | 66 |
| 257 | 13 | 258 | 294 | 13 | 491 | 258 |
| 1.025 | 13 | 1.026 | 294 | 13 | 1.259 | 1.026 |
| 4.097 | 13 | 4.098 | 294 | 13 | 4.331 | 4.098 |
| 16.385 | 13 | 16.386 | 294 | 13 | 16.619 | 16.386 |
| 65.537 | 13 | 65.538 | 294 | 13 | 65.771 | 65.538 |
| 262.145 | 13 | 262.146 | 294 | 13 | 262.379 | 262.146 |
| 1.048.577 | 13 | 1.048.578 | 294 | 13 | 1.048.811 | 1.048.578 |
