@echo off
chcp 65001 >nul
title DeepSeek Token Monitor

python "%~dp0main.py"
pause
