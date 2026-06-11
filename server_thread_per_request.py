"""
Servidor MULTI-THREADED (1 thread por conexão)
================================================
A cada nova conexão aceita, o servidor cria uma nova
thread (threading.Thread) dedicada exclusivamente a esse
cliente. A thread principal volta IMEDIATAMENTE ao accept()
para aceitar o próximo cliente.

Vantagem: alta concorrência, simples de implementar.
Desvantagem: criar/destruir uma thread do SO a cada requisição
tem custo (alocação de pilha, registro no escalonador do kernel,
context switch). Sob carga muito alta, esse overhead domina e
pode até reduzir a vazão e esgotar recursos (memória/threads).
"""

import socket
import threading

HOST = "0.0.0.0"
PORT = 9002
DATA_FILE = "data.txt"


def carregar_dados():
    with open(DATA_FILE, "r") as f:
        return f.readlines()


def atender_cliente(conn, addr, linhas):
    """Mesma lógica de protocolo do servidor single-threaded,
    porém agora roda dentro de sua própria thread."""
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


def main():
    linhas = carregar_dados()
    print(f"[thread-per-request] {len(linhas)} linhas carregadas. Ouvindo em {HOST}:{PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(128)

        while True:
            conn, addr = srv.accept()

            # Cria UMA NOVA THREAD por conexão recebida.
            # daemon=True garante que essas threads não impeçam
            # o encerramento do processo principal.
            t = threading.Thread(
                target=atender_cliente,
                args=(conn, addr, linhas),
                daemon=True,
            )
            t.start()
            # A thread principal NÃO espera (sem join):
            # volta imediatamente ao laço para aceitar o próximo cliente.


if __name__ == "__main__":
    main()
