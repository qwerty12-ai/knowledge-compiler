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

    if unit.kind == "function":
        observations.append(f"The unit defines a function named {unit.name}.")
    elif unit.kind == "class":
        observations.append(f"The unit defines a class named {unit.name}.")
    elif unit.kind == "documentation":
        observations.append("The unit contains documentation.")

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
                    "You are a software repository investigator. "
                    "Analyze the supplied unit and report observations "
                    "supported by its content. Do not invent behavior, "
                    "intent, or evidence. If the content is insufficient, "
                    "return no observations. Return JSON with an "
                    "'observations' array containing strings."
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
            "num_predict": 256
        }
    )

    data = json.loads(response.message.content)
    model_observations = data.get("observations", [])

    if not isinstance(model_observations, list) or not all(isinstance(item, str) for item in model_observations):
        raise ValueError("Model response must contain an observations array of strings.")

    observations.extend(model_observations)

    return InvestigationResult(unit=unit, observations=tuple(observations))