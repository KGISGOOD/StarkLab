@echo off
call C:\ProgramData\Anaconda3\Scripts\activate myenv

set "PATH=C:\myenv;%PATH%"
set "PATH=C:\myenv\Scripts;%PATH%"
python --version

cd /d %~dp0
python project3_test_auto_worldnews.py
pause