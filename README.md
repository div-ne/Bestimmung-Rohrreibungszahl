# Rohrreibungszahl Bestimmung

[**Zur Live-Anwendung**](https://rohrreibungszahl.streamlit.app/)

Ein webbasiertes Berechnungstool zur Bestimmung der **Rohrreibungszahl λ** auf Basis der in `Lambda.py` hinterlegten Logik. Die Anwendung verwendet Stoffdaten, Temperatur, Druck, Geometrie und Strömungsgeschwindigkeit, um daraus Reynolds-Zahl, relative Rauheit und die resultierende Rohrreibungszahl zu bestimmen.

## Funktionen

- Berechnung der **Rohrreibungszahl λ** gemäß der hochgeladenen Python-Logik
- Eingabe von **Fluid**, **Temperatur**, **Druck**, **Innendurchmesser**, **Strömungsgeschwindigkeit** und **Rohrrauhigkeit**
- Berechnung der **kinematischen Viskosität** über **CoolProp** und darauf aufbauend der Reynolds-Zahl
- Anzeige der **Berechnungsgrundlage** und des zugehörigen **Strömungstyps**
- Korrekte Auswahl von **Colebrook-White** nur als Fallback, wenn keine der vorherigen Bedingungen greift
- Vergleich der Ergebnisse aus **Hagen-Poiseuille**, **Blasius**, **Nikuradse**, **Prandtl** und **Colebrook-White**
- Zusätzliche Hilfebereiche für **Anleitung**, **Rohrrauheitswerte** und **Moody-Diagramm**
- Export der Ergebnisse als **CSV-Datei**

## Berechnungsgrundlage

Die Rohrreibungszahl wird anhand verschiedener Formeln bestimmt. So wird das gesamte Moody-Diagramm abgedeckt. Folgende Formeln werden betrachtet: Gesetz von Hagen-Poiseuille, Formeln nach Blasius, nach Nikuradse, nach Colebrook & White und nach Prandtl.

Die App zeigt zusätzlich an, welche Berechnungsgrundlage letztlich ausgewählt wurde und welchem Strömungstyp der berechnete Zustand zugeordnet ist. Damit wird direkt sichtbar, ob es sich um laminare Strömung, ein hydraulisch glattes Rohr, ein hydraulisch raues Rohr oder den Übergangsbereich handelt.

## Eingaben

Für die Berechnung werden folgende Eingaben benötigt:

- **Fluid**
- **Temperatur [°C]**
- **Druck [bar]**
- **Innendurchmesser [mm]**
- **Strömungsgeschwindigkeit [m/s]**
- **Rohrrauhigkeit [mm]**

## Ergebnisdarstellung

Die Anwendung zeigt:

- die berechnete **kinematische Viskosität**,
- die **Reynolds-Zahl**,
- die **relative Rauheit**,
- die ausgewählte **Berechnungsgrundlage**,
- den zugehörigen **Strömungstyp**,
- die resultierende **Rohrreibungszahl λ**,
- sowie eine aufklappbare Vergleichstabelle der einzelnen Formeln.

## Moody-Diagramm

Zusätzlich enthält die App einen aufklappbaren Bereich mit einem Moody-Diagramm zur Orientierung. Als Quelle ist die Wikipedia-Seite zum Moody-Chart verlinkt: [https://en.wikipedia.org/wiki/Moody_chart](https://en.wikipedia.org/wiki/Moody_chart).

## Technologie

Dieses Projekt basiert auf:

- **Python**
- **Streamlit** für die Weboberfläche
- **CoolProp** zur Bestimmung der Stoffwerte
- **NumPy** und **Pandas** für Berechnung und Ergebnisdarstellung
