# Hermes SWAS

Stack simples para executar o Hermes Agent no Portainer com dashboard e API publicados pelo Traefik.

A Stack usa `nousresearch/hermes-agent:latest`. Para receber uma nova versão, use **Pull and redeploy** no Portainer; o volume `hermes_data` preserva configurações, sessões, skills e memórias entre atualizações.

## O que esta Stack cria

- Um único serviço `hermes_agent` no nó manager do Swarm.
- Um volume persistente `hermes_data` para os dados do Hermes.
- Dashboard HTTPS na porta interna `9119`.
- API HTTPS compatível com OpenAI na porta interna `8642`.

Não há bind mounts, serviços de inicialização, `cron` ou necessidade de clonar o repositório na VPS.

Na primeira execução em um volume novo, a Stack cria o **Hermes Admin Principal**. Pelo dashboard, ele conduz um onboarding seguro e conversacional para criar o perfil `atendimento`, definir regras, conectar canais e instalar skills conforme sua aprovação.

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

## Onboarding no dashboard

1. Abra `https://<DOMAIN_DASHBOARD>` e entre com as credenciais definidas.
2. Abra o chat do perfil principal e escreva: **“Inicie meu onboarding.”**
3. O Admin Principal fará uma pergunta por vez e só criará o perfil `atendimento` ou ativará integrações após sua aprovação.
4. Informe segredos somente nos campos seguros do Portainer ou das integrações; nunca no chat.
5. Antes de liberar automações reais, peça um teste controlado e revise o resumo de permissões fornecido pelo Admin.

O onboarding é gravado uma única vez no volume `hermes_data`; atualizações da Stack não substituem a personalidade que você já personalizou.

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

O serviço deve ficar com `1/1` réplicas. Para atualizar o Hermes, use **Pull and redeploy** no Portainer.

Se os logs indicarem que `config.yaml` é muito antigo para migrar, a Stack está reutilizando um volume `hermes_data` de uma instalação anterior. Faça backup antes de decidir entre executar `hermes setup` para regenerar a configuração ou remover o volume e iniciar uma instalação nova.

## Segurança

- Nunca envie `.env` ou chaves ao Git.
- Use chaves diferentes para dashboard e API.
- Mantenha a lista de CORS restrita às origens confiáveis.
- O volume `hermes_data` é persistente. Não o remova sem backup se já houver dados em uso.
