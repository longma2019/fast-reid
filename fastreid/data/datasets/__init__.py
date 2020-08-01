# encoding: utf-8
"""
@author:  liaoxingyu
@contact: sherlockliao01@gmail.com
"""

from ...utils.registry import Registry

DATASET_REGISTRY = Registry("DATASET")
DATASET_REGISTRY.__doc__ = """
Registry for datasets
It must returns an instance of :class:`Backbone`.
"""

from .cuhk03 import CUHK03
from .dukemtmcreid import DukeMTMC
from .market1501 import Market1501
from .msmt17 import MSMT17
from .veri import VeRi
from .vehicleid import VehicleID, SmallVehicleID, MediumVehicleID, LargeVehicleID
from .veriwild import VeRiWild, SmallVeRiWild, MediumVeRiWild, LargeVeRiWild
from .fangdao_16stores import Fangdao_16stores
from .fangdao_23stores import Fangdao_23stores
from .fangdao_74stores import Fangdao_74stores
from .fangdao_fanhua_14stores import Fangdao_Fanhua_14stores
from .fangdao_fanhua_35stores import Fangdao_Fanhua_35stores

__all__ = [k for k in globals().keys() if "builtin" not in k and not k.startswith("_")]
