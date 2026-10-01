# Relatório de Execução — Deploy do Modo Vaping no GCE

**Data:** 27 de Setembro de 2026  
**Palavras-chave:** `deploy`, `vaping`, `gce`, `neon`, `ssh`, `flask`, `gunicorn`, `postgresql`, `nginx`  
**Autor:** Antigravity (AGY)  
**Projeto:** EUFit (`/home/jurandir/EUFit`)  
**Instância de Produção:** `gce` (`136.114.199.181` / `eufit.duckdns.org`)

---

## 1. Resumo Executivo

Este documento consolida a análise do estado da aplicação **EUFit**, a resolução da interrupção de acesso remoto e a conclusão com sucesso da **Fase N7 (Deploy em Produção do Modo Vaping com Neon PostgreSQL)** na máquina virtual do Google Compute Engine (GCE).

A aplicação encontra-se atualmente em pleno funcionamento em produção, servida via Nginx + Gunicorn, com persistência migrada para o Neon e protegida por CSRF global e autenticação Google OAuth.

---

## 2. Contexto e Diagnóstico da Interrupção

### 2.1 Estado Pré-existente no Repositório Local
O desenvolvimento do **Modo Vaping** (Fases N0 a N6 do `reg/EscopoVaping.txt`) havia sido implementado e sincronizado no GitHub até o commit `322b8ba`:
- **Modelos:** Tabela `record_vape` integrada via SQLAlchemy (`RecordVape`).
- **Serviços:** CRUD completo com cálculo de média móvel de consumo de 15 dias.
- **Interface Dark:** Templates `home.html`, `history.html` e `edit.html` estendendo o layout base moderno `menu.html`.
- **Navegação:** Card **StopVaping** ativado no menu pós-login.
- **Segurança:** Ativação global do `CSRFProtect` em todas as rotas e formulários.

### 2.2 Causa da Interrupção
Ao tentar iniciar a Fase N7 de deploy, a conexão SSH local direta para a VM através do alias/comando `gce` falhou com erro de chave pública (`Permission denied (publickey)`), interrompendo a sequência de comandos antes do reinício dos serviços de produção.

---

## 3. Resolução da Conectividade SSH (GCE)

1. **Credenciais Google Cloud SDK:**
   - Foi gerado um par de chaves dedicado (`~/.ssh/google_compute_engine`) e propagado com sucesso para os metadados do projeto GCP `eufit-513da`.
2. **Configuração do SSH Local (`~/.ssh/config`):**
   ```ssh
   Host gce
       HostName 136.114.199.181
       User jurandir
       IdentityFile ~/.ssh/google_compute_engine
       IdentitiesOnly yes
   ```
3. **Criação de Alias no Shell (`~/.bash_aliases`):**
   - Configurado `alias gce="ssh gce"` para permitir acesso direto com um único comando no terminal.

---

## 4. Execução do Deploy em Produção (Fase N7)

A sequência estabelecida no plano de deploy foi executada na VM de produção (`/home/jurandir_fisico/eufit`):

1. **Backup Preventivo:**
   - Criada cópia de segurança do banco local legado:
     `/home/jurandir_fisico/eufit/instance/app.db.bak-20260927`.
2. **Sincronização de Código:**
   - Confirmado que a branch `main` na VM estava atualizada com `origin/main` no commit `322b8ba` (`fix(csrf): ativa CSRFProtect globalmente`).
3. **Ambiente Virtual e Dependências:**
   - Verificado o ambiente `.EUFit/bin/activate` com todas as dependências satisfeitas (`Flask 3.1.3`, `Flask-SQLAlchemy`, `psycopg 3.3.6`, `Flask-WTF 1.3.0`, `Authlib 1.8.0`, etc.).
4. **Alinhamento da Base de Dados:**
   - Verificado `flask db heads` e `db current`, apontando para a instância de produção no Neon PostgreSQL (`postgresql+psycopg`).
5. **Reinicialização do Serviço:**
   - Executado `sudo systemctl restart eufit`.
   - O daemon Gunicorn (2 workers) reiniciou normalmente escutando em `127.0.0.1:8000`.

---

## 5. Bateria de Testes e Validação

### 5.1 Verificação dos Logs do Sistema
Inspeção detalhada de `journalctl -u eufit -n 20 --no-pager` confirmou inicialização limpa, sem exceções de inicialização nem erros de conexão com o PostgreSQL.

### 5.2 Teste dos Endpoints Públicos (HTTPS)
Foram disparadas requisições de validação para o domínio público `https://eufit.duckdns.org`:

| Endpoint | HTTP Status | Resultado Esperado | Validação |
|---|---|---|---|
| `GET /` | `302 Found` | Redirecionar para `/auth/login` | ✅ Aprovado |
| `GET /auth/login` | `200 OK` | Exibir tela de login + visitante | ✅ Aprovado |
| `GET /dashboard/` | `200 OK` | Exibir menu de aplicações com StopVaping ativo | ✅ Aprovado |
| `GET /vaping/` | `302 Found` | Redirecionar para login com parâmetro `next` | ✅ Aprovado |

---

## 6. Homologação e Testes de Aceitação de Usuário (UAT)

Os testes reais em ambiente de produção foram executados diretamente pelo usuário final no navegador Google Chrome via `https://eufit.duckdns.org` com autenticação Google (`jurandir.fisico@gmail.com`).

### 6.1 Resultados dos Testes de Aceitação

| Ação Realizada | Evidência nos Logs / Base de Dados | Status |
|---|---|---|
| **Login Google OAuth** | Redirecionamento 302 -> callback `/auth/google-auth` -> sessão criada no Neon | ✅ Aprovado |
| **Acesso ao Menu & StopVaping** | Renderização de `/dashboard/` e `/vaping/` (média inicial: `431.3` puffs/dia) | ✅ Aprovado |
| **Criação de Registros** | Inseridos registros ID 100 (100 puffs), ID 101 (200 puffs), ID 102 (262 puffs) via POST `/vaping/log` | ✅ Aprovado |
| **Recálculo de Média Móvel** | Média diária recalculada automaticamente no Neon de `431.3` para `468.8` puffs/dia | ✅ Aprovado |
| **Consulta de Histórico** | Acesso e renderização completa de `/vaping/history` (`200 OK`) | ✅ Aprovado |
| **Edição de Registro** | Formulário de edição acessado (`/vaping/edit/100`) e registro atualizado para 101 puffs | ✅ Aprovado |

---

## 7. Próximos Passos e Recomendações

1. **Fase N8 (Limpeza Programada do SQLite):**
   - Após 1 semana de estabilidade comprovada no Neon sem incidentes, remover os arquivos SQLite legados (`app.db` local e `app.db` na VM).
2. **Padronização Cosmética (Opcional):**
   - Uniformizar o caminho do projeto na VM de `eufit` para `EUFit`, ajustando previamente o serviço `/etc/systemd/system/eufit.service` e Nginx.
