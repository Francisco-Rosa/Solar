# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the Solar addon.

# ***************************************************************************
# *   Copyright (c) 2019 Yorik van Havre <yorik@uncreated.net>              *
# *   Copyright (c) 2025 Francisco Rosa                                     *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENSE text file.                                 *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Lesser General Public License for more details.                   *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with FreeCAD; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

"""A sun black and white shadow module with independent widget window"""

import OfflineRenderingUtils
import FreeCAD
import FreeCADGui as Gui
from PySide import QtWidgets
from PySide.QtCore import QT_TRANSLATE_NOOP

LIGHT = None
VIEW = None

def clean_view_state():

    """Clean the shadow view."""

    global VIEW
    VIEW = None

def create_shadows_black_white():

    """Sets up the black and white shadow view from
    the currently active 3D view."""

    global LIGHT, VIEW

    obj = FreeCAD.ActiveDocument.SunProperties

    if VIEW is None:
        # Use only the active 3D view
        view = Gui.ActiveDocument.ActiveView
        if view is None:
            QtWidgets.QMessageBox.warning(
                None, "No 3D View",
                "No active 3D view found. "
                "Please select or open a 3D view "
                "for your document and try again."
                )
            return
        result = show_warning_dialog()
        if result == QtWidgets.QMessageBox.Ok:
            camera_string = view.getCamera()
            Gui.runCommand('Std_ViewCreate',0)
            view2 = Gui.ActiveDocument.ActiveView
            FreeCAD.ActiveDocument.SunLight.Visibility = False
            FreeCAD.ActiveDocument.Line.Visibility = False
            objs = [o for o in FreeCAD.ActiveDocument.Objects
                    if o.ViewObject.Visibility is True]
            cam = view.getCamera()
            scene = OfflineRenderingUtils.buildScene(objs)
            shadow_group = OfflineRenderingUtils.embedLight(scene,
                                        (-obj.SunLightPosition.x,
                                         -obj.SunLightPosition.y,
                                         -obj.SunLightPosition.z)
                                        )
            light = shadow_group.getChild(0)
            view2.setCamera(cam)
            view2.getViewer().setSceneGraph(shadow_group)
            view2.setNavigationType("Trackball")
            # Update view
            view2 = Gui.ActiveDocument.ActiveView
            view2.setCamera(camera_string)
            LIGHT = light
            VIEW = view2
            if obj.SunLightRepresentation is True:
                FreeCAD.ActiveDocument.SunLight.Visibility = True
                if obj.RayRepresentation is True:
                    FreeCAD.ActiveDocument.Line.Visibility = True
        else:
            print('Create BW shadows was canceled')

def update_shadow_direction(light = None):

    """Update shadow direction"""

    obj = FreeCAD.ActiveDocument.SunProperties
    try:
        light = LIGHT
        light.direction = (
            -obj.SunLightPosition.x,
            -obj.SunLightPosition.y,
            -obj.SunLightPosition.z)
    except Exception:
        pass

def show_warning_dialog():

    """Show warning dialog"""

    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle("BWShadow Save Warning")
    msg.setText(QT_TRANSLATE_NOOP('SunShadowBW',
        "This feature has not been fully tested yet! \n"
        "To prevent issues, save your file before opening it. \n"
        "For transparent surfaces, it is recommended \n"
        "to make them invisible before generating these shadows. \n"
        "\n"
        "Do you want to generate shadows now?"
    ))
    msg.setIcon(QtWidgets.QMessageBox.Warning)
    msg.setStandardButtons(
           QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
    result = msg.exec_()
    return result
