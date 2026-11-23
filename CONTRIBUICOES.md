# Contribuições e validação da Equipe 4

Cada integrante deve conferir as etapas atribuídas ao seu nome, escrever `VALIDADO` na célula correspondente da coluna **Status** e registrar a alteração em um commit com sua própria conta. Deixe a célula em branco enquanto a etapa estiver pendente. Atualize sua cópia da branch antes de editar.

## Israel Erlich · Definição e força bruta

| Etapa | O que conferir | Status |
| --- | --- | --- |
| Enunciado e domínio | Inteiros não negativos, uso único de cada posição e resposta SIM ou NÃO. | |
| Exemplo à mão | Enumeração das máscaras até encontrar 5 + 9 = 14 para [3, 5, 9, 12]. | |
| Código e testes | Ordem das máscaras em Python e C++. Rode `python tests/testar.py` e confira as 688 decisões. | |
| Melhor e pior caso | Alvo no primeiro item e instância sem solução com valores pares e alvo ímpar. | |
| Apresentação | Ensaio dos slides 1 a 3, previstos para 1 min 31 s. | |

## Luís Augusto · Programação dinâmica e análise

| Etapa | O que conferir | Status |
| --- | --- | --- |
| Recorrência | Casos com e sem o item, caso-base e estado de resposta. | |
| Ordem de atualização | Simule [4] com alvo 8 e confira que a atualização decrescente impede reutilizar o item. | |
| Exemplo do slide | Confira que a soma 5 já era alcançável quando o item 9 permitiu marcar a soma 14. | |
| Tempo e espaço | Limites assintóticos do relatório e vetor com S + 1 estados. | |
| Apresentação | Ensaio dos slides 4 e 5, previstos para 1 min 33 s. | |

## Theo Moura · Medições e interpretação

| Etapa | O que conferir | Status |
| --- | --- | --- |
| Dados e testes | Semente 20261123, tamanhos das entradas, 1.080 medições principais e 480 com tamanho fixo. | |
| Reprodução | Rode `python scripts/medir.py` e `python scripts/variar_alvo.py` em uma cópia e compare as respostas. | |
| Tabelas e gráficos | Recalcule média e desvio amostral para um grupo com n = 19 e confira o relatório e o slide 7. | |
| Fronteira de 60 segundos | Confira em `resultados/limite.csv` os limites de 25 itens em Python e 29 em C++ e as sondagens seguintes. | |
| Apresentação | Ensaio dos slides 6 a 8, previstos para 2 min 6 s. | |

## Guilherme Rabelo · Complexidade e entrega

| Etapa | O que conferir | Status |
| --- | --- | --- |
| P e NP | Certificado, NP-dureza e dependência pseudopolinomial do alvo. | |
| Redução para Partição | Confira o exemplo com dois grupos de soma 15 e os casos S > W e x = 0. | |
| Relatório | Confira os itens do enunciado, os nomes, a declaração e o link do código. | |
| GitHub e entrega | Confira README, testes e resultados. Verifique se o professor tem acesso ao repositório privado. | |
| Apresentação | Ensaio dos slides 9 e 10 e cronometragem do ensaio completo, com limite de 7 min. | |
