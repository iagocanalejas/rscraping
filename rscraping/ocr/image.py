from abc import ABC, abstractmethod

from matplotlib import pyplot as plt
from numpy.typing import NDArray
from pandas import DataFrame

from pyutils.strings import remove_symbols
from rscraping.data.models import Datasource


class ImageProcessor(ABC):
    DATASOURCE: Datasource
    _registry = {}
    _allow_plot: bool = False

    img: NDArray  # grayscale loaded image
    img_bin: NDArray  # binary representation of the image
    img_vh: NDArray  # vertical and horizontal lines found in the image
    bitnot: NDArray  # binary images with remarked vertical and horizontal lines

    def __init_subclass__(cls, **kwargs):
        source = kwargs.pop("source")
        super().__init_subclass__(**kwargs)
        cls._registry[source] = cls

    def __new__(cls, source: str, allow_plot: bool = False, **_) -> "ImageProcessor":  # pragma: no cover
        subclass = cls._registry[source]
        final_obj = object.__new__(subclass)
        final_obj._allow_plot = allow_plot

        return final_obj

    ####################################################
    #                 ABSTRACT METHODS                 #
    ####################################################
    @abstractmethod
    def retrieve_header_data(self, path: str, header_size: int = 3, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    def retrieve_tabular_dataframe(self, path: str, header_size: int = 3, **kwargs) -> DataFrame:
        raise NotImplementedError

    ####################################################
    #               PROTECTED METHODS                 #
    ####################################################
    def _plot(self, img: NDArray, cmap="gray"):
        if self._allow_plot:
            plt.imshow(img, cmap=cmap)
            plt.show()

    def _clean_dataframe(self, df: DataFrame) -> DataFrame:
        df = df.applymap(remove_symbols)
        return df
