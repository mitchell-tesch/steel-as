
# API

## Members

### Member shear capacities

`SteelMember.V_v` and `SteelMember.phiV_v` retain their existing nominal and
design major-axis shear capacities (kN). `V_vy` and `phiV_vy` provide the
corresponding minor-axis capacities:

| Section | Minor-axis area | Panel width / thickness | Shear distribution |
| --- | --- | --- | --- |
| UB, UC, TFB, WB, WC, PFC | Both full flanges, `2 b tf` | `b / tf` | Non-uniform, maximum/average ratio 1.5 |
| RHS, SHS | Two clear panels, `2 (b - 2t) t` | `(b - 2t) / t` | Approximately uniform |
| CHS | Existing CHS area/formula | Direction-independent | Reuses `V_v` / `phiV_v` |

The non-CHS calculation uses flange/material yield stress, the existing
unstiffened-panel shear-buckling reduction, and the Clause 5.11.3
`min(Vu, 2 Vu / (0.9 + stress_ratio))` reduction. Fillets and hollow-section
corner radii are not added to the shear area. Non-CHS minor-axis results
have no additional member-level rounding; CHS exactly preserves the existing
rounded or unrounded capacity, including the member's capacity factor.

These properties are evaluated only when requested, so unsupported
minor-axis families do not prevent existing major-axis calculations.
An unsupported family raises `NotImplementedError`; invalid panel dimensions
or yield stress raise `ValueError`. Recognising TFB here does not add a TFB
catalogue, geometry or slenderness implementation.

The flange/panel interpretation requires independent engineering verification.
This API does not assemble action resultants, shear-bending interactions or
torsion checks.

<!-- 

### *geometry* Module

:::steelas.member.geometry

### *material* Module

:::steelas.member.material

### *member* Module

:::steelas.member.member

### *slenderness* Module

:::steelas.member.slenderness -->

## Components

### *bolt* Module

:::steelas.component.bolt

### *plate* Module

:::steelas.component.plate

### *weld* Module

:::steelas.component.weld

## Connections

### *FEP* Module

:::steelas.connection.FEP

### *WSP* Module

:::steelas.connection.WSP