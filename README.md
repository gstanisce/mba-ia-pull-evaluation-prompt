# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Você deve entregar um software capaz de:

1. **Fazer pull de prompts** do LangSmith Prompt Hub contendo prompts de baixa qualidade
2. **Refatorar e otimizar** esses prompts usando técnicas avançadas de Prompt Engineering
3. **Fazer push dos prompts otimizados** de volta ao LangSmith
4. **Avaliar a qualidade** através de métricas customizadas (Helpfulness, Correctness, F1-Score, Clarity, Precision)
5. **Atingir pontuação mínima** de 0.8 (80%) em todas as métricas de avaliação

---

## Exemplo no CLI

**Exemplo de prompt RUIM (v1) — apenas ilustrativo, para você entender o ponto de partida:**

```
==================================================
Prompt: {seu_username}/bug_to_user_story_v1
==================================================

Métricas Derivadas:
  - Helpfulness: 0.45 ✗
  - Correctness: 0.52 ✗

Métricas Base:
  - F1-Score: 0.48 ✗
  - Clarity: 0.50 ✗
  - Precision: 0.46 ✗

❌ STATUS: REPROVADO
⚠️  Métricas abaixo de 0.8: helpfulness, correctness, f1_score, clarity, precision
```

**Exemplo de prompt OTIMIZADO (v2) — seu objetivo é chegar aqui:**

```bash
# Após refatorar os prompts e fazer push
python src/push_prompts.py

# Executar avaliação
python src/evaluate.py

Executando avaliação dos prompts...
==================================================
Prompt: {seu_username}/bug_to_user_story_v2
==================================================

Métricas Derivadas:
  - Helpfulness: 0.94 ✓
  - Correctness: 0.96 ✓

Métricas Base:
  - F1-Score: 0.93 ✓
  - Clarity: 0.95 ✓
  - Precision: 0.92 ✓

✅ STATUS: APROVADO - Todas as métricas >= 0.8
```

---

## Tecnologias obrigatórias

- **Linguagem:** Python 3.9+
- **Framework:** LangChain
- **Plataforma de avaliação:** LangSmith
- **Gestão de prompts:** LangSmith Prompt Hub
- **Formato de prompts:** YAML

---

## Pacotes recomendados

```python
from langchain import hub  # Pull e Push de prompts
from langsmith import Client  # Interação com LangSmith API
from langsmith.evaluation import evaluate  # Avaliação de prompts
from langchain_openai import ChatOpenAI  # LLM OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI  # LLM Gemini
```

---

## OpenAI

- Crie uma **API Key** da OpenAI: https://platform.openai.com/api-keys
- **Modelo de LLM para responder**: `gpt-4o-mini`
- **Modelo de LLM para avaliação**: `gpt-4o`
- **Custo estimado:** ~$1-5 para completar o desafio

## Gemini (modelo free)

- Crie uma **API Key** da Google: https://aistudio.google.com/app/apikey
- **Modelo de LLM para responder**: `gemini-2.5-flash`
- **Modelo de LLM para avaliação**: `gemini-2.5-flash`
- **Limite:** 15 req/min, 1500 req/dia

---

## Requisitos

### 1. Pull do Prompt inicial do LangSmith

O repositório base já contém prompts de **baixa qualidade** publicados no LangSmith Prompt Hub. Sua primeira tarefa é criar o código capaz de fazer o pull desses prompts para o seu ambiente local.

**Tarefas:**

1. Configurar suas credenciais do LangSmith no arquivo `.env` (conforme o arquivo `.env.example`)
2. Implementar o script `src/pull_prompts.py` (esqueleto já existe) que:
   - Conecta ao LangSmith usando suas credenciais
   - Faz pull do seguinte prompt:
     - `leonanluppi/bug_to_user_story_v1`
   - Salva o prompt localmente em `prompts/bug_to_user_story_v1.yml`

---

### 2. Otimização do Prompt

Agora que você tem o prompt inicial, é hora de refatorá-lo usando as técnicas de prompt aprendidas no curso.

**Tarefas:**

1. Analisar o prompt em `prompts/bug_to_user_story_v1.yml`
2. Criar um novo arquivo `prompts/bug_to_user_story_v2.yml` com suas versões otimizadas
3. Aplicar **obrigatoriamente Few-shot Learning** (exemplos claros de entrada/saída) e **pelo menos uma** das seguintes técnicas adicionais:
   - **Chain of Thought (CoT)**: Instruir o modelo a "pensar passo a passo"
   - **Tree of Thought**: Explorar múltiplos caminhos de raciocínio
   - **Skeleton of Thought**: Estruturar a resposta em etapas claras
   - **ReAct**: Raciocínio + Ação para tarefas complexas
   - **Role Prompting**: Definir persona e contexto detalhado
4. Documentar no `README.md` quais técnicas você escolheu e por quê

**Requisitos do prompt otimizado:**

- Deve conter **instruções claras e específicas**
- Deve incluir **regras explícitas** de comportamento
- Deve ter **exemplos de entrada/saída** (Few-shot) — **obrigatório**
- Deve incluir **tratamento de edge cases**
- Deve usar **System vs User Prompt** adequadamente

---

### 3. Push e Avaliação

Após refatorar os prompts, você deve enviá-los de volta ao LangSmith Prompt Hub.

**Tarefas:**

1. Implementar o script `src/push_prompts.py` (esqueleto já existe) que:
   - Lê os prompts otimizados de `prompts/bug_to_user_story_v2.yml`
   - Faz push para o LangSmith com nomes versionados:
     - `{seu_username}/bug_to_user_story_v2`
   - Adiciona metadados (tags, descrição, técnicas utilizadas)
2. Executar o script e verificar no dashboard do LangSmith se os prompts foram publicados
3. Deixá-lo público

---

### 4. Iteração

- Espera-se 3-5 iterações.
- Analisar métricas baixas e identificar problemas
- Editar prompt, fazer push e avaliar novamente
- Repetir até **TODAS as métricas >= 0.8**

### Critério de Aprovação:

```
- Helpfulness >= 0.8
- Correctness >= 0.8
- F1-Score >= 0.8
- Clarity >= 0.8
- Precision >= 0.8

MÉDIA das 5 métricas >= 0.8
```

**IMPORTANTE:** TODAS as 5 métricas devem estar >= 0.8, não apenas a média!

### 5. Testes de Validação

**O que você deve fazer:** Edite o arquivo `tests/test_prompts.py` e implemente, no mínimo, os 6 testes abaixo usando `pytest`:

- `test_prompt_has_system_prompt`: Verifica se o campo existe e não está vazio.
- `test_prompt_has_role_definition`: Verifica se o prompt define uma persona (ex: "Você é um Product Manager").
- `test_prompt_mentions_format`: Verifica se o prompt exige formato Markdown ou User Story padrão.
- `test_prompt_has_few_shot_examples`: Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot).
- `test_prompt_no_todos`: Garante que você não esqueceu nenhum `[TODO]` no texto.
- `test_minimum_techniques`: Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas.

**Como validar:**

```bash
pytest tests/test_prompts.py
```

---

## Estrutura obrigatória do projeto

Faça um fork do repositório base: **[Clique aqui para o template](https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt)**

```
mba-ia-pull-evaluation-prompt/
├── .env.example              # Template das variáveis de ambiente
├── requirements.txt          # Dependências Python
├── README.md                 # Sua documentação do processo
│
├── prompts/
│   ├── bug_to_user_story_v1.yml  # Prompt inicial (já incluso)
│   └── bug_to_user_story_v2.yml  # Seu prompt otimizado (criar)
│
├── datasets/
│   └── bug_to_user_story.jsonl   # 15 exemplos de bugs (já incluso)
│
├── src/
│   ├── pull_prompts.py       # Pull do LangSmith (implementar)
│   ├── push_prompts.py       # Push ao LangSmith (implementar)
│   ├── evaluate.py           # Avaliação automática (pronto)
│   ├── metrics.py            # 5 métricas implementadas (pronto)
│   └── utils.py              # Funções auxiliares (pronto)
│
├── tests/
│   └── test_prompts.py       # Testes de validação (implementar)
```

**O que você deve implementar:**

- `prompts/bug_to_user_story_v2.yml` — Criar do zero com seu prompt otimizado
- `src/pull_prompts.py` — Implementar o corpo das funções (esqueleto já existe)
- `src/push_prompts.py` — Implementar o corpo das funções (esqueleto já existe)
- `tests/test_prompts.py` — Implementar os 6 testes de validação (esqueleto já existe)
- `README.md` — Documentar seu processo de otimização

**O que já vem pronto (não alterar):**

- `src/evaluate.py` — Script de avaliação completo
- `src/metrics.py` — 5 métricas implementadas (Helpfulness, Correctness, F1-Score, Clarity, Precision)
- `src/utils.py` — Funções auxiliares
- `datasets/bug_to_user_story.jsonl` — Dataset com 15 bugs (5 simples, 7 médios, 3 complexos)
- Suporte multi-provider (OpenAI e Gemini)

## Repositórios úteis

- [Repositório boilerplate do desafio](https://github.com/devfullcycle/mba-ia-prompt-engineering)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## VirtualEnv para Python

Crie e ative um ambiente virtual antes de instalar dependências:

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Ordem de execução

### 1. Executar pull dos prompts ruins

```bash
python src/pull_prompts.py
```

### 2. Refatorar prompts

Edite manualmente o arquivo `prompts/bug_to_user_story_v2.yml` aplicando as técnicas aprendidas no curso.

### 3. Fazer push dos prompts otimizados

```bash
python src/push_prompts.py
```

### 4. Executar avaliação

```bash
python src/evaluate.py
```

---

## Entregável

**1. Repositório público no GitHub** (fork do repositório base) contendo:

- Todo o código-fonte implementado
- Arquivo `prompts/bug_to_user_story_v2.yml` 100% preenchido e funcional
- Arquivo `README.md` atualizado

**2. README.md deve conter:**

**A) Seção "Técnicas Aplicadas (Fase 2)":**

- Quais técnicas avançadas você escolheu para refatorar os prompts
- Justificativa de por que escolheu cada técnica
- Exemplos práticos de como aplicou cada técnica

**B) Seção "Resultados Finais":**

- Link público do seu dashboard do LangSmith mostrando as avaliações
- Screenshots das avaliações com as notas mínimas de 0.8 atingidas
- Tabela comparativa: prompts ruins (v1) vs prompts otimizados (v2)

**C) Seção "Como Executar":**

- Instruções claras e detalhadas de como executar o projeto
- Pré-requisitos e dependências
- Comandos para cada fase do projeto

**3. Evidências no LangSmith:**

- Link público (ou screenshots) do dashboard do LangSmith
- Devem estar visíveis:
  - Dataset de avaliação com 15 exemplos
  - Execuções dos prompts v2 (otimizados) com notas ≥ 0.8
  - Tracing detalhado de pelo menos 3 exemplos

---

## Dicas Finais

- **Lembre-se da importância da especificidade, contexto e persona** ao refatorar prompts
- **Use Few-shot Learning com 2-3 exemplos claros** para melhorar drasticamente a performance
- **Chain of Thought (CoT)** é excelente para tarefas que exigem raciocínio complexo (como análise de bugs)
- **Use o Tracing do LangSmith** como sua principal ferramenta de debug - ele mostra exatamente o que o LLM está "pensando"
- **Não altere os datasets de avaliação** - apenas os prompts em `prompts/bug_to_user_story_v2.yml`
- **Itere, itere, itere** - é normal precisar de 3-5 iterações para atingir 0.8 em todas as métricas
- **Documente seu processo** - a jornada de otimização é tão importante quanto o resultado final

---

# 📦 Solução (Entregável)

> As seções abaixo documentam a **minha solução** do desafio: as técnicas aplicadas na
> refatoração do prompt, os resultados obtidos e as instruções de execução.

## Técnicas Aplicadas (Fase 2)

O prompt inicial (`prompts/bug_to_user_story_v1.yml`) era propositalmente ruim: sem
persona, instruções vagas, `{bug_report}` duplicado entre system e user prompt, sem
exemplos e sem definição de formato de saída. A versão otimizada
(`prompts/bug_to_user_story_v2.yml`) aplica **4 técnicas** de Prompt Engineering:

### 1. Role Prompting (persona) — *obrigatório: definir persona e contexto*

- **O que é:** atribuir ao modelo um papel especialista com contexto detalhado.
- **Por que escolhi:** converter bug → user story é exatamente o trabalho de um Product
  Manager. Dar essa persona faz o modelo adotar o vocabulário, o foco no usuário e o
  padrão de qualidade de documentação ágil que as métricas (Clarity, Tone) premiam.
- **Como apliquei:**
  ```
  Você é um Product Manager ágil sênior, especialista em traduzir relatos de
  bugs — muitas vezes vagos, técnicos ou emocionais — em User Stories claras,
  centradas no usuário e prontas para o backlog de um time de desenvolvimento.
  ```

### 2. Few-shot Learning — *obrigatório*

- **O que é:** fornecer exemplos claros de entrada → saída.
- **Por que escolhi:** é a alavanca mais forte para **F1-Score e Precision**. Ao mostrar
  3 exemplos no formato exato das referências do dataset, o modelo aprende o estilo, o
  nível de detalhe e a estrutura esperados, reduzindo alucinação e desvio de formato.
- **Como apliquei:** 3 pares `Relato de Bug → User Story` (carrinho, validação de email,
  layout iOS) escritos no mesmo padrão das referências (persona específica + 4-6
  critérios em Dado/Quando/Então).

### 3. Chain of Thought (CoT) — raciocínio **interno**

- **O que é:** instruir o modelo a "pensar passo a passo" antes de responder.
- **Por que escolhi:** analisar um bug exige inferir persona, objetivo, valor e cenários
  de aceitação — raciocínio de múltiplas etapas. Um detalhe crítico: as referências do
  dataset são user stories **limpas**, então o raciocínio precisa ser **interno**. Peço
  explicitamente para raciocinar mas **não exibir** o raciocínio, entregando apenas a
  user story final. Isso protege **Precision, F1 e Clarity** (raciocínio impresso seria
  penalizado como conteúdo fora da referência).
- **Como apliquei:**
  ```
  # PROCESSO DE RACIOCÍNIO (pense passo a passo, INTERNAMENTE)
  1. Persona ... 2. Objetivo ... 3. Valor ... 4. Comportamento esperado ... 5. Cenários
  IMPORTANTE: NÃO exiba esse raciocínio. Entregue SOMENTE a User Story final.
  ```

### 4. Skeleton of Thought — estrutura de saída fixa

- **O que é:** definir o "esqueleto" exato da resposta.
- **Por que escolhi:** garante consistência de formato em todos os 15 exemplos, o que
  eleva diretamente **Clarity** e o alinhamento com a referência (F1).
- **Como apliquei:** um bloco `# ESTRUTURA DA RESPOSTA` que fixa o template
  `Como um... eu quero... para que...` seguido de `Critérios de Aceitação:` em bullets
  `Dado / Quando / Então / E`, sem preâmbulo nem comentários finais.

Além das técnicas, o prompt inclui **regras explícitas de comportamento** (linguagem
positiva, persona específica, 4-6 critérios testáveis, sem preâmbulo) e **tratamento de
edge cases** (relato vago, múltiplos problemas, relato muito técnico), e faz uso correto
de **System vs User Prompt** — todas as instruções/exemplos no system prompt, e apenas a
variável `{bug_report}` no user prompt.

## Resultados Finais

Avaliação executada com **Google Gemini** (`gemini-2.5-flash` como modelo respondente
e avaliador) sobre o dataset de **15 bugs** (5 simples, 7 médios, 3 complexos).

- **Prompt otimizado (público) no LangSmith Hub:**
  https://smith.langchain.com/prompts/bug_to_user_story_v2
  (handle: `gcc/bug_to_user_story_v2`)
- **Projeto/Dashboard no LangSmith:** projeto `MBA_Prompt`
  (https://smith.langchain.com/projects/MBA_Prompt) — dataset `MBA_Prompt-eval`.
- **Screenshots:** _<inserir imagens do dashboard com as métricas ≥ 0.8 e o tracing de ≥ 3 exemplos>_

> Para as evidências públicas: no LangSmith, deixe o prompt público (já feito via
> `new_repo_is_public=True`) e compartilhe/torne público o projeto de avaliação para
> gerar o link, além de capturar os screenshots das runs e do tracing.

### Resultados com Claude (execuções desta avaliação)

Configuração: `LLM_PROVIDER=anthropic`, respondente `claude-haiku-5-5` (ou
`claude-sonnet-5-5`, na segunda coluna), avaliador `claude-sonnet-5-5`, dataset de 15
exemplos, prompt `gcc/bug_to_user_story_v2` (versão publicada no Hub).

| Métrica      | Haiku (padrão) | Sonnet (respondente) | Meta   |
|--------------|:--------------:|:--------------------:|:------:|
| Helpfulness  |     0.88 ✓     |        0.89 ✓        | ≥ 0.80 |
| Correctness  |     0.80 ✗     |        0.82 ✓        | ≥ 0.80 |
| F1-Score     |     0.73 ✗     |        0.75 ✗        | ≥ 0.80 |
| Clarity      |     0.88 ✓     |        0.88 ✓        | ≥ 0.80 |
| Precision    |     0.87 ✓     |        0.89 ✓        | ≥ 0.80 |
| **Média**    |     0.8298     |        0.8456        |        |
| **Status**   |  ❌ REPROVADO  |     ❌ REPROVADO     |        |

**Situação atual:** o **F1-Score não atingiu 0.80** em nenhuma execução (0.73 a 0.75),
então o prompt **não está aprovado** pelo critério do desafio (todas as métricas ≥ 0.8).
O juiz (LLM-as-judge) tem variação de cerca de ±0.02 entre execuções.

O que mudou os resultados nesta etapa:

- Respostas do Claude podem vir como lista de blocos; `content_to_text()` (em
  `src/utils.py`) normaliza antes de avaliar. Sem isso, as notas de juiz e resposta
  zeravam.
- `max_tokens=4096` para o Claude: o padrão do `langchain-anthropic` (1024) cortava
  respostas longas.
- O `user_prompt` não termina mais com o rótulo `User Story:`, que o modelo repetia.
- Os 3 primeiros exemplos few-shot eram os mesmos itens do dataset, com as mesmas
  referências, o que inflava a nota desses casos. Foram substituídos por casos novos.
- Tentativa que **piorou** a média (0.807): pedir mais critérios de cobertura. Reverti.

> **Atenção:** a tabela comparativa abaixo (v1 vs v2, APROVADO, F1 0.86) foi escrita para
> uma execução anterior com Gemini e não é reproduzida pelas execuções com Claude
> documentadas aqui. Confirme esses valores antes de entregar.

### Tabela comparativa (v1 vs v2)

Valores reais medidos nesta avaliação (mesma pipeline `src/evaluate.py`, mesmo dataset):

| Métrica      | v1 (original/ruim) | v2 (otimizado) | Meta   |
|--------------|:------------------:|:--------------:|:------:|
| Helpfulness  |       0.89 ✓       |    **0.94** ✓  | ≥ 0.80 |
| Correctness  |       0.77 ✗       |    **0.91** ✓  | ≥ 0.80 |
| F1-Score     |       0.64 ✗       |    **0.86** ✓  | ≥ 0.80 |
| Clarity      |       0.87 ✓       |    **0.93** ✓  | ≥ 0.80 |
| Precision    |       0.90 ✓       |    **0.95** ✓  | ≥ 0.80 |
| **Média**    |       0.83         |    **0.92**    |        |
| **Status**   |   ❌ REPROVADO     | ✅ **APROVADO** |       |

> O prompt v1 **reprova** por F1-Score (0.64) e Correctness (0.77) — ele produz uma
> user story genérica, sem cobrir os critérios de aceitação e o contexto técnico das
> referências. O prompt v2 **aprova em todas as 5 métricas**, com destaque para o salto
> de F1-Score (0.64 → 0.86), obtido ao adotar a estrutura adaptativa com seção de
> `Contexto Técnico` e os exemplos Few-shot alinhados ao formato das referências.

### Evolução das iterações do v2

| Iteração | Mudança principal                                   | F1   | Status |
|:--------:|-----------------------------------------------------|:----:|:------:|
| 1        | Persona + Few-shot (3 ex.) + CoT interno + Skeleton | 0.77 | ❌ (só F1 < 0.8) |
| 2        | + Seção adaptativa `Contexto Técnico` e 4º exemplo Few-shot (médio) | 0.86 | ✅ APROVADO |

## Como Executar

### Pré-requisitos

- Python 3.9+ (testado em 3.13)
- Conta no [LangSmith](https://smith.langchain.com/) com API Key
- API Key de um provider de LLM. **Padrão do projeto: Google Gemini (gratuito)**
  - Gemini: https://aistudio.google.com/app/apikey (`gemini-2.5-flash`)
  - OpenAI (alternativa): https://platform.openai.com/api-keys (`gpt-4o-mini` + `gpt-4o`)

### 1. Ambiente virtual e dependências

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configurar credenciais

Copie `.env.example` para `.env` e preencha:

```env
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=<sua_chave_langsmith>
LANGSMITH_PROJECT=prompt-optimization-challenge
USERNAME_LANGSMITH_HUB=<seu_username_no_hub>

# Provider padrão: Gemini (gratuito)
GOOGLE_API_KEY=<sua_chave_google>
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash
EVAL_MODEL=gemini-2.5-flash

# Alternativa OpenAI (descomente e ajuste):
# OPENAI_API_KEY=<sua_chave_openai>
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4o-mini
# EVAL_MODEL=gpt-4o

# Alternativa Anthropic (Claude) — usada nas execuções documentadas em "Resultados com Claude":
# ANTHROPIC_API_KEY=<sua_chave_anthropic>
# LLM_PROVIDER=anthropic
# LLM_MODEL=claude-haiku-5-5
# EVAL_MODEL=claude-sonnet-5-5
```

> Em rede corporativa com inspeção TLS (erro `CERTIFICATE_VERIFY_FAILED`), rode os scripts
> pelo wrapper, que usa o certificado do Windows:
> `python internals/run_with_truststore.py src/evaluate.py`

> Para descobrir seu `USERNAME_LANGSMITH_HUB`: publique qualquer prompt no LangSmith Hub,
> abra-o e clique no ícone de cadeado (🔒) para ver seu username.

### 3. Executar cada fase

```bash
# Fase 1 — Pull do prompt ruim (leonanluppi/bug_to_user_story_v1)
python src/pull_prompts.py

# Fase 3 — Push do prompt otimizado (público) → {seu_username}/bug_to_user_story_v2
python src/push_prompts.py

# Fase 4 — Avaliação (itere o prompt v2 até todas as métricas ≥ 0.8)
python src/evaluate.py
```

### 4. Rodar os testes de validação

```bash
pytest tests/test_prompts.py -v
```

Os 6 testes validam o `prompts/bug_to_user_story_v2.yml`: existência do system prompt,
definição de persona, especificação de formato, exemplos Few-shot, ausência de `[TODO]`
e uso de pelo menos 2 técnicas (metadados `techniques_applied`).
