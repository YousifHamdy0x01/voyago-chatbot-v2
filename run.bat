@echo off
title Voyago Chatbot Server
echo ===================================================
echo   Starting Voyago Chatbot FastAPI Server...
echo ===================================================
echo.
.\venv\Scripts\python -m app.main
if %errorlevel% neq 0 (
    echo.
    echo Server stopped with error code %errorlevel%.
    pause
)
