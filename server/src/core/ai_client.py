import json
from typing import Any, Dict

from openai import OpenAI
from src.config import settings
from src.prompts.loader import PromptLoader


class AIClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.loader = PromptLoader()

    def run_prompt(self, name: str, model: str = None, **kwargs) -> str:
        """Load a prompt by name, render it with variables, and call OpenAI API."""
        prompt = self.loader.load(name)
        rendered = self.loader.render(prompt, **kwargs)

        use_model = model or prompt.get("model", settings.OPENAI_MODEL_FAST)

        response = self.client.chat.completions.create(
            model=use_model,
            messages=[
                {"role": "system", "content": rendered["system"]},
                {"role": "user", "content": rendered["user"]},
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content

    def run_prompt_json(self, name: str, model: str = None, **kwargs) -> Dict[str, Any]:
        """Run a prompt and parse the response as JSON."""
        content = self.run_prompt(name, model=model, **kwargs)
        # Try to extract JSON from markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)
