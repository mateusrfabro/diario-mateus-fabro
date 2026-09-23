"""Pré-commit: a única guarda que roda ANTES de algo ficar público.

A CI do GitHub não enxerga a lista de nomes proibidos (ela mora fora do repositório, de
propósito), então a checagem de vazamento precisa rodar aqui, na máquina.

  1. o e-mail do autor tem de ser o de contato do site (um clone novo herda o e-mail
     global da máquina, que é o corporativo);
  2. public/ tem de estar em dia com conteudo/dados.json;
  3. nenhum termo da lista pode aparecer em arquivo, mensagem ou autor.

Instalar uma vez:  git config core.hooksPath scripts/hooks
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def main() -> int:
    esperado = json.loads((RAIZ / "conteudo" / "dados.json").read_text(encoding="utf-8"))["perfil"]["email"]
    atual = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, cwd=RAIZ).stdout.strip()
    if atual != esperado:
        print(f"[pre-commit] e-mail do autor não é o pessoal. Rode: git config user.email {esperado}")
        return 1
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_build.py",
                        "-k", "confidencial or public_e_exatamente or vermelha"], cwd=RAIZ)
    if r.returncode:
        print("[pre-commit] bloqueado: veja o teste acima (o termo nunca é impresso, só o índice)")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
