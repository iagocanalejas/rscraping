import locale
import logging
from abc import ABC, abstractmethod
from datetime import date
from typing import Tuple, Optional, List

import cv2
import numpy as np
from matplotlib import pyplot as plt
from pandas import DataFrame

from src.utils.models import RaceItem
from src.utils.normalization.clubs import normalize_club_name
from src.utils.normalization.trophies import normalize_trophy_name

logger = logging.getLogger(__name__)


class ImageOCR(ABC):
    DATASOURCE: str
    _registry = {}

    img: str  # grayscale loaded image
    img_bin: str  # binary representation of the image
    img_vh: str  # vertical and horizontal lines found in the image
    bitnot: str  # binary images with remarked vertical and horizontal lines

    def __init_subclass__(cls, **kwargs):
        source = kwargs.pop('source')
        super().__init_subclass__(**kwargs)
        cls._registry[source] = cls

    def __new__(cls, source: str, allow_plot: bool = False, **kwargs) -> 'ImageOCR':  # pragma: no cover
        subclass = cls._registry[source]
        final_obj = object.__new__(subclass)
        final_obj.allow_plot = allow_plot

        return final_obj

    def plot(self, img: str, cmap='gray'):
        if self.allow_plot:
            plt.imshow(img, cmap=cmap)
            plt.show()

    @staticmethod
    def set_language(language: str | Tuple[str, str] = 'es_ES.utf8'):
        locale.setlocale(locale.LC_TIME, language)

    ####################################################
    #                 ABSTRACT METHODS                 #
    ####################################################
    @abstractmethod
    def digest(self, path: str) -> List[RaceItem]:
        raise NotImplementedError

    @abstractmethod
    def prepare_image(self, path: str, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def prepare_dataframe(self, **kwargs) -> DataFrame:
        raise NotImplementedError

    @abstractmethod
    def parse_header(self, **kwargs) -> Tuple[str, date, Optional[str]]:
        raise NotImplementedError

    @abstractmethod
    def clean_dataframe(self, df: DataFrame) -> DataFrame:
        raise NotImplementedError

    ####################################################
    #                     OVERRIDES                    #
    ####################################################

    def normalized_name(self, name: str, **kwargs) -> str:
        return normalize_trophy_name(name, False)

    def normalized_club_name(self, name: str, **kwargs) -> str:
        return normalize_club_name(name)

    ####################################################
    #                 IMAGE PROCESSING                 #
    ####################################################

    @staticmethod
    def get_vh_lines(img: np.array) -> np.array:
        """
        :param img: a binary image representation
        :return: image with vertical and horizontal lines
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
        img_vh = cv2.erode(~img_vh, kernel, iterations=2)
        _, img_vh = cv2.threshold(img_vh, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        return img_vh

    @staticmethod
    def get_image_header(img: np.array, size: int = 25) -> np.array:
        """
        :param img: an image representation
        :param size: wanted % (1-100)
        :return: cropped image
        """
        width, height = img.shape
        return img[:int(height * (size / 100)), :]

    @staticmethod
    def get_boxes(img_vh: np.array) -> Tuple[np.array, Tuple[int, int]]:
        # Detect contours for following box detection
        contours, hierarchy = cv2.findContours(img_vh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

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
            for k in range(count_col):
                lis.append([])
            for j in range(len(row[i])):
                diff = abs(center - (row[i][j][0] + row[i][j][2] / 4))
                idx = list(diff).index(min(diff))
                lis[idx].append(row[i][j])
            final_boxes.append(lis)

        return final_boxes, (count_col, len(row))
