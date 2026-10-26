"""
Wrapper INTERNO (means-to-an-end) para rodar os scripts do desafio atrás de um
proxy corporativo com inspeção TLS (self-signed root CA).

Problema: na rede corporativa, o certificado raiz é injetado pelo proxy. O
`certifi` embutido não confia nele, então toda chamada HTTPS para
`api.smith.langchain.com` e para a API do Gemini falha com
CERTIFICATE_VERIFY_FAILED.

Solução: `truststore.inject_into_ssl()` faz o Python usar o keystore do sistema
operacional (Windows), que JÁ contém o root CA corporativo. Precisa ser chamado
ANTES de qualquer conexão SSL.

Este wrapper NÃO altera src/evaluate.py, src/push_prompts.py, src/pull_prompts.py
nem src/metrics.py — apenas injeta o truststore e executa o script alvo como
`__main__`, preservando o comportamento original.

Uso:
    python internals/run_with_truststore.py src/push_prompts.py
    python internals/run_with_truststore.py src/evaluate.py
"""
import runpy
import sys
from pathlib import Path

import truststore

truststore.inject_into_ssl()


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python internals/run_with_truststore.py <script.py> [args...]")
        return 2

    target = Path(sys.argv[1]).resolve()
    if not target.exists():
        print(f"Script alvo não encontrado: {target}")
        return 2

    # Garante que o diretório do script alvo (src/) esteja no sys.path para os
    # imports internos (from utils import ...), replicando `python src/<script>.py`.
    sys.path.insert(0, str(target.parent))

    # Repassa os argumentos restantes ao script alvo.
    sys.argv = [str(target)] + sys.argv[2:]

    runpy.run_path(str(target), run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
