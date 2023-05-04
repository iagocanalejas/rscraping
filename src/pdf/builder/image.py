import logging

from fillpdf import fillpdfs

from src.pdf.builder import PDFItem
from src.pdf.builder._consts import *

FILE = 'templates/image.pdf'
MINOR_FILE = 'templates/image_minor.pdf'


def fill_image_form(data: PDFItem, with_parent: bool):
    logging.info(f'fill_image_form:: forms={fillpdfs.get_form_fields(MINOR_FILE if with_parent else FILE)}')

    values = {
        FORM_FULL_NAME: f"{data.name} {data.surname}",
        FORM_NIF: data.nif,
        FORM_SIGN_IN: data.sign_in,
        FORM_SIGN_ON_DAY: data.sign_on_day,
        FORM_SIGN_ON_MONTH: data.sign_on_month,
        FORM_SIGN_ON_YEAR: data.sign_on_year[2:],
    }

    if with_parent:
        values[f'parent_{FORM_FULL_NAME}'] = f"{data.parent_name} {data.parent_surname}"
        values[f'parent_{FORM_NIF}'] = data.parent_dni
        values[f'parent_{FORM_CATEGORY}'] = data.parent_category

    logging.info(f'fill_image_form:: {values=}')
    fillpdfs.write_fillable_pdf(
        MINOR_FILE if with_parent else FILE,
        f"./out/{data.birth.split('/')[-1]} - {data.surname}, {data.name}_image.pdf",
        values
    )
