@echo off
REM Build RahulVideoDownloader.exe from app.py using PyInstaller
pip install pyinstaller
pyinstaller --onefile --name RahulVideoDownloader app.py
echo Executable created at dist\RahulVideoDownloader.exe
