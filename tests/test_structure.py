import pytest
from pathlib import Path
from knowledge_compiler.structure import extract_structure

def test_extracts_function(tmp_path):
    source = """
def hello():
    return "world"
"""

    file_path = tmp_path / "example.py"
    file_path.write_text(source)

    structure = extract_structure(file_path)

    assert len(structure.functions) == 1

    assert structure.functions[0].name == "hello"

def test_extracts_classes(tmp_path):
    source = """
class PaymentService:
    pass
"""

    file_path = tmp_path / "example.py"
    file_path.write_text(source)

    structure = extract_structure(file_path)

    assert len(structure.classes) == 1

    assert structure.classes[0].name == "PaymentService"

def test_extracts_imports(tmp_path):
    source = """
import os
from pathlib import Path
"""

    file_path = tmp_path / "example.py"
    file_path.write_text(source)
    
    structure = extract_structure(file_path)
    
    assert len(structure.imports) == 2

    assert structure.imports[0].module == "os"
    assert structure.imports[1].module == "pathlib"

def test_extracts_function_location(tmp_path):
    source = """
def hello():
    return "world"
    """

    file_path = tmp_path / "example.py"
    file_path.write_text(source)

    structure = extract_structure(file_path)
    function = structure.functions[0]

    assert function.source == file_path
    assert function.line_start == 2
    assert function.line_end == 3

def test_extracts_class_location(tmp_path):
    source = """
class PaymentService:
    pass
"""

    file_path = tmp_path / "example.py"
    file_path.write_text(source)

    structure = extract_structure(file_path)
    code_class = structure.classes[0]

    assert code_class.source == file_path
    assert code_class.line_start == 2
    assert code_class.line_end == 3

def test_extracts_class_method_relationship(tmp_path):
    source = """
class PaymentService:
    def execute(self):
        pass
"""

    file_path = tmp_path / "example.py"
    file_path.write_text(source)

    structure = extract_structure(file_path)
    
    assert len(structure.classes) == 1
    assert len(structure.functions) == 1

    function = structure.functions[0]
    assert function.name == "execute"
    assert function.parent_class == "PaymentService"

def test_extracts_multiple_structures(tmp_path):
    source = """
import os

class PaymentService:
    def execute(self):
        pass

class UserService:
    def create(self):
        pass

def helper():
    pass
"""

    file_path = tmp_path / "example.py"
    file_path.write_text(source)

    structure = extract_structure(file_path)

    assert len(structure.imports) == 1
    assert len(structure.classes) == 2
    assert len(structure.functions) == 3

    assert structure.classes[0].name == "PaymentService"
    assert structure.classes[1].name == "UserService"

    assert structure.functions[0].name == "execute"
    assert structure.functions[0].parent_class == "PaymentService"

    assert structure.functions[1].name == "create"
    assert structure.functions[1].parent_class == "UserService"

    assert structure.functions[2].name == "helper"
    assert structure.functions[2].parent_class is None

def test_extracts_nested_functions(tmp_path):
    source = """
def outer():
    def inner():
        pass
"""

    file_path = tmp_path / "example.py"
    file_path.write_text(source)

    structure = extract_structure(file_path)

    assert len(structure.functions) == 2

    assert structure.functions[0].name == "outer"
    assert structure.functions[0].parent_class is None

    assert structure.functions[1].name == "inner"
    assert structure.functions[1].parent_class is None

def test_rejects_invalid_python(tmp_path):
    source = """
def broken(:
    pass
"""

    file_path = tmp_path / "example.py"
    file_path.write_text(source)

    with pytest.raises(SyntaxError):
        extract_structure(file_path)