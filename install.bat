@echo off

# install anaconda, then
conda create -n auto_hyakuretsu python=3.7
conda activate auto_hyakuretsu
conda install -c conda-forge pyinstaller
conda install -c simonflueckiger tesserocr

pip install numpy keyboard pyautogui matplotlib tesserocr scipy opencv-python opencv-contrib-python pillow PyQt5 texttable pywinauto autogen pyautogen
pip install --pre openai