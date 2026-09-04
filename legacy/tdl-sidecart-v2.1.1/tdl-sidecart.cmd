@echo off
setlocal EnableExtensions
set "TSC_SCRIPT=%~dp0tdl-sidecart.ps1"

if not exist "%TSC_SCRIPT%" (
  echo [tdl-sidecart] Missing script: "%TSC_SCRIPT%" 1>&2
  exit /b 3
)

rem Remove only the Windows Internet-zone marker from this downloaded script.
rem This does NOT change LocalMachine, CurrentUser, Process, or Group Policy execution policy.
set "TSC_UNBLOCK_TARGET=%TSC_SCRIPT%"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -NonInteractive -Command "try { Unblock-File -LiteralPath $env:TSC_UNBLOCK_TARGET -ErrorAction Stop; exit 0 } catch { Write-Error $_; exit 1 }"
if errorlevel 1 (
  echo [tdl-sidecart] Could not remove the Windows download marker. 1>&2
  exit /b 1
)

"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -File "%TSC_SCRIPT%" %*
exit /b %ERRORLEVEL%
