"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

# Prompt de baixa qualidade publicado no Hub que servirá de ponto de partida.
SOURCE_PROMPT = "leonanluppi/bug_to_user_story_v1"
OUTPUT_FILE = "prompts/bug_to_user_story_v1.yml"
TOP_LEVEL_KEY = "bug_to_user_story_v1"


def _extract_template_text(message_template) -> str:
    """
    Extrai o texto (template) de uma mensagem de um ChatPromptTemplate.

    Suporta SystemMessagePromptTemplate / HumanMessagePromptTemplate (que
    possuem um atributo .prompt.template) e PromptTemplate simples.
    """
    # Mensagens de chat encapsulam um PromptTemplate em .prompt
    prompt = getattr(message_template, "prompt", None)
    if prompt is not None and hasattr(prompt, "template"):
        return prompt.template

    # Fallback: PromptTemplate direto
    if hasattr(message_template, "template"):
        return message_template.template

    return ""


def extract_prompts_from_template(prompt_template) -> dict:
    """
    Converte um objeto de prompt do LangChain em um dicionário serializável.

    Args:
        prompt_template: Objeto retornado por hub.pull (geralmente ChatPromptTemplate)

    Returns:
        Dicionário com system_prompt e user_prompt extraídos.
    """
    system_prompt = ""
    user_prompt = ""

    messages = getattr(prompt_template, "messages", None)

    if messages:
        for message in messages:
            role = message.__class__.__name__.lower()
            text = _extract_template_text(message)

            if "system" in role:
                system_prompt = text
            elif "human" in role or "user" in role:
                user_prompt = text
    else:
        # PromptTemplate simples (sem mensagens) — tudo vira system_prompt
        system_prompt = _extract_template_text(prompt_template)

    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
    }


def pull_prompts_from_langsmith() -> bool:
    """
    Faz pull do prompt inicial do LangSmith Hub e salva localmente em YAML.

    Returns:
        True se sucesso, False caso contrário.
    """
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return False

    try:
        print(f"Puxando prompt do LangSmith Hub: {SOURCE_PROMPT}")
        prompt_template = hub.pull(SOURCE_PROMPT)
        print("   ✓ Prompt carregado com sucesso")

        extracted = extract_prompts_from_template(prompt_template)

        if not extracted["system_prompt"] and not extracted["user_prompt"]:
            print("❌ Não foi possível extrair o conteúdo do prompt.")
            return False

        prompt_data = {
            TOP_LEVEL_KEY: {
                "description": "Prompt inicial (baixa qualidade) para converter bugs em User Stories",
                "system_prompt": extracted["system_prompt"],
                "user_prompt": extracted["user_prompt"],
                "version": "v1",
                "source": SOURCE_PROMPT,
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }

        if save_yaml(prompt_data, OUTPUT_FILE):
            print(f"   ✓ Prompt salvo localmente em: {OUTPUT_FILE}")
            return True

        return False

    except Exception as e:
        print(f"\n❌ Erro ao fazer pull do prompt '{SOURCE_PROMPT}': {e}")
        print("\nVerifique:")
        print("- LANGSMITH_API_KEY está configurada corretamente no .env")
        print("- Você tem acesso ao workspace do LangSmith")
        print("- Sua conexão com a internet está funcionando")
        return False


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    success = pull_prompts_from_langsmith()

    if success:
        print("\n✅ Pull concluído com sucesso!")
        print("\nPróximos passos:")
        print(f"1. Analise o prompt em {OUTPUT_FILE}")
        print("2. Crie a versão otimizada em prompts/bug_to_user_story_v2.yml")
        print("3. Faça push: python src/push_prompts.py")
        return 0
    else:
        print("\n❌ Falha ao fazer pull do prompt.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
