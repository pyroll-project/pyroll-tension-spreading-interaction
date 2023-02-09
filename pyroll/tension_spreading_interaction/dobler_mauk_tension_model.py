from pyroll.core import RollPass
from dataclasses import dataclass


@dataclass
class TensionElongationModel:
    """
    Class representing an elongation model through tension published by Mauk and Dobler.
    """
    roll_pass: RollPass
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
        self.mean_flow_stress = (self.roll_pass.in_profile.flow_stress + 2 * self.roll_pass.out_profile.flow_stress) / 3
        self.mean_cross_section = (self.roll_pass.in_profile.cross_section.area + 2 * self.roll_pass.out_profile.cross_section.area) / 3

        self.rel_back_tension = self.roll_pass.mean_back_tension / self.mean_flow_stress
        self.rel_front_tension = self.roll_pass.mean_front_tension / self.mean_flow_stress


        self.first_coefficient = self.m11 * self.roll_pass.rel_draught + self.m12 * (self.roll_pass.in_profile.width / self.roll_pass.in_profile.height) + self.m13 * (self.roll_pass.contact_area / self.mean_cross_section)
        self.second_coefficient = self.m21 * self.roll_pass.rel_draught + self.m22 * (self.roll_pass.in_profile.width / self.roll_pass.in_profile.height) + self.m23 * (self.roll_pass.contact_area / self.mean_cross_section)
        self.third_coefficient = self.m31 * self.roll_pass.rel_draught + self.m32 * (self.roll_pass.in_profile.width / self.roll_pass.in_profile.height) + self.m33 * (self.roll_pass.contact_area / self.mean_cross_section)
        self.log_elongation_through_tension = self.elongation_through_tension()

    def elongation_through_tension(self):
        return self.first_coefficient * self.rel_back_tension ** 2 + self.second_coefficient * self.rel_back_tension + self.third_coefficient * self.rel_front_tension
