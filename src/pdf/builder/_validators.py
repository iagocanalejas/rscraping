import re

tabla = "TRWAGMYFPDXBNJZSQVHLCKE"
external = "XYZ"
external_map = {'X': '0', 'Y': '1', 'Z': '2'}
numbers = "1234567890"


def is_valid_dni(dni: str) -> bool:
    if len(dni) == 9:
        dig_control = dni[8]
        dni = dni[:8]
        if dni[0] in external:
            dni = dni.replace(dni[0], external_map[dni[0]])
        return len(dni) == len([n for n in dni if n in numbers]) and tabla[int(dni) % 23] == dig_control
    return False


def is_valid_email(email: str) -> bool:
    return bool(re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email))
