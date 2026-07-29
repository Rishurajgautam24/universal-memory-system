from ums.llm.interface import LLMProvider


class ModelRouter:
    def __init__(self, provider: LLMProvider):
        self._provider = provider

    @property
    def provider(self) -> LLMProvider:
        return self._provider

    def get(self, task: str) -> LLMProvider:
        return self._provider
