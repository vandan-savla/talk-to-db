import copy

from langchain_groq import ChatGroq
from pydantic import BaseModel


def _close_object_schemas(schema: dict) -> dict:
    if isinstance(schema, dict):
        if schema.get("type") == "object":
            schema.setdefault("additionalProperties", False)
        for value in schema.values():
            _close_object_schemas(value)
    elif isinstance(schema, list):
        for item in schema:
            _close_object_schemas(item)
    return schema


def invoke_groq_structured(
    *,
    schema_model: type[BaseModel],
    messages: list,
    model_name: str,
    groq_api_key: str | None,
):
    schema = _close_object_schemas(copy.deepcopy(schema_model.model_json_schema()))
    llm = ChatGroq(model=model_name, groq_api_key=groq_api_key).bind(
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema_model.__name__,
                "strict": True,
                "schema": schema,
            },
        }
    )
    response = llm.invoke(messages)
    return schema_model.model_validate_json(response.content)
