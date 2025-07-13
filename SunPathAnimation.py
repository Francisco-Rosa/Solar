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
# ***************************************************************************

"""This module implements the sun path animation configuration"""


import os
import time
import FreeCAD
import FreeCADGui as Gui
from PySide.QtCore import QT_TRANSLATE_NOOP
import SunProperties as sp

Gui.addLanguagePath(sp.LanguagePath)
# Gui.updateLocale()


class StartSunPathAnimation:
    """Class to start a sun path animation"""

    def QT_TRANSLATE_NOOP(self, text):
        return text

    def GetResources(self):
        __dir__ = os.path.dirname(__file__)
        return {'Pixmap': __dir__ + '/icons/StartSunPathAnimationIcon.svg',
                'MenuText': QT_TRANSLATE_NOOP(
                'StartSunPathAnimation', 'StartSunPathAnimation'),
                'ToolTip': QT_TRANSLATE_NOOP(
                'StartSunPathAnimation', 'Start a sun path animation. \n'
                'To enable it, choose an image type in “Image from”\n'
                'other than None/Reset and configure its properties. \n'
                'Click this button to get started its animation')}

    def IsActive(self):
        if Gui.ActiveDocument:
            try:
                obj = FreeCAD.ActiveDocument.SunProperties
                if obj.Image_from != "None/Reset" and obj.SunPathAnimation is True:
                    return True
            except:
                pass
        else:
            return False

    def Activated(self):
        modify_anim_indicator(animation = True)
        sun_path_animation()
        modify_anim_indicator(animation = False)

class StopSunPathAnimation:
    """Class to stop a sun path animation"""

    def QT_TRANSLATE_NOOP(self, text):
        return text

    def GetResources(self):
        __dir__ = os.path.dirname(__file__)
        return {'Pixmap': __dir__ + '/icons/StopSunPathAnimationIcon.svg',
                'MenuText': QT_TRANSLATE_NOOP(
                'StopSunPathAnimation', 'StopSunPathAnimation'),
                'ToolTip': QT_TRANSLATE_NOOP(
                'StopSunPathAnimation', 'Stop a sun path animation. '
                'After the sun path animation started, '
                'click this button to stop it.')}

    def IsActive(self):
        if Gui.ActiveDocument:
            try:
                obj = FreeCAD.ActiveDocument.SunProperties
                if obj.Image_from != "None/Reset" and obj.SunPathAnimation is True:
                    return True
            except:
                pass
        else:
            return False

    def Activated(self):
        modify_anim_indicator(animation = False)
        try:
            #FreeCAD.ActiveDocument.Clapperboard
            Gui.runCommand('StopRecordCamera',0)
        except:
            pass

#-----------------
## Sun path animation
ANIMATION = False
def modify_anim_indicator(animation = False):
    """Function to modify the indicator a sun path animation"""

    global ANIMATION
    if animation is False:
        ANIMATION = False
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP(
            'Solar', 'SunPathAnimation, Animation off.') + '\n')
    if animation is True:
        ANIMATION = True
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP(
            'Solar', 'SunPathAnimation, Animation on.') + '\n')
    FreeCAD.ActiveDocument.recompute()

def calculate_frames():
    obj = FreeCAD.ActiveDocument.SunProperties
    # Data_interval
    hi = float(obj.InitialHour) + float(obj.InitialMin/60)
    hf = float(obj.FinalHour) + float(obj.FinalMin/60)
    time_range = hf - hi
    interv = float(obj.Inter_hour) + float(obj.Inter_min/60)
    obj.Frames = int(time_range / interv)

def sun_path_animation():
    """Send data to sun's position for a given date,
    time, interval and fps.
    Returns: City, Date and Time"""

    obj = FreeCAD.ActiveDocument.SunProperties
    if obj.Image_from == "Render 3D view" and obj.SunPathAnimation is True:
        if obj.Save_path == "":
            FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("Solar",
                "Please, provide a file path to save the render images!") + "\n")
            Gui.runCommand('SunConfigurationDialog',0)
            return
    # Data_interval
    calculate_frames()
    fps = obj.Fps
    pause = 1/fps
    obj.Hour = obj.InitialHour
    obj.Min = obj.InitialMin
    sp.get_sun_position() # First step
    Gui.updateGui()
    print(f'{obj.City}, {obj.Day:0>2}/{obj.Month:0>2}/{obj.Year}, {obj.Hour:0>2}:{obj.Min:0>2}')
    time.sleep(pause)
    for t in range(obj.Frames):
        minutes = obj.Min + obj.Inter_min
        if minutes < 60:
            obj.Min = minutes
        else:
            obj.Min = minutes - 60
            hour = obj.Hour + 1
            if hour < 24:
                obj.Hour = hour
            else:
                print("Hour is higher then 24")
                pass
        hour = obj.Hour + obj.Inter_hour
        if hour < 24:
            obj.Hour = hour
        else:
            print("Hour is higher then 24")
            pass
        sp.get_sun_position()
        Gui.updateGui()
        print(f'{obj.City}, {obj.Day:0>2}/{obj.Month:0>2}/{obj.Year}, {obj.Hour:0>2}:{obj.Min:0>2}')
        time.sleep(pause)
        if ANIMATION is False:
            break

def set_render_animation():
    """Make the adjustments for a render animation"""
    obj = FreeCAD.ActiveDocument.SunProperties
    # MovieCamera
    try:
        MC = FreeCAD.ActiveDocument.MovieCamera
        MC.Cam_03AnimEndStep = obj.Frames
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(MC)
        Gui.runCommand('EnableMovieCamera',0)
        Gui.Selection.clearSelection()
    except Exception:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("Solar",
            "No MovieCamera found!") + '\n')
    # Clapperboard
    try:
        CL = FreeCAD.ActiveDocument.Clapperboard
        CL.Frame_04OutputPath = obj.Save_path
        CL.Clap_05AnimFps = int(obj.Fps)
        CL.Frame_07R2OnRec = True
        Gui.Selection.addSelection(CL)
        Gui.runCommand('EnableMovieClapperboard',0)
        FreeCAD.ActiveDocument.recompute()
        print("set render animation")
    except:
        FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP("Solar",
            "No Clapperboard found!") + '\n')

#---------------------------------------------------

if FreeCAD.GuiUp:
    FreeCAD.Gui.addCommand('StartSunPathAnimation', StartSunPathAnimation())
    FreeCAD.Gui.addCommand('StopSunPathAnimation', StopSunPathAnimation())
