#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analysiert Import-Hierarchie und Redundanzen im core.simulation Package."""

import ast
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

# Definiere die Hierarchie gemäß Spec
HIERARCHY = {
    0: ["exceptions", "infrastructure", "synchronization"],
    1: ["state", "utils", "physics"],
    2: ["command", "observer"],
    3: ["controller", "view"],
}

# Reverse Mapping
MODULE_LEVEL = {}
for level, modules in HIERARCHY.items():
    for mod in modules:
        MODULE_LEVEL[mod] = level


class ImportAnalyzer:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.imports_by_file = {}
        self.violations = []
        self.unused_imports = []
        self.redundant_imports = []

    def analyze_file(self, filepath: Path) -> Dict:
        """Analysiert eine einzelne Datei."""
        result = {
            'filepath': filepath,
            'imports': [],
            'from_imports': {},
            'used_names': set(),
        }

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)

            # Sammle Imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Extrahiere Modul-Name
                        if node.level == 2:  # from ..xyz
                            module_parts = node.module.split('.') if node.module else []
                            if module_parts:
                                base_module = module_parts[0]
                                result['imports'].append(base_module)
                                if base_module not in result['from_imports']:
                                    result['from_imports'][base_module] = []
                                for alias in node.names:
                                    result['from_imports'][base_module].append(alias.name)
                        elif node.level == 1:  # from .xyz
                            module_parts = node.module.split('.') if node.module else []
                            if module_parts:
                                result['imports'].append(f"local.{module_parts[0]}")

                # Sammle verwendete Namen (vereinfacht)
                elif isinstance(node, ast.Name):
                    result['used_names'].add(node.id)

        except Exception as e:
            result['error'] = str(e)

        return result

    def check_hierarchy(self, filepath: Path, imports: List[str]) -> List[Dict]:
        """Prüft Hierarchie-Einhaltung."""
        violations = []

        # Bestimme aktuelles Modul
        try:
            rel_path = filepath.relative_to(self.base_path)
            current_module = rel_path.parts[0] if rel_path.parts else None
        except ValueError:
            return violations

        if not current_module or current_module not in MODULE_LEVEL:
            return violations

        current_level = MODULE_LEVEL[current_module]

        for imported_module in imports:
            if imported_module.startswith('local.'):
                continue  # Interne Imports sind OK

            if imported_module not in MODULE_LEVEL:
                continue

            imported_level = MODULE_LEVEL[imported_module]

            # Regel: Darf nur von gleicher oder niedrigerer Ebene importieren
            if imported_level > current_level:
                violations.append({
                    'file': str(rel_path),
                    'current_module': current_module,
                    'current_level': current_level,
                    'imported_module': imported_module,
                    'imported_level': imported_level,
                })

        return violations

    def analyze_all(self):
        """Analysiert alle Dateien."""
        print("=" * 80)
        print("UMFASSENDE IMPORT-ANALYSE")
        print("=" * 80)

        # Sammle alle Python-Dateien
        py_files = list(self.base_path.rglob("*.py"))
        py_files = [f for f in py_files if '__pycache__' not in str(f)]

        print(f"\n📊 Analysiere {len(py_files)} Dateien...")

        # Analysiere jede Datei
        for filepath in py_files:
            result = self.analyze_file(filepath)
            self.imports_by_file[filepath] = result

            # Prüfe Hierarchie
            violations = self.check_hierarchy(filepath, result['imports'])
            self.violations.extend(violations)

        self.print_results()

    def print_results(self):
        """Gibt Analyse-Ergebnisse aus."""
        print("\n" + "=" * 80)
        print("1️⃣  HIERARCHIE-VALIDIERUNG")
        print("=" * 80)

        if self.violations:
            print(f"\n❌ {len(self.violations)} HIERARCHIE-VERLETZUNG(EN) GEFUNDEN:\n")
            for v in self.violations:
                print(f"FEHLER in {v['file']}:")
                print(f"  {v['current_module']} (Ebene {v['current_level']}) "
                      f"importiert {v['imported_module']} (Ebene {v['imported_level']})")
                print(f"  ❌ Höhere Ebene darf nicht von niedrigerer importiert werden!\n")
        else:
            print("\n✅ KEINE HIERARCHIE-VERLETZUNGEN\n")

        print("=" * 80)
        print("2️⃣  IMPORT-ÜBERSICHT PRO MODUL")
        print("=" * 80)

        # Gruppiere nach Modulen
        by_module = defaultdict(lambda: defaultdict(set))

        for filepath, result in self.imports_by_file.items():
            try:
                rel_path = filepath.relative_to(self.base_path)
                if rel_path.parts:
                    current_module = rel_path.parts[0]
                    for imp in result['imports']:
                        if not imp.startswith('local.'):
                            by_module[current_module][imp].add(str(rel_path))
            except:
                pass

        for module in sorted(by_module.keys()):
            if module not in MODULE_LEVEL:
                continue
            level = MODULE_LEVEL[module]
            print(f"\n{module}/ (Ebene {level}):")
            imports = by_module[module]
            if imports:
                for imp in sorted(imports.keys()):
                    imp_level = MODULE_LEVEL.get(imp, '?')
                    status = "✅" if isinstance(imp_level, int) and imp_level <= level else "❌"
                    print(f"  {status} → {imp} (Ebene {imp_level})")
            else:
                print("  (keine cross-module imports)")

        print("\n" + "=" * 80)
        print("3️⃣  SYNCHRONIZATION IMPORT-KONSISTENZ")
        print("=" * 80)

        sync_importers = defaultdict(list)
        utils_threads_importers = []

        for filepath, result in self.imports_by_file.items():
            try:
                rel_path = str(filepath.relative_to(self.base_path))

                # Prüfe synchronization imports
                if 'synchronization' in result['imports']:
                    sync_importers['direct'].append(rel_path)

                # Prüfe utils.threads imports (DEPRECATED)
                with open(filepath, 'r') as f:
                    content = f.read()
                if 'from ..utils.threads import' in content or 'from .threads import' in content:
                    utils_threads_importers.append(rel_path)
            except:
                pass

        if sync_importers['direct']:
            print(f"\n✅ {len(sync_importers['direct'])} Dateien nutzen synchronization korrekt:")
            for f in sorted(sync_importers['direct'])[:10]:
                print(f"  • {f}")
            if len(sync_importers['direct']) > 10:
                print(f"  ... und {len(sync_importers['direct']) - 10} weitere")

        if utils_threads_importers:
            print(f"\n⚠️  {len(utils_threads_importers)} Dateien nutzen DEPRECATED utils.threads:")
            for f in sorted(utils_threads_importers):
                print(f"  • {f}")
        else:
            print("\n✅ Keine Dateien nutzen utils.threads (deprecated)")

        print("\n" + "=" * 80)
        print("ZUSAMMENFASSUNG")
        print("=" * 80)

        if not self.violations and not utils_threads_importers:
            print("\n🎉 ALLE CHECKS BESTANDEN!")
            print("  ✅ Keine Hierarchie-Verletzungen")
            print("  ✅ Keine deprecated imports (utils.threads)")
            print("  ✅ Import-Struktur korrekt\n")
        else:
            print("\n⚠️  PROBLEME GEFUNDEN:")
            if self.violations:
                print(f"  ❌ {len(self.violations)} Hierarchie-Verletzung(en)")
            if utils_threads_importers:
                print(f"  ⚠️  {len(utils_threads_importers)} deprecated import(s)")
            print()


if __name__ == '__main__':
    base = Path(__file__).parent.parent / "src" / "core" / "simulation"
    analyzer = ImportAnalyzer(base)
    analyzer.analyze_all()
