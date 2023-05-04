import logging

from fillpdf import fillpdfs

from src.pdf.builder import PDFItem
from src.pdf.builder._consts import *

FILE = 'templates/fegar.pdf'


def fill_fegar_form(data: PDFItem, with_parent: bool):
    logging.info(f'fill_fegar_form:: forms={fillpdfs.get_form_fields(FILE)}')

    values = {
        FORM_NAME: data.name,
        FORM_SURNAME: data.surname,
        FORM_NIF: data.nif,
        FORM_GENDER: data.gender,
        FORM_BIRTH: data.birth,
        FORM_CATEGORY: data.category,
        FORM_TOWN: data.town,
        FORM_STATE: data.state,
        FORM_NATIONALITY: data.nationality,
        FORM_ADDRESS: data.address,
        FORM_ADDRESS_NUMBER: data.address_number,
        FORM_POSTAL_CODE: data.postal_code,
        FORM_COUNTRY: data.country,
        FORM_PHONE: data.phone,
        FORM_ENTITY: data.entity,
        FORM_EMAIL: data.email,
        FORM_SIGN_IN: data.sign_in,
        FORM_SIGN_ON_DAY: data.sign_on_day,
        FORM_SIGN_ON_MONTH: data.sign_on_month,
        FORM_SIGN_ON_YEAR: data.sign_on_year[2:],
        FORM_ENTITY_ADDRESS: data.entity_town,
        FORM_ENTITY_STATE: data.entity_state,
    }

    if with_parent:
        values[f'parent_{FORM_NAME}'] = data.parent_name
        values[f'parent_{FORM_SURNAME}'] = data.parent_surname
        values[f'parent_{FORM_NIF}'] = data.parent_dni
        values[f'parent_{FORM_ADDRESS}'] = data.address
        values[f'parent_{FORM_ADDRESS_NUMBER}'] = data.address_number
        values[f'parent_{FORM_TOWN}'] = data.town
        values[f'parent_{FORM_POSTAL_CODE}'] = data.postal_code

    logging.info(f'fill_fegar_form:: {values=}')
    fillpdfs.write_fillable_pdf(FILE, f"./out/{data.birth.split('/')[-1]} - {data.surname}, {data.name}_fegar.pdf", values)
