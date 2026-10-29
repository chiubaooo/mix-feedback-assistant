@echo off
chcp 65001 >nul
title AI 混音修改意見智能提煉工廠
echo ========================================================
echo   🎛️  林从胤音樂工作室 - AI 混音修改意見智能提煉工廠
echo ========================================================
echo 正在啟動網頁服務，請稍候...
echo.

cd /d "%~dp0"
python -m streamlit run app.py --server.port=8501 --server.headless=false

pause
