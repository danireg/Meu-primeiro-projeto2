# Conectando com o SAP (S/4HANA)

Primeiro experimento de programa para se conectar ao SAP da empresa e,
depois, puxar uma informação real.

## Como funciona (resumo)

Você faz login no navegador usando SSO, clicando em "S/4HANA - PRD".
Isso é ótimo para uso humano, mas um programa/script geralmente **não
usa SSO** - ele se conecta via uma **API OData** do SAP usando um
**usuário técnico** (usuário/senha criado especialmente para
integrações, sem ser uma pessoa).

## O que pedir para o time de TI/Basis

1. A URL base do sistema SAP (ex: `https://sap-prd.suaempresa.com.br:8443`)
2. O número do mandante/client (ex: `100`)
3. Um usuário técnico com senha, com permissão de leitura em pelo menos
   um serviço OData ativado (para teste, `API_BUSINESS_PARTNER` é um
   serviço padrão comum - mas pode ser outro, se preferirem)
4. Confirmar se é preciso VPN/rede da empresa para acessar de fora
5. Confirmar se o serviço OData realmente está ativo na transação
   `/IWFND/MAINT_SERVICE` (isso é trabalho da TI, só pergunte)

## Passo 1 - Testar a conexão ("Hello World")

```bash
cd sap
python3 -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edite o .env com os dados que a TI te passou

python conectar_sap.py
```

Se aparecer `✅ Conexão com o SAP funcionou!`, deu certo.

## Passo 2 - Puxar uma informação real

Depois que o passo 1 funcionar:

```bash
python puxar_dados.py
```

Isso busca 5 registros de parceiros de negócio (clientes/fornecedores)
como exemplo. Se seu usuário não tiver acesso a esse serviço, troque as
variáveis `SERVICO` e `ENTIDADE` no arquivo `puxar_dados.py` pelo que a
TI liberar.

## Erros comuns

- **401 Unauthorized**: usuário ou senha errados.
- **403 Forbidden**: usuário certo, mas sem autorização (falta um
  "papel"/role no SAP - pedir para a TI liberar).
- **404 Not Found**: o nome do serviço está errado ou ele não está
  ativo no sistema.
- **Erro de SSL**: normalmente é certificado interno da empresa; veja a
  variável `SAP_VERIFY_SSL` no `.env.example`.
- **Timeout / não conecta**: provavelmente precisa estar na rede da
  empresa ou conectado na VPN.

## Alternativa (se não houver OData disponível)

Se a TI disser que não há API OData exposta e o acesso programático só
é possível via **RFC/BAPI** (o jeito mais "clássico" do SAP), o caminho
muda bastante: seria necessário instalar o **SAP NetWeaver RFC SDK**
(biblioteca oficial da SAP, com licença própria, baixada no site deles)
e usar a biblioteca Python `pyrfc`. É mais burocrático de configurar -
se for o caso, me avise que ajustamos o programa para isso.
