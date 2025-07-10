import logging
import webbrowser
from pathlib import Path

import matplotlib.pyplot as plt
from pyroll.core import Profile, PassSequence, RollPass, Roll, CircularOvalGroove, Transport, RoundGroove

in_profile = Profile.round(
        diameter=30e-3,
        temperature=1200 + 273.15,
        strain=0,
        material=["C45", "steel"],
        flow_stress=100e6,
        density=7.5e3,
        thermal_capacity=690,
    )

def test_solve_only_front_tension(tmp_path: Path, caplog):
    caplog.set_level(logging.INFO, logger="pyroll")

    import pyroll.wusatowski_spreading
    import pyroll.tension_spreading_interaction

    sequence = PassSequence([
        RollPass(
            label="Oval I",
            roll=Roll(
                groove=CircularOvalGroove(
                    depth=8e-3,
                    r1=6e-3,
                    r2=40e-3
                ),
                nominal_radius=160e-3,
                rotational_frequency=1
            ),
            gap=2e-3,
            front_tension=25e6,
            back_tension=0
        )
    ])

    try:
        sequence.solve(in_profile)
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


def test_solve_only_back_tension(tmp_path: Path, caplog):
    caplog.set_level(logging.INFO, logger="pyroll")

    import pyroll.wusatowski_spreading
    import pyroll.tension_spreading_interaction

    sequence = PassSequence([
        RollPass(
            label="Oval I",
            roll=Roll(
                groove=CircularOvalGroove(
                    depth=8e-3,
                    r1=6e-3,
                    r2=40e-3
                ),
                nominal_radius=160e-3,
                rotational_frequency=1
            ),
            gap=2e-3,
            front_tension=0,
            back_tension=25e6
        )
    ])

    try:
        sequence.solve(in_profile)
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

def test_solve_comparison(tmp_path: Path, caplog):
    caplog.set_level(logging.INFO, logger="pyroll")

    import pyroll.wusatowski_spreading
    import pyroll.tension_spreading_interaction


    sequence_front_tension = PassSequence([
        RollPass(
            label="Oval I",
            roll=Roll(
                groove=CircularOvalGroove(
                    depth=8e-3,
                    r1=6e-3,
                    r2=40e-3
                ),
                nominal_radius=160e-3,
                rotational_frequency=1
            ),
            gap=2e-3,
            front_tension=10e6,
            back_tension=0
        )
    ])

    sequence_back_tension = PassSequence([
        RollPass(
            label="Oval I",
            roll=Roll(
                groove=CircularOvalGroove(
                    depth=8e-3,
                    r1=6e-3,
                    r2=40e-3
                ),
                nominal_radius=160e-3,
                rotational_frequency=1
            ),
            gap=2e-3,
            front_tension=0,
            back_tension=10e6
        )
    ])

    sequence_without_tension = PassSequence([
        RollPass(
            label="Oval I",
            roll=Roll(
                groove=CircularOvalGroove(
                    depth=8e-3,
                    r1=6e-3,
                    r2=40e-3
                ),
                nominal_radius=160e-3,
                rotational_frequency=1
            ),
            gap=2e-3,
            front_tension=0,
            back_tension=0
        )
    ])

    sequence_front_tension.solve(in_profile)
    sequence_back_tension.solve(in_profile)
    sequence_without_tension.solve(in_profile)

    fig,ax = plt.subplots()

    ax.grid()
    ax.fill(*sequence_without_tension.out_profile.cross_section.boundary.xy, label="No Tension")
    ax.fill(*sequence_front_tension.out_profile.cross_section.boundary.xy, label="Front Tension")
    ax.fill(*sequence_back_tension.out_profile.cross_section.boundary.xy, label="Back Tension")
    ax.legend()
    fig.show()
