# Testing & Debugging Tools - Verwendungsanleitung

Diese Dokumentation beschreibt die installierten Tools für Testing und Debugging von Threading/Lock-Problemen.

## Installierte Tools

### 1. pytest-timeout
**Zweck**: Automatische Erkennung von Deadlocks und hängenden Tests

**Installation**: Automatisch über `requirements.txt` installiert

**Konfiguration**: In `pyproject.toml` unter `[tool.pytest.ini_options]`

**Verwendung**:
```bash
# Standard-Tests mit 300s Timeout (konfiguriert in pyproject.toml)
pytest tests/

# Einzelner Test mit custom Timeout
pytest tests/test_utils_instance_lock.py --timeout=60

# Test mit spezifischem Timeout dekorieren
@pytest.mark.timeout(10)
def test_quick_operation():
    pass
```

**Vorteile**:
- Verhindert unendlich laufende Tests im CI/CD
- Zeigt Stack-Trace wo Test hängt
- Erkennt Deadlocks automatisch

---

### 2. threadpoolctl
**Zweck**: Kontrolle über Thread-Pool-Größe und Monitoring

**Installation**: Automatisch über `requirements.txt` installiert

**Verwendung**:
```python
from threadpoolctl import threadpool_limits, threadpool_info

# Thread-Anzahl begrenzen (reduziert Lock-Contention)
with threadpool_limits(limits=4, user_api='blas'):
    # Code der viele Threads spawnt
    result = heavy_computation()

# Aktuelle Thread-Pool-Info abrufen
info = threadpool_info()
for pool in info:
    print(f"Library: {pool['user_api']}, Threads: {pool['num_threads']}")
```

**Beispiel für Tests**:
```python
import threadpoolctl

def test_with_limited_threads():
    """Test mit begrenzter Thread-Anzahl."""
    with threadpoolctl.threadpool_limits(limits=2):
        # Test-Code hier
        sim = UfoSim()
        # Simulation läuft mit max 2 Threads
```

**Vorteile**:
- Reduziert Lock-Contention in Tests
- Macht Tests deterministischer
- Hilfreich bei "Warum spawnen wir 500 Threads?"

---

### 3. py-spy
**Zweck**: Live-Profiling von Python-Prozessen (KEINE Code-Änderung nötig!)

**Installation**: Automatisch über `requirements.txt` installiert

**Verwendung**:

#### Option A: Top-Ansicht (wie htop für Python)
```bash
# Simulation starten
python src/core/simulation/ufo_main.py &
PID=$!

# py-spy attachen
py-spy top --pid $PID
```

#### Option B: Flamegraph erstellen
```bash
# Während Simulation läuft
py-spy record --pid $PID --output profile.svg

# SVG-Datei kann in Browser geöffnet werden
firefox profile.svg
```

#### Option C: Direktes Starten mit Profiling
```bash
py-spy record -- python src/core/simulation/ufo_main.py
```

#### Option D: Deadlock-Erkennung
```bash
# Zeigt wo Threads warten/blockieren
py-spy dump --pid $PID

# Ausgabe zeigt z.B.:
# Thread 3 (idle): "Waiting on lock at ufosim.py:245"
```

**Vorteile**:
- **Keine Code-Änderung nötig**
- Zeigt live welcher Thread wo wartet
- Erkennt: "Thread 3 wartet seit 5s auf Lock in Zeile 245"
- Production-ready (kann an laufende Prozesse attachen)

---

## Praktische Workflows

### Workflow 1: Deadlock-Debugging
```bash
# 1. Simulation starten
python src/core/simulation/ufo_main.py &
PID=$!

# 2. Bei Verdacht auf Deadlock
py-spy dump --pid $PID

# 3. Ausgabe analysieren - zeigt wartende Threads
```

### Workflow 2: Test-Deadlock erkennen
```bash
# pytest-timeout erkennt hängende Tests automatisch
pytest tests/ -v

# Wenn Test hängt (>300s):
# - pytest killt Test
# - Zeigt Stack-Trace wo es hängt
# - CI/CD schlägt fehl (gut!)
```

### Workflow 3: Lock-Contention reduzieren
```python
# In Tests: Thread-Anzahl begrenzen
import threadpoolctl

def test_simulation_multithread():
    with threadpoolctl.threadpool_limits(limits=4):
        # Simulation mit max 4 Threads
        sim = UfoSim()
        sim.run_for_seconds(10)
```

### Workflow 4: Production-Monitoring
```bash
# Auf Production-Server
ps aux | grep python  # PID finden

# Profiling starten (nicht-invasiv!)
py-spy record --pid $PID --duration 60 --output /tmp/profile.svg

# Flamegraph analysieren
# - Welche Funktionen brauchen Zeit?
# - Wo warten Threads?
```

---

## Integration in CI/CD

Die Tools sind bereits für CI/CD vorbereitet:

**GitHub Actions Beispiel**:
```yaml
- name: Run Tests with Timeout
  run: |
    pytest tests/ --timeout=300 --timeout-method=thread
    
- name: Check for Thread Issues
  if: failure()
  run: |
    # Bei Failure: Thread-Info sammeln
    python -c "import threadpoolctl; print(threadpoolctl.threadpool_info())"
```

---

## Troubleshooting

### pytest-timeout funktioniert nicht
```bash
# Überprüfen ob installiert
pytest --co -q --timeout=1

# Sollte zeigen: "timeout: 1.0s"
```

### py-spy Permission Error
```bash
# Auf Linux: ptrace-Berechtigung nötig
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope

# Oder mit sudo
sudo py-spy top --pid $PID
```

### threadpoolctl zeigt nichts
```python
# threadpoolctl funktioniert nur mit BLAS/OpenMP Libraries
# Für eigene Thread-Pools: Manuelle Kontrolle nötig
```

---

## Best Practices

1. **pytest-timeout**: 
   - Default 300s ist OK für die meisten Tests
   - Für schnelle Unit-Tests: `@pytest.mark.timeout(5)`
   - Für Integration-Tests: `@pytest.mark.timeout(600)`

2. **threadpoolctl**:
   - In Tests verwenden um Determinismus zu erhöhen
   - In Production nur wenn Lock-Contention Problem ist

3. **py-spy**:
   - Für Debugging: `py-spy top --pid $PID`
   - Für Analyse: `py-spy record --duration 60`
   - **Niemals** in kritischen Production-Pfaden (Overhead!)

---

## Siehe auch

- [pytest-timeout Docs](https://github.com/pytest-dev/pytest-timeout)
- [threadpoolctl Docs](https://github.com/joblib/threadpoolctl)
- [py-spy Docs](https://github.com/benfred/py-spy)
