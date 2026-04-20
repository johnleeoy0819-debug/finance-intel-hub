import json
from typing import Any, Dict, List

from openai import OpenAI
from src.config import settings
from src.prompts.loader import PromptLoader


class AIClient:
    def __init__(self):
        client_kwargs = {"api_key": settings.OPENAI_API_KEY}
        if settings.OPENAI_BASE_URL:
            client_kwargs["base_url"] = settings.OPENAI_BASE_URL
        self.client = OpenAI(**client_kwargs)
        self.loader = PromptLoader()

    def _get_user_rules(self) -> str:
        """Fetch user rules from database."""
        try:
            from src.db.engine import SessionLocal
            from src.db.models import UserRule
            db = SessionLocal()
            try:
                rule = db.query(UserRule).first()
                if rule and rule.rules:
                    return f"\n\n【用户自定义规则】\n{rule.rules}"
            finally:
                db.close()
        except Exception:
            pass
        return ""

    def run_prompt(self, name: str, model: str = None, fewshot_field: str = None, **kwargs) -> str:
        """Load a prompt by name, render it with variables, and call OpenAI API.

        If SKILL_EVOLUTION_ENABLED and fewshot_field is provided, inject few-shot
        examples from user corrections before the main user message.
        """
        prompt = self.loader.load(name)
        rendered = self.loader.render(prompt, **kwargs)

        use_model = model or prompt.get("model", settings.OPENAI_MODEL_FAST)

        # Inject user rules into system prompt
        user_rules = self._get_user_rules()
        system_content = rendered["system"] + user_rules

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_content},
        ]

        # Inject few-shot examples from corrections if enabled
        if settings.SKILL_EVOLUTION_ENABLED and fewshot_field:
            from src.core.feedback import build_fewshot_samples
            samples = build_fewshot_samples(field=fewshot_field, limit=3)
            for sample in samples:
                messages.append({"role": "user", "content": sample["input"]})
                messages.append({"role": "assistant", "content": sample["output"]})

        messages.append({"role": "user", "content": rendered["user"]})

        kwargs = {"model": use_model, "messages": messages}
        # Kimi K2.5 uses fixed temperature; passing custom value errors out
        if "kimi-k2" not in use_model:
            kwargs["temperature"] = 0.3
        response = self.client.chat.completions.create(**kwargs)

        return response.choices[0].message.content

    def run_prompt_json(self, name: str, model: str = None, fewshot_field: str = None, **kwargs) -> Dict[str, Any]:
        """Run a prompt and parse the response as JSON."""
        content = self.run_prompt(name, model=model, fewshot_field=fewshot_field, **kwargs)
        # Try to extract JSON from markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)
