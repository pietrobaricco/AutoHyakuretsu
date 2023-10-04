@echo off
echo Installing Python 3.11.5...
:: Download the Python 3.11.5 installer
:: curl -o python-installer.exe https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe
:: Install Python 3.11.5 with required options
:: python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

pip install numpy keyboard pyautogui matplotlib tesserocr scipy opencv-python pillow PyQt5