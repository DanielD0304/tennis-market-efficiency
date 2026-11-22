@echo off
rem Naechtlicher Lauf: Daten aktualisieren, dann die Polymarket- und Kalshi-Historie nachladen.
rem Ausgabe nach data\odds\history.log. Die Aufgabe "TennisNightly" startet das Skript taeglich um 04:15.
if not defined TENNIS_PYTHON set "TENNIS_PYTHON=py -3"
set PYTHONIOENCODING=utf-8
cd /d "%~dp0..\.." || exit /b 1
if not exist data\odds mkdir data\odds
echo ==== %date% %time% >> data\odds\history.log
%TENNIS_PYTHON% -m src.update_data >> data\odds\history.log 2>&1 && %TENNIS_PYTHON% -m src.odds.collect --history >> data\odds\history.log 2>&1
