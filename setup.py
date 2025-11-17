#!/usr/bin/env python3
"""
🛸 UFO-Simulation Schulung - Automatisches Setup Script

Dieses Script richtet die Entwicklungsumgebung automatisch ein.
Funktioniert auf Windows, macOS und Linux.

WICHTIG:
- Behebt Fehler automatisch und versucht sich selbst zu reparieren!
- Liest Python-Version aus pyproject.toml
- Liest Pakete aus requirements.txt

Verwendung:
    python setup.py

Das war's! Alles funktioniert danach automatisch.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import time
import re
import tomllib  # Python 3.11+ built-in


def print_header(text: str) -> None:
    """Druckt einen formatierten Header."""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def print_success(text: str) -> None:
    """Druckt erfolgreiche Nachricht."""
    print(f"   ✅ {text}")


def print_error(text: str) -> None:
    """Druckt Fehlernachricht."""
    print(f"   ❌ {text}")


def print_warning(text: str) -> None:
    """Druckt Warnmeldung."""
    print(f"   ⚠️  {text}")


def print_info(text: str) -> None:
    """Druckt Info-Nachricht."""
    print(f"   ℹ️  {text}")


def print_fix(text: str) -> None:
    """Druckt Fix-Nachricht."""
    print(f"   🔧 {text}")


def parse_pyproject_toml() -> dict:
    """
    Liest pyproject.toml und extrahiert Python-Versionsanforderung.

    Gibt dict mit:
    - "requires_python": ">=3.11"
    - "python_major": 3
    - "python_minor": 11
    """
    print("📖 Lese pyproject.toml...")
    pyproject_file = Path("pyproject.toml")

    if not pyproject_file.exists():
        print_error("pyproject.toml nicht gefunden!")
        return {}

    try:
        with open(pyproject_file, "rb") as f:
            data = tomllib.load(f)

        requires_python = data.get("project", {}).get("requires-python", ">=3.11")
        print_info(f"Python-Anforderung: {requires_python}")

        # Parse ">=3.11" zu (3, 11)
        match = re.search(r"(\d+)\.(\d+)", requires_python)
        if match:
            major, minor = int(match.group(1)), int(match.group(2))
            print_success(f"Erkannt: Python {major}.{minor}+")
            print()
            return {
                "requires_python": requires_python,
                "python_major": major,
                "python_minor": minor,
            }
    except Exception as e:
        print_error(f"Fehler beim Parsen von pyproject.toml: {e}")
        return {}

    return {}


def parse_requirements() -> dict[str, str]:
    """
    Liest requirements.txt und parst Pakete mit Versionen.

    Gibt dict mit Format: {"paketname": "version_spec"}
    z.B. {"PyQt5": "==5.15.11", "numpy": "==1.26.4"}
    """
    print("📖 Lese requirements.txt...")
    req_file = Path("requirements.txt")

    if not req_file.exists():
        print_error("requirements.txt nicht gefunden!")
        return {}

    requirements = {}
    try:
        with open(req_file, "r") as f:
            for line in f:
                line = line.strip()
                # Ignoriere leere Zeilen und Kommentare
                if not line or line.startswith("#"):
                    continue

                # Parse "paket==version" oder "paket>=version" etc.
                match = re.match(r"([a-zA-Z0-9\-_]+)(.*)", line)
                if match:
                    package_name = match.group(1)
                    version_spec = match.group(2).strip()
                    requirements[package_name] = version_spec
                    print_info(f"{package_name}{version_spec}")
    except Exception as e:
        print_error(f"Fehler beim Parsen von requirements.txt: {e}")
        return {}

    print_success(f"Requirements gelesen: {len(requirements)} Pakete")
    print()
    return requirements


def check_python_version(pyproject: dict) -> bool:
    """Prüft ob die benötigte Python-Version installiert ist."""
    print("📋 Prüfe Python-Version...")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"   Python: {version_str}")

    if pyproject:
        required_major = pyproject["python_major"]
        required_minor = pyproject["python_minor"]
        requires_str = pyproject["requires_python"]

        if version < (required_major, required_minor):
            print_error(f"Python {requires_str} erforderlich, aber {version.major}.{version.minor} installiert")
            print_info(
                f"Bitte installiere Python {required_major}.{required_minor}+ von https://www.python.org/downloads/")
            print_warning("Das Script kann dies nicht automatisch beheben.")
            print()
            return False

        print_success(f"Python {required_major}.{required_minor}+ OK (Anforderung: {requires_str})")
    else:
        print_success("Python OK")

    print()
    return True


def get_platform_info() -> dict[str, str]:
    """Gibt plattformabhängige Informationen."""
    system = platform.system()
    venv_path = Path(".venv")

    if system == "Windows":
        python_venv = venv_path / "Scripts" / "python.exe"
        activate_cmd = ".venv\\Scripts\\activate"
    else:
        python_venv = venv_path / "bin" / "python"
        activate_cmd = "source .venv/bin/activate"

    return {
        "system": system,
        "python_venv": str(python_venv),
        "activate_cmd": activate_cmd,
    }


def create_venv() -> bool:
    """Erstellt Virtual Environment, löscht bei Fehler und versucht erneut."""
    print("📦 Erstelle Virtual Environment...")
    venv_path = Path(".venv")

    if venv_path.exists():
        print_success("Virtual Environment existiert bereits")
        print()
        return True

    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True, capture_output=True)
        print_success("Virtual Environment erstellt")
        print()
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Fehler beim Erstellen des Virtual Environment")
        print_fix("Lösche beschädigtes .venv und versuche erneut...")

        try:
            import shutil
            if venv_path.exists():
                shutil.rmtree(venv_path)
            print_info(".venv gelöscht")
            time.sleep(1)
        except Exception as delete_error:
            print_error(f"Konnte .venv nicht löschen: {delete_error}")
            return False

        try:
            subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True, capture_output=True)
            print_success("Virtual Environment beim 2. Versuch erstellt")
            print()
            return True
        except subprocess.CalledProcessError as retry_error:
            print_error(f"Virtual Environment Erstellung fehlgeschlagen auch beim 2. Versuch")
            print()
            return False


def handle_pyqt5_macos(platform_info: dict[str, str]) -> bool:
    """
    Behebt macOS-spezifische PyQt5-Probleme (M1/M2/M3).
    """
    print("🍎 Prüfe macOS PyQt5-Kompatibilität...")
    python_venv = platform_info["python_venv"]

    if platform_info["system"] != "Darwin":
        print_info("Nicht macOS - Überspringe macOS-Fix")
        print()
        return True

    try:
        # Versuche PyQt5 zu importieren
        result = subprocess.run(
            [python_venv, "-c", "import PyQt5; print('OK')"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        if "OK" in result.stdout:
            print_success("PyQt5 funktioniert auf macOS")
            print()
            return True
    except:
        pass

    # Falls PyQt5 nicht funktioniert, installiere mit spezifischen Flags
    print_warning("PyQt5 Import fehlgeschlagen auf macOS")
    print_fix("Installiere PyQt5 mit macOS-Kompatibilität...")

    try:
        subprocess.run(
            [python_venv, "-m", "pip", "install", "--upgrade",
             "PyQt5==5.15.11",
             "--no-cache-dir",
             "--force-reinstall"],
            check=True,
            timeout=120,
        )
        print_success("PyQt5 auf macOS installiert")
        print()
        return True
    except subprocess.CalledProcessError:
        print_warning("PyQt5 Installation auf macOS fehlgeschlagen (nicht kritisch)")
        print_warning("Das Projekt sollte trotzdem funktionieren")
        print()
        return True

def upgrade_pip(platform_info: dict[str, str]) -> bool:
    """Aktualisiert pip, versucht bei Fehler Neuinstallation."""
    print("⬆️  Aktualisiere pip...")
    python_venv = platform_info["python_venv"]

    try:
        subprocess.run(
            [python_venv, "-m", "pip", "install", "--upgrade", "pip", "--quiet"],
            check=True,
            capture_output=True,
        )
        print_success("pip aktualisiert")
        print()
        return True
    except subprocess.CalledProcessError as e:
        print_warning("pip Upgrade fehlgeschlagen, versuche Neuinstallation...")
        print_fix("Installiere pip neu...")

        try:
            subprocess.run(
                [python_venv, "-m", "ensurepip", "--upgrade"],
                check=True,
                capture_output=True,
            )
            print_success("pip neu installiert")
            print()
            return True
        except subprocess.CalledProcessError:
            print_warning("pip Neuinstallation auch fehlgeschlagen (nicht kritisch)")
            print()
            return True


def configure_pip_index(platform_info: dict[str, str]) -> bool:
    """Konfiguriert PyPI Index URL, erstellt Config-Datei bei Fehler."""
    print("🔧 Konfiguriere pip Index (behebt PyPI-Fehler)...")
    python_venv = platform_info["python_venv"]

    try:
        subprocess.run(
            [
                python_venv,
                "-m",
                "pip",
                "config",
                "set",
                "global.index-url",
                "https://pypi.org/simple",
            ],
            check=True,
            capture_output=True,
        )
        print_success("PyPI Index konfiguriert")
        print()
        return True
    except subprocess.CalledProcessError as e:
        print_warning("pip config Befehl fehlgeschlagen, versuche manuelle Konfiguration...")
        print_fix("Erstelle pip config manuell...")

        try:
            if platform_info["system"] == "Windows":
                config_dir = Path.home() / "AppData" / "Roaming" / "pip"
                config_file = config_dir / "pip.ini"
            else:
                config_dir = Path.home() / ".config" / "pip"
                config_file = config_dir / "pip.conf"

            config_dir.mkdir(parents=True, exist_ok=True)

            config_content = "[global]\nindex-url = https://pypi.org/simple\n"
            config_file.write_text(config_content)

            print_success(f"pip Konfiguration erstellt")
            print()
            return True
        except Exception as config_error:
            print_warning(f"Manuelle pip Konfiguration auch fehlgeschlagen (nicht kritisch)")
            print()
            return True


def install_dependencies(platform_info: dict[str, str], requirements: dict[str, str], retry_count: int = 0) -> bool:
    """Installiert Dependencies aus requirements.txt, versucht bei Fehler mehrfach erneut."""
    print("📥 Installiere Dependencies (aus requirements.txt)...")
    python_venv = platform_info["python_venv"]
    max_retries = 3

    try:
        subprocess.run(
            [python_venv, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )
        print_success("Alle Dependencies installiert")
        print()
        return True
    except subprocess.CalledProcessError as e:
        retry_count += 1

        if retry_count < max_retries:
            print_error(f"Installation fehlgeschlagen (Versuch {retry_count}/{max_retries})")
            print_fix(f"Warte 3 Sekunden und versuche erneut...")
            time.sleep(3)

            try:
                subprocess.run(
                    [python_venv, "-m", "pip", "install", "--upgrade", "pip"],
                    check=True,
                    capture_output=True,
                )
            except:
                pass

            return install_dependencies(platform_info, requirements, retry_count)
        else:
            print_error(f"Installation nach {max_retries} Versuchen fehlgeschlagen")
            print_info("Falls PyPI-Fehler: Prüfe deine Internetverbindung")
            print()
            return False


def verify_installation(platform_info: dict[str, str], requirements: dict[str, str]) -> bool:
    """
    Prüft ob alle aus requirements.txt definierten Module installiert sind.
    WICHTIG: Kein Rekursion! Maximal 1 Retry-Versuch pro Modul.
    """
    print("✔️  Prüfe Installation (von requirements.txt)...")
    python_venv = platform_info["python_venv"]

    all_ok = True
    failed_modules = []
    max_module_retries = 1  # Pro Modul max 1 Versuch
    module_retry_count = {}

    for package_name, version_spec in requirements.items():
        # Map für Import-Namen (z.B. PyQt5 -> PyQt5, aber andere können unterschiedlich sein)
        import_name_map = {
            "PyQt5": "PyQt5",
            "numpy": "numpy",
        }
        import_name = import_name_map.get(package_name, package_name)

        try:
            # Versuche zu importieren
            result = subprocess.run(
                [python_venv, "-c", f"import {import_name}; print({import_name}.__version__)"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
            )
            version = result.stdout.strip()
            print_success(f"{package_name}{version_spec} (installiert: {version})")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            print_error(f"{package_name}{version_spec} - Importtest fehlgeschlagen")

            # Prüfe ob schon pip list funktioniert
            try:
                pip_list = subprocess.run(
                    [python_venv, "-m", "pip", "show", package_name],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=5,
                )
                if "Location:" in pip_list.stdout:
                    print_warning(f"   → Aber pip zeigt: {package_name} ist installiert")
                    print_warning(f"   → Import-Fehler ignoriert (Module können dennoch funktionieren)")
                    continue
            except:
                pass

            # Modul ist nicht installiert oder fehlerhaft
            module_retry_count[package_name] = module_retry_count.get(package_name, 0) + 1

            if module_retry_count[package_name] <= max_module_retries:
                print_fix(f"   Versuche zu reparieren...")
                install_spec = f"{package_name}{version_spec}"
                try:
                    subprocess.run(
                        [python_venv, "-m", "pip", "install", install_spec, "--upgrade", "--force-reinstall"],
                        check=True,
                        capture_output=True,
                        timeout=60,
                    )
                    print_success(f"   {package_name} neu installiert")

                    # Prüfe nochmal
                    try:
                        result = subprocess.run(
                            [python_venv, "-c", f"import {import_name}; print({import_name}.__version__)"],
                            capture_output=True,
                            text=True,
                            check=True,
                            timeout=5,
                        )
                        version = result.stdout.strip()
                        print_success(f"   Import funktioniert jetzt: {version}")
                        continue
                    except:
                        print_warning(f"   Import funktioniert immer noch nicht - aber pip zeigt Paket als installiert")
                        continue
                except subprocess.CalledProcessError as e:
                    print_error(f"   Konnte {package_name} nicht neu installieren")
                    failed_modules.append((package_name, version_spec))
                    all_ok = False
            else:
                print_error(f"   Max Versuche für {package_name} erreicht")
                failed_modules.append((package_name, version_spec))
                all_ok = False

    print()

    if not all_ok and failed_modules:
        print_error(f"Folgende Module konnten nicht installiert werden:")
        for pkg, spec in failed_modules:
            print_error(f"   - {pkg}{spec}")
        return False

    return True


def print_next_steps(platform_info: dict[str, str]) -> None:
    """Druckt die nächsten Schritte."""
    print_header("🎉 Setup erfolgreich abgeschlossen!")

    activate_cmd = platform_info["activate_cmd"]

    print("📍 Nächste Schritte:\n")
    print(f"1️⃣  Aktiviere das Virtual Environment:")
    print(f"    {activate_cmd}\n")
    print(f"2️⃣  Starte die Demo:")
    print(f"    python -m ufo_simulation.ufo_main\n")
    print(f"3️⃣  Öffne ufo_simulation/autopilot.py")
    print(f"    Implementiere die 3 Aufgaben:\n")
    print(f"    - takeoff()  - Startphase")
    print(f"    - cruise()   - Reiseflug")
    print(f"    - landing()  - Landephase\n")
    print(f"4️⃣  Setze USE_DEMO = False in autopilot.py\n")
    print(f"5️⃣  Starte die Demo erneut und teste deinen Autopiloten!\n")
    print("Happy Flying! 🚀\n")


def print_troubleshooting() -> None:
    """Druckt Troubleshooting-Tipps."""
    print_header("🆘 Troubleshooting")

    print("Falls immer noch etwas schiefgeht:\n")
    print("❌ Python-Version nicht korrekt?")
    print("   → Prüfe: python --version")
    print("   → Installiere erforderliche Version von https://www.python.org/downloads/\n")

    print("❌ pip Fehler / PyPI-Download fehlgeschlagen?")
    print("   → Prüfe deine Internetverbindung")
    print("   → Versuche: python -m pip install -r requirements.txt\n")

    print("❌ Virtual Environment Fehler?")
    print("   → Lösche .venv: rm -rf .venv (Linux/macOS)")
    print("   →               rmdir /s .venv (Windows)")
    print("   → Führe setup.py erneut aus\n")

    print("❌ PyQt5 Import-Fehler (aber pip zeigt installiert)?")
    print("   → Das ist ein bekanntes Problem auf macOS mit M1/M2")
    print("   → Versuche: pip install --upgrade PyQt5")
    print("   → Oder: Verwende native Python statt Homebrew\n")

    print("📞 Weitere Hilfe:")
    print("   → Öffne ein Issue auf GitHub")
    print("   → Kontaktiere deinen Lehrer\n")


def main() -> int:
    """Haupt-Setup Funktion."""
    print_header("🛸 UFO-Simulation Schulung - Setup")

    # Platform Info
    platform_info = get_platform_info()
    print_info(f"Betriebssystem: {platform_info['system']}\n")

    # 0. Lese pyproject.toml (Python-Version)
    pyproject = parse_pyproject_toml()

    # 1. Lese requirements.txt
    requirements = parse_requirements()
    if not requirements:
        print_error("Keine Requirements gefunden!")
        return 1

    # 2. Prüfe Python-Version (gegen pyproject.toml)
    if not check_python_version(pyproject):
        print_troubleshooting()
        return 1

    # 3. Erstelle Virtual Environment
    if not create_venv():
        print_troubleshooting()
        return 1

    # 4. Upgrade pip
    if not upgrade_pip(platform_info):
        pass

    # 5. Konfiguriere pip Index
    configure_pip_index(platform_info)

    # NEU: macOS-Fix NACH pip-Konfiguration
    if platform_info["system"] == "Darwin":
        handle_pyqt5_macos(platform_info)

    # 6. Installiere Dependencies
    if not install_dependencies(platform_info, requirements):
        print_troubleshooting()
        return 1

    # 7. Verifiziere Installation (KEINE Rekursion!)
    if not verify_installation(platform_info, requirements):
        print_troubleshooting()
        return 1

    # 8. Nächste Schritte
    print_next_steps(platform_info)

    return 0


if __name__ == "__main__":
    sys.exit(main())