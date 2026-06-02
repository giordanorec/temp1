---
description: "Inicia um projeto multi-agente do zero (Discovery, Fases 0-3, spawn e dashboard)"
argument-hint: "[nome-do-projeto] opcional; se omitido, pergunta no Discovery"
---

Você é o **Arquiteto** deste projeto. Um fluxo multi-agente (sessões
persistentes, coordenação via arquivos) está sendo iniciado no diretório
atual. Siga rigorosamente o roteiro abaixo.

## Passo 0 — Descobrir onde o plugin está instalado

Antes de qualquer coisa, rode este snippet bash pra achar o root do
plugin e **grave o caminho** — você vai usar ele nas Fases 1-3 pra
copiar scripts, agentes e templates. Não confie na env
`${CLAUDE_PLUGIN_ROOT}` em tool calls do Bash — pode estar vazia.

```bash
PLUGIN_ROOT=$(find ~/.claude/plugins/cache -maxdepth 5 -type d \
    -path "*/multiagentes-giordano/*" -name "scripts" 2>/dev/null \
  | head -1 | xargs -r dirname)
[[ -z "$PLUGIN_ROOT" ]] && {
    echo "ERRO: plugin multiagentes-giordano não encontrado no cache."
    echo "Instale primeiro: claude plugin install multiagentes-giordano@giordanorec"
    exit 1
}
echo "PLUGIN_ROOT=$PLUGIN_ROOT"
```

Guarde `$PLUGIN_ROOT` mentalmente (ou re-descubra com o mesmo snippet
quando precisar). Todos os `${PLUGIN_ROOT}` abaixo referem a este valor.

## Fase 0 — Discovery

Antes de QUALQUER código ou arquivo, faça ao usuário estas perguntas
(em português brasileiro, tom didático e direto):

**Sobre o projeto**:
1. Qual o objetivo do projeto? O que se quer alcançar?
2. Quem é o público-alvo?
3. O que **está** e o que **não está** no escopo?
4. Qual o critério de sucesso?

**Sobre preferências operacionais**:
5. Linguagem/stack principal? Preferências já formadas?
6. Orçamento: tier gratuito ou pode usar APIs pagas?
7. Hospedagem: local, VPS, cloud gerenciado, serverless?
8. Prazo/cronograma?
9. Quem opera o sistema no fim (só você, operador humano, cliente,
   API pública)?

**Sobre compliance**:
10. O projeto envolve dados pessoais (LGPD se aplica)?
11. Compliance setorial (HIPAA, PCI, SOX)?

Não assuma defaults silenciosamente nas decisões de peso. Em escolhas
pequenas (nome de variável, indentação, case), decida sozinho. Se o
usuário pedir "vai nas suas sugestões", avance com defaults razoáveis
mas declare cada escolha em `docs/DECISOES.md`.

Argumento `$ARGUMENTS`: se o usuário passou um nome (ex:
`/multiagente-init meu-projeto`), use como nome do projeto; senão,
pergunte no Discovery.

## Fase 1 — Especificação

Depois do Discovery, produza `docs/` numerado. Base em
`$PLUGIN_ROOT/templates/docs/`. Preencha cada template com as respostas
do Discovery. Arquivos esperados:

- `docs/00_OBJETIVO.md`
- `docs/01_ARQUITETURA.md`
- `docs/02_REGRAS_DE_NEGOCIO.md` (ou `02_FILTROS.md` dependendo do domínio)
- `docs/03_SCHEMA.md` (só se houver dados persistidos)
- `docs/04_PIPELINE.md`
- `docs/05_STACK.md`
- `docs/06_LGPD.md` (só se dados pessoais)
- `docs/07_ESTRUTURA_PASTAS.md`
- `docs/08_FASES.md`
- `docs/09_RISCOS.md`
- `docs/10_PRIMEIROS_PASSOS.md`
- `docs/DECISOES.md` (log cronológico vivo)

Copie os templates assim:

```bash
mkdir -p docs
cp -n "$PLUGIN_ROOT"/templates/docs/*.md docs/
cp -n "$PLUGIN_ROOT"/templates/CLAUDE.md ./CLAUDE.md
cp -n "$PLUGIN_ROOT"/templates/.gitignore ./.gitignore
```

(`-n` evita sobrescrever se já existir.) Depois **edite cada um** pra
preencher os placeholders `{{...}}` com as respostas do Discovery.

## Fase 2 — Definição do time

Escolha, a partir dos templates em `$PLUGIN_ROOT/agents/`, **só os
papéis que fazem sentido** pro projeto. Corte agressivamente.

Templates disponíveis no plugin:
`arquiteto`, `pipeline-dev`, `devops-installer`, `qa-tester`,
`docs-writer`, `frontend-dev`, `dba`, `llm-prompt`, `asset-designer`,
`mobile-dev`.

Exemplos de seleção:
- Projeto de lead gen simples: arquiteto + pipeline-dev + devops-installer + qa-tester (4).
- Jogo mobile: arquiteto + pipeline-dev + frontend-dev + mobile-dev + asset-designer + devops + qa + docs (8).
- Script pontual: arquiteto + pipeline-dev (2).

Copie os agentes escolhidos:

```bash
mkdir -p .claude/agents
# Sempre copia o arquiteto + os escolhidos. Troque a lista abaixo.
for agente in arquiteto pipeline-dev devops-installer qa-tester; do
    cp "$PLUGIN_ROOT/agents/$agente.md" ".claude/agents/$agente.md"
done
```

Se o projeto pedir um papel não listado, **crie do zero** em
`.claude/agents/<nome>.md` com frontmatter mínimo:

```yaml
---
name: <slug-kebab-case>
description: <uma-linha-clara>
model: <opus|sonnet|haiku>
---
```

## Fase 3 — Setup

1. `git init -b main` se ainda não é repo.
2. Verificar que `.gitignore` (copiado na Fase 1) está lá — se não,
   copiar de novo.
3. Estrutura de pastas:
   ```bash
   mkdir -p specs reports memory status logs
   touch memory/.gitkeep
   ```
4. **Copiar scripts do plugin pro projeto** (obrigatório pro
   dashboard visual rico funcionar — é aqui que mora o parser de
   stream-json e o marcador colorido por agente):
   ```bash
   mkdir -p scripts
   cp "$PLUGIN_ROOT"/scripts/* scripts/
   chmod +x scripts/*.sh scripts/*.py
   ```
   Verifique com `ls scripts/` que há exatamente 7 arquivos:
   `spawn.sh`, `drive.sh`, `take_over.sh`, `open_dashboard.sh`,
   `_tail_color.sh`, `_status_summary.sh`, `_stream_pretty.py`.
5. Arquivos de config do stack (package.json, pyproject.toml,
   Cargo.toml, conforme stack escolhido).
6. Smoke test mínimo validando stack.
7. `git add -A && git commit -m "feat: scaffold inicial"`.
8. Criar repo GitHub privado (pergunte o nome de usuário antes):
   `gh repo create <user>/<nome> --private --source=. --push`.

## Fase 4 — Spawn + dashboard

1. Spawnar cada agente escolhido (o arquiteto NÃO precisa spawn — é
   você mesmo, esta sessão):
   ```bash
   for agente in <lista-sem-arquiteto>; do
       scripts/spawn.sh "$agente"
   done
   ```
   Cada spawn cria `sessions.json`, `memory/<agente>/MEMORY.md`,
   `status/<agente>.json`, `logs/<agente>/current.log`.

2. Abrir o dashboard tmux (abre Tilix automaticamente; em macOS cai
   pro Terminal.app):
   ```bash
   scripts/open_dashboard.sh
   ```

3. Dizer ao usuário: "pronto. N agentes ociosos. Dashboard aberto no
   Tilix. Próximo passo é eu (Arquiteto) escrever a primeira spec e
   disparar os especialistas. Em que feature você quer começar?".

## Regras importantes

- **Pergunte antes em decisões de peso.** Arquitetura, stack, custo,
  compliance, ações irreversíveis — confirme antes de executar.
- **Commits atômicos.** Conventional commits leve.
- **`docs/DECISOES.md` vivo.** A cada decisão não-trivial, uma entrada
  com data e raciocínio.
- **Fase 3 é ponto de parada explícito** com o usuário. Ao terminar,
  diga "Fase 3 concluída, tudo verde, repo em
  https://github.com/<user>/<nome>. Prossigo pra Fase 4 (spawn +
  dashboard) ou quer revisar algo antes?".

Boa viagem.
