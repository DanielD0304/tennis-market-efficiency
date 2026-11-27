# Roadmap (Stand 15.11.2026)

Diese Datei sagt, wohin das Projekt will und in welcher Reihenfolge. Die Arbeit selbst steht in den GitHub-Issues,
je Milestone gibt es ein Übersichts-Issue. Wie gemessen wird, steht in [`EXPERIMENTS.md`](EXPERIMENTS.md), die
Arbeitsregeln für Claude in [`../CLAUDE.md`](../CLAUDE.md).

## Wofür das Projekt steht

Eine ehrliche, reproduzierbare Prognose für Tennis-Matches (ATP und WTA, Haupttour, Challenger, ITF) mit dem Markt
als Messlatte, dazu ein Forward-Test auf Matches, die beim Vorhersagen noch nicht gespielt waren. Das Projekt bleibt
nicht-kommerzielle Forschung, die Lizenzen von Sackmann (CC BY-NC-SA) und TennisMyLife lassen nichts anderes zu.

Die Frage „schlägt ein Modell den Markt?" ist bisher mit Nein beantwortet. Sie bleibt als Forschungsspur mit festem
Protokoll offen (M4), ist aber nicht mehr das, woran die tägliche Arbeit gemessen wird.

## Kennzahlen

**North Star: Gap zum Markt** = Log Loss des Modells minus Log Loss des Markts, auf Haupttour-Matches mit scharfem
Preis (Pinnacle, sonst Betfair Exchange), im Walk-forward.

| Kennzahl | Stand 15.11.2026 | nach M1 | nach M2 |
|---|---|---|---|
| Gap ATP-Haupttour (2024–2026) | 0,0079 | höchstens 0,008 | höchstens 0,006 |
| Gap WTA-Haupttour (2024–2026) | 0,0122 (2026 allein 0,0184) | höchstens 0,009 | höchstens 0,007 |
| Log Loss ATP, alle Level (2024–2026) | 0,5723 | | höchstens 0,568 |
| Forward-Ledger | zurückgestellt (Entscheidung vom 27.11.2026) | | erst nach einem GO im Backtest |

Die Zielwerte sind Hypothesen. Den Markt zu erreichen ist unwahrscheinlich. Die Werte in der Spalte „Stand" stammen
aus den Vorhersagen vom 27.10.2026 und werden mit #36 durch eine frische Baseline ersetzt (`docs/BASELINE.md`).

## Was die Analyse vom 15.11.2026 ergeben hat

Gerechnet auf `data/eval/timing_predictions.parquet` (Walk-forward 2024–2026) und `data/matches.csv`.

| Befund | Zahl | Issue |
|---|---|---|
| Die Tabelle in der README ist veraltet | 0,6089 gegen 0,5891 stammt aus PR #10, vor Challenger/ITF-Daten, Power-Marge, `refit_all` und TML. Aktuell ATP 0,6027 gegen 0,5948 | #36 |
| Phantom-Spieler aus tennis-data-Kürzeln (`Wang Xin.`, `Osorio M.`) | fünf Namen tragen 16 % des WTA-Gaps 2024–2026 und ein Drittel des Gaps 2026 | #40 |
| Spieler-Identitäten reißen ab | 1.950 neue ATP-Entitäten von Juni bis November 2026, in den Vorjahren rund 400 | #41 |
| Scores fehlen seit dem Sackmann-Ende | ITF 0 %, ATP-Challenger 60 bis 65 %, WTA-Haupttour 55 bis 70 %. Ohne Score rechnet `features.py` mit 50 % Game-Anteil | #42, #44 |
| Ränge veralten | ITF: Rang für beide Spieler nur noch bei 38 bis 66 % | #45 |
| Der Gap entsteht, wo Modell und Markt weit auseinanderliegen | 3 bis 5 % der Matches (Abstand über 15 Punkte) tragen 34 bis 39 % des Gaps | #39, #49 |
| Pausen | nach 14 bis 30 Tagen Pause ist der Gap doppelt so groß (ATP 0,0127 gegen 0,0069, WTA 0,0246 gegen 0,0093) | #48 |
| Frühe Runden und Grand Slams | R128: 0,0105 (ATP), 0,0157 (WTA) | #51 |
| Kalibrierung ist kein Hebel | Platt-Steigung von gbdt 0,95 bis 1,02 auf allen Leveln, Mittel mit elo2 bringt 0 | |
| gbdt nutzt keine Aufschlag- und Return-Werte | vier Feature-Gruppen liegen ungemessen auf `claude/gbdt-features` | #47 |
| Paper-Trading v1 | 434 Modell-Wetten, CLV −4,9 %, erwarteter Edge +11 %, also NO-GO | #27 |
| Betrieb | Paper-Loop und Nightly stehen seit dem Repo-Umzug am 15.11. | #35 |

Die wichtigste Einsicht: Der größte gemessene Hebel liegt in den Daten seit Juni 2026, nicht im Modell. Deshalb
kommt M1 vor M2.

## Milestones

Reihenfolge ist Priorität. Innerhalb eines Milestones gilt die Reihenfolge im Übersichts-Issue.

| Milestone | Ziel | Übersicht |
|---|---|---|
| **M0 Betrieb & Fundament** | Loops laufen, Baseline stimmt, Experimente sind mit einem Befehl messbar, der Ledger sammelt | #66 |
| **M1 Datenintegrität** | Identitäten, Scores, Ränge und Überwachung seit dem Sackmann-Ende | #67 |
| **M2 Modell** | Features und Ratings, jedes Issue ein Experiment | #68 |
| **M3 Produkt** | Dashboard (Heute, Track Record, Data Health), Modell-Versionen, Tageslauf, Aufräumen | #69 |
| **M4 Edge-Forschung** | festes Protokoll, Paper v2 auf reparierten Daten, genau ein neuer Timing-Backtest | #70 |

Seit dem 27.11.2026 läuft nichts dauerhaft (siehe „Entscheidungen“): Snapshots, Paper-Trading und Ledger ruhen.
M3 darf parallel zu M2 laufen, sobald der Ledger Daten hat.

## Entscheidungen

| Datum | Entscheidung | Grund |
|---|---|---|
| 15.11.2026 | North Star ist der Gap zum Markt, nicht der Wett-Yield | Der Gap ist auf Tausenden Matches messbar, ein Yield erst nach Tausenden Wetten |
| 15.11.2026 | Daten vor Modell (M1 vor M2) | Ein Drittel des WTA-Gaps 2026 ist ein Namensfehler, ITF läuft ohne Scores |
| 15.11.2026 | Transformer wird Legacy (#26, #55) | gbdt ist das Live-Modell, der Transformer wird im Walk-forward nicht neu trainiert, die Hebel liegen woanders |
| 15.11.2026 | Experimente nur nach Protokoll, Holdout 2025–2026 | Schutz vor Überanpassung an den Backtest, Anlass war das falsche Timing-GO vom 27.10. |
| 15.11.2026 | Wetten eingefroren: keine neuen Strategien oder Regeln vor M1 | Paper v1 ist NO-GO, und es lief auf den schlechtesten Daten |
| 15.11.2026 | Features mit Marktwissen (#49) sind für die Prognose erlaubt, werden aber getrennt ausgewiesen | Sie nutzen nur frühere Preise, verändern aber die Aussage „Modell gegen Markt" |
| 27.11.2026 | **Kein Dauerbetrieb.** Paper-Loop, Odds-API-Abfrage und Nightly sind als geplante Aufgaben deaktiviert. Gearbeitet wird mit einzelnen Benchmarks auf Abruf. Prediction-Ledger (#38), Tageslauf (#57) und die Dashboards „Heute“ und „Track Record“ (#58, #59) sind bis dahin zurückgestellt | Daniel: Das Projekt ist kein Produktivsystem zum Wetten, solange kein Modell den Markt schlägt. Preis dafür: Quoten-Snapshots und Orderbücher aus dieser Zeit fehlen später und lassen sich nicht nachholen. Wieder einschalten erst, wenn der Backtest ein GO liefert |

Neue Entscheidungen bitte hier anhängen, mit Datum und Grund.

## Bewusst nicht geplant

- Weiterentwicklung des Transformers oder ein Umbau auf Deep Learning.
- Neue Wettstrategien, bevor das Protokoll (#27) steht und M1 erledigt ist.
- Öffentliches Hosting oder ein kommerzielles Angebot (Lizenzen).
- Live-Wetten (In-Play) und andere Märkte als der Matchsieger.

## So ist die Arbeit organisiert

- **Issues** sind die einzige Liste. Jedes Issue trägt Befund, Aufgabe, Akzeptanz und, wo sinnvoll, eine Erwartung.
- **Milestones** M0 bis M4, je ein Übersichts-Issue (Label `tracking`) mit Reihenfolge.
- **Labels:** `area:data|model|eval|product|ops|research`, `prio:P0|P1|P2`,
  `type:experiment|bug|feature|chore|spike`, `needs:human` (braucht Daniel: Rechner, Konto, Schlüssel, Entscheidung).
- **Was als Nächstes?** `gh issue list --milestone "M0 Betrieb & Fundament" --label prio:P0 --state open`, dann das
  oberste aus dem Übersichts-Issue.
- **Fertig heißt:** Akzeptanzkriterien erfüllt, Tests grün, Messung im Experiment-Log (auch negative), Doku
  angepasst, PR mit `Closes #N`.
