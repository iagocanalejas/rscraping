import logging

from ._item import Field, PdfItem
from fillpdf import fillpdfs

FILE = "templates/image.pdf"
MINOR_FILE = "templates/image_minor.pdf"


def fill_image_form(data: PdfItem, with_parent: bool):
    logging.info(f"image:: starting image form")

    values = {
        Field.FORM_FULL_NAME: f"{data.name} {data.surname}",
        Field.FORM_NIF: data.nif,
        Field.FORM_SIGN_IN: data.sign_in,
        Field.FORM_SIGN_ON_DAY: data.sign_on_day,
        Field.FORM_SIGN_ON_MONTH: data.sign_on_month,
        Field.FORM_SIGN_ON_YEAR: data.sign_on_year[2:] if data.sign_on_year else None,
    }
    assert data.birth

    if with_parent:
        values[f"parent_{Field.FORM_FULL_NAME}"] = f"{data.parent_name} {data.parent_surname}"
        values[f"parent_{Field.FORM_NIF}"] = data.parent_dni
        values[f"parent_{Field.FORM_CATEGORY}"] = data.parent_category

    logging.info(f"image:: {values=}")
    fillpdfs.write_fillable_pdf(
        MINOR_FILE if with_parent else FILE,
        f"./out/{data.birth.split('/')[-1]} - {data.surname}, {data.name}_image.pdf",
        values,
    )
