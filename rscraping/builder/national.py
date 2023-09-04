import logging

from fillpdf import fillpdfs

from ._fields import Fields
from ._item import PdfItem

FILE = "templates/national.pdf"


def fill_national_form(data: PdfItem, with_parent: bool):
    logging.info("national:: starting national form")

    values = {
        Fields.FORM_FULL_NAME: f"{data.name} {data.surname}",
        Fields.FORM_ADDRESS: f"{data.address}, {data.address_number}" if data.address_number else data.address,
        Fields.FORM_POSTAL_CODE: data.postal_code,
        Fields.FORM_TOWN: data.town,
        Fields.FORM_STATE: data.state,
        Fields.FORM_PHONE: data.phone,
        Fields.FORM_BIRTH: data.birth,
        Fields.FORM_GENDER: data.gender,
        Fields.FORM_NATIONALITY: data.nationality,
        Fields.FORM_NIF: data.nif,
        Fields.FORM_ENTITY: data.entity,
        Fields.FORM_EMAIL: data.email,
        Fields.FORM_SIGN_IN: data.sign_in,
        Fields.FORM_SIGN_ON_DAY: data.sign_on_day,
        Fields.FORM_SIGN_ON_MONTH: data.sign_on_month,
        Fields.FORM_SIGN_ON_YEAR: data.sign_on_year[2:] if data.sign_on_year else None,
        Fields.FORM_ROWER: "Yes" if data.is_rower else None,
        Fields.FORM_COACH: "Yes" if data.is_coach else None,
        Fields.FORM_DIRECTIVE: "Yes" if data.is_directive else None,
    }
    assert data.birth

    if with_parent:
        values[f"parent_{Fields.FORM_FULL_NAME}"] = f"{data.parent_name} {data.parent_surname}"
        values[f"parent_{Fields.FORM_NIF}"] = data.parent_dni

    logging.info(f"national:: {values=}")
    fillpdfs.write_fillable_pdf(
        FILE, f"./out/{data.birth.split('/')[-1]} - {data.surname}, {data.name}_national.pdf", values
    )
