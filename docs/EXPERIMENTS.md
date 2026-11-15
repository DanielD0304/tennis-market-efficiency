# Experimente: Protokoll und Log

Jede Änderung, die den Log Loss verbessern soll (Feature, Rating, Hyperparameter, Kalibrierung, Datenkorrektur mit
Modellwirkung), wird nach diesem Protokoll gemessen und hier eingetragen, auch wenn sie nichts bringt. Ein
verworfenes Experiment ist ein Ergebnis.

Anlass: Am 27.10.2026 erschien ein GO im Timing-Backtest, das sich als Artefakt herausstellte, und die Regeln wurden
danach angepasst (#27). Je öfter man am selben Backtest dreht, desto weniger sagt er.

## Fenster

| Fenster | Jahre | Wofür |
|---|---|---|
| Historie | ab 2015 | Elo, Features, Training. Elo2-Parameter werden nur auf Daten vor 2020 gewählt |
| **Dev** | 2021–2024 | Alle Experimente, alle Entscheidungen |
| **Holdout** | 2025–2026 | Nur zur Abnahme eines Milestones, einmal, mit allen angenommenen Änderungen zusammen |
| Forward | ab Start des Ledgers (#38) | Der eigentliche Test, lässt sich nicht überanpassen |

Der Holdout hat seit Juni 2026 schlechtere Daten (Scores, Ränge, siehe `ROADMAP.md`). Deshalb wird er getrennt
berichtet: bis 05/2026 und ab 06/2026.

Innerhalb des Dev-Fensters gilt für Suchen (Hyperparameter, #52): wählen auf 2021–2022, bestätigen auf 2023–2024.

## Ablauf eines Experiments

1. **Vorher aufschreiben** (im Issue): Hypothese, erwartete Größe, welche Schnitte der Diagnose (#39) sich bewegen
   sollen.
2. **Variante bauen**, ohne das Standardmodell zu ändern (`gbdt.<gruppe>`, siehe `src/feature_groups.py` auf dem
   Branch `claude/gbdt-features` bzw. nach #37 auf `main`).
3. **Vorlauf** mit jährlichem Refit (`--gbdt-refit year`), um grobe Fehler billig zu finden.
4. **Messung** mit quartalsweisem Refit auf dem Dev-Fenster, beide Touren, Variante gegen Basis auf derselben
   Stichprobe (gepaarter Bootstrap).
5. **Entscheidung** nach der Annahmeregel.
6. **Eintrag** im Log unten, Ergebnis ins Issue, bei Annahme: Standardmodell, Live-Pfad und Live-Modell nachziehen.

Bis der Befehl aus #37 existiert, läuft die Messung über
`python -m src.evaluation.backtest --start 2021 --end 2024 --tour atp --level all --models market,elo2,gbdt,<variante>`
und die Tabelle `metrics.compare_to_base` vom Branch `claude/gbdt-features`.

## Annahmeregel

Eine Variante wird nur übernommen, wenn alle Punkte gelten:

1. Haupttour: Log Loss besser als die Basis, das 95-%-Konfidenzintervall der Differenz schließt die 0 aus.
2. Die Variante ist in mindestens zwei Dritteln der Quartale besser.
3. Kein Level wird signifikant schlechter (Challenger, ITF, jeweils beide Touren).
4. Die Differenz liegt über der Rauschgrenze (Streuung über Seeds, wird mit #36 gemessen und hier eingetragen).
5. Die Features sind live verfügbar. Ein Feature, das im Betrieb fehlt, zählt nicht.

Gilt 1 bis 4 nur für eine Tour, wird die Variante nur dort übernommen. Mehrere kleine Änderungen, die einzeln
unter der Rauschgrenze liegen, werden nicht gebündelt durchgewinkt, sondern als Bündel neu gemessen.

**Rauschgrenze:** noch nicht gemessen (#36). Anhaltspunkt: Das Mitteln von drei Seeds ändert den Log Loss um 0,0001.

**Laufzeit eines Experiments:** noch nicht gemessen (#36).

## Was nicht erlaubt ist

- Auf dem Holdout abstimmen oder nach einem Blick auf den Holdout nachbessern.
- Schwellen, Fenster oder die Annahmeregel nach einem Ergebnis ändern. Wer die Regel ändern will, schreibt das
  vorher in `ROADMAP.md` unter „Entscheidungen".
- Features, die das Match selbst sehen. `tests/test_features.py` erzwingt das für die vorhandenen Gruppen, neue
  Gruppen brauchen denselben Test.
- Ergebnisse nur im Docstring oder im PR-Text festhalten.

## Log

Differenzen als Log Loss Variante minus Basis, negativ ist besser. „Quartale" = Quartale, in denen die Variante
besser ist.

### Vor dem Protokoll (aus Docstrings und PRs übernommen, nicht nach der Regel oben gemessen)

| Datum | Variante | Tour, Fenster | alle Level | Haupttour | Quartale | Entscheidung | Quelle |
|---|---|---|---|---|---|---|---|
| 09.11.2026 | `refit_all` (Bäume nach dem Early Stopping auf allen Daten neu) | ATP, 2024–2026 | −0,0022 (0,5745 → 0,5723) | −0,0003 (0,6029 → 0,6026, nicht signifikant) | 11/12 | übernommen | PR #33 |
| 09.11.2026 | Zeitgewichte, Halbwertszeit 3 Jahre | ATP, 2024–2026 | +0,0000 | +0,0012 | | verworfen | `gbdt.py` |
| 09.11.2026 | 3 Seeds gemittelt | ATP, 2024–2026 | −0,0001 | | | verworfen (zu klein) | `gbdt.py` |
| 09.11.2026 | Level-Feature (main, challenger, itf) | ATP, 2024–2026 | +0,0002 | | | verworfen | `gbdt.py` |
| 09.11.2026 | `max_rounds` 6000 statt 2000 | WTA, 2024–2026 | −0,0001 (0,5415 → 0,5414) | | | 4000 übernommen | `gbdt.py` |
| 15.11.2026 | Mittel der Logits elo2 und gbdt (Gewicht 0,2) | ATP und WTA, 2024–2026, Haupttour | | 0,0000 | | verworfen | Analyse, #55 |
| 15.11.2026 | Platt-Kalibrierung je Level | 2024–2026 | Steigung 0,95 bis 1,02, also kaum etwas zu holen | | | nicht verfolgt | Analyse, #39 |

### Nach Protokoll

| Datum | Issue | Commit | Tour | Variante | Fenster | n | alle Level | Haupttour | Haupttour scharf | 95-%-KI Haupttour | Quartale | Entscheidung |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | | |
