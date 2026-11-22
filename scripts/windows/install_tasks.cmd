@echo off
rem Legt die drei Aufgaben TennisPaper, TennisOddsApi und TennisNightly in der Aufgabenplanung an (oder ersetzt sie).
rem Ohne Adminrechte, die Aufgaben laufen als angemeldeter Benutzer. Mit -WhatIf nur anzeigen, was angelegt wuerde:
rem   scripts\windows\install_tasks.cmd -WhatIf
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_tasks.ps1" %*
