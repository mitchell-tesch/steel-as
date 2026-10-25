"""AS/NZS 3678 Grade 450 plate (AS 4100 Table 2.1) and thickness-dependent f_u."""

import pytest

from steelas.member.material import AS3678_fu, AS3678_fy, SteelMaterial
from steelas.member.member import SteelSection


@pytest.mark.parametrize(
    ("t", "fy", "fu"),
    [(10, 450, 520), (20, 450, 520), (21, 420, 500), (32, 420, 500), (33, 400, 500), (50, 400, 500)],
)
def test_gr450_table_2_1(t, fy, fu):
    assert AS3678_fy("GR450", t) == fy
    assert AS3678_fu("GR450", t) == fu


def test_gr450_beyond_50mm_is_not_covered():
    with pytest.raises(ValueError):
        AS3678_fy("GR450", 60)
    with pytest.raises(ValueError):
        AS3678_fu("GR450", 60)


def test_other_as3678_grades_unchanged():
    assert AS3678_fy("GR400", 10) == 400
    assert AS3678_fy("GR350", 16) == 350
    assert AS3678_fy("GR300", 25) == 280
    assert AS3678_fu("GR400") == 480
    assert AS3678_fu("GR300") == 430


def test_welded_gr450_section_uses_thickest_plate_for_fu():
    """f_u follows the thickest plate of the section (lower, conservative)."""
    section = SteelSection.from_section_dict(dict(
        name="X", sec_type="WB", mat_type="WeldedSection", grade="GR450",
        d=700.0, b=250.0, t_f=16.0, t_w=25.0,
    ))
    assert section.mat.f_y == 450   # flange, t_f = 16
    assert section.mat.f_yw == 420  # web, t_w = 25
    assert section.mat.f_u == 500   # thickest plate, 25 mm


def test_thin_welded_gr450_section():
    mat = SteelMaterial(grade="GR450", mat_type="WeldedSection", t_f=12.0, t_w=8.0)
    assert (mat.f_y, mat.f_yw, mat.f_u) == (450, 450, 520)
