from simplemma.lemmatizer import text_lemmatizer

from pyutils.strings import normalize_synonyms, remove_conjunctions, remove_parenthesis, remove_symbols, unaccent
from rscraping.data.constants import SYNONYMS


def lemmatize(phrase: str, lang: str = "es") -> list[str]:
    """
    Lemmatize a phrase using the simplemma library. The phrase is preprocessed before lemmatization.
    Synonyms are normalized, conjunctions are removed and symbols are removed. Accents are removed after lemmatization.

    Parameters:
    - phrase (str): The phrase to lemmatize.
    - lang (str): The language of the phrase (default: "es").

    Returns: list[str]: A list of lemmatized words from the phrase.
    """
    phrase = normalize_synonyms(phrase, SYNONYMS)
    phrase = remove_symbols(remove_conjunctions(phrase)).replace(".", " ")
    phrase = remove_parenthesis(phrase, preserve_content=True)
    tokens = [unaccent(w).strip() for w in set(text_lemmatizer(phrase, lang=lang))]

    return tokens
