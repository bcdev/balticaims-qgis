@echo off
set "SCRIPT_PATH=%~dp0environment.ps1"
set "ENV_PATH=%~dp0env"
set "BASE_DIR=%~dp0"
set "ENV_NAME=env"

echo Installing Python dependencies... It may take several minutes, until further output is generated.
echo Python dependencies are installed to %ENV_PATH%
echo.

REM powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_PATH%"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "& { & '%SCRIPT_PATH%' '-o' '%BASE_DIR%' '-e' '%ENV_NAME%'}"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Installation completed successfully!
) else (
    echo.
    echo Installation failed!
)

pause