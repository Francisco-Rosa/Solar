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

"""This module implements the sun path animation configuration"""

import os
import time
import FreeCAD
import FreeCADGui as Gui
from PySide.QtCore import QT_TRANSLATE_NOOP

translate = FreeCAD.Qt.translate

LanguagePath = os.path.dirname(__file__) + '/translations'
Gui.addLanguagePath(LanguagePath)

import freecad.Solar.SunProperties as Properties

Gui.addLanguagePath(Properties.LanguagePath)

class StartSunPathAnimation:

    """Class to start a sun path animation"""

    def QT_TRANSLATE_NOOP(self, text):
        return text

    def GetResources(self):
        __dir__ = os.path.dirname(__file__)
        return {'Pixmap': __dir__ + '/icons/StartSunPathAnimationIcon.svg',
                'MenuText': QT_TRANSLATE_NOOP('StartSunPathAnimation', 'Start Sun Path Animation'),
                'ToolTip': QT_TRANSLATE_NOOP('StartSunPathAnimation', 'Starts a sun path animation.\n'
                'To use it, open the dialog and enable Sun Path animation.\n'
                'To view shadow projection, choose the image other than None.\n'
                'Click this button to get started its animation')}

    def IsActive(self):
        if Gui.ActiveDocument:
            try:
                obj = FreeCAD.ActiveDocument.SunProperties
                if obj.SunPathAnimation is True:
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
                'MenuText': QT_TRANSLATE_NOOP('StopSunPathAnimation',
                                            'Stop SunPath Animation'),
                'ToolTip': QT_TRANSLATE_NOOP('StopSunPathAnimation',
                                        'Stops a sun path animation. '
                                        'After the sun path animation started, '
                                        'click this button to stop it.')}

    def IsActive(self):
        if Gui.ActiveDocument:
            try:
                obj = FreeCAD.ActiveDocument.SunProperties
                if obj.SunPathAnimation is True:
                    return True
            except:
                pass
        else:
            return False

    def Activated(self):
        modify_anim_indicator(animation = False)
        try:
            Gui.runCommand('StopRecordCamera',0)
        except:
            pass

#-----------------

ANIMATION = False

def modify_anim_indicator(animation = False):

    """Function to modify the indicator of a sun path animation"""

    global ANIMATION
    if animation is False:
        ANIMATION = False
        FreeCAD.Console.PrintMessage(translate(
            'SunPathAnimation', 'Sun Path animation, animation off.') + '\n')
    if animation is True:
        ANIMATION = True
        FreeCAD.Console.PrintMessage(translate(
            'SunPathAnimation', 'Sun Path animation, animation on.') + '\n')
    FreeCAD.ActiveDocument.recompute()

def calculate_frames():

    """Function to calculate the frames animation"""

    obj = FreeCAD.ActiveDocument.SunProperties
    # Data_interval
    hi = float(obj.start_hour) + float(obj.start_min/60)
    hf = float(obj.end_hour) + float(obj.end_min/60)
    time_range = hf - hi
    interv = float(obj.inter_hour) + float(obj.inter_min/60)
    if interv != 0:
        obj.Frames = int(time_range / interv)
    else:
        FreeCAD.Console.PrintMessage(translate(
            'SunPathAnimation', 'Interval must be non-zero!') + '\n')

def sun_path_animation():

    """Function to animate the sun path"""

    obj = FreeCAD.ActiveDocument.SunProperties
    # Data_interval
    fps = obj.Fps
    pause = 1/fps
    obj.Hour = obj.start_hour
    obj.Min = obj.start_min
    if obj.SunPathAnimation is True and obj.Image_from[0:2] == "03":
        Gui.runCommand('StartRecordRender',0)
        CL = FreeCAD.ActiveDocument.Clapperboard
        if CL.Frame_04OutputPath == "":
            FreeCAD.Console.PrintMessage(translate(
                "SunPathAnimation", "A path to save images is required! \n"
                "Click 'Stop Animation' to start again.") + '\n')
            return
    Properties.get_sun_position() # First step
    Gui.updateGui()
    print(f'{obj.City}, {obj.Day:0>2}/{obj.Month:0>2}/{obj.Year}, '
          f'{obj.Hour:0>2}:{obj.Min:0>2}')
    time.sleep(pause)
    for t in range(obj.Frames):
        minutes = obj.Min + obj.inter_min
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
        hour = obj.Hour + obj.inter_hour
        if hour < 24:
            obj.Hour = hour
        else:
            print("Hour is higher then 24")
            pass
        Properties.get_sun_position()
        Gui.updateGui()
        print(f'{obj.City}, {obj.Day:0>2}/{obj.Month:0>2}/{obj.Year}, '
              f'{obj.Hour:0>2}:{obj.Min:0>2}')
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
        FreeCAD.Console.PrintMessage(translate(
                        "SunPathAnimation",
                        "No MovieCamera found!") + '\n')
    # Clapperboard
    try:
        CL = FreeCAD.ActiveDocument.Clapperboard
        CL.Clap_05AnimFps = int(obj.Fps)
        CL.Frame_07R2OnRec = True
        CL.Clap_02AnimCurrentStep = 0
        Gui.Selection.addSelection(CL)
        Gui.runCommand('EnableMovieClapperboard',0)
        Gui.runCommand('PlayBackwardMovieAnimation',0)
        FreeCAD.ActiveDocument.recompute()
        FreeCAD.Console.PrintMessage(translate(
                        "SunPathAnimation",
                        "Render animation was set! \n"
                        "Click play to start the animation.") + '\n')
    except:
        FreeCAD.Console.PrintMessage(translate(
                        "SunPathAnimation",
                        "No Clapperboard found!") + '\n')

#---------------------------------------------------

if FreeCAD.GuiUp:
    FreeCAD.Gui.addCommand('StartSunPathAnimation',
                           StartSunPathAnimation())
    FreeCAD.Gui.addCommand('StopSunPathAnimation',
                           StopSunPathAnimation())
