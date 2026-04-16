' Next2Flash Desktop Launcher — no console window
' Double-click this file to start Next2Flash silently.

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory this script lives in
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
electronDir = fso.BuildPath(scriptDir, "electron")
electronExe = fso.BuildPath(electronDir, "node_modules\electron\dist\electron.exe")

' Launch electron.exe directly (no cmd, no console window)
' 0 = hidden window, False = don't wait for exit
WshShell.Run Chr(34) & electronExe & Chr(34) & " " & Chr(34) & electronDir & Chr(34), 0, False
