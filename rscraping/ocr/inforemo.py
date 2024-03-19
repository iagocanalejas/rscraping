import locale
import os

import cv2
import numpy as np
import pytesseract
from numpy.typing import NDArray
from pandas import DataFrame

from rscraping.data.models import Datasource
from rscraping.ocr.image import ImageProcessor


class InforemoImageProcessor(ImageProcessor, source=Datasource.INFOREMO):
    DATASOURCE = Datasource.INFOREMO

    def retrieve_header_data(self, path: str, header_size: int = 3, **_) -> DataFrame:
        if not os.path.exists(path) or not os.path.isfile(path):
            raise ValueError(f"invalid {path=}")

        default_locale = locale.getlocale(locale.LC_TIME)
        locale.setlocale(locale.LC_TIME, "es_ES.utf8")

        self._load_header_image(path, header_size=header_size)

        out = pytesseract.image_to_string(self.img, config="--psm 4")
        if len(out) == 0:
            out = pytesseract.image_to_string(self.img, config="--psm 10")

        locale.setlocale(locale.LC_TIME, default_locale)
        return out

    def retrieve_tabular_dataframe(self, path: str, header_size: int = 3, **_) -> DataFrame:
        if not os.path.exists(path) or not os.path.isfile(path):
            raise ValueError(f"invalid {path=}")

        default_locale = locale.getlocale(locale.LC_TIME)
        locale.setlocale(locale.LC_TIME, "es_ES.utf8")

        self._load_tabular_image(path, header_size=header_size)

        final_boxes, (count_col, count_row) = self._get_boxes(self.img_vh)
        # from every single image-based cell/box the strings are extracted via pytesseract and stored in a list
        outer = []
        for i in range(len(final_boxes)):
            for j in range(len(final_boxes[i])):
                inner = ""
                if len(final_boxes[i][j]) == 0:
                    outer.append(" ")
                    continue

                for k in range(len(final_boxes[i][j])):
                    y, x, w, h = (
                        final_boxes[i][j][k][0],
                        final_boxes[i][j][k][1],
                        final_boxes[i][j][k][2],
                        final_boxes[i][j][k][3],
                    )
                    finalimg = self.bitnot[x : x + h, y : y + w]
                    border = cv2.copyMakeBorder(finalimg, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=[255, 255])

                    out = pytesseract.image_to_string(border, config="--psm 4")
                    if len(out) == 0:
                        out = pytesseract.image_to_string(border, config="--psm 10")
                    inner = inner + " " + out
                outer.append(inner)

        # Creating a dataframe of the generated OCR list
        arr = np.array(outer)

        locale.setlocale(locale.LC_TIME, default_locale)
        return self._clean_dataframe(DataFrame(arr.reshape(count_row, count_col)))

    def _load_header_image(self, image_path: str, header_size: int):
        # load and remove parts of an image
        img = cv2.imread(image_path, 0)

        img = img[: img.shape[0] // header_size, :]
        self._plot(img)

        # can't be done directly
        self.img = img

    def _load_tabular_image(self, image_path: str, header_size: int):
        # load and remove the top third of the image
        img = cv2.imread(image_path, 0)
        img = img[img.shape[0] // header_size :, :]
        self._plot(img)

        # thresholding the image to a binary image and invert it
        _, img_bin = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)
        img_bin = 255 - img_bin  # pyright: ignore

        # find vertical and horizontal lines
        img_vh = self._get_vh_lines(img_bin)

        # Eroding and thesholding the image
        bitxor = cv2.bitwise_xor(img, img_vh)
        bitnot = cv2.bitwise_not(bitxor)
        self._plot(bitnot)  # find vertical and horizontal lines

        # can't be done directly
        self.img, self.img_vh, self.img_bin, self.bitnot = img, img_vh, img_bin, bitnot

    def _get_vh_lines(self, img: NDArray) -> NDArray:
        """
        Detect vertical and horizontal lines in an image and return a new image with the lines highlighted.

        This method applies morphological operations to detect both vertical and horizontal lines in the input image.
        It uses a combination of erosion and dilation to identify the lines and generates a new image with the lines
        highlighted.

        Parameters:
            img (NDArray): A NumPy array representing the input image.

        Returns:
            NDArray: A NumPy array representing the image with detected vertical and horizontal lines highlighted.

        Note:
            The input image should be a grayscale image for optimal line detection.
        """

        # countcol(width) of kernel as 100th of total width
        kernel_len = np.array(img).shape[1] // 100

        # Defining kernels to detect all lines of image
        ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len))
        hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

        # Use vertical kernel to detect and save the vertical lines in a jpg
        image_1 = cv2.erode(img, ver_kernel, iterations=3)
        vertical_lines = cv2.dilate(image_1, ver_kernel, iterations=3)

        # Use horizontal kernel to detect and save the horizontal lines in a jpg
        image_2 = cv2.erode(img, hor_kernel, iterations=3)
        horizontal_lines = cv2.dilate(image_2, hor_kernel, iterations=3)

        # Combine horizontal and vertical lines in a new third image, with both having same weight.
        img_vh = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)
        img_vh = cv2.erode(~img_vh, kernel, iterations=2)  # pyright: ignore
        _, img_vh = cv2.threshold(img_vh, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        return img_vh

    def _get_boxes(self, img_vh: NDArray) -> tuple[list, tuple[int, int]]:
        """
        Detect and organize bounding boxes around cells within a tabular image.

        This method takes an image containing highlighted vertical and horizontal lines representing a table,
        and performs contour detection and bounding box calculations to identify and organize bounding boxes around
        individual cells within the table.

        Parameters:
            img_vh (NDArray): A NumPy array representing the image with highlighted vertical and horizontal lines.

        Returns:
            Tuple[List, Tuple[int, int]]: A tuple containing the list of final organized bounding boxes for cells and
                                        a tuple containing the number of columns and rows detected in the table.
        """

        # Detect contours for following box detection
        contours, _ = cv2.findContours(img_vh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Sort all the contours by top to bottom.
        bounding_boxes = [cv2.boundingRect(c) for c in contours]
        contours, bounding_boxes = zip(*sorted(zip(contours, bounding_boxes), key=lambda b: b[1][1], reverse=False))

        boxes = []
        # Get position (x,y), width and height for every contour and show the contour on image
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if w < 1000 and h < 500:
                boxes.append([x, y, w, h])

        height_mean = np.mean([bounding_boxes[i][3] for i in range(len(bounding_boxes))])

        # Creating two lists to define row and column in which cell is located
        row = []
        column = [boxes[0]]

        # Sorting the boxes to their respective row and column
        previous = boxes[0]
        for i in range(1, len(boxes)):
            if boxes[i][1] <= previous[1] + height_mean / 2:
                column.append(boxes[i])
                previous = boxes[i]
                if i == len(boxes) - 1:
                    row.append(column)
            else:
                row.append(column)
                column = []
                previous = boxes[i]
                column.append(boxes[i])

        # calculating maximum number of cells
        count_col = 0
        for i in range(len(row)):
            count_col = len(row[i])
            if count_col > count_col:
                count_col = count_col

        last = len(row) - 1

        # Retrieving the center of each column
        center = np.array([int(row[last][j][0] + row[last][j][2] / 2) for j in range(len(row[last])) if row[0]])
        center.sort()

        final_boxes = []
        for i in range(len(row)):
            lis = []
            for _ in range(count_col):
                lis.append([])
            for j in range(len(row[i])):
                diff = abs(center - (row[i][j][0] + row[i][j][2] / 4))
                idx = list(diff).index(min(diff))
                lis[idx].append(row[i][j])
            final_boxes.append(lis)

        return final_boxes, (count_col, len(row))
