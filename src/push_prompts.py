"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()

INPUT_FILE = "prompts/bug_to_user_story_v2.yml"
TOP_LEVEL_KEY = "bug_to_user_story_v2"
PROMPT_NAME = "bug_to_user_story_v2"


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Reutiliza a validação central de utils.validate_prompt_structure, que checa:
    - campos obrigatórios (description, system_prompt, version)
    - system_prompt não vazio e sem TODOs
    - pelo menos 2 técnicas em techniques_applied

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def build_chat_prompt(prompt_data: dict) -> ChatPromptTemplate:
    """
    Monta um ChatPromptTemplate a partir do system_prompt e user_prompt do YAML.

    O user_prompt contém a variável {bug_report}, esperada pelo dataset de avaliação.
    O system_prompt deve ser livre de chaves (formato f-string do ChatPromptTemplate).
    """
    system_prompt = prompt_data["system_prompt"]
    user_prompt = prompt_data.get("user_prompt") or "{bug_report}"

    return ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", user_prompt),
        ]
    )


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt (ex.: 'bug_to_user_story_v2')
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        chat_prompt = build_chat_prompt(prompt_data)

        description = prompt_data.get("description", "")
        techniques = prompt_data.get("techniques_applied", [])
        tags = prompt_data.get("tags", [])

        readme = (
            f"{description}\n\n"
            f"Técnicas aplicadas: {', '.join(techniques)}"
        )

        print(f"Fazendo push (público) para o LangSmith Hub: {prompt_name}")
        url = hub.push(
            prompt_name,
            chat_prompt,
            new_repo_is_public=True,
            new_repo_description=description,
            tags=tags,
            readme=readme,
        )

        print(f"   ✓ Push concluído com sucesso!")
        print(f"   ✓ URL: {url}")
        return True

    except Exception as e:
        print(f"\n❌ Erro ao fazer push do prompt '{prompt_name}': {e}")
        print("\nVerifique:")
        print("- LANGSMITH_API_KEY está configurada corretamente no .env")
        print("- O system_prompt não contém chaves { } soltas (apenas {bug_report} no user_prompt)")
        print("- Sua conexão com a internet está funcionando")
        return False


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS AO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    data = load_yaml(INPUT_FILE)
    if not data:
        print(f"❌ Não foi possível carregar {INPUT_FILE}")
        return 1

    # Aceita tanto o formato aninhado (chave bug_to_user_story_v2) quanto plano.
    prompt_data = data.get(TOP_LEVEL_KEY, data)

    print("Validando estrutura do prompt...")
    is_valid, errors = validate_prompt(prompt_data)

    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("   ✓ Prompt válido\n")

    if push_prompt_to_langsmith(PROMPT_NAME, prompt_data):
        print("\n✅ Push concluído com sucesso!")
        print("\nPróximos passos:")
        print("1. Confira o prompt publicado (e público) em https://smith.langchain.com/prompts")
        print("2. Execute a avaliação: python src/evaluate.py")
        return 0

    print("\n❌ Falha ao fazer push do prompt.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
