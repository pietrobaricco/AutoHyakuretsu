@echo off
echo Installing Python 3.11.5...
:: Download the Python 3.11.5 installer
:: curl -o python-installer.exe https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe
:: Install Python 3.11.5 with required options
:: python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

echo Installing PyQt5...
pip install PyQt5

echo Installing Pillow (PIL)...
pip install pillow

echo Installing OpenCV...
pip install opencv-python

echo Installing NumPy...
pip install numpy

echo Installing keyboard...
pip install keyboard

echo Installing pyautogui...
pip install pyautogui

:: Optional: Clone or copy your program and dependencies here

echo Installation complete.
pause
