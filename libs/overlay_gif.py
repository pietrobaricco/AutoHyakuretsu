import pyautogui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QMovie, QCursor
from PyQt5.QtWidgets import QSplashScreen, QLabel


def display_animated_gif_at(gif_path, x, y, msecs):
    def show_gif():
        main_win = QLabel()

        # Load the animated GIF
        movie = QMovie(gif_path)
        main_win.setMovie(movie)
        movie.start()

        main_win.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        main_win.setAttribute(Qt.WA_TranslucentBackground)
        main_win.setAttribute(Qt.WA_TransparentForMouseEvents)  # Make the window transparent for mouse events

        gif_size = movie.frameRect().size()
        main_win.resize(gif_size)

        mouse_x, mouse_y = pyautogui.position()
        pyautogui.moveTo(x, y)

        # Get the global cursor position
        cursor = QCursor()
        cursor_pos = cursor.pos()

        # Calculate the offset to adjust the window position
        x_offset = cursor_pos.x()
        y_offset = cursor_pos.y()

        main_win.move(x_offset, y_offset)
        pyautogui.moveTo(mouse_x, mouse_y)
        # pyautogui.dragTo(mouse_x, mouse_y)

        main_win.show()

        def close_main_win():
            main_win.close()

        # Close the main window after the specified time
        QTimer.singleShot(msecs, close_main_win)

    # Add a small delay (e.g., 100 milliseconds) before showing the GIF
    QTimer.singleShot(150, show_gif)
