# Arbeitsregeln für Claude in diesem Repo

## Worum es geht

Prognose von Tennis-Matches (ATP, WTA; Haupttour, Challenger, ITF) mit dem Markt als Messlatte. Kennzahl ist der
**Gap zum Markt** (Log Loss Modell minus Log Loss Markt, Haupttour, scharfer Preis, Walk-forward). Ziele, Befunde
und Reihenfolge stehen in `docs/ROADMAP.md`, das Messverfahren in `docs/EXPERIMENTS.md`.

## Was als Nächstes dran ist

Die Arbeit steht in den GitHub-Issues, geordnet nach Milestones M0 bis M4. Je Milestone gibt es ein
Übersichts-Issue mit der Reihenfolge (#66 bis #70).

```bash
gh issue list --milestone "M0 Betrieb & Fundament" --state open
gh issue view 66
```

Ohne andere Ansage von Daniel: frühester Milestone mit offenen Issues, darin das oberste offene Issue aus dem
Übersichts-Issue. Issues mit `needs:human` brauchen Daniel (Rechner, Konto, Schlüssel, Entscheidung): vorbereiten,
was geht, dann fragen.

## Ablauf je Issue

1. Issue ganz lesen, die genannten Dateien ansehen. Stimmt der Befund noch? Die Zahlen stammen vom 15.11.2026.
2. Branch `claude/<thema>` von `main`.
3. Umsetzen, Tests dazu. `python -m pytest` muss grün sein.
4. Bei allem, was den Log Loss ändern kann: messen nach `docs/EXPERIMENTS.md` und ins Log eintragen, auch bei
   negativem Ergebnis.
5. Doku nachziehen (`docs/DETAILS.md`, bei Kennzahlen `docs/BASELINE.md`, bei Entscheidungen `docs/ROADMAP.md`).
6. PR gegen `main` mit `Closes #N`, Messwerte in die Beschreibung. Daniel mergt.
7. Übersichts-Issue abhaken. Neue Funde als eigenes Issue mit Milestone und Labels anlegen, nicht nebenbei
   miterledigen.

Commit-Nachrichten wie bisher: `add:`, `fix:`, `perf:`, `test:`, `docs:` und ein deutscher Satz.

## Feste Regeln

- **Kein Blick in die Zukunft.** Features, Elo und Fits sehen nur Matches vor dem vorhergesagten Match. Die
  Leakage-Asserts in `evaluation/backtest.py` und `evaluation/predictors.py` und die Tests in
  `tests/test_features.py` bleiben, neue Feature-Gruppen bekommen denselben Test.
- **Nicht auf dem Holdout (2025–2026) abstimmen.** Entscheidungen fallen auf dem Dev-Fenster 2021–2024.
- **Regeln nicht nach dem Ergebnis ändern** (Annahmeregel, Go/No-Go, Schwellen). Wer eine Regel ändern will,
  schreibt das vorher in `docs/ROADMAP.md` unter „Entscheidungen".
- **Keine Daten ins Repo.** `data/` und `models/` sind ignoriert. Tests arbeiten mit erfundenen Zeilen
  (TennisMyLife erlaubt keine Weitergabe der Rohdaten, Sackmann ist CC BY-NC-SA).
- **Zahlen in README und Doku** kommen aus `docs/BASELINE.md` oder dem Experiment-Log, mit Datum und Befehl.
- **Ergebnisse ehrlich berichten.** Ein Feature, das nichts bringt, wird verworfen und eingetragen. Ein Yield ohne
  Konfidenzintervall oder auf wenigen hundert Wetten ist kein Beleg.
- **Wetten:** Die Spur ist eingefroren (M4). Keine neuen Strategien, Schwellen oder Segmente im Paper-Trading ohne
  Vorregistrierung nach #27.
- **Löschen und Überschreiben** (Branches, `data/`, Modelle) nur nach Rückfrage.

## Befehle

```bash
python -m pytest                                    # alle Tests
python -m src.update_data                           # Daten aktualisieren (--full: alles neu)
python -m src.evaluation.backtest --start 2021 --end 2024 --tour atp --models market,rank,elo,elo2,gbdt,stack
python -m src.evaluation.backtest --level all ...   # alle Level auswerten (Standard: Haupttour)
python -m src.models.gbdt --tour atp                # Live-Modell trainieren (auch --tour wta)
python -m src.paper.run --loop 30                   # Paper-Trading und Snapshots
python -m src.evaluation.timing                     # Timing-Backtest (nur nach #64)
cd betscraper && python manage.py runserver         # Dashboard
```

Ein Walk-forward über mehrere Jahre mit gbdt dauert lange. Im Hintergrund starten, `--no-refresh` setzen, wenn
die Daten gerade aktuell sind, und für einen Vorlauf `--gbdt-refit year` nehmen.

## Wo was liegt

| Bereich | Dateien |
|---|---|
| Quellen und Zusammenführung | `src/sources/` (`build.py`: Namen, Duplikate, Level), `src/names.py`, `src/update_data.py` |
| Ratings und Features | `src/elo.py`, `src/features.py`, `src/score.py`, `src/chronology.py` |
| Modelle | `src/models/gbdt.py`, `stack.py`, `calibration.py` |
| Messung | `src/evaluation/` (`backtest.py`, `predictors.py`, `metrics.py`, `betting.py`, `venues.py`, `timing.py`, `sharp.py`) |
| Quoten | `src/odds/` (Collector, Historie, Schema) |
| Live und Paper | `src/predict.py`, `src/paper/` |
| Dashboard | `betscraper/` (Django) |
| Legacy | Transformer: `src/model.py`, `train.py`, `preprocessing.py`, `dataset.py`, `main.py` (nicht weiterentwickeln, #26) |

Offene Vorarbeit: Branch `claude/gbdt-features` (Feature-Gruppen `serve`, `form`, `elox`, `market` und der
Vergleich `metrics.compare_to_base`), siehe #37 und #47.

## Umgebung

Windows 11, Python 3.13, Git Bash oder PowerShell. `data/matches.csv` hat rund 670.000 Zeilen und 150 MB, also
`pd.read_csv(..., low_memory=False)` und nur die nötigen Spalten laden. Doku und Issues sind auf Deutsch, die
README auf Englisch.
