import re

import cv2

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
            print("found funnel")
            start_x = fx + filter_icon_pos['x'] + 15
            start_y = fy + filter_icon_pos['y'] - 3

            headers_height_multiplier = 1.2
            headers_overscan_px = 2
            headers_x = start_x

            headers_y = start_y - row_height - int(row_height * headers_height_multiplier)
            # with a little overscan:
            headers_img = screen_img[headers_y - headers_overscan_px:headers_y + int(
                row_height * headers_height_multiplier) + headers_overscan_px,
                          headers_x - headers_overscan_px:start_x + row_width + headers_overscan_px]

            matches = self.macro.search_templates(headers_img, ["headers-separator"])
            separators = matches.get("headers-separator", [])

            if(len(separators) == 0):
                # hack, try a little lower
                headers_y = start_y - int(row_height * headers_height_multiplier)
                # with a little overscan:
                headers_img = screen_img[headers_y - headers_overscan_px:headers_y + int(
                    row_height * headers_height_multiplier) + headers_overscan_px,
                              headers_x - headers_overscan_px:start_x + row_width + headers_overscan_px]

                matches = self.macro.search_templates(headers_img, ["headers-separator"])
                separators = matches.get("headers-separator", [])

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
                # threshold and upscale header_img so that gray text becomes white, and sort controls are removed
                header_img_gray = cv2.cvtColor(header_img, cv2.COLOR_BGR2GRAY)
                header_img_gray = self.macro.app.image_manipulator.upscale_gray_4x(header_img_gray)
                _, header_img_gray_th = cv2.threshold(header_img_gray, 120, 255, cv2.THRESH_BINARY)
                header_img_clean = cv2.cvtColor(header_img_gray_th, cv2.COLOR_GRAY2BGR)

                text, confidence = self.macro.app.ocr_utils.ocr(header_img_clean, 0, 0, header_img_clean.shape[1],
                                                                header_img_clean.shape[0], 7, threshold=0)
                # trim the text removing any character not in a-z, A-Z, 0-9, or space, using regex
                text = re.sub(r'[^a-zA-Z0-9 ]+', '', text)

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
                    cell_img = row_img[0:row_height, cell_x:cell_x1]
                    cell_text, cell_confidence = self.macro.app.ocr_utils.ocr(cell_img, 0, 0, cell_img.shape[1],
                                                                              cell_img.shape[0], 7, threshold=0)
                    cell_text = re.sub(r'[^a-zA-Z0-9 ]+', '', cell_text)
                    if (cell_confidence > 70):
                        good_finds += 1
                    record[col["text"]] = cell_text

                if (good_finds < 3):
                    break

                ret.append(record)
                row += 1

            print("Found", row - 1, "rows")

            return ret, columns
