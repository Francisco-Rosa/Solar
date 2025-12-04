# ***************************************************************************
# *   Copyright (c) 2025 Francisco Rosa                                     *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
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

"""Gui initialization module for Solar Workbench."""

import os
import FreeCAD
import FreeCADGui as Gui
import SunProperties as sp

Gui.addLanguagePath(sp.LanguagePath)
Gui.updateLocale()

class Solar(Workbench):
    """The Solar Workbench."""

    translate = FreeCAD.Qt.translate

    MenuText = translate("InitGui", "Solar")
    ToolTip = translate("InitGui",
                        "Workbench to manage solar analysis and configurations")
    from SunProperties import IconPath
    Icon = os.path.join(IconPath, "SolarIcon.svg")

    def Initialize(self):
        """This function is executed when the workbench is first activated.
        It is executed once in a FreeCAD session followed by the Activated function.
        """
        # import here all the needed files that create your FreeCAD commands
        import SunPathAnimation
        import SunDialog
        import SkyDomes

        translate = FreeCAD.Qt.translate

        self.list1 = ['SunConfigurationDialog',
                       'StartSunPathAnimation',
                       'StopSunPathAnimation',
                       'CreateSkyDomes',
                       'ModifySkyDomes',
                       'DeleteSkyDomes'
                       ] # a list of command names created in the line above

        default_title1 = translate("InitGui", "Solar tools")
        self.appendToolbar(default_title1, self.list1) # creates the solar toolbar
        self.appendMenu(default_title1, self.list1) # creates the Solar tools menu


    def Activated(self):
        """This function is executed whenever the workbench is activated"""

        translate = FreeCAD.Qt.translate

        FreeCAD.Console.PrintMessage(translate(
                                     "InitGui","Solar Workbench loaded") + "\n")
        return

    def Deactivated(self):
        """This function is executed whenever the workbench is deactivated"""
        return

    def ContextMenu(self, recipient):
        """This function is executed whenever the user right-clicks on screen"""

        translate = FreeCAD.Qt.translate

        # "recipient" will be either "view" or "tree"
        default_title1 = translate("InitGui", "Solar tools")
        # add commands to the context menu
        self.appendContextMenu(default_title1, self.list1)

    def GetClassName(self):
        # This function is mandatory if this is a full Python workbench
        # This is not a template,
        # the returned string should be exactly "Gui::PythonWorkbench"
        return "Gui::PythonWorkbench"

Gui.addWorkbench(Solar())

#https://wiki.freecadweb.org/Workbench_creation
#https://wiki.freecad.org/Translating_an_external_workbench
