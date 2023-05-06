import logging

from fillpdf import fillpdfs

from src.pdf.builder import PdfItem
from src.pdf.builder._item import Field

FILE = 'templates/xogade.pdf'


def fill_xogade_form(data: PdfItem):
    logging.info(f'xogade:: starting xogade form')

    values = {
        Field.FORM_FULL_NAME: f"{data.name} {data.surname}",
        Field.FORM_ENTITY: data.entity,
        Field.FORM_SIGN_IN: data.sign_in,
        Field.FORM_SIGN_ON_DAY: data.sign_on_day,
        Field.FORM_SIGN_ON_MONTH: data.sign_on_month,
        Field.FORM_SIGN_ON_YEAR: data.sign_on_year[2:],
        f'parent_{Field.FORM_FULL_NAME}': f"{data.parent_name} {data.parent_surname}",
        f'parent_{Field.FORM_NIF}': data.parent_dni,
    }

    logging.info(f'xogade:: {values=}')
    fillpdfs.write_fillable_pdf(FILE, f"./out/{data.birth.split('/')[-1]} - {data.surname}, {data.name}_xogade.pdf", values)
