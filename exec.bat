@echo off
start mongod
python call.py %*
pause