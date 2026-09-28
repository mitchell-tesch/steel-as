"""AS4100 Section 8 combined actions.

Expected values are hand calculations from the capacities pinned in
test_capacities_used_in_hand_calcs, rounded to 4 significant figures.
"""

import pytest

from steelas.data.io import MemberLibrary
from steelas.member.member import SteelMember, SteelSection


@pytest.fixture(scope="module")
def ub150() -> SteelSection:
    return SteelSection.from_library(MemberLibrary.OpenSections, "150UB18.0 (GR300)")


@pytest.fixture(scope="module")
def member(ub150) -> SteelMember:
    # k_t < 1 so that N_t differs from N_s
    return SteelMember(section=ub150, l_ex=3000, l_ey=3000, l_eb=3000, k_t=0.75)


@pytest.fixture(scope="module")
def restrained_member(ub150) -> SteelMember:
    return SteelMember(section=ub150, l_ex=3000, l_ey=3000, l_eb=0, k_t=0.75)


def test_capacities_used_in_hand_calcs(member, restrained_member):
    assert member.phi == 0.9
    assert member.M_sx == pytest.approx(43.2)
    assert member.M_sy == pytest.approx(8.61)
    assert member.M_bx == pytest.approx(20.5)
    assert member.N_s == pytest.approx(735)
    assert member.N_t == pytest.approx(644)
    assert member.N_cx == pytest.approx(618)
    assert member.N_cy == pytest.approx(131)
    assert restrained_member.M_bx == pytest.approx(43.2)


@pytest.mark.parametrize(
    "method, N_star, expected",
    [
        ("M_rx", 0, 43.2),  # M_sx
        ("M_rx", -100, 36.67),  # 43.2 * (1 - 100 / (0.9 * 735))
        ("M_rx", 100, 35.75),  # 43.2 * (1 - 100 / (0.9 * 644))
        ("M_rx", -700, 0),  # N* > phiN_s
        ("M_ry", -100, 7.308),  # 8.61 * (1 - 100 / (0.9 * 735))
        ("M_ry", 100, 7.124),  # 8.61 * (1 - 100 / (0.9 * 644))
        ("M_ix", -100, 35.43),  # 43.2 * (1 - 100 / (0.9 * 618))
        ("M_ix", 100, 35.75),  # Cl 8.4.2.3, M_rx
        ("M_iy", -50, 4.959),  # 8.61 * (1 - 50 / (0.9 * 131))
        ("M_iy", 100, 7.124),  # Cl 8.4.2.3, M_ry
        ("M_ox", -50, 11.81),  # 20.5 * (1 - 50 / (0.9 * 131))
        ("M_ox", 100, 24.04),  # 20.5 * (1 + 100 / (0.9 * 644)) < M_rx = 35.75
        ("M_cx", -50, 11.81),  # min(M_ix = 39.32, M_ox = 11.81)
        ("M_cx", 100, 24.04),  # min(M_rx = 35.75, M_ox = 24.04)
    ],
)
def test_general_capacities(member, method, N_star, expected):
    assert getattr(member, method)(N_star) == pytest.approx(expected, rel=1e-3, abs=1e-9)


def test_M_ox_tension_limited_to_M_rx(restrained_member):
    # 43.2 * (1 + 100 / (0.9 * 644)) = 50.65 > M_rx = 35.75
    assert restrained_member.M_ox(100) == pytest.approx(35.75, rel=1e-3)
