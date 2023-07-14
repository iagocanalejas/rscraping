import logging
import os
import re
import cv2
import inquirer
import numpy as np

from ._image import ImageOCR
from datetime import date, datetime
from typing import List, Optional, Tuple, Generator, Any
from pandas import DataFrame
from pytesseract import pytesseract
from pyutils.strings import whitespaces_clean, remove_symbols
from data.models import Participant, Race, OCR
from data.normalization.times import normalize_lap_time
from data.constants import (
    RACE_TRAINERA,
    GENDER_MALE,
    GENDER_FEMALE,
    GENDER_MIX,
    PARTICIPANT_CATEGORY_VETERAN,
    PARTICIPANT_CATEGORY_ABSOLUT,
)

logger = logging.getLogger(__name__)


class ImageOCRInforemo(ImageOCR, source=OCR.INFOREMO):
    DATASOURCE = OCR.INFOREMO

    _GENDERS = {
        GENDER_MALE: ["MASCULINO", "ABSOLUTO", "VETERANO"],
        GENDER_FEMALE: ["FEMENINO", "VETERANA"],
        GENDER_MIX: ["MIXTO"],
    }

    def digest(self, path: str) -> Generator[Race, Any, Any]:
        logger.info(f"processing {path}")

        self.prepare_image(path)

        name, t_date, town = self.parse_header()
        name = inquirer.text(message="Race name:", default=name)
        t_date = inquirer.text(message="Race date (YYYY-MM-DD):", default=t_date)

        if not name or not t_date:
            logger.error(f"unable to process: {path}")
            return []

        df = self.prepare_dataframe()

        if self.allow_plot:
            logger.info(df)

        trophy_name = self.normalized_name(name)
        race_lanes = self.get_race_lanes(df)
        race_laps = self.get_race_laps(df)
        race = Race(
            name=name,
            trophy_name=trophy_name,
            date=t_date,
            edition=self.get_edition(),
            day=self.get_day(),
            type="",  # TODO: type in image
            modality=self.get_modality(),
            league=self.get_league(),
            town=town,
            organizer=self.get_organizer(),
            race_id=os.path.basename(path),
            url=None,
            datasource=self.DATASOURCE.value,
            race_laps=race_laps,
            race_lanes=race_lanes,
            participants=[],
        )
        for _, row in df.iterrows():
            club_name = self.get_club_name(row)
            race.participants.append(
                Participant(
                    gender=self.get_gender(row),
                    category=self.get_category(row),
                    club_name=club_name,
                    lane=self.get_lane(row),
                    series=self.get_series(row),
                    laps=self.get_laps(row),
                    distance=self.get_distance(),
                    participant=self.normalized_club_name(club_name),
                    race=race,
                )
            )
        yield race

    ####################################################
    #                 IMAGE PROCESSING                 #
    ####################################################

    def prepare_image(self, path: str):
        img = cv2.imread(path, 0)
        self.plot(img)

        _, img_bin = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)  # thresholding the image to a binary image
        img_bin = 255 - img_bin  # inverting the image
        self.plot(img_bin)

        img_vh = self.get_vh_lines(img_bin)  # find vertical and horizontal lines
        self.plot(img_vh)

        # Eroding and thesholding the image
        bitxor = cv2.bitwise_xor(img, img_vh)
        bitnot = cv2.bitwise_not(bitxor)
        self.plot(bitnot)  # find vertical and horizontal lines

        # can't be done directly
        self.img, self.img_vh, self.img_bin, self.bitnot = img, img_vh, img_bin, bitnot

    def parse_header(self) -> Tuple[str, Optional[date], Optional[str]]:
        # TODO: improve name detection
        header = self.get_image_header(self.img_bin)
        self.plot(header)

        # https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html#page-segmentation-method
        out = pytesseract.image_to_string(header, config="--psm 3")
        return self.get_name(out), self.get_date(out), self.get_town(out)

    ####################################################
    #              DATAFRAME PROCESSING                #
    ####################################################

    def prepare_dataframe(self) -> DataFrame:
        final_boxes, (count_col, count_row) = self.get_boxes(self.img_vh)

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
        return self.clean_dataframe(DataFrame(arr.reshape(count_row, count_col)))

    def clean_dataframe(self, df: DataFrame) -> DataFrame:
        df = df.applymap(whitespaces_clean)
        remove = []
        # remove rows without any content
        for index, row in df.iterrows():
            col_with_content = 0
            for _, col in row.items():
                content = whitespaces_clean(col)
                if content and len(content) > 5:
                    col_with_content += 1
            if col_with_content < 2:  # check we at least have (maybe) name and final time
                remove.append(index)
        df.drop(remove, inplace=True)

        return df

    ####################################################
    #                      GETTERS                     #
    ####################################################

    def get_name(self, image: str) -> str:
        for line in image.split("\n"):
            if any(w in line for w in ["@", "inforemo"]):
                continue

            match = re.match(r"^[a-zA-ZñÑ ]+$", whitespaces_clean(remove_symbols(line)))
            if match and len(match.group(0)) > 5:
                return match.group(0)
        return ""

    def get_distance(self, **_) -> int:
        return 5556

    def get_date(self, image: str) -> Optional[date]:
        for line in image.split("\n"):
            match = re.findall(r"\d{1,2} [a-zA-ZñÑ]+ 20\d{2}", whitespaces_clean(line))
            if not len(match):
                continue

            try:
                return datetime.strptime(match[0], "%d %B %Y")
            except ValueError:
                continue

    def get_town(self, image: str) -> Optional[str]:
        name = self.get_name(image)
        for line in image.split("\n"):
            if any(w in line for w in ["@", "inforemo"]):
                continue
            line = whitespaces_clean(remove_symbols(line))
            if line == name:
                continue
            match = re.match(r"^[a-zA-ZñÑ \-0]+$", line)
            if match and len(match.group(0)) > 4:
                return match.group(0)

    def get_gender(self, data) -> str:
        gender = data[2]
        for k, v in self._GENDERS.items():
            if gender in v or any(part in gender for part in v):
                gender = k
                break
        return gender

    def get_modality(self) -> str:
        return RACE_TRAINERA

    def get_category(self, data) -> str:
        modality = data[2]
        if "VETERANO" in modality:
            return PARTICIPANT_CATEGORY_VETERAN
        return PARTICIPANT_CATEGORY_ABSOLUT

    def get_club_name(self, data) -> str:
        return data[1]

    def get_lane(self, data) -> int:
        try:
            # if : means we are in a TIME_TRIAL image so all the boats will be in the same lane
            return 1 if ":" in data[4] else int(data[4])
        except ValueError:
            return 1

    def get_series(self, data) -> int:
        try:
            return int(data[3])
        except ValueError:
            return 1

    @staticmethod
    def clean_lap(maybe_tyme: str) -> str:
        # clean normal OCR errors
        maybe_tyme = maybe_tyme.replace('"a', "4:").replace("T", "").replace("_", "")
        maybe_tyme = maybe_tyme.replace("::", ":")

        return whitespaces_clean(maybe_tyme)

    def get_laps(self, data) -> List[str]:
        idx = 3 if ":" in data[4] else 4
        return [t.isoformat() for t in [normalize_lap_time(self.clean_lap(t)) for t in data.iloc[idx:]] if t]

    def get_race_lanes(self, df: DataFrame) -> int:
        lanes = max(int(row[4]) for _, row in df.iterrows())
        try:
            lanes = int(lanes)
            return lanes if lanes < 7 else 1
        except ValueError:
            return 1

    def get_race_laps(self, df: DataFrame) -> int:
        return len(df.columns) - 4

    def normalized_club_name(self, name: str) -> str:
        new_name = super(ImageOCRInforemo, self).normalized_club_name(name)
        new_name = remove_symbols(new_name, ignore_quotes=True)
        new_name = new_name.replace("'", '"')  # normalize quotes

        return new_name

    ####################################################
    #                 DEFAULT VALUES                   #
    ####################################################

    @staticmethod
    def get_edition() -> int:
        return 1

    def get_league(self) -> Optional[str]:
        return None

    def get_day(self) -> int:
        return 1

    def get_organizer(self) -> Optional[str]:
        return None
