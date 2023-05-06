import logging

from fillpdf import fillpdfs

from src.pdf.builder._item import PdfItem, Field

FILE = 'templates/national.pdf'


def fill_national_form(data: PdfItem, with_parent: bool):
    logging.info(f'national:: starting national form')

    values = {
        Field.FORM_FULL_NAME: f"{data.name} {data.surname}",
        Field.FORM_ADDRESS: f'{data.address}, {data.address_number}' if data.address_number else data.address,
        Field.FORM_POSTAL_CODE: data.postal_code,
        Field.FORM_TOWN: data.town,
        Field.FORM_STATE: data.state,
        Field.FORM_PHONE: data.phone,
        Field.FORM_BIRTH: data.birth,
        Field.FORM_GENDER: data.gender,
        Field.FORM_NATIONALITY: data.nationality,
        Field.FORM_NIF: data.nif,
        Field.FORM_ENTITY: data.entity,
        Field.FORM_EMAIL: data.email,
        Field.FORM_SIGN_IN: data.sign_in,
        Field.FORM_SIGN_ON_DAY: data.sign_on_day,
        Field.FORM_SIGN_ON_MONTH: data.sign_on_month,
        Field.FORM_SIGN_ON_YEAR: data.sign_on_year[2:],
        Field.FORM_ROWER: 'Yes' if data.is_rower else None,
        Field.FORM_COACH: 'Yes' if data.is_coach else None,
        Field.FORM_DIRECTIVE: 'Yes' if data.is_directive else None,
    }

    if with_parent:
        values[f'parent_{Field.FORM_FULL_NAME}'] = f"{data.parent_name} {data.parent_surname}"
        values[f'parent_{Field.FORM_NIF}'] = data.parent_dni

    logging.info(f'national:: {values=}')
    fillpdfs.write_fillable_pdf(FILE, f"./out/{data.birth.split('/')[-1]} - {data.surname}, {data.name}_national.pdf", values)
