from pathlib import Path
from typing import Any, Dict

import yaml
from jinja2 import Template


class PromptLoader:
    def __init__(self, version: str = "v1"):
        self.prompts_dir = Path(__file__).parent / version
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Prompt version directory not found: {self.prompts_dir}")

    def load(self, name: str) -> Dict[str, Any]:
        path = self.prompts_dir / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Prompt not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            prompt = yaml.safe_load(f)

        # Validate required fields
        required = ["version", "name", "system", "user"]
        for field in required:
            if field not in prompt:
                raise ValueError(f"Prompt '{name}' missing required field: {field}")

        return prompt

    def render(self, prompt: Dict[str, Any], **kwargs) -> Dict[str, str]:
        """Render system and user templates with given variables."""
        return {
            "system": Template(prompt["system"]).render(**kwargs),
            "user": Template(prompt["user"]).render(**kwargs),
        }
