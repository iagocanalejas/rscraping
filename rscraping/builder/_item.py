from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import inquirer

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

    def prompt_data(self, prompt_entity: bool, has_parent: bool, use_preset: bool, debug: bool = False) -> "PdfItem":
        if debug:
            self.name = "name"
            self.surname = "surname"
            self.nif = "11753905P"
            self.gender = "HOMBRE"
            self.birth = "23/11/2000"
            self.address = "address"
            self.address_number = "15"
            self.postal_code = "15940"
            self.town = "A POBRA DO CARAMIÑAL"
            self.state = "A CORUÑA"
            self.category = "CATEGORIA"

            self.parent_name = "parent_name"
            self.parent_surname = "parent_surname"
            self.parent_dni = "11753905P"
            return self

        self.prompt_rower_data()
        if has_parent:
            self.prompt_parent_data()
        if not prompt_entity:
            self.prompt_entity_data()
        if not use_preset:
            self.prompt_extra_data()
        return self

    def prompt_rower_data(self) -> "PdfItem":
        answers = inquirer.prompt(
            [
                inquirer.Text("name", message="Nombre", validate=lambda _, x: bool(x)),
                inquirer.Text("surname", message="Apellidos", validate=lambda _, x: bool(x)),
                inquirer.Text("nif", message="DNI", validate=lambda _, x: is_valid_dni(x.upper())),
                inquirer.Text(
                    "birth",
                    message="Fecha nacimiento (DD/MM/YYYY)",
                    validate=lambda _, x: len(x.split("/")) == 3,
                ),
                inquirer.Text("gender", message="Sexo", choices=["HOMBRE", "MUJER"], validate=lambda _, x: bool(x)),
                inquirer.Text("address", message="Dirección (calle, número)", validate=lambda _, x: bool(x)),
                inquirer.Text(
                    "town",
                    message="Localidad",
                    default="A POBRA DO CARAMIÑAL",
                    validate=lambda _, x: bool(x),
                ),
                inquirer.Text(
                    "postal_code",
                    message="Código Postal",
                    default="15940",
                    validate=lambda _, x: len(x) == 5,
                ),
                inquirer.Text("state", message="Provincia", default="A CORUÑA", validate=lambda _, x: bool(x)),
            ]
        )

        if not answers:
            raise ValueError(f"error in {answers=}")

        self.name = answers["name"].upper()
        self.surname = answers["surname"].upper()
        self.nif = answers["nif"].upper()
        self.birth = answers["birth"]
        self.gender = answers["gender"].upper()
        self.town = answers["town"].upper()
        self.postal_code = answers["postal_code"]
        self.state = answers["state"].upper()

        address = answers["address"].upper().split(",")
        if len(address) == 1:
            self.address = address[0]
        else:
            self.address = " ".join(address[:-1])
            self.address_number = address[-1]

        self.category = self._compute_category(int(self.birth.split("/")[-1]))
        return self

    def prompt_extra_data(self) -> "PdfItem":
        answers = inquirer.prompt(
            [
                inquirer.Text("nationality", message="Nacionalidad", default="ESPAÑOLA", validate=lambda _, x: bool(x)),
                inquirer.Text("country", message="Pais", default="ESPAÑA", validate=lambda _, x: bool(x)),
                inquirer.Text(
                    "sign_in",
                    message="Firmado en",
                    default="A POBRA DO CARAMIÑAL",
                    validate=lambda _, x: bool(x),
                ),
            ]
        )

        if not answers:
            raise ValueError(f"error in {answers=}")

        self.nationality = answers["nationality"].upper()
        self.country = answers["country"].upper()
        self.sign_in = answers["sign_in"].upper()

        return self

    def prompt_entity_data(self) -> "PdfItem":
        answers = inquirer.prompt(
            [
                inquirer.Text("phone", message="Telefono", default="609262163", validate=lambda _, x: len(x) == 9),
                inquirer.Text(
                    "email",
                    message="Correo",
                    default="remopuebla@gmail.com",
                    validate=lambda _, x: is_valid_email(x),
                ),
                inquirer.Text("entity", message="Club", default="CLUB REMO PUEBLA", validate=lambda _, x: bool(x)),
                inquirer.Text(
                    "entity_town",
                    message="Localidad Club",
                    default="A POBRA DO CARAMIÑAL",
                    validate=lambda _, x: bool(x),
                ),
                inquirer.Text(
                    "entity_state",
                    message="Provincia Club",
                    default="A CORUÑA",
                    validate=lambda _, x: bool(x),
                ),
            ]
        )

        if not answers:
            raise ValueError(f"error in {answers=}")

        self.phone = answers["phone"]
        self.email = answers["email"].lower()
        self.entity = answers["entity"].upper()
        self.entity_town = answers["entity_town"].upper()
        self.entity_state = answers["entity_state"].upper()

        return self

    def prompt_parent_data(self) -> "PdfItem":
        answers = inquirer.prompt(
            [
                inquirer.Text("parent_name", message="Nombre Tutor", validate=lambda _, x: bool(x)),
                inquirer.Text("parent_surname", message="Apellidos Tutor", validate=lambda _, x: bool(x)),
                inquirer.Text("parent_dni", message="DNI Tutor", validate=lambda _, x: is_valid_dni(x.upper())),
                inquirer.Text(
                    "parent_category",
                    message="Tipo de Tutor",
                    default="TUTOR",
                    validate=lambda _, x: bool(x),
                ),
            ]
        )

        if not answers:
            raise ValueError(f"error in {answers=}")

        self.parent_name = answers["parent_name"]
        self.parent_surname = answers["parent_surname"].upper()
        self.parent_dni = answers["parent_dni"].upper()
        self.parent_category = answers["parent_category"].upper()

        return self

    def sign_on(self, date: str) -> "PdfItem":
        day, month, year = date.split("/")
        self.sign_on_day = day
        self.sign_on_month = month
        self.sign_on_year = year
        return self

    def _compute_category(self, birth_year: int) -> str:
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
