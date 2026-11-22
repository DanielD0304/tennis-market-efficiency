# Legt die Aufgaben fuer den Dauerbetrieb an (oder ersetzt gleichnamige Aufgaben):
#   TennisPaper    alle 30 Minuten paper.cmd (Paper-Loop mit --loop 30, die Aufgabe wirkt als Waechter)
#   TennisOddsApi  alle 8 Stunden odds_api.cmd (nur wenn ODDS_API_KEY gesetzt ist, Kontingent 500 Credits im Monat)
#   TennisNightly  taeglich 04:15 nightly.cmd (update_data, dann odds.collect --history)
# Alle Pfade ergeben sich aus dem Ort dieses Skripts, das Repo kann also umziehen: danach einfach neu ausfuehren.
# Aufruf ueber install_tasks.cmd. Mit -WhatIf wird nur angezeigt, was angelegt wuerde.
# Die Datei bleibt ASCII, weil Windows PowerShell 5.1 Skripte ohne BOM in der ANSI-Codepage liest.
param([switch]$WhatIf)

$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
$repo = (Resolve-Path (Join-Path $here '..\..')).Path
$vbs = Join-Path $here 'run_hidden.vbs'

if (-not (Test-Path (Join-Path $repo 'src\paper\run.py'))) {
    throw "Repo nicht gefunden: $repo (erwartet src\paper\run.py)"
}

# Python wie in den .cmd-Skripten: TENNIS_PYTHON oder der Launcher. Fehlt pandas, laufen die Aufgaben ins Leere.
$py = $env:TENNIS_PYTHON
if (-not $py) { $py = [Environment]::GetEnvironmentVariable('TENNIS_PYTHON', 'User') }
if (-not $py) { $py = 'py -3' }
cmd /c "$py -c `"import pandas, lightgbm`"" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Warning "'$py' findet pandas oder lightgbm nicht. TENNIS_PYTHON als Benutzervariable auf das richtige python.exe setzen (setx TENNIS_PYTHON ...)."
}

$user = "$env:USERDOMAIN\$env:USERNAME"
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited

function New-TennisSettings([TimeSpan]$limit) {
    New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
        -StartWhenAvailable -ExecutionTimeLimit $limit
}

function Register-TennisTask($name, $script, $trigger, [TimeSpan]$limit, $description) {
    $cmdPath = Join-Path $here $script
    $action = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument "//B //NoLogo `"$vbs`" `"$cmdPath`"" -WorkingDirectory $repo
    if ($WhatIf) {
        Write-Host "[WhatIf] $name -> $cmdPath"
        return
    }
    Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Principal $principal `
        -Settings (New-TennisSettings $limit) -Description $description -Force | Out-Null
    Write-Host "angelegt: $name -> $cmdPath"
}

$now = Get-Date

# Paper-Loop laeuft dauerhaft, deshalb ohne Zeitlimit. Bricht er ab, startet ihn der naechste 30-Minuten-Termin neu.
$paperTrigger = New-ScheduledTaskTrigger -Once -At $now.AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 30)
Register-TennisTask 'TennisPaper' 'paper.cmd' $paperTrigger ([TimeSpan]::Zero) `
    'Paper-Trading mit --loop 30 (tennis_transformer, scripts\windows\paper.cmd)'

$key = $env:ODDS_API_KEY
if (-not $key) { $key = [Environment]::GetEnvironmentVariable('ODDS_API_KEY', 'User') }
if ($key) {
    $oddsTrigger = New-ScheduledTaskTrigger -Once -At $now.Date.AddHours(13).AddMinutes(5) -RepetitionInterval (New-TimeSpan -Hours 8)
    Register-TennisTask 'TennisOddsApi' 'odds_api.cmd' $oddsTrigger (New-TimeSpan -Hours 1) `
        'Odds API alle 8 Stunden (tennis_transformer, scripts\windows\odds_api.cmd)'
} else {
    Write-Warning 'ODDS_API_KEY ist nicht gesetzt: TennisOddsApi wird nicht angelegt (setx ODDS_API_KEY "...", dann erneut ausfuehren).'
}

$nightlyTrigger = New-ScheduledTaskTrigger -Daily -At '04:15'
Register-TennisTask 'TennisNightly' 'nightly.cmd' $nightlyTrigger (New-TimeSpan -Hours 6) `
    'update_data und Markt-Historie (tennis_transformer, scripts\windows\nightly.cmd)'

if (-not $WhatIf) {
    Write-Host ''
    Write-Host 'Pruefen: Get-ScheduledTask Tennis* | Get-ScheduledTaskInfo'
    Write-Host 'Sofort starten: Start-ScheduledTask TennisPaper'
}
