@echo off
echo Running Duckling server
cd .\duckling\
start .\run.bat

echo Running flask server
cd ..
.\venv\Scripts\python .\run.py
pause