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

"""This module implements the sun properties."""

import os, sys
import shutil
import FreeCAD
import FreeCADGui as Gui
from PySide.QtCore import QT_TRANSLATE_NOOP
from PySide.QtGui import QFileDialog
from ladybug.location import Location
from ladybug.sunpath import Sunpath
import freecad.Solar.SunPathAnimation as SunPathAnimation
import freecad.Solar.SunShadowBW as SunShadow

_dir = os.path.dirname(__file__)
IconPath = os.path.join(_dir, 'icons')
LanguagePath = os.path.join(_dir, 'translations')
Gui.addLanguagePath(LanguagePath)

SUNLIGHT = None
RAY = None
OUTPUT_FILE = None
SD = None

class SunProperties:

    """Property container for the Sun dialog properties"""

    def __init__(self,obj):
        obj.Proxy = self
        self.setProperties(obj)

    def setProperties(self,obj):

        """Assigns properties to the solar
        position object."""

        pl = obj.PropertiesList
        # 01 epw file
        if not "epw_path" in pl:
            obj.addProperty(
            "App::PropertyFile",
            "epw_path", "01_epw_path",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Path to epw file"
                )
            ).epw_path = ""
        # 02 Location
        if not "City" in pl:
            obj.addProperty(
            "App::PropertyString",
            "City", "02_Location",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "City of the location"
                )
            ).City = "Sao Paulo"
        if not "Country" in pl:
            obj.addProperty(
            "App::PropertyString",
            "Country", "02_Location",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Country of the location"
                )
            ). Country = "BR"
        if not "Elevation" in pl:
            obj.addProperty(
            "App::PropertyFloat",
            "Elevation", "02_Location",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Elevation of the location"
                )
            ).Elevation = 720.00
        if not "Latitude" in pl:
            obj.addProperty(
            "App::PropertyFloat",
            "Latitude", "02_Location",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Latitude of the location"
                )
            ).Latitude = -23.550
        if not "Longitude" in pl:
            obj.addProperty(
            "App::PropertyFloat",
            "Longitude", "02_Location",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Longitude of the location"
                )
            ).Longitude = -46.633
        if not "TimeZone" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "TimeZone", "02_Location",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "UTC location"
                )
            ).TimeZone = -3
        # 03 North
        if not "North" in pl:
            obj.addProperty(
            "App::PropertyAngle",
            "North", "03_North_angle",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "North angle (clockwise)"
                )
            ).North = 0
        # 04 Date and time
        if not "Day" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Day", "04_Date_and_time",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The day of the sun's position"
                )
            ).Day = 1
        if not "DaylightSaving" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "DaylightSaving", "04_Date_and_time",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "True, for daylight saving time to be applied."
                )
            ).DaylightSaving = False
        if not "Hour" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Hour", "04_Date_and_time",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The hour of the sun's position"
                )
            ).Hour = 9
        if not "Min" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Min", "04_Date_and_time",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The minutes of the sun's position"
                )
            ).Min = 30
        if not "Month" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Month", "04_Date_and_time",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The month of the sun's position"
                )
            ).Month = 1
        if not "Year" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Year", "04_Date_and_time",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The year of the sun's position"
                )
            ).Year = 2025
        # 05 Results
        if not "Altitude" in pl:
            obj.addProperty(
            "App::PropertyFloat",
            "Altitude", "05_Results",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Sun altitude - it is indicative only"
                )
            )
        if not "Azimuth" in pl:
            obj.addProperty(
            "App::PropertyFloat",
            "Azimuth", "05_Results",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Sun azimuth - it is indicative only"
                )
            )
        if not "DaylightHours" in pl:
            obj.addProperty(
            "App::PropertyString",
            "DaylightHours", "05_Results",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Daylight hours - it is indicative only"
                )
            )
        if not "Noon" in pl:
            obj.addProperty(
            "App::PropertyString",
            "Noon", "05_Results",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Noon - it is indicative only"
                )
            )
        if not "Sunrise" in pl:
            obj.addProperty(
            "App::PropertyString",
            "Sunrise", "05_Results",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Sunrise - it is indicative only"
                )
            )
        if not "Sunset" in pl:
            obj.addProperty(
            "App::PropertyString",
            "Sunset", "05_Results",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Sunset - it is indicative only"
                )
            )
        # 06 Sun light and diagram configurations
        if not "SunLightDiagramConfig" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "SunLightDiagramConfig", "06_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "True, for configuring "
                "the sun light and/or diagram"
                )
            ).SunLightDiagramConfig = False
        if not "Distance" in pl:
            obj.addProperty(
            "App::PropertyLength",
            "Distance", "06_Sun_light_diagram_confign",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Light representation distance"
                 )
            ).Distance = 30000
        if not "Radius" in pl:
            obj.addProperty(
            "App::PropertyLength",
            "Radius", "06_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Light representation radius"
                )
            ).Radius = 700
        if not "SunLightPosition" in pl:
            obj.addProperty(
            "App::PropertyVector",
            "SunLightPosition", "06_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Position of the sun light (x, y, z)"
                )
            ).SunLightPosition = (1.0, 1.0, 1.0)
        if not "DiagPosition" in pl:
            obj.addProperty(
            "App::PropertyVector",
            "DiagPosition", "06_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The center position of the sun path diagram (x, y, z)"
                )
            ).DiagPosition = (0.0, 0.0, 0.0)
        if not "SunLightRepresentation" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "SunLightRepresentation", "06_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "True, for sun light representation to be visibled"
                )
            ).SunLightRepresentation = False
        if not "RayRepresentation" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "RayRepresentation", "06_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "True, for light ray representation to be visible"
                )
            ).RayRepresentation = False
        if not "SunLightColor" in pl:
            obj.addProperty(
            "App::PropertyColor",
            "SunLightColor", "06_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Color of the sun light"
                )
             ).SunLightColor = (255, 255, 0)
        if not "SunPathDiagram" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "SunPathDiagram", "06_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "True, for sun path diagram to be visible"
                )
            ).SunPathDiagram = False
        if not "DiagColor" in pl:
            obj.addProperty(
            "App::PropertyColor",
            "DiagColor", "06_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Color of sun path diagram"
                )
             ).DiagColor = (255, 255, 0)
        # 07 Show and/or save image:
        if not "Image_from" in pl:
            obj.addProperty(
            "App::PropertyEnumeration",
            "Image_from", "07_Show_save_image",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The image type to save"
                )
            ).Image_from = ("None/Reset",
                            "BW 3D view",
                            "Color 3D view",
                            "Render 3D view")
        if not "Height" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Height", "07_Show_save_image",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The image height to be saved in pixels"
                )
            ).Height = 1080
        if not "Width" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Width", "07_Show_save_image",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The image width to be saved in pixels"
                )
            ).Width = 1920
        if not "Save_to" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "Save_to", "07_Show_save_image",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "True, for saving image"
                )
            ).Save_to = False
        # 08. Sun path animation
        if not "SunPathAnimation" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "SunPathAnimation", "08_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "True, for sun path animation"
                )
            ).SunPathAnimation = False
        if not "start_hour" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "start_hour", "08_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The initial hour of the analysis period \n"
                "or sun path animation"
                )
            ).start_hour = 6
        if not "end_hour" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "end_hour", "08_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The final hour of the analysis period \n"
                "or sun path animation"
                )
            ).end_hour = 18
        if not "start_min" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "start_min", "08_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The initial minute of the analysis period \n"
                "or sun path animation"
                )
            ).start_min = 0
        if not "end_min" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "end_min", "08_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The final minute of the analysis period \n"
                "or sun path animation"
                )
            ).end_min = 0
        if not "sunrise_sunset" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "sunrise_sunset", "08_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "True, for getting sunrise and sunset data"
                )
            ).sunrise_sunset = False
        if not "inter_hour" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "inter_hour", "08_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The interval (in hours) of the analysis period \n"
                "or sun path animation"
                )
            ).inter_hour = 0
        if not "inter_min" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "inter_min", "08_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The interval (in minutes) of the analysis period \n"
                "or sun path animation"
                )
            ).inter_min = 10
        if not "Recompute" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "Recompute", "08_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "True, when necessary to recompute between frames"
                )
            ).Recompute = False
        if not "Fps" in pl:
            obj.addProperty(
            "App::PropertyFloat",
            "Fps", "08_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "The frames per second of the sun path animation"
                )
            ).Fps = 24.0
        if not "Frames" in pl:
            obj.addProperty(
            "App::PropertyInteger",
             "Frames", "08_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                 "Total resulting frames from the sun path animation"
                 )
            )

class SunPropertiesViewProvider:

    """A View Provider for the SunProperties object"""

    def __init__(self, obj):
        obj.Proxy = self

    def getIcon(self):
        __dir__ = os.path.dirname(__file__)
        return __dir__ + '/icons/SunPropertiesIcon.svg'

    def updateData(self,obj,prop):

        """Method called when the object has a property changed.
        If Image from has changed, set the to clean view state,
        enable bw white, color or render shadows.
        If the epw path has changed, set the autofill location data."""

        if prop in ["Image_from"]:
            if obj.Image_from == "None/Reset":
                SunShadow.clean_view_state()
            if obj.Image_from == "BW 3D view":
                SunShadow.create_shadows_black_white()
            if obj.Image_from == "Color 3D view":
                try:
                    site_obj = Gui.ActiveDocument.Site
                    if site_obj.SolarDiagram is True:
                        site_obj.SolarDiagram = False # Avoid sun path diagram
                except:
                    pass
                try:
                    Gui.runCommand('Std_DrawStyleShadow',0)
                    Gui.ActiveDocument.ActiveView.Shadow_ShowGround = False
                except Exception:
                    FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP(
                                "SunProperties",
                                "So far, the shadows with colored images"
                                "only work in the FreeCAD-Link version 20241006.\n"))
        if prop in ["epw_path"]:
            if obj.epw_path is not None:
                autofill_from_epw2()
                get_sun_position()

def activated_sun_properties():

    """Checks the existence of the 'SunProperties' and creates it if not"""

    try:
        folder = FreeCAD.ActiveDocument.SunProperties

    except Exception:
        folder = FreeCAD.ActiveDocument.addObject('App::DocumentObjectGroupPython',
                                                  'SunProperties')
        folder.Label = QT_TRANSLATE_NOOP('SunProperties', 'SunProperties')
        SunProperties(folder)
        SunPropertiesViewProvider(folder.ViewObject)
        create_sun_representation()
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP('SunProperties',
                                    'A sun position was created! '
                                    'To configure it, '
                                    'make the adjustments in its properties window.') + '\n')

def autofill_from_epw2(obj = None):

    """Get the EPW file path from the properties window"""

    from ladybug.epw import EPW
    obj = FreeCAD.ActiveDocument.SunProperties
    epw_path = obj.epw_path
    if not epw_path or not os.path.isfile(epw_path):
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("SunProperties",
            "If you want use EPW, please provide a valid file path.") + '\n')
        return
    try:
        epw = EPW(epw_path)
        # From epw file to properties
        obj.City = epw.location.city
        obj.Country = epw.location.country
        obj.Latitude = epw.location.latitude
        obj.Longitude = epw.location.longitude
        obj.Elevation = epw.location.elevation
        obj.TimeZone = int(epw.location.time_zone)
        try:
            site_obj = FreeCAD.ActiveDocument.Site
            # From epw file to Arch Site
            site_obj.EPWFile = epw_path
            site_obj.City = epw.location.city
            site_obj.Country = epw.location.country
            site_obj.Latitude = epw.location.latitude
            site_obj.Longitude = epw.location.longitude
            site_obj.Elevation = epw.location.elevation
            site_obj.TimeZone = int(epw.location.time_zone)
        except:
            pass
    except Exception as e:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP(
                                     "SunProperties",
                                     "File Error"),
                                     QT_TRANSLATE_NOOP(
                                     "SunProperties",
                                     f"Could not read EPW file:\n{e}" + '\n'))
        return

def get_sun_position(obj = None):

    """Compute the sun's position (its altitude, azimuth, and coordinates)
    for a given location and time using ladybug-core to orient the shadows'
    direction of the objects.
    Returns:
        Solar coordinates (x, y, and z);
        Solar altitude and azimuth;
        Sunrise, noon, and sunset;
        Daylight hours."""

    obj = FreeCAD.ActiveDocument.SunProperties
    if obj.Min >= 0 and obj.Min < 60:
        if obj.Hour >= 0 and obj.Hour <= 23:
            if obj.Day >= 1 and obj.Day <= 31:
                if obj.Month >= 1 and obj.Month <= 12:
                    if obj.DaylightSaving is True:
                        tz = obj.TimeZone + 1
                    else:
                        tz = obj.TimeZone
                    tim = float(obj.Hour) + float(obj.Min/60)
                    # Sun light coordinates:
                    location_data = Location(
                        city = obj.City,
                        country = obj.Country,
                        latitude = obj.Latitude,
                        longitude = obj.Longitude,
                        time_zone = tz,
                        elevation = obj.Elevation
                    )
                    sp = Sunpath.from_location(location_data)
                    # The north angle is only used to adjust the sun_vector
                    # and does not affect the sun altitude or azimuth.
                    sp.north_angle = -obj.North
                    sun = sp.calculate_sun(month = obj.Month,
                                           day = obj.Day,
                                           hour = tim
                                           ) # Obs.: hours in decimal values
                    sun_coordinates = sun.position_3d(radius = float(obj.Distance))
                    obj.SunLightPosition = (sun_coordinates[0],
                                            sun_coordinates[1],
                                            sun_coordinates[2]
                                            )
                    # Update Sun representation
                    update_sun_representation()
                    # Update BW shadows
                    if obj.Image_from == "BW 3D view":
                        SunShadow.update_shadow_direction()
                        if obj.Save_to is True and obj.SunPathAnimation is False:
                            save_image()
                    # Update Color shadows - until now, only for FreeCAD-Link
                    if obj.Image_from == "Color 3D view":
                        if obj.SunPathDiagram is True:
                            obj.SunPathDiagram = False # Avoid sun path diagram
                        try:
                            Gui.ActiveDocument.ActiveView.Shadow_LightDirection = (
                                               -sun_coordinates[0],
                                               -sun_coordinates[1],
                                               -sun_coordinates[2]
                                               )
                            if obj.Save_to is True and obj.SunPathAnimation is False:
                                save_image()
                        except:
                            pass
                    # Update render shadows - only with Render WB installed
                    if obj.Image_from == "Render 3D view":
                        from .SunPathAnimation import ANIMATION
                        try: # Render image
                            obj_render_sun = FreeCAD.ActiveDocument.SunskyLight
                            obj_render_sun.SunDirection = obj.SunLightPosition
                            project = FreeCAD.ActiveDocument.Project
                            project.RenderHeight = obj.Height
                            project.RenderWidth = obj.Width
                            if obj.SunPathAnimation is False and ANIMATION is False:
                                print("SunProperties: Render image")
                                project.OpenAfterRender = True
                                output_file = project.Proxy.render(
                                              skip_meshing=False,
                                              wait_for_completion=True)
                                if obj.Save_to is True:
                                    global OUTPUT_FILE
                                    OUTPUT_FILE = output_file
                                    save_image()
                            # Render animation
                            if obj.SunPathAnimation is True and ANIMATION is True:
                                project.OpenAfterRender = False
                                try:
                                    print("SunProperties: Render animation")
                                    Gui.ActiveDocument.Clapperboard
                                    Gui.ActiveDocument.MovieCamera
                                    import MovieClapperboard as cl
                                    cl.runRecordCamera(Back = False)
                                    Gui.runCommand('PostMovieAnimation',0)
                                except:
                                    print("SunProperties: No Render animation")
                        except Exception:
                            FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP(
                                "SunProperties",
                                "No render project found!") + '\n')

                    # Altitude and Azimute:
                    obj.Altitude = sun.altitude
                    obj.Azimuth = sun.azimuth
                    # Sunrise, noon and sunset
                    sunrise_sunset = sp.calculate_sunrise_sunset(
                                     month=obj.Month,
                                     day = obj.Day)
                    noon_str = str(sunrise_sunset ['noon'])
                    obj.Noon = noon_str[7:12]
                    sunrise_str = str(sunrise_sunset ['sunrise'])
                    obj.Sunrise = sunrise_str[7:12]
                    sunset_str = str(sunrise_sunset ['sunset'])
                    obj.Sunset = sunset_str[7:12]
                    # Daylight hours:
                    obj.DaylightHours = str((sunrise_sunset ['sunset']
                        - sunrise_sunset ['sunrise']))
                    # Calculate frames
                    SunPathAnimation.calculate_frames()
                    if obj.Recompute is True:
                        FreeCAD.ActiveDocument.recompute()
                else:
                    print("Invalid value for month")
            else:
                print("Invalid value for day")
        else:
            print("Invalid value for hours")
    else:
        print("Invalid value for minutes")

def create_sun_representation(obj = None):

    """
    Create sun and ray representation
    """

    obj = FreeCAD.ActiveDocument.SunProperties
    pt1_vector = obj.DiagPosition
    pt2_vector = obj.SunLightPosition + obj.DiagPosition
    try:
        FreeCAD.ActiveDocument.SunLight
    except Exception:
        # Sun representation
        sun_light_1 = FreeCAD.ActiveDocument.addObject("Part::Sphere","SunLight")
        sun_light_1.Label = QT_TRANSLATE_NOOP("SunProperties", "SunLight")
        sun_light_1.Placement.Base = pt2_vector
        sun_light_1.Radius = str(obj.Radius)
        try:
            Gui.ActiveDocument.SunLight.ShapeAppearance = (
                FreeCAD.Material(DiffuseColor = obj.SunLightColor)
            )
        except:
            pass
        try:
            Gui.ActiveDocument.SunLight.ShapeColor = obj.SunLightColor
        except:
            pass
        obj_sun = FreeCAD.ActiveDocument.SunLight
        obj.addObject(obj_sun)
        if obj.SunLightRepresentation is True:
            sun_light_1.Visibility = True
        else:
            sun_light_1.Visibility = False
        FreeCAD.ActiveDocument.recompute()
    # solar ray
    try:
        FreeCAD.ActiveDocument.RayLine
    except Exception:
        import Draft
        pl = FreeCAD.Placement()
        pl.Base = pt1_vector
        pt_final = FreeCAD.Vector(pt2_vector)
        points = [FreeCAD.Vector(pl.Base), FreeCAD.Vector(pt_final)]
        ray_1 = Draft.make_wire(points,
                                placement=pl,
                                closed=False,
                                face=True,
                                support=None)
        ray_1.Label = QT_TRANSLATE_NOOP("SunProperties", "Ray")
        obj.addObject(ray_1)
        if hasattr(RAY, "ViewObject"):
            ray_1.ViewObject.LineColor = obj.SunLightColor
            ray_1.ViewObject.PointColor = obj.SunLightColor
        if obj.SunLightRepresentation is True:
            if obj.RayRepresentation is True:
                ray_1.Visibility = True
            else:
                ray_1.Visibility = False
        else:
            ray_1.Visibility = False
        FreeCAD.ActiveDocument.recompute()

def update_sun_representation(obj = None):

    """
    Update sun and ray representations
    """

    obj = FreeCAD.ActiveDocument.SunProperties
    pt1_vector = obj.DiagPosition
    pt2_vector = obj.SunLightPosition + obj.DiagPosition
    # Sun representation
    try:
        sun_light_2 = obj.Group[0]
        if obj.SunLightRepresentation is True:
            sun_light_2.Visibility = True
            sun_light_2.Placement.Base = pt2_vector
            sun_light_2.Radius = obj.Radius
            try:
                Gui.ActiveDocument.SunLight.ShapeAppearance = (
                    FreeCAD.Material(DiffuseColor = obj.SunLightColor)
                )
            except:
                pass
            try:
                Gui.ActiveDocument.SunLight.ShapeColor = obj.SunLightColor
            except:
                pass
        else:
            sun_light_2.Visibility = False
    except Exception:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP(
            'SunProperties', 'There is no SunLight to update!') + '\n')
    # solar ray
    try:
        ray_2 = obj.Group[1]
        if obj.SunLightRepresentation is True:
            if obj.RayRepresentation is True:
                ray_2.Visibility = True
                ray_2.Start = pt1_vector
                ray_2.End = pt2_vector
                Gui.ActiveDocument.getObject(
                            ray_2.Name).LineColor = obj.SunLightColor
                Gui.ActiveDocument.getObject(
                            ray_2.Name).PointColor = obj.SunLightColor
                FreeCAD.ActiveDocument.getObject(
                            ray_2.Name).recompute()
            else:
                ray_2.Visibility = False
        else:
            ray_2.Visibility = False
    except Exception:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP(
            'SunProperties', 'There is no sun ray to update!') + '\n')

def get_diagram_from_site(obj = None):

    """Get solar diagram path from Arch Site object"""

    obj = FreeCAD.ActiveDocument.SunProperties
    try:
        site_obj = Gui.ActiveDocument.Site
        obj.SunPathDiagram = site_obj.SolarDiagram
        obj.DiagColor = site_obj.SolarDiagramColor
        obj.DiagPosition = site_obj.SolarDiagramPosition
        obj.Distance = site_obj.SolarDiagramScale
        FreeCAD.ActiveDocument.recompute()
    except:
        pass

def send_diagram_to_site(obj = None):

    """Send data to solar diagram path of Arch Site object"""

    obj = FreeCAD.ActiveDocument.SunProperties
    try:
        site_obj1 = Gui.ActiveDocument.Site
        site_obj1.SolarDiagram = obj.SunPathDiagram
        if obj.SunPathDiagram is True:
            site_obj1.SolarDiagramColor = obj.DiagColor
            site_obj1.SolarDiagramPosition = obj.DiagPosition
            site_obj1.SolarDiagramScale = float(obj.Distance)
            site_obj2 = FreeCAD.ActiveDocument.Site
            site_obj2.EPWFile = obj.epw_path
            site_obj2.City = obj.City
            site_obj2.Country = obj.Country
            site_obj2.Latitude = obj.Latitude
            site_obj2.Longitude = obj.Longitude
            site_obj2.Elevation = obj.Elevation
            site_obj2.TimeZone = obj.TimeZone
            site_obj2.Declination = - obj.North
    except:
        print("Site diagram was not updated")
        pass

def send_data_to_sky_domes(obj = None, SD = None):

    """Send data to sky domes"""

    obj = FreeCAD.ActiveDocument.SunProperties
    if SD is not None and obj.sky_domes is True:
        obj1 = SD
        print (f"send data to sky domes: SD = {SD.Name}")
    else:
        print (f"send data to sky domes: SD = {SD}")
        return
    try:
        obj1.epw_path = obj.epw_path
        obj1.position = obj.DiagPosition
        obj1.radius = float(obj.Distance)
        obj1.north = obj.North
        obj1.start_year = obj.start_year
        obj1.end_year = obj.end_year
        obj1.start_month = obj.start_month
        obj1.end_month = obj.end_month
        obj1.start_day = obj.start_day
        obj1.end_day = obj.end_day
        obj1.start_hour = obj.start_hour
        obj1.end_hour =  obj.end_hour
        obj1.start_min = obj.start_min
        obj1.end_min = obj.end_min
        obj1.timestep = obj.timestep
        obj1.leap_year = obj.leap_year
        obj1.model = obj.model
        obj1.units = obj.units
        obj1.sky_domes = obj.sky_domes
        obj1.Group[0].Visibility = obj.sky_domes
        obj1.direct_diffuse_domes = obj.direct_diffuse
        obj1.Group[1].Visibility = obj.sky_domes and obj1.direct_diffuse_domes
        obj1.Group[2].Visibility = obj.sky_domes and obj1.direct_diffuse_domes
        obj1.Group[3].Visibility = obj.sky_domes
    except Exception:
        print("Send data: sky domes was not updated")

def save_image(obj = None):

    """Save image"""

    print("save image was call")
    try:
        obj = FreeCAD.ActiveDocument.SunProperties
        if obj.Save_to is True:
            if obj.Image_from == "BW 3D view":
                from .SunShadowBW import VIEW
                if VIEW is not None:
                    # outputfile = "/tmp/freecad_shadow.png"
                    # width = 1920
                    # height = 1080
                    # Save the image using saveImage() # Not working
                    # view.saveImage(outputfile, width , height, 'Current')
                    # Or
                    # Save the image using OfflineRenderingUtils.render
                    # (not working)
                    # camera_node = Gui.ActiveDocument.ActiveView.getCameraNode()
                    # zoom = False
                    # background = (1.0,1.0,1.0)
                    # data =
                    # (outputfile, scene, camera_node,
                    # zoom, width, height, background, lightdir)
                    # OfflineRenderingUtils.render(data)
                    # print(f"Saved 3D view image to {output_path}")
                    VIEW.printPdf() # Save a pdf image
                    print("save BW image was call")
            if obj.Image_from == "Color 3D view":
                print("saveColorPdf")
                Gui.runCommand('Std_PrintPdf',0)
            if obj.Image_from == "Render 3D view":
                print("save render")
                output_file_name, _ = QFileDialog.getSaveFileName(
                    None, "Save render image", "", " image file (*png)"
                )
                shutil.move(OUTPUT_FILE, output_file_name)
    except:
        print("The save image option was enabled, but it didn't work.")
