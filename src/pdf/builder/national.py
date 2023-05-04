import logging

from fillpdf import fillpdfs

from src.pdf.builder._consts import *
from src.pdf.builder._item import PDFItem

FILE = 'templates/national.pdf'


def fill_national_form(data: PDFItem, with_parent: bool):
    logging.info(f'fill_national_form:: forms={fillpdfs.get_form_fields(FILE)}')

    values = {
        FORM_FULL_NAME: f"{data.name} {data.surname}",
        FORM_ADDRESS: f'{data.address}, {data.address_number}' if data.address_number else data.address,
        FORM_POSTAL_CODE: data.postal_code,
        FORM_TOWN: data.town,
        FORM_STATE: data.state,
        FORM_PHONE: data.phone,
        FORM_BIRTH: data.birth,
        FORM_GENDER: data.gender,
        FORM_NATIONALITY: data.nationality,
        FORM_NIF: data.nif,
        FORM_ENTITY: data.entity,
        FORM_EMAIL: data.email,
        FORM_SIGN_IN: data.sign_in,
        FORM_SIGN_ON_DAY: data.sign_on_day,
        FORM_SIGN_ON_MONTH: data.sign_on_month,
        FORM_SIGN_ON_YEAR: data.sign_on_year[2:],
    }

    if with_parent:
        values[f'parent_{FORM_FULL_NAME}'] = f"{data.parent_name} {data.parent_surname}"
        values[f'parent_{FORM_NIF}'] = data.parent_dni

    logging.info(f'fill_national_form:: {values=}')
    fillpdfs.write_fillable_pdf(FILE, f"./out/{data.birth.split('/')[-1]} - {data.surname}, {data.name}_national.pdf", values)
