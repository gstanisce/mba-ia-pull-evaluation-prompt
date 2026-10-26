"""
Testes automatizados para validação de prompts.

Validam o prompt otimizado em prompts/bug_to_user_story_v2.yml quanto aos
requisitos do desafio: system prompt, persona, formato, few-shot, ausência de
TODOs e uso de pelo menos 2 técnicas de prompt engineering.
"""
import re
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_prompt_data():
    """
    Carrega o prompt v2 e normaliza o retorno para o dicionário interno,
    aceitando tanto o formato aninhado (chave 'bug_to_user_story_v2') quanto plano.
    """
    data = load_prompts(str(PROMPT_FILE))
    assert data, f"Arquivo de prompt vazio ou não encontrado: {PROMPT_FILE}"
    return data.get("bug_to_user_story_v2", data)


class TestPrompts:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.prompt = load_prompt_data()
        self.system_prompt = self.prompt.get("system_prompt", "") or ""
        self.user_prompt = self.prompt.get("user_prompt", "") or ""
        self.full_text = f"{self.system_prompt}\n{self.user_prompt}"

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in self.prompt, "Campo 'system_prompt' ausente"
        assert self.system_prompt.strip(), "'system_prompt' está vazio"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        assert re.search(
            r"voc[êe]\s+é\s+um", self.system_prompt, re.IGNORECASE
        ), "O system_prompt não define uma persona (ex.: 'Você é um Product Manager')"

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        text_lower = self.full_text.lower()
        indicators = [
            "markdown",
            "como um",
            "eu quero",
            "para que",
            "critérios de aceitação",
            "user story",
        ]
        assert any(ind in text_lower for ind in indicators), (
            "O prompt não especifica o formato de saída (Markdown / User Story padrão)"
        )

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        text_lower = self.full_text.lower()
        # Sinal explícito de exemplos + múltiplas ocorrências do formato de saída
        has_example_marker = "exemplo" in text_lower or (
            "relato de bug:" in text_lower and "user story:" in text_lower
        )
        story_count = text_lower.count("como um")
        assert has_example_marker and story_count >= 2, (
            "O prompt não contém exemplos de entrada/saída suficientes (Few-shot)"
        )

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        # Checagem sensível a maiúsculas (alinhada a utils.validate_prompt_structure):
        # a palavra portuguesa "todos" é minúscula e não deve gerar falso positivo;
        # buscamos marcadores de placeholder deixados por engano (TODO / [TODO]).
        assert "[TODO]" not in self.full_text, "O prompt ainda contém placeholders [TODO]"
        assert "TODO" not in self.full_text, "O prompt ainda contém marcadores TODO"

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = self.prompt.get("techniques_applied", [])
        assert isinstance(techniques, list), "'techniques_applied' deve ser uma lista"
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])