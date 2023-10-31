import time

import cv2
import pyautogui

from libs.capture import capture_screen
from libs.delay import NonBlockingDelay
from libs.macro import Macro

class ask_something(Macro):
    def get_required_parameters(self):
        return ["prompt","new_chat"]

    def run(self, screenshot_cv, parameters={}):

        prompt = parameters['prompt'] if 'prompt' in parameters else "Tell me the meaning of life"

        m = self.search_and_click("send-a-message", screenshot_cv, 20)
        if m:
            NonBlockingDelay.wait(200)
            self.app.peon.write_text(prompt + "\n", interval=0.02, wait_ms=0)

            while True:
                NonBlockingDelay.wait(2000)
                screen = capture_screen()

                e = self.search_template("error", screen)
                if e:
                    print("Error")
                    # move to e and send f5
                    pyautogui.moveTo(e['x'], e['y'])
                    pyautogui.press('f5')
                    return

                m = self.search_template("stop-generating-button", screen)
                if m:
                    print("Waiting for response...")
                else:

                    text, c = self.extract_answer(screen)
                    print("Answer:", text, c)

                    break

    def extract_answer(self, cv2_image):
        green_logo_xy = self.search_template("chatgpt-icon-green", cv2_image)
        response_end_xy = self.search_template("regenerate-button", cv2_image)

        if green_logo_xy and response_end_xy:
            box_x = green_logo_xy['x'] + 80
            box_y = green_logo_xy['y']
            box_x1 = response_end_xy['x'] + 180
            box_y1 = response_end_xy['y'] - 150

            answer_cv2 = capture_screen(bbox=(box_x, box_y, box_x1, box_y1))

            # show in a resizable window
            #cv2.namedWindow("answer", cv2.WINDOW_NORMAL)
            #cv2.imshow("answer", answer_cv2)

            text, confidence = self.app.ocr_utils.ocr(answer_cv2, 0, 0, answer_cv2.shape[1], answer_cv2.shape[0])

            return text, confidence
        else:
            print("Couldn't find the green logo or the response end")
            return None, None









