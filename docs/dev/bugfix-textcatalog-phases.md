# Bugfix: TextCatalog und Phase-Texte ✅

## Probleme gefunden und behoben

### 1. ❌ `slots=True` + `cached_property` Konflikt

**Fehler:**

```
TypeError: No '__dict__' attribute on 'TextCatalog' instance to cache '_data' property.
```

**Ursache:**

```python
@dataclass(frozen=True, slots=True)  # slots=True verhindert __dict__
class TextCatalog:
    @cached_property  # braucht __dict__ zum Cachen
    def _data(self):
        ...
```

**Lösung:**

```python
@dataclass(frozen=True)  # slots=True entfernt
class TextCatalog:
    @cached_property  # funktioniert jetzt
    def _data(self):
        ...
```

### 2. ❌ IndexError bei Phase-Texten

**Fehler:**

```
IndexError: list index out of range
bei phase_text.split(",")[1]
```

**Ursache:**

1. TOML-Schlüssel `[progress_phases.install_project]` wurde als verschachtelte Sektion interpretiert
2. `_TEXTS.block("progress_phases.install_project")` fand den Block nicht
3. Fallback war leerer String → Split ergab `['']` → Index 1 existiert nicht

**Lösung 1 - TOML-Struktur vereinfachen:**

```toml
# ALT (verschachtelt, funktioniert nicht mit Punkt-Notation)
[progress_phases.install_project]
body = "Phase1,Phase2,..."

# NEU (flach)
[install_project_phases]
body = "Phase1,Phase2,..."
```

**Lösung 2 - Robuster Code mit Fallback:**

```python
# ALT
phase_text = _TEXTS.text("progress_phases.install_project")
phases = [
    (20, phase_text.split(",")[0]),  # ❌ Crash wenn leer
    (40, phase_text.split(",")[1]),  # ❌ IndexError
]

# NEU
try:
    phase_block = _TEXTS.block("install_project_phases")
    phase_text = phase_block.get("body", "")
except Exception:
    phase_text = "Phase1,Phase2,..."  # Hardcoded Fallback

phase_list = [p.strip() for p in phase_text.split(",") if p.strip()]
phases = [
    (20, phase_list[0] if len(phase_list) > 0 else "Phase 1"),  # ✅ Safe
    (40, phase_list[1] if len(phase_list) > 1 else "Phase 2"),  # ✅ Safe
]
```

## Geänderte Dateien

### ✅ tools/ui/resources/catalog.py

- `slots=True` entfernt aus `@dataclass` Decorator
- `cached_property` funktioniert jetzt

### ✅ tools/ui/resources/text_blocks.toml

- `[progress_phases.install_project]` → `[install_project_phases]`
- `[progress_phases.run_tests]` → `[run_tests_phases]`
- Flache Struktur ohne Punkt-Notation

### ✅ tools/setup/bootstrap.py

- `install_project_editable()`: Robustes Phase-Loading mit Try/Except
- `run_tests()`: Robustes Phase-Loading mit Try/Except
- Fallbacks für alle Phase-Listen
- Index-Zugriffe mit Length-Checks

## Root Cause Analysis

### Problem 1: `slots=True` Design-Konflikt

**Warum passiert?**

- `slots=True` optimiert Speicher durch Entfernen von `__dict__`
- `@cached_property` speichert Werte in `instance.__dict__`
- **Konflikt**: Kein `__dict__` → Kein Caching möglich

**Warum nicht früher erkannt?**

- Code kompiliert ohne Fehler
- Fehler tritt erst zur **Laufzeit** beim ersten `_data`-Zugriff auf

### Problem 2: TOML Punkt-Notation Missverständnis

**Warum passiert?**

- TOML unterstützt **zwei** Arten geschachtelter Strukturen:
  ```toml
  # Variante 1: Punkt-Notation (echte Verschachtelung)
  [progress_phases.install_project]
  body = "..."
  # Zugriff: data["progress_phases"]["install_project"]["body"]
  
  # Variante 2: Flacher Schlüssel
  [install_project_phases]
  body = "..."
  # Zugriff: data["install_project_phases"]["body"]
  ```

- Code verwendete: `_TEXTS.block("progress_phases.install_project")`
- Aber TOML erzeugte: `{"progress_phases": {"install_project": {...}}}`
- Lösung: Flache Schlüssel ohne Punkt verwenden

**Warum funktioniert Fallback nicht?**

- `_TEXTS.text()` mit `fallback=""` gab leeren String zurück
- `"".split(",")` → `[""]` (Liste mit 1 Element: leerer String)
- `phases[1]` → IndexError

## Lessons Learned

1. ✅ **`slots=True` + `@cached_property` = ❌**
    - Bei Bedarf: Manuelles Caching oder `__slots__` mit `__dict__` Slot

2. ✅ **TOML-Schlüssel ohne Punkte für einfachen Zugriff**
    - `[simple_key]` statt `[nested.key]`

3. ✅ **Immer robuste Index-Zugriffe**
    - `list[i] if len(list) > i else default`

4. ✅ **Fallbacks testen**
    - Leerer String ist valide, aber `split()` erzeugt trotzdem Liste!

## Testing

```bash
# Test TextCatalog
python -c "from tools.ui.resources import TextCatalog; t = TextCatalog(); print(t.block('setup_header'))"

# Test Phase-Loading
python -c "from tools.ui.resources import TextCatalog; t = TextCatalog(); b = t.block('install_project_phases'); print(b['body'].split(','))"

# Vollständiger Setup-Test
python setup.py
```

## Status

✅ `slots=True` entfernt  
✅ TOML-Struktur vereinfacht  
✅ Robuste Phase-Loading Logik  
✅ Syntax-Check erfolgreich  
✅ Bereit für Setup-Ausführung

