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

"""This module implements the sun radiation analysis."""

import os
import FreeCAD
import FreeCADGui as Gui
#import Draft
import Part
import MeshPart
from PySide.QtCore import QT_TRANSLATE_NOOP
from PySide import QtWidgets
from ladybug.analysisperiod import AnalysisPeriod
from ladybug_radiance.intersection import intersection_matrix, sky_intersection_matrix
from ladybug_radiance.skymatrix import SkyMatrix
import freecad.Solar.SunAnalysisDialog as SunAnalysisDialog
import freecad.Solar.LBComponents as LBComponents

translate = FreeCAD.Qt.translate

LanguagePath = os.path.dirname(__file__) + '/translations'
Gui.addLanguagePath(LanguagePath)

#=================================================
# A. Main classes
#=================================================
SA = None
SA_NEW = False

class SunAnalysis:

    """Visualize and configure Sun Analysis in FreeCAD's 3D view."""

    def __init__(self,obj):
        obj.Proxy = self
        self.setProperties(obj)

    def setProperties(self,obj):

        """Gives the object properties to Sun Analysis."""

        pl = obj.PropertiesList
        # 01 epw and location
        if not "epw_path" in pl:
            obj.addProperty("App::PropertyFile",
                            "epw_path", "01_epw_location",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Path to epw file")
                            ).epw_path = ""
        if not "city" in pl:
            obj.addProperty("App::PropertyString",
                            "city", "01_epw_location",
                            QT_TRANSLATE_NOOP("App::Property",
                            "City - read only")
                            ).city = ""
        if not "country" in pl:
            obj.addProperty("App::PropertyString",
                            "country", "01_epw_location",
                            QT_TRANSLATE_NOOP(
                            "App::Property",
                            "Country of the location - read only")
                            ).country = "BR"
        if not "elevation" in pl:
            obj.addProperty("App::PropertyFloat",
                            "elevation", "01_epw_location",
                            QT_TRANSLATE_NOOP(
                            "App::Property",
                            "Elevation of the location - read only")
                            ).elevation = 720.00
        if not "latitude" in pl:
            obj.addProperty("App::PropertyFloat",
                            "latitude", "01_epw_location",
                            QT_TRANSLATE_NOOP(
                            "App::Property",
                             "Latitude of the location - read only")
                            ).latitude = -23.550
        if not "longitude" in pl:
            obj.addProperty("App::PropertyFloat",
                            "longitude", "01_epw_location",
                            QT_TRANSLATE_NOOP(
                            "App::Property",
                            "Longitude of the location - read only")
                            ).longitude = -46.633
        if not "time_zone" in pl:
            obj.addProperty("App::PropertyInteger",
                            "time_zone", "01_epw_location",
                            QT_TRANSLATE_NOOP(
                            "App::Property",
                            "Time zone - read only")
                            ).time_zone = -3
        if not "north" in pl:
            obj.addProperty("App::PropertyAngle",
                            "north", "01_epw_location",
                            QT_TRANSLATE_NOOP(
                            "App::Property",
                            "North angle (clockwise)")
                            ).north = 0
        # 02. Geometries
        if not "objs_group" in pl:
            obj.addProperty("App::PropertyLink",
                            "objs_group", "02.Geometries",
                            QT_TRANSLATE_NOOP(
                            "App::Property",
                            "Group of objects to be analyzed.")
                            ).objs_group = None
        if not "study_objs" in pl:
            obj.addProperty("App::PropertyLinkList",
                            "study_objs", "02.Geometries",
                            QT_TRANSLATE_NOOP(
                            "App::Property",
                            "Select the objects to be analyzed.")
                            ).study_objs = []
        if not "study_context" in pl:
            obj.addProperty("App::PropertyLinkList",
                            "study_context", "02.Geometries",
                            QT_TRANSLATE_NOOP(
                            "App::Property",
                            "Select the objects from the context \n"
                            "of the analysis.\n"
                            "If there isn't one, adopt \n"
                            "the objects of study.")
                            ).study_context = []
        if not "max_length" in pl:
            obj.addProperty("App::PropertyFloat",
                            "max_length", "02.Geometries",
                            QT_TRANSLATE_NOOP(
                            "App::Property",
                            "Maximum value for the \n"
                            "triangular sub faces (mm).")
                            ).max_length = 2000
        if not "offset_distance" in pl:
            obj.addProperty("App::PropertyFloat",
                            "offset_distance", "02.Geometries",
                            QT_TRANSLATE_NOOP(
                            "App::Property",
                            "Offset distance (mm).")
                            ).offset_distance = 100
        if not "study_compound" in pl:
            obj.addProperty("App::PropertyLink",
                            "study_compound", "02.Geometries",
                            QT_TRANSLATE_NOOP(
                            "App::Property",
                            "Compound of the sub faces of the objects "
                            "of study - read only")
                            ).study_compound = None
        # 03. Analysis period
        if not "start_year" in pl:
            obj.addProperty("App::PropertyInteger",
                            "start_year", "03_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The initial year of the analysis period")
                            ).start_year = 2026
        if not "end_year" in pl:
            obj.addProperty("App::PropertyInteger",
                            "end_year", "03_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The final year of the analysis period")
                            ).end_year = 2026
        if not "start_month" in pl:
            obj.addProperty("App::PropertyInteger",
                            "start_month", "03_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The initial month of the analysis period")
                            ).start_month = 1
        if not "end_month" in pl:
            obj.addProperty("App::PropertyInteger",
                            "end_month", "03_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The final month of the analysis period")
                            ).end_month = 2
        if not "start_day" in pl:
            obj.addProperty("App::PropertyInteger",
                            "start_day", "03_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The initial day of the analysis period")
                            ).start_day = 1
        if not "end_day" in pl:
            obj.addProperty("App::PropertyInteger",
                            "end_day", "03_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The final day of the analysis period")
                            ).end_day = 30
        if not "start_hour" in pl:
            obj.addProperty("App::PropertyInteger",
                            "start_hour", "03_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The initial hour of the analysis period")
                            ).start_hour = 0
        if not "end_hour" in pl:
            obj.addProperty("App::PropertyInteger",
                            "end_hour", "03_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "The final hour of the analysis period")
                            ).end_hour = 23
        if not "timestep" in pl:
            obj.addProperty("App::PropertyEnumeration",
                            "timestep", "03_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Timestep per hour")
                            ).timestep = (1, 2, 3, 4, 5, 6, 10,
                                          12, 15, 20, 30, 60
                            )
        if not "leap_year" in pl:
            obj.addProperty("App::PropertyBool",
                            "leap_year", "03_Analysis_period",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Leap year")
                            ).leap_year = False
        # 04 Analysis results
        if not "results" in pl:
            from freecad.Solar.LBComponents import RESUL_00, RESUL_01, RESUL_02
            obj.addProperty("App::PropertyEnumeration",
                            "results", "04_Analysis_results",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Sun analysis results")
                            ).results = (f"00 - {RESUL_00}",
                                         f"01 - {RESUL_01}",
                                         f"02 - {RESUL_02}",
                            )
        if not "sky_matrix_high_density" in pl:
            obj.addProperty("App::PropertyBool",
                            "sky_matrix_high_density", "04_Analysis_results",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Enable sky matrix high density (Reinhart model) \n"
                            "or not (Tregenza one).")
                            ).sky_matrix_high_density = False
        if not "direct_diffuse_values" in pl:
            obj.addProperty("App::PropertyBool",
                            "direct_diffuse_values", "04_Analysis_results",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Visualize direct and diffuse analysis")
                            ).direct_diffuse_values = False
        if not "direct_values" in pl:
            obj.addProperty("App::PropertyFloatList",
                            "direct_values", "04_Analysis_results",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Direct radiation/irradiance values "
                            "- read only")
                            ).direct_values = []
        if not "diffuse_values" in pl:
            obj.addProperty("App::PropertyFloatList",
                            "diffuse_values", "04_Analysis_results",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Diffuse radiation/irradiance values "
                            "- read only")
                            ).diffuse_values = []
        if not "total_values" in pl:
            obj.addProperty("App::PropertyFloatList",
                            "total_values", "04_Analysis_results",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Total radiation/irradiance values "
                            "- read only")
                            ).total_values = []
        if not "sun_vector_values" in pl:
            obj.addProperty("App::PropertyVectorList",
                            "sun_vector_values", "04_Analysis_results",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Sun path vectors values "
                            "- read only")
                            ).sun_vector_values = []
        if not "sun_hour_values" in pl:
            obj.addProperty("App::PropertyFloatList",
                            "sun_hour_values", "04_Analysis_results",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Sun hour values "
                            "- read only")
                            ).sun_hour_values = []
        # 05 Legend
        if not "leg_title" in pl:
            obj.addProperty("App::PropertyString",
                            "leg_title", "05_Legend",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Sun analysis legend title "
                            "- read only")
                            ).leg_title = ""
        if not "leg_position" in pl:
            obj.addProperty("App::PropertyVector",
                            "leg_position", "05_Legend",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Base left position of legend "
                            "bar in mm (x, y, z) \n"
                            "- read only")
                            ).leg_position = (0.0, 0.0, 0.0)
        if not "leg_height" in pl:
            obj.addProperty("App::PropertyFloat",
                            "leg_height", "05_Legend",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Height of legend bar in mm "
                            "(x, y, z) - read only")
                            ).leg_height = 11000
        if not "leg_width" in pl:
            obj.addProperty("App::PropertyFloat",
                            "leg_width", "05_Legend",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Width of legend bar in mm "
                            "(x, y, z) - read only")
                            ).leg_width = 1000
        if not "color_count" in pl:
            obj.addProperty("App::PropertyInteger",
                            "color_count", "05_Legend",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Number of segments of legend bar "
                            "(default = 11).")
                            ).color_count = 11
        if not "metadata" in pl:
            obj.addProperty("App::PropertyStringList",
                            "metadata", "05_Legend",
                            QT_TRANSLATE_NOOP("App::Property",
                            "Metadata - read only")
                            ).metadata = []
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
                            "color_set", "05_Legend",
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

class SunAnalysisViewProvider:

    """A View Provider for the SunAnalysis object"""

    def __init__(self, obj):
        obj.Proxy = self

    def getIcon(self):
        __dir__ = os.path.dirname(__file__)
        return __dir__ + '/icons/SunAnalysisIcon.svg'

class CreateSunAnalysis:

    """Create a Sun Analysis as colored subfaces."""

    def QT_TRANSLATE_NOOP(self, text):
        return text

    def GetResources(self):
        __dir__ = os.path.dirname(__file__)
        return {'Pixmap': __dir__ + '/icons/CreateSunAnalysisIcon.svg',
                'MenuText': QT_TRANSLATE_NOOP('CreateSunAnalysis', 'Create a Sun Analysis'),
                'ToolTip': QT_TRANSLATE_NOOP('CreateSunAnalysis',
                           'First, select the group containing the objects \n'
                           'to be analyzed, created previously, then click \n'
                           'this button to configure the analysis.\n'
                           'You need to select an epw file and choose \n'
                           'the objects to be analyzed, \n'
                           'as well as their context.')}

    def IsActive(self):
        if Gui.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        activated_create_sun_analysis(self)

class ModifySunAnalysis:

    """Modify a Sun Analysis."""

    def QT_TRANSLATE_NOOP(self, text):
        return text

    def GetResources(self):
        __dir__ = os.path.dirname(__file__)
        return {'Pixmap': __dir__ + '/icons/ModifySunAnalysisIcon.svg',
                'MenuText': QT_TRANSLATE_NOOP('ModifySunAnalysis', 'Modify a Sun Analysis'),
                           'ToolTip': QT_TRANSLATE_NOOP('ModifySunAnalysis',
                                      'Select a Sun Analysis, click this button to \n'
                                      'open the dialog and modify its configuration.')}

    def IsActive(self):
        if Gui.ActiveDocument:
            try:
                FreeCAD.ActiveDocument.findObjects(Name = "SunAnalysis")[0].Name
                return True
            except:
                pass
        else:
            return False

    def Activated(self):
        activated_modify_sun_analysis(self)

class DeleteSunAnalysis:

    """Delete a selected Sun Analysis."""

    def QT_TRANSLATE_NOOP(self, text):
        return text

    def GetResources(self):
        __dir__ = os.path.dirname(__file__)
        return {'Pixmap': __dir__ + '/icons/DeleteSunAnalysisIcon.svg',
                'MenuText': QT_TRANSLATE_NOOP('DeleteSunAnalysis', 'Delete a Sun Analysis'),
                             'ToolTip': QT_TRANSLATE_NOOP('DeleteSunAnalysis',
                                        'Select a Sun Analysis, click this button \n'
                                        'to delete it.\n'
                                        'Be careful, you will not be able to \n'
                                        'undo this action!')}

    def IsActive(self):
        if Gui.ActiveDocument:
            try:
                FreeCAD.ActiveDocument.findObjects(Name = "SunAnalysis")[0].Name
                return True
            except:
                pass
        else:
            return False

    def Activated(self):
        activated_delete_sun_analysis(self)

def activated_create_sun_analysis(self):

    """Create the SunAnalysis"""

    global SA
    global SA_NEW
    try:
        sel_objs_group = []
        sel_objs_group = Gui.Selection.getSelection()
        if sel_objs_group[0].Name[0:5] == "Group":
            objs_group = sel_objs_group[0]
        else:
            FreeCAD.Console.PrintMessage(translate("SunAnalysis",
                "The selection is not a Group!") + "\n")
            return
    except Exception:
        FreeCAD.Console.PrintMessage(translate("SunAnalysis",
            "To create a new Sun Analysis, you must select a group \n"
            "that contents all objects to be analyzed!") + "\n")
        return
    folder = FreeCAD.ActiveDocument.addObject(
             'App::DocumentObjectGroupPython',
             'SunAnalysis')
    SunAnalysis(folder)
    SunAnalysisViewProvider(folder.ViewObject)
    SA = folder
    SA.objs_group = objs_group
    print(f"create Sun Analysis: SA = {SA.Name}")
    SA_NEW = True
    SunAnalysisDialog.open_sun_analysis_configuration()
    FreeCAD.ActiveDocument.recompute()

def activated_modify_sun_analysis(self):

    """Modify the Sun Analysis selected"""

    global SA
    global SA_NEW
    SA_NEW = False
    SA = select_sun_analysis()
    if SA is not None:
        print(f"activated modify sun_analysis: SA = {SA.Name}")
        SunAnalysisDialog.open_sun_analysis_configuration()
    else:
        FreeCAD.Console.PrintMessage(translate("SunAnalysis",
            "To modify a set of Sun Analysis, first you must select one!") + "\n")

def activated_delete_sun_analysis(self):

    """Delete the SunAnalysis selected"""

    try:
        selection = select_sun_analysis()
        if selection is not None:
            print(f"activated delete sun analysis: SA = {selection.Name}")
            delete_sun_analysis(selection)
        else:
            FreeCAD.Console.PrintMessage(translate("SunAnalysis",
             "To delete a Sun Analysis, first you must select one!") + "\n")
    except Exception:
        FreeCAD.Console.PrintMessage(translate("SunAnalysis",
            "To delete a set of Sun Analysis, first you must select one!") + "\n")

def select_sun_analysis():

    """Select a Sun Analysis"""

    SA = None
    selection = []
    selection = Gui.Selection.getSelection()
    try:
        selection[0]
        if selection[0].Name[0:11] == "SunAnalysis":
            SA = selection[0]
            return SA
        else:
            FreeCAD.Console.PrintMessage(translate("SunAnalysis",
                "Warning: The object selected is not a Sun Analysis!") + "\n")
    except:
        FreeCAD.Console.PrintMessage(translate("SunAnalysis",
                              "There is no selection!") + "\n")

#=================================================
# B. General functions
#=================================================

def tessellate_to_compound(selection = None,
                           max_length = None,
                           only_objs = False
                           ):

    """Tressellate the objects selected,
    return as face tris or a compound"""

    doc = FreeCAD.ActiveDocument

    #get main faces from selected object
    sel = selection
    total_objs_tris = []
    for o in range(len(sel)):
        target_obj = sel[o]
        #mesh
        __mesh=doc.addObject("Mesh::Feature","Mesh")
        __part=doc.getObject(target_obj.Name)
        __shape=Part.getShape(__part,"")
        __mesh.Mesh=MeshPart.meshFromShape(Shape = __shape,
                                           MaxLength = max_length)
        del __shape
        #obj1
        obj1_n = "obj" + str(o + 1)
        obj1 = doc.addObject('Part::Feature', 'Analysis_' + obj1_n)
        __shape__ = Part.Shape()
        __shape__.makeShapeFromMesh(
                  FreeCAD.getDocument(doc.Name).getObject(
                  __mesh.Name).Mesh.Topology, 0.100000, False)
        doc.getObject(obj1.Name).Shape = __shape__
        doc.getObject(obj1.Name).purgeTouched()
        #get face tris
        total_objs_tris.append(obj1)
        del __shape__
        doc.removeObject(__mesh.Name)
        target_obj.Visibility = False
    #compound total faces
    if only_objs is True:
        FreeCAD.ActiveDocument.recompute()
        return total_objs_tris
    else:
        faces_compound = FreeCAD.activeDocument().addObject(
                                       "Part::Compound",
                                       "Total_SunAnalysis_compound")
        faces_compound.Label = translate("SunAnalysis",
                                       "Total Sun Analysis")
        faces_compound.Links = total_objs_tris
        FreeCAD.ActiveDocument.recompute()
        return faces_compound

def tessellate_to_lb_faces(selection = None
                           ):

    """Tressellate the objects selected,
    return lb Face3D tris"""

    doc = FreeCAD.ActiveDocument
    sel = selection
    context_obj_lb_faces3D = []
    for o in range(len(sel)):
        context_obj = sel[o]
        #mesh
        __mesh=doc.addObject("Mesh::Feature","Mesh")
        __part=doc.getObject(context_obj.Name)
        __shape=Part.getShape(__part,"")
        __mesh.Mesh=MeshPart.meshFromShape(Shape=__shape, LinearDeflection=1000, #LinearDeflection=0.1
                                           AngularDeflection=0.523599, Relative=False)
        del __shape
        #obj2
        obj2 = doc.addObject('Part::Feature', 'tel_faces_obj')
        __shape__ = Part.Shape()
        __shape__.makeShapeFromMesh(
                  FreeCAD.getDocument(doc.Name).getObject(
                  __mesh.Name).Mesh.Topology, 0.100000, False)

        doc.getObject(obj2.Name).Shape = __shape__
        doc.getObject(obj2.Name).purgeTouched()
        del __shape__
        doc.removeObject(__mesh.Name)
        #get lb FAce3D tris
        for t in range(len(obj2.Shape.Faces)):
            face3D = LBComponents.convert_face3D(obj2.Shape.Faces[t])
            context_obj_lb_faces3D.append(face3D)
        doc.removeObject(obj2.Name)

    FreeCAD.ActiveDocument.recompute()
    return context_obj_lb_faces3D

def get_leg_pos(study_objs = None,
                    study_context = None,
                    color_count = None
                    ):

    """Getting the legend positions
    from the boundaries of the analyzed objects."""

    #get max boundary of all objects
    posx = []
    posy = []
    for o in range(len(study_objs)):
        study_obj = study_objs[o]
        x1 = study_obj.Shape.BoundBox.XMax
        posx.append(x1)
        x2 = study_obj.Shape.BoundBox.XMin
        posx.append(x2)
        y1 = study_obj.Shape.BoundBox.YMax
        posy.append(y1)
        y2 = study_obj.Shape.BoundBox.YMin
        posy.append(y2)
    for c in range(len(study_context)):
        context_obj = study_context[c]
        x1 = context_obj.Shape.BoundBox.XMax
        posx.append(x1)
        x2 = context_obj.Shape.BoundBox.XMin
        posx.append(x2)
        y1 = context_obj.Shape.BoundBox.YMax
        posy.append(y1)
        y2 = context_obj.Shape.BoundBox.YMin
        posy.append(y2)
    #print(f"posx:{posx}")
    #print(f"posy:{posy}")
    #get legend position1
    #boundaries
    max_x = max(posx)
    max_y = max(posy)
    min_x = min(posx)
    min_y = min(posy)
    #get legend bar position 1
    max_side = max((max_x - min_x), (max_y - min_y))
    deltx1 = max_side/5
    leg_bar_position1 = ((max_x + deltx1), min_y, 0)
    #get legend height and width
    bar_leg_height = (max_y - min_y)
    bar_leg_width = bar_leg_height/color_count
    #get clone position 1 and 2
    deltx2 = (max_x - min_x) + deltx1 + bar_leg_width
    clone_position1 = (deltx2, 0, 0)
    clone_position2 = (2*deltx2, 0, 0)
    #get legend position 1, 2 and 3
    main_leg_position1 = (min_x, (min_y - deltx1), 0)
    main_leg_position2 = (min_x + deltx2, (min_y - deltx1), 0)
    main_leg_position3 = (min_x + 2*deltx2, (min_y - deltx1), 0)
    #get legend bar position 2
    leg_bar_position2 = (max_x + deltx1 + 2*deltx2, min_y, 0)
    #get legend compass position 1, 2 and 3
    x1 = (max_x - min_x) - (max_y - min_y)/12 + min_x
    y1 = (min_y - deltx1) - (max_y - min_y)/12
    compass_leg_position1 = (x1, y1, 0)
    compass_leg_position2 = (x1 + deltx2, y1, 0)
    compass_leg_position3 = (x1 + 2*deltx2, y1, 0)
    return [leg_bar_position1, #0
            leg_bar_position2, #1
            bar_leg_width, #2
            bar_leg_height, #3
            clone_position1, #4
            clone_position2, #5
            main_leg_position1, #6
            main_leg_position2, #7
            main_leg_position3, #8
            compass_leg_position1, #9
            compass_leg_position2, #10
            compass_leg_position3, #11
            ]

#=================================================
# C. Main functions
#=================================================

# C.1 Create Sun Analysis
#------------------------

def create_sun_analysis(study_objs = None,
                        max_length = 1000,
                        study_context = None,
                        period = None,
                        epw_path = None,
                        results = None,
                        color_set = 0,
                        ground_reflectance = 0.2
                        ):

    """Create Sun Analysis object.
    Set the analysis data (EPW, period, location, and north)
    Create the analysis surfaces from target and context objects
    Calculate sun hours or radiations/irradiaces
    Check intersections
    Calculate sun hours
    Calculate sun radiations/irradiaces
    Apply the corresponding color to each subface (study and surrounding objects)
    Get the necessary legends
    """

    doc = FreeCAD.ActiveDocument

    from freecad.Solar.LBComponents import RESUL_00, RESUL_01, RESUL_02

    if SA is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage("create sun analysis: " + translate(
            "SunAnalysis",
            "Sun Analysis object could not be found!") + "\n")
        return
    global SA_NEW
    #epw_path
    if SA.epw_path != "":
        epw_path = SA.epw_path
        if not epw_path or not os.path.isfile(epw_path):
            FreeCAD.Console.PrintMessage("create sun analysis: " + translate(
                "SunAnalysis",
                "For using EPW, please provide a valid file path.") + "\n")
    else:
        FreeCAD.Console.PrintMessage(translate("SunAnalysis",
            "Could not get epw!") + "\n")
        return
    #period
    period = None
    period = AnalysisPeriod(SA.start_month,
                            SA.start_day,
                            SA.start_hour,
                            SA.end_month,
                            SA.end_day,
                            SA.end_hour,
                            int(SA.timestep),
                            SA.leap_year
                            )
    #get metadata
    SA.metadata = []
    SA.metadata = LBComponents.get_metadata(epw_path, period)
    #print(f"SA.metadata: {SA.metadata}")
    #geometries
    if SA.study_objs == [] or SA.study_context == []:
        FreeCAD.Console.PrintMessage(translate("SunAnalysis",
                "There is no study objects or \n"
                "context selected!") + "\n")
        return
    #get study compound
    SA.study_compound = None
    SA.study_compound = tessellate_to_compound(selection = SA.study_objs,
                                               max_length = SA.max_length,
                                               only_objs = False
                                               )
    #get total study group
    study_total_group = doc.addObject('App::DocumentObjectGroup',
                                     'Total_SA_group')
    study_total_group.Label = translate('SunAnalysis',
                                     'Total Sun Analysis Group')
    #doc.getObject(study_total_group.Name).addObject(SA.study_compound)
    SA.addObject(SA.study_compound)
    SA.addObject(study_total_group)
    #get study faces
    faces_tris = SA.study_compound.Shape.Faces
    centroids_normals_lb = LBComponents.get_lb_centroids_normals(faces_tris)
    #study_context Face3D
    tess_context_geom = tessellate_to_lb_faces(SA.study_context
                                               )
    #get legend bar data
    leg_pos = get_leg_pos(study_objs = SA.study_objs,
                              study_context = SA.study_context,
                              color_count = SA.color_count
                              )
    SA.leg_height = leg_pos[3]
    #print(f"color_set: {int(SA.color_set[0:2])}")
    title = " "
    # Get direct sunlight (Sun hours)
    if SA.results[0:2] == "00":
        get_modify_sun_hours(period,
                            centroids_normals_lb,
                            tess_context_geom,
                            leg_pos,
                            study_total_group,
                            modify = False
                            )
        title = f"{RESUL_00}"
    else:
        if SA.results[0:2] == "01":
            title = f"{RESUL_01}"
        if SA.results[0:2] == "02":
            title = f"{RESUL_02}"
        get_modify_sun_radiation(epw_path,
                                 period,
                                 ground_reflectance,
                                 centroids_normals_lb,
                                 tess_context_geom,
                                 title,
                                 leg_pos,
                                 study_total_group,
                                 modify = False
                                 )
    SA.Label = translate("SunAnalysis",
               "Sun Analysis {} - {}").format(SA.city, title)
    SA.leg_title = title
    SA_NEW = False
    Gui.SendMsgToActiveView("ViewFit")
    Gui.runCommand('Std_ViewGroup',2)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(SA)
    FreeCAD.Console.PrintMessage(translate('SunAnalysis',
                                "Sun Analysis created! \n"
                                "Do not modify their original structure of groups \n"
                                "to make possible further adjustments.") + "\n")
    FreeCAD.ActiveDocument.recompute()

def get_modify_sun_hours(period = None,
                         centroids_normals_lb = None,
                         tess_context_geom = None,
                         leg_pos = None,
                         study_total_group = None,
                         modify = False
                         ):

    """Create or modify sun hour analysis."""

    if SA is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage("get modify sun hours: " + translate(
            "SunAnalysis",
            "Sun Analysis object could not be found!") + "\n")
        return

    doc = FreeCAD.ActiveDocument
    from freecad.Solar.LBComponents import RESUL_00
    print("getting sun hours results...")
    #lb sun vectors
    lb_sun_vectors = LBComponents.get_sun_lb_vectors(SA.latitude,
                                                     SA.longitude,
                                                     SA.time_zone,
                                                     -SA.north,
                                                     #SA.daylight_saving,
                                                     period)
    SA.sun_vector_values = []
    SA.sun_vector_values = LBComponents.convert_lb_vectors(
                        lb_vectors = lb_sun_vectors
                        )
    #get inter_matrix_bools
    inter_matrix_bools = intersection_matrix(vectors = lb_sun_vectors,
                        points = centroids_normals_lb[0],
                        normals = centroids_normals_lb[1],
                        context_geometry = tess_context_geom,
                        offset_distance = SA.offset_distance,
                        numericalize = False,
                        sim_folder = None,
                        use_radiance_mesh = False
                        )
    #get sun hours values
    #calculate sun hours
    SA.sun_hour_values = []
    SA.sun_hour_values = LBComponents.calculate_sun_hours(inter_matrix_bools,
                                                         SA.timestep
                                                         )
    #return SA.sun_hours_results
    title = f"{RESUL_00}"
    leg_title = translate("SunAnalysis",
                                  "Sun hours")
    SA.leg_position = leg_pos[0]
    pos1 = leg_pos[6]
    pos2 = None
    pos3 = None
    SA.leg_title = title
    SA.leg_width = leg_pos[2]
    compass_main_leg_created = False
    try:
        SA.Group[1].Group[1].Group[0] #main legend
    except Exception:
        print ("getting main legends...")
        main_leg_groups = LBComponents.get_main_legends(pos1,
                                      pos2,
                                      pos3,
                                      units = title,
                                      metadata = SA.metadata,
                                      text_high = SA.leg_width/2,
                                      )

        #get compass legends
        compass_groups = LBComponents.get_compass_group(center = leg_pos[9],
                                 radius = SA.leg_height/12,
                                 north = float(SA.north),
                                 variation_angle = 90,
                                 total_group = main_leg_groups[0],
                                 direct_group = main_leg_groups[1],
                                 diffuse_group = main_leg_groups[2],
                                 deltx = leg_pos[10][0] - leg_pos[9][0]
                                 )
        compass_main_leg_created = True
    if modify == False:
        print("getting legend bar and colors...")
        bar_leg = LBComponents.get_modify_legend_bar(bar_obj = None, # legend array obj
                                           text_leg_group = None, # legend text group
                                           title = leg_title,
                                           values = SA.sun_hour_values,
                                           position = SA.leg_position,
                                           seg_height = SA.leg_width,
                                           seg_width = SA.leg_width,
                                           seg_count = SA.color_count,
                                           color_leg_set = int(SA.color_set[0:2])
                                           )
        bar_leg_group = bar_leg[0]
        doc.getObject(study_total_group.Name).addObject(bar_leg_group)
        doc.getObject(study_total_group.Name).addObject(main_leg_groups[0])
        doc.getObject(main_leg_groups[0].Name).addObject(compass_groups[0])
    else:
        print("updating legend bar and colors...")
        #Update leg bar data
        seg_height = SA.leg_height/SA.color_count
        SA.leg_width = seg_height
        bar_leg = LBComponents.get_modify_legend_bar(bar_obj = SA.Group[1].Group[0].Group[0],
                                                   text_leg_group = SA.Group[1].Group[0].Group[1],
                                                   title = title,
                                                   values = SA.sun_hour_values,
                                                   position = SA.leg_position,
                                                   seg_height = seg_height,
                                                   seg_width = SA.leg_width,
                                                   seg_count = SA.color_count,
                                                   color_leg_set = int(SA.color_set[0:2])
                                                   )
        if compass_main_leg_created == False:
            print ("updating main legends...")
            LBComponents.modify_main_legends(
                                     main_leg1 = SA.Group[1].Group[1].Group[0],
                                     main_leg2 = None,
                                     main_leg3 = None,
                                     pos1 = pos1,
                                     pos2 = pos2,
                                     pos3 = pos3,
                                     unit = SA.leg_title,
                                     metadata = SA.metadata,
                                     modify_position = True,
                                     modify_values = True,
                                     font_size = SA.leg_width/2
                                     )
            #modify compass
            LBComponents.modify_compass(center = leg_pos[9],
                                        radius = SA.leg_height/12,
                                        north = float(SA.north),
                                        variation_angle = 90,
                                        sky_domes_group = None,
                                        sun_analysis_group = SA,
                                        deltx = leg_pos[10][0] - leg_pos[9][0]
                                        )
        #remove direct an diffuse groups and clones
        try:
            doc.getObject(SA.Group[2].Group[1].Name).removeObjectsFromDocument()#direct main leg group content
            doc.getObject(SA.Group[3].Group[1].Name).removeObjectsFromDocument()#diffuse main leg group content
            doc.getObject(SA.Group[2].Name).removeObjectsFromDocument()#direct group content
            doc.getObject(SA.Group[3].Name).removeObjectsFromDocument()#direct group content
            doc.removeObject(SA.Group[2].Name)#direct group
            doc.removeObject(SA.Group[2].Name)#direct group
            doc.recompute()
        except:
            pass
    print("getting Sun Analysis colors...")
    f_colors_total = LBComponents.get_face_colors(sun_analysis_results = SA.sun_hour_values,
                                                   domain = SA.sun_hour_values,
                                                   leg_colors = bar_leg[1]
                                                   )
    print("applying face colors...")
    LBComponents.apply_color_faces(obj = SA.study_compound,
                                   face_colors = f_colors_total)
    try:
        total_compass = compass_groups[3]
    except Exception:
        total_compass = SA.Group[1].Group[1].Group[1].Group[0]
    color = bar_leg[-1][-1]
    color_rgb = (color[0], color[1], color[2])
    total_compass.ViewObject.ShapeAppearance = FreeCAD.Material(
                                    DiffuseColor = color_rgb)

def get_modify_sun_radiation(epw_path = "",
                             period = None,
                             ground_reflectance = 0.2,
                             centroids_normals_lb = None,
                             tess_context_geom = None,
                             title = "",
                             leg_pos = None,
                             study_total_group = None,
                             modify = False
                             ):

    """Create or modify sun radiation/irradiance analysis object."""

    doc = FreeCAD.ActiveDocument
    pos1 = leg_pos[6]
    pos2 = leg_pos[7]
    pos3 = leg_pos[8]
    #Verify direc study clones
    try:
        study_direct_clone = SA.Group[2].Group[0]
        study_diffuse_clone = SA.Group[3].Group[0]
    except Exception:
        #create direc study clone and group, rename total
        direct_diffuse_clones_groups = get_direct_diffuse_analysis(SA.study_compound,
                                                              leg_pos
                                                              )
        study_direct_clone = direct_diffuse_clones_groups[1]
        study_direct_group = direct_diffuse_clones_groups[2]
        study_diffuse_clone = direct_diffuse_clones_groups[3]
        study_diffuse_group  = direct_diffuse_clones_groups[4]
    #leg_title = title
    # Get sky radiations
    print("gettind sun radiations results...")
    #get sky dome radiation values
    high_density = False
    if SA.sky_matrix_high_density is True:
        high_density = True
    irradiance = False
    if SA.results[0:2] == "02":
        irradiance = True
    radiation_values = LBComponents.get_sky_matrix_dome_values(epw_path,
                            period,
                            high_density,
                            plot_irradiance = irradiance,
                            timestep = int(SA.timestep),
                            center_vectors = False,
                            ground_reflectance = 0.2
                            )
    #print(f"radiation_values: {radiation_values}")
    total_values = radiation_values[0]
    total_grd_val = (sum(total_values) / len(total_values)) * ground_reflectance
    total_ground_rad = [total_grd_val] * len(total_values)
    all_total_rad = total_values + total_ground_rad

    direct_values = radiation_values[1]
    direct_grd_val = (sum(direct_values) / len(direct_values)) * ground_reflectance
    direct_ground_rad = [direct_grd_val] * len(direct_values)
    all_direct_rad = direct_values + direct_ground_rad

    diffuse_values = radiation_values[2]
    diffuse_grd_val = (sum(diffuse_values) / len(diffuse_values)) * ground_reflectance
    diffuse_ground_rad = [diffuse_grd_val] * len(diffuse_values)
    all_diffuse_rad = diffuse_values + diffuse_ground_rad

    hoys = [h for h in period.hoys]
    try:
        sky_matrix = SkyMatrix.from_epw(SA.epw_path, hoys) # Radiance must be installed
        sky_matrix.north = - float(SA.north)
    except Exception:
        FreeCAD.Console.PrintMessage("get modify Sun Radiation: " + translate("SunAnalysis",
            "For getting irradiance values, Radiance software must be \n"
            "installed in your machine.") + "\n")
        return
    #get sky matrix cosine intersections
    sky_inter_matrix_cosines = sky_intersection_matrix(sky_matrix,
                                                       centroids_normals_lb[0],
                                                       centroids_normals_lb[1],
                                                       tess_context_geom,
                                                       offset_distance=SA.offset_distance,
                                                       numericalize=True,
                                                       sim_folder=None,
                                                       use_radiance_mesh=False
                                                       )
    total_radiation_values = [
                    sum(r * w for r, w in zip(pt_rel, all_total_rad))
                    for pt_rel in sky_inter_matrix_cosines
                    ]
    direct_radiation_values = [
                    sum(r * w for r, w in zip(pt_rel, all_direct_rad))
                    for pt_rel in sky_inter_matrix_cosines
                    ]
    diffuse_radiation_values = [
                    sum(r * w for r, w in zip(pt_rel, all_diffuse_rad))
                    for pt_rel in sky_inter_matrix_cosines
                    ]
    #print(f"sky_inter_matrix_cosines: {sky_inter_matrix_cosines}")
    SA.total_values = []
    SA.direct_values = []
    SA.diffuse_values = []
    SA.total_values = total_radiation_values
    SA.direct_values = direct_radiation_values
    SA.diffuse_values = diffuse_radiation_values
    total_values = SA.total_values
    direct_values = SA.direct_values
    diffuse_values = SA.diffuse_values
    if SA.direct_diffuse_values == False:
        SA.leg_position = leg_pos[0]
    else:
        SA.leg_position = leg_pos[1]
    SA.leg_width = leg_pos[2]
    compass_main_leg_created = False
    try:
        SA.Group[2].Group[1].Group[0] #direct main legend
        SA.Group[3].Group[1].Group[0] #diffuse main legend
    except Exception:
        try:
            SA.Group[1].Group[1].Group[0] #total main legend
            compass_links = SA.Group[1].Group[1].Group[1].Group[0].Links
            links1 = len(compass_links)
            for i in range(links1):
                doc.removeObject(SA.Group[1].Group[1].Group[1].Group[0].Links[0].Name) #compass link
            doc.getObject(SA.Group[1].Group[1].Name).removeObjectsFromDocument() #Total main legend group content
            doc.removeObject(SA.Group[1].Group[1].Name) #Total main legend group
            doc.recompute()
        except:
            pass
        print ("getting main legends...")
        main_leg_groups = LBComponents.get_main_legends(pos1,
                                          pos2,
                                          pos3,
                                          units = title,
                                          metadata = SA.metadata,
                                          text_high = SA.leg_width/2,
                                          )
        #get compass legends
        compass_groups = LBComponents.get_compass_group(center = leg_pos[9],
                                     radius = SA.leg_height/12,
                                     north = float(SA.north),
                                     variation_angle = 90,
                                     total_group = main_leg_groups[0],
                                     direct_group = main_leg_groups[1],
                                     diffuse_group = main_leg_groups[2],
                                     deltx = leg_pos[10][0] - leg_pos[9][0]
                                     )
        doc.getObject(main_leg_groups[0].Name).addObject(compass_groups[0])
        doc.getObject(main_leg_groups[1].Name).addObject(compass_groups[1])
        doc.getObject(main_leg_groups[2].Name).addObject(compass_groups[2])
        compass_main_leg_created = True
    except:
        pass
    if modify == False:
        print("getting legend bar and colors...")
        bar_leg = LBComponents.get_modify_legend_bar(bar_obj = None, # legend array obj
                                       text_leg_group = None, # legend text group
                                       title = title,
                                       values = SA.total_values,
                                       position = SA.leg_position,
                                       seg_height = SA.leg_width,
                                       seg_width = SA.leg_width,
                                       seg_count = SA.color_count,
                                       color_leg_set = int(SA.color_set[0:2])
                                       )
        leg_bar_group = bar_leg[0]
        doc.getObject(study_total_group.Name).addObject(leg_bar_group)
    else:
        study_direct_group = SA.Group[2]
        study_diffuse_group = SA.Group[3]
        print("updating legend bar and colors...")
        #Update leg bar data
        seg_height = SA.leg_height/SA.color_count
        SA.leg_width = seg_height
        SA.leg_title = title
        bar_leg = LBComponents.get_modify_legend_bar(bar_obj = SA.Group[1].Group[0].Group[0],
                                                   text_leg_group = SA.Group[1].Group[0].Group[1],
                                                   title = title,
                                                   values = SA.total_values,
                                                   position = SA.leg_position,
                                                   seg_height = seg_height,
                                                   seg_width = SA.leg_width,
                                                   seg_count = SA.color_count,
                                                   color_leg_set = int(SA.color_set[0:2])
                                                   )
        if compass_main_leg_created is False:
            print ("updating main legends...")
            LBComponents.modify_main_legends(
                                         main_leg1 = SA.Group[1].Group[1].Group[0],
                                         main_leg2 = SA.Group[2].Group[1].Group[0],
                                         main_leg3 = SA.Group[3].Group[1].Group[0],
                                         pos1 = pos1,
                                         pos2 = pos2,
                                         pos3 = pos3,
                                         unit = SA.leg_title,
                                         metadata = SA.metadata,
                                         modify_position = True,
                                         modify_values = True,
                                         font_size = SA.leg_width/2
                                         )
            #modify compass
            LBComponents.modify_compass(center = leg_pos[9],
                                            radius = SA.leg_height/12,
                                            north = float(SA.north),
                                            variation_angle = 90,
                                            sky_domes_group = None,
                                            sun_analysis_group = SA,
                                            deltx = leg_pos[10][0] - leg_pos[9][0]
                                            )
    try:
        total_main_leg_group = main_leg_groups[0]
        direct_main_leg_group = main_leg_groups[1]
        diffuse_main_leg_group = main_leg_groups[2]
    except Exception:
        total_main_leg_group = SA.Group[1].Group[1]
        direct_main_leg_group = SA.Group[2].Group[1]
        diffuse_main_leg_group = SA.Group[3].Group[1]
    doc.getObject(study_total_group.Name).addObject(total_main_leg_group)
    doc.getObject(study_direct_group.Name).addObject(direct_main_leg_group)
    doc.getObject(study_diffuse_group.Name).addObject(diffuse_main_leg_group)
    print("getting Sun Analysis colors...")
    f_colors_total = LBComponents.get_face_colors(sun_analysis_results = total_values,
                                               domain = total_values,
                                               leg_colors = bar_leg[1]
                                               )
    f_colors_direct = LBComponents.get_face_colors(sun_analysis_results = direct_values,
                                                   domain = total_values,
                                                   leg_colors = bar_leg[1]
                                                   )
    f_colors_diffuse = LBComponents.get_face_colors(sun_analysis_results = diffuse_values,
                                                   domain = total_values,
                                                   leg_colors = bar_leg[1]
                                                   )
    print("applying face colors...")
    LBComponents.apply_color_faces(obj = SA.study_compound,
                               face_colors = f_colors_total)
    LBComponents.apply_color_faces(obj = study_direct_clone,
                                   face_colors = f_colors_direct)
    LBComponents.apply_color_faces(obj = study_diffuse_clone,
                                   face_colors = f_colors_diffuse)
    try:
        total_compass = compass_groups[3]
        direct_compass = compass_groups[4]
        diffuse_compass = compass_groups[5]
    except Exception:
        total_compass = SA.Group[1].Group[1].Group[1].Group[0]
        direct_compass = SA.Group[2].Group[1].Group[1].Group[0]
        diffuse_compass = SA.Group[3].Group[1].Group[1].Group[0]
    color = bar_leg[-1][-1]
    color_rgb = (color[0], color[1], color[2])
    total_compass.ViewObject.ShapeAppearance = FreeCAD.Material(
                                    DiffuseColor = color_rgb)
    direct_compass.ViewObject.ShapeAppearance = FreeCAD.Material(
                                    DiffuseColor = color_rgb)
    diffuse_compass.ViewObject.ShapeAppearance = FreeCAD.Material(
                                    DiffuseColor = color_rgb)
    #groups
    doc.getObject(study_direct_group.Name).Visibility = SA.direct_diffuse_values
    doc.getObject(study_diffuse_group.Name).Visibility = SA.direct_diffuse_values

def get_direct_diffuse_analysis(study_compound = None,
                           leg_pos = None
                           ):

    """Get study clones and their groups"""

    doc = FreeCAD.ActiveDocument
    from freecad.Solar.LBComponents import RESUL_01, RESUL_02

    #get direc study clone and group
    study_direct_clone = LBComponents.get_analysis_clone(compound = study_compound,
                                                  obj_label = translate("SunAnalysis",
                                                                "Direct Sun Analysis"),
                                                  analysis_group = SA
                                                  )
    study_direct_group = doc.addObject('App::DocumentObjectGroup',
                                     'Direct_SA_group')
    study_direct_group.Label = translate('SunAnalysis',
                                     'Direct Sun Analysis Group')
    doc.getObject(study_direct_group.Name).addObject(study_direct_clone)
    SA.addObject(study_direct_group)
    #get diffuse study clone and group
    study_diffuse_clone = LBComponents.get_analysis_clone(compound = study_compound,
                                                  obj_label = translate("SunAnalysis",
                                                               "Diffuse Sun Analysis"),
                                                  analysis_group = SA
                                                  )
    study_diffuse_group = doc.addObject('App::DocumentObjectGroup',
                                     'Diffuse_SA_group')
    study_diffuse_group.Label = translate('SunAnalysis',
                                     'Diffuse Sun Analysis Group')
    doc.getObject(study_diffuse_group.Name).addObject(study_diffuse_clone)
    SA.addObject(study_diffuse_group)
    #get clone positions
    pl1 = FreeCAD.Placement()
    pl1.Base = FreeCAD.Vector(leg_pos[4])
    study_direct_clone.Placement = pl1
    pl2 = FreeCAD.Placement()
    pl2.Base = FreeCAD.Vector(leg_pos[5])
    study_diffuse_clone.Placement = pl2
    #get study label and main title text
    if SA.results[0:2] == "01":
        print("getting radiation results...")
        title = f"{RESUL_01}"
    if SA.results[0:2] == "02":
        print("getting irradiance results...")
        title = f"{RESUL_02}"
    return [title, #0
            study_direct_clone, #1
            study_direct_group, #2
            study_diffuse_clone, #3
            study_diffuse_group #4
            ]

def direct_diffuse_visualization():

    """Manage direct and diffuse analysis visualization
    and legend bar position"""

    if SA is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage("direct diffuse visualization: " + translate(
            "SunAnalysis",
            "Sun Analysis object could not be found!") + "\n")
        return
    #update direct and diffuse analysis visualization
    try:
        doc = FreeCAD.ActiveDocument
        doc.getObject(SA.Group[2].Name).Visibility = SA.direct_diffuse_values #direct group
        doc.getObject(SA.Group[3].Name).Visibility = SA.direct_diffuse_values #diffuse group
        try:
            #update legend and bar positions
            leg_pos = get_leg_pos(study_objs = SA.study_objs,
                                      study_context = SA.study_context,
                                      color_count = SA.color_count
                                      )
            SA.leg_height = leg_pos[3]
            #update leg bar position
            if SA.direct_diffuse_values == False:
                SA.leg_position = leg_pos[0]
            else:
                SA.leg_position = leg_pos[1]
            bar_obj = SA.Group[1].Group[0].Group[0]
            bar_obj.Base.Placement.Base = FreeCAD.Vector(SA.leg_position)
            #update text leg bar positions
            text_leg = SA.Group[1].Group[0].Group[1].Group
            for i in range(len(text_leg)):
                text = text_leg[i]
                text.Placement.Base.x = SA.leg_position.x + SA.leg_width
        except Exception:
            FreeCAD.Console.PrintMessage(translate("SunAnalysis",
                           "It was not possible to update bar legend position!") + "\n")
    except Exception:
        FreeCAD.Console.PrintMessage(translate("SunAnalysis",
                           "There is no direct and diffuse analysis!") + "\n")
    doc.recompute()

# C.2 Modify Sun Analysis
#------------------------

def modify_sun_analysis(forms = False,
                        values_colors = False,
                        colors = False
                        ):

    """Modify a selected Sun Analysis object"""

    if SA is not None:
        pass
    else:
        FreeCAD.Console.PrintMessage("modify sun analysis: " + translate(
            "SunAnalysis",
            "Attempting to get Sun Analysis values: "
            "Sun Analysis object could not be found!") + "\n")
        return
    global SA_NEW
    #epw_path
    if SA.epw_path != "":
        epw_path = SA.epw_path
        if not epw_path or not os.path.isfile(epw_path):
            FreeCAD.Console.PrintMessage("modify sun analysis: " + translate(
                "SunAnalysis",
                "For using EPW, please provide a valid file path.") + "\n")
    else:
        FreeCAD.Console.PrintMessage("modify sun analysis: " + translate(
            "SunAnalysis",
            "Could not get epw!") + "\n")
        return
    #period
    period = None
    period = AnalysisPeriod(SA.start_month,
                            SA.start_day,
                            SA.start_hour,
                            SA.end_month,
                            SA.end_day,
                            SA.end_hour,
                            int(SA.timestep),
                            SA.leap_year
                            )
    if forms is True:
        update_sun_analys_forms(epw_path, period)
        print("updated forms!")
    if values_colors is True:
        update_sun_analysis_values_colors(epw_path, period)
        print("updated values!")
    if colors is True:
        update_sun_analysis_colors()
        print("updated values!")
    Gui.SendMsgToActiveView("ViewFit")
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(SA)
    FreeCAD.ActiveDocument.recompute()

def update_sun_analys_forms(epw_path = None,
                            period = None
                            ):

    """Update forms in a selected Sun Analysis object"""

    #check geometries
    if SA.study_objs != [] and SA.study_context != []:
        for o in range(len(SA.study_context)):
            SA.study_context[o].Visibility = True
    else:
        FreeCAD.Console.PrintMessage("update sun analys forms: " + translate(
            "SunAnalysis",
            "There is no study objects!") + "\n")
        return
    obj_list1 = []
    obj_list2 = []
    for dep_obj in SA.study_compound.OutList:
        obj_list1.append(dep_obj)
    #update study compound - obj_list2
    obj_list2 = tessellate_to_compound(selection = SA.study_objs,
                                               max_length = SA.max_length,
                                               only_objs = True)
    SA.study_compound.Links = obj_list2
    #remove compound obj_list1
    for objs1 in obj_list1:
        FreeCAD.ActiveDocument.removeObject(objs1.Name)
    FreeCAD.ActiveDocument.recompute()
    try:
        #update legend and bar positions
        leg_pos = get_leg_pos(study_objs = SA.study_objs,
                                  study_context = SA.study_context,
                                  color_count = SA.color_count
                                  )
        SA.leg_height = leg_pos[3]
        #update clone positions
        study_direct_clone = SA.Group[2].Group[0]
        study_diffuse_clone = SA.Group[3].Group[0]
        study_direct_clone.Placement.Base = FreeCAD.Vector(leg_pos[4])
        study_diffuse_clone.Placement.Base = FreeCAD.Vector(leg_pos[5])
    except Exception:
        FreeCAD.Console.PrintMessage("update sun analys forms: " + translate("SunAnalysis",
                "There is no legend position!") + "\n")
    FreeCAD.ActiveDocument.recompute()
    #Get direct sunlight (Sun hours) or radiations
    update_sun_analysis_values_colors(epw_path,
                                      period
                                      )

def update_sun_analysis_values_colors(epw_path = None,
                                      period = None
                                      ):

    """Update the values and colors applied in a selected Sun Analysis object"""

    #doc = FreeCAD.ActiveDocument
    from freecad.Solar.LBComponents import RESUL_00, RESUL_01, RESUL_02

    #update metadata
    SA.metadata = []
    SA.metadata = LBComponents.get_metadata(epw_path, period)

    #get study faces
    faces_tris = SA.study_compound.Shape.Faces
    centroids_normals_lb = LBComponents.get_lb_centroids_normals(faces_tris)
    #study_context Face3D
    tess_context_geom = tessellate_to_lb_faces(SA.study_context
                                               )
    #update legend position and width
    leg_pos = get_leg_pos(study_objs = SA.study_objs,
                              study_context = SA.study_context,
                              color_count = SA.color_count
                              )
    SA.leg_height = leg_pos[3]
    title = ""
    study_total_group = SA.Group[1]
    #get direct sunlight (Sun hours)
    if SA.results[0:2] == "00":
        get_modify_sun_hours(period,
                                 centroids_normals_lb,
                                 tess_context_geom ,
                                 leg_pos,
                                 study_total_group,
                                 modify = True
                                 )
        title = f"{RESUL_00}"     
    #Get sky radiations
    else:
        if SA.results[0:2] == "01":
            title = f"{RESUL_01}"
        if SA.results[0:2] == "02":
            title = f"{RESUL_02}"
        ground_reflectance = 0.2
        get_modify_sun_radiation(epw_path,
                                     period,
                                     ground_reflectance,
                                     centroids_normals_lb,
                                     tess_context_geom,
                                     title,
                                     leg_pos,
                                     study_total_group,
                                     modify = True
                                     )
    SA.Label = translate("SunAnalysis",
    "Sun Analysis {} - {}").format(SA.city, title)

def update_sun_analysis_colors():

    """Update the colors applied in a selected Sun Analysis object"""

    doc = FreeCAD.ActiveDocument
    from freecad.Solar.LBComponents import RESUL_01, RESUL_02
    title1 = " "
    if SA.results[0:2] == "00":
        title1 = " "
        title1 = translate("SunAnalysis", "Sun hours")
        sun_analysis_results = SA.sun_hour_values
        domain = SA.sun_hour_values
    else:
        if SA.results[0:2] == "01":
            title1 = f"{RESUL_01}"
        if SA.results[0:2] == "02":
            title1 = f"{RESUL_02}"
        sun_analysis_results = SA.total_values
        domain = SA.total_values
    #update leg bar data
    seg_height = SA.leg_height/SA.color_count
    SA.leg_width = seg_height
    SA.leg_title = title1
    bar_leg = LBComponents.get_modify_legend_bar(bar_obj = SA.Group[1].Group[0].Group[0],
                                               text_leg_group = SA.Group[1].Group[0].Group[1],
                                               title = title1,
                                               values = sun_analysis_results,
                                               position = SA.leg_position,
                                               seg_height = seg_height,
                                               seg_width = SA.leg_width,
                                               seg_count = SA.color_count,
                                               color_leg_set = int(SA.color_set[0:2])
                                               )
    f_colors_total = LBComponents.get_face_colors(sun_analysis_results,
                                                domain,
                                                bar_leg[1]
                                                )
    LBComponents.apply_color_faces(obj = SA.study_compound,
                                   face_colors = f_colors_total)
    total_compass = SA.Group[1].Group[1].Group[1].Group[0]
    color = bar_leg[-1][-1]
    color_rgb = (color[0], color[1], color[2])
    total_compass.ViewObject.ShapeAppearance = FreeCAD.Material(
                                    DiffuseColor = color_rgb)
    if SA.results[0:2] == "01" or SA.results[0:2] == "02":
        try:
            study_direct_group = doc.getObject(SA.Group[2].Name)
            study_diffuse_group = doc.getObject(SA.Group[3].Name)
            study_direct_clone = doc.getObject(SA.Group[2].Group[0].Name)
            study_diffuse_clone = doc.getObject(SA.Group[3].Group[0].Name)
            f_colors_direct = LBComponents.get_face_colors(sun_analysis_results = SA.direct_values,
                                                           domain = SA.total_values,
                                                           leg_colors = bar_leg[1]
                                                           )
            f_colors_diffuse = LBComponents.get_face_colors(sun_analysis_results = SA.diffuse_values,
                                                           domain = SA.total_values,
                                                           leg_colors = bar_leg[1]
                                                           )
            LBComponents.apply_color_faces(obj = study_direct_clone,
                                           face_colors = f_colors_direct)
            LBComponents.apply_color_faces(obj = study_diffuse_clone,
                                           face_colors = f_colors_diffuse)
            doc.getObject(study_direct_group.Name).Visibility = SA.direct_diffuse_values
            doc.getObject(study_diffuse_group.Name).Visibility = SA.direct_diffuse_values
            direct_compass = SA.Group[2].Group[1].Group[1].Group[0]
            diffuse_compass = SA.Group[3].Group[1].Group[1].Group[0]
            direct_compass.ViewObject.ShapeAppearance = FreeCAD.Material(
                                            DiffuseColor = color_rgb)
            diffuse_compass.ViewObject.ShapeAppearance = FreeCAD.Material(
                                            DiffuseColor = color_rgb)
        except Exception:
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText(translate("SunAnalysis",
            "There is no direct or diffuse analysis group!"
            ))
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setStandardButtons(
                QtWidgets.QMessageBox.Ok) #| QtWidgets.QMessageBox.Cancel)
            msg.exec_()

def delete_sun_analysis(SA = None):

    """Delete a complete Sun Analysis objects"""

    def show_warning_dialog():
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("Delete Warning")
        msg.setText(translate("SunAnalysis",
            "This will delete all objects from \n"
            "the selected Sun Analysis, \n"
            "and you won't be able to undo it. \n"
            "\n"
            "Are you sure you want to delete these Sun Analysis?"
        ))
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setStandardButtons(
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        result = msg.exec_()
        return result
    result = show_warning_dialog()
    if result == QtWidgets.QMessageBox.Ok:
        doc = FreeCAD.ActiveDocument
        compass_links = SA.Group[1].Group[1].Group[1].Group[0].Links
        compound_links = SA.Group[0].Links
        links1 = len(compass_links)
        links2 = len(compound_links)
        for i in range(links1):
            doc.removeObject(SA.Group[1].Group[1].Group[1].Group[0].Links[0].Name) #compass link
        for i in range(links2):
            doc.removeObject(SA.Group[0].Links[0].Name) #compound link
        doc.removeObject(SA.Group[1].Group[0].Group[0].Base.Name) #rectangle
        doc.getObject(SA.Name).removeObjectsFromDocument() #SA content
        doc.removeObject(SA.Name) #SA
        doc.recompute()

#=================================================
# D. Commands
#=================================================

if FreeCAD.GuiUp:
    FreeCAD.Gui.addCommand('CreateSunAnalysis', CreateSunAnalysis())
    FreeCAD.Gui.addCommand('ModifySunAnalysis', ModifySunAnalysis())
    FreeCAD.Gui.addCommand('DeleteSunAnalysis', DeleteSunAnalysis())

