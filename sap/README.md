# Conectando com o SAP (replicando o login manual)

Este programa não usa uma API do SAP nem precisa de usuário técnico -
ele **automatiza o navegador** para fazer exatamente o que você faz na
mão: abrir a tela do Fiori Launchpad e deixar o SSO da empresa
autenticar sozinho, do jeito que já acontece quando você clica em
"S/4HANA - PRD (SSO)".

Não é preciso pedir nada para a TI para este primeiro teste.

## Como funciona

Usamos a biblioteca **Playwright**, que abre um navegador de verdade
(o programa "aperta os botões" nele). Como o SSO da sua empresa
normalmente depende de você estar logado no Windows do domínio e
conectado na rede/VPN corporativa, isso só funciona **rodando no seu
próprio computador** - não dá para rodar num servidor qualquer.

## Instalação (uma vez só)

```bash
cd sap
python3 -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

cp .env.example .env
```

Edite o `.env` e preencha `SAP_FIORI_URL` com a URL que aparece na
barra de endereço do navegador quando você está na tela onde clica em
"S/4HANA - PRD (SSO)" (copie e cole direto de lá).

## Passo 1 - Testar a conexão ("Hello World")

```bash
python conectar_sap.py
```

Uma janela do navegador vai abrir sozinha e tentar carregar o Fiori
Launchpad:

- Se o SSO funcionar sozinho (comum se você já está logado no domínio
  da empresa), a página carrega direto e o script confirma com
  `✅ Login no SAP Fiori Launchpad funcionou!`.
- Se pedir login, entre normalmente na janela que abriu. A sessão fica
  salva numa pasta local (`.perfil_navegador`) para as próximas vezes
  não pedirem login de novo.

## Passo 2 - Puxar uma informação real

Depois que o passo 1 funcionar, abra `puxar_dados.py` e troque a linha:

```python
FILTRO_TILE = "Pedidos"
```

pelo texto exato de algum tile/app que aparece na tela inicial do seu
Launchpad (ex: o nome de um relatório que você usa). Depois rode:

```bash
python puxar_dados.py
```

O script procura esse texto na tela e mostra o que encontrou - é o
primeiro exemplo de "ler uma informação" do SAP pelo programa.

## Erros comuns

- **Navegador não abre / erro de "channel"**: apague a linha
  `SAP_BROWSER_CHANNEL` do `.env` (ou deixe em branco) para usar o
  Chromium que vem com o Playwright em vez do Edge/Chrome instalado.
- **Fica pedindo login toda vez**: confirme que está rodando sempre a
  partir da mesma pasta (a sessão é salva em `sap/.perfil_navegador`,
  relativa ao script).
- **Página não carrega / timeout**: confirme que está na rede/VPN da
  empresa e que a URL em `SAP_FIORI_URL` está certa.
- **Não acha o tile no passo 2**: confira o texto exato (maiúsculas,
  acentos) como aparece na tela do Launchpad.

## Alternativa (via API, se um dia quiser evoluir)

Se no futuro você tiver (ou pedir) acesso a uma API OData do SAP com
usuário técnico, veja a pasta `api_odata/` - guardei lá uma versão
alternativa que conecta direto por HTTPS, sem precisar abrir navegador.
É mais robusto para automações que rodam sem ninguém acompanhando a
tela, mas exige que a TI libere um usuário de serviço.
