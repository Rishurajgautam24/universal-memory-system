from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel


class LLMMessage(BaseModel):
    role: str
    content: str


class LLMResponse(BaseModel):
    content: str
    usage: Optional[dict] = None
    model: str
    provider: str


class LLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def default_model(self) -> str: ...

    @abstractmethod
    async def complete(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> LLMResponse: ...

    @abstractmethod
    async def embed(
        self, texts: List[str], model: Optional[str] = None
    ) -> List[List[float]]: ...
