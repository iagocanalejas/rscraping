import unittest

from rscraping.clients import (
    ACTClient,
    ARCClient,
    Client,
    LGTClient,
    TrainerasClient,
)
from rscraping.clients.ete import ETEClient
from rscraping.data.constants import CATEGORY_VETERAN, GENDER_FEMALE
from rscraping.data.models import Datasource


class TestClient(unittest.TestCase):
    def test_client_initialization(self):
        self.assertTrue(isinstance(Client(source=Datasource.TRAINERAS), TrainerasClient))
        self.assertTrue(isinstance(Client(source=Datasource.ACT), ACTClient))
        self.assertTrue(isinstance(Client(source=Datasource.ARC), ARCClient))
        self.assertTrue(isinstance(Client(source=Datasource.LGT), LGTClient))

        with self.assertRaises(ValueError):
            # cannot create an ETE client with 'MALE' gender
            Client(source=Datasource.ETE)

    def test_client_initialization_with_config(self):
        self.assertTrue(isinstance(Client(source=Datasource.ACT, gender=GENDER_FEMALE), ACTClient))
        self.assertTrue(isinstance(Client(source=Datasource.ARC, gender=GENDER_FEMALE), ARCClient))
        self.assertTrue(isinstance(Client(source=Datasource.LGT, gender=GENDER_FEMALE), LGTClient))
        self.assertTrue(isinstance(Client(source=Datasource.ETE, gender=GENDER_FEMALE), ETEClient))

        client = Client(source=Datasource.TRAINERAS, gender=GENDER_FEMALE, category=CATEGORY_VETERAN)
        self.assertTrue(isinstance(client, TrainerasClient))
