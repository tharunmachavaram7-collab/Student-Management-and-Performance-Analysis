@echo off
cd /d "%~dp0"
echo ========================================================
echo  Starting EduMetrics - Student Performance System
echo ========================================================
echo Opening browser at http://localhost:5000 ...
start http://localhost:5000
python app.py
pause

