import json
from pathlib import Path
from knowledge_compiler.investigation import InvestigationUnit
from knowledge_compiler.investigator import InvestigationResult, investigate

class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeResponse:
    def __init__(self, content):
        self.message = FakeMessage(content)


class FakeOllamaClient:
    def __init__(self, observations=None):
        self.messages = None
        self.observations = (observations if observations is not None else [])

    def chat(self, **kwargs):
        self.messages = kwargs["messages"]
        return FakeResponse(
            json.dumps(
                {
                    "observations": self.observations
                }
            )
        )

def test_investigation_result_stores_unit_and_observations():
    unit = InvestigationUnit(
        source=Path("src/payments.py"),
        name="process_payment",
        kind="function",
        content="def process_payment():\n    pass",
        line_start=1,
        line_end=2,
    )

    result = InvestigationResult(
        unit=unit,
        observations=("The function processes a payment.",),
    )

    assert result.unit == unit
    assert result.observations == (
        "The function processes a payment.",
    )

def test_investigate_returns_result_for_unit():
    unit = InvestigationUnit(
        source=Path("src/payments.py"),
        name="process_payment",
        kind="function",
        content="def process_payment():\n    pass",
        line_start=1,
        line_end=2,
    )

    result = investigate(unit, client=FakeOllamaClient())

    assert isinstance(result, InvestigationResult)
    assert result.unit == unit

def test_investigate_observes_function_name():
    unit = InvestigationUnit(
        source=Path("src/payments.py"),
        name="process_payment",
        kind="function",
        content="def process_payment():\n    pass",
        line_start=1,
        line_end=2,
    )

    result = investigate(unit, client=FakeOllamaClient())

    assert "The unit defines a function named process_payment." in (
        result.observations
    )

def test_investigate_observes_class_name():
    unit = InvestigationUnit(
        source=Path("src/payments.py"),
        name="PaymentProcessor",
        kind="class",
        content="class PaymentProcessor:\n    pass",
        line_start=1,
        line_end=2,
    )

    result = investigate(unit, client=FakeOllamaClient())

    assert (
        "The unit defines a class named PaymentProcessor."
        in result.observations
    )


def test_investigate_observes_documentation():
    unit = InvestigationUnit(
        source=Path("README.md"),
        name="README.md",
        kind="documentation",
        content="# Payment Service",
    )

    result = investigate(unit, client=FakeOllamaClient())

    assert (
        "The unit contains documentation."
        in result.observations
    )




def test_investigate_uses_model_response():
    unit = InvestigationUnit(
        source=Path("src/math_utils.py"),
        name="add",
        kind="function",
        content="def add(a, b):\n    return a + b",
        line_start=1,
        line_end=2,
    )
    client = FakeOllamaClient( 
        observations=[
            "The function returns the sum of two values."
        ]
    )

    result = investigate(unit, client=client)

    assert result.unit == unit
    assert result.observations == (
        "The unit defines a function named add.",
        "The function returns the sum of two values.",
    )
    assert client.messages is not None