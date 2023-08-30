import numpy as np
from pyroll.core import RollPass, Hook
from dataclasses import dataclass

VERSION = "2.1.1"


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


RollPass.tension_model = Hook[TensionElongationModel]()
"""Tension model according to Dobler and Mauk."""

RollPass.log_tension_elongation = Hook[float]()
"""Logarithmic elongation of the profile due to tension."""


@RollPass.tension_model
def tension_model(self: RollPass):
    return TensionElongationModel(self)


@RollPass.log_tension_elongation
def log_tension_elongation(self: RollPass):
    mean_flow_stress = (self.in_profile.flow_stress + 2 * self.out_profile.flow_stress) / 3
    mean_cross_section = (self.in_profile.cross_section.area + 2 * self.out_profile.cross_section.area) / 3

    relative_back_tension = self.back_tension / mean_flow_stress
    relative_front_tension = self.front_tension / mean_flow_stress

    profile_aspect_ratio = self.in_profile.equivalent_width / self.in_profile.equivalent_height
    area_ratio = self.roll.contact_area / mean_cross_section

    first_coefficient = self.tension_model.m11 * self.rel_draught + self.tension_model.m12 * profile_aspect_ratio + self.tension_model.m13 * area_ratio
    second_coefficient = self.tension_model.m21 * self.rel_draught + self.tension_model.m22 * profile_aspect_ratio + self.tension_model.m23 * area_ratio
    third_coefficient = self.tension_model.m31 * self.rel_draught + self.tension_model.m32 * profile_aspect_ratio + self.tension_model.m33 * area_ratio

    return first_coefficient * relative_back_tension ** 2 + second_coefficient * relative_back_tension + third_coefficient * relative_front_tension


# @RollPass.spread(wrapper=True)
# def spread(self: RollPass, cycle):
#    if cycle:
#        return None
#
#    spread_without_tension = (yield)
#
#    elongation_with_tension = np.exp(self.log_elongation + self.log_tension_elongation)
#    spread_with_tension = (spread_without_tension * self.draught * self.elongation) / (
#            self.draught * elongation_with_tension)
#
#    return spread_with_tension


@RollPass.OutProfile.width(wrapper=True)
def width_with_tension(self: RollPass.OutProfile, cycle):
    if cycle:
        return None

    out_profile_width_without_tension = (yield)
    self.__cache__["width"] = out_profile_width_without_tension

    rp = self.roll_pass

    spread_without_tension = out_profile_width_without_tension / rp.in_profile.width

    elongation_with_tension = np.exp(rp.log_elongation + rp.log_tension_elongation)
    spread_with_tension = (spread_without_tension * rp.draught * rp.elongation) / (
            rp.draught * elongation_with_tension)

    return  rp.in_profile.width * spread_with_tension
