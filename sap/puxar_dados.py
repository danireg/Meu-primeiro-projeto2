"""
Passo 2 - Puxar uma informação real do SAP

Só rode este script depois que conectar_sap.py já tiver funcionado
(status 200). Aqui vamos pedir uma listinha pequena de dados reais,
usando o mesmo serviço OData de teste (API_BUSINESS_PARTNER).

Se o seu usuário técnico não tiver acesso a esse serviço, troque
SERVICO e ENTIDADE pelo serviço/entidade que a TI/Basis liberar para
você (cada serviço OData do SAP tem sua própria lista de "entidades",
que são como se fossem tabelas).
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

SERVICO = "API_BUSINESS_PARTNER"
ENTIDADE = "A_BusinessPartner"
QUANTIDADE = 5  # quantos registros trazer, só para o teste


def puxar_dados() -> bool:
    if not all([SAP_BASE_URL, SAP_USER, SAP_PASSWORD]):
        print(
            "Erro: preencha SAP_BASE_URL, SAP_USER e SAP_PASSWORD no "
            "arquivo .env (veja .env.example)."
        )
        return False

    url = f"{SAP_BASE_URL}/sap/opu/odata/sap/{SERVICO}/{ENTIDADE}"
    params = {
        "$format": "json",
        "$top": QUANTIDADE,
    }
    if SAP_CLIENT:
        params["sap-client"] = SAP_CLIENT

    print(f"Buscando {QUANTIDADE} registro(s) de {ENTIDADE} em {url}")
    try:
        resposta = requests.get(
            url,
            params=params,
            auth=(SAP_USER, SAP_PASSWORD),
            headers={"Accept": "application/json"},
            verify=SAP_VERIFY_SSL,
            timeout=15,
        )
    except requests.exceptions.RequestException as erro:
        print(f"Falha ao conectar no SAP: {erro}")
        return False

    print(f"Status HTTP: {resposta.status_code}")

    if resposta.status_code != 200:
        print("❌ Não foi possível puxar os dados. Resposta do servidor:")
        print(resposta.text[:800])
        return False

    dados = resposta.json().get("d", {}).get("results", [])
    if not dados:
        print("Conexão OK, mas nenhum registro foi retornado.")
        return True

    print(f"✅ {len(dados)} registro(s) recebido(s):\n")
    for item in dados:
        parceiro = item.get("BusinessPartner", "?")
        nome = item.get("BusinessPartnerFullName") or item.get(
            "OrganizationBPName1", ""
        )
        print(f"  - Parceiro {parceiro}: {nome}")

    return True


if __name__ == "__main__":
    ok = puxar_dados()
    sys.exit(0 if ok else 1)
