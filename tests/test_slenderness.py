"""AS4100 Cl 5.2 section slenderness."""

import math

import pytest

from steelas.member.geometry import SectionGeometry
from steelas.member.material import SteelMaterial
from steelas.member.member import SteelMember, SteelSection
from steelas.member.slenderness import SteelSlenderness


def _chs(d: float, t: float, grade: str = "C350"):
    section = f"{d}x{t}CHS"
    params = dict(
        name=f"{section} ({grade})",
        section=section,
        sec_type="CHS",
        mat_type="HollowSection",
        grade=grade,
        d=d,
        b=math.nan,
        t=t,
        r_o=math.nan,
    )
    return SectionGeometry.from_dict(**params), SteelMaterial.from_dict(**params)


@pytest.mark.parametrize(
    ("t", "governing_ratio"),
    [
        # lam_s = 914 / 9.5 * 350 / 250 = 134.7: root term governs near lam_sy = 120
        (9.5, math.sqrt(120 / (914 / 9.5 * 1.4))),
        # lam_s = 914 / 3 * 350 / 250 = 426.5: squared term governs beyond 2.52 lam_sy
        (3.0, (2 * 120 / (914 / 3.0 * 1.4)) ** 2),
    ],
)
def test_slender_chs_effective_section_modulus(t, governing_ratio):
    geom, mat = _chs(914.0, t)
    slenderness = SteelSlenderness(geom=geom, mat=mat, sig_figs=0)

    assert (slenderness.compact_x, slenderness.compact_y) == ("S", "S")
    assert slenderness.Z_ex == pytest.approx(geom.Z_x * governing_ratio)
    assert slenderness.Z_ey == pytest.approx(slenderness.Z_ex)


def test_slender_chs_effective_section_modulus_is_continuous_at_yield_limit():
    # C250 CHS: lam_s = d / t, so t = 5 sits exactly on lam_sy = 120
    at_limit_geom, at_limit_mat = _chs(600.0, 5.0, "C250")
    beyond_geom, beyond_mat = _chs(600.0, 4.999, "C250")
    at_limit = SteelSlenderness(geom=at_limit_geom, mat=at_limit_mat, sig_figs=0)
    beyond = SteelSlenderness(geom=beyond_geom, mat=beyond_mat, sig_figs=0)

    assert (at_limit.compact_x, beyond.compact_x) == ("N", "S")
    assert beyond.Z_ex / beyond_geom.Z_x == pytest.approx(
        at_limit.Z_ex / at_limit_geom.Z_x, rel=1e-3
    )


def test_slender_chs_member_bending_capacity():
    geom, mat = _chs(914.0, 9.5)
    section = SteelSection(geom=geom, mat=mat, slenderness=None)
    member = SteelMember(section=section, l_ex=6000, l_ey=6000, l_eb=6000, sig_figs=0)

    assert member.M_sx == pytest.approx(section.Z_ex * 350 / 1e6)
    assert member.M_sy == pytest.approx(member.M_sx)
