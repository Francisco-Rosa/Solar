# ***************************************************************************
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
# ***************************************************************************/

"""Create and modify a sky matrix as colored domes, subdivided into patches."""

import os
import math
import FreeCAD
import FreeCADGui as Gui
import Draft
from PySide import QtWidgets
from PySide.QtCore import QT_TRANSLATE_NOOP
from ladybug.wea import Wea
from ladybug.analysisperiod import AnalysisPeriod
from ladybug_radiance.skymatrix import SkyMatrix #pip install -U ladybug-radiance
from ladybug_radiance.visualize.skydome import SkyDome

#=================================================
# A. Main classes
#=================================================
SD = None
SD_NEW = False

class SkyDomes:

    """Visualize and configure Sky domes in FreeCAD's 3D view."""

    def __init__(self,obj):
        obj.Proxy = self
        self.setProperties(obj)

    def setProperties(self,obj):

        """Gives the object properties to sky domes."""

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
            obj.addProperty("App::PropertyEnumeration",
                            "units", "03_Units",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Sky domes units")
                            ).units = ("Radiation (kWh/m²)",
                                       "Irradiance (W/m²)"
                            )
        # 04 Sky domes
        if not "sky_domes" in pl:
            obj.addProperty("App::PropertyBool",
                            "sky_domes", "04_SkyDomes",
                            QT_TRANSLATE_NOOP("App::Property",
                            "True, for using sky domes"
                            )).sky_domes = True
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
                            "Skyd dome total values")
                            ).total_values = []
        if not "direct_values" in pl:
            obj.addProperty("App::PropertyFloatList",
                            "direct_values", "04_SkyDomes",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Skyd ome direct values")
                            ).direct_values = []
        if not "diffuse_values" in pl:
            obj.addProperty("App::PropertyFloatList",
                            "diffuse_values", "04_SkyDomes",
                            QT_TRANSLATE_NOOP("App::Property",
                            "sky dome diffuse values")
                            ).diffuse_values = []
        if not "center_vectors" in pl:
            obj.addProperty("App::PropertyBool",
                            "center_vectors", "04_SkyDomes",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Visualize the center vectors of each patch dome")
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
                            "Sky domes radius (mm)")
                            ).radius = 10000
        # 07 Position
        if not "position" in pl:
            obj.addProperty("App::PropertyVector",
                            "position", "07_Position",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Center position of the sky dome total in mm (x, y, z)")
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
                            ).end_day = 30
        if not "start_hour" in pl:
            obj.addProperty("App::PropertyInteger",
                            "start_hour", "08_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The initial hour of the analysis period")
                            ).start_hour = 1
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
                            "Sky domes transparency")
                            ).transparency = 20

class SkyDomesViewProvider:

    """A View Provider for the Skydomes object"""

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
                'MenuText': QT_TRANSLATE_NOOP(
                'SkyDomes', 'CreateSkyDomes'),
                'ToolTip': QT_TRANSLATE_NOOP(
                'SkyDomes', 'Create Sky Domes. \n'
                'Open the dialog and configure its data.')}

    def IsActive(self):
        if Gui.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        activated_create_sky_domes(self)

class ModifySkyDomes:

    """Modify a set of sky domes."""

    def QT_TRANSLATE_NOOP(self, text):
        return text

    def GetResources(self):
        __dir__ = os.path.dirname(__file__)
        return {'Pixmap': __dir__ + '/icons/ModifySkyDomesIcon.svg',
                'MenuText': QT_TRANSLATE_NOOP(
                           'SkyDomes', 'ModifySkyDomes'),
                           'ToolTip': QT_TRANSLATE_NOOP(
                                      'SkyDomes', 'Modify Sky Domes. \n'
                                      'Select a SkyDomes group, click this button to '
                                      'open the dialog and modify its configuration.')}

    def IsActive(self):
        if Gui.ActiveDocument:
            try:
                FreeCAD.ActiveDocument.SkyDomes
                return True
            except:
                pass
        else:
            return False

    def Activated(self):
        activated_modify_sky_domes(self)

class DeleteSkyDomes:

    """Delete a set of sky domes."""

    def QT_TRANSLATE_NOOP(self, text):
        return text

    def GetResources(self):
        __dir__ = os.path.dirname(__file__)
        return {'Pixmap': __dir__ + '/icons/DeleteSkyDomesIcon.svg',
                'MenuText': QT_TRANSLATE_NOOP(
                            'SkyDomes', 'DeleteSkyDomes'),
                             'ToolTip': QT_TRANSLATE_NOOP(
                                        'SkyDomes', 'Delete Sky Domes. \n'
                                        'Select a SkyDomes group to delete.\n'
                                        'Be careful, you will not be able to '
                                        'undo this action.!')}

    def IsActive(self):
        if Gui.ActiveDocument:
            try:
                FreeCAD.ActiveDocument.SkyDomes
                return True
            except:
                pass
        else:
            return False

    def Activated(self):
        activated_delete_sky_domes(self)

def activated_create_sky_domes(self):

    """Create the SkyDomes"""

    global SD
    global SD_NEW
    folder = FreeCAD.ActiveDocument.addObject(
             'App::DocumentObjectGroupPython',
             'SkyDomes')
    SkyDomes(folder)
    SkyDomesViewProvider(folder.ViewObject)
    SD = folder
    print(f"create sky domes: SD = {SD.Name}")
    SD_NEW = True
    create_sky_domes()

def activated_modify_sky_domes(self):

    """Modify the SkyDomes selected"""

    global SD
    global SD_NEW
    SD_NEW = False
    SD = select_sky_domes()
    if SD is not None:
        print(f"activated modify sky domes: SD = {SD.Name}")
        modify_sky_domes(forms = True, values = True)
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "To modify a set of sky domes, first you must select one!" + '\n'))

def activated_delete_sky_domes(self):

    """Delete the SkyDomes selected"""

    try:
        selection = select_sky_domes()
        if selection is not None:
            print(f"activated delete sky domes: SD = {selection.Name}")
            delete_sky_domes(selection)
        else:
            FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
             "To delete a set of sky domes, first you must select one!" + '\n'))
    except Exception:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "To delete a set of sky domes, first you must select one!" + '\n'))

def select_sky_domes():

    """Select a SkyDomes"""

    SD = None
    selection = []
    selection = Gui.Selection.getSelection()
    try:
        selection[0]
        if selection[0].Name[0:8] == "SkyDomes":
            SD = selection[0]
            return SD
        else:
            FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
                "Warning: The object selected is not a SkyDomes!" + '\n'))
    except:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
                              "There is no selection!" + '\n'))

#=================================================
# B. Get data
#=================================================

def get_sky_dome_values(epw_path = "",
                        period = None,
                        sky_dome_model = "",
                        sky_dome_units = "",
                        ):

    """Obtains the necessary data (epw file, analysis period, model,
    total, directs and diffuse values and returns the sky domes values
    (total, direct, and diffuse values, legend parameters,
    colors, and values)"""

    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Attempting to get sky domes values: "
            "Skydomes object could not be found!") + "\n")
        return
    # epw_path
    if SD.epw_path != "":
        epw_path = SD.epw_path
        if not epw_path or not os.path.isfile(epw_path):
            FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
                "Getting values: to use EPW, please provide a valid file path.") + '\n')
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Could not get epw!" + '\n'))
        return
    # period
    period = None
    period = AnalysisPeriod(SD.start_month,
                            SD.start_day,
                            SD.start_hour,
                            SD.end_month,
                            SD.end_day,
                            SD.end_hour,
                            int(SD.timestep),
                            SD.leap_year
                            )
    # Hoys and sky matrix
    hoys = [h for h in period.hoys]
    sky = SkyMatrix.from_epw(epw_path, hoys) # Radiance must be installed
    # model
    sky_dome_model = SD.model
    if sky_dome_model == "Tregenza":
        sky.high_density = False
    if sky_dome_model == "Reinhart":
        sky.high_density = True
    # units
    sky_dome_units = SD.units
    if sky_dome_units == "Irradiance (W/m²)":
        Wea.from_epw_file(SD.epw_path) # for irradiance values
        sky_dome_obj = SkyDome(sky, plot_irradiance = True)
    else:
        sky_dome_obj = SkyDome(sky) # Radiance installed
    # Get values
    sky_dome_values = []
    total_values = []
    total_values = sky_dome_obj.total_values
    direct_values = []
    direct_values = sky_dome_obj.direct_values
    diffuse_values = []
    diffuse_values = sky_dome_obj.diffuse_values
    SD.total_values = []
    SD.direct_values = []
    SD.diffuse_values = []
    SD.total_values = list(total_values)
    SD.direct_values = list(direct_values)
    SD.diffuse_values = list(diffuse_values)
    vector_values = []
    vectors = sky_dome_obj.patch_vectors
    for i in range(len(vectors)):
        vector = (vectors[i][0], vectors[i][1], vectors[i][2])
        vector_values.append(vector)
    SD.vector_values = vector_values
    metadata = []
    metadata = sky_dome_obj.metadata
    metadata_str = []
    SD.metadata = []
    for i in range(len(metadata)):
        data = metadata[i]
        str_data = str(data)
        metadata_str.append(str_data)
    SD.metadata = metadata_str
    # Colors legend
    colors_leg = sky_dome_obj.legend_parameters.colors
    total_colors = len(colors_leg)
    color_rgb_leg = []
    for i in range(total_colors):
        rgb = (colors_leg[i][0], colors_leg[i][1], colors_leg[i][2])
        color_rgb_leg.append(rgb)
    sky_dome_values.append(color_rgb_leg) # [0]
    # values legend
    interval_value = max(total_values) / total_colors
    values_leg = []
    for v in range(total_colors + 1):
        value = v * interval_value
        values_leg.append(value)
    sky_dome_values.append(values_leg) # [1]
    FreeCAD.ActiveDocument.recompute()
    return sky_dome_values

def get_color_assigment(value = None,
                        total_values = None,
                        values_leg = None,
                        color_rgb_leg = None
                        ):

    """Get the legend colors that correspond to the values."""

    if values_leg[0] <= value < values_leg[1]:
        rgb0 = color_rgb_leg[0]
        return rgb0
    if values_leg[1] <= value < values_leg[2]:
        rgb1 = color_rgb_leg[1]
        return rgb1
    if values_leg[2] <= value < values_leg[3]:
        rgb2 = color_rgb_leg[2]
        return rgb2
    if values_leg[3] <= value < values_leg[4]:
        rgb3 = color_rgb_leg[3]
        return rgb3
    if values_leg[4] <= value < values_leg[5]:
        rgb4 = color_rgb_leg[4]
        return rgb4
    if values_leg[5] <= value < values_leg[6]:
        rgb5 = color_rgb_leg[5]
        return rgb5
    if values_leg[6] <= value < values_leg[7]:
        rgb6 = color_rgb_leg[6]
        return rgb6
    if values_leg[7] <= value < values_leg[8]:
        rgb7 = color_rgb_leg[7]
        return rgb7
    if values_leg[8] <= value < values_leg[9]:
        rgb8 = color_rgb_leg[8]
        return rgb8
    if values_leg[9] <= value <= max(total_values):
        rgb9 = color_rgb_leg[9]
        return rgb9
    FreeCAD.ActiveDocument.recompute()

#=================================================
# C. Sky domes
#=================================================

# 1. Get sky domes geometry
def get_sky_domes(center_dome = None,
                  radius = None,
                  north = None,
                  sky_dome_model = "None"
                  ):

    """Get sky domes geometry"""

    doc = FreeCAD.ActiveDocument
    TREGENZA_PATCHES_PER_ROW = (30, 30, 24, 24, 18, 12, 6)
    REINHART_PATCHES_PER_ROW = (60, 60, 60, 60, 48, 48, 48,
                                48, 36, 36, 24, 24, 12, 12)

    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Sky domes geometry: Could not get sky domes properties!") + "\n")
        return
    model = "None"
    sky_dome_model = "None"
    sky_dome_model = SD.model
    # model
    if sky_dome_model == "Tregenza":
        model = TREGENZA_PATCHES_PER_ROW
        ang_model = 12
    if sky_dome_model == "Reinhart":
        model = REINHART_PATCHES_PER_ROW
        ang_model = 6.2
    # Center, radius and north
    center_dome = SD.position
    radius = float(SD.radius)
    north = float(SD.north)
    surfaces = []
    rings = None
    rings = len(model)
    radius_init = 1000
    create_surfaces =  False
    dome_compound = None
    # create groups
    try:
        doc.SD_construction
        dome_const_group = doc.SD_construction
    except Exception:
        dome_const_group = doc.addObject('App::DocumentObjectGroup',
                                         'SD_construction')
        dome_const_group.Label = QT_TRANSLATE_NOOP('SkyDomes',
                                         'SD_constructions')
    if sky_dome_model == "Tregenza":
        try:
            doc.Model_Tregenza
            dome_model_group = doc.Model_Tregenza
            dome_compound = doc.SD_Tregenza
            create_surfaces = False
        except Exception:
            dome_model_group = doc.addObject('App::DocumentObjectGroup',
                                             'Model_Tregenza')
            dome_model_group.Label = QT_TRANSLATE_NOOP('SkyDomes',
                                             'Model_Tregenza')
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
            dome_model_group.Label = QT_TRANSLATE_NOOP('SkyDomes',
                                             'Model_Reinhart')
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
            dome.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                           "SD_Tregenza")
            dome.Links = surfaces
        if sky_dome_model == "Reinhart":
            dome = FreeCAD.activeDocument().addObject(
                                           "Part::Compound",
                                           "SD_Reinhart")
            dome.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                           "SD_Reinhart")
            dome.Links = surfaces
        doc.getObject(dome_model_group.Name).addObject(dome)
        # Group visibility
        doc.getObject(dome_const_group.Name).Visibility = False
        doc.getObject(dome_model_group.Name).Visibility = False
        dome_compound = dome

    # Create clones for total, direct and diffuse values
    scale = radius/radius_init
    # total values - clone1
    dome_total = Draft.make_clone(doc.getObject(dome_compound.Name))
    doc.getObject(dome_total.Name).Label = QT_TRANSLATE_NOOP(
                                           "SkyDomes",
                                           "Sky_Dome_Total")
    dome_total_group = doc.addObject("App::DocumentObjectGroup",
                                           "Sky_Dome_Total")
    dome_total_group.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                           "Sky_Dome_Total")
    doc.getObject(dome_total_group.Name).addObject(dome_total)
    pl1 = FreeCAD.Placement()
    pl1.Base = FreeCAD.Vector(center_dome)
    pl1.Rotation.setYawPitchRoll(-north, 0, 0)
    dome_total.Placement = pl1
    Gui.ActiveDocument.getObject(dome_total.Name).LineWidth = 1
    Gui.ActiveDocument.getObject(dome_total.Name).PointSize = 1
    dome_total.Scale = (scale, scale, scale)
    # direct values - clone2
    dome_direct = Draft.make_clone(doc.getObject(dome_compound.Name))
    doc.getObject(dome_direct.Name).Label = QT_TRANSLATE_NOOP(
                                            "SkyDomes",
                                            "Sky_Dome_Direct")
    dome_direct_group = doc.addObject('App::DocumentObjectGroup',
                                            'Sky_Dome_Direct')
    dome_direct_group.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                            "Sky_Dome_Direct")
    doc.getObject(dome_direct_group.Name).addObject(dome_direct)
    pl2 = FreeCAD.Placement()
    pl2.Base = FreeCAD.Vector(radius*3 + center_dome[0],
                              center_dome[1], center_dome[2])
    pl2.Rotation.setYawPitchRoll(-north, 0, 0)
    dome_direct.Placement = pl2
    Gui.ActiveDocument.getObject(dome_direct.Name).LineWidth = 1
    Gui.ActiveDocument.getObject(dome_direct.Name).PointSize = 1
    dome_direct.Scale = (scale, scale, scale)
    # diffuse values - clone3
    dome_diffuse = Draft.make_clone(doc.getObject(dome_compound.Name))
    doc.getObject(dome_diffuse.Name).Label = QT_TRANSLATE_NOOP(
                                             "SkyDomes",
                                             "Sky_Dome_Diffuse")
    dome_diffuse_group = doc.addObject('App::DocumentObjectGroup',
                                       'Sky_Dome_Diffuse')
    dome_diffuse_group.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                                 "Sky_Dome_Diffuse")
    doc.getObject(dome_diffuse_group.Name).addObject(dome_diffuse)
    pl3 = FreeCAD.Placement()
    pl3.Base = FreeCAD.Vector(radius*6 + center_dome[0],
                              center_dome[1], center_dome[2])
    pl3.Rotation.setYawPitchRoll(-north, 0, 0)
    dome_diffuse.Placement = pl3
    Gui.ActiveDocument.getObject(dome_diffuse.Name).LineWidth = 1
    Gui.ActiveDocument.getObject(dome_diffuse.Name).PointSize = 1
    dome_diffuse.Scale = (scale, scale, scale)
    # Save and return data
    sky_domes = []
    sky_domes.append(dome_total_group) # [0]
    sky_domes.append(dome_direct_group) # [1]
    sky_domes.append(dome_diffuse_group) # [2]
    FreeCAD.ActiveDocument.recompute()
    return sky_domes

# 2. Modify sky domes geometry
def modify_sky_domes_forms(sky_domes_group = None,
                           center_dome = None,
                           radius = None,
                           north = None
                           ):

    """Modify sky domes geometry"""

    # Get initial objects and necessary data
    doc = FreeCAD.ActiveDocument
    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Modify sky domes: Could not get sky domes properties!") + "\n")
        return

    center_dome = SD.position
    radius = float(SD.radius)
    north = SD.north
    sky_domes_group = SD
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
    dome_total.ViewObject.Transparency =  SD.transparency
    # Update distance between original and clone2
    pl2 = FreeCAD.Placement()
    pl2.Base = FreeCAD.Vector(radius*3 + center_dome[0],
                              center_dome[1], center_dome[2])
    pl2.Rotation.setYawPitchRoll(-north, 0, 0)
    dome_direct.Placement = pl2
    dome_direct.Scale = (scale, scale, scale)
    dome_direct.ViewObject.Transparency =  SD.transparency
    # Update distance between original and clone3
    pl3 = FreeCAD.Placement()
    pl3.Base = FreeCAD.Vector(radius*6 + center_dome[0],
                              center_dome[1], center_dome[2])
    pl3.Rotation.setYawPitchRoll(-north, 0, 0)
    dome_diffuse.Placement = pl3
    dome_diffuse.Scale = (scale, scale, scale)
    dome_diffuse.ViewObject.Transparency =  SD.transparency
    # Update center vectors visibility
    if SD.model == "Tregenza" and hasattr(doc, 'SD_Vectors_TR'):
        doc.SD_Vectors_TR.Visibility = SD.center_vectors
    if SD.model == "Reinhart" and hasattr(doc, 'SD_Vectors_RE'):
        doc.SD_Vectors_RE.Visibility = SD.center_vectors
    FreeCAD.ActiveDocument.recompute()

# 3. Apply and modify colors
def apply_sky_dome_values(sky_domes_group = None,
                          total_values = None,
                          direct_values = None,
                          diffuse_values = None,
                          sky_values = None
                          ):

    """Apply and modify colors"""

    doc = FreeCAD.ActiveDocument
    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Apply sky dome values: Could not get sky domes properties!") + "\n")
        return
    sky_domes_group = SD
    dome_total = sky_domes_group.Group[0].Group[0]
    dome_direct = sky_domes_group.Group[1].Group[0]
    dome_diffuse = sky_domes_group.Group[2].Group[0]
    surfaces = []
    surfaces = dome_total.Shape.Faces
    # Colors and values
    SD.Label = f"SD_{SD.city}_{SD.units}"
    total_values = SD.total_values
    direct_values = SD.direct_values
    diffuse_values = SD.diffuse_values
    colors_seq1 = []
    colors_seq2 = []
    colors_seq3 = []
    for i in range(len(surfaces)):
        value1 = total_values[i]
        value2 = direct_values[i]
        value3 = diffuse_values[i]
        rgb1 = get_color_assigment(value = value1,
                                   total_values = SD.total_values,
                                   values_leg = sky_values[1],
                                   color_rgb_leg = sky_values[0]
                                   )
        rgb2 = get_color_assigment(value = value2,
                                   total_values = SD.total_values,
                                   values_leg = sky_values[1],
                                   color_rgb_leg = sky_values[0]
                                   )
        rgb3 = get_color_assigment(value = value3,
                                   total_values = SD.total_values,
                                   values_leg = sky_values[1],
                                   color_rgb_leg = sky_values[0]
                                   )
        colors_seq1.append(rgb1)
        colors_seq2.append(rgb2)
        colors_seq3.append(rgb3)
    # Apply the colors of each patch in sky domes clones
    doc.getObject(dome_total.Name).ViewObject.DiffuseColor = colors_seq1
    doc.getObject(dome_direct.Name).ViewObject.DiffuseColor = colors_seq2
    doc.getObject(dome_diffuse.Name).ViewObject.DiffuseColor = colors_seq3
    # Adjust transparencies
    Gui.ActiveDocument.getObject(dome_total.Name).Transparency = SD.transparency
    Gui.ActiveDocument.getObject(dome_direct.Name).Transparency = SD.transparency
    Gui.ActiveDocument.getObject(dome_diffuse.Name).Transparency = SD.transparency
    FreeCAD.ActiveDocument.recompute()

# 4. Center vectors - patches
def get_center_vectors():

    """Get center vectors"""

    doc = FreeCAD.ActiveDocument
    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Get center vectors: Could not get sky domes properties!") + "\n")
        return
    radius = SD.radius
    vector_values = SD.vector_values
    angle = -SD.north
    center = SD.position
    if SD.model == "Tregenza":
        dome_vectors_group = doc.addObject('App::DocumentObjectGroup',
                                           'SD_Vectors_TR')
        dome_vectors_group.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                                     "SD_Vectors_TR")
    if SD.model == "Reinhart":
        dome_vectors_group = doc.addObject('App::DocumentObjectGroup',
                                           'SD_Vectors_RE')
        dome_vectors_group.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                                     "SD_Vectors_RE")

    for i in range(len(vector_values)):
        point = Draft.make_point(
                    float(vector_values[i][0]*radius) + SD.position[0],
                    float(vector_values[i][1]*radius) + SD.position[1],
                    float(vector_values[i][2]*radius) + SD.position[2])
        doc.getObject(dome_vectors_group.Name).addObject(point)
    FreeCAD.ActiveDocument.recompute()
    points = dome_vectors_group.Group
    for i in range(len(points)):
        Draft.rotate([points[i]], angle, center,
                     axis=FreeCAD.Vector(0.0, 0.0, 1.0),
                     copy=False)
    doc.getObject(dome_vectors_group.Name).Visibility = SD.center_vectors
    FreeCAD.ActiveDocument.recompute()

def modify_center_vectors():

    """modify center vectors"""

    doc = FreeCAD.ActiveDocument
    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Modify center vectors: Could not get sky domes properties!") + "\n")
        return
    radius = SD.radius
    vector_values = SD.vector_values
    if SD.model == "Tregenza":
        vectors_group = doc.SD_Vectors_TR
    if SD.model == "Reinhart":
        vectors_group = doc.SD_Vectors_RE
    points = vectors_group.Group
    angle = -SD.north
    center = SD.position
    for i in range(len(points)):
        points[i].X = float(vector_values[i][0]*radius) + SD.position[0]
        points[i].Y = float(vector_values[i][1]*radius) + SD.position[1]
        points[i].Z = float(vector_values[i][2]*radius) + SD.position[2]
    FreeCAD.ActiveDocument.recompute()
    for i in range(len(points)):
        Draft.rotate([points[i]], angle, center,
                      axis=FreeCAD.Vector(0.0, 0.0, 1.0),
                      copy=False)
    vectors_group.Visibility = SD.center_vectors
    FreeCAD.ActiveDocument.recompute()

#=================================================
# D. Compass
#=================================================

# 1. Create compass
def get_compass(center = None,
                radius = None,
                north = None,
                variation_angle = None,
                dome_group1 = None,
                dome_group2 = None,
                dome_group3 = None
                ):

    """Create compass"""

    doc = FreeCAD.ActiveDocument
    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Get compass: Could not get sky domes properties!") + "\n")
        return
    center = SD.position
    radius = float(SD.radius)
    north = float(SD.north)
    variation_angle = 10
    # Create generic compass and values
    angles_compas = []
    angles_compas_leg = []
    compass_list = []
    max_angle = 360
    n_angles = int(max_angle / variation_angle)
    # create compass angles and legend text lists
    for i in range(n_angles):
        angle = variation_angle * i
        angles_compas.append(angle) # angles, clockwise
        angle_leg = str(angle) # string angles, clockwise
        if angle_leg == "0":
            angle_leg = QT_TRANSLATE_NOOP("SkyDomes", "N")
        elif angle_leg == "90":
            angle_leg = QT_TRANSLATE_NOOP("SkyDomes", "E")
        elif angle_leg == "180":
            angle_leg = QT_TRANSLATE_NOOP("SkyDomes", "S")
        elif angle_leg == "270":
            angle_leg = QT_TRANSLATE_NOOP("SkyDomes", "W")
        angles_compas_leg.append(angle_leg)
    # create compass circles
    pl=FreeCAD.Placement()
    pl.Base = FreeCAD.Vector(center)
    pl1=FreeCAD.Placement()
    pl2=FreeCAD.Placement()
    pl3=FreeCAD.Placement()
    pl.Rotation.setYawPitchRoll(0,0,0)
    radius_compas = radius
    circle1 = Draft.make_circle(radius=radius_compas,
                                placement=pl,
                                face=False,
                                support=None)
    circle2 = Draft.make_circle(radius=radius_compas*1.02,
                                placement=pl,
                                face=False,
                                support=None)
    circle3 = Draft.make_circle(radius=radius_compas*1.05,
                                placement=pl,
                                face=False,
                                support=None)
    compass_list = [circle1, circle2, circle3]
    # Create groups
    dome_leg1_group = doc.addObject('App::DocumentObjectGroup',
                                    'Compass_legend_total')
    dome_leg1_group.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                              "Compass_legend_total")
    dome_leg2_group = doc.addObject('App::DocumentObjectGroup',
                                    'Compass_legend_direct')
    dome_leg2_group.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                              "Compass_legend_direct")
    dome_leg3_group = doc.addObject('App::DocumentObjectGroup',
                                    'Compass_legend_diffuse')
    dome_leg3_group.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                              "Compass_legend_diffuse")

    # Create lines and texts
    for i in range(n_angles):
        # lines
        angle = (90 - float(north)) - angles_compas[i] # north y-axis, clockwise
        x1 = radius_compas * math.cos(math.radians(angle))
        y1 = radius_compas * math.sin(math.radians(angle))
        x2 = radius_compas * math.cos(math.radians(angle)) * 1.05
        y2 = radius_compas * math.sin(math.radians(angle)) * 1.05
        points = [FreeCAD.Vector(x1 + center[0],
                                 y1 + center[1],
                                 center[2]),
                  FreeCAD.Vector(x2 + center[0],
                                 y2 + center[1],
                                 center[2])]
        line = Draft.make_wire(points, placement=pl,
                               closed=False, face=False,
                               support=None)
        compass_list.append(line)
        # compass text total values
        x3 = radius_compas * math.cos(math.radians(angle)) * 1.15
        y3 = radius_compas * math.sin(math.radians(angle)) * 1.15
        title_leg_compas = angles_compas_leg[i]
        pl1.Base = FreeCAD.Vector(x3 - radius/20 + center[0],
                                  y3 - radius/50 + center[1],
                                  center[2])
        text_compas_leg1 = Draft.make_text([title_leg_compas],
                                            placement=pl1,
                                            screen=None,
                                            height=radius/15,
                                            line_spacing=None
                                           )
        text_compas_leg1.Label = str(title_leg_compas) + "_"
        # compass text direct values
        pl2.Base = FreeCAD.Vector(x3 - radius/20 + radius*3 + center[0],
                                  y3-radius/50 + center[1],
                                  center[2])
        text_compas_leg2 = Draft.make_text([title_leg_compas],
                                            placement=pl2,
                                            screen=None,
                                            height=radius/15,
                                            line_spacing=None
                                           )
        text_compas_leg2.Label = str(title_leg_compas) + "_"
        # compass text diffuse values
        pl3.Base = FreeCAD.Vector(x3 - radius/20 + radius*6 + center[0],
                                  y3-radius/50 + center[1],
                                  center[2])
        text_compas_leg3 = Draft.make_text([title_leg_compas],
                                            placement=pl3,
                                            screen=None,
                                            height=radius/15,
                                            line_spacing=None
                                            )
        text_compas_leg3.Label = str(title_leg_compas) + "_"
        # text groups
        doc.getObject(dome_leg1_group.Name).addObject(text_compas_leg1)
        doc.getObject(dome_leg2_group.Name).addObject(text_compas_leg2)
        doc.getObject(dome_leg3_group.Name).addObject(text_compas_leg3)

    # Configure compass and values
    # Get total, direct and diffuse groups
    dome_total_group = dome_group1
    dome_direct_group = dome_group2
    dome_diffuse_group = dome_group3
    # Compass total values - compound
    compass_total = doc.addObject("Part::Compound",
                                  "Compass_circles_total")
    compass_total.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                            "Compass_circles_total")
    doc.getObject(compass_total.Name).Links = compass_list
    doc.getObject(dome_total_group.Name).addObject(compass_total)
    # Compass direct values - clones
    compass_direct = Draft.make_clone(doc.getObject(compass_total.Name))
    doc.getObject(compass_direct.Name).Placement.Base = (radius*3, 0,0)
    doc.getObject(compass_direct.Name).Label = QT_TRANSLATE_NOOP(
                                               "SkyDomes",
                                               "Compass_circles_direct")
    doc.getObject(dome_direct_group.Name).addObject(compass_direct)
    # Compass diffuse values - clone
    compass_diffuse = Draft.make_clone(doc.getObject(compass_total.Name))
    doc.getObject(compass_diffuse.Name).Placement.Base = (radius*6, 0,0)
    doc.getObject(compass_diffuse.Name).Label = QT_TRANSLATE_NOOP(
                                                "SkyDomes",
                                                "Compass_circles_diffuse")
    doc.getObject(dome_diffuse_group.Name).addObject(compass_diffuse)
    # Save and return data
    compass_data = []
    compass_data.append(dome_leg1_group) # [0]
    compass_data.append(dome_leg2_group) # [1]
    compass_data.append(dome_leg3_group) # [2]
    FreeCAD.ActiveDocument.recompute()
    return compass_data

# 2. Modify compass
def modify_compass(center = None,
                   radius = None,
                   north = None,
                   variation_angle = None,
                   circ_lines_list = None,
                   text_list1 = None,
                   text_list2 = None,
                   text_list3 = None,
                   sky_domes_group = None
                   ):

    """Modify compass"""

    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Modify compass: Could not get sky domes properties!") + "\n")
        return
    center = SD.position
    radius = float(SD.radius)
    north = SD.north
    variation_angle = 10
    # Configure compass circles
    angles_compas = []
    max_angle = 360
    n_angles = int(max_angle / variation_angle)
    # Create compass angles and legend text lists
    for i in range(n_angles):
        angle = variation_angle * i
        angles_compas.append(angle)
    # Get necessary object lists
    sky_domes_group = SD
    circ_lines_list = []
    circ_lines_list = sky_domes_group.Group[0].Group[1].Links
    text_list1 = []
    text_list1 = sky_domes_group.Group[0].Group[2].Group[1].Group
    text_list2 = []
    text_list2 = sky_domes_group.Group[1].Group[2].Group[1].Group
    text_list3 = []
    text_list3 = sky_domes_group.Group[2].Group[2].Group[1].Group
    compass_original = sky_domes_group.Group[0].Group[1]
    compass_clone1 = sky_domes_group.Group[1].Group[1]
    compass_clone2 = sky_domes_group.Group[2].Group[1]
    pl = FreeCAD.Placement() # original
    pl.Base = FreeCAD.Vector(center)
    pl.Rotation.setYawPitchRoll(north,0,0)
    circle1 = circ_lines_list[0]
    circle1.Placement = pl
    circle1.Radius = radius
    circle2 = circ_lines_list[1]
    circle2.Placement = pl
    circle2.Radius = radius*1.02
    circle3 = circ_lines_list[2]
    circle3.Placement = pl
    circle3.Radius = radius*1.05
    # Configure lines and texts positions
    for i in range(len(circ_lines_list) - 3):
        angle = (90 - float(north)) - angles_compas[i] # north y-axis, clockwise
        # modify lines
        x1 = radius * math.cos(math.radians(angle))
        y1 = radius * math.sin(math.radians(angle))
        x2 = radius * math.cos(math.radians(angle)) * 1.05
        y2 = radius * math.sin(math.radians(angle)) * 1.05
        line = circ_lines_list[i + 3]
        line.Placement = pl
        line.Start = FreeCAD.Vector(x1 + center[0],
                                    y1 + center[1],
                                    center[2])
        line.End = FreeCAD.Vector(x2 + center[0],
                                  y2 + center[1],
                                  center[2])
        # modify texts
        x3 = radius * math.cos(math.radians(angle)) * 1.15
        y3 = radius * math.sin(math.radians(angle)) * 1.15
        x_text1 = center[0] + (x3 - radius/20)
        y_text1 = center[1] + (y3 - radius/50)
        z_text1 = center[2]
        text1 = text_list1[i]
        text1.Placement.Base = FreeCAD.Vector(x_text1,
                                              y_text1,
                                              z_text1
                                              )
        text1.ViewObject.FontSize = radius/15
        text2 = text_list2[i]
        text2.Placement.Base = FreeCAD.Vector(x_text1 + radius*3,
                                              y_text1,
                                              z_text1
                                              )
        text2.ViewObject.FontSize = radius/15
        text3 = text_list3[i]
        text3.Placement.Base = FreeCAD.Vector(x_text1 + radius*6,
                                              y_text1,
                                              z_text1
                                              )
        text3.ViewObject.FontSize = radius/15
    FreeCAD.ActiveDocument.recompute()
    # Update distance between original and clone1
    base_ori = compass_original.Placement.Base # original
    x_ori = base_ori[0]
    y_ori = base_ori[1]
    z_ori = base_ori[2]
    x1_fin = x_ori + radius*3
    pl1 = FreeCAD.Placement()
    pl1.Base = FreeCAD.Vector(x1_fin, y_ori, z_ori)
    compass_clone1.Placement = pl1
    # Update distance between original and clone2
    x2_fin = x_ori + radius*6
    pl2 = FreeCAD.Placement()
    pl2.Base = FreeCAD.Vector(x2_fin, y_ori, z_ori)
    compass_clone2.Placement = pl2

    FreeCAD.ActiveDocument.recompute()

#=================================================
# E. Legend bar
#=================================================
# 1. Create colored legend bar with values
def get_legend_bar(scale = None,
                   color_rgb_leg = None,
                   values_leg = None,
                   radius_dome = None
                   ):

    """Create colored legend bar with values."""

    doc = FreeCAD.ActiveDocument
    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Get legend bar: Could not get sky domes properties!") + "\n")
        return
    center_dome = SD.position
    radius_dome = float(SD.radius)
    sky_dome_units = SD.units
    scale = 1
    # create legend group
    leg_bar_group = doc.addObject('App::DocumentObjectGroup',
                                  'Legend_bar')
    leg_bar_group.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                            "Legend_bar")
    # Create bar
    bar_width = radius_dome/5 * scale
    bar_height = radius_dome*2 * scale
    parts = len(color_rgb_leg)
    if SD.direct_diffuse_domes is True:
        bar_x = radius_dome * 7.3 + center_dome[0]
    else:
        bar_x = radius_dome * 1.3 + center_dome[0]
    bar_y = -radius_dome + center_dome[1]
    bar_rects = []
    bar_leg_pos = []
    pl = FreeCAD.Placement()
    for i in range(parts):
        y_bottom = bar_y + ((bar_height/ parts) * i )
        vector_bar_leg = FreeCAD.Vector(bar_x + bar_width*1.2,
                                        y_bottom,
                                        center_dome[2])
        bar_leg_pos.append(vector_bar_leg)

        # Create rectangles
        pl.Base = FreeCAD.Vector(bar_x,
                                 bar_y + (bar_height/parts)*i,
                                 center_dome[2])
        rect = Draft.make_rectangle(length=bar_width,
                                    height=bar_height/parts,
                                    placement=pl,
                                    face=True,
                                    support=None)
        bar_rects.append(rect)
    # Create compound
    bar_obj = doc.addObject("Part::Compound",
                            "Sky_Dome_bar")
    bar_obj.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                      "Sky_Dome_bar")
    doc.getObject(bar_obj.Name).Links = bar_rects
    Gui.ActiveDocument.getObject(bar_obj.Name).PointSize = 2
    Gui.ActiveDocument.getObject(bar_obj.Name).ShapeAppearance = (
             FreeCAD.Material(SpecularColor=(0.33,0.33,0.33))
             )
    # apply the corresponding colors to bar
    bar_obj.ViewObject.DiffuseColor = color_rgb_leg # colors_leg
    # put bar into legend group
    doc.getObject(leg_bar_group.Name).addObject(bar_obj)
    # get bar values
    # values_leg
    pl_bar = FreeCAD.Placement()
    for i in range(len(bar_leg_pos)):
        pl_bar.Base = bar_leg_pos[i]
        value_bar = f"{round(values_leg[i], 1)}"
        text_value = Draft.make_text([value_bar],
                                      placement=pl_bar,
                                      screen=None,
                                      height=radius_dome/14,
                                      line_spacing=None
                                    )
        text_value.Label = value_bar + "_"
        # put text value into legend group
        doc.getObject(leg_bar_group.Name).addObject(text_value)
    # max value
    max_value = f"{round(values_leg[-1], 1)}"
    pl_bar.Base = (bar_x + bar_width*1.2,
                   bar_height/2 + center_dome[1],
                   center_dome[2])
    text_units1 = Draft.make_text([max_value],
                                   placement=pl_bar,
                                   screen=None,
                                   height=radius_dome/14,
                                   line_spacing=None
                                  )
    text_units1.Label = max_value + "_"
    # put max value into legend group
    doc.getObject(leg_bar_group.Name).addObject(text_units1)
    # units
    if sky_dome_units == "Irradiance (W/m²)":
        units_bar = "W/m²"
    else:
        units_bar = "kWh/m²"
    pl_bar.Base = (bar_x,
                   bar_height/2 * 1.1 + center_dome[1],
                   center_dome[2])
    text_unit = Draft.make_text([units_bar],
                                 placement=pl_bar,
                                 screen=None,
                                 height=radius_dome/10,
                                 line_spacing=None
                                )
    text_unit.Label = units_bar + "_"
    # put text unit into legend group
    doc.getObject(leg_bar_group.Name).addObject(text_unit)
    # save and return data
    leg_data = []
    leg_data.append(leg_bar_group) # [0]
    leg_data.append(bar_width) # [1]
    leg_data.append(bar_x) # [2]
    leg_data.append(bar_height) # [3]
    leg_data.append(bar_leg_pos) # [4]
    FreeCAD.ActiveDocument.recompute()
    return leg_data

# 2. Apply and modify legend values
def modify_legend_bar(center_dome = None,
                   scale = None,
                   color_rgb_leg = None,
                   values = None,
                   modify_dimensions = False,
                   modify_values = False,
                   ):

    """Modify legend bar."""

    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Modify legend bar: Could not get sky domes properties!") + "\n")
        return
    # Modify position and dimensions (bar and text)
    Sky_Dome_legend = SD.Group[3].Group[0]
    legend = SD.Group[3].Group
    text_values = legend[1:13]
    color_rgb_leg = Sky_Dome_legend.ViewObject.DiffuseColor
    center_dome = SD.position
    dome_radius = float(SD.radius)
    scale = 1
    if modify_dimensions is True:
        # Update bar
        bar_width = dome_radius/5 * scale
        bar_height = dome_radius*2 * scale
        parts = len(Sky_Dome_legend.Links)
        if SD.direct_diffuse_domes is True:
            bar_x = center_dome[0] + dome_radius * 7.3
        else:
            bar_x = center_dome[0] + dome_radius * 1.3
        bar_y = center_dome[1] - dome_radius
        # Update bar rectangles
        for i in range(parts):
            y_bottom = bar_y + ((bar_height/parts) * i)
            rect = Sky_Dome_legend.Links[i]
            rect.Height = bar_width
            rect.Length = bar_height/parts
            rect.Placement.Base = FreeCAD.Vector(bar_x,
                                                 y_bottom,
                                                 center_dome[2])
    for i in range(len(text_values) - 1):
        text1 = None
        text1 = text_values[i]
        if modify_dimensions is True:
            # Update text position and size
            y_bottom = bar_y + ((bar_height/ parts) * i)
            vector_bar_leg = FreeCAD.Vector(bar_x + bar_width*1.2,
                                            y_bottom,
                                            center_dome[2])
            text1.Placement.Base = vector_bar_leg
            text1.ViewObject.FontSize = dome_radius / 14
        if modify_values is True:
            # Update text value and label
            text1.Text = f"{round(values[i], 1)}"
            text1.Label = f"{round(values[i], 1)}" + "_"
    # Update unit
    sky_dome_units = SD.units
    text2 = None
    text2 = text_values[11]
    if modify_dimensions is True:
        # Update text position and size
        text2.Placement.Base = (bar_x,
                                center_dome[1] + bar_height/2 * 1.1,
                                center_dome[2])
        text2.ViewObject.FontSize = dome_radius / 10
    if modify_values is True:
        # Update unit
        if sky_dome_units == "Irradiance (W/m²)":
            text2.Text = "W/m²"
            text2.Label = "W/m²" + "_"
        else:
            text2.Text = "kWh/m²"
            text2.Label = "kWh/m²" + "_"
    if modify_values is True:
        # update the corresponding colors to legend
        Sky_Dome_legend.ViewObject.DiffuseColor = color_rgb_leg # colors_leg
    FreeCAD.ActiveDocument.recompute()

#=================================================
# F. Main legend
#=================================================

# 1. Get main legend content
def get_main_legend_values(units = None,
                           metadata = None
                           ):

    """Get main legend"""

    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Get main legend: Could not get sky domes properties!") + "\n")
        return
    title_leg1 = QT_TRANSLATE_NOOP(
                 "SkyDomes", "Total" + " " + "{}").format(SD.units)
    period_leg = f"{SD.metadata[2]} - {SD.metadata[3]}"
    city_leg = f"{SD.metadata[6]}"
    country_leg = f"{SD.metadata[5]}"
    time_zone_leg = f"{SD.metadata[7]}"
    source_leg = f"{SD.metadata[4]}"
    text_total = [title_leg1, period_leg, city_leg,
                  country_leg, time_zone_leg, source_leg]
    # direct values
    title_leg2 = QT_TRANSLATE_NOOP(
                 "SkyDomes", "Direct" + " " + "{}").format(SD.units)
    text_direct = [title_leg2, period_leg, city_leg,
                   country_leg, time_zone_leg, source_leg]
    # diffuse values
    title_leg3 = QT_TRANSLATE_NOOP(
                 "SkyDomes", "Diffuse" + " " + "{}").format(SD.units)
    text_diffuse = [title_leg3, period_leg, city_leg,
                    country_leg, time_zone_leg, source_leg]
    leg_titles = [text_total, text_direct, text_diffuse]
    return leg_titles

# 2. Create main legend
def create_main_legends(dome_center = None,
                        radius = None
                        ):

    """Create main legend"""

    doc = FreeCAD.ActiveDocument
    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Create main legend: Could not get sky domes properties!") + "\n")
        return
    dome_center = SD.position
    radius = float(SD.radius)
    leg_titles = get_main_legend_values()
    text_total = leg_titles[0]
    text_direct = leg_titles[1]
    text_diffuse = leg_titles[2]

    # create legends
    pl1_leg = FreeCAD.Placement()
    pl1_leg.Base = FreeCAD.Vector(-radius + dome_center[0],
                                  -radius*1.4 + dome_center[1],
                                  dome_center[2])
    pl2_leg = FreeCAD.Placement()
    pl2_leg.Base = FreeCAD.Vector(radius*2 + dome_center[0],
                                  -radius*1.4 + dome_center[1],
                                  dome_center[2])
    pl3_leg = FreeCAD.Placement()
    pl3_leg.Base = FreeCAD.Vector(radius*5 + dome_center[0],
                                  -radius*1.4 + dome_center[1],
                                  dome_center[2])
    text_leg1 = Draft.make_text(text_total,
                                placement=pl1_leg,
                                screen=None,
                                height=radius/10,
                                line_spacing=1.2
                                )
    text_leg1.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                        "Legend_SD_total")
    text_leg2 = Draft.make_text(text_direct,
                                placement=pl2_leg,
                                screen=None,
                                height=radius/10,
                                line_spacing=1.2
                                )
    text_leg2.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                        "Legend_SD_direct")
    text_leg3 = Draft.make_text(text_diffuse, placement=pl3_leg,
                                screen=None, height=radius/10,
                                line_spacing=1.2
                                )
    text_leg3.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                        "Legend_SD_diffuse")
    # create and put text bar into legend group
    leg_total_group = doc.addObject('App::DocumentObjectGroup',
                                    'Legend_Total')
    leg_total_group.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                              "Legend_Total")
    doc.getObject(leg_total_group.Name).addObject(text_leg1)
    leg_direct_group = doc.addObject('App::DocumentObjectGroup',
                                     'Legend_Direct')
    leg_direct_group.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                               "Legend_Direct")
    doc.getObject(leg_direct_group.Name).addObject(text_leg2)
    leg_diffuse_group = doc.addObject('App::DocumentObjectGroup',
                                      'Legend_Diffuse')
    leg_diffuse_group.Label = QT_TRANSLATE_NOOP("SkyDomes",
                                                "Legend_Diffuse")
    doc.getObject(leg_diffuse_group.Name).addObject(text_leg3)
    main_leg_groups = []
    main_leg_groups = [leg_total_group,
                       leg_direct_group,
                       leg_diffuse_group]
    return main_leg_groups
    FreeCAD.ActiveDocument.recompute()

# 3. Modify position of the main legends (and text size?)
def modify_main_legends(position = None,
                        dome_radius = None,
                        modify_position = False,
                        modify_values = False
                        ):

    """ Modify position and text size"""

    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Modify main legend: Could not get sky domes properties!") + "\n")
        return
    position = SD.position
    dome_radius = float(SD.radius)
    sky_domes_group = SD
    legend1 = None
    legend2 = None
    legend3 = None
    legend1 = sky_domes_group.Group[0].Group[2].Group[0]
    legend2 = sky_domes_group.Group[1].Group[2].Group[0]
    legend3 = sky_domes_group.Group[2].Group[2].Group[0]
    if modify_position is True:
        legend1.Placement.Base = FreeCAD.Vector(position[0] - dome_radius,
                                                position[1] - dome_radius*1.4,
                                                position[2]
                                                )
        legend1.ViewObject.FontSize = dome_radius/10
        legend2.Placement.Base = FreeCAD.Vector(position[0] + dome_radius*2,
                                                position[1] - dome_radius*1.4,
                                                position[2]
                                                )
        legend2.ViewObject.FontSize = dome_radius/10
        legend3.Placement.Base = FreeCAD.Vector(position[0] + dome_radius*5,
                                                position[1] - dome_radius*1.4,
                                                position[2]
                                                )
        legend3.ViewObject.FontSize = dome_radius/10
    if modify_values is True:
        leg_titles = get_main_legend_values()
        legend1.Text = leg_titles[0]
        legend2.Text = leg_titles[1]
        legend3.Text = leg_titles[2]

    FreeCAD.ActiveDocument.recompute()

#=================================================
# G. Groups
#=================================================

def manage_sky_dome_groups(domes_group = None,
                           dome_total_group = None,
                           dome_direct_group = None,
                           dome_diffuse_group = None,
                           leg_bar_group = None,
                           dome_leg1_group = None,
                           dome_leg2_group = None,
                           dome_leg3_group = None,
                           leg_total_group = None,
                           leg_direct_group = None,
                           leg_diffuse_group = None
                           ):

    """Manage the sky domes groups"""

    doc = FreeCAD.ActiveDocument
    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Manage sky dome groups: Could not get sky domes properties!") + "\n")
        return
    domes_group = SD
    # legend groups
    # Total compass leg group to sky dome total leg group
    doc.getObject(leg_total_group.Name).addObject(dome_leg1_group)
    # Total leg group to sky dome total group
    doc.getObject(dome_total_group.Name).addObject(leg_total_group)
    # Direct compass leg group to sky dome direct group
    doc.getObject(leg_direct_group.Name).addObject(dome_leg2_group)
    # Direct leg group to sky dome direct group
    doc.getObject(dome_direct_group.Name).addObject(leg_direct_group)
    # Diffuse compass leg group to sky dome dissuse group
    doc.getObject(leg_diffuse_group.Name).addObject(dome_leg3_group)
    # Diffuse leg group to sky dome diffuse group
    doc.getObject(dome_diffuse_group.Name).addObject(leg_diffuse_group)
    FreeCAD.ActiveDocument.recompute()
    # groups to main group
    # Sky dome total group to sky domes group
    doc.getObject(domes_group.Name).addObject(dome_total_group)
    # Sky dome direct group to sky domes group
    doc.getObject(domes_group.Name).addObject(dome_direct_group)
    doc.getObject(dome_direct_group.Name).Visibility = SD.direct_diffuse_domes
    # Sky dome diffuse group to sky domes group
    doc.getObject(domes_group.Name).addObject(dome_diffuse_group)
    doc.getObject(dome_diffuse_group.Name).Visibility = SD.direct_diffuse_domes
     # Legend bar group to sky domes group
    doc.getObject(domes_group.Name).addObject(leg_bar_group)
    FreeCAD.ActiveDocument.recompute()
    return domes_group

#=================================================
# H. Main functions
#=================================================

#1. Create a sky domes set
def create_sky_domes():

    """Create a complete sky domes set"""

    doc = FreeCAD.ActiveDocument
    if SD is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "Create sky domes: Could not get sky domes properties!") + "\n")
        return
    global SD_NEW
    # epw_path
    #if SD.epw_path != "":
    try:
        obj1 = FreeCAD.ActiveDocument.SunProperties
        SD.epw_path = obj1.epw_path
        epw_path = SD.epw_path
        if not epw_path or not os.path.isfile(epw_path):
            FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
                "To create sky domes you must provide a valid epw file!") + '\n')
            return
    #else:
    except Exception:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            "To create sky domes, you need to indicate an epw file!" + '\n'))
        return
    # Getting sky domes
    print ("getting sky domes...")
    sky_domes = get_sky_domes()
    # Getting compass
    print ("compass_data...")
    compass_data = get_compass(dome_group1 = sky_domes[0],
                               dome_group2 = sky_domes[1],
                               dome_group3 = sky_domes[2]
                               )
    # Getting values
    sky_dome_values = get_sky_dome_values()
    # Getting center vector
    print ("center vectors...")
    if SD.center_vectors is True:
        if SD.model == "Tregenza":
            if hasattr(doc, 'SD_Vectors_TR'):
                modify_center_vectors()
            else:
                get_center_vectors()
        if SD.model == "Reinhart":
            if hasattr(doc, 'SD_Vectors_RE'):
                modify_center_vectors()
            else:
                get_center_vectors()
    # Getting main legend
    print ("main_leg...")
    leg_data = get_legend_bar(color_rgb_leg = sky_dome_values[0],
                              values_leg = sky_dome_values[1],
                              )
    print ("getting main legends...")
    main_leg_groups = create_main_legends()
    # Managing groups
    print("managing group...")
    manage_sky_dome_groups(dome_total_group = sky_domes[0],
                           dome_direct_group = sky_domes[1],
                           dome_diffuse_group = sky_domes[2],
                           leg_bar_group = leg_data[0],
                           dome_leg1_group = compass_data[0],
                           dome_leg2_group = compass_data[1],
                           dome_leg3_group = compass_data[2],
                           leg_total_group = main_leg_groups[0],
                           leg_direct_group = main_leg_groups[1],
                           leg_diffuse_group = main_leg_groups[2],
                           )
    # Applying sky domes values
    print ("applying values...")
    apply_sky_dome_values(sky_values = sky_dome_values
                          )
    Gui.SendMsgToActiveView("ViewFit")
    FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP(
                                'SkyDomes',
                                'Sky domes were created! To configure it, '
                                'make the adjustments in its properties window.'
                                 ) + '\n')
    SD_NEW = False
    Gui.runCommand('Std_ViewGroup',2)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(SD)
    FreeCAD.ActiveDocument.recompute()

#2. Modify a sky domes set
def modify_sky_domes(forms = False, values = False):

    """Modify a complete sky domes set"""

    if forms is True:
        #print("Try update forms!")
        update_forms()
        print("updated forms!")
    if values is True:
        #print("Try update values!")
        update_values()
        print("updated values!")
    Gui.SendMsgToActiveView("ViewFit")
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(SD)
    FreeCAD.ActiveDocument.recompute()

#2.1. Update forms of a sky domes set
def update_forms():

    """Update a complete sky domes set geometry"""

    doc = FreeCAD.ActiveDocument
    try:
        SD != None
    except Exception as e:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            f"Update forms: Could not get Sky domes:\n{e}") + '\n')
        return
    modify_sky_domes_forms()
    if SD.center_vectors is True:
        if SD.model == "Tregenza":
            if hasattr(doc, 'SD_Vectors_TR'):
                modify_center_vectors()
            else:
                get_center_vectors()
        if SD.model == "Reinhart":
            if hasattr(doc, 'SD_Vectors_RE'):
                modify_center_vectors()
            else:
                get_center_vectors()
    modify_compass()
    modify_legend_bar(modify_dimensions = True)
    modify_main_legends(modify_position = True)
    FreeCAD.ActiveDocument.recompute()

#2.1. Update values of a sky domes set
def update_values():

    """Update a complete sky domes set values"""

    try:
        SD is not None
    except Exception as e:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SkyDomes",
            f"Update values: Could not get Sky domes:\n{e}") + '\n')
        return
    sky_dome_values = get_sky_dome_values()
    modify_sky_domes_forms()
    print ("applying sky domes values...")
    apply_sky_dome_values(sky_values=sky_dome_values)
    print("modifying legend bar...")
    modify_legend_bar(values = sky_dome_values[1],
                      modify_values = True)
    print("modifying main legend...")
    modify_main_legends(modify_values = True)
    FreeCAD.ActiveDocument.recompute()

#3. Delete a sky domes set
def delete_sky_domes(sky_domes = None):

    """Delete a complete sky domes"""

    def show_warning_dialog():
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Delete Warning")
        msg.setText(QT_TRANSLATE_NOOP("SkyDomes",
            "This will delete all main objects from the selected Sky Domes, \n"
            "and you won't be able to undo it. \n"
            "\n"
            "Are you sure you want to delete these Sky Domes? \n"
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
# I. Commands
#=================================================

if FreeCAD.GuiUp:
    FreeCAD.Gui.addCommand('CreateSkyDomes', CreateSkyDomes())
    FreeCAD.Gui.addCommand('ModifySkyDomes', ModifySkyDomes())
    FreeCAD.Gui.addCommand('DeleteSkyDomes', DeleteSkyDomes())
