@echo off
rem Odds API (Pinnacle, Betfair und Co.) plus Polymarket und Kalshi im selben Fenster, Ausgabe nach data\odds\collect.log.
rem Kostet Kontingent (rund 4 Credits je Lauf bei 500 im Monat), die Aufgabe "TennisOddsApi" laeuft deshalb nur alle 8 Stunden.
rem Ohne ODDS_API_KEY ueberspringt der Collector die Odds API.
if not defined TENNIS_PYTHON set "TENNIS_PYTHON=py -3"
set PYTHONIOENCODING=utf-8
cd /d "%~dp0..\.." || exit /b 1
if not exist data\odds mkdir data\odds
%TENNIS_PYTHON% -m src.odds.collect --venues odds_api >> data\odds\collect.log 2>&1
