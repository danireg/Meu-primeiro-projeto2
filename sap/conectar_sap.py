"""
Hello World - Conexão com o SAP (S/4HANA) via API OData

Objetivo deste primeiro passo: apenas provar que o programa consegue
"falar" com o servidor SAP da empresa e receber uma resposta válida.
Nenhum dado de negócio é lido ainda - isso vem no passo 2
(veja puxar_dados.py).

Como funciona:
- O SAP expõe serviços via "OData" (um jeito padrão de trocar dados
  por HTTPS, parecido com uma API REST comum).
- Para autenticar por um programa (fora do navegador), normalmente
  não se usa o SSO que você usa no Fiori - é preciso um USUÁRIO DE
  SERVIÇO (technical user) criado pelo time de Basis/TI, com usuário
  e senha (ou um certificado/OAuth, dependendo de como a empresa
  configurou).

O que pedir para o time de TI/Basis antes de rodar este script:
  1. A URL base do sistema (ex: https://sap-prd.suaempresa.com.br:8443)
  2. O "mandante" / client SAP (ex: 100)
  3. Um usuário técnico com senha, autorizado a ler pelo menos um
     serviço OData (para teste, qualquer serviço padrão já ativado
     serve, ex: API_BUSINESS_PARTNER)
  4. Confirmar se é preciso estar na rede da empresa/VPN para acessar
"""

import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

SAP_BASE_URL = os.getenv("SAP_BASE_URL", "").rstrip("/")
SAP_CLIENT = os.getenv("SAP_CLIENT", "")
SAP_USER = os.getenv("SAP_USER", "")
SAP_PASSWORD = os.getenv("SAP_PASSWORD", "")
SAP_VERIFY_SSL = os.getenv("SAP_VERIFY_SSL", "true").lower() != "false"

# Serviço usado só para testar a conexão (metadados = "descrição" do
# serviço, não são dados de negócio). Troque pelo nome do serviço que
# a TI liberar, se for diferente.
SERVICO_TESTE = "API_BUSINESS_PARTNER"


def testar_conexao() -> bool:
    if not all([SAP_BASE_URL, SAP_USER, SAP_PASSWORD]):
        print(
            "Erro: preencha SAP_BASE_URL, SAP_USER e SAP_PASSWORD no "
            "arquivo .env (veja .env.example)."
        )
        return False

    url = f"{SAP_BASE_URL}/sap/opu/odata/sap/{SERVICO_TESTE}/$metadata"
    params = {"sap-client": SAP_CLIENT} if SAP_CLIENT else {}

    print(f"Conectando em: {url}")
    try:
        resposta = requests.get(
            url,
            params=params,
            auth=(SAP_USER, SAP_PASSWORD),
            headers={"Accept": "application/xml"},
            verify=SAP_VERIFY_SSL,
            timeout=15,
        )
    except requests.exceptions.SSLError as erro:
        print(f"Falha de certificado SSL: {erro}")
        print(
            "Se for um certificado interno da empresa, veja a opção "
            "SAP_VERIFY_SSL no .env.example."
        )
        return False
    except requests.exceptions.RequestException as erro:
        print(f"Falha ao conectar no SAP: {erro}")
        print(
            "Verifique: a URL está certa? Você está na rede/VPN da "
            "empresa? O sistema está no ar?"
        )
        return False

    print(f"Status HTTP: {resposta.status_code}")

    if resposta.status_code == 200:
        print("✅ Conexão com o SAP funcionou! (Hello World alcançado)")
        return True
    if resposta.status_code == 401:
        print("❌ Usuário/senha inválidos (401 Unauthorized).")
    elif resposta.status_code == 403:
        print("❌ Acesso negado (403 Forbidden) - falta autorização no SAP.")
    elif resposta.status_code == 404:
        print(
            f"❌ Serviço '{SERVICO_TESTE}' não encontrado (404) - "
            "confirme o nome do serviço OData com o time de Basis."
        )
    else:
        print("⚠️ Resposta inesperada, veja o conteúdo abaixo:")
        print(resposta.text[:500])

    return False


if __name__ == "__main__":
    ok = testar_conexao()
    sys.exit(0 if ok else 1)
