import sys

import pyautogui
from PyQt5.QtCore import QTimer
import pyperclip
from pywinauto.keyboard import send_keys

from libs.delay import NonBlockingDelay


class Peon:

    def __init__(self):
        self.is_win = sys.platform.startswith('win')

    def write_text(self, text, interval=0.1, wait_ms=0):
        pyperclip.copy(text)
        NonBlockingDelay.wait(200)
        pyautogui.hotkey('ctrl', 'v', interval=0.1)
        #pyautogui.typewrite(text, interval=interval)
        NonBlockingDelay.wait(100)
        NonBlockingDelay.wait(wait_ms)

    def enter(self):
        if self.is_win:
            send_keys('{ENTER}')
        else:
            pyautogui.press('enter')

    def space(self):
        if self.is_win:
            send_keys('{SPACE}')
        else:
            pyautogui.press('space')

    def backspace(self):
        if self.is_win:
            send_keys('{BACKSPACE}')
        else:
            pyautogui.press('backspace')

    def CANC(self):
        if self.is_win:
            send_keys('{DELETE}')
        else:
            pyautogui.press('delete')

    def END(self):
        if self.is_win:
            send_keys('{END}')
        else:
            pyautogui.press('end')

    def down(self):
        if self.is_win:
            send_keys('{DOWN}')
        else:
            pyautogui.press('down')

    def up(self):
        if self.is_win:
            send_keys('{UP}')
        else:
            pyautogui.press('up')

    def left(self):
        if self.is_win:
            send_keys('{LEFT}')
        else:
            pyautogui.press('left')

    def right(self):
        if self.is_win:
            send_keys('{RIGHT}')
        else:
            pyautogui.press('right')

    def ESC(self):
        if self.is_win:
            send_keys('{ESC}')
        else:
            pyautogui.press('esc')

    def alt_n(self):
        if self.is_win:
            send_keys('%n')
        else:
            pyautogui.hotkey('alt', 'n')

    def alt_f2(self):
        if self.is_win:
            send_keys('%{F2}')
        else:
            pyautogui.hotkey('alt', 'f2')

    def shift_alt_f5(self):
        if self.is_win:
            send_keys('+%{F5}')
        else:
            pyautogui.hotkey('shift', 'alt', 'f5')

    def alt_8(self):
        if self.is_win:
            send_keys('%8')
        else:
            pyautogui.hotkey('alt', '8')

    def alt_q(self):
        if self.is_win:
            send_keys('%q')
        else:
            pyautogui.hotkey('alt', 'q')

    def ctrl_a(self):
        if self.is_win:
            send_keys('^a')
        else:
            pyautogui.hotkey('ctrl', 'a')