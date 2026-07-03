#!/bin/bash

echo "======================================================================"
echo "🚀 AdaptEngineV1: AI_Codex Integration Setup (Self-Healing V2)"
echo "======================================================================"

# 1. ENVIRONMENT CHECK
echo "[1/6] Checking Prerequisites..."
command -v node >/dev/null 2>&1 || { echo "❌ Node.js not found"; exit 1; }
command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1 || { echo "❌ Python not found"; exit 1; }
echo "✅ Environment Prerequisites OK."

# 2. PROJECT SCAFFOLDING
echo "[2/6] Creating Project Scaffolding..."
FOLDERS=("backend/app/api" "backend/app/core" "backend/app/skills/knowledge_acquisition" "backend/tests" "frontend/src/components" "frontend/src/hooks" "frontend/src/pages" "frontend/src/styles")
for folder in "${FOLDERS[@]}"; do mkdir -p "$folder"; done

# 3. FRONTEND INITIALIZATION
echo "[3/6] Initializing Frontend..."
if [ ! -f "frontend/package.json" ]; then
    npm create vite@latest frontend -- --template react
fi
cd frontend
npm install
npm install -D tailwindcss postcss autoprefixer
echo "✅ Dependencies Installed."

# --- CRITICAL FIX: POSTCSS GLUE ---
if [ ! -f "postcss.config.js" ]; then
    echo "Creating postcss.config.js..."
    cat <<EOF > postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF
fi

# --- CRITICAL FIX: TAILWIND CONFIG ---
if [ ! -f "tailwind.config.js" ]; then
    echo "Creating Obsidian Silver Tailwind config..."
    cat <<EOF > tailwind.config.js
module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        obsidian: { 900: '#0B0E14', 800: '#151921', 700: '#1C222D' },
        silver: { 400: '#9CA3AF', 300: '#E5E7EB', 100: '#F9FAFB' },
      },
    },
  },
  plugins: [],
}
EOF
fi
cd ..

# 4. BACKEND INITIALIZATION
echo "[4/6] Initializing Backend..."
if [ ! -f "backend/requirements.txt" ]; then
    cat <<EOF > backend/requirements.txt
fastapi
uvicorn[standard]
pydantic
sqlalchemy[asyncio]
asyncpg
pgvector
langchain
langgraph
EOF
    python3 -m venv backend/venv || python -m venv backend/venv
    source backend/venv/Scripts/activate || source backend/venv/bin/activate
    pip install --upgrade pip
    pip install -r backend/requirements.txt
fi

# 5. CONFIGURATION FILES
echo "[5/6] Finalizing Configs..."
if [ -f "frontend/src/index.css" ]; then
    echo "@tailwind base;" > frontend/src/index.css
    echo "@tailwind components;" >> frontend/src/index.css
    echo "@tailwind utilities;" >> frontend/src/index.css
fi

# 6. VERIFICATION
echo "[6/6] Verifying Installation..."
if [ ! -d "frontend/node_modules/tailwindcss" ]; then
    echo "❌ Tailwind installation failed. Attempting emergency repair..."
    cd frontend && npm install -D tailwindcss postcss autoprefixer && cd ..
fi

echo "======================================================================"
echo "✅ SELF-HEALING SETUP COMPLETE!"
echo "🚀 Run: cd frontend && npm run dev"
echo "======================================================================"
