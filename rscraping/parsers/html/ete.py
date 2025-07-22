import logging
import os

from rscraping.data.models import Datasource
from rscraping.parsers.html.arc import ARCHtmlParser

logger = logging.getLogger(os.path.dirname(os.path.realpath(__file__)))


class ETEHtmlParser(ARCHtmlParser):
    DATASOURCE = Datasource.ETE
