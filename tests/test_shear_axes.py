"""Axis shear regressions; formula expectations are not independent certification."""

from copy import deepcopy
from math import nan

import pytest

from steelas.data.io import MemberLibrary
from steelas.member.member import SteelMember, SteelSection


def member(name="150UB18.0 (GR300)", library=MemberLibrary.OpenSections, **kwargs):
    return SteelMember(
        section=SteelSection.from_library(library, name), sig_figs=0, **kwargs
    )


@pytest.mark.parametrize(
    "name, library, nominal",
    [
        ("150UB18.0 (GR300)", MemberLibrary.OpenSections, 178.56),
        ("250UC72.9 (GR300)", MemberLibrary.OpenSections, 419.07456),
        ("150PFC (GR300)", MemberLibrary.OpenSections, 172.8),
        ("125x75x6RHS (C450)", MemberLibrary.HollowSections, 366.12),
    ],
)
def test_major_axis_capacities_are_unchanged(name, library, nominal):
    m = member(name, library)
    assert m.V_v == pytest.approx(nominal, rel=1e-12)
    assert m.phiV_v == pytest.approx(0.9 * nominal, rel=1e-12)
    before = deepcopy(vars(m))
    assert m.phiV_vy > 0
    assert m.V_v == before["V_v"] and m.phiV_v == before["phiV_v"]


@pytest.mark.parametrize("series", ["UB", "UC", "TFB", "WB", "WC", "PFC"])
def test_open_section_full_flange_nonuniform_model(series):
    m = member(phi=0.8)
    # Exercise the common flange model independently of catalogue coverage.
    m.section.geom.sec_type = series
    m.section.geom.b = 100.0
    m.section.geom.t_f = 10.0
    m.section.mat.f_y = 250.0
    # Two flanges: A = 2000 mm2; Vu = 300 kN; Vnu = 2*300/(0.9+1.5).
    assert m.V_vy == pytest.approx(250.0)
    assert m.phiV_vy == pytest.approx(200.0)


@pytest.mark.parametrize(
    "width, expected",
    [(81.0, 20.25), (82.0, 20.5), (164.0, 10.25)],
)
def test_full_flange_shear_buckling_boundary(width, expected):
    m = member()
    m.section.geom.b, m.section.geom.t_f = width, 1.0
    m.section.mat.f_y = 250.0
    assert m.V_vy == pytest.approx(expected, rel=1e-12)


def test_rectangular_hollow_uses_two_clear_uniform_panels_and_rotation():
    m = member("125x75x6RHS (C450)", MemberLibrary.HollowSections)
    # (75 - 12) * 2 * 6 * 0.6 * 450 / 1000
    assert m.V_vy == pytest.approx(204.12)
    assert m.phiV_vy == pytest.approx(183.708)
    geometry = m.section.geom
    geometry.b = geometry.d
    geometry.sec_type = "SHS"
    assert m.V_vy == pytest.approx(m.V_v, rel=1e-12)


def test_hollow_minor_axis_uses_its_own_shear_buckling_width():
    m = member("125x75x6RHS (C450)", MemberLibrary.HollowSections)
    m.section.geom.b, m.section.geom.t = 166.0, 1.0
    m.section.mat.f_y = 250.0
    # Clear width/t = 164; alpha_v = (82/164)^2 = 0.25.
    assert m.V_vy == pytest.approx(12.3)


@pytest.mark.parametrize("sig_figs", [0, 3])
def test_chs_preserves_same_capacity_for_both_axes(sig_figs):
    m = SteelMember(
        section=SteelSection.from_library(
            MemberLibrary.HollowSections, "26.9x2.6CHS (C250)"
        ),
        sig_figs=sig_figs,
        phi=0.8,
    )
    assert m.V_vy == m.V_v
    assert m.phiV_vy == m.phiV_v
    if sig_figs == 0:
        assert m.V_vy == pytest.approx(0.36 * m.section.f_y * m.section.A_g / 1000)


@pytest.mark.parametrize("field, value", [("b", 0), ("b", nan), ("t_f", -1)])
def test_invalid_minor_panel_dimensions_raise(field, value):
    m = member()
    setattr(m.section.geom, field, value)
    with pytest.raises(ValueError, match="positive finite"):
        _ = m.V_vy


def test_unsupported_minor_family_is_explicit_and_does_not_change_major_result():
    m = member()
    major = m.phiV_v
    m.section.geom.sec_type = "RectPlate"
    with pytest.raises(NotImplementedError, match="RectPlate"):
        _ = m.phiV_vy
    assert m.phiV_v == major
