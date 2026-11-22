' Startet das uebergebene .cmd-Skript ohne sichtbares Fenster, wartet auf sein Ende und gibt den Exit-Code weiter.
' Aufruf (so legt es install_tasks.ps1 an): wscript.exe //B //NoLogo run_hidden.vbs "<Pfad zum .cmd>"
' Der Pfad wird in Anfuehrungszeichen weitergereicht, Leerzeichen im Repo-Pfad sind also kein Problem.
If WScript.Arguments.Count < 1 Then WScript.Quit 2
WScript.Quit CreateObject("WScript.Shell").Run("cmd /c """ & WScript.Arguments(0) & """", 0, True)
