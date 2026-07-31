from typing import Optional

from ums.llm.interface import LLMProvider
from ums.llm.openrouter import OpenRouterProvider
from ums.llm.router import ModelRouter


def create_llm_router(provider: LLMProvider | None = None) -> ModelRouter:
    return ModelRouter(provider or OpenRouterProvider())
