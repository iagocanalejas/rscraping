import logging

from fillpdf import fillpdfs

from ._fields import Fields
from ._item import PdfItem

FILE = "templates/xogade.pdf"


def fill_xogade_form(data: PdfItem):
    logging.info("xogade:: starting xogade form")

    values = {
        Fields.FORM_FULL_NAME: f"{data.name} {data.surname}",
        Fields.FORM_ENTITY: data.entity,
        Fields.FORM_SIGN_IN: data.sign_in,
        Fields.FORM_SIGN_ON_DAY: data.sign_on_day,
        Fields.FORM_SIGN_ON_MONTH: data.sign_on_month,
        Fields.FORM_SIGN_ON_YEAR: data.sign_on_year[2:] if data.sign_on_year else None,
        f"parent_{Fields.FORM_FULL_NAME}": f"{data.parent_name} {data.parent_surname}",
        f"parent_{Fields.FORM_NIF}": data.parent_dni,
    }
    assert data.birth

    logging.info(f"xogade:: {values=}")
    fillpdfs.write_fillable_pdf(
        FILE, f"./out/{data.birth.split('/')[-1]} - {data.surname}, {data.name}_xogade.pdf", values
    )
