REM @echo off
set "ENV_PATH=%~dp0env"
echo Running QGIS with Conda environment %ENV_PATH%
echo. 

"%ENV_PATH%\Library\bin\micromamba.exe" run -p "%ENV_PATH%" "%ENV_PATH%\Library\bin\qgis.exe"

pause