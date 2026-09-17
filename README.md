# Hermes SWAS

Stack simples para executar o Hermes Agent no Portainer com dashboard e API publicados pelo Traefik.

## O que esta Stack cria

- Um único serviço `hermes_agent` no nó manager do Swarm.
- Um volume persistente `hermes_data` para os dados do Hermes.
- Dashboard HTTPS na porta interna `9119`.
- API HTTPS compatível com OpenAI na porta interna `8642`.

Não há bind mounts, serviços de inicialização, `cron` ou necessidade de clonar o repositório na VPS.

## Pré-requisito único

O Traefik já precisa usar uma rede overlay externa chamada `network_public`. Confirme no nó manager:

```bash
docker network inspect network_public
```

Se sua rede do Traefik tiver outro nome, substitua `network_public` no arquivo `docker-compose.yml` pelo nome correto.

## Instalação pelo Portainer

1. Abra **Stacks** → **Add stack** no ambiente Swarm.
2. Escolha **Repository** e informe:
   - Repository URL: `https://github.com/douglaswbc/hermes-swas.git`
   - Compose path: `docker-compose.yml`
   - Reference: `main`
3. Na seção **Environment variables**, adicione os valores abaixo.
4. Clique em **Deploy the stack**.

```env
OPENAI_API_KEY=sua-chave-openai
DOMAIN_DASHBOARD=hermes.seudominio.com.br
DOMAIN_API=hermes-api.seudominio.com.br
DASHBOARD_USERNAME=admin
DASHBOARD_PASS=uma-senha-forte
DASHBOARD_SECRET=gere-com-openssl-rand-hex-32
API_SERVER_KEY=gere-com-openssl-rand-hex-32
API_SERVER_CORS_ORIGINS=https://app.seudominio.com.br
```

`ANTHROPIC_API_KEY` é opcional. Se nenhum frontend no navegador acessar diretamente a API, deixe `API_SERVER_CORS_ORIGINS` vazio. Não use `*`.

## DNS e acesso

Crie registros DNS apontando para o IP da VPS:

- `DOMAIN_DASHBOARD`
- `DOMAIN_API`

Depois do certificado emitido pelo Traefik:

```text
https://<DOMAIN_DASHBOARD>
https://<DOMAIN_API>
```

O dashboard usa `DASHBOARD_USERNAME` e `DASHBOARD_PASS`. A API exige `API_SERVER_KEY` como Bearer token.

## Validação

```bash
docker service ls
docker service logs --raw --tail 100 NOME_DA_STACK_hermes_agent
```

O serviço deve ficar com `1/1` réplicas. Para atualizar, use **Pull and redeploy** no Portainer.

## Segurança

- Nunca envie `.env` ou chaves ao Git.
- Use chaves diferentes para dashboard e API.
- Mantenha a lista de CORS restrita às origens confiáveis.
- O volume `hermes_data` é persistente. Não o remova sem backup se já houver dados em uso.
