# Hermes Agent no Portainer

Stack Docker Swarm para executar o Hermes Agent com dashboard, API e Composio, publicados pelo Traefik.

## Pré-requisitos

- Portainer conectado a um ambiente Docker Swarm.
- Traefik usando a rede overlay externa `network_public`.
- DNS `hermes.autofunil.com.br` e `hermes-api.autofunil.com.br` apontando para a VPS.
- Volume Docker externo `hermes_agent_data` criado no nó manager.

No nó manager, confirme os recursos externos:

```bash
docker network inspect network_public
docker volume create hermes_agent_data
```

## Criar a Stack

No Portainer, abra **Stacks** → **Add stack** → **Web editor**, cole o conteúdo de `docker-compose.yml` e informe estas variáveis em **Environment variables**:

```env
DASHBOARD_PASS=uma-senha-forte
DASHBOARD_SECRET=gere-com-openssl-rand-hex-32
API_SERVER_KEY=gere-com-openssl-rand-hex-32
COMPOSIO_API_KEY=sua-chave-composio
```

Depois clique em **Deploy the stack**.

## Acessos

- Dashboard: `https://hermes.autofunil.com.br`
- API: `https://hermes-api.autofunil.com.br`

O usuário do dashboard é `admin`; a senha é o valor de `DASHBOARD_PASS`. A API usa `API_SERVER_KEY` como Bearer token.

## Configuração pelo dashboard

Depois de iniciar, configure o modelo de IA, canais, integrações, perfis e skills diretamente pelo dashboard. O estado fica persistido em `hermes_agent_data`.

## Logs

```bash
docker service ls
docker service logs --raw --tail 100 NOME_DA_STACK_hermes_agent
```

## Segurança

- Nunca publique `.env` ou chaves no Git.
- Use senhas e chaves diferentes para dashboard e API.
- Faça backup do volume `hermes_agent_data` antes de remover ou atualizar uma configuração antiga.
