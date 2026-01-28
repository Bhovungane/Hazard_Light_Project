' VBScript to create desktop shortcut for inspection system
' Double-click this file to create a shortcut on desktop

Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.SpecialFolders("Desktop") & "\Vehicle Inspection.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)

' Get current script directory
Set fso = CreateObject("Scripting.FileSystemObject")
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName)

oLink.TargetPath = scriptPath & "\start_inspection.bat"
oLink.WorkingDirectory = scriptPath
oLink.Description = "Vehicle Light Inspection System"
oLink.IconLocation = "shell32.dll,13"  ' Folder icon
oLink.Save

WScript.Echo "Shortcut created on Desktop: Vehicle Inspection"
WScript.Echo "You can now double-click it to start the inspection system."

