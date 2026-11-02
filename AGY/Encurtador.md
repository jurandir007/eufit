# Relatório de Implementação: Encurtador de URLs (EUFit)

**Data:** 02/11/2026  
**Projeto:** EUFit  
**Módulo:** `app/routers/url_shortener`  

---

## 1. Visão Geral

Foi implementado no projeto **EUFit** um sistema completo de encurtador de URLs com redirecionamento direto na raiz, proteção contra colisões de rotas, controle de cota por categoria de usuário (autenticados vs. visitantes) e rastreamento analítico de cliques (IP e User-Agent).

---

## 2. Regras de Negócio e Políticas de Acesso

### A. Usuários Visitantes (Guest Tiers)
* O sistema identifica as contas de demonstração (`demo_iniciante@eufit.internal`, `demo_pleno@eufit.internal`, `demo_fiel@eufit.internal` via `current_user.is_guest`).
* **Limite estrito:** Apenas **1 link ativo** por vez.
* **Expiração temporária:** O link é configurado com expiração automática de **15 minutos** após a criação (`expires_at = now + 15 min`).
* **Aviso obrigatório em inglês na interface:**
  > *"Guest Notice: Temporary Link Policy — As a guest user, you can shorten only 1 link at a time. Each guest link will automatically expire and be deleted 15 minutes after creation."*
* Links expirados são removidos e direcionam para a página de aviso de expiração (`/templates/shortener/expired.html`).

### B. Usuários Autenticados (Padrão)
* **Limite diário:** Até **10 links por dia**.
* **Permanência:** Links persistentes sem expiração obrigatória.
* Contabilização e exibição da cota diária utilizada em tempo real no topo da página.

### C. Personalização de Slugs / Códigos
* **Opcional:** O usuário pode digitar um slug personalizado (ex: `meu-treino`, `promo-2026`) ou deixar em branco.
* **Geração Automática:** Caso não informado, o sistema gera uma chave alfanumérica segura com 6 caracteres (`secrets.choice`).
* **Proteção de Rotas:** Bloqueio de palavras reservadas do sistema (`login`, `logout`, `dashboard`, `scale`, `vaping`, `social`, etc.) e garantia de unicidade via banco de dados.

### D. Rastreamento e Métricas
* **Contador de cliques:** Incremento atômico de `clicks_count`.
* **Carimbo do último acesso:** Atualização de `last_accessed_at`.
* **Histórico analítico detalhado:** Registro de cada acesso na tabela `url_clicks` capturando IP do cliente (`X-Forwarded-For` ou `remote_addr`), User-Agent e carimbo de data/hora.

---

## 3. Arquitetura e Estrutura de Arquivos

### Arquivos Criados:
1. `app/routers/url_shortener/__init__.py`: Definição e registro do Blueprint `shortener_bp`.
2. `app/routers/url_shortener/models.py`:
   - Modelo `ShortenedUrl`: Mapeia a tabela `shortened_urls`.
   - Modelo `UrlClick`: Mapeia a tabela `url_clicks`.
3. `app/routers/url_shortener/routes.py`:
   - `GET /shortener`: Interface principal e listagem dos links do usuário logado.
   - `POST /shortener`: Processamento, validação de URL, cota e criação do link encurtado.
   - `POST /shortener/delete/<id>`: Exclusão de links pertencentes ao usuário.
   - `GET /<string:code>`: Rota raiz de redirecionamento, verificação de expiração e captura de telemetria.
4. `app/templates/shortener/index.html`: Interface Tailwind CSS com cards responsivos, botão de cópia rápida para clipboard e avisos de status.
5. `app/templates/shortener/expired.html`: Tela de aviso de link expirado (HTTP 410).
6. `migrations/versions/2eab8df76ae1_add_shortened_urls_and_url_clicks_tables.py`: Script de migração Alembic para criação das tabelas no PostgreSQL/Neon.

### Arquivos Atualizados:
1. `app/__init__.py`: Registro do Blueprint `shortener_bp`.
2. `app/templates/dashboard/home.html`: Atualização do card `Shorten URL` para `status: 'available'` com link direto para `url_for('shortener.index')`.

---

## 4. Banco de Dados & Esquema

### Tabela `shortened_urls`
| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | `INTEGER PRIMARY KEY` | Identificador autoincremental |
| `user_id` | `INTEGER REFERENCES users(id)` | Usuário proprietário com `ON DELETE CASCADE` |
| `original_url` | `TEXT` | URL original de destino |
| `code` | `VARCHAR(50) UNIQUE INDEX` | Slug ou código da URL encurtada |
| `clicks_count` | `INTEGER DEFAULT 0` | Contador total de acessos |
| `expires_at` | `TIMESTAMP NULL` | Data/hora limite (utilizado para visitantes - 15 min) |
| `last_accessed_at` | `TIMESTAMP NULL` | Data/hora do último clique |
| `created_at` | `TIMESTAMP` | Criado em (`TimestampMixin`) |
| `updated_at` | `TIMESTAMP` | Atualizado em (`TimestampMixin`) |

### Tabela `url_clicks`
| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | `INTEGER PRIMARY KEY` | Identificador autoincremental |
| `shortened_url_id` | `INTEGER REFERENCES shortened_urls(id)` | FK com `ON DELETE CASCADE` |
| `clicked_at` | `TIMESTAMP DEFAULT now()` | Data/hora do clique |
| `ip_address` | `VARCHAR(45)` | IP de origem do clique |
| `user_agent` | `TEXT` | Dispositivo / Navegador do visitante |

---

## 5. Validação e Testes Realizados

- [x] Inicialização do aplicativo Flask com o novo blueprint integrado.
- [x] Migração de banco de dados executada e aplicada com sucesso (`flask db upgrade`).
- [x] Teste de ciclo de vida completo: criação de link temporário para visitante, validação da flag `is_expired`, registro de clique analítico e limpeza.
- [x] Disponibilização do atalho no Menu do Dashboard com card ativo.
