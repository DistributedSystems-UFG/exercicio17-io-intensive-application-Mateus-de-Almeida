"""
Servidor MULTI-THREADED com POOL DE THREADS
=============================================
Em vez de criar uma thread nova para cada conexão, um conjunto
FIXO de threads "trabalhadoras" (workers) é criado UMA VEZ no
início do programa. Cada conexão aceita é colocada em uma fila
(queue.Queue) e qualquer worker ocioso a retira para processá-la.

Vantagens:
  - Evita o custo repetido de criar/destruir threads do SO.
  - Limita o número máximo de threads concorrentes (controle de
    recursos), evitando que o servidor seja sobrecarregado.

Desvantagens:
  - Se o número de workers for muito pequeno em relação à demanda,
    requisições ficam enfileiradas (latência aumenta sob pico).
  - Exige escolher um bom tamanho de pool (depende do hardware
    e do tipo de carga: I/O-bound vs CPU-bound).
"""

import socket
import threading
import queue

HOST = "0.0.0.0"
PORT = 9003
DATA_FILE = "data.txt"
NUM_WORKERS = 8  # tamanho fixo do pool de threads


def carregar_dados():
    with open(DATA_FILE, "r") as f:
        return f.readlines()


def atender_cliente(conn, addr, linhas):
    """Mesma lógica de protocolo das versões anteriores."""
    with conn:
        while True:
            dado = conn.recv(1024)
            if not dado:
                break

            comando = dado.decode().strip()

            if comando.startswith("GET "):
                try:
                    idx = int(comando.split()[1])
                    if 0 <= idx < len(linhas):
                        resposta = linhas[idx]
                    else:
                        resposta = "ERRO: indice fora do intervalo\n"
                except (ValueError, IndexError):
                    resposta = "ERRO: comando invalido\n"
            else:
                resposta = "ERRO: comando desconhecido\n"

            conn.sendall(resposta.encode())


def worker(fila_conexoes, linhas):
    """Função executada por cada thread do pool.
    Fica em loop infinito retirando conexões da fila e processando-as."""
    while True:
        conn, addr = fila_conexoes.get()
        try:
            atender_cliente(conn, addr, linhas)
        finally:
            fila_conexoes.task_done()


def main():
    linhas = carregar_dados()
    fila_conexoes = queue.Queue()

    # Cria o pool: NUM_WORKERS threads, todas iniciadas UMA VEZ
    # e que ficam vivas durante toda a execução do servidor.
    for _ in range(NUM_WORKERS):
        t = threading.Thread(target=worker, args=(fila_conexoes, linhas), daemon=True)
        t.start()

    print(f"[thread-pool] {len(linhas)} linhas carregadas. "
          f"{NUM_WORKERS} workers. Ouvindo em {HOST}:{PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(128)

        while True:
            conn, addr = srv.accept()
            # Apenas ENFILEIRA a conexão. A thread principal volta
            # imediatamente ao accept(); algum worker ocioso pegará
            # esta conexão da fila quando estiver livre.
            fila_conexoes.put((conn, addr))


if __name__ == "__main__":
    main()
