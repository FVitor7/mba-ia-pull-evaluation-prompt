"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_SOURCE = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = "prompts/bug_to_user_story_v1.yml"


def pull_prompts_from_langsmith():
    """
    Faz pull do prompt do LangSmith Hub e salva localmente em YAML.

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        client = Client()
        print(f"Fazendo pull do prompt: {PROMPT_SOURCE}")
        prompt = client.pull_prompt(PROMPT_SOURCE, dangerously_pull_public_prompt=True)

        system_prompt = ""
        user_prompt = ""

        for message in prompt.messages:
            cls_name = message.__class__.__name__
            template = ""
            if hasattr(message, "prompt") and hasattr(message.prompt, "template"):
                template = message.prompt.template
            elif hasattr(message, "content"):
                template = message.content

            if "System" in cls_name:
                system_prompt = template
            elif "Human" in cls_name:
                user_prompt = template

        yaml_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }

        if save_yaml(yaml_data, OUTPUT_PATH):
            print(f"   Prompt salvo em: {OUTPUT_PATH}")
            return True
        else:
            print(f"   Erro ao salvar prompt em: {OUTPUT_PATH}")
            return False

    except Exception as e:
        print(f"Erro ao fazer pull do prompt: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    if pull_prompts_from_langsmith():
        print("\nPull concluido com sucesso!")
        return 0
    else:
        print("\nFalha no pull dos prompts.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
