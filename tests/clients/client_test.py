import unittest

from rscraping.clients import (
    ABEClient,
    ACTClient,
    ARCClient,
    Client,
    LGTClient,
    TabularClientConfig,
    TabularDataClient,
    TrainerasClient,
)
from rscraping.data.constants import CATEGORY_VETERAN
from rscraping.data.models import Datasource


class TestClient(unittest.TestCase):
    def test_client_initialization(self):
        self.assertTrue(isinstance(Client(source=Datasource.TRAINERAS), TrainerasClient))
        self.assertTrue(isinstance(Client(source=Datasource.ACT), ACTClient))
        self.assertTrue(isinstance(Client(source=Datasource.ARC), ARCClient))
        self.assertTrue(isinstance(Client(source=Datasource.ABE), ABEClient))
        self.assertTrue(isinstance(Client(source=Datasource.LGT), LGTClient))

    def test_client_initialization_with_config(self):
        self.assertTrue(isinstance(Client(source=Datasource.ACT, is_female=True), ACTClient))
        self.assertTrue(isinstance(Client(source=Datasource.ARC, is_female=True), ARCClient))
        self.assertTrue(isinstance(Client(source=Datasource.ABE, is_female=True), ABEClient))
        self.assertTrue(isinstance(Client(source=Datasource.LGT, is_female=True), LGTClient))

        client = Client(source=Datasource.TRAINERAS, is_female=True, category=CATEGORY_VETERAN)
        self.assertTrue(isinstance(client, TrainerasClient))

        with self.assertRaises(ValueError):
            config = TabularClientConfig(file_path="1", sheet_id="1")
            TabularDataClient(source=Datasource.TABULAR, config=config)

        TabularDataClient._load_dataframe = self._load_dataframe  # type: ignore
        client = Client(source=Datasource.TABULAR, config=TabularClientConfig(sheet_id=""))
        self.assertTrue(isinstance(client, TabularDataClient))

        client = Client(source=Datasource.TABULAR, config=TabularClientConfig(sheet_id="", sheet_name="femenina"))
        self.assertTrue(isinstance(client, TabularDataClient))
        self.assertTrue(client._is_female)

    # testing replacement for _load_dataframe
    def _load_dataframe(*_, **__):
        return None
