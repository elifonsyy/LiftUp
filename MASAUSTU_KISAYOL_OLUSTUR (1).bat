@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "SCRIPT=%~dp0test.py"
set "IKON=%~dp0specter.ico"
set "CALISMA=%~dp0"
set "PYTHONW=C:\Users\musda\AppData\Local\Programs\Python\Python312\pythonw.exe"

rem OneDrive Masaustu yolunu al
for /f "tokens=*" %%i in ('powershell -Command "[Environment]::GetFolderPath(\"Desktop\")"') do set "MASAUSTU=%%i"

set "KISAYOL=%MASAUSTU%\SPECTER.lnk"

echo Masaustu yolu: %MASAUSTU%
echo Kisayol olusturuluyor...

powershell -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%KISAYOL%'); $s.TargetPath = '%PYTHONW%'; $s.Arguments = '\"%SCRIPT%\"'; $s.WorkingDirectory = '%CALISMA%'; $s.IconLocation = '%IKON%'; $s.WindowStyle = 1; $s.Description = 'SPECTER Simulasyon'; $s.Save(); Write-Host 'Tamam'"

if exist "%KISAYOL%" (
    echo BASARILI! Masaustunde SPECTER ikonu olusturuldu.
) else (
    echo HATA: Olusturulamadi.
)
pause
