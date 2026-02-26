# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the Solar addon.

################################################################################
#                                                                              #
#   Copyright (c) 2025 Francisco Rosa                                          #
#                                                                              #
#   This addon is free software; you can redistribute it and/or modify it      #
#   under the terms of the GNU Lesser General Public License as published      #
#   by the Free Software Foundation; either version 2.1 of the License, or     #
#   (at your option) any later version.                                        #
#                                                                              #
#   This addon is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                       #
#                                                                              #
#   See the GNU Lesser General Public License for more details.                #
#                                                                              #
#   You should have received a copy of the GNU Lesser General Public           #
#   License along with this addon. If not, see https://www.gnu.org/licenses    #
#                                                                              #
################################################################################

"""Create and modify a sky matrix as colored domes, subdivided into patches."""

import os
import math
import FreeCAD
import FreeCADGui as Gui
import Draft
from PySide import QtWidgets
from PySide.QtCore import QT_TRANSLATE_NOOP
from ladybug.analysisperiod import AnalysisPeriod
import freecad.Solar.SkyDomesDialog as SkyDomesDialog
import freecad.Solar.LBComponents as LBComponents

translate = FreeCAD.Qt.translate

LanguagePath = os.path.dirname(__file__) + '/translations'
Gui.addLanguagePath(LanguagePath)

#=================================================
# A. Main classes
#=================================================
SD = None
SD_NEW = False

class SkyDomes:

    """Visualize and configure Sky Domes in FreeCAD's 3D view."""

    def __init__(self,obj):
        obj.Proxy = self
        self.setProperties(obj)

    def setProperties(self,obj):

        """Gives the object properties to Sky Domes."""

        pl = obj.PropertiesList
        # 01 epw file and city
        if not "epw_path" in pl:
            obj.addProperty("App::PropertyFile",
                            "epw_path", "01_epw_path",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Path to epw file")
                            ).epw_path = ""
        if not "city" in pl:
            obj.addProperty("App::PropertyString",
                            "city", "01_epw_path",
                            QT_TRANSLATE_NOOP("App::Property",
                            "City")
                            ).city = ""
        if not "metadata" in pl:
            obj.addProperty("App::PropertyStringList",
                            "metadata", "01_epw_path",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Metadata")
                            ).metadata = []
        # 02 Model
        if not "model" in pl:
            obj.addProperty("App::PropertyEnumeration",
                            "model", "02_Model",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Sky dome model")
                            ).model = ("Tregenza", "Reinhart"
                            )
        # 03 Units
        if not "units" in pl:
            from freecad.Solar.LBComponents import RESUL_01, RESUL_02
            obj.addProperty("App::PropertyEnumeration",
                            "units", "03_Units",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Sky Domes units")
                            ).units = (f"00 - {RESUL_01}",
                                       f"01 - {RESUL_02}",
                            )
        # 04 Sky domes
        if not "direct_diffuse_domes" in pl:
            obj.addProperty("App::PropertyBool",
                            "direct_diffuse_domes", "04_SkyDomes",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Visualize direct and diffuse domes")
                            ).direct_diffuse_domes = True
        if not "total_values" in pl:
            obj.addProperty("App::PropertyFloatList",
                            "total_values", "04_SkyDomes",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Total sky dome values")
                            ).total_values = []
        if not "direct_values" in pl:
            obj.addProperty("App::PropertyFloatList",
                            "direct_values", "04_SkyDomes",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Direct sky dome values")
                            ).direct_values = []
        if not "diffuse_values" in pl:
            obj.addProperty("App::PropertyFloatList",
                            "diffuse_values", "04_SkyDomes",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Diffuse sky dome values")
                            ).diffuse_values = []
        if not "center_vectors" in pl:
            obj.addProperty("App::PropertyBool",
                            "center_vectors", "04_SkyDomes",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Visualize the center points (vectors) \n"
                            "of each patch dome")
                            ).center_vectors = False
        if not "vector_values" in pl:
            obj.addProperty("App::PropertyVectorList",
                            "vector_values", "04_SkyDomes",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Vectors values of each patch dome")
                            ).vector_values = []
        # 05 North
        if not "north" in pl:
            obj.addProperty("App::PropertyAngle",
                            "north", "05_North_angle",
                            QT_TRANSLATE_NOOP("App::Property",
                            "North angle (clockwise)")
                            ).north = 0
        # 06 Radius
        if not "radius" in pl:
            obj.addProperty("App::PropertyLength",
                            "radius", "06_Radius",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Sky Domes radius (mm)")
                            ).radius = 10000
        # 07 Position
        if not "position" in pl:
            obj.addProperty("App::PropertyVector",
                            "position", "07_Position",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Center position of the total sky dome "
                            "in mm (x, y, z)")
                            ).position = (0.0, 0.0, 0.0)
        # 08 Analysis period
        if not "start_year" in pl:
            obj.addProperty("App::PropertyInteger",
                            "start_year", "08_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The initial year of the analysis period")
                            ).start_year = 2025
        if not "end_year" in pl:
            obj.addProperty("App::PropertyInteger",
                            "end_year", "08_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The final year of the analysis period")
                            ).end_year = 2025
        if not "start_month" in pl:
            obj.addProperty("App::PropertyInteger",
                            "start_month", "08_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The initial month of the analysis period")
                            ).start_month = 1
        if not "end_month" in pl:
            obj.addProperty("App::PropertyInteger",
                            "end_month", "08_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The final month of the analysis period")
                            ).end_month = 12
        if not "start_day" in pl:
            obj.addProperty("App::PropertyInteger",
                            "start_day", "08_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The initial day of the analysis period")
                            ).start_day = 1
        if not "end_day" in pl:
            obj.addProperty("App::PropertyInteger",
                            "end_day", "08_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The final day of the analysis period")
                            ).end_day = 31
        if not "start_hour" in pl:
            obj.addProperty("App::PropertyInteger",
                            "start_hour", "08_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The initial hour of the analysis period")
                            ).start_hour = 0
        if not "end_hour" in pl:
            obj.addProperty("App::PropertyInteger",
                            "end_hour", "08_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The final hour of the analysis period")
                            ).end_hour = 23
        if not "timestep" in pl:
            obj.addProperty("App::PropertyEnumeration",
                            "timestep", "08_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Timestep per hour")
                            ).timestep = (1, 2, 3, 4, 5, 6, 10,
                                          12, 15, 20, 30, 60
                            )
        if not "leap_year" in pl:
            obj.addProperty("App::PropertyBool",
                            "leap_year", "08_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Leap year")
                            ).leap_year = False
        if not "transparency" in pl:
            obj.addProperty("App::PropertyPercent",
                            "transparency", "08_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Sky Domes transparency")
                            ).transparency = 20
        # 09 Legend
        if not "leg_title" in pl:
            obj.addProperty("App::PropertyString",
                            "leg_title", "09_Legend",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Sun analysis legend title.\n"
                            "It's read-only. It's get from the units.")
                            ).leg_title = ""
        if not "leg_position" in pl:
            obj.addProperty("App::PropertyVector",
                            "leg_position", "09_Legend",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Base left position of legend bar "
                            "in mm (x, y, z).\n"
                            "It is read only.")
                            ).leg_position = (0.0, 0.0, 0.0)
        if not "leg_width" in pl:
            obj.addProperty("App::PropertyFloat",
                            "leg_width", "09_Legend",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Width of legend bar in mm (x, y, z).\n"
                            "It is read only.")
                            ).leg_width = 1000
        if not "color_count" in pl:
            obj.addProperty("App::PropertyInteger",
                            "color_count", "09_Legend",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Number of segments of legend bar "
                            "(default = 11).")
                            ).color_count = 11
        if not "color_set" in pl:
            from freecad.Solar.LBComponents import COLORS_00, COLORS_01, COLORS_02, COLORS_03
            from freecad.Solar.LBComponents import COLORS_04, COLORS_05, COLORS_06, COLORS_07
            from freecad.Solar.LBComponents import COLORS_08, COLORS_09, COLORS_10, COLORS_11
            from freecad.Solar.LBComponents import COLORS_12, COLORS_13, COLORS_14, COLORS_15
            from freecad.Solar.LBComponents import COLORS_16, COLORS_17, COLORS_18, COLORS_19
            from freecad.Solar.LBComponents import COLORS_20, COLORS_21, COLORS_22, COLORS_23
            from freecad.Solar.LBComponents import COLORS_24, COLORS_25, COLORS_26, COLORS_27
            from freecad.Solar.LBComponents import COLORS_28, COLORS_29, COLORS_30, COLORS_31
            from freecad.Solar.LBComponents import COLORS_32
            obj.addProperty("App::PropertyEnumeration",
                            "color_set", "09_Legend",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Choose the legend color set.")
                            ).color_set = (
                            f"00 - {COLORS_00}",
                            f"01 - {COLORS_01}",
                            f"02 - {COLORS_02}",
                            f"03 - {COLORS_03}",
                            f"04 - {COLORS_04}",
                            f"05 - {COLORS_05}",
                            f"06 - {COLORS_06}",
                            f"07 - {COLORS_07}",
                            f"08 - {COLORS_08}",
                            f"09 - {COLORS_09}",
                            f"10 - {COLORS_10}",
                            f"11 - {COLORS_11}",
                            f"12 - {COLORS_12}",
                            f"13 - {COLORS_13}",
                            f"14 - {COLORS_14}",
                            f"15 - {COLORS_15}",
                            f"16 - {COLORS_16}",
                            f"17 - {COLORS_17}",
                            f"18 - {COLORS_18}",
                            f"19 - {COLORS_19}",
                            f"20 - {COLORS_20}",
                            f"21 - {COLORS_21}",
                            f"22 - {COLORS_22}",
                            f"23 - {COLORS_23}",
                            f"24 - {COLORS_24}",
                            f"25 - {COLORS_25}",
                            f"26 - {COLORS_26}",
                            f"27 - {COLORS_27}",
                            f"28 - {COLORS_28}",
                            f"29 - {COLORS_29}",
                            f"30 - {COLORS_30}",
                            f"31 - {COLORS_31}",
                            f"32 - {COLORS_32}",
                            )

class SkyDomesViewProvider:

    """A View Provider for the Sky Domes object"""

    def __init__(self, obj):
        obj.Proxy = self

    def getIcon(self):
        __dir__ = os.path.dirname(__file__)
        return __dir__ + '/icons/SkyDomesIcon.svg'

class CreateSkyDomes:

    """Create a sky matrix as colored domes, subdivided into patches."""

    def QT_TRANSLATE_NOOP(self, text):
        return text

    def GetResources(self):
        __dir__ = os.path.dirname(__file__)
        return {'Pixmap': __dir__ + '/icons/CreateSkyDomesIcon.svg',
                'MenuText': QT_TRANSLATE_NOOP('CreateSkyDomes',
                                              'Create Sky Domes'),
                'ToolTip': QT_TRANSLATE_NOOP('CreateSkyDomes',
                'Click this button to open the dialog '
                'and configure the data for new Sky Domes.')}

    def IsActive(self):
        if Gui.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        activated_create_sky_domes(self)

class ModifySkyDomes:

    """Modify a set of Sky Domes."""

    def QT_TRANSLATE_NOOP(self, text):
        return text

    def GetResources(self):
        __dir__ = os.path.dirname(__file__)
        return {'Pixmap': __dir__ + '/icons/ModifySkyDomesIcon.svg',
                'MenuText': QT_TRANSLATE_NOOP('ModifySkyDomes', 'Modify Sky Domes'),
                           'ToolTip': QT_TRANSLATE_NOOP('ModifySkyDomes',
                            'Select a Sky Domes group, click this button to \n'
                            'open the dialog and modify its configuration. \n'
                            'Please note, this only works if the original \n'
                            'group structure is preserved!')}

    def IsActive(self):
        if Gui.ActiveDocument:
            try:
                FreeCAD.ActiveDocument.findObjects(Name = "SkyDomes")[0].Name
                return True
            except:
                pass
        else:
            return False

    def Activated(self):
        activated_modify_sky_domes(self)

class DeleteSkyDomes:

    """Delete a set of Sky Domes."""

    def QT_TRANSLATE_NOOP(self, text):
        return text

    def GetResources(self):
        __dir__ = os.path.dirname(__file__)
        return {'Pixmap': __dir__ + '/icons/DeleteSkyDomesIcon.svg',
                'MenuText': QT_TRANSLATE_NOOP('DeleteSkyDomes', 'Delete Sky Domes'),
                             'ToolTip': QT_TRANSLATE_NOOP('DeleteSkyDomes',
                             'Select a Sky Domes group to delete.\n'
                             'Be careful, you will not be able to \n'
                             'undo this action!')}
    def IsActive(self):
        if Gui.ActiveDocument:
            try:
                FreeCAD.ActiveDocument.findObjects(Name = "SkyDomes")[0].Name
                return True
            except:
                pass
        else:
            return False
    def Activated(self):
        activated_delete_sky_domes(self)

def activated_create_sky_domes(self):

    """Create the Sky Domes"""

    global SD
    global SD_NEW
    folder = FreeCAD.ActiveDocument.addObject(
             'App::DocumentObjectGroupPython',
             'SkyDomes')
    SkyDomes(folder)
    SkyDomesViewProvider(folder.ViewObject)
    SD = folder
    #print(f"create sky domes: SD = {SD.Name}")
    SD_NEW = True
    SkyDomesDialog.open_sky_domes_configuration()

def activated_modify_sky_domes(self):

    """Modify the Sky Domes selected"""

    global SD
    global SD_NEW
    SD_NEW = False
    SD = select_sky_domes()
    if SD is not None:
        print(f"activated modify sky domes: SD = {SD.Name}")
        SkyDomesDialog.open_sky_domes_configuration()
    else:
        FreeCAD.Console.PrintMessage(translate("SkyDomes",
            "To modify a set of Sky Domes, "
            "first you must select one!") + '\n')

def activated_delete_sky_domes(self):

    """Delete the Sky Domes selected"""

    try:
        selection = select_sky_domes()
        if selection is not None:
            print(f"activated delete sky domes: SD = {selection.Name}")
            delete_sky_domes(selection)
        else:
            FreeCAD.Console.PrintMessage(translate("SkyDomes",
             "To delete a set of Sky Domes, "
             "first you must select one!") + '\n')
    except Exception:
        FreeCAD.Console.PrintMessage(translate("SkyDomes",
            "To delete a set of Sky Domes, "
            "first you must select one!") + '\n')

def select_sky_domes():

    """Select a Sky Domes"""

    SD = None
    selection = []
    selection = Gui.Selection.getSelection()
    try:
        selection[0]
        if selection[0].Name[0:8] == "SkyDomes":
            SD = selection[0]
            return SD
        else:
            FreeCAD.Console.PrintMessage(translate("SkyDomes",
                "Warning: The objects selected are not Sky Domes!") + '\n')
    except:
        FreeCAD.Console.PrintMessage(translate("SkyDomes",
                              "There is no selection!") + '\n')

#=================================================
# B. Sky domes
#=================================================

def get_sky_dome_forms(center_dome = None,
                        radius = None,
                        north = None,
                        sky_dome_model = ""
                        ):

    """Get Sky Domes geometry"""

    doc = FreeCAD.ActiveDocument
    TREGENZA_PATCHES_PER_ROW = (30, 30, 24, 24, 18, 12, 6)
    REINHART_PATCHES_PER_ROW = (60, 60, 60, 60, 48, 48, 48,
                                48, 36, 36, 24, 24, 12, 12)

    # model
    if sky_dome_model == "Tregenza":
        model = TREGENZA_PATCHES_PER_ROW
        ang_model = 12
    if sky_dome_model == "Reinhart":
        model = REINHART_PATCHES_PER_ROW
        ang_model = 6.2
    surfaces = []
    rings = None
    rings = len(model)
    radius_init = 1000
    create_surfaces =  False
    dome_compound = None
    # create groups
    try:
        doc.SD_Construction_Group
        dome_const_group = doc.SD_Construction_Group
    except Exception:
        dome_const_group = doc.addObject('App::DocumentObjectGroup',
                                         'SD_Construction_Group')
        dome_const_group.Label = translate('SkyDomes',
                                         'SD Constructions Group')
    if sky_dome_model == "Tregenza":
        try:
            doc.Model_Tregenza
            dome_model_group = doc.Model_Tregenza
            dome_compound = doc.SD_Tregenza
            create_surfaces = False
        except Exception:
            dome_model_group = doc.addObject('App::DocumentObjectGroup',
                                             'Model_Tregenza')
            dome_model_group.Label = translate('SkyDomes',
                                             'Model Tregenza')
            doc.getObject(dome_const_group.Name).addObject(dome_model_group)
            create_surfaces = True
    if sky_dome_model == "Reinhart":
        try:
            doc.Model_Reinhart
            dome_model_group = doc.Model_Reinhart
            dome_compound = doc.SD_Reinhart
            create_surfaces = False
        except Exception:
            dome_model_group = doc.addObject('App::DocumentObjectGroup',
                                             'Model_Reinhart')
            dome_model_group.Label = translate('SkyDomes',
                                             'Model Reinhart')
            doc.getObject(dome_const_group.Name).addObject(dome_model_group)
            create_surfaces = True
    # Get the patch surfaces
    if create_surfaces is True:
        for ring in range(rings): # get rings
            # Obtain the two horizontal and vertical arcs
            # Obtain the arcs of the first patch of the ring
            # get arcs
            av1 = ang_model * ring
            z1 = radius_init * math.sin(math.radians(av1))
            av2 = ang_model * (ring + 1)
            z2 = radius_init * math.sin(math.radians(av2))
            r = radius_init
            r1 = radius_init * math.cos(math.radians(av1))
            r2 = radius_init * math.cos(math.radians(av2))
            # get horizontal arcs
            segments = model[ring] # get segments
            ah1 = 90 - 360/segments/2
            ah2 = (360 / segments) + ah1
            pl = FreeCAD.Placement()
            pl.Base = FreeCAD.Vector(0.0,0.0,0.0)
            pl1 = FreeCAD.Placement()
            pl1.Base = FreeCAD.Vector(0, 0, z1)
            pl.Rotation.setYawPitchRoll(90,0,90)
            pl1.Rotation.setYawPitchRoll(0, 0,0)
            ch1 = Draft.make_circle(
                    radius=r1, placement=pl1, face=False,
                    startangle=ah1,
                    endangle=ah2, support=None
                    )
            doc.getObject(dome_model_group.Name).addObject(ch1)
            pl2 = FreeCAD.Placement()
            pl2.Base = FreeCAD.Vector(0, 0, z2)
            pl2.Rotation.setYawPitchRoll(0, 0, 0)
            ch2 = Draft.make_circle(
                    radius=r2, placement=pl2, face=False,
                    startangle=ah1,
                    endangle=ah2, support=None
                    )
            doc.getObject(dome_model_group.Name).addObject(ch2)
            # get vertical arcs
            pl.Rotation.setYawPitchRoll(ah1, 0, 90)
            cv1 = Draft.make_circle(
                    radius=r, placement=pl, face=False,
                     startangle=av1,
                    endangle=av2, support=None
                    )
            doc.getObject(dome_model_group.Name).addObject(cv1)
            pl.Rotation.setYawPitchRoll(ah2, 0, 90)
            cv2 = Draft.make_circle(
                    radius=r, placement=pl, face=False,
                    startangle=av1,
                    endangle=av2, support=None
                    )
            doc.getObject(dome_model_group.Name).addObject(cv2)
            # Obtain the surface of the first patch of the ring
            fill_surface = doc.addObject("Surface::GeomFillSurface",
                                         "Surface")
            fill_surface.BoundaryList = [ch1, ch2, cv1, cv2]
            fill_surface.FillType = "Coons"
            obj_surf = FreeCAD.ActiveDocument.getObject(fill_surface.Name)
            surfaces.append(obj_surf)
            # Clone and rotate the surfaces of the remaining patches of the ring
            for i in range(segments - 1):
                clone_obj = Draft.make_clone(
                            FreeCAD.ActiveDocument.getObject(
                            fill_surface.Name))
                ah = -(ah2 - ah1) * (i + 1) # rotate clock wise!
                Draft.rotate([FreeCAD.ActiveDocument.getObject(
                            clone_obj.Name)],
                            ah, FreeCAD.Vector(0.0,0.0,0.0),
                            axis=FreeCAD.Vector(0.0, 0.0, 1.0),
                            copy=False
                            )
                surfaces.append(clone_obj)
        # Obtain the vertical arc for the zenith
        av1 = ang_model * rings
        av2 = av1 + ang_model/2
        r = radius_init
        # get vertical arc
        pl.Rotation.setYawPitchRoll(90,0,90)
        cv1 = None
        cv1 = Draft.make_circle(
                radius=r, placement=pl, face=False,
                 startangle=av1,
                endangle=av2, support=None
                )
        doc.getObject(cv1.Name).Visibility = False
        # Create the zenith surface
        if sky_dome_model == "Tregenza":
            cap = doc.addObject("Part::Revolution","Revolve_tr")
            doc.Revolve_tr.Source = doc.getObject(cv1.Name)
            doc.Revolve_tr.Axis = (0.0,0.0,1.0)
            doc.Revolve_tr.Base = (0.0,0.0,0.0)
            doc.Revolve_tr.Angle = 360.0
            doc.Revolve_tr.Solid = False
            doc.Revolve_tr.AxisLink = None
            doc.Revolve_tr.Symmetric = False
        if sky_dome_model == "Reinhart":
            cap = doc.addObject("Part::Revolution","Revolve_re")
            doc.Revolve_re.Source = doc.getObject(cv1.Name)
            doc.Revolve_re.Axis = (0.0,0.0,1.0)
            doc.Revolve_re.Base = (0.0,0.0,0.0)
            doc.Revolve_re.Angle = 360.0
            doc.Revolve_re.Solid = False
            doc.Revolve_re.AxisLink = None
            doc.Revolve_re.Symmetric = False
        surfaces.append(cap)
        # Join all parts (patches) - compound
        if sky_dome_model == "Tregenza":
            dome = FreeCAD.activeDocument().addObject(
                                           "Part::Compound",
                                           "SD_Tregenza")
            dome.Label = translate("SkyDomes",
                                   "SD Tregenza")
            dome.Links = surfaces
        if sky_dome_model == "Reinhart":
            dome = FreeCAD.activeDocument().addObject(
                                           "Part::Compound",
                                           "SD_Reinhart")
            dome.Label = translate("SkyDomes",
                                   "SD Reinhart")
            dome.Links = surfaces
        doc.getObject(dome_model_group.Name).addObject(dome)
        # Group visibility
        doc.getObject(dome_const_group.Name).Visibility = False
        doc.getObject(dome_model_group.Name).Visibility = False
        dome_compound = dome

    # Create clones for total, direct and diffuse values
    scale = radius/radius_init
    # total values - clone1
    # total group
    dome_total_group = doc.addObject("App::DocumentObjectGroup",
                                     "Total_Sky_Dome_Group")
    dome_total_group.Label = translate("SkyDomes",
                                           "Total Sky Dome Group")
    # total values - clone1
    dome_total = LBComponents.get_analysis_clone(compound = dome_compound,
                           obj_label = translate(
                                            "SkyDomes",
                                            "Total Sky Dome"),
                           analysis_group = dome_total_group
                           )
    # clone total position, rotation and scale
    pl1 = FreeCAD.Placement()
    pl1.Base = FreeCAD.Vector(center_dome)
    pl1.Rotation.setYawPitchRoll(-north, 0, 0)
    dome_total.Placement = pl1
    dome_total.Scale = (scale, scale, scale)
    # direct values - clone2
    # direct group
    dome_direct_group = doc.addObject('App::DocumentObjectGroup',
                                      'Direct_Sky_Dome_Group')
    dome_direct_group.Label = translate("SkyDomes",
                                        "Direct Sky Dome Group")
    # direct values - clone2
    dome_direct = LBComponents.get_analysis_clone(compound = dome_compound,
                           obj_label = translate(
                                            "SkyDomes",
                                            "Direct Sky Dome"),
                           analysis_group = dome_direct_group
                           )
    # clone direct position, rotation and scale
    pl2 = FreeCAD.Placement()
    pl2.Base = FreeCAD.Vector(radius*3 + center_dome[0],
                              center_dome[1], center_dome[2])
    pl2.Rotation.setYawPitchRoll(-north, 0, 0)
    dome_direct.Placement = pl2
    dome_direct.Scale = (scale, scale, scale)
    # diffuse values - clone3
    dome_diffuse_group = doc.addObject('App::DocumentObjectGroup',
                                       'Diffuse_Sky_Dome_Group')
    dome_diffuse_group.Label = translate("SkyDomes",
                                         "Diffuse Sky Dome Group")
    # diffuse values - clone3
    dome_diffuse = LBComponents.get_analysis_clone(compound = dome_compound,
                           obj_label = translate(
                                            "SkyDomes",
                                            "Diffuse Sky Dome"),
                           analysis_group = dome_diffuse_group
                           )
    # clone diffuse position, rotation and scale
    pl3 = FreeCAD.Placement()
    pl3.Base = FreeCAD.Vector(radius*6 + center_dome[0],
                              center_dome[1], center_dome[2])
    pl3.Rotation.setYawPitchRoll(-north, 0, 0)
    dome_diffuse.Placement = pl3
    dome_diffuse.Scale = (scale, scale, scale)
    # Save and return data
    sky_domes = []
    sky_domes.append(dome_total_group) # [0]
    sky_domes.append(dome_direct_group) # [1]
    sky_domes.append(dome_diffuse_group) # [2]
    FreeCAD.ActiveDocument.recompute()
    return sky_domes

def modify_sky_dome_forms(sky_domes_group = None,
                           center_dome = None,
                           radius = None,
                           north = None,
                           model = "",
                           transparency = 0,
                           center_vectors = False
                           ):

    """Modify Sky Domes geometry"""

    # Get initial objects and necessary data
    doc = FreeCAD.ActiveDocument
    dome_total = sky_domes_group.Group[0].Group[0]
    dome_direct = sky_domes_group.Group[1].Group[0]
    dome_diffuse = sky_domes_group.Group[2].Group[0]

    # Update position and rotation of total, direct and diffuse clones
    # Update the clone 1
    scale = radius/1000
    pl1 = FreeCAD.Placement()
    pl1.Base = FreeCAD.Vector(center_dome)
    pl1.Rotation.setYawPitchRoll(-north, 0, 0)
    dome_total.Placement = pl1
    dome_total.Scale = (scale, scale, scale)
    dome_total.ViewObject.Transparency =  transparency
    # Update distance between original and clone2
    pl2 = FreeCAD.Placement()
    pl2.Base = FreeCAD.Vector(radius*3 + center_dome[0],
                              center_dome[1], center_dome[2])
    pl2.Rotation.setYawPitchRoll(-north, 0, 0)
    dome_direct.Placement = pl2
    dome_direct.Scale = (scale, scale, scale)
    dome_direct.ViewObject.Transparency =  transparency
    # Update distance between original and clone3
    pl3 = FreeCAD.Placement()
    pl3.Base = FreeCAD.Vector(radius*6 + center_dome[0],
                              center_dome[1], center_dome[2])
    pl3.Rotation.setYawPitchRoll(-north, 0, 0)
    dome_diffuse.Placement = pl3
    dome_diffuse.Scale = (scale, scale, scale)
    dome_diffuse.ViewObject.Transparency =  transparency
    # Update center vectors visibility
    if model == "Tregenza" and hasattr(doc, 'SD_Vectors_TR'):
        doc.SD_Vectors_TR.Visibility = center_vectors
    if model == "Reinhart" and hasattr(doc, 'SD_Vectors_RE'):
        doc.SD_Vectors_RE.Visibility = center_vectors
    FreeCAD.ActiveDocument.recompute()

def apply_sky_dome_values(sky_domes_group = None,
                          total_values = None,
                          direct_values = None,
                          diffuse_values = None,
                          leg_colors = None,
                          label = "",
                          transparency = 0
                          ):

    """Apply and modify values and colors"""

    dome_total = sky_domes_group.Group[0].Group[0]
    dome_direct = sky_domes_group.Group[1].Group[0]
    dome_diffuse = sky_domes_group.Group[2].Group[0]
    # Colors and values
    sky_domes_group.Label = label
    total_values = total_values
    direct_values = direct_values
    diffuse_values = diffuse_values
    colors_seq1 = []
    colors_seq2 = []
    colors_seq3 = []
    colors_seq1 = LBComponents.get_face_colors(
                            sun_analysis_results = total_values,
                            domain = total_values,
                            leg_colors = leg_colors
                            )
    colors_seq2 = LBComponents.get_face_colors(
                            sun_analysis_results = direct_values,
                            domain = total_values,
                            leg_colors = leg_colors
                            )
    colors_seq3 = LBComponents.get_face_colors(
                            sun_analysis_results = diffuse_values,
                            domain = total_values,
                            leg_colors = leg_colors
                            )
    # Apply the colors of each patch in sky domes clones
    LBComponents.apply_color_faces(obj = dome_total,
                          face_colors = colors_seq1,
                          transparency = transparency)
    LBComponents.apply_color_faces(obj = dome_direct,
                          face_colors = colors_seq2,
                          transparency = transparency)
    LBComponents.apply_color_faces(obj = dome_diffuse,
                          face_colors = colors_seq3,
                          transparency = transparency)
    FreeCAD.ActiveDocument.recompute()

def get_center_vectors(center = (0.0, 0.0, 0.0),
                       radius = 1000,
                       center_vectors = False,
                       vector_values = None,
                       angle = 0,
                       model = "",
                       ):

    """Get center vectors"""

    doc = FreeCAD.ActiveDocument
    #vector group
    if model == "Tregenza":
        dome_vectors_group = doc.addObject('App::DocumentObjectGroup',
                                           'Vectors_TR')
        dome_vectors_group.Label = translate("SkyDomes",
                                             "Vectors TR")
    if model == "Reinhart":
        dome_vectors_group = doc.addObject('App::DocumentObjectGroup',
                                           'Vectors_RE')
        dome_vectors_group.Label = translate("SkyDomes",
                                             "Vectors RE")
    #modify scale and position
    for i in range(len(vector_values)):
        point = Draft.make_point(
                    float(vector_values[i][0]*radius) + center[0],
                    float(vector_values[i][1]*radius) + center[1],
                    float(vector_values[i][2]*radius) + center[2])
        doc.getObject(dome_vectors_group.Name).addObject(point)
    FreeCAD.ActiveDocument.recompute()
    points = dome_vectors_group.Group
    #rotate
    for i in range(len(points)):
        Draft.rotate([points[i]], angle, center,
                     axis=FreeCAD.Vector(0.0, 0.0, 1.0),
                     copy=False)
    doc.getObject(dome_vectors_group.Name).Visibility = center_vectors
    return dome_vectors_group
    FreeCAD.ActiveDocument.recompute()

def modify_center_vectors(vectors_group = None,
                          center = (0.0, 0.0, 0.0),
                          radius = 1000,
                          center_vectors = False,
                          vector_values = None,
                          angle = 0,
                          model = "",
                          ):

    """modify center vectors"""

    points = vectors_group.Group
    for i in range(len(points)):
        points[i].X = float(vector_values[i][0]*radius) + center[0]
        points[i].Y = float(vector_values[i][1]*radius) + center[1]
        points[i].Z = float(vector_values[i][2]*radius) + center[2]
    FreeCAD.ActiveDocument.recompute()
    for i in range(len(points)):
        Draft.rotate([points[i]], angle, center,
                      axis=FreeCAD.Vector(0.0, 0.0, 1.0),
                      copy=False)
    vectors_group.Visibility = center_vectors
    FreeCAD.ActiveDocument.recompute()

#=================================================
# C. Groups
#=================================================

def manage_sky_dome_groups(domes_group = None,
                           dome_total_group = None,
                           dome_direct_group = None,
                           dome_diffuse_group = None,
                           leg_bar_group = None,
                           total_compass_group = None,
                           direct_compass_group = None,
                           diffuse_compass_group = None,
                           leg_total_group = None,
                           leg_direct_group = None,
                           leg_diffuse_group = None,
                           dome_vectors_group = None,
                           direct_diffuse_domes = False
                           ):

    """Manage the Sky Domes groups"""

    doc = FreeCAD.ActiveDocument
    # Total compass group to total sky dome group
    doc.getObject(dome_total_group.Name).addObject(total_compass_group)
    # Total leg group to total sky dome group
    doc.getObject(dome_total_group.Name).addObject(leg_total_group)
    # Direct compass group to direct sky dome group
    doc.getObject(dome_direct_group.Name).addObject(direct_compass_group)
    # Direct leg group to direct sky dome group
    doc.getObject(dome_direct_group.Name).addObject(leg_direct_group)
    # Diffuse compass group to diffuse sky dome group
    doc.getObject(dome_diffuse_group.Name).addObject(diffuse_compass_group)
    # Diffuse leg group to diffuse sky dome group
    doc.getObject(dome_diffuse_group.Name).addObject(leg_diffuse_group)
    FreeCAD.ActiveDocument.recompute()
    # vectors group to sky dome total leg group
    if dome_vectors_group is not None:
        doc.getObject(dome_total_group.Name).addObject(dome_vectors_group)
    # groups to main group
    # Sky dome total group to sky domes group
    doc.getObject(domes_group.Name).addObject(dome_total_group)
    # Sky dome direct group to sky domes group
    doc.getObject(domes_group.Name).addObject(dome_direct_group)
    doc.getObject(dome_direct_group.Name).Visibility = direct_diffuse_domes
    # Sky dome diffuse group to sky domes group
    doc.getObject(domes_group.Name).addObject(dome_diffuse_group)
    doc.getObject(dome_diffuse_group.Name).Visibility = direct_diffuse_domes
     # Legend bar group to sky domes group
    doc.getObject(domes_group.Name).addObject(leg_bar_group)
    FreeCAD.ActiveDocument.recompute()
    return domes_group

#=================================================
# D. Main functions
#=================================================

def create_sky_domes():

    """Create a complete Sky Domes set"""

    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage("create sky domes: " + translate("SkyDomes",
            "Could not get Sky Domes properties!") + "\n")
        return
    global SD_NEW
    # epw_path
    if SD.epw_path != "":
        epw_path = SD.epw_path
        if not epw_path or not os.path.isfile(epw_path):
            FreeCAD.Console.PrintMessage(translate("SkyDomes",
                "To create Sky Domes you must provide a valid epw file!") + '\n')
            return
    else:
        FreeCAD.Console.PrintMessage(translate("SkyDomes",
            "To create Sky Domes, you need to indicate an epw file!") + '\n')
        return
    #period
    period = None
    period = AnalysisPeriod(SD.start_month,
                            SD.start_day,
                            SD.start_hour,
                            SD.end_month,
                            SD.end_day,
                            SD.end_hour,
                            #int(SD.timestep),
                            1,
                            SD.leap_year
                            )
    # Getting sky domes
    print ("getting Sky Domes...")
    sky_domes = get_sky_dome_forms(center_dome = SD.position,
                              radius = float(SD.radius),
                              north = float(SD.north),
                              sky_dome_model = SD.model
                              )
    # Getting compass
    print ("compass_data...")
    compass_data = LBComponents.get_compass_group(center = SD.position,
                               radius = float(SD.radius),
                               north = float(SD.north),
                               variation_angle = 10,
                               total_group = sky_domes[0],
                               direct_group = sky_domes[1],
                               diffuse_group = sky_domes[2],
                               deltx = None
                               )
    # Getting values
    print ("getting Sky Domes values...")
    high_density = False
    if SD.model == "Reinhart":
        high_density = True
    irradiance = False
    if SD.units[0:2] == "01":
        irradiance = True
    sky_dome_values = LBComponents.get_sky_matrix_dome_values(epw_path,
                                          period,
                                          high_density = high_density,
                                          plot_irradiance = irradiance,
                                          timestep = int(SD.timestep),
                                          center_vectors = SD.center_vectors,
                                          ground_reflectance = 0.2
                                          )
    SD.total_values = sky_dome_values[0]
    SD.direct_values = sky_dome_values[1]
    SD.diffuse_values = sky_dome_values[2]
    SD.vector_values = sky_dome_values[3]
    SD.metadata = sky_dome_values[4]
    # Getting legend bar
    print("getting legend bar...")
    SD.leg_width = float(SD.radius*2/SD.color_count)
    if SD.direct_diffuse_domes is True:
        bar_x = float(SD.radius) * 7.3 + float(SD.position[0])
    else:
        bar_x = float(SD.radius) * 1.3 + float(SD.position[0])
    bar_y = -float(SD.radius) + float(SD.position[1])
    SD.leg_position = (bar_x, bar_y, 0.0)
    legend = LBComponents.get_modify_legend_bar(bar_obj = None,
                              text_leg_group = None,
                              #title = SD.units,
                              title = SD.leg_title,
                              values = SD.total_values,
                              position = SD.leg_position,
                              seg_height = SD.leg_width,
                              seg_width = SD.leg_width,
                              seg_count = SD.color_count,
                              color_leg_set = int(SD.color_set[0:2])
                              )
    leg_group = legend[0]
    color_rgb_leg = legend[1]
    # Getting center vectors
    if SD.center_vectors is True:
        print ("getting center values...")
        vectors_group = get_center_vectors(center = SD.position,
                               radius = float(SD.radius),
                               center_vectors = SD.center_vectors,
                               vector_values = SD.vector_values,
                               angle = -float(SD.north),
                               model = SD.model
                               )
    else:
        vectors_group = None

    print ("getting main legends...")
    pos1 = (-float(SD.radius) + SD.position[0],
            -float(SD.radius)*1.4 + SD.position[1],
            SD.position[2])
    pos2 = (float(SD.radius)*2 + SD.position[0],
            -float(SD.radius)*1.4 + SD.position[1],
            SD.position[2])
    pos3 = (float(SD.radius)*5 + SD.position[0],
            -float(SD.radius)*1.4 + SD.position[1],
             SD.position[2])
    main_leg_groups = LBComponents.get_main_legends(pos1,
                                           pos2,
                                           pos3,
                                           #units = SD.units,
                                           units = SD.leg_title,
                                           metadata = SD.metadata,
                                           text_high = float(SD.radius)/10,
                                           )
    # Managing groups
    print("managing group...")
    manage_sky_dome_groups(domes_group = SD,
                           dome_total_group = sky_domes[0],
                           dome_direct_group = sky_domes[1],
                           dome_diffuse_group = sky_domes[2],
                           leg_bar_group = leg_group,
                           total_compass_group = compass_data[0],
                           direct_compass_group = compass_data[1],
                           diffuse_compass_group = compass_data[2],
                           leg_total_group = main_leg_groups[0],
                           leg_direct_group = main_leg_groups[1],
                           leg_diffuse_group = main_leg_groups[2],
                           dome_vectors_group = vectors_group,
                           direct_diffuse_domes = SD.direct_diffuse_domes
                           )
    # Applying sky domes values
    print ("applying values...")
    apply_sky_dome_values(sky_domes_group = SD,
                          total_values = SD.total_values,
                          direct_values = SD.direct_values,
                          diffuse_values = SD.diffuse_values,
                          leg_colors = color_rgb_leg,
                          label = translate("SkyDomes",
                                                    "Sky Domes {} {}").format(
                                                           SD.city, SD.units),
                          transparency = SD.transparency
                          )
    FreeCAD.Console.PrintMessage(translate(
                                'SkyDomes',
                                'Sky Domes created! \n'
                                'Do not modify their original structure of groups \n'
                                'to make possible further adjustments.'
                                 ) + '\n')
    SD_NEW = False
    Gui.SendMsgToActiveView("ViewFit")
    Gui.runCommand('Std_ViewGroup',2)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(SD)
    FreeCAD.ActiveDocument.recompute()

def modify_sky_domes(forms = False, values = False):

    """Modify a complete Sky Domes set"""

    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage("modify sky domes: " + translate("SkyDomes",
            "Sky Domes properties not found!") + "\n")
        return
    global SD_NEW
    # epw_path
    if SD.epw_path != "":
        epw_path = SD.epw_path
        if not epw_path or not os.path.isfile(epw_path):
            FreeCAD.Console.PrintMessage(translate("SkyDomes",
                "To create Sky Domes you must provide a valid epw file!") + '\n')
            return
    else:
        FreeCAD.Console.PrintMessage(translate("SkyDomes",
            "To create Sky Domes, you need to indicate an epw file!") + '\n')
        return
    #period
    period = None
    period = AnalysisPeriod(SD.start_month,
                            SD.start_day,
                            SD.start_hour,
                            SD.end_month,
                            SD.end_day,
                            SD.end_hour,
                            #int(SD.timestep),
                            1,
                            SD.leap_year
                            )
    if forms is True:
        update_forms()
        print("updated forms!")
    if values is True:
        update_values(epw_path, period)
        print("updated values!")
    Gui.SendMsgToActiveView("ViewFit")
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(SD)
    FreeCAD.ActiveDocument.recompute()

def update_forms():

    """Update a complete Sky Domes set geometry"""

    doc = FreeCAD.ActiveDocument
    try:
        SD != None
    except Exception as e:
        FreeCAD.Console.PrintMessage("update forms: " + translate("SkyDomes",
            "Could not get Sky Domes:\n{}").format(e) + '\n')
        return
    modify_sky_dome_forms(sky_domes_group = SD,
                           center_dome = SD.position,
                           radius = float(SD.radius),
                           north = float(SD.north),
                           model = SD.model,
                           transparency = SD.transparency,
                           center_vectors = SD.center_vectors
                           )
    try:
        SD.Group[0].Group[3]
        print ("modifying center values...")
        modify_center_vectors(vectors_group = SD.Group[0].Group[3],
                              center = SD.position,
                              radius = float(SD.radius),
                              center_vectors = SD.center_vectors,
                              vector_values = SD.vector_values,
                              angle = -float(SD.north),
                              model = SD.model
                              )
    except Exception:
        if SD.center_vectors is True:
            print ("getting center values...")
            vectors_group = get_center_vectors(center = SD.position,
                               radius = float(SD.radius),
                               center_vectors = SD.center_vectors,
                               vector_values = SD.vector_values,
                               angle = -float(SD.north),
                               model = SD.model
                               )
            doc.getObject(SD.Group[0].Name).addObject(vectors_group)
    LBComponents.modify_compass(center = SD.position,
                       radius = float(SD.radius),
                       north = float(SD.north),
                       variation_angle = 10,
                       sky_domes_group = SD,
                       sun_analysis_group = None,
                       deltx = None
                       )
    SD.leg_width = float(SD.radius*2/SD.color_count)
    if SD.direct_diffuse_domes is True:
        bar_x = float(SD.radius) * 7.3 + float(SD.position[0])
    else:
        bar_x = float(SD.radius) * 1.3 + float(SD.position[0])
    bar_y = -float(SD.radius) + float(SD.position[1])
    SD.leg_position = (bar_x, bar_y, 0.0)
    LBComponents.get_modify_legend_bar(bar_obj = SD.Group[3].Group[0],
                              text_leg_group = SD.Group[3].Group[1],
                              #title = SD.units,
                              title = SD.leg_title,
                              values = SD.total_values,
                              position = SD.leg_position,
                              seg_height = SD.leg_width,
                              seg_width = SD.leg_width,
                              seg_count = SD.color_count,
                              color_leg_set = int(SD.color_set[0:2])
                              )
    x1 = SD.position[0] - float(SD.radius)
    x2 = SD.position[0] + float(SD.radius)*2
    x3 = SD.position[0] + float(SD.radius)*5
    y = SD.position[1] - float(SD.radius)*1.4
    z = SD.position[2]
    pos1 = (x1, y, z)
    pos2 = (x2, y, z)
    pos3 = (x3, y, z)
    LBComponents.modify_main_legends(
                             main_leg1 = SD.Group[0].Group[2].Group[0],
                             main_leg2 = SD.Group[1].Group[2].Group[0],
                             main_leg3 = SD.Group[2].Group[2].Group[0],
                             pos1 = pos1,
                             pos2 = pos2,
                             pos3 = pos3,
                             unit = SD.leg_title,
                             metadata = SD.metadata,
                             modify_position = True,
                             modify_values = False,
                             font_size = float(SD.radius)/10
                             )
    FreeCAD.ActiveDocument.recompute()

def update_values(epw_path = None, period = None):

    """Update a complete Sky Domes set values"""

    try:
        SD is not None
    except Exception as e:
        FreeCAD.Console.PrintMessage("update values: " + translate("SkyDomes",
            f"Could not get Sky Domes:\n{e}") + '\n')
        return
    high_density = False
    if SD.model == "Reinhart":
        high_density = True
    irradiance = False
    if SD.units[0:2] == "01":
        irradiance = True
    sky_dome_values = LBComponents.get_sky_matrix_dome_values(epw_path,
                                                 period,
                                                 high_density = high_density,
                                                 plot_irradiance = irradiance,
                                                 timestep = int(SD.timestep),
                                                 ground_reflectance = 0.2
                                                )
    SD.total_values = sky_dome_values[0]
    SD.direct_values = sky_dome_values[1]
    SD.diffuse_values = sky_dome_values[2]
    SD.vector_values = sky_dome_values[3]
    SD.metadata = sky_dome_values[4]
    print("modifying legend bar...")
    SD.leg_width = float(SD.radius*2/SD.color_count)
    if SD.direct_diffuse_domes is True:
        bar_x = float(SD.radius) * 7.3 + float(SD.position[0])
    else:
        bar_x = float(SD.radius) * 1.3 + float(SD.position[0])
    bar_y = -float(SD.radius) + float(SD.position[1])
    SD.leg_position = (bar_x, bar_y, 0.0)
    legend = LBComponents.get_modify_legend_bar(bar_obj = SD.Group[3].Group[0],
                              text_leg_group = SD.Group[3].Group[1],
                              #title = SD.units,
                              title = SD.leg_title,
                              values = SD.total_values,
                              position = SD.leg_position,
                              seg_height = SD.leg_width,
                              seg_width = SD.leg_width,
                              seg_count = SD.color_count,
                              color_leg_set = int(SD.color_set[0:2])
                              )
    color_rgb_leg = legend[1]
    print ("modifying Sky Domes forms...")
    modify_sky_dome_forms(sky_domes_group = SD,
                           center_dome = SD.position,
                           radius = float(SD.radius),
                           north = float(SD.north),
                           model = SD.model,
                           transparency = SD.transparency,
                           center_vectors = SD.center_vectors
                           )
    print ("modifying Sky Domes values...")
    apply_sky_dome_values(sky_domes_group = SD,
                          total_values = SD.total_values,
                          direct_values = SD.direct_values,
                          diffuse_values = SD.diffuse_values,
                          leg_colors = color_rgb_leg,
                          label = translate("SkyDomes",
                          "Sky Domes {} {}").format(
                                 SD.city, SD.units),
                          transparency = SD.transparency
                          )
    x1 = SD.position[0] - float(SD.radius)
    x2 = SD.position[0] + float(SD.radius)*2
    x3 = SD.position[0] + float(SD.radius)*5
    y = SD.position[1] - float(SD.radius)*1.4
    z = SD.position[2]
    pos1 = (x1, y, z)
    pos2 = (x2, y, z)
    pos3 = (x3, y, z)
    LBComponents.modify_main_legends(
                             main_leg1 = SD.Group[0].Group[2].Group[0],
                             main_leg2 = SD.Group[1].Group[2].Group[0],
                             main_leg3 = SD.Group[2].Group[2].Group[0],
                             pos1 = pos1,
                             pos2 = pos2,
                             pos3 = pos3,
                             unit = SD.leg_title,
                             metadata = SD.metadata,
                             modify_position = False,
                             modify_values = True,
                             font_size = float(SD.radius)/10
                             )
    FreeCAD.ActiveDocument.recompute()

def delete_sky_domes(sky_domes = None):

    """Delete a complete Sky Domes"""

    def show_warning_dialog():
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Delete Warning")
        msg.setText(translate("SkyDomes",
            "This will delete all main objects \n"
            "from the selected Sky Domes, \n"
            "and you won't be able to undo it. \n"
            "\n"
            "Are you sure you want to delete these Sky Domes?\n"
        ))
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setStandardButtons(
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        result = msg.exec_()
        return result
    result = show_warning_dialog()
    if result == QtWidgets.QMessageBox.Ok:
        # colect the objects to delete
        all_to_select = set()
        all_to_select.add(sky_domes)# Add the initial selected object(s)
        # Find all objects that the current object depends on
        def find_out_dependents(current_obj, dependents_set):
            for dep_obj in current_obj.OutList:
                if (dep_obj.Name[0:3] != "SD_"
                    and dep_obj.Name[0:3] != "Mod"
                    and dep_obj.Name[0:3] != "Arc"
                    and dep_obj.Name[0:3] != "Sur"
                    and dep_obj.Name[0:3] != "Res"):
                    if dep_obj not in dependents_set:
                        dependents_set.add(dep_obj)
                        find_out_dependents(dep_obj, dependents_set)

        find_out_dependents(sky_domes, all_to_select)
        # Clear current selection and add all identified objects
        Gui.Selection.clearSelection()
        for obj_to_add in all_to_select:
            FreeCAD.ActiveDocument.removeObject(obj_to_add.Name)

#=================================================
# E. Commands
#=================================================

if FreeCAD.GuiUp:
    FreeCAD.Gui.addCommand('CreateSkyDomes', CreateSkyDomes())
    FreeCAD.Gui.addCommand('ModifySkyDomes', ModifySkyDomes())
    FreeCAD.Gui.addCommand('DeleteSkyDomes', DeleteSkyDomes())
