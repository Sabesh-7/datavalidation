@echo off
echo =========================================================
echo Starting MoSPI Data Validation Platform - Python Backend
echo =========================================================

IF NOT EXIST .venv (
    echo Creating Python Virtual Environment...
    python -m venv .venv
)

echo Activating Virtual Environment...
call .venv\Scripts\activate

echo Installing Requirements...
pip install -r requirements.txt

echo Launching FastAPI Server on http://localhost:8005 ...
uvicorn main:app --host 0.0.0.0 --port 8005 --reload
