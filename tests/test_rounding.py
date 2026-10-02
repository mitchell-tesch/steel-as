"""Values are stored unrounded and rounded to sig_figs only when reported."""

import math

import pytest

from steelas.data.io import MemberLibrary, round_sig
from steelas.member.member import SteelMember, SteelSection


@pytest.fixture(scope="module")
def member() -> SteelMember:
    section = SteelSection.from_library(MemberLibrary.OpenSections, "150UB18.0 (GR300)")
    return SteelMember(section=section, l_ex=3456, l_eb=3456, alpha_m=1.135)


def test_inputs_are_not_rounded(member):
    assert (member.l_ex, member.l_eb, member.alpha_m) == (3456, 3456, 1.135)
    assert member.end_i_restraint is True


def test_capacities_match_values_calculated_after_construction(member):
    assert member.N_cx == pytest.approx(member.alpha_cx * member.N_s)


@pytest.mark.parametrize(
    "value, expected",
    [
        (584.594, 585.0),
        (0.0012345, 0.00123),
        (3456, 3456),
        (True, True),
        (0.0, 0.0),
        (math.inf, math.inf),
    ],
)
def test_round_sig(value, expected):
    assert round_sig(value, 3) == expected


def test_report_shows_floats_to_sig_figs(member, capsys):
    member.report(attribute_names=["l_ex", "N_cx", "end_i_restraint"], with_name=False)
    assert capsys.readouterr().out.split() == [
        "l_ex", "=", "3456", "N_cx", "=", "585.0", "end_i_restraint", "=", "True"
    ]
