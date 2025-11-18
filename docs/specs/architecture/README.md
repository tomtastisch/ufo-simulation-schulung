# Architektur-Dokumentation – core.simulation

Dieses Verzeichnis enthält die verbindliche Architektur-Dokumentation für das `src/core/simulation/` Paket.

---

## Verfügbare Dokumente

### 1. [core-simulation-zielbild.md](./core-simulation-zielbild.md)

**Status:** ✅ Aktiv und verbindlich  
**Erstellt in:** Ticket T0 (Phase 0)  
**Zweck:** Definiert die Zielarchitektur nach Abschluss aller Refactoring-Phasen

**Inhalt:**
- Vollständige Paketstruktur (8 Teilpakete)
- Öffentliche API-Definition
- Verantwortlichkeiten aller Module
- Import-Hierarchie und Abhängigkeitsregeln
- Threading-Modell
- Qualitätskriterien
- Referenz für Tickets T1–T17

**Zielgruppe:**
- Entwickler (während Refactoring-Phasen)
- Reviewer (Code-Review)
- Tech Lead (Architektur-Entscheidungen)
- Externe Nutzer (API-Spezifikation)

---

## Beziehung zu anderen Dokumenten

| Dokument                                      | Zweck                                    | Beziehung                                      |
|-----------------------------------------------|------------------------------------------|------------------------------------------------|
| `docs/specs/notes/introductions.md`           | Detaillierter Ablaufplan (Phasen 1–9)    | Basis für Zielbild; beschreibt Umsetzungsweg   |
| `docs/planning/refactoring-tracker.md`        | Ticket-Übersicht (T0–T17)                | Verweist auf Zielbild als Referenz             |
| `docs/guidelines/general-gd.md`               | Allgemeine Code-Richtlinien              | Gilt auch für core.simulation                  |
| `docs/guidelines/project-specific-gd.md`      | Simulations-spezifische Richtlinien      | Ergänzt Zielbild um fachliche Vorgaben         |

---

## Nutzung

### Für Entwickler während Refactoring (T1–T17):

1. **Vor Beginn eines Tickets:**
   - Lese den relevanten Abschnitt in `core-simulation-zielbild.md`
   - Prüfe Import-Hierarchie (Abschnitt 5)
   - Beachte Verantwortlichkeiten des betroffenen Pakets

2. **Während der Implementierung:**
   - Halte dich strikt an die definierten Abhängigkeitsregeln
   - Nutze nur die dokumentierten öffentlichen APIs
   - Orientiere dich an den Dateistrukturen (Abschnitt 2)

3. **Code-Review:**
   - Prüfe Konformität mit Zielbild
   - Achte auf verbotene Importe (Abschnitt 5.2)
   - Validiere Thread-Safety-Anforderungen (Abschnitt 7)

### Für externe Nutzer:

- **Abschnitt 4:** Öffentliche API und Nutzungsbeispiele
- **Abschnitt 6:** Unterscheidung öffentlich/intern
- **Abschnitt 3:** Verantwortlichkeiten (um Module zu verstehen)

---

## Änderungshistorie

| Datum      | Dokument                     | Version | Änderung                    |
|------------|------------------------------|---------|----------------------------|
| 2025-11-18 | core-simulation-zielbild.md  | 1.0     | Initiale Erstellung (T0)    |
| 2025-11-18 | README.md                    | 1.0     | Navigation erstellt         |

---

## Hinweise

- **Alle Dokumente in diesem Verzeichnis sind verbindlich.**
- Änderungen am Zielbild erfordern Freigabe durch den Lead Developer.
- Bei Abweichungen zwischen Zielbild und Implementierung: Zielbild hat Vorrang (außer bei bewussten, dokumentierten Änderungen).

---

**Kontakt:** Lead Developer / Tech Reviewer  
**Letzte Aktualisierung:** 2025-11-18
