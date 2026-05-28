"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def prompt_data():
    """Carrega e retorna os dados do prompt v2."""
    data = load_prompts(str(PROMPT_FILE))
    return data[PROMPT_KEY]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' nao encontrado no YAML"
        system_prompt = prompt_data["system_prompt"].strip()
        assert len(system_prompt) > 0, "system_prompt esta vazio"
        assert len(system_prompt) > 100, "system_prompt parece muito curto para ser funcional"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: 'Você é um Product Manager')."""
        system_prompt = prompt_data["system_prompt"].lower()
        role_keywords = [
            "voce e um", "você é um",
            "voce e uma", "você é uma",
            "product manager", "business analyst",
            "especialista", "senior",
            "persona", "papel",
        ]
        has_role = any(keyword in system_prompt for keyword in role_keywords)
        assert has_role, (
            "system_prompt nao define uma persona/role. "
            "Deve conter algo como 'Voce e um Product Manager' ou similar"
        )

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data["system_prompt"].lower()
        format_keywords = [
            "user story", "como um", "eu quero", "para que",
            "criterios de aceitacao", "dado que", "quando", "entao",
            "markdown", "formato",
        ]
        matches = [kw for kw in format_keywords if kw in system_prompt]
        assert len(matches) >= 3, (
            f"system_prompt nao menciona formato suficiente. "
            f"Encontrados: {matches}. Esperado pelo menos 3 keywords de formato"
        )

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data["system_prompt"].lower()
        has_example_marker = any(kw in system_prompt for kw in [
            "exemplo", "example", "few-shot", "entrada", "saida",
        ])
        assert has_example_marker, "system_prompt nao contem exemplos (few-shot)"

        has_input = any(kw in system_prompt for kw in ["entrada", "input", "bug report", "bug simples"])
        has_output = any(kw in system_prompt for kw in ["saida", "output", "como um"])
        assert has_input and has_output, (
            "Exemplos few-shot devem conter tanto entrada quanto saida"
        )

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum [TODO] no texto."""
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "")
        description = prompt_data.get("description", "")

        full_text = f"{system_prompt} {user_prompt} {description}"
        assert "[TODO]" not in full_text, "Prompt contem [TODO] nao resolvido"
        assert "TODO:" not in full_text, "Prompt contem TODO: nao resolvido"

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied", [])
        assert isinstance(techniques, list), "techniques_applied deve ser uma lista"
        assert len(techniques) >= 2, (
            f"Minimo de 2 tecnicas requeridas, encontradas: {len(techniques)}. "
            f"Tecnicas: {techniques}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
