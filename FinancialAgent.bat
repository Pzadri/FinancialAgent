@echo off
title FinancialAgent
color 0A
cls

set "PROJECT_DIR=c:\Codigos\FinancialAgent"
set "BACKEND_DIR=%PROJECT_DIR%\backend"
set "FRONTEND_DIR=%PROJECT_DIR%\frontend"

echo.
echo  ================================================
echo   FinancialAgent - Iniciando sistema...
echo  ================================================
echo.

:: ── Limpiar puertos anteriores ─────────────────────────────────────────────
echo  [1/4] Limpiando sesiones anteriores...
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":8000 " ^| findstr "LISTENING"') do taskkill /PID %%p /F >nul 2>&1
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":5173 " ^| findstr "LISTENING"') do taskkill /PID %%p /F >nul 2>&1
timeout /t 1 /nobreak >nul
echo  [1/4] OK - Puertos libres
echo.

:: ── Iniciar backend ────────────────────────────────────────────────────────
echo  [2/4] Iniciando Backend (FastAPI)...
START "" /B cmd /c "cd /d "%BACKEND_DIR%" && python run.py >> "%BACKEND_DIR%\backend.log" 2>&1"

set /a TRIES=0
set "BAR="
:WAIT_BACKEND
timeout /t 1 /nobreak >nul
set /a TRIES+=1
set "BAR=%BAR%#"
curl -s --max-time 1 http://localhost:8000/api/health >nul 2>&1
if %ERRORLEVEL%==0 goto BACKEND_OK
if %TRIES% GEQ 30 (
    echo  [ERROR] Backend no respondio en 30 segundos.
    echo  Revisa: %BACKEND_DIR%\backend.log
    pause
    exit /b 1
)
<nul set /p "=  Esperando backend... [%BAR%]"
echo.
goto WAIT_BACKEND

:BACKEND_OK
echo  [2/4] OK - Backend corriendo en http://localhost:8000
echo.

:: ── Iniciar frontend ───────────────────────────────────────────────────────
echo  [3/4] Iniciando Frontend (Vite)...
START "" /B cmd /c "cd /d "%FRONTEND_DIR%" && npm run dev >> "%FRONTEND_DIR%\frontend.log" 2>&1"

set /a TRIES=0
set "BAR="
:WAIT_FRONTEND
timeout /t 1 /nobreak >nul
set /a TRIES+=1
set "BAR=%BAR%#"
curl -s --max-time 1 http://localhost:5173 >nul 2>&1
if %ERRORLEVEL%==0 goto FRONTEND_OK
if %TRIES% GEQ 20 (
    echo  [ERROR] Frontend no respondio en 20 segundos.
    echo  Revisa: %FRONTEND_DIR%\frontend.log
    pause
    exit /b 1
)
<nul set /p "=  Esperando frontend... [%BAR%]"
echo.
goto WAIT_FRONTEND

:FRONTEND_OK
echo  [3/4] OK - Frontend corriendo en http://localhost:5173
echo.

:: ── Abrir navegador ────────────────────────────────────────────────────────
echo  [4/4] Abriendo Opera...
start "" "C:\Users\Adria\AppData\Local\Programs\Opera\opera.exe" --new-window "http://localhost:5173"
echo  [4/4] OK - Navegador abierto
echo.

:: ── Sistema listo ──────────────────────────────────────────────────────────
echo  ================================================
echo   Sistema corriendo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo.
echo   Cierra esta ventana para apagar todo.
echo  ================================================
echo.

:: Mantener el CMD abierto
pause >nul
