import unittest

from rscraping.clients import ABEClient, ACTClient, ARCClient, Client, LGTClient, TrainerasClient
from rscraping.data.models import Datasource


class TestClient(unittest.TestCase):
    def test_client_initialization(self):
        self.assertTrue(isinstance(Client(source=Datasource.TRAINERAS), TrainerasClient))
        self.assertTrue(isinstance(Client(source=Datasource.ACT), ACTClient))
        self.assertTrue(isinstance(Client(source=Datasource.ARC), ARCClient))
        self.assertTrue(isinstance(Client(source=Datasource.ABE), ABEClient))
        self.assertTrue(isinstance(Client(source=Datasource.LGT), LGTClient))
