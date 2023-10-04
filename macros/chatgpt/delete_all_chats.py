import time

import cv2

from libs.capture import capture_screen
from libs.delay import NonBlockingDelay
from libs.macro import Macro

class delete_all_chats(Macro):

    def run(self, screenshot_cv, parameters={}):

        m = self.search_and_click("old-chat-icon", screenshot_cv, 20)
        if m:
            NonBlockingDelay.wait(200)

            box_x = m['x']
            box_y = m['y'] - 20
            screenshot_cv2 = capture_screen(bbox=(box_x, box_y, box_x+500, box_y+100))

            m2 = self.search_template("chat-delete", screenshot_cv2)
            if m2:
                print("Found the delete button at", m2['x'], m2['y'])
                self.app.click(box_x + m2['center_x'], box_y + m2['center_y'])

                NonBlockingDelay.wait(300)

                screenshot_cv2 = capture_screen()

                self.search_and_click("delete-button-red", screenshot_cv2)

            else:
                print("Couldn't find the delete button")
                return



