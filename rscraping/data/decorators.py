import locale
from functools import wraps


def uses_locale(new_locale):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            original_locale = locale.getlocale(locale.LC_TIME)
            locale.setlocale(locale.LC_TIME, new_locale)

            result = func(*args, **kwargs)

            locale.setlocale(locale.LC_TIME, original_locale)
            return result
        return wrapper
    return decorator
