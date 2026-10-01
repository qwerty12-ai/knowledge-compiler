from pathlib import Path
from knowledge_compiler.investigation import InvestigationUnit
from knowledge_compiler.context import build_repository_context
from knowledge_compiler.investigation import build_investigation_units


def test_investigation_unit_can_be_created():
    unit = InvestigationUnit(
        source=Path("src/payments.py"),
        name="execute_payment",
        kind="function",
        content="def execute_payment():\n    pass\n",
        line_start=10,
        line_end=11,
    )

    assert unit.source == Path("src/payments.py")
    assert unit.name == "execute_payment"
    assert unit.kind == "function"
    assert unit.content == "def execute_payment():\n    pass\n"
    assert unit.line_start == 10
    assert unit.line_end == 11


def test_investigation_unit_allows_missing_line_numbers():
    unit = InvestigationUnit(
        source=Path("README.md"),
        name="README.md",
        kind="documentation",
        content="# Payment Service\n",
    )

    assert unit.line_start is None
    assert unit.line_end is None

def test_build_investigation_units_extracts_functions(tmp_path: Path):
    source_file = tmp_path / "payment.py"
    source_file.write_text(
        "def execute_payment():\n"
        "    return True\n"
    )

    context = build_repository_context(tmp_path)
    units = build_investigation_units(context)

    assert len(units) == 1

    unit = units[0]
    assert unit.name == "execute_payment"
    assert unit.kind == "function"
    assert unit.source == source_file
    assert unit.content == (
        "def execute_payment():\n"
        "    return True"
    )
    assert unit.line_start == 1
    assert unit.line_end == 2


def test_build_investigation_units_extracts_classes(tmp_path: Path):
    source_file = tmp_path / "payment.py"
    source_file.write_text(
        "class PaymentService:\n"
        "    def execute(self):\n"
        "        return True\n"
    )

    context = build_repository_context(tmp_path)
    units = build_investigation_units(context)

    class_units = [
        unit for unit in units
        if unit.kind == "class"
    ]

    assert len(class_units) == 1

    unit = class_units[0]
    assert unit.name == "PaymentService"
    assert unit.content == (
        "class PaymentService:\n"
        "    def execute(self):\n"
        "        return True"
    )
    assert unit.line_start == 1
    assert unit.line_end == 3

def test_build_investigation_units_includes_documentation(
    tmp_path: Path,
):
    readme_file = tmp_path / "README.md"
    readme_file.write_text("# Payment Service\n")

    context = build_repository_context(tmp_path)
    units = build_investigation_units(context)

    documentation_units = [
        unit for unit in units
        if unit.kind == "documentation"
    ]

    assert len(documentation_units) == 1
    assert documentation_units[0].name == "README.md"
    assert documentation_units[0].content == "# Payment Service\n"