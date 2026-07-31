from ums.llm.interface import LLMMessage


def entity_extraction_prompt(content: str) -> list[LLMMessage]:
    return [
        LLMMessage(
            role="system",
            content=(
                "You are an entity extraction system. Extract all named entities "
                "(people, organizations, locations, concepts, events, objects) "
                "from the given text. Return a JSON array of objects, each with "
                "'name', 'type', and 'description' fields."
            ),
        ),
        LLMMessage(role="user", content=content),
    ]


def observation_extraction_prompt(content: str) -> list[LLMMessage]:
    return [
        LLMMessage(
            role="system",
            content=(
                "You are an observation extraction system. Extract factual "
                "observations, attributes, and relationships about entities from "
                "the given text. Return a JSON array of objects, each with "
                "'statement', 'confidence' (0.0-1.0), and 'category' fields. "
                "The 'category' should be one of: CONVERSATION, DOCUMENT, CODE, "
                "REFLECTION, WEB, MANUAL, SYSTEM. The 'statement' should be a "
                "concise factual observation."
            ),
        ),
        LLMMessage(role="user", content=content),
    ]


def relationship_extraction_prompt(content: str) -> list[LLMMessage]:
    return [
        LLMMessage(
            role="system",
            content=(
                "You are a relationship extraction system. Extract semantic "
                "relationships between entities from the given text. Return a JSON "
                "array of objects, each with 'source', 'target', 'relation_type', "
                "'description', and 'strength' (0.0-1.0) fields."
            ),
        ),
        LLMMessage(role="user", content=content),
    ]