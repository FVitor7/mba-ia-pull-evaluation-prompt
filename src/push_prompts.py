"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)
"""

import os
import sys
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_FILE = "prompts/bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt (sem username)
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        username = os.getenv("USERNAME_LANGSMITH_HUB", "")
        if not username:
            print("USERNAME_LANGSMITH_HUB nao configurada no .env")
            return False

        full_name = f"{username}/{prompt_name}"

        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "{bug_report}")

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        client = Client()
        print(f"   Fazendo push para: {full_name}")
        try:
            client.push_prompt(full_name, object=prompt_template, is_public=True)
        except TypeError:
            client.push_prompt(full_name, object=prompt_template)
            print(f"   IMPORTANTE: Torne o prompt publico manualmente no LangSmith Hub")
        print(f"   Prompt publicado com sucesso: {full_name}")

        return True

    except Exception as e:
        print(f"   Erro ao fazer push: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt.

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    system_prompt = prompt_data.get("system_prompt", "").strip()
    if not system_prompt:
        errors.append("system_prompt esta vazio")

    user_prompt = prompt_data.get("user_prompt", "").strip()
    if not user_prompt:
        errors.append("user_prompt esta vazio")

    if "TODO" in system_prompt or "[TODO]" in system_prompt:
        errors.append("system_prompt contem TODOs nao resolvidos")

    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(f"Minimo de 2 tecnicas requeridas, encontradas: {len(techniques)}")

    if not prompt_data.get("description", "").strip():
        errors.append("description esta vazio")

    if not prompt_data.get("version", "").strip():
        errors.append("version esta vazio")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS AO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    print(f"Carregando prompt de: {PROMPT_FILE}")
    data = load_yaml(PROMPT_FILE)
    if not data:
        print(f"Erro ao carregar arquivo: {PROMPT_FILE}")
        return 1

    prompt_data = data.get(PROMPT_KEY)
    if not prompt_data:
        print(f"Chave '{PROMPT_KEY}' nao encontrada no YAML")
        return 1

    print("\nValidando prompt...")
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("Prompt invalido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("   Prompt valido!\n")

    print(f"Tecnicas aplicadas: {', '.join(prompt_data.get('techniques_applied', []))}")
    print(f"Tags: {', '.join(prompt_data.get('tags', []))}")
    print(f"Versao: {prompt_data.get('version', 'N/A')}\n")

    if push_prompt_to_langsmith(PROMPT_KEY, prompt_data):
        username = os.getenv("USERNAME_LANGSMITH_HUB", "")
        print(f"\nPush concluido com sucesso!")
        print(f"Verifique em: https://smith.langchain.com/hub/{username}/{PROMPT_KEY}")
        return 0
    else:
        print("\nFalha no push do prompt.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
