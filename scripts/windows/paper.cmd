@echo off
rem Paper-Trading als Dauerprozess (eine Runde alle 30 Minuten), Ausgabe nach data\paper\run.log.
rem Die Aufgabe "TennisPaper" startet dieses Skript alle 30 Minuten. Laeuft der Loop noch, startet die
rem Aufgabenplanung keine zweite Instanz. Bricht er ab, startet ihn der naechste Termin neu.
rem Python: Variable TENNIS_PYTHON (z. B. set "TENNIS_PYTHON=C:\Pfad\python.exe"), sonst der Python-Launcher.
if not defined TENNIS_PYTHON set "TENNIS_PYTHON=py -3"
set PYTHONIOENCODING=utf-8
cd /d "%~dp0..\.." || exit /b 1
if not exist data\paper mkdir data\paper
echo ==== %date% %time% Start paper.cmd >> data\paper\run.log
%TENNIS_PYTHON% -m src.paper.run --loop 30 >> data\paper\run.log 2>&1
