import json
import os
import tkinter

import cv2
from PyQt5.QtCore import pyqtSignal, QTimer, QObject
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QApplication

from libs.overlay_gif import display_animated_gif_at


class Sprite:

    def __init__(self, filePath, sounds_dir):
        self.filePath = filePath
        self.fileDir = os.path.dirname(filePath)
        self.name = os.path.basename(filePath).split(".")[0]
        self.metadata = self.get_metadata()

        self.x_offset = self.metadata["x_offset"] if "x_offset" in self.metadata else 0
        self.y_offset = self.metadata["y_offset"] if "y_offset" in self.metadata else 0
        self.delay = self.metadata["delay"] if "delay" in self.metadata else 0
        self.duration = self.metadata["duration"] if "duration" in self.metadata else 2000
        self.sound_file = self.metadata["sound"] if "sound" in self.metadata else None

        if self.sound_file:
            self.sound = QSound(os.path.join(sounds_dir, self.sound_file))
        else:
            self.sound = None

        self.x = 0
        self.y = 0

    def display_at(self, x, y, msecs=2000, with_sound=True):
        gif_path = self.filePath

        screen = QApplication.primaryScreen()

        root = tkinter.Tk()
        dpi = root.winfo_fpixels('1i')
        qtDpi = screen.logicalDotsPerInch()

        scaling_factor = dpi / qtDpi

        mulX = int(self.x_offset * scaling_factor)
        mulY = int(self.y_offset * scaling_factor)

        self.x = x
        self.y = y

        display_animated_gif_at(gif_path, x - mulX, y - mulY, msecs)
        if self.sound and with_sound:
            self.sound.play()
            QTimer.singleShot(msecs, self.sound.stop)

    def get_metadata(self):
        metadata_file_path = self.fileDir + f"/{self.name}.json"
        if os.path.exists(metadata_file_path):
            with open(metadata_file_path, 'r') as metadata_file:
                return json.load(metadata_file)
        else:
            return []


def load_sprites(folder_path, sounds_dir):
    # animated GIFs
    sprite_files = [file for file in os.listdir(folder_path) if file.lower().endswith('.gif')]
    ret = {}
    for file in sprite_files:
        # Now you can work with each PNG file in the folder
        print(f"Processing {file}")
        ret[file.split(".")[0]] = Sprite(folder_path + "/" + file, sounds_dir)

    # print all the loaded sprites
    for sprite in ret.values():
        print(sprite.name + " loaded:")

    return ret
