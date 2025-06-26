import logging
import webbrowser
import numpy as np
import pyroll.core as pr

from pathlib import Path


def test_solve_with_tension_algorithm(tmp_path: Path, caplog):
    caplog.set_level(logging.INFO, logger="pyroll")

    import pyroll.wusatowski_spreading
    import pyroll.freiberg_flow_stress
    #import pyroll.tension_spreading_interaction

    in_profile = pr.Profile.round(
        diameter=17e-3,
        temperature=1200 + 273.15,
        material=["C45", "steel"],

        elastic_modulus=5.1e10
    )

    ratios = np.array([1.241, 1.229, 1.276])

    sequence = pr.PassSequence(
        [
            pr.RollPass(
                label="Oval I",
                roll=pr.Roll(
                    groove=pr.CircularOvalGroove(
                        depth=4.35e-3,
                        r1=1.8e-3,
                        r2=18.5e-3
                    ),
                    nominal_radius=208e-3,
                ),
                gap=2.05e-3,
            ),
            pr.Transport(
                label="I => II",
                length=1,
            ),
            pr.RollPass(
                label="Round II",
                roll=pr.Roll(
                    groove=pr.FalseRoundGroove(
                        r1=1.55e-3,
                        r2=7.1e-3,
                        flank_angle=60,
                        depth=6e-3
                    ),
                    nominal_radius=208e-3,
                ),
                gap=3e-3,
            ),
            pr.Transport(label="II => III", length=1),
            pr.RollPass(
                label="Oval III",
                roll=pr.Roll(
                    groove=pr.CircularOvalGroove(
                        depth=3.6e-3,
                        r1=1.4e-3,
                        r2=15e-3
                    ),
                    nominal_radius=208e-3,
                ),
                gap=3e-3,
            ),
        ]
    )

    try:
        sequence.solve_interstand_tensions_with_given_velocity_ratios(in_profile=in_profile, final_speed=20.47, velocity_ratios=ratios)
    finally:
        print("\nLog:")
        print(caplog.text)

    try:
        import pyroll.report

        report = pyroll.report.report(sequence)

        report_file = tmp_path / "report.html"
        report_file.write_text(report, encoding="utf-8")
        print(report_file)
        webbrowser.open(report_file.as_uri())

    except ImportError:
        pass
