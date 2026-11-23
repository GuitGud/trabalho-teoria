#include <chrono>
#include <cstddef>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#endif

using Valor = std::uint64_t;
using Valores = std::vector<Valor>;
using Algoritmo = bool (*)(const Valores&, Valor);

#ifdef _WIN32
// O steady_clock de algumas compilações MinGW registra apenas microssegundos.
using Instante = std::int64_t;

Instante agora() {
    LARGE_INTEGER contador;
    QueryPerformanceCounter(&contador);
    return contador.QuadPart;
}

std::int64_t duracao_ns(Instante inicio, Instante fim) {
    static const long double ns_por_tick = [] {
        LARGE_INTEGER frequencia;
        if (!QueryPerformanceFrequency(&frequencia)) {
            throw std::runtime_error("contador de desempenho indisponivel");
        }
        return 1.0e9L / frequencia.QuadPart;
    }();
    return static_cast<std::int64_t>((fim - inicio) * ns_por_tick);
}
#else
using Instante = std::chrono::steady_clock::time_point;

Instante agora() {
    return std::chrono::steady_clock::now();
}

std::int64_t duracao_ns(Instante inicio, Instante fim) {
    return std::chrono::duration_cast<std::chrono::nanoseconds>(fim - inicio).count();
}
#endif

bool forca_bruta(const Valores& valores, Valor alvo) {
    const std::size_t n = valores.size();
    std::vector<std::uint8_t> mascara(n, 0);

    while (true) {
        Valor soma = 0;
        for (std::size_t i = 0; i < n; ++i) {
            if (mascara[i]) {
                soma += valores[i];
            }
        }
        if (soma == alvo) {
            return true;
        }

        std::size_t i = 0;
        while (i < n && mascara[i]) {
            mascara[i] = 0;
            ++i;
        }
        if (i == n) {
            return false;
        }
        mascara[i] = 1;
    }
}

bool programacao_dinamica(const Valores& valores, Valor alvo) {
    std::vector<std::uint8_t> alcancavel(static_cast<std::size_t>(alvo) + 1, 0);
    alcancavel[0] = 1;

    for (Valor valor : valores) {
        for (std::size_t coluna = alcancavel.size(); coluna > 0; --coluna) {
            const std::size_t soma = coluna - 1;
            if (soma >= valor && alcancavel[soma - valor]) {
                alcancavel[soma] = 1;
            }
        }
    }
    return alcancavel[static_cast<std::size_t>(alvo)] != 0;
}

struct Caso {
    std::string id;
    std::string cenario;
    Valor alvo;
    std::size_t repeticoes;
    Valores valores;
};

Valor inteiro(const std::string& texto) {
    if (texto.empty() || texto.find_first_not_of("0123456789") != std::string::npos) {
        throw std::invalid_argument("inteiro nao negativo esperado: " + texto);
    }
    return std::stoull(texto);
}

std::vector<Caso> ler_entradas(std::istream& entrada) {
    const std::string cabecalho = "caso\tcenario\tn\talvo\trepeticoes\tvalores";
    const Valor max_soma = std::numeric_limits<std::int64_t>::max();
    std::string linha;
    std::getline(entrada, linha);
    if (!linha.empty() && linha.back() == '\r') {
        linha.pop_back();
    }
    if (linha != cabecalho) {
        throw std::invalid_argument("cabecalho TSV invalido");
    }

    std::vector<Caso> casos;
    while (std::getline(entrada, linha)) {
        if (!linha.empty() && linha.back() == '\r') {
            linha.pop_back();
        }
        std::istringstream registro(linha);
        std::string id, cenario, n, alvo, repeticoes, dados;
        if (!std::getline(registro, id, '\t') || !std::getline(registro, cenario, '\t') ||
            !std::getline(registro, n, '\t') || !std::getline(registro, alvo, '\t') ||
            !std::getline(registro, repeticoes, '\t') || registro.eof() ||
            id.empty() || cenario.empty()) {
            throw std::invalid_argument("linha TSV invalida");
        }
        std::getline(registro, dados);
        if (dados.find('\t') != std::string::npos) {
            throw std::invalid_argument("colunas excedentes no caso " + id);
        }

        const Valor total_repeticoes = inteiro(repeticoes);
        const Valor objetivo = inteiro(alvo);
        if (total_repeticoes == 0 || total_repeticoes >= std::numeric_limits<std::size_t>::max() ||
            objetivo > max_soma || objetivo >= std::numeric_limits<std::ptrdiff_t>::max()) {
            throw std::invalid_argument("entrada fora dos limites no caso " + id);
        }

        Caso caso{id, cenario, objetivo, static_cast<std::size_t>(total_repeticoes), {}};
        std::istringstream lista(dados);
        std::string termo;
        Valor soma = 0;
        while (lista >> termo) {
            const Valor valor = inteiro(termo);
            if (valor > max_soma - soma) {
                throw std::invalid_argument("soma excede 2^63 - 1 no caso " + id);
            }
            soma += valor;
            caso.valores.push_back(valor);
        }
        if (caso.valores.size() != inteiro(n)) {
            throw std::invalid_argument("n incompativel no caso " + id);
        }
        casos.push_back(std::move(caso));
    }
    return casos;
}

void executar(const std::vector<Caso>& casos, Algoritmo algoritmo,
              const std::string& nome, std::ostream& saida) {
    const Valores aquecimento{3, 5, 9};
    for (int i = 0; i < 5; ++i) {
        algoritmo(aquecimento, 8);
    }

    for (const Caso& caso : casos) {
        for (std::size_t repeticao = 1; repeticao <= caso.repeticoes; ++repeticao) {
            const auto inicio = agora();
            const bool resposta = algoritmo(caso.valores, caso.alvo);
            const auto fim = agora();
            const auto tempo = duracao_ns(inicio, fim);
            saida << caso.id << ',' << caso.cenario << ',' << caso.valores.size() << ','
                  << caso.alvo << ',' << nome << ',' << repeticao << ',' << resposta << ','
                  << tempo << '\n';
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        std::cerr << "Uso: subset_sum ENTRADA.tsv SAIDA.csv {forca_bruta|pd|ambos}\n";
        return 2;
    }
    const std::string modo = argv[3];
    if (modo != "forca_bruta" && modo != "pd" && modo != "ambos") {
        std::cerr << "Algoritmo desconhecido: " << modo << '\n';
        return 2;
    }

    try {
        std::ifstream entrada(argv[1]);
        if (!entrada) {
            throw std::runtime_error("nao foi possivel abrir o TSV de entrada");
        }
        const auto casos = ler_entradas(entrada);
        std::ofstream saida(argv[2]);
        if (!saida) {
            throw std::runtime_error("nao foi possivel criar o CSV de saida");
        }
        saida << "caso,cenario,n,alvo,algoritmo,repeticao,resposta,tempo_ns\n";
        if (modo != "pd") {
            executar(casos, forca_bruta, "forca_bruta", saida);
        }
        if (modo != "forca_bruta") {
            executar(casos, programacao_dinamica, "pd", saida);
        }
        saida.flush();
        if (!saida) {
            throw std::runtime_error("falha ao gravar o CSV");
        }
    } catch (const std::exception& erro) {
        std::cerr << "Erro: " << erro.what() << '\n';
        return 1;
    }
}
