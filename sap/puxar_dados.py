"""
Passo 2 - Puxar uma informação real, navegando como você navega

Só rode isto depois que conectar_sap.py já tiver funcionado. Aqui o
programa abre o Fiori Launchpad e lê o texto de um "tile" (aqueles
quadradinhos da tela inicial, que às vezes mostram um número/KPI) - é
o mais parecido com "olhar uma informação na tela", só que feito pelo
programa em vez de você.

Troque FILTRO_TILE pelo texto (ou parte dele) do tile/app que você
quer ler, exatamente como aparece na tela do Launchpad.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

FIORI_URL = os.getenv("SAP_FIORI_URL", "")
NAVEGADOR = os.getenv("SAP_BROWSER_CHANNEL", "msedge")
PASTA_PERFIL = Path(__file__).parent / ".perfil_navegador"

FILTRO_TILE = "Pedidos"  # <-- troque pelo texto do tile/app que você quer ler


def puxar_info_da_tela() -> bool:
    if not FIORI_URL:
        print("Erro: preencha SAP_FIORI_URL no arquivo .env (veja .env.example).")
        return False

    with sync_playwright() as p:
        kwargs = {"headless": False}
        if NAVEGADOR:
            kwargs["channel"] = NAVEGADOR

        contexto = p.chromium.launch_persistent_context(
            user_data_dir=str(PASTA_PERFIL), **kwargs
        )
        pagina = contexto.new_page()

        print(f"Acessando: {FIORI_URL}")
        pagina.goto(FIORI_URL, wait_until="networkidle", timeout=60000)
        pagina.wait_for_timeout(5000)

        print(f"Procurando um elemento com o texto: '{FILTRO_TILE}'")
        elemento = pagina.get_by_text(FILTRO_TILE, exact=False).first

        try:
            elemento.wait_for(timeout=10000)
        except Exception:
            print(
                f"❌ Não achei nenhum elemento com o texto '{FILTRO_TILE}' na "
                "tela. Confira o nome exato do tile/app (com maiúsculas/minúsculas "
                "e acentos certos) e tente de novo."
            )
            contexto.close()
            return False

        texto_encontrado = elemento.inner_text()
        print(f'✅ Encontrei: "{texto_encontrado}"')

        input("Pressione ENTER aqui no terminal para fechar o navegador...")
        contexto.close()
        return True


if __name__ == "__main__":
    ok = puxar_info_da_tela()
    sys.exit(0 if ok else 1)
