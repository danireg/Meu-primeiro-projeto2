"""
Hello World - Conectando no SAP do jeito que você faz na mão

Em vez de usar uma API com usuário técnico (que exigiria pedir algo
para a TI), este script automatiza o NAVEGADOR: abre a tela do Fiori
Launchpad e deixa o SSO da empresa autenticar sozinho - exatamente como
acontece quando você clica em "S/4HANA - PRD (SSO)".

IMPORTANTE:
- Isso só funciona rodando NO SEU COMPUTADOR (não em um servidor
  qualquer), conectado na rede/VPN da empresa, com o Windows logado no
  domínio - é isso que faz o SSO acontecer sem pedir senha.
- Na primeira vez, se aparecer uma tela de login mesmo assim, você loga
  normalmente na janela que abrir. A sessão fica salva numa pasta local
  (.perfil_navegador) para as próximas vezes não pedirem login de novo.

Pré-requisitos (rodar uma vez, no terminal):
    pip install -r requirements.txt
    playwright install chromium

Configuração (arquivo .env, copiado de .env.example):
    SAP_FIORI_URL = a URL que aparece na barra de endereço do navegador
    quando você está na tela onde clica em "S/4HANA - PRD (SSO)"
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

FIORI_URL = os.getenv("SAP_FIORI_URL", "")
NAVEGADOR = os.getenv("SAP_BROWSER_CHANNEL", "msedge")  # "msedge", "chrome" ou vazio p/ Chromium puro

# Pasta onde o navegador guarda cookies/sessão de login. Fica só no seu
# computador - nunca é enviada para o Git (veja .gitignore).
PASTA_PERFIL = Path(__file__).parent / ".perfil_navegador"


def abrir_e_logar() -> bool:
    if not FIORI_URL:
        print("Erro: preencha SAP_FIORI_URL no arquivo .env (veja .env.example).")
        return False

    with sync_playwright() as p:
        print("Abrindo o navegador...")
        kwargs = {"headless": False}  # precisa aparecer na tela p/ SSO funcionar
        if NAVEGADOR:
            kwargs["channel"] = NAVEGADOR

        try:
            contexto = p.chromium.launch_persistent_context(
                user_data_dir=str(PASTA_PERFIL), **kwargs
            )
        except Exception as erro:
            print(f"Não consegui abrir o navegador '{NAVEGADOR}': {erro}")
            print(
                "Dica: se não tiver o Edge instalado, apague SAP_BROWSER_CHANNEL "
                "do .env para usar o Chromium que vem com o Playwright."
            )
            return False

        pagina = contexto.new_page()
        print(f"Acessando: {FIORI_URL}")
        try:
            pagina.goto(FIORI_URL, wait_until="networkidle", timeout=60000)
        except Exception as erro:
            print(f"Não consegui carregar a página: {erro}")
            print("Verifique se está na rede/VPN da empresa e se a URL está certa.")
            contexto.close()
            return False

        print(
            "Se aparecer uma tela de login, entre normalmente. Da próxima vez "
            "a sessão pode já estar salva e isso não será necessário."
        )
        pagina.wait_for_timeout(5000)

        titulo = pagina.title()
        print(f"Título da página carregada: {titulo!r}")

        sucesso = "launchpad" in titulo.lower() or "fiori" in titulo.lower()
        if sucesso:
            print("✅ Login no SAP Fiori Launchpad funcionou! (Hello World alcançado)")
        else:
            print(
                "⚠️ Não consegui confirmar pelo título da página. Olhe a janela "
                "que abriu para ver se o login realmente funcionou - se sim, "
                "está tudo certo, o título pode só ter um nome diferente."
            )

        input("Pressione ENTER aqui no terminal para fechar o navegador...")
        contexto.close()
        return sucesso


if __name__ == "__main__":
    ok = abrir_e_logar()
    sys.exit(0 if ok else 1)
