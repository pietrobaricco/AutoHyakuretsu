import re

import cv2
import tesserocr

from libs.capture import capture_screen
from libs.delay import NonBlockingDelay
from libs.macro import Macro


class aplan_utils:
    macro: Macro = None

    def __init__(self, macro):
        self.macro = macro

    def get_table_rows(self, screen_img, fx, fy, fx1, fy1, row_height=16):
        ret = []
        columns = []
        row_width = screen_img.shape[1]

        cropped = screen_img[fy:fy1, fx:fx1]

        filter_icon_pos = self.macro.search_template("funnel-icon", cropped)

        if (filter_icon_pos):
            print("found funnel icon at", filter_icon_pos)

            start_x = fx + filter_icon_pos['x'] + 15
            start_y = fy + filter_icon_pos['y'] - 3

            headers_height_multiplier = 1.2
            headers_overscan_px = 5
            headers_x = start_x

            headers_y = start_y - row_height - int(row_height * headers_height_multiplier)

            t1 = self.macro.search_template("table-marker-1", cropped)
            if t1:
                headers_y = start_y - int(row_height * headers_height_multiplier)

            # with a little overscan:
            headers_img = screen_img[headers_y - headers_overscan_px:headers_y + int(
                row_height * headers_height_multiplier) + headers_overscan_px,
                          headers_x - headers_overscan_px:start_x + row_width + headers_overscan_px]

            matches = self.macro.search_templates(headers_img, ["headers-separator", "headers-separator-2"])
            separators = matches.get("headers-separator", [])
            # include also the second separator
            separators.extend(matches.get("headers-separator-2", []))
            #remove separators with y > offset (found somewhere else)
            separators = [s for s in separators if s['y'] < headers_overscan_px]

            if (len(separators) == 0):
                # hack, try a little lower
                headers_y = start_y - int(row_height * headers_height_multiplier)
                # with a little overscan:
                headers_img = screen_img[headers_y - headers_overscan_px:headers_y + int(
                    row_height * headers_height_multiplier) + headers_overscan_px,
                              headers_x - headers_overscan_px:start_x + row_width + headers_overscan_px]

                matches = self.macro.search_templates(headers_img, ["headers-separator", "headers-separator-2"])
                separators = matches.get("headers-separator", [])
                separators.extend(matches.get("headers-separator-2", []))
                separators = [s for s in separators if s['y'] < headers_overscan_px]

            # sort separators by x
            separators = sorted(separators, key=lambda k: k['x'])

            print("Found", len(separators), "separators")
            offsets = []

            # offsets are absolute to the screen_img
            for s in separators:
                offsets.append(s["center_x"] + (headers_x - headers_overscan_px))

            print("Offsets:", offsets)

            # OCR the headers and create columns
            for i in range(len(offsets) - 1):
                x = offsets[i]
                x1 = offsets[i + 1]
                header_img = screen_img[headers_y:headers_y + int(row_height * headers_height_multiplier), x:x1]
                if(header_img.shape[0] == 0 or header_img.shape[1] == 0):
                    continue
                # threshold and upscale header_img so that gray text becomes white, and sort controls are removed

                header_img_gray = cv2.cvtColor(header_img, cv2.COLOR_BGR2GRAY)
                header_img_gray = self.macro.app.image_manipulator.upscale_gray_4x(header_img_gray)
                _, header_img_gray_th = cv2.threshold(header_img_gray, 120, 255, cv2.THRESH_BINARY)
                header_img_clean = cv2.cvtColor(header_img_gray_th, cv2.COLOR_GRAY2BGR)

                text, confidence = self.macro.app.ocr_utils.ocr(header_img_clean, 0, 0, header_img_clean.shape[1],
                                                                header_img_clean.shape[0], psm=tesserocr.PSM.SINGLE_LINE, threshold=0)
                # trim the text removing any character not in a-z, A-Z, 0-9, or space, using regex
                text = re.sub(r'[^a-zA-Z0-9 ]+', '', text)

                # trim spaces from the beginning and end of the text
                text = text.strip()
                columns.append({"text": text, "offset": x, "confidence": confidence})

            print("Found", len(columns), "columns")
            # print columns as json
            print("Columns:", columns)

            # find
            row = 1  # start from row 1, as row 0 contains the filters
            while True:

                box_x = start_x
                box_y = start_y + row_height * row
                box_x1 = start_x + row_width
                box_y1 = start_y + row_height * (row + 1)

                row_img = screen_img[box_y:box_y1, box_x:box_x1]
                # cycle columns, ocr each cell
                record = {}
                good_finds = 0
                for i in range(len(columns) - 1):
                    col = columns[i]
                    cell_x = col["offset"] - box_x
                    cell_x1 = columns[i + 1]["offset"] - box_x
                    cell_img = row_img[0:row_height-1, cell_x+1:cell_x1-1]
                    if cell_img.shape[0] == 0 or cell_img.shape[1] == 0:
                        continue

                    cell_text, cell_confidence = self.macro.app.ocr_utils.ocr(cell_img, 0, 0, cell_img.shape[1],
                                                                              cell_img.shape[0], psm=tesserocr.PSM.SINGLE_LINE, threshold=0)
                    cell_text = re.sub(r'[^a-zA-Z0-9-%/\.,]+', '', cell_text)

                    if (cell_confidence > 70):
                        good_finds += 1
                    record[col["text"]] = cell_text

                if (good_finds < 3):
                    break

                ret.append(record)
                row += 1

            print("Found", row - 1, "rows")

            return ret, columns, {"x": start_x, "y": start_y}

    def filter_table_by(self, value, screen_img, header_template, table_x, table_y, x_offset=0, parse=True, clear_before=True, clear_if_no_result=True):

        row_width = screen_img.shape[1]

        cropped = screen_img[table_y:table_y + 100, table_x:table_x + row_width]

        search_box = self.macro.search_template(header_template, cropped)
        if search_box:
            print("Filtering the list")
            self.macro.app.click(table_x + search_box['center_x'] + x_offset, table_y + search_box['center_y'] + 20)

            if clear_before:
                self.macro.app.peon.ctrl_a()
                NonBlockingDelay.wait(200)
                self.macro.app.peon.backspace()
                NonBlockingDelay.wait(200)

            self.macro.app.peon.write_text(value, interval=0.02, wait_ms=200)
            self.macro.app.peon.enter()

            if parse:
                screenshot_cv = capture_screen(delay_ms=3000)

                rows, cols, funnel_pos = self.get_table_rows(screenshot_cv, table_x, table_y, table_x + 100, table_y + 200)

                if not rows and clear_if_no_result:
                    print("No results found, clearing the search box")
                    self.macro.app.click(table_x + search_box['center_x'], table_y + search_box['center_y'] + 20)

                    self.macro.app.peon.ctrl_a()
                    self.macro.app.peon.backspace()

                return rows, cols, funnel_pos
            else:
                NonBlockingDelay.wait(500)

        return None, None, None
