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