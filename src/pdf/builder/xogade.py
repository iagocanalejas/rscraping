import logging

from fillpdf import fillpdfs

from src.pdf.builder import PDFItem
from src.pdf.builder._consts import *

FILE = 'templates/xogade.pdf'


def fill_xogade_form(data: PDFItem):
    logging.info(f'fill_xogade_form:: forms={fillpdfs.get_form_fields(FILE)}')

    values = {
        FORM_FULL_NAME: f"{data.name} {data.surname}",
        FORM_ENTITY: data.entity,
        FORM_SIGN_IN: data.sign_in,
        FORM_SIGN_ON_DAY: data.sign_on_day,
        FORM_SIGN_ON_MONTH: data.sign_on_month,
        FORM_SIGN_ON_YEAR: data.sign_on_year[2:],
        f'parent_{FORM_FULL_NAME}': f"{data.parent_name} {data.parent_surname}",
        f'parent_{FORM_NIF}': data.parent_dni,
    }

    logging.info(f'fill_xogade_form:: {values=}')
    fillpdfs.write_fillable_pdf(FILE, f"./out/{data.birth.split('/')[-1]} - {data.surname}, {data.name}_xogade.pdf", values)
