@echo off
setlocal enabledelayedexpansion

echo [Spirit Bird] Initializing AdaptEngineV1 Development Environment...

:: 1. Handle Environment Variables (.env)
if not exist .env (
    echo [INFO] .env file not found. Creating it from .env.example...
    copy .env.example .env
    echo [ACTION] Please edit the .env file now if you need to change default passwords.
    echo Press any key to continue after saving .env...
    pause >nul
)

:: 2. Docker Engine Status Check
echo [Spirit Bird] Checking Docker Engine status...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Engine is not running. 
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

:: 3. Docker Compose Installation Check
docker-compose version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] docker-compose not found. Please install Docker Compose.
    pause
    exit /b 1
)

:: 4. Orchestration
echo [Spirit Bird] Spinning up containers...
docker-compose up -d

if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Docker containers.
    pause
    exit /b 1
)

echo [Spirit Bird] Infrastructure is booting. Waiting for PostgreSQL to be ready...
:: Dynamic validation: wait for pg_isready
set MAX_RETRIES=30
set RETRY_COUNT=0

:wait_loop
docker-compose exec -T db pg_isready >nul 2>&1
if %errorlevel% equ 0 (
    echo [Spirit Bird] PostgreSQL is ready!
    goto db_ready
)
set /a RETRY_COUNT+=1
if %RETRY_COUNT% geq %MAX_RETRIES% (
    echo [ERROR] PostgreSQL failed to start in time. Check docker-compose logs.
    pause
    exit /b 1
)
echo Waiting for PostgreSQL... ^(%RETRY_COUNT%/%MAX_RETRIES%^)
timeout /t 2 /nobreak >nul
goto wait_loop

:db_ready

:: 5. Python Environment & Database Initialization
echo [Spirit Bird] Setting up Python Environment...
if not exist backend\venv\Scripts\activate (
    echo [Spirit Bird] Creating virtual environment...
    python -m venv backend\venv
)
call backend\venv\Scripts\activate
echo [Spirit Bird] Installing/Updating dependencies...
pip install -r backend\requirements.txt >nul

echo [Spirit Bird] Running database schema initialization...
:: We use python -m to ensure it runs in the context of the current directory
python db_init.py

if %errorlevel% neq 0 (
    echo [ERROR] Database initialization failed. Check if your .env settings match docker-compose.
    pause
    exit /b 1
)

echo [Spirit Bird] Database initialized successfully!

:: 6. Starting Services
echo [Spirit Bird] Starting Backend Service...
start "AdaptEngine Backend" cmd /k "call backend\venv\Scripts\activate && uvicorn main:app --reload --port 8000"

echo [Spirit Bird] Starting Frontend Service...
start "AdaptEngine Frontend" cmd /k "cd frontend && npm run dev"

echo [Spirit Bird] Environment is FULLY UP and Initialized.
echo =========================================================
echo Backend API URL: http://localhost:8000
echo Frontend UI URL: http://localhost:5173
echo =========================================================
echo [Spirit Bird] Use 'docker-compose logs -f' to monitor the database.
pause
