import logging

from fillpdf import fillpdfs

from ._fields import Fields
from ._item import PdfItem

FILE = "templates/image.pdf"
MINOR_FILE = "templates/image_minor.pdf"


def fill_image_form(data: PdfItem, with_parent: bool):
    logging.info("image:: starting image form")

    values = {
        Fields.FORM_FULL_NAME: f"{data.name} {data.surname}",
        Fields.FORM_NIF: data.nif,
        Fields.FORM_SIGN_IN: data.sign_in,
        Fields.FORM_SIGN_ON_DAY: data.sign_on_day,
        Fields.FORM_SIGN_ON_MONTH: data.sign_on_month,
        Fields.FORM_SIGN_ON_YEAR: data.sign_on_year[2:] if data.sign_on_year else None,
    }
    assert data.birth

    if with_parent:
        values[f"parent_{Fields.FORM_FULL_NAME}"] = f"{data.parent_name} {data.parent_surname}"
        values[f"parent_{Fields.FORM_NIF}"] = data.parent_dni
        values[f"parent_{Fields.FORM_CATEGORY}"] = data.parent_category

    logging.info(f"image:: {values=}")
    fillpdfs.write_fillable_pdf(
        MINOR_FILE if with_parent else FILE,
        f"./out/{data.birth.split('/')[-1]} - {data.surname}, {data.name}_image.pdf",
        values,
    )
