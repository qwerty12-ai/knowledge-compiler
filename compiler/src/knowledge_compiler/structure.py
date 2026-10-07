import ast
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class CodeFunction:
    name: str
    source: Path
    line_start: int
    line_end: int
    parent_class: str | None = None

@dataclass(frozen=True)
class CodeClass:
    name: str
    source: Path
    line_start: int
    line_end: int

@dataclass(frozen=True)
class CodeImport:
    module: str
    source: Path
    line: int

@dataclass(frozen=True)
class CodeStructure:
    source: Path
    functions: tuple[CodeFunction,...]
    classes: tuple[CodeClass,...]
    imports: tuple[CodeImport,...]

class StructureVisitor(ast.NodeVisitor):
    def __init__(self, file_path: Path, source_path: Path):
        self.file_path = source_path
        self.functions = []
        self.classes = []
        self.imports = []
        self.class_stack = []
        self.function_stack = []

    def visit_ClassDef(self, node):
        self.classes.append(
            CodeClass(
                name=node.name,
                source=self.file_path,
                line_start=node.lineno,
                line_end=node.end_lineno,
            )
        )

        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()

    def visit_FunctionDef(self, node):
        parent_class = (
            self.class_stack[-1]
            if self.class_stack and not self.function_stack
            else None
        )

        self.functions.append(
            CodeFunction(
                name=node.name,
                source=self.file_path,
                line_start=node.lineno,
                line_end=node.end_lineno,
                parent_class=parent_class,
            )
        )

        self.function_stack.append(node.name)
        self.generic_visit(node)
        self.function_stack.pop()

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(
                CodeImport(
                    module=alias.name,
                    source=self.file_path,
                    line=node.lineno,
                )
            )

        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module is not None:
            self.imports.append(
                CodeImport(
                    module=node.module,
                    source=self.file_path,
                    line=node.lineno,
                )
            )

        self.generic_visit(node)

def extract_structure(file_path: Path, source_path: Path) -> CodeStructure:
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    visitor = StructureVisitor(file_path, source_path)
    visitor.visit(tree)

    return CodeStructure(
        source=source_path,
        functions=tuple(visitor.functions), 
        classes=tuple(visitor.classes),
        imports=tuple(visitor.imports)
    )