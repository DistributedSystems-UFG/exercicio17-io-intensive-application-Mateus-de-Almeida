"""
CLIENTE DE BENCHMARK
=====================
Mede a vazão (requisições por segundo) de um servidor TCP.

Estratégia:
  - Cria N "clientes" concorrentes (threads), cada um abrindo
    sua própria conexão TCP com o servidor.
  - Cada cliente envia M requisições "GET <indice>" sequencialmente
    pela MESMA conexão e aguarda a resposta de cada uma.
  - Mede o tempo total decorrido e calcula:
        vazao = (N * M) / tempo_total
"""

import socket
import threading
import time
import random
import sys

HOST = "127.0.0.1"
NUM_CLIENTES = 100         # conexões concorrentes
REQS_POR_CLIENTE = 50      # requisições sequenciais por conexão
MAX_INDICE = 9999          # baseado no tamanho do data.txt


def trabalho_cliente(porta, resultados, idx_cliente):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, porta))

    sucesso = 0
    for _ in range(REQS_POR_CLIENTE):
        idx = random.randint(0, MAX_INDICE)
        msg = f"GET {idx}\n".encode()
        sock.sendall(msg)
        resp = sock.recv(1024)
        if resp:
            sucesso += 1

    sock.close()
    resultados[idx_cliente] = sucesso


def benchmark(porta, nome):
    resultados = [0] * NUM_CLIENTES
    threads = []

    inicio = time.perf_counter()

    for i in range(NUM_CLIENTES):
        t = threading.Thread(target=trabalho_cliente, args=(porta, resultados, i))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    fim = time.perf_counter()

    total_requisicoes = sum(resultados)
    duracao = fim - inicio
    vazao = total_requisicoes / duracao

    print(f"--- {nome} (porta {porta}) ---")
    print(f"Requisicoes totais: {total_requisicoes}")
    print(f"Tempo total: {duracao:.3f}s")
    print(f"Vazao: {vazao:.2f} req/s")
    print()

    return vazao


if __name__ == "__main__":
    print(sys.argv)
    porta = int(sys.argv[1])
    nome = sys.argv[2] if len(sys.argv) > 2 else f"porta-{porta}"
    vazoes = []
    for _ in range(3):
        vazoes.append(benchmark(porta, nome))
    media = sum(vazoes) / len(vazoes)
    print(f"=== Media de {nome}: {media:.2f} req/s ===")
