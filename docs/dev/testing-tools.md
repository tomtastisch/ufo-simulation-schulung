# Testing & Debugging Tools – Verwendungsanleitung

Diese Dokumentation beschreibt die installierten Tools für Testing und Debugging von Threading/Lock-Problemen.

---

## Übersicht

| Tool               | Zweck                 | Installation                     |
|--------------------|-----------------------|----------------------------------|
| **pytest-timeout** | Deadlock-Erkennung    | Automatisch via requirements.txt |
| **threadpoolctl**  | Thread-Pool-Kontrolle | Automatisch via requirements.txt |
| **py-spy**         | Live-Profiling        | Automatisch via requirements.txt |

---

## 1. pytest-timeout

### Zweck

Automatische Erkennung von Deadlocks und hängenden Tests durch Timeout-Überwachung.

### Installation

Automatisch installiert über `requirements.txt`.

### Konfiguration

In `pyproject.toml` unter `[tool.pytest.ini_options]`:

```toml
[tool.pytest.ini_options]
timeout = 300  # Standard-Timeout: 5 Minuten
```

### Verwendung

#### Standard-Tests mit konfiguriertem Timeout

```bash
pytest tests/
```

#### Einzelner Test mit custom Timeout

```bash
pytest tests/test_synchronization_instance_lock.py --timeout=60
```

#### Test mit spezifischem Timeout dekorieren

```python
import pytest

@pytest.mark.timeout(10)
def test_quick_operation():
    """Test sollte innerhalb von 10 Sekunden abgeschlossen sein."""
    result = quick_operation()
    assert result is not None
```

### Vorteile

- ✅ Verhindert unendlich laufende Tests im CI/CD
- ✅ Zeigt Stack-Trace wo Test hängt (hilfreich bei Deadlocks)
- ✅ Erkennt Deadlocks automatisch

### Beispiel-Output bei Timeout

```
_____________________ ERROR at teardown of test_deadlock _____________________
TIMEOUT: Test exceeded timeout of 10.0 seconds
Stack trace:
  File "test_sync.py", line 45, in test_deadlock
    lock.acquire()
```

---

## 2. threadpoolctl

### Zweck

Kontrolle über Thread-Pool-Größe und Monitoring zur Reduzierung von Lock-Contention.

### Installation

Automatisch installiert über `requirements.txt`.

### Verwendung

#### Thread-Anzahl begrenzen

```python
from threadpoolctl import threadpool_limits

# Thread-Anzahl für numerische Bibliotheken begrenzen
with threadpool_limits(limits=4, user_api='blas'):
    # Code der viele Threads spawnt
    result = heavy_computation()
```

#### Aktuelle Thread-Pool-Info abrufen

```python
from threadpoolctl import threadpool_info

info = threadpool_info()
for pool in info:
    print(f"Library: {pool['user_api']}")
    print(f"Threads: {pool['num_threads']}")
    print(f"Filepath: {pool['filepath']}")
```

#### In Tests verwenden

```python
import threadpoolctl

def test_with_limited_threads():
    """Test mit begrenzter Thread-Anzahl für deterministische Ergebnisse."""
    with threadpoolctl.threadpool_limits(limits=2):
        sim = UfoSim()
        # Simulation läuft mit max 2 Threads
        sim.run()
```

### Vorteile

- ✅ Reduziert Lock-Contention in Tests
- ✅ Macht Tests deterministischer
- ✅ Hilfreich bei "Warum spawnen wir 500 Threads?"
- ✅ Debugging von Thread-Pool-Problemen

### Unterstützte Bibliotheken

- BLAS (numpy, scipy)
- OpenMP
- MKL
- OpenBLAS

---

## 3. py-spy

### Zweck

Live-Profiling von Python-Prozessen **ohne Code-Änderungen** – ideal für Deadlock-Analyse.

### Installation

Automatisch installiert über `requirements.txt`.

### Verwendung

#### Option A: Top-Ansicht (wie htop für Python)

```bash
# Simulation starten
python src/core/simulation/ufo_main.py &
PID=$!

# py-spy attachen
py-spy top --pid $PID
```

**Ausgabe**:

```
Total Samples: 1000
GIL: 5.00%, Active: 95.00%, Threads: 4

  %Own   %Total  OwnTime  TotalTime  Function (filename:line)
  45.00%  45.00%   0.45s     0.45s   compute_physics (physics/engine.py:123)
  25.00%  70.00%   0.25s     0.70s   update_state (state/manager.py:45)
  15.00%  15.00%   0.15s     0.15s   render_frame (view/viewport.py:67)
```

#### Option B: Flamegraph erstellen

```bash
# Während Simulation läuft
py-spy record --pid $PID --output profile.svg

# SVG-Datei im Browser öffnen
firefox profile.svg
# oder
open profile.svg  # macOS
```

#### Option C: Direktes Starten mit Profiling

```bash
# Programm mit py-spy starten
py-spy record --output profile.svg -- python src/core/simulation/ufo_main.py
```

#### Option D: Threads überwachen (Deadlock-Erkennung!)

```bash
# Zeigt alle Thread-Stacks
py-spy dump --pid $PID

# Mehrfach aufrufen um zu sehen wo Threads hängen
for i in {1..5}; do 
    echo "=== Sample $i ===" 
    py-spy dump --pid $PID
    sleep 1
done
```

**Ausgabe bei Deadlock**:

```
Thread 1 (active): "MainThread"
    acquire (threading.py:123)
    _synchronized_method (utils/threads.py:45)
    update_state (state/manager.py:67)

Thread 2 (active): "PhysicsThread"
    acquire (threading.py:123)  # <-- Hängt beim Warten
    _synchronized_method (utils/threads.py:45)
    compute_physics (physics/engine.py:89)
```

### Vorteile

- ✅ **Keine Code-Änderungen nötig** – attach an laufenden Prozess
- ✅ **Deadlock-Erkennung** – zeigt wo Threads hängen
- ✅ **Performance-Analyse** – Flamegraphs für Hotspots
- ✅ **GIL-Monitoring** – sieht GIL-Contention
- ✅ **Native-Code** – funktioniert auch mit C-Extensions

---

## Workflow: Threading-Problem debuggen

### 1. Problem reproduzieren

```bash
# Simulation starten
python src/core/simulation/ufo_main.py &
PID=$!
```

### 2. Live-Monitoring

```bash
# Top-Ansicht für Überblick
py-spy top --pid $PID
```

### 3. Deadlock-Verdacht?

```bash
# Thread-Dumps mehrfach aufrufen
for i in {1..5}; do 
    echo "=== Sample $i ===" 
    py-spy dump --pid $PID
    sleep 1
done
```

**Was suchen?**

- Threads die immer an gleicher Stelle hängen
- `acquire()` oder `wait()` Aufrufe
- Zwei Threads die auf Locks des jeweils anderen warten

### 4. Performance-Analyse

```bash
# Flamegraph erstellen (30 Sekunden laufen lassen)
py-spy record --duration 30 --output profile.svg --pid $PID

# Flamegraph analysieren
open profile.svg
```

**Was suchen?**

- Breite Balken = viel Zeit verbracht
- Hohe Stacks = viele Funktionsaufrufe
- Rote Bereiche (falls aktiviert) = CPU-intensive Bereiche

### 5. Thread-Anzahl reduzieren (falls zu viele Threads)

```python
# In conftest.py oder Test-Setup
import threadpoolctl

@pytest.fixture(autouse=True)
def limit_threads():
    """Begrenzt Thread-Anzahl für alle Tests."""
    with threadpoolctl.threadpool_limits(limits=2):
        yield
```

---

## Best Practices

### pytest-timeout

- ✅ Setze sinnvolle Timeouts für Tests (nicht zu kurz!)
- ✅ Nutze `@pytest.mark.timeout(...)` für langsame Tests
- ✅ Bei CI/CD: Längere Timeouts als lokal (langsame Runner)

### threadpoolctl

- ✅ Nutze in Tests um deterministische Thread-Anzahl zu garantieren
- ✅ Nutze `threadpool_info()` um zu verstehen welche Bibliothek Threads spawnt
- ✅ Dokumentiere wenn Code Thread-Anzahl-sensitiv ist

### py-spy

- ✅ Nutze `py-spy top` für ersten Überblick
- ✅ Nutze `py-spy dump` bei Deadlock-Verdacht (mehrfach aufrufen!)
- ✅ Nutze `py-spy record` für Performance-Analyse
- ✅ Flamegraphs in Browser öffnen (interaktiv!)
- ⚠️ Bei Production: Minimal-Overhead, aber teste vorher!

---

## Troubleshooting

### pytest-timeout: "ImportError: No module named pytest_timeout"

```bash
# Prüfe Installation
pip list | grep pytest-timeout

# Neu installieren falls fehlt
pip install pytest-timeout
```

### py-spy: "Permission denied"

```bash
# macOS/Linux: Eventuell mit sudo
sudo py-spy top --pid $PID

# Oder: User Permissions anpassen (macOS)
sudo dtruss py-spy top --pid $PID
```

### py-spy: "No such process"

```bash
# Prüfe ob Prozess läuft
ps aux | grep python

# PID korrekt?
echo $PID
```

---

## Siehe auch

- **pytest Dokumentation**: https://docs.pytest.org/
- **pytest-timeout Dokumentation**: https://github.com/pytest-dev/pytest-timeout
- **threadpoolctl Dokumentation**: https://github.com/joblib/threadpoolctl
- **py-spy Dokumentation**: https://github.com/benfred/py-spy
- **Flamegraph Anleitung**: http://www.brendangregg.com/flamegraphs.html

---

**Hinweis**: Diese Tools sind für Entwickler-Debugging gedacht, nicht für Schüler.

