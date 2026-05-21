' Tradesight launcher - starts the app server with no visible console window.
' This script locates itself, so the project folder can be moved freely.
Set fso = CreateObject("Scripting.FileSystemObject")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

pythonw = scriptDir & "\.venv\Scripts\pythonw.exe"
appScript = scriptDir & "\run_app.py"

Set sh = CreateObject("WScript.Shell")
sh.CurrentDirectory = scriptDir
' Window style 0 = hidden, False = do not wait for it to finish
sh.Run """" & pythonw & """ """ & appScript & """", 0, False
