import numpy as np
from pyroll.core import RollPass, Hook
from .dobler_mauk_tension_model import TensionElongationModel

RollPass.tension_model = Hook[TensionElongationModel]()
"""Tension model."""


@RollPass.tension_model
def tension_model(self: RollPass):
    return TensionElongationModel(self)


@RollPass.spread
def spread(self: RollPass, cycle):
    if cycle:
        return None

    elongation_with_tension = np.exp(self.log_elongation + self.tension_model.log_elongation_through_tension)
    spread_with_tension = (self.spread * self.draught * self.elongation) / (self.draught * elongation_with_tension)

    return spread_with_tension
