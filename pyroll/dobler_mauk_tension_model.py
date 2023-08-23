import numpy as np
from pyroll.core import RollPass, Hook
from dataclasses import dataclass

VERSION = "2.1"


@dataclass
class TensionElongationModel:
    """
    Class representing an elongation model through tension published by Mauk and Dobler.
    """
    rp: RollPass
    m11: float = 1.05502
    m12: float = 0.100816
    m13: float = -0.591029
    m21: float = -0.886507
    m22: float = -0.00258613
    m23: float = 0.159971
    m31: float = -0.347681
    m32: float = -0.0457338
    m33: float = 0.0525161

    def __post_init__(self):
        self.mean_flow_stress = (self.rp.in_profile.flow_stress + 2 * self.rp.out_profile.flow_stress) / 3
        self.mean_cross_section = (
                                          self.rp.in_profile.cross_section.area + 2 * self.rp.out_profile.cross_section.area) / 3

        self.rel_back_tension = self.rp.back_tension / self.mean_flow_stress
        self.rel_front_tension = self.rp.front_tension / self.mean_flow_stress

        self.first_coefficient = self.m11 * self.rp.rel_draught + self.m12 * (
                self.rp.in_profile.width / self.rp.in_profile.height) + self.m13 * (
                                         self.rp.roll.contact_area / self.mean_cross_section)
        self.second_coefficient = self.m21 * self.rp.rel_draught + self.m22 * (
                self.rp.in_profile.width / self.rp.in_profile.height) + self.m23 * (
                                          self.rp.roll.contact_area / self.mean_cross_section)
        self.third_coefficient = self.m31 * self.rp.rel_draught + self.m32 * (
                self.rp.in_profile.width / self.rp.in_profile.height) + self.m33 * (
                                         self.rp.roll.contact_area / self.mean_cross_section)
        self.log_elongation_through_tension = self.tension_elongation()

    def tension_elongation(self):
        return self.first_coefficient * self.rel_back_tension ** 2 + self.second_coefficient * self.rel_back_tension + self.third_coefficient * self.rel_front_tension


RollPass.tension_model = Hook[TensionElongationModel]()
"""Tension model according to Dobler and Mauk."""


@RollPass.tension_model
def tension_model(self: RollPass):
    return TensionElongationModel(self)


@RollPass.spread(wrapper=True)
def spread(self: RollPass, cycle):
    if cycle:
        return None

    spread_without_tension = (yield)

    elongation_with_tension = np.exp(self.log_elongation + self.tension_model.log_elongation_through_tension)
    spread_with_tension = (spread_without_tension * self.draught * self.elongation) / (
            self.draught * elongation_with_tension)

    return spread_with_tension
