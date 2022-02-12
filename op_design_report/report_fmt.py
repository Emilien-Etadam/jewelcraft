# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2015-2022 Mikhail Rachinskiy

from math import pi
from collections.abc import Callable

from ..lib import gemlib, ringsizelib


def data_format(Report, _: Callable[[str], str]) -> None:
    _mm = _("mm")
    _g = _("g")

    if Report.gems:

        gems_fmt = []

        for (stone, cut, size), qty in sorted(
            Report.gems.items(),
            key=lambda x: (x[0][0], x[0][1], -x[0][2][1], -x[0][2][0]),
        ):

            w, l, h = size
            ct = gemlib.ct_calc(stone, cut, size)
            total_ct = round(ct * qty, 3)

            try:
                stonef = _(gemlib.STONES[stone].name)
                cutf = _(gemlib.CUTS[cut].name)
                xy_symmetry = gemlib.CUTS[cut].xy_symmetry
            except KeyError:
                stonef = stone
                cutf = cut
                xy_symmetry = False

            if xy_symmetry:
                sizef = str(l)
            else:
                sizef = f"{l} × {w}"

            gems_fmt.append((stonef, cutf, sizef, ct, qty, total_ct))

        Report.gems = gems_fmt

    if Report.materials:

        mats_fmt = []

        for mat_name, density, vol in Report.materials:
            weight = round(vol * density, 2)
            weightf = f"{weight} {_g}"

            mats_fmt.append((mat_name, weightf))

        Report.materials = mats_fmt

    if Report.notes:

        notes_fmt = []

        for item_type, name, values in Report.notes:

            if item_type == "DIMENSIONS":
                valuef = " × ".join([str(x) for x in values])
                valuef += f" {_mm}"

            elif item_type == "RING_SIZE":
                dia, size_format = values
                cir = dia * pi

                if size_format == "DIA":
                    valuef = f"{dia} {_mm}"
                elif size_format == "CIR":
                    valuef = f"{round(cir, 2)} {_mm}"
                else:
                    try:
                        valuef = ringsizelib.cir_to_size(cir, size_format)
                    except ValueError:
                        valuef = "[NO CORRESPONDING SIZE]"

            notes_fmt.append((name, valuef))

        Report.notes = notes_fmt
