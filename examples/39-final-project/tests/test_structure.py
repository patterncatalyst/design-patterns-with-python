"""Only the composition root names a concrete carrier."""

import ast
from pathlib import Path

import final_project

_CONCRETE = {"FastlineGateway", "FastlineClient"}


def _names(tree: ast.AST) -> set[str]:
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) for a in n.names}
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    return (imported | used) & _CONCRETE


def test_only_the_composition_root_names_a_concrete_carrier() -> None:
    """Credits ``build_desk``: importing the gateway in ``desk.py`` adds that module to the list."""
    package = Path(final_project.__file__).parent
    naming = sorted(
        path.name
        for path in package.glob("*.py")
        if path.name != "carriers.py" and _names(ast.parse(path.read_text()))
    )

    assert naming == ["app.py"]
