import logging

import numpy as np
from pyroll.core import RollPass, Hook
from .dobler_mauk_tension_model import TensionElongationModel

RollPass.tension_model = Hook[TensionElongationModel]()
"""Tension model."""

RollPass.log_elongation_with_tension = Hook[float]()
"""Elongation with tensions."""


@RollPass.tension_model
def tension_model(self: RollPass):
    return TensionElongationModel(self)


@RollPass.log_elongation_with_tension
def log_elongation_with_tension(self: RollPass):
    return self.log_elongation + self.tension_model.log_elongation_through_tension


@RollPass.log_elongation
def log_elongation(self: RollPass, cycle: bool):
    if cycle:
        return None
    return self.log_elongation_with_tension


@RollPass.OutProfile.width
def width(self: RollPass.OutProfile):
    log = logging.getLogger(__name__)
    roll_pass = self.roll_pass

    if not self.has_set_or_cached("width"):
        self.width = roll_pass.roll.groove.usable_width

    log_spread = - roll_pass.log_draught - roll_pass.log_elongation
    spread = np.exp(log_spread)

    log.info(f"Calculated spread with tension influence: {spread}.")

    return spread
