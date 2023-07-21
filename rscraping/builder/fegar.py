import logging
import os

from ._item import Field, PdfItem
from typing import Optional
from fillpdf import fillpdfs

FILE = "templates/fegar.pdf"
NIF_SIZE = (245, 150)
IMAGE_SIZE = (90, 110)


def fill_fegar_form(
    data: PdfItem, with_parent: bool, images_folder: Optional[str] = None, remove_temp_files: bool = True
):
    logging.info(f"fegar:: starting fegar form")

    values = {
        Field.FORM_NAME: data.name,
        Field.FORM_SURNAME: data.surname,
        Field.FORM_NIF: data.nif,
        Field.FORM_GENDER: data.gender,
        Field.FORM_BIRTH: data.birth,
        Field.FORM_CATEGORY: data.category,
        Field.FORM_TOWN: data.town,
        Field.FORM_STATE: data.state,
        Field.FORM_NATIONALITY: data.nationality,
        Field.FORM_ADDRESS: data.address,
        Field.FORM_ADDRESS_NUMBER: data.address_number,
        Field.FORM_POSTAL_CODE: data.postal_code,
        Field.FORM_COUNTRY: data.country,
        Field.FORM_PHONE: data.phone,
        Field.FORM_ENTITY: data.entity,
        Field.FORM_EMAIL: data.email,
        Field.FORM_SIGN_IN: data.sign_in,
        Field.FORM_SIGN_ON_DAY: data.sign_on_day,
        Field.FORM_SIGN_ON_MONTH: data.sign_on_month,
        Field.FORM_SIGN_ON_YEAR: data.sign_on_year[2:] if data.sign_on_year else None,
        Field.FORM_ENTITY_ADDRESS: data.entity_town,
        Field.FORM_ENTITY_STATE: data.entity_state,
        Field.FORM_ROWER: "Yes" if data.is_rower else None,
        Field.FORM_COACH: "Yes" if data.is_coach else None,
        Field.FORM_DIRECTIVE: "Yes" if data.is_directive else None,
    }
    assert data.birth

    if with_parent:
        values[f"parent_{Field.FORM_NAME}"] = data.parent_name
        values[f"parent_{Field.FORM_SURNAME}"] = data.parent_surname
        values[f"parent_{Field.FORM_NIF}"] = data.parent_dni
        values[f"parent_{Field.FORM_ADDRESS}"] = data.address
        values[f"parent_{Field.FORM_ADDRESS_NUMBER}"] = data.address_number
        values[f"parent_{Field.FORM_TOWN}"] = data.town
        values[f"parent_{Field.FORM_POSTAL_CODE}"] = data.postal_code

    logging.info(f"fegar:: {values=}")
    file_name = f"./out/{data.birth.split('/')[-1]} - {data.surname}, {data.name}_fegar"
    fillpdfs.write_fillable_pdf(FILE, f"{file_name}.pdf", values)

    if images_folder:
        add_images(data, images_folder, file_name, remove_temp_files=remove_temp_files)


def add_images(data: PdfItem, images_folder: str, file_name: str, remove_temp_files: bool):
    assert data.name and data.surname
    image_file = front_file = back_file = None

    for file in os.listdir(images_folder):
        file_lower = file.lower()
        if not os.path.isfile(file) and not any(file_lower.endswith(x) for x in ["png", "jpg", "jpeg"]):
            continue

        if data.name.lower() in file_lower and data.surname.lower() in file_lower:
            if "image" in file_lower:
                image_file = os.path.join(images_folder, file)
            if "back" in file_lower:
                back_file = os.path.join(images_folder, file)
            if "front" in file_lower:
                front_file = os.path.join(images_folder, file)

    if any(x is None for x in [image_file, front_file, back_file]):
        raise ValueError(f"Image not found")

    logging.info(f"fegar:: adding {image_file=}")
    fillpdfs.place_image(
        file_name=image_file,
        x=460,
        y=95,
        input_pdf_path=f"{file_name}.pdf",
        output_map_path=f"{file_name}_with_image.pdf",
        page_number=0,
        width=IMAGE_SIZE[0],
        height=IMAGE_SIZE[1],
    )

    logging.info(f"fegar:: adding {front_file=}")
    fillpdfs.place_image(
        file_name=front_file,
        x=76,
        y=625,
        input_pdf_path=f"{file_name}_with_image.pdf",
        output_map_path=f"{file_name}_with_front.pdf",
        page_number=0,
        width=NIF_SIZE[0],
        height=NIF_SIZE[1],
    )

    logging.info(f"fegar:: adding {back_file=}")
    fillpdfs.place_image(
        file_name=back_file,
        x=322,
        y=625,
        input_pdf_path=f"{file_name}_with_front.pdf",
        output_map_path=f"{file_name}_complete.pdf",
        page_number=0,
        width=NIF_SIZE[0],
        height=NIF_SIZE[1],
    )

    if remove_temp_files:
        logging.info(f"fegar:: removing temporal files")
        os.remove(f"{file_name}.pdf")
        os.remove(f"{file_name}_with_image.pdf")
        os.remove(f"{file_name}_with_front.pdf")

        os.rename(f"{file_name}_complete.pdf", f"{file_name}.pdf")
