import os
from backend.app.config.settings import settings

class PromptBuilder:
    """
    Builds the final prompt by injecting the deterministic context into the chosen prompt template.
    """
    @staticmethod
    def build_prompt(context_str: str) -> str:
        prompt_version = settings.REASONING_PROMPT_VERSION
        prompt_path = os.path.join(os.getcwd(), "prompts", f"{prompt_version}.txt")
        
        # Fallback to a default if the file is missing, or raise an error.
        if not os.path.exists(prompt_path):
            raise FileNotFoundError(f"Prompt template {prompt_path} not found.")

        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()
        
        # Inject the context securely.
        return template.replace("{{CONTEXT}}", context_str)
