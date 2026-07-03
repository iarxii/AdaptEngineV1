@echo off
SETLOCAL EnableDelayedExpansion
echo ======================================================================
echo 🚀 AdaptEngineV1: AI_Codex Integration Setup (Self-Healing V2)
echo ======================================================================

:: 1. ENVIRONMENT CHECK
echo [1/6] Checking Prerequisites...
where node >nul 2>nul
if %errorlevel% neq 0 (echo ❌ Node.js not found. & pause & exit /b)
where python >nul 2>nul
if %errorlevel% neq 0 (echo ❌ Python not found. & pause & exit /b)
echo ✅ Environment Prerequisites OK.

:: 2. PROJECT SCAFFOLDING
echo [2/6] Creating Project Scaffolding...
set "FOLDERS=backend\app\api backend\app\core backend\app\skills\knowledge_acquisition backend\tests frontend\src\components frontend\src\hooks frontend\src\pages frontend\src\styles"
for %%f in (%FOLDERS%) do (if not exist "%%f" mkdir "%%f")

:: 3. FRONTEND INITIALIZATION (Vite + Tailwind + PostCSS)
echo [3/6] Initializing Frontend...
if not exist "frontend\package.json" (
    mkdir frontend 2>nul
    call npm create vite@latest frontend -- --template react
)
cd frontend
call npm install
call npm install -D tailwindcss postcss autoprefixer
echo ✅ Dependencies Installed.

:: --- CRITICAL FIX: POSTCSS GLUE ---
if not exist "postcss.config.js" (
    echo Creating postcss.config.js...
    (
        echo module.exports = {
        echo   plugins: {
        echo     tailwindcss: {},
        echo     autoprefixer: {},
        echo   },
        echo }
    ) > postcss.config.js
)

:: --- CRITICAL FIX: TAILWIND CONFIG ---
if not exist "tailwind.config.js" (
    echo Creating Obsidian Silver Tailwind config...
    (
        echo module.exports = {
        echo   content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
        echo   theme: {
        echo     extend: {
        echo       colors: {
        echo         obsidian: { 900: '#0B0E14', 800: '#151921', 700: '#1C222D' },
        echo         silver: { 400: '#9CA3AF', 300: '#E5E7EB', 100: '#F9FAFB' },
        echo       },
        echo     },
        echo   },
        echo   plugins: [],
        echo }
    ) > tailwind.config.js
)
cd ..

:: 4. BACKEND INITIALIZATION
echo [4/6] Initializing Backend...
if not exist "backend\requirements.txt" (
    (echo fastapi^
uvicorn[standard]^
pydantic^
sqlalchemy[asyncio]^
asyncpg^
pgvector^
langchain^
langgraph) > backend\requirements.txt
    python -m venv backend\venv
    call backend\venv\Scripts\activate
    python -m pip install --upgrade pip
    pip install -r backend\requirements.txt
)

:: 5. CONFIGURATION FILES
echo [5/6] Finalizing Configs...
:: Ensure frontend/src/index.css has Tailwind directives
if exist "frontend\src\index.css" (
    echo @tailwind base; > frontend\src\index.css
    echo @tailwind components; >> frontend\src\index.css
    echo @tailwind utilities; >> frontend\src\index.css
)

:: 6. VERIFICATION
echo [6/6] Verifying Installation...
if not exist "frontend\node_modules\tailwindcss" (
    echo ❌ Tailwind installation failed. Attempting emergency repair...
    cd frontend && call npm install -D tailwindcss postcss autoprefixer && cd ..
)

echo ======================================================================
echo ✅ SELF-HEALING SETUP COMPLETE!
echo 🚀 Run: cd frontend ^&^& npm run dev
echo ======================================================================
pause
