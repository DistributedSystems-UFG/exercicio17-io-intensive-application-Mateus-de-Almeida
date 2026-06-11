"""
Servidor SINGLE-THREADED
=========================
Atende UMA conexão por vez. Enquanto processa o cliente atual,
nenhuma outra conexão pode ser aceita ou atendida.

Protocolo simples:
  Cliente envia: "GET <numero_da_linha>\n"
  Servidor responde com o conteúdo da linha (ou "ERRO\n")
"""

import socket

HOST = "0.0.0.0"
PORT = 9001
DATA_FILE = "data.txt"


def carregar_dados():
    """Carrega o arquivo inteiro em memória (lista de linhas).
    Em um cenário real poderia ser leitura sob demanda no disco,
    mas aqui simulamos 'acesso a dados em arquivo' com um pequeno
    atraso artificial para tornar o teste de vazão mais realista."""
    with open(DATA_FILE, "r") as f:
        return f.readlines()


def atender_cliente(conn, addr, linhas):
    """Processa as requisições de UM cliente até ele desconectar."""
    with conn:
        while True:
            dado = conn.recv(1024)
            if not dado:
                break  # cliente fechou a conexão

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
    print(f"[single] {len(linhas)} linhas carregadas. Ouvindo em {HOST}:{PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(128)

        while True:
            conn, addr = srv.accept()
            # ATENÇÃO: chamada BLOQUEANTE.
            # O servidor só volta ao accept() depois que ESTE
            # cliente terminar (ou desconectar). Nada de threads.
            atender_cliente(conn, addr, linhas)


if __name__ == "__main__":
    main()
