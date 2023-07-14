import inquirer

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from pyutils.validators import is_valid_dni, is_valid_email


@dataclass
class PdfItem:
    name: Optional[str] = None
    surname: Optional[str] = None
    nif: Optional[str] = None
    gender: Optional[str] = None
    birth: Optional[str] = None
    nationality: Optional[str] = None
    category: Optional[str] = None

    address: Optional[str] = None
    address_number: Optional[str] = None
    postal_code: Optional[str] = None
    town: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    entity: Optional[str] = None
    entity_town: Optional[str] = None
    entity_state: Optional[str] = None

    sign_in: Optional[str] = None
    sign_on_day: Optional[str] = None
    sign_on_month: Optional[str] = None
    sign_on_year: Optional[str] = None

    parent_name: Optional[str] = None
    parent_surname: Optional[str] = None
    parent_dni: Optional[str] = None
    parent_category: Optional[str] = None
    is_rower: Optional[bool] = False

    is_coach: Optional[bool] = False
    is_directive: Optional[bool] = False

    @classmethod
    def preset(cls) -> "PdfItem":
        return PdfItem(
            country="ESPAÑA",
            nationality="ESPAÑOLA",
            phone="609262163",
            email="remopuebla@gmail.com",
            entity="CLUB REMO PUEBLA",
            entity_town="A POBRA DO CARAMIÑAL",
            entity_state="A CORUÑA",
            sign_in="A POBRA DO CARAMIÑAL",
            parent_category="TUTOR",
        )

    def sign_on(self, date: str) -> "PdfItem":
        day, month, year = date.split("/")
        self.sign_on_day = day
        self.sign_on_month = month
        self.sign_on_year = year
        return self


def prompt_rower_data(data: PdfItem) -> PdfItem:
    answers = inquirer.prompt(
        [
            inquirer.Text("name", message="Nombre", validate=lambda _, x: bool(x)),
            inquirer.Text("surname", message="Apellidos", validate=lambda _, x: bool(x)),
            inquirer.Text("nif", message="DNI", validate=lambda _, x: is_valid_dni(x.upper())),
            inquirer.Text(
                "birth", message="Fecha nacimiento (DD/MM/YYYY)", validate=lambda _, x: len(x.split("/")) == 3
            ),
            inquirer.Text("gender", message="Sexo", choices=["HOMBRE", "MUJER"], validate=lambda _, x: bool(x)),
            inquirer.Text("address", message="Dirección (calle, número)", validate=lambda _, x: bool(x)),
            inquirer.Text("town", message="Localidad", default="A POBRA DO CARAMIÑAL", validate=lambda _, x: bool(x)),
            inquirer.Text("postal_code", message="Código Postal", default="15940", validate=lambda _, x: len(x) == 5),
            inquirer.Text("state", message="Provincia", default="A CORUÑA", validate=lambda _, x: bool(x)),
        ]
    )

    if not answers:
        raise ValueError("error in {answers=}")

    data.name = answers["name"].upper()
    data.surname = answers["surname"].upper()
    data.nif = answers["nif"].upper()
    data.birth = answers["birth"]
    data.gender = answers["gender"].upper()
    data.town = answers["town"].upper()
    data.postal_code = answers["postal_code"]
    data.state = answers["state"].upper()

    address = answers["address"].upper().split(",")
    if len(address) == 1:
        data.address = address[0]
    else:
        data.address = " ".join(address[:-1])
        data.address_number = address[-1]

    data.category = _compute_category(int(data.birth.split("/")[-1]))
    return data


def prompt_extra_data(data: PdfItem) -> PdfItem:
    answers = inquirer.prompt(
        [
            inquirer.Text("nationality", message="Nacionalidad", default="ESPAÑOLA", validate=lambda _, x: bool(x)),
            inquirer.Text("country", message="Pais", default="ESPAÑA", validate=lambda _, x: bool(x)),
            inquirer.Text(
                "sign_in", message="Firmado en", default="A POBRA DO CARAMIÑAL", validate=lambda _, x: bool(x)
            ),
        ]
    )

    if not answers:
        raise ValueError("error in {answers=}")

    data.nationality = answers["nationality"].upper()
    data.country = answers["country"].upper()
    data.sign_in = answers["sign_in"].upper()

    return data


def prompt_entity_data(data: PdfItem) -> PdfItem:
    answers = inquirer.prompt(
        [
            inquirer.Text("phone", message="Telefono", default="609262163", validate=lambda _, x: len(x) == 9),
            inquirer.Text(
                "email", message="Correo", default="remopuebla@gmail.com", validate=lambda _, x: is_valid_email(x)
            ),
            inquirer.Text("entity", message="Club", default="CLUB REMO PUEBLA", validate=lambda _, x: bool(x)),
            inquirer.Text(
                "entity_town", message="Localidad Club", default="A POBRA DO CARAMIÑAL", validate=lambda _, x: bool(x)
            ),
            inquirer.Text("entity_state", message="Provincia Club", default="A CORUÑA", validate=lambda _, x: bool(x)),
        ]
    )

    if not answers:
        raise ValueError("error in {answers=}")

    data.phone = answers["phone"]
    data.email = answers["email"].lower()
    data.entity = answers["entity"].upper()
    data.entity_town = answers["entity_town"].upper()
    data.entity_state = answers["entity_state"].upper()

    return data


def prompt_parent_data(data: PdfItem) -> PdfItem:
    answers = inquirer.prompt(
        [
            inquirer.Text("parent_name", message="Nombre Tutor", validate=lambda _, x: bool(x)),
            inquirer.Text("parent_surname", message="Apellidos Tutor", validate=lambda _, x: bool(x)),
            inquirer.Text("parent_dni", message="DNI Tutor", validate=lambda _, x: is_valid_dni(x.upper())),
            inquirer.Text("parent_category", message="Tipo de Tutor", default="TUTOR", validate=lambda _, x: bool(x)),
        ]
    )

    if not answers:
        raise ValueError("error in {answers=}")

    data.parent_name = answers["parent_name"]
    data.parent_surname = answers["parent_surname"].upper()
    data.parent_dni = answers["parent_dni"].upper()
    data.parent_category = answers["parent_category"].upper()

    return data


def _compute_category(birth_year: int) -> str:
    age = datetime.now().year - birth_year
    category_ranges = {
        "SENIOR": (19, float("inf")),
        "JUVENIL": (17, 18),
        "CADETE": (15, 16),
        "INFANTIL": (13, 14),
        "ALEVIN": (0, 12),
    }
    for category, (min_age, max_age) in category_ranges.items():
        if min_age <= age <= max_age:
            return category
    raise ValueError(f"not found category for {birth_year=}")


class Field:
    FORM_NAME = "name"
    FORM_SURNAME = "surname"
    FORM_FULL_NAME = "full_name"
    FORM_NIF = "nif"
    FORM_GENDER = "gender"
    FORM_BIRTH = "birth"
    FORM_CATEGORY = "category"
    FORM_NATIONALITY = "nationality"

    FORM_ADDRESS = "address"
    FORM_ADDRESS_NUMBER = "address_number"
    FORM_POSTAL_CODE = "postal_code"
    FORM_TOWN = "town"
    FORM_STATE = "state"
    FORM_COUNTRY = "country"
    FORM_PHONE = "phone"
    FORM_EMAIL = "email"

    FORM_ENTITY = "entity"
    FORM_ENTITY_ADDRESS = "entity_address"
    FORM_ENTITY_STATE = "entity_state"

    FORM_SIGN_IN = "sign_in"
    FORM_SIGN_ON_DAY = "sign_on_day"
    FORM_SIGN_ON_MONTH = "sign_on_month"
    FORM_SIGN_ON_YEAR = "sign_on_year"

    FORM_ROWER = "checkbox_rower"
    FORM_COACH = "checkbox_coach"
    FORM_DIRECTIVE = "checkbox_directive"
