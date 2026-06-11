"""
COMPARADOR AUTOMATICO
======================
Sobe cada um dos 3 servidores (single, thread-per-request, thread-pool),
roda o benchmark contra cada um, derruba o servidor e ao final imprime
uma tabela comparativa de vazao (req/s).

Uso:
    python3 run_comparison.py
"""

import subprocess
import sys
import time
import os

# (arquivo do servidor, porta, nome amigavel)
SERVIDORES = [
    ("server_single.py", 9001, "Single-threaded"),
    ("server_thread_per_request.py", 9002, "Thread-per-request"),
    ("server_thread_pool.py", 9003, "Thread-pool"),
]

DIR = os.path.dirname(os.path.abspath(__file__))


def rodar_servidor(arquivo):
    """Inicia o servidor como subprocesso em background.
    stdout/stderr sao descartados para nao poluir a saida."""
    caminho = os.path.join(DIR, arquivo)
    return subprocess.Popen(
        [sys.executable, caminho],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def rodar_benchmark(porta, nome):
    """Executa o benchmark_client.py e captura a saida (texto)."""
    caminho = os.path.join(DIR, "benchmark_client.py")
    resultado = subprocess.run(
        [sys.executable, caminho, str(porta), nome],
        capture_output=True,
        text=True,
        timeout=120,
    )
    return resultado.stdout


def extrair_media(saida_texto):
    """Procura a linha '=== Media de ...: X.XX req/s ===' e retorna o float."""
    for linha in saida_texto.splitlines():
        if linha.startswith("=== Media de"):
            # ex: "=== Media de Single-threaded: 41909.27 req/s ==="
            partes = linha.split(":")
            valor = partes[1].strip().split()[0]
            return float(valor)
    return None


def main():
    resultados = {}

    for arquivo, porta, nome in SERVIDORES:
        print(f"\n{'='*60}")
        print(f"Testando: {nome} (arquivo: {arquivo}, porta: {porta})")
        print(f"{'='*60}")

        proc = rodar_servidor(arquivo)
        time.sleep(1)  # da tempo do servidor subir e fazer bind na porta

        try:
            saida = rodar_benchmark(porta, nome)
            print(saida.strip())
            media = extrair_media(saida)
            resultados[nome] = media
        except Exception as e:
            print(f"ERRO ao testar {nome}: {e}")
            resultados[nome] = None
        finally:
            # encerra o servidor antes de seguir para o proximo
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            time.sleep(0.5)  # garante que a porta seja liberada

    # ---- Tabela comparativa final ----
    print(f"\n{'='*60}")
    print("RESULTADO COMPARATIVO (vazao media em req/s)")
    print(f"{'='*60}")
    print(f"{'Versao':<25} {'Vazao (req/s)':>15}")
    print("-" * 42)

    validos = {k: v for k, v in resultados.items() if v is not None}
    for nome, media in resultados.items():
        if media is not None:
            print(f"{nome:<25} {media:>15,.2f}")
        else:
            print(f"{nome:<25} {'ERRO':>15}")

    if validos:
        melhor = max(validos, key=validos.get)
        pior = min(validos, key=validos.get)
        print("-" * 42)
        print(f"Melhor: {melhor} ({validos[melhor]:,.2f} req/s)")
        print(f"Pior:   {pior} ({validos[pior]:,.2f} req/s)")

        if validos[pior] > 0:
            ganho = (validos[melhor] / validos[pior] - 1) * 100
            print(f"Diferenca: {melhor} foi {ganho:.1f}% mais rapido que {pior}")


if __name__ == "__main__":
    main()
