# Hermes SWAS

Stack Docker Swarm para executar os perfis `atendimento` e `admin` do Hermes Agent, com dashboard e API publicados pelo Traefik.

## Arquitetura

- `hermes_init`: copia `configs`, `skills` e `prompts` do repositório para volumes Docker. Os agentes aguardam esses arquivos antes de iniciar, o que também funciona no Swarm.
- `hermes_atendimento`: perfil de atendimento, com os artefatos montados como somente leitura.
- `hermes_admin`: perfil administrativo, com dashboard na porta interna `9119` e API na porta interna `8642`.
- `network_public`: rede overlay externa já usada pelo Traefik.

Os serviços são restritos ao nó manager. Por isso, o repositório e o volume externo de dados precisam existir nesse nó.

## Pré-requisitos

- VPS Linux com Docker Swarm ativo e Portainer conectado ao ambiente Swarm.
- Traefik configurado com provider Swarm, entrypoint `websecure` e resolver de certificados chamado `letsencryptresolver`.
- Rede overlay externa chamada `network_public`, compartilhada com o Traefik.
- DNS dos domínios do dashboard e da API apontando para o IP público da VPS.
- Chaves válidas do OpenAI e do Composio.

> O arquivo usa labels no bloco `deploy`, que é a forma correta para o provider Swarm do Traefik. Não use este Compose como uma aplicação Docker Compose comum sem adaptá-lo.

## 1. Preparar a VPS

Execute os comandos abaixo no nó **manager** do Swarm.

Confira se o Swarm está ativo:

```bash
docker node ls
```

Confirme que a rede pública do Traefik existe:

```bash
docker network inspect network_public
```

Se ela não existir, crie-a apenas se esse for o nome e a rede desejados pelo seu Traefik:

```bash
docker network create --driver overlay --attachable network_public
```

Crie o volume externo de dados, caso ainda não exista:

```bash
docker volume create hermes_agent_data
```

Baixe o repositório no caminho definido para a Stack:

```bash
sudo mkdir -p /opt/hermes-swas
sudo chown "$USER":"$USER" /opt/hermes-swas
git clone <URL_DO_SEU_REPOSITORIO> /opt/hermes-swas
cd /opt/hermes-swas
```

Para atualizar uma instalação existente:

```bash
cd /opt/hermes-swas
git pull
```

## 2. Configurar variáveis

Copie ou edite o arquivo `/opt/hermes-swas/.env`. Nunca o envie ao Git ou ao editor público da Stack.

Estas variáveis são obrigatórias:

```env
HERMES_REPO_PATH=/opt/hermes-swas
COMPOSIO_API_KEY=...
OPENAI_API_KEY=...
DOMAIN_DASHBOARD=hermes.seudominio.com.br
DOMAIN_API=hermes-api.seudominio.com.br
DASHBOARD_USERNAME=admin
DASHBOARD_PASS=uma-senha-forte
DASHBOARD_SECRET=um-segredo-longo-e-aleatorio
API_SERVER_KEY=uma-chave-longa-e-aleatoria
```

Se um frontend no navegador chamar a API diretamente, inclua somente suas origens confiáveis, separadas por vírgula e sem barra final:

```env
API_SERVER_CORS_ORIGINS=https://hermes.seudominio.com.br
```

Para integrações servidor a servidor, deixe `API_SERVER_CORS_ORIGINS` vazio. `ANTHROPIC_API_KEY` e `TELEGRAM_BOT_TOKEN` são opcionais. `HERMES_REPO_PATH` deve ser o caminho **absoluto no host da VPS**, e não um caminho interno do container Portainer.

## 3. Criar a Stack no Portainer

1. No Portainer, selecione o ambiente Swarm.
2. Acesse **Stacks** → **Add stack**.
3. Defina o nome `hermes`.
4. Selecione **Web editor** e cole o conteúdo de `docker-compose.yml` deste repositório.
5. Na seção **Environment variables**, cadastre todas as variáveis obrigatórias da seção anterior, incluindo `HERMES_REPO_PATH=/opt/hermes-swas`.
6. Clique em **Deploy the stack**.

O uso do editor é seguro porque os arquivos da aplicação já existem no nó manager em `/opt/hermes-swas`; o serviço `hermes_init` os monta a partir desse caminho e os copia para volumes nomeados.

## 4. DNS e acesso

Crie registros DNS `A` (e `AAAA`, se aplicável) para os valores de:

- `DOMAIN_DASHBOARD`
- `DOMAIN_API`

Após o Traefik emitir o certificado, acesse:

```text
https://<DOMAIN_DASHBOARD>
https://<DOMAIN_API>
```

O dashboard exige autenticação básica com `DASHBOARD_USERNAME` e `DASHBOARD_PASS`. A API deve ser chamada usando a chave configurada em `API_SERVER_KEY`.

## 5. Validar o deploy

No Portainer, abra a Stack e confirme:

- `hermes_init` concluiu com código `0`.
- `hermes_admin` está com `1/1` réplica em execução.
- `hermes_atendimento` está com `1/1` réplica em execução.

Pelo terminal da VPS:

```bash
docker service ls
docker service ps hermes_hermes_init
docker service logs hermes_hermes_init
docker service logs -f hermes_hermes_admin
```

O prefixo `hermes_` corresponde ao nome sugerido para a Stack. Ajuste os comandos se você escolher outro nome.

## Solução de problemas

| Sintoma | Verificação e correção |
| --- | --- |
| `hermes_init` falha ao montar arquivos | Confirme que `/opt/hermes-swas/configs`, `/opt/hermes-swas/skills` e `/opt/hermes-swas/prompts` existem no nó manager e que `HERMES_REPO_PATH` está correto. |
| Serviço não inicia | Confira no Portainer se todas as variáveis obrigatórias foram incluídas; `COMPOSIO_API_KEY` vazia interrompe o deploy intencionalmente. |
| Traefik retorna 404 | Verifique DNS, a existência da rede `network_public`, os domínios configurados e se o Traefik usa o provider Swarm. |
| Traefik retorna 502 | Veja os logs de `hermes_admin`; confirme que as portas internas `9119` e `8642` são as esperadas pela imagem do Hermes Agent. |
| Alterações em `skills` não aparecem | Atualize o repositório na VPS e faça **Update the stack** no Portainer para executar novamente o `hermes_init`. |

## Segurança

- Rotacione credenciais se elas já foram compartilhadas, enviadas por chat ou incluídas em commits.
- Prefira Docker Secrets ou o gerenciamento de secrets do Portainer para produção.
- Mantenha o `.env` fora do versionamento.
- Restrinja `API_SERVER_CORS_ORIGINS` às origens confiáveis; não use `*` para uma API exposta publicamente.
