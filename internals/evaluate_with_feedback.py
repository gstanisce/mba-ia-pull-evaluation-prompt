"""
Helper OPCIONAL (Option A) — registra as métricas como FEEDBACK no LangSmith.

Problema: na visão de tracing, o score fica preso dentro de uma string JSON
(dentro de um bloco de texto), então não dá para criar uma coluna apontando para
`output.score`. A forma idiomática do LangSmith é gravar o score como *feedback*
no run — feedback vira automaticamente uma coluna ordenável/filtrável na tabela de
runs, sem precisar configurar path.

Este script:
1. Puxa o prompt otimizado do Hub ({username}/bug_to_user_story_v2).
2. Para cada exemplo do dataset, gera a resposta capturando o run_id da geração.
3. Calcula F1 / Clarity / Precision (reutilizando src/metrics.py) e as métricas
   derivadas (Helpfulness, Correctness).
4. Grava cada métrica como feedback no run via client.create_feedback(...).

NÃO altera src/evaluate.py nem src/metrics.py — apenas reutiliza suas funções.

Uso:
    python internals/evaluate_with_feedback.py            # todos os 15 exemplos
    python internals/evaluate_with_feedback.py 2          # apenas os 2 primeiros (smoke test)

Depois de rodar, abra o projeto no LangSmith → aba Runs → botão de colunas e
adicione as colunas de feedback (f1_score, clarity, precision, helpfulness,
correctness). Elas ficam disponíveis automaticamente porque foram gravadas como
feedback nos runs.
"""

import os
import sys
from pathlib import Path

# Console Windows costuma ser cp1252 — evita UnicodeEncodeError ao imprimir emojis.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Rede corporativa com interceptação TLS: usa o trust store do SO (CA corporativa).
# Opcional: só ativa se o pacote 'truststore' estiver instalado.
try:
    import truststore

    truststore.inject_into_ssl()
except Exception:
    pass

# Torna o pacote 'src' importável (reutilização das funções prontas).
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv()

from langsmith import Client
from langchain_core.tracers.context import collect_runs
from langchain_core.tracers.langchain import wait_for_all_tracers

import evaluate as ev  # reutiliza get_llm, pull_prompt_from_langsmith, create_evaluation_dataset
from metrics import evaluate_f1_score, evaluate_clarity, evaluate_precision
from utils import check_env_vars, print_section_header, format_score

# Métricas base que também gravaremos como feedback.
BASE_KEYS = ("f1_score", "clarity", "precision")


def _create_feedback(client: Client, run_id, key: str, score: float, comment: str = "") -> None:
    """Grava um feedback numérico no run; falhas não interrompem a avaliação."""
    try:
        client.create_feedback(
            run_id=run_id,
            key=key,
            score=score,
            comment=(comment or "")[:2000],
        )
    except Exception as e:
        print(f"      ⚠️  Falha ao gravar feedback '{key}' no run {run_id}: {e}")


def evaluate_and_log(prompt_name: str, dataset_name: str, client: Client, limit: int | None = None) -> dict:
    prompt_template = ev.pull_prompt_from_langsmith(prompt_name)

    examples = list(client.list_examples(dataset_name=dataset_name))
    if limit:
        examples = examples[:limit]
    print(f"   Dataset: {len(examples)} exemplo(s) a avaliar")

    llm = ev.get_llm()
    chain = prompt_template | llm

    acc = {"f1_score": [], "clarity": [], "precision": [], "helpfulness": [], "correctness": []}

    for i, example in enumerate(examples, 1):
        inputs = example.inputs or {}
        outputs = example.outputs or {}
        reference = outputs.get("reference", "") if isinstance(outputs, dict) else ""
        question = inputs.get("bug_report", inputs.get("question", "N/A")) if isinstance(inputs, dict) else "N/A"

        # Captura o run_id da geração da resposta (o run que aparece no tracing).
        with collect_runs() as cb:
            response = chain.invoke(inputs)
        # Garante que o run foi enviado ao LangSmith antes de anexar feedback.
        wait_for_all_tracers()
        run_id = cb.traced_runs[0].id if cb.traced_runs else None
        answer = response.content

        f1 = evaluate_f1_score(question, answer, reference)
        clarity = evaluate_clarity(question, answer, reference)
        precision = evaluate_precision(question, answer, reference)

        results = {"f1_score": f1, "clarity": clarity, "precision": precision}
        for key in BASE_KEYS:
            acc[key].append(results[key]["score"])

        helpfulness = round((clarity["score"] + precision["score"]) / 2, 4)
        correctness = round((f1["score"] + precision["score"]) / 2, 4)
        acc["helpfulness"].append(helpfulness)
        acc["correctness"].append(correctness)

        if run_id:
            for key in BASE_KEYS:
                _create_feedback(client, run_id, key, results[key]["score"], results[key].get("reasoning", ""))
            _create_feedback(client, run_id, "helpfulness", helpfulness)
            _create_feedback(client, run_id, "correctness", correctness)

        status = "run=" + str(run_id) if run_id else "run=N/D (tracing off?)"
        print(
            f"      [{i}/{len(examples)}] f1={f1['score']:.2f} clarity={clarity['score']:.2f} "
            f"precision={precision['score']:.2f} help={helpfulness:.2f} corr={correctness:.2f} | {status}"
        )

    return {k: (round(sum(v) / len(v), 4) if v else 0.0) for k, v in acc.items()}


def main() -> int:
    print_section_header("AVALIAÇÃO + FEEDBACK NO LANGSMITH (Option A)")

    provider = os.getenv("LLM_PROVIDER", "openai")
    required = ["LANGSMITH_API_KEY", "LLM_PROVIDER"]
    required.append("OPENAI_API_KEY" if provider == "openai" else "GOOGLE_API_KEY")
    if not check_env_vars(required):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB", "")
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurada no .env")
        return 1

    # Aceita um limite opcional de exemplos como primeiro argumento (smoke test).
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print(f"⚠️  Argumento inválido '{sys.argv[1]}', ignorando (avaliando todos).")

    client = Client()
    project_name = os.getenv("LANGSMITH_PROJECT", "prompt-optimization-challenge-resolved").strip().strip('"')
    dataset_name = f"{project_name}-eval"

    jsonl_path = "datasets/bug_to_user_story.jsonl"
    ev.create_evaluation_dataset(client, dataset_name, jsonl_path)

    prompt_name = f"{username}/bug_to_user_story_v2"
    print(f"\n🔍 Avaliando e gravando feedback: {prompt_name}")

    scores = evaluate_and_log(prompt_name, dataset_name, client, limit=limit)

    print("\n" + "=" * 50)
    print("MÉDIAS (também gravadas como feedback por run)")
    print("=" * 50)
    for key in ("helpfulness", "correctness", "f1_score", "clarity", "precision"):
        print(f"  - {key}: {format_score(scores[key], threshold=0.8)}")

    print(f"\n✓ Feedback gravado. Abra o projeto no LangSmith e adicione as colunas de feedback:")
    print(f"  https://smith.langchain.com/projects/{project_name}")
    print("  (aba Runs → seletor de colunas → f1_score, clarity, precision, helpfulness, correctness)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
