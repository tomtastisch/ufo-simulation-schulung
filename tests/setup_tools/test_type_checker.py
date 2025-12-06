# tests/setup_tools/test_type_checker.py
from __future__ import annotations

"""
Funktionale Tests für den TypingCheckStep.

Prüft nicht nur die Struktur, sondern auch die tatsächliche Funktionalität:
- Erkennung fehlender Parameter-Annotationen
- Erkennung fehlender Return-Annotationen
- Erkennung fehlender Variablen-Annotationen
- Modi (strict vs. relaxed)
- Konfigurierbarkeit
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from tools.setup.domain import BootstrapConfig, PyProjectProfile
from tools.setup.steps.base import BaseStepContext
from tools.setup.steps.type_checker import (
    TypingCheckStep,
    AnnotationChecker,
)


# ============================================================================
# Test-Fixtures
# ============================================================================

@pytest.fixture
def temp_task_dir(tmp_path: Path) -> Path:
    """Erstellt temporäres src/task/ Verzeichnis."""
    task_dir = tmp_path / "src" / "task"
    task_dir.mkdir(parents=True)
    (task_dir / "__init__.py").write_text("")
    return task_dir


@pytest.fixture
def mock_context(tmp_path: Path) -> BaseStepContext:
    """Erstellt minimalen Mock-Context für Tests."""
    config = BootstrapConfig(repo_root=tmp_path)

    # Minimales Profile mit typing_check Optionen
    profile = PyProjectProfile(
        requires_min_python=(3, 11),
        runtime_requirements={},
        dev_requirements={},
        step_include=tuple(),
        step_exclude=tuple(),
        step_options={
            "typing_check": {
                "mode": "relaxed",
                "check_params": True,
                "check_returns": True,
                "check_variables": False,
            }
        },
        verbosity=1,
        auto_install=True,
        linter_contracts="all",
        pyproject_data={
            "tool": {
                "setup": {
                    "options": {
                        "typing_check": {
                            "mode": "relaxed",
                            "check_params": True,
                            "check_returns": True,
                            "check_variables": False,
                        }
                    }
                }
            }
        },
    )

    # Mock-Console und Mock-Log (nicht relevant für Type-Checker Tests)
    mock_console = Mock()
    mock_log = Mock()

    return BaseStepContext(
        config=config,
        profile=profile,
        console=mock_console,
        log=mock_log,
    )


# ============================================================================
# Tests: AnnotationChecker (AST-Visitor)
# ============================================================================

class TestAnnotationChecker:
    """Tests für den AST-basierten Annotation-Checker."""

    def test_missing_parameter_annotation(self):
        """Erkennt fehlende Parameter-Annotation."""
        code = '''
def calculate(x, y: float) -> float:
    return x + y
'''
        checker = AnnotationChecker(
            mode="relaxed",
            check_variables=False,
            check_params=True,
            check_returns=True,
        )
        checker.set_file("test.py")

        import ast
        tree = ast.parse(code)
        checker.visit(tree)

        # Sollte Parameter 'x' ohne Annotation finden
        assert len(checker.findings) == 1
        finding = checker.findings[0]
        assert finding.name == "x"
        assert finding.type == "parameter"

    def test_missing_return_annotation(self):
        """Erkennt fehlende Return-Annotation."""
        code = '''
def calculate(x: float, y: float):
    return x + y
'''
        checker = AnnotationChecker(
            mode="relaxed",
            check_variables=False,
            check_params=True,
            check_returns=True,
        )
        checker.set_file("test.py")

        import ast
        tree = ast.parse(code)
        checker.visit(tree)

        # Sollte fehlende Return-Annotation finden
        assert len(checker.findings) == 1
        finding = checker.findings[0]
        assert finding.name == "calculate"
        assert finding.type == "return"

    def test_init_no_return_annotation_required(self):
        """__init__ benötigt keine Return-Annotation."""
        code = '''
class Foo:
    def __init__(self, x: int):
        self.x = x
'''
        checker = AnnotationChecker(
            mode="relaxed",
            check_variables=False,
            check_params=True,
            check_returns=True,
        )
        checker.set_file("test.py")

        import ast
        tree = ast.parse(code)
        checker.visit(tree)

        # __init__ soll KEINE Return-Annotation-Warnung erzeugen
        return_findings = [f for f in checker.findings if f.type == "return"]
        assert len(return_findings) == 0

    def test_self_and_cls_ignored(self):
        """self und cls werden nicht bemängelt."""
        code = '''
class Foo:
    def method(self, x):
        pass
    
    @classmethod
    def factory(cls, x):
        pass
'''
        checker = AnnotationChecker(
            mode="relaxed",
            check_variables=False,
            check_params=True,
            check_returns=True,
        )
        checker.set_file("test.py")

        import ast
        tree = ast.parse(code)
        checker.visit(tree)

        # Nur 'x' in beiden Methoden sollte bemängelt werden, nicht self/cls
        param_findings = [f for f in checker.findings if f.type == "parameter"]
        assert all(f.name == "x" for f in param_findings)
        assert len(param_findings) == 2

    def test_variable_annotation_in_relaxed_mode(self):
        """Im relaxed mode ohne check_variables=True werden Variablen ignoriert."""
        code = '''
x = 42
y: int = 100
'''
        checker = AnnotationChecker(
            mode="relaxed",
            check_variables=False,
            check_params=True,
            check_returns=True,
        )
        checker.set_file("test.py")

        import ast
        tree = ast.parse(code)
        checker.visit(tree)

        # Keine Variable-Findings im relaxed mode ohne check_variables
        var_findings = [f for f in checker.findings if f.type == "variable"]
        assert len(var_findings) == 0

    def test_variable_annotation_with_check_variables(self):
        """Mit check_variables=True werden Variablen geprüft."""
        code = '''
x = 42
y: int = 100
'''
        checker = AnnotationChecker(
            mode="relaxed",
            check_variables=True,
            check_params=True,
            check_returns=True,
        )
        checker.set_file("test.py")

        import ast
        tree = ast.parse(code)
        checker.visit(tree)

        # Variable 'x' sollte bemängelt werden, 'y' nicht
        var_findings = [f for f in checker.findings if f.type == "variable"]
        assert len(var_findings) == 1
        assert var_findings[0].name == "x"

    def test_fully_annotated_code(self):
        """Vollständig annotierter Code erzeugt keine Findings."""
        code = '''
def calculate(x: float, y: float) -> float:
    result: float = x + y
    return result
'''
        checker = AnnotationChecker(
            mode="strict",
            check_variables=True,
            check_params=True,
            check_returns=True,
        )
        checker.set_file("test.py")

        import ast
        tree = ast.parse(code)
        checker.visit(tree)

        # Keine Findings bei vollständig annotiertem Code
        assert len(checker.findings) == 0

    def test_check_params_disabled(self):
        """Mit check_params=False werden Parameter nicht geprüft."""
        code = '''
def calculate(x, y) -> float:
    return x + y
'''
        checker = AnnotationChecker(
            mode="relaxed",
            check_variables=False,
            check_params=False,  # ← deaktiviert
            check_returns=True,
        )
        checker.set_file("test.py")

        import ast
        tree = ast.parse(code)
        checker.visit(tree)

        # Keine Parameter-Findings
        param_findings = [f for f in checker.findings if f.type == "parameter"]
        assert len(param_findings) == 0

    def test_check_returns_disabled(self):
        """Mit check_returns=False werden Returns nicht geprüft."""
        code = '''
def calculate(x: float, y: float):
    return x + y
'''
        checker = AnnotationChecker(
            mode="relaxed",
            check_variables=False,
            check_params=True,
            check_returns=False,  # ← deaktiviert
        )
        checker.set_file("test.py")

        import ast
        tree = ast.parse(code)
        checker.visit(tree)

        # Keine Return-Findings
        return_findings = [f for f in checker.findings if f.type == "return"]
        assert len(return_findings) == 0


# ============================================================================
# Tests: TypingCheckStep (Integration)
# ============================================================================

class TestTypingCheckStep:
    """Tests für den kompletten Setup-Step."""

    def test_step_registration(self):
        """Step ist korrekt registriert."""
        from tools.setup.steps import STEPS

        assert TypingCheckStep in STEPS
        assert TypingCheckStep.stid == "typing_check"
        assert TypingCheckStep.prio == 100

    def test_prepare_no_task_dir(self, mock_context: BaseStepContext):
        """Prepare gibt leeres Tuple zurück wenn src/task/ fehlt."""
        step = TypingCheckStep()
        result = step.prepare(mock_context)

        # prepare() gibt durch @handle_prepare nur das payload zurück
        assert result == tuple()

    def test_prepare_finds_python_files(
            self,
            mock_context: BaseStepContext,
            temp_task_dir: Path
    ):
        """Prepare findet Python-Dateien in src/task/."""
        # Erstelle Test-Dateien
        (temp_task_dir / "task1.py").write_text("# test")
        (temp_task_dir / "task2.py").write_text("# test")
        (temp_task_dir / "subdir").mkdir()
        (temp_task_dir / "subdir" / "task3.py").write_text("# test")

        step = TypingCheckStep()
        result = step.prepare(mock_context)

        # prepare() gibt durch @handle_prepare nur das payload zurück
        assert result is not None
        assert len(result) == 3

        # __init__.py soll ignoriert werden
        files = [f.name for f in result]
        assert "__init__.py" not in files

    def test_step_impl_no_files(self, mock_context: BaseStepContext):
        """Step-Impl mit keinen Dateien gibt Success zurück."""
        step = TypingCheckStep()
        result = step._step_impl(mock_context, tuple(), None)

        assert result.ok
        assert "nicht gefunden" in result.label or "übersprungen" in result.label

    def test_step_impl_finds_missing_annotations(
            self,
            mock_context: BaseStepContext,
            temp_task_dir: Path,
    ):
        """Step findet fehlende Annotationen und meldet sie."""
        # Erstelle Datei mit fehlenden Annotationen
        test_file = temp_task_dir / "bad_code.py"
        test_file.write_text('''
def calculate(x, y):
    return x + y
''')

        step = TypingCheckStep()
        prepared = step.prepare(mock_context)
        result = step._step_impl(mock_context, prepared, None)

        # Im relaxed mode sollte es eine Warnung geben (aber Success)
        assert result.ok  # relaxed mode
        assert "bad_code.py" in result.details
        assert "x" in result.details or "y" in result.details

    def test_step_impl_all_annotated(
            self,
            mock_context: BaseStepContext,
            temp_task_dir: Path,
    ):
        """Step gibt Success bei vollständig annotiertem Code."""
        # Erstelle Datei mit vollständigen Annotationen
        test_file = temp_task_dir / "good_code.py"
        test_file.write_text('''
def calculate(x: float, y: float) -> float:
    return x + y
''')

        step = TypingCheckStep()
        prepared = step.prepare(mock_context)
        result = step._step_impl(mock_context, prepared, None)

        assert result.ok
        assert "vollständig" in result.label.lower() or "keine" in result.details.lower()

    def test_syntax_error_handling(
            self,
            mock_context: BaseStepContext,
            temp_task_dir: Path,
    ):
        """Syntaxfehler werden abgefangen und ignoriert."""
        # Erstelle Datei mit Syntaxfehler
        test_file = temp_task_dir / "broken.py"
        test_file.write_text('''
def broken(
    # unvollständige Funktionsdefinition
''')

        step = TypingCheckStep()
        prepared = step.prepare(mock_context)

        # Sollte nicht crashen
        result = step._step_impl(mock_context, prepared, None)
        assert result.ok  # Syntaxfehler werden ignoriert


# ============================================================================
# Tests: Konfiguration
# ============================================================================

class TestConfiguration:
    """Tests für Konfigurationsoptionen."""

    def test_strict_mode_fails_on_missing_annotations(
            self,
            tmp_path: Path,
    ):
        """Im strict mode schlägt der Step bei fehlenden Annotationen fehl."""
        # Setup mit strict mode
        task_dir = tmp_path / "src" / "task"
        task_dir.mkdir(parents=True)
        (task_dir / "__init__.py").write_text("")

        test_file = task_dir / "code.py"
        test_file.write_text('def calc(x, y): return x + y')

        config = BootstrapConfig(repo_root=tmp_path)

        profile = PyProjectProfile(
            requires_min_python=(3, 11),
            runtime_requirements={},
            dev_requirements={},
            step_include=tuple(),
            step_exclude=tuple(),
            step_options={
                "typing_check": {
                    "mode": "strict",  # ← strict!
                    "check_params": True,
                    "check_returns": True,
                    "check_variables": False,
                }
            },
            verbosity=1,
            auto_install=True,
            linter_contracts="all",
            pyproject_data={
                "tool": {
                    "setup": {
                        "options": {
                            "typing_check": {
                                "mode": "strict",
                                "check_params": True,
                                "check_returns": True,
                                "check_variables": False,
                            }
                        }
                    }
                }
            },
        )

        # Mock-Console und Mock-Log
        mock_console = Mock()
        mock_log = Mock()

        context = BaseStepContext(
            config=config,
            profile=profile,
            console=mock_console,
            log=mock_log,
        )
        step = TypingCheckStep()
        prepared = step.prepare(context)
        result = step._step_impl(context, prepared, None)

        # Im strict mode sollte es fehlschlagen
        assert not result.ok
        assert result.cause == "missing_annotations"


# ============================================================================
# Test-Runner
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
