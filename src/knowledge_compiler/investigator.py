import json
import ollama
from dataclasses import dataclass
from knowledge_compiler.investigation import InvestigationUnit

@dataclass(frozen=True)
class InvestigationResult:
    unit: InvestigationUnit
    observations: tuple[str,...]

def investigate(unit: InvestigationUnit,client=None) -> InvestigationResult:

    observations = []

    if client is None:
        client = ollama.Client()

    response = client.chat(
        model="qwen3:4b",
        think=False,
        format="json",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a software repository investigator."
                    "Analyze the supplied code unit to identify its purpose, behavior, constraints, side effects, dependencies, or important design decisions."
                    "Return only observations that are directly supported by the supplied content. Do not merely restate the unit's name or its type. Explain what the code actually does."
                    "Do not infer developer intent unless the content provides evidence. Do not invent behavior or evidence. If the content does not support a useful observation beyond its name or type, return an empty observations array."
                    "Return valid JSON with an 'observations' array containing strings."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Unit kind: {unit.kind}\n"
                    f"Unit name: {unit.name}\n"
                    f"Source: {unit.source}\n"
                    f"Content:\n{unit.content}"
                )
            }
        ],
        options={
            "num_predict": 512,
            "temperature": 0.2,
            "repeat_penalty": 1.1
        }
    )

    try:
        data = json.loads(response.message.content)
    except json.JSONDecodeError:
        data = {}

    model_observations = (data.get("observations", []) if isinstance(data, dict) else [])
    if(isinstance(data, dict) and isinstance(model_observations, list) and all(isinstance(item,str) for item in model_observations)):
        observations.extend(item.strip() for item in model_observations if item.strip())

    return InvestigationResult(
        unit=unit,
        observations=tuple(observations)
    )