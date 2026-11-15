---
name: Experiment
about: Änderung, die den Log Loss verbessern soll (Feature, Rating, Hyperparameter), gemessen nach docs/EXPERIMENTS.md
labels: "type:experiment, area:model"
---

## Befund

Was zeigt, dass hier etwas zu holen ist? Zahlen aus der Diagnose (`python -m src.evaluation.diagnose`) oder aus dem Experiment-Log.

## Hypothese und Erwartung

Was soll sich ändern, um wie viel, und in welchem Schnitt der Diagnose?

## Aufgabe

Welche Variante (`gbdt.<gruppe>`), welche Dateien, was lässt sich wiederverwenden?

## Messung

Nach `docs/EXPERIMENTS.md`: Dev-Fenster 2021–2024, beide Touren, Eintrag im Log auch bei negativem Ergebnis. Nichts auf dem Holdout abstimmen.

## Akzeptanz

- [ ] Log-Zeile je Variante und Tour
- [ ] Entscheidung nach der Annahmeregel, Ergebnis hier im Issue
- [ ] Bei Annahme: Standardmodell, Live-Pfad und Live-Modell nachgezogen
