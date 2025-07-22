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

"""This module implements the sun properties."""

import os, sys
import shutil
import FreeCAD
import FreeCADGui as Gui
from PySide.QtCore import QT_TRANSLATE_NOOP
from PySide.QtGui import QFileDialog

_dir = os.path.dirname(__file__)
IconPath = os.path.join(_dir, 'icons')
LanguagePath = os.path.join(_dir, 'translations')
Gui.addLanguagePath(LanguagePath)

try:
    for root, dirs, files in os.walk(os.path.join(_dir, "AdditionalPythonPackages")):
        if os.path.basename(root) == "site-packages":
            sys.path.append(root)
except:
    pass
from ladybug.location import Location
from ladybug.sunpath import Sunpath
import SunShadowBW as sh
import SunPathAnimation as spa

SUNLIGHT = None
RAY = None
OUTPUT_FILE = None

class SunProperties:
    """Property container for the Sun dialog properties"""

    def __init__(self,obj):
        obj.Proxy = self
        self.setProperties(obj)

    def setProperties(self,obj):
        """Gives the object properties unique to sun position object."""

        pl = obj.PropertiesList
        # 1 epw file
        if not "epw_path" in pl:
            obj.addProperty(
            "App::PropertyFile",
            "epw_path", "1_epw_path",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Path to epw file"
                )
            ).epw_path = ""
        # 2 Location
        if not "City" in pl:
            obj.addProperty(
            "App::PropertyString",
            "City", "2_Location",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "City of the location"
                )
            ).City = "Sao Paulo"
        if not "Country" in pl:
            obj.addProperty(
            "App::PropertyString",
            "Country", "2_Location",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Country of the location"
                )
            ). Country = "BR"
        if not "Elevation" in pl:
            obj.addProperty(
            "App::PropertyFloat",
            "Elevation", "2_Location",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Elevation of the location"
                )
            ).Elevation = 720.00
        if not "Latitude" in pl:
            obj.addProperty(
            "App::PropertyFloat",
            "Latitude", "2_Location",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Latitude of the location"
                )
            ).Latitude = -23.550
        if not "Longitude" in pl:
            obj.addProperty(
            "App::PropertyFloat",
            "Longitude", "2_Location",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Longitude of the location"
                )
            ).Longitude = -46.633
        if not "TimeZone" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "TimeZone", "2_Location",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "UTC location"
                )
            ).TimeZone = -3
        # 3 North
        if not "North" in pl:
            obj.addProperty(
            "App::PropertyAngle",
            "North", "3_North_angle",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Delta angle (counterclockwise) "
                "between the true north and Y axis direction"
                )
            ).North = 0
        # 4 Date and time
        if not "Day" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Day", "4_Date_and_time",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Set the day of the solar position"
                )
            ).Day = 1
        if not "DaylightSaving" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "DaylightSaving", "4_Date_and_time",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Choose true if daylight saving must be applied"
                )
            ).DaylightSaving = False
        if not "Hour" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Hour", "4_Date_and_time",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Set the hour of the solar position"
                )
            ).Hour = 9
        if not "Min" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Min", "4_Date_and_time",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Set the minutes of the solar position"
                )
            ).Min = 30
        if not "Month" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Month", "4_Date_and_time",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Set the month of the solar position"
                )
            ).Month = 1
        if not "Year" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Year", "4_Date_and_time",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Set the year of the solar position"
                )
            ).Year = 2025
        # 5 Results
        if not "Altitude" in pl:
            obj.addProperty(
            "App::PropertyFloat",
            "Altitude", "5_Results",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Sun altitude - it is indicative only"
                )
            )
        if not "Azimuth" in pl:
            obj.addProperty(
            "App::PropertyFloat",
            "Azimuth", "5_Results",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Sun azimuth - it is indicative only"
                )
            )
        if not "DaylightHours" in pl:
            obj.addProperty(
            "App::PropertyString",
            "DaylightHours", "5_Results",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Daylight hours - it is indicative only"
                )
            )
        if not "Noon" in pl:
            obj.addProperty(
            "App::PropertyString",
            "Noon", "5_Results",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Noon - it is indicative only"
                )
            )
        if not "Sunrise" in pl:
            obj.addProperty(
            "App::PropertyString",
            "Sunrise", "5_Results",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Sunrise - it is indicative only"
                )
            )
        if not "Sunset" in pl:
            obj.addProperty(
            "App::PropertyString",
            "Sunset", "5_Results",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Sunset - it is indicative only"
                )
            )
        # 6 Sun light and diagram configurations
        if not "SunLightDiagramConfig" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "SunLightDiagramConfig", "6_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Choose true if you want to configurate "
                "the sun light and/or diagram"
                )
            ).SunLightDiagramConfig = False
        if not "Distance" in pl:
            obj.addProperty(
            "App::PropertyLength",
            "Distance", "6_Sun_light_diagram_confign",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Light representation distance"
                 )
            ).Distance = 30000
        if not "Radius" in pl:
            obj.addProperty(
            "App::PropertyLength",
            "Radius", "6_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Light representation radius"
                )
            ).Radius = 700
        if not "SunLightPosition" in pl:
            obj.addProperty(
            "App::PropertyVector",
            "SunLightPosition", "6_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Position of the sun light (x, y, z)"
                )
            ).SunLightPosition = (1.0, 1.0, 1.0)
        if not "DiagPosition" in pl:
            obj.addProperty(
            "App::PropertyVector",
            "DiagPosition", "6_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Center position of center of the sun path diagram (x, y, z)"
                )
            ).DiagPosition = (0.0, 0.0, 0.0)
        if not "SunLightRepresentation" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "SunLightRepresentation", "6_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Choose true if sun light representation must be visible"
                )
            ).SunLightRepresentation = False
        if not "RayRepresentation" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "RayRepresentation", "6_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Choose true if light ray representation must be visible"
                )
            ).RayRepresentation = False
        if not "SunLightColor" in pl:
            obj.addProperty(
            "App::PropertyColor",
            "SunLightColor", "6_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Color of the sun light"
                )
             ).SunLightColor = (255, 255, 0)
        if not "SunPathDiagram" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "SunPathDiagram", "6_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Choose true if sun path diagram must be visible"
                )
            ).SunPathDiagram = False
        if not "DiagColor" in pl:
            obj.addProperty(
            "App::PropertyColor",
            "DiagColor", "6_Sun_light_diagram_config",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Color of sun path diagram"
                )
             ).DiagColor = (255, 255, 0)
        # 7 Show and/or save image:
        if not "Image_from" in pl:
            obj.addProperty(
            "App::PropertyEnumeration",
            "Image_from", "7_Show_save_image",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Choose the type of image to save"
                )
            ).Image_from = ("None/Reset", "BW 3D view", "Color 3D view", "Render 3D view")
        if not "Height" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Height", "7_Show_save_image",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Set the height in pixels of the image to be saved"
                )
            ).Height = 1080
        if not "Width" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Width", "7_Show_save_image",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Set the width in pixels of the image to be saved"
                )
            ).Width = 1920
        if not "Save_to" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "Save_to", "7_Show_save_image",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Choose true to save image"
                )
            ).Save_to = False
        # 8 Sun path animation
        if not "SunPathAnimation" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "SunPathAnimation", "8_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Choose true if you want sun path animation"
                )
            ).SunPathAnimation = False
        if not "InitialHour" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "InitialHour", "8_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Set the initial hour of the sun path animation"
                )
            ).InitialHour = 6
        if not "InitialMin" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "InitialMin", "8_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Set the initial minute of the sun path animation"
                )
            ).InitialMin = 10
        if not "FinalHour" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "FinalHour", "8_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Set the final hour of the sun path animation"
                )
            ).FinalHour = 18
        if not "FinalMin" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "FinalMin", "8_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Set the final minute of the sun path animation"
                )
            ).FinalMin = 20
        if not "Inter_hour" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Inter_hour", "8_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Set the interval (in hours) of the sun path animation "
                )
            ).Inter_hour = 00
        if not "Inter_min" in pl:
            obj.addProperty(
            "App::PropertyInteger",
            "Inter_min", "8_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Set the interval (in minutes) of the sun path animation "
                )
            ).Inter_min = 10
        if not "Recompute" in pl:
            obj.addProperty(
            "App::PropertyBool",
            "Recompute", "8_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Choose true if is necessary to recompute between frames"
                )
            ).Recompute = False
        if not "Fps" in pl:
            obj.addProperty(
            "App::PropertyFloat",
            "Fps", "8_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                "Set the frames per second of the sun path animation"
                )
            ).Fps = 24.0
        if not "Frames" in pl:
            obj.addProperty(
            "App::PropertyInteger",
             "Frames", "8_Sun_path_animation",
            QT_TRANSLATE_NOOP(
                "App::Property",
                 "Show total resulting frames from the sun path animation"
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
        If the epw path has changed, set the autofill localtion data."""

        if prop in ["Image_from"]:
            if obj.Image_from == "None/Reset":
                sh.clean_view_state()
            if obj.Image_from == "BW 3D view":
                sh.create_shadows_black_white()
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
                    FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("solar",
                                   "So far, the shadows with colored "
                                   "images only work in the FreeCAD-Link version 20241006.\n"))
        if prop in ["epw_path"]:
            if obj.epw_path is not None:
                autofill_from_epw2()
                get_sun_position()

def activated_sun_properties():
    """Checks the existence of the 'SunProperties' and creates it if not"""
    try:
        folder = FreeCAD.ActiveDocument.SunProperties
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP('Solar',
            'It was planned to work with only one '
            'SunProperties per document, and one already exists!') + '\n')

    except Exception:
        folder = FreeCAD.ActiveDocument.addObject('App::DocumentObjectGroupPython', 'SunProperties')
        SunProperties(folder)
        SunPropertiesViewProvider(folder.ViewObject)
        create_sun_representation()
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP('Solar', 'A sun position was created! '
                                    'To configure it, '
                                    'make the adjustments in its properties window.') + '\n')

def autofill_from_epw2():
    """Get the EPW file path from the properties window"""
    from ladybug.epw import EPW
    obj = FreeCAD.ActiveDocument.SunProperties
    epw_path = obj.epw_path
    if not epw_path or not os.path.isfile(epw_path):
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("Solar",
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
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("Solar",
            "File Error", f"Could not read EPW file:\n{e}") + '\n')
        return

def get_sun_position():
    """Compute the sun's position (its altitude, azimuth, and coordinates) for a given location
    and time using ladybug-core to orient the shadows' direction of the objects.
    Returns:
        Solar coordinates (x, y, and z);
        Solar altitude and azimuth;
        Sunrise, noon, and sunset;
        Daylight hours.
    """

    obj = FreeCAD.ActiveDocument.SunProperties
    if obj.Min >= 0 and obj.Min < 60:
        if obj.Hour >= 0 and obj.Hour <= 23:
            if obj.Day >= 1 and obj.Day <= 31:
                if obj.Month >= 1 and obj.Month <= 12:
                    if obj.DaylightSaving is True:  # dsl check
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
                    # North angle. This is only used to adjust the sun_vector
                    # and does not affect the sun altitude or azimuth.
                    sp.north_angle = obj.North
                    sun = sp.calculate_sun(month=obj.Month, day=obj.Day,
                        hour=tim) # Obs.: hours in decimal values
                    sun_coordinates = sun.position_3d(radius = float(obj.Distance))
                    obj.SunLightPosition = (sun_coordinates[0],
                        sun_coordinates[1], sun_coordinates[2]
                    )
                    # Update Sun representation
                    update_sun_representation()
                    # Update BW shadows
                    if obj.Image_from == "BW 3D view":
                        sh.update_shadow_direction()
                        if obj.Save_to is True and obj.SunPathAnimation is False:
                            save_image()
                    # Update Color shadows - until now, only for FreeCAD-Link
                    if obj.Image_from == "Color 3D view":
                        if obj.SunPathDiagram is True:
                            obj.SunPathDiagram = False # Avoid sun path diagram
                        try:
                            Gui.ActiveDocument.ActiveView.Shadow_LightDirection = (
                                 -sun_coordinates[0], -sun_coordinates[1], -sun_coordinates[2]
                            )

                            if obj.Save_to is True and obj.SunPathAnimation is False:
                                save_image()
                        except:
                            pass
                    # Update render shadows - only with Render WB installed
                    if obj.Image_from == "Render 3D view":
                        from SunPathAnimation import ANIMATION
                        try: # Render image
                            obj_render_sun = FreeCAD.ActiveDocument.SunskyLight
                            obj_render_sun.SunDirection = obj.SunLightPosition
                            project = FreeCAD.ActiveDocument.Project
                            project.RenderHeight = obj.Height
                            project.RenderWidth = obj.Width
                            if obj.SunPathAnimation is False and ANIMATION is False:
                                print("Solar: Render image")
                                project.OpenAfterRender = True
                                output_file = project.Proxy.render(skip_meshing=False,
                                    wait_for_completion=True)
                                if obj.Save_to is True:
                                    global OUTPUT_FILE
                                    OUTPUT_FILE = output_file
                                    save_image()
                            # Render animation
                            if obj.SunPathAnimation is True and ANIMATION is True:
                                project.OpenAfterRender = False
                                try:
                                    print("Solar: Render animation")
                                    Gui.ActiveDocument.Clapperboard
                                    Gui.ActiveDocument.MovieCamera
                                    import MovieClapperboard as cl
                                    cl.runRecordCamera(Back = False)
                                    Gui.runCommand('PostMovieAnimation',0)
                                except:
                                    print("Solar: No Render animation")
                        except Exception:
                            FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("Solar",
                                "No render project found!") + '\n')

                    # Altitude and Azimute:
                    obj.Altitude = sun.altitude
                    obj.Azimuth = sun.azimuth
                    ## Sunrise, noon and sunset:
                    sunrise_sunset = sp.calculate_sunrise_sunset(month=obj.Month, day = obj.Day)
                    Noon = str(sunrise_sunset ['noon'])
                    obj.Noon = Noon[7:12]
                    Sunrise = str(sunrise_sunset ['sunrise'])
                    obj.Sunrise = Sunrise[7:12]
                    Sunset = str(sunrise_sunset ['sunset'])
                    obj.Sunset = Sunset[7:12]
                    # Daylight hours:
                    obj.DaylightHours = str((sunrise_sunset ['sunset']
                        - sunrise_sunset ['sunrise']))
                    # Calculate frames
                    spa.calculate_frames()
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

def create_sun_representation():
    """
    Create sun and ray representation
    """

    obj = FreeCAD.ActiveDocument.SunProperties
    pt1_vector = obj.DiagPosition
    pt2_vector = obj.SunLightPosition + obj.DiagPosition
    # Sun representation
    try:
        FreeCAD.ActiveDocument.SunLight
    except Exception:
        # Sun representation
        SUNLIGHT = FreeCAD.ActiveDocument.addObject("Part::Sphere","SunLight")
        SUNLIGHT.Label = "SunLight"
        SUNLIGHT.Placement.Base = pt2_vector
        SUNLIGHT.Radius = str(obj.Radius)
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
            SUNLIGHT.Visibility = True
        else:
            SUNLIGHT.Visibility = False
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
        RAY = Draft.make_wire(points, placement=pl, closed=False, face=True, support=None)
        RAY.Label = "Ray"
        obj.addObject(RAY)

        if hasattr(RAY, "ViewObject"):
            RAY.ViewObject.LineColor = obj.SunLightColor
            RAY.ViewObject.PointColor = obj.SunLightColor
            
        if obj.SunLightRepresentation is True:
            if obj.RayRepresentation is True:
                RAY.Visibility = True
            else:
                RAY.Visibility = False
        else:
            RAY.Visibility = False
        FreeCAD.ActiveDocument.recompute()

def update_sun_representation():
    """
    Update sun and ray representations
    """

    obj = FreeCAD.ActiveDocument.SunProperties
    pt1_vector = obj.DiagPosition
    pt2_vector = obj.SunLightPosition + obj.DiagPosition

    # Sun representation
    try:
        sun_light = obj.Group[0]
        if obj.SunLightRepresentation is True:
            sun_light.Visibility = True
            sun_light.Placement.Base = pt2_vector
            sun_light.Radius = obj.Radius
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
            sun_light.Visibility = False
    except Exception:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP(
            'Solar', 'There is no SunLight to update!') + '\n')

    # solar ray
    try:
        ray = obj.Group[1]
        if obj.SunLightRepresentation is True:
            if obj.RayRepresentation is True:
                ray.Visibility = True
                ray.Start = pt1_vector
                ray.End = pt2_vector
                Gui.ActiveDocument.getObject(ray.Name).LineColor = obj.SunLightColor
                Gui.ActiveDocument.getObject(ray.Name).PointColor = obj.SunLightColor
                FreeCAD.ActiveDocument.getObject(ray.Name).recompute()
            else:
                ray.Visibility = False
        else:
            ray.Visibility = False
    except Exception:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP(
            'Solar', 'There is no sun ray to update!') + '\n')

def get_diagram_from_site():
    """
    Get solar diagram path from Arch Site object
    """
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

def send_diagram_to_site():
    """
    Send data to solar diagram path of Arch Site object
    """
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
            site_obj2.Declination = obj.North
            #FreeCAD.ActiveDocument.recompute()
    except:
        print("Site diagram was not updated")
        pass

def save_image():
    print("save image was call")
    try:
        obj = FreeCAD.ActiveDocument.SunProperties
        if obj.Save_to is True:
            if obj.Image_from == "BW 3D view":
                from SunShadowBW import VIEW
                if VIEW is not None:
                    # outputfile = "/tmp/freecad_shadow.png"
                    # width = 1920
                    # height = 1080
                    # Save the image using saveImage() # Not working
                    # view.saveImage(outputfile, width , height, 'Current')
                    # Or
                    # Save the image using OfflineRenderingUtils.render # Not working
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
        print("Save image was call but not work")
