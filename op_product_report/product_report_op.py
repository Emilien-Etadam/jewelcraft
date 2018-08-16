# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2015-2018  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import os

import bpy
from bpy.types import Operator
from bpy.app.translations import pgettext_tip as _

from .. import var
from .report_data_collect import data_collect
from .report_data_format import data_format


class WM_OT_jewelcraft_product_report(Operator):
    bl_label = "JewelCraft Product Report"
    bl_description = "Save product report to text file"
    bl_idname = "wm.jewelcraft_product_report"

    def execute(self, context):
        prefs = context.user_preferences.addons[var.ADDON_ID].preferences
        data_raw = data_collect()
        data_fmt = data_format(data_raw)

        # Compose text datablock
        # ---------------------------

        if data_raw["warn"]:
            msgsf = [_(x) for x in data_raw["warn"]]
            sep = "—" * max(40, len(max(msgsf)) + 2)
            warns = "{}\n{}\n".format(_("WARNING"), sep)

            for msg in msgsf:
                warns += "-{}\n".format(_(msg))

            warns += "{}\n\n".format(sep)
            data_fmt = warns + data_fmt

        if "JewelCraft Product Report" in bpy.data.texts:
            txt = bpy.data.texts["JewelCraft Product Report"]
            txt.clear()
        else:
            txt = bpy.data.texts.new("JewelCraft Product Report")

        txt.write(data_fmt)
        txt.current_line_index = 0

        # Save to file
        # ---------------------------

        if prefs.product_report_save and bpy.data.is_saved:

            filepath = bpy.data.filepath
            filename = os.path.splitext(os.path.basename(filepath))[0]
            save_path = os.path.join(os.path.dirname(filepath), filename + " Report.txt")

            with open(save_path, "w", encoding="utf-8") as file:
                file.write(data_fmt)

        # Display
        # ---------------------------

        if prefs.product_report_display:

            bpy.ops.screen.userpref_show("INVOKE_DEFAULT")

            area = bpy.context.window_manager.windows[-1].screen.areas[0]
            area.type = "TEXT_EDITOR"

            space = area.spaces[0]
            space.text = txt

        elif data_raw["warn"] or prefs.product_report_save:

            def draw(self_local, context):
                for msg in data_raw["warn"]:
                    self_local.layout.label(_(msg), icon="ERROR")
                    self.report({"WARNING"}, _(msg))

                if prefs.product_report_save:

                    if bpy.data.is_saved:
                        msg = "Text file successfully created in the project folder"
                        report_icon = "FILE_TICK"
                        report_type = {"INFO"}
                    else:
                        msg = "Could not create text file, project folder does not exist"
                        report_icon = "ERROR"
                        report_type = {"WARNING"}

                    self_local.layout.label(_(msg), icon=report_icon)
                    self.report(report_type, _(msg))

            context.window_manager.popup_menu(draw, title=_("Product Report"))

        return {"FINISHED"}
