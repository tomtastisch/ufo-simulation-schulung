bitte analysiere die #file:setup.py diese ist eigentlich auch darauf ausgelegt aufzuräumen (alte .venv etc) und
anschließend zu prüfen, welche der packete die benötigt werden bereits installiert sind und/oder gegebenenfalls
nachinstallieren. Es soll aufgrund dessen verwendet werden, damit schüler sich um das im lehrrahmen geplanten
Aufgaben (=>die tasks welche zukünftig noch weiter ausgebaut werden und mehr sub-tasks erhalten, aufbauend auf den im
core enthaltenen inhalten) konzentreieren können. dies stellt sicher das er sich zielgerichtet mit dem themen
auseinandersetzt, welche relevant sind. Das #setup.py soll deshalb vorbereitende maßnahmen, wie beispielsweise der
installation und konfiguration, welche notwendig zur ausführung sind umsetzen und sicherstellen, dass durch verwenden
mithilfe von .venv sichergestellt ist, das ide und os unabhängig immer, jeder schüler crossplattform/unabhängig seine
aufgaben umsetzen und ausführen kann. Zur sicherstellung der Erweiterbarkeit ohne große umbauten sollen packete in
#file:requirements.txt zentral verwaltet und dynamisch während des setups geladen werden.

-

# Geplanter Vorgang und Ablauf

Der geplante Vorgang und Ablauf zur Einrichtung und Vorbereitung des Schülers für die
es gibt darum dem Schüler das grundlegende Wissen zu vermitteln und dabei sicher zu stellen,
das er im Rahmen der Umsetzung des Wissens auf die realitätsnahe Arbeit vorbereitet ist.
Der gesamte Ablauf setzt voraus, das jegliche Umsetzung so erfolgt, dass der Rahmen, in welchem
er sein Wissen anwendet, klar und ohne hohe Komplexität unnötig zur Verwirrung sorgt.
Deshalb werden bestimmte Inhalte, wie beispielsweise das Setup von uns übernommen (setup.py) und
somit Sichergestellt dass der Schüler sich auf das wesentliche konzentrieren kann.
zukünftigen Aufgaben und Projekte gliedert sich in folgende Phasen:

*Wichtig*: Programmiersprache wird python sein

## Vorausgehende Maßnahmen zur Vorbereitung

Diese sind irrelevant für uns und wir gehen immer von einer umfassenden und entsprechend
ausgearbeiteten Vorbereitung der schüler aus. Jedoch dient diese Information um dir den
Kompletten Vorgang zu erläutern

-

### Grundlegende Einführung zum thema

(beispiele):
-> Themen der programmierung
-> Github/Versionsverwaltung
-> etc.

### Weitere Themen und Informationen...

    ...

## Projekteinführung und Einrichtung der Entwicklungsumgebung

Hierbei werden Möglichkeiten zum Erstellen von Projekten und deren Einrichtung vorgestellt.
Hierbei werden Mögliche IDE's, Spezifikationen und Anforderungen erläutert. Dabei wird der
Schüler angeleitet, wie er seine Entwicklungsumgebung einrichtet und konfiguriert, um die
notwendigen Voraussetzungen für die Arbeit an den Projekten zu erfüllen.

### Angeleitete Installation und Einrichtung der Entwicklungsumgebung

Als Basis zur Umsetzung muss auch die Installation der Entwicklungsumgebung angeleitet werden.
Da diese aufgrund der verschiedenen Betriebssysteme und deren Unterschiede sehr komplex sind,
soll hierbei eine angeleitete Installation und Einrichtung der Entwicklungsumgebung vorgenommen werden.
Zusätzlich gibt es zur Vereinfachung und besseren Klarheit auch die Optionen der zu verwendenden IDE's
vorgegeben, aus der jeder Schüler seine Wahl treffen kann.

    - Anhand vorgegebener Möglichkeiten zur Auwahl eienr IDE (Wichtig um Ausnahmefälle zu vermeiden)
    - Anleiten des Schülers und Hilöfestellung bei aufkommenden Fragen
    - Fertigstellung und Prüfung ob alle den selben Stand haben

### Vorbereitende Maßnahmen zur Projekteinrichtung

Hierbei werden Details zur Einrichtung der Projekte vorgestellt. Es geht darum, sicherzustellen,
dass der Schüler alle notwendigen Werkzeuge und Zugänge hat, um effektiv am Projekt arbeiten zu können.

    - Klärung offener Fragen
    - Sicherstellung das alle notwendigen Werkzeuge installiert sind
    - Sicherstellung das alle notwendigen Zugänge (z.B. GitHub) vorhanden sind
    - Berechtigungen zur Verwendung der Projekte

### Einstieg in die Projektsarbeit

Diese Maßnahmen sind die Schnittstelle zwischen dem theoretischen Vorwissen und der praktischen
Arbeit am Projekt. Hierbei wird der Schüler in die Lage versetzt, das Projekt zu verstehen und
die notwendigen Schritte zur Arbeit am Projekt zu kennen.

    - Einführung in die Versionsverwaltung mit Git/GitHub (Projektbezogene Infos)
    - Laden des Repositories aus GitHub
    - Gemeinsames Verständnis der Projektziele und -anforderungen
    - Erklärung der Projektstruktur und deren Zwecke/Inhalte

## Detaillierte Phasen der Projektdurchführung

Die detaillierten Phasen der Projektdurchführung umfassen spezifische Aufgaben und Meilensteine,
die der Schüler im Verlauf des Projekts erreichen soll. Jede Phase ist darauf ausgelegt,
bestimmte Fähigkeiten zu entwickeln und das Verständnis für die Projektarbeit zu vertiefen.

### Phase 1: Versionsverwaltung/Projekte starten

Hier wird die Basis für die Arbeit am Projekt gelegt. Weitestgehend soll der Schüler nur verstehen und
klar erkennen, wie er das Projekt startet und die notwendigen Werkzeuge verwendet. Es ist wichtig das
er durch den realitätsnahen Aufbau des Projekts und Ablaufs, sich auf die zukünftigen Aufgaben und Projekte
vorbereitet fühlt und die notwendigen Kenntnisse besitzt um diese umzusetzen.

*Wichtig:* Der Schüler wird angeleitet, das Projekt mithilfe der `setup.py` zu starten, um sicherzustellen, dass alle
notwendigen Abhängigkeiten installiert sind und die Entwicklungsumgebung korrekt eingerichtet ist. Diese Aufgabe ist
nicht von ihm manuell auszuführen, da es den geplanten Lernprozess durch dessen (teilweise hoher) Komplexität stören
würde

    - Erstellen eines neuen Branches - nach Vorgabe - um das Projekt zu starten
    - Gemeinsames Starten des Projekts
    - Ausführen der `setup.py` zur Sicherstellung, dass alle notwendigen Abhängigkeiten installiert sind (!)
    - Klärung eventueller Probleme bei der Einrichtung (z.B. Fehlermeldungen)

### Phase 2: Arbeit am Projektbitte analysiere die #file:setup.py diese ist eigentlich auch darauf ausgelegt aufzuräumen (alte .venv etc) und anschließend zu prüfen, welche der packete die benötigt werden bereits installiert sind und/oder gegebenenfalls nachinstallieren. Es soll aufgrund dessen verwendet werden, damit schüler sich um das im lehrrahmen geplanten Aufgaben (=>die tasks welche zukünftig noch weiter ausgebaut werden und mehr sub-tasks erhalten, aufbauend auf den im core enthaltenen inhalten) konzentreieren können. dies stellt sicher das er sich zielgerichtet mit dem themen auseinandersetzt, welche relevant sind. Das #setup.py soll deshalb vorbereitende maßnahmen, wie beispielsweise der installation und konfiguration, welche notwendig zur ausführung sind umsetzen und sicherstellen, dass durch verwenden mithilfe von .venv sichergestellt ist, das ide und os unabhängig immer, jeder schüler crossplattform/unabhängig seine aufgaben umsetzen und ausführen kann. Zur sicherstellung der Erweiterbarkeit ohne große umbauten sollen packete in #file:requirements.txt  zentral verwaltet und dynamisch während des setups geladen werden.

-

# Geplanter Vorgang und Ablauf

Der geplante Vorgang und Ablauf zur Einrichtung und Vorbereitung des Schülers für die
es gibt darum dem Schüler das grundlegende Wissen zu vermitteln und dabei sicher zu stellen,
das er im Rahmen der Umsetzung des Wissens auf die realitätsnahe Arbeit vorbereitet ist.
Der gesamte Ablauf setzt voraus, das jegliche Umsetzung so erfolgt, dass der Rahmen, in welchem
er sein Wissen anwendet, klar und ohne hohe Komplexität unnötig zur Verwirrung sorgt.
Deshalb werden bestimmte Inhalte, wie beispielsweise das Setup von uns übernommen (setup.py) und
somit Sichergestellt dass der Schüler sich auf das wesentliche konzentrieren kann.
zukünftigen Aufgaben und Projekte gliedert sich in folgende Phasen:

*Wichtig*: Programmiersprache wird python sein

## Vorausgehende Maßnahmen zur Vorbereitung

Diese sind irrelevant für uns und wir gehen immer von einer umfassenden und entsprechend
ausgearbeiteten Vorbereitung der schüler aus. Jedoch dient diese Information um dir den
Kompletten Vorgang zu erläutern

-

### Grundlegende Einführung zum thema

(beispiele):
-> Themen der programmierung
-> Github/Versionsverwaltung
-> etc.

### Weitere Themen und Informationen...

    ...

## Projekteinführung und Einrichtung der Entwicklungsumgebung

Hierbei werden Möglichkeiten zum Erstellen von Projekten und deren Einrichtung vorgestellt.
Hierbei werden Mögliche IDE's, Spezifikationen und Anforderungen erläutert. Dabei wird der
Schüler angeleitet, wie er seine Entwicklungsumgebung einrichtet und konfiguriert, um die
notwendigen Voraussetzungen für die Arbeit an den Projekten zu erfüllen.

### Angeleitete Installation und Einrichtung der Entwicklungsumgebung

Als Basis zur Umsetzung muss auch die Installation der Entwicklungsumgebung angeleitet werden.
Da diese aufgrund der verschiedenen Betriebssysteme und deren Unterschiede sehr komplex sind,
soll hierbei eine angeleitete Installation und Einrichtung der Entwicklungsumgebung vorgenommen werden.
Zusätzlich gibt es zur Vereinfachung und besseren Klarheit auch die Optionen der zu verwendenden IDE's
vorgegeben, aus der jeder Schüler seine Wahl treffen kann.

    - Anhand vorgegebener Möglichkeiten zur Auwahl eienr IDE (Wichtig um Ausnahmefälle zu vermeiden)
    - Anleiten des Schülers und Hilöfestellung bei aufkommenden Fragen
    - Fertigstellung und Prüfung ob alle den selben Stand haben

### Vorbereitende Maßnahmen zur Projekteinrichtung

Hierbei werden Details zur Einrichtung der Projekte vorgestellt. Es geht darum, sicherzustellen,
dass der Schüler alle notwendigen Werkzeuge und Zugänge hat, um effektiv am Projekt arbeiten zu können.

    - Klärung offener Fragen
    - Sicherstellung das alle notwendigen Werkzeuge installiert sind
    - Sicherstellung das alle notwendigen Zugänge (z.B. GitHub) vorhanden sind
    - Berechtigungen zur Verwendung der Projekte

### Einstieg in die Projektsarbeit

Diese Maßnahmen sind die Schnittstelle zwischen dem theoretischen Vorwissen und der praktischen
Arbeit am Projekt. Hierbei wird der Schüler in die Lage versetzt, das Projekt zu verstehen und
die notwendigen Schritte zur Arbeit am Projekt zu kennen.

    - Einführung in die Versionsverwaltung mit Git/GitHub (Projektbezogene Infos)
    - Laden des Repositories aus GitHub
    - Gemeinsames Verständnis der Projektziele und -anforderungen
    - Erklärung der Projektstruktur und deren Zwecke/Inhalte

## Detaillierte Phasen der Projektdurchführung

Die detaillierten Phasen der Projektdurchführung umfassen spezifische Aufgaben und Meilensteine,
die der Schüler im Verlauf des Projekts erreichen soll. Jede Phase ist darauf ausgelegt,
bestimmte Fähigkeiten zu entwickeln und das Verständnis für die Projektarbeit zu vertiefen.

### Phase 1: Versionsverwaltung/Projekte starten

Hier wird die Basis für die Arbeit am Projekt gelegt. Weitestgehend soll der Schüler nur verstehen und
klar erkennen, wie er das Projekt startet und die notwendigen Werkzeuge verwendet. Es ist wichtig das
er durch den realitätsnahen Aufbau des Projekts und Ablaufs, sich auf die zukünftigen Aufgaben und Projekte
vorbereitet fühlt und die notwendigen Kenntnisse besitzt um diese umzusetzen.

*Wichtig:* Der Schüler wird angeleitet, das Projekt mithilfe der `setup.py` zu starten, um sicherzustellen, dass alle
notwendigen Abhängigkeiten installiert sind und die Entwicklungsumgebung korrekt eingerichtet ist. Diese Aufgabe ist
nicht von ihm manuell auszuführen, da es den geplanten Lernprozess durch dessen (teilweise hoher) Komplexität stören
würde

    - Erstellen eines neuen Branches - nach Vorgabe - um das Projekt zu starten
    - Gemeinsames Starten des Projekts
    - Ausführen der `setup.py` zur Sicherstellung, dass alle notwendigen Abhängigkeiten installiert sind (!)
    - Klärung eventueller Probleme bei der Einrichtung (z.B. Fehlermeldungen)

### Phase 2: Arbeit am Projekt

Hier beginnt die eigentliche Arbeit am Projekt. Der Schüler wird angeleitet, wie er erste Änderungen vornimmt und diese
in das Versionsverwaltungssystem einpflegt. Dies umfasst das Verständnis der grundlegenden Git-Befehle und die Anwendung
dieser im Kontext des Projekts
Mithilfe von vordefinierten Aufgaben werden erste Grundlegende Programmiererfahrungen gesammelt, welche durch erstellen
einzelner Skripts (also weder verwendung von Klassen oder funktionen) ermöglicht werden sollen.

    - Erste Änderungen vornehmen und committen
    - Committen der Änderungen und Pushen (Remote-Repository selbst bleibt sauber) 

Hier beginnt die eigentliche Arbeit am Projekt. Der Schüler wird angeleitet, wie er erste Änderungen vornimmt und diese
in das Versionsverwaltungssystem einpflegt. Dies umfasst das Verständnis der grundlegenden Git-Befehle und die Anwendung
dieser im Kontext des Projekts
Mithilfe von vordefinierten Aufgaben werden erste Grundlegende Programmiererfahrungen gesammelt, welche durch erstellen
einzelner Skripts (also weder verwendung von Klassen oder funktionen) ermöglicht werden sollen.

    - Erste Änderungen vornehmen und committen
    - Committen der Änderungen und Pushen (Remote-Repository selbst bleibt sauber) 

... continue