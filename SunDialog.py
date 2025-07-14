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

"""This module implements the sun configuration dialog"""

import os
import re
import FreeCAD
import FreeCADGui as Gui
from PySide2 import QtUiTools, QtCore, QtWidgets
from PySide2.QtCore import QDate, QTime
from PySide.QtCore import QT_TRANSLATE_NOOP
import SunProperties as sp
import SunPathAnimation as spa

class SunConfigurationDialog(QtWidgets.QDialog):
    """A sun configuration dialog"""
    def __init__(self, parent = None):
        super(SunConfigurationDialog, self).__init__(parent)

        # Load the UI
        loader = QtUiTools.QUiLoader()
        ui_file = os.path.join(os.path.dirname(__file__), "SunSetup.ui")
        ui_file_obj = QtCore.QFile(ui_file)
        ui_file_obj.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(ui_file_obj, parent)
        ui_file_obj.close()

        # Correctly embed the loaded UI as a child widget
        self.setWindowTitle(self.ui.windowTitle())
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.ui)
        self.resize(self.ui.size())

        # Connect signals/slots
        # radioButton_1_epw_file and radioButton_2_Location
        self.ui.radioButton_1_epw_file.toggled.connect(self.epw_radio_toggled)
        # radioButton_2_Location
        self.ui.radioButton_2_Location.setEnabled(True)
        self.ui.radioButton_2_Location.toggled.connect(self.location_radio_toggled)
        # toolButton_1_epw_path
        self.ui.toolButton_1_epw_path.clicked.connect(self.open_epw_file_dialog)
        # Make label_1_epw_map_link clickable:
        self.ui.label_1_epw_map_link.setText(
            '<a href="https://www.ladybug.tools/epwmap/"'
            '>https://www.ladybug.tools/epwmap/</a>'
        )
        self.ui.label_1_epw_map_link.setOpenExternalLinks(True)
        self.ui.label_1_epw_map_link.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        # Make label_4_Equinoxes_link clickable:
        self.ui.label_4_Equinoxes_link.setText(
            '<a href="https://en.wikipedia.org/wiki/Equinox"'
            '>https://en.wikipedia.org/wiki/Equinox</a>'
        )
        self.ui.label_4_Equinoxes_link.setOpenExternalLinks(True)
        self.ui.label_4_Equinoxes_link.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        # Make label_4_Solstices_link clickable:
        self.ui.label_4_Solstices_link.setText(
            '<a href="https://en.wikipedia.org/wiki/Solstice"'
            '>https://en.wikipedia.org/wiki/Solstice</a>'
        )
        self.ui.label_4_Solstices_link.setOpenExternalLinks(True)
        self.ui.label_4_Solstices_link.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        # colorButtonTop
        self.ui.colorButtonTop.clicked.connect(self.choose_color)
        # colorButtonTop_2
        self.ui.colorButtonTop_2.clicked.connect(self.choose_color2)
        # pushButton_Apply
        self.ui.pushButton_Apply.clicked.connect(self.save_to_propeties)
        self.ui.pushButton_Apply.clicked.connect(self.get_results)
        # buttonBox_Cancel_OK
        self.ui.buttonBox_Cancel_OK.clicked.connect(self.accept)
        self.ui.buttonBox_Cancel_OK.rejected.connect(self.reject)

    def QT_TRANSLATE_NOOP(self, text):
        return text

    def GetResources(self):
        __dir__ = os.path.dirname(__file__)
        return {'Pixmap': __dir__ + '/icons/SunDialogIcon.svg',
                'MenuText': QT_TRANSLATE_NOOP(self, 'SunDialog'),
                'ToolTip': QT_TRANSLATE_NOOP(self, 'Create and manage the SunDialog. '
                            'After the sun configuration created, configure its properties'
                )
        }

    def IsActive(self):
        if Gui.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        try:
            FreeCAD.ActiveDocument.SunProperties
        except:
            sp.activated_sun_properties() #Create sun properties
        open_sun_configuration()

    ## Slots -------------
    def show_dialog(self):
        """Show dialog"""
        result = self.exec_()
        return result == QtWidgets.QDialog.Accepted

    def epw_radio_toggled(self, checked):
        """When EPW radio is checked, enable its fields and disable the others
        self.ui.radioButton_2_Location.setEnabled(not checked)
        Enable/disable fields for epw file"""
        self.ui.label_1_epw_path.setEnabled(checked)
        self.ui.toolButton_1_epw_path.setEnabled(checked)
        self.ui.lineEdit_1_epw_path.setEnabled(checked)
        self.ui.label_1_Get_epw_file.setEnabled(checked)
        self.ui.label_1_epw_map_link.setEnabled(checked)
        # Disable fields for location
        for w in [
            self.ui.label_2_City, self.ui.lineEdit_2_City,
            self.ui.label_2_Country, self.ui.lineEdit_2_Country,
            self.ui.label_2_Latitude, self.ui.lineEdit_2_Latitude,
            self.ui.label_2_Longitude, self.ui.lineEdit_2_Longitude,
            self.ui.label_2_Elevation, self.ui.lineEdit_2_Elevation,
            self.ui.label_2_Time_zone, self.ui.lineEdit_2_Time_zone,
            ]:
            w.setEnabled(not checked)
    def open_epw_file_dialog(self):
        """Open epw file dialog"""
        parent = None
        try:
            parent = Gui.getMainWindow()
        except Exception:
            parent = None
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent,  # parent window
            "Select epw file",
            "",
            "EPW Files (*.epw);;All Files (*)"
        )
        if fname:
            self.ui.lineEdit_1_epw_path.setText(fname)
            self.autofill_from_epw()

    def autofill_from_epw(self):
        """Get the EPW file path from the UI"""
        from ladybug.epw import EPW
        epw_path = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit_1_epw_path").text()
        if not epw_path or not os.path.isfile(epw_path):
            QtWidgets.QMessageBox.warning(
                self, "File Error",
                "If you want to use EPW, provide a valid file path."
            )
            return
        try:
            epw = EPW(epw_path)
            # Set the dialog fields with EPW info
            self.ui.lineEdit_2_City.setText(epw.location.city)
            self.ui.lineEdit_2_Country.setText(epw.location.country)
            self.ui.lineEdit_2_Latitude.setText(str(epw.location.latitude))
            self.ui.lineEdit_2_Longitude.setText(str(epw.location.longitude))
            self.ui.lineEdit_2_Elevation.setText(str(epw.location.elevation))
            self.ui.lineEdit_2_Time_zone.setText(str(epw.location.time_zone))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "File Error", f"Could not read EPW file:\n{e}")
            return

    def location_radio_toggled(self, checked):
        """When Location radio is checked, enable its fields and disable the others
        self.ui.radioButton_1_epw_file.setEnabled(not checked)
        Enable/disable fields for location"""
        for w in [
            self.ui.label_2_City, self.ui.lineEdit_2_City,
            self.ui.label_2_Country, self.ui.lineEdit_2_Country,
            self.ui.label_2_Latitude, self.ui.lineEdit_2_Latitude,
            self.ui.label_2_Longitude, self.ui.lineEdit_2_Longitude,
            self.ui.label_2_Elevation, self.ui.lineEdit_2_Elevation,
            self.ui.label_2_Time_zone, self.ui.lineEdit_2_Time_zone,
            ]:
            w.setEnabled(checked)
        # Disable fields for epw file
        self.ui.label_1_epw_path.setEnabled(not checked)
        self.ui.toolButton_1_epw_path.setEnabled(not checked)
        self.ui.lineEdit_1_epw_path.setEnabled(not checked)
        self.ui.label_1_Get_epw_file.setEnabled(not checked)
        self.ui.label_1_epw_map_link.setEnabled(not checked)

    def choose_color(self):
        """Open color dialog; returns QColor"""
        color = QtWidgets.QColorDialog.getColor(parent=self, title="Select Color")
        color_rgba = color.getRgb()
        color_rgb = (color_rgba[0], color_rgba[1], color_rgba[2])
        if color.isValid():
            self.ui.colorButtonTop.setStyleSheet(f"background-color: rgb{color_rgb};")

    def choose_color2(self):
        """Open color dialog; returns QColor"""
        color = QtWidgets.QColorDialog.getColor(parent=self, title="Select Color")
        color_rgba = color.getRgb()
        color_rgb = (color_rgba[0], color_rgba[1], color_rgba[2])
        if color.isValid():
            self.ui.colorButtonTop_2.setStyleSheet(f"background-color: rgb{color_rgb};")

    def get_properties_data(self):
        """Show the dialog with initial data"""
        try:
            obj1 = FreeCAD.ActiveDocument.SunProperties
            # epw file
            self.ui.lineEdit_1_epw_path.setText(obj1.epw_path)
            # Location
            self.ui.lineEdit_2_City.setText(obj1.City)
            self.ui.lineEdit_2_Country.setText(obj1.Country)
            self.ui.lineEdit_2_Latitude.setText(str(obj1.Latitude))
            self.ui.lineEdit_2_Longitude.setText(str(obj1.Longitude))
            self.ui.lineEdit_2_Elevation.setText(str(obj1.Elevation))
            self.ui.lineEdit_2_Time_zone.setText(str(obj1.TimeZone))
            self.ui.lineEdit_3_North_angle.setText((str(float(obj1.North))))
        except:
            print ("Dialog epw file or Location not changed from properties")
        try:
            obj1 = FreeCAD.ActiveDocument.SunProperties
            # Date and time
            self.ui.dateEdit_4_Date.setDate(QDate(obj1.Year, obj1.Month, obj1.Day))
            self.ui.timeEdit_4_time.setTime(QTime(obj1.Hour, obj1.Min))
            self.ui.checkBox_DaylightSaving.setChecked(obj1.DaylightSaving)
        except:
            print ("Dialog date and time not changed from properties")
        try:
            obj1 = FreeCAD.ActiveDocument.SunProperties
            # Sun light representation
            self.ui.checkBox_Sun_light_representation.setChecked(obj1.SunLightRepresentation)
            self.ui.lineEdit_Radius.setText(str(int(obj1.Radius)))
            self.ui.lineEdit_Distance.setText(str(int(obj1.Distance)))
            self.ui.checkBox_Ray_representation.setChecked(obj1.RayRepresentation)
            color = obj1.SunLightColor  # (R, G, B) floats in [0,1]
            self.ui.colorButtonTop.setStyleSheet(
                f"background-color: rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)});")
        except:
            print ("Dialog Sun light representation not changed from properties")
        try:
            obj1 = FreeCAD.ActiveDocument.SunProperties
            # Sun path diagram
            sp.get_diagram_from_site()
            self.ui.checkBox_Sun_path_diagram.setChecked(obj1.SunPathDiagram)
            self.ui.lineEdit_Position_x.setText(str(obj1.DiagPosition.x))
            self.ui.lineEdit_Position_y.setText(str(obj1.DiagPosition.y))
            self.ui.lineEdit_Position_z.setText(str(obj1.DiagPosition.z))
            color1 = obj1.DiagColor   # (R, G, B) floats in [0,1]
            self.ui.colorButtonTop_2.setStyleSheet(
                f"background-color: rgb({int(color1[0]*255)}, {int(color1[1]*255)}, {int(color1[2]*255)});")

        except:
            print ("Dialog Sun path diagram not changed from properties")
        try:
            obj1 = FreeCAD.ActiveDocument.SunProperties
            # Sun_path_animation
            self.ui.checkBox_Sun_path_animation.setChecked(obj1.SunPathAnimation)
            self.ui.timeEdit_1_From.setTime(QTime(obj1.InitialHour, obj1.InitialMin))
            self.ui.timeEdit_1_To.setTime(QTime(obj1.FinalHour, obj1.FinalMin))
            self.ui.timeEdit_1_Interval.setTime(QTime(obj1.Inter_hour, obj1.Inter_min))
            self.ui.lineEdit_2_Fps.setText(str(obj1.Fps))
            self.ui.checkBox_2_Recompute.setChecked(obj1.Recompute)
            self.ui.lineEdit_height.setText(str(obj1.Height))
            self.ui.lineEdit_width.setText(str(obj1.Width))
        except:
            print ("Dialog Sun_path_animation not changed from properties")
        try:
            obj1 = FreeCAD.ActiveDocument.SunProperties
            # Show_save
            self.ui.checkBox_Save_to.setChecked(obj1.Save_to)
            idx = self.ui.comboBox_Images.findText(obj1.Image_from)
            if idx >= 0:
                self.ui.comboBox_Images.setCurrentIndex(idx)
        except:
            print ("Dialog Show_save not changed from properties")

    def save_to_propeties(self):
        """Set data to properties"""
        try:
            obj1 = FreeCAD.ActiveDocument.SunProperties
            # epw file
            epw_path = self.ui.lineEdit_1_epw_path.text()
            obj1.epw_path = epw_path
        except:
            print ("epw file properties not changed from dialog")
        try:
            obj1 = FreeCAD.ActiveDocument.SunProperties
            # Location
            obj1.City = self.ui.lineEdit_2_City.text()
            obj1.Country = self.ui.lineEdit_2_Country.text()
            obj1.Latitude  = float(self.ui.lineEdit_2_Latitude.text())
            obj1.Longitude  = float(self.ui.lineEdit_2_Longitude.text())
            obj1.Elevation  = float(self.ui.lineEdit_2_Elevation.text())
            obj1.TimeZone  = int(self.ui.lineEdit_2_Time_zone.text())
            # North angle
            obj1.North  = float(self.ui.lineEdit_3_North_angle.text())
        except:
            print ("Location or North angle properties not changed from dialog")
        try:
            obj1 = FreeCAD.ActiveDocument.SunProperties
            # Date and time
            date_string2 = self.ui.dateEdit_4_Date.text()
            time_string2 = self.ui.timeEdit_4_time.text()
            obj1.Day = int(date_string2[0:2])
            obj1.Month = int(date_string2[3:5])
            obj1.Year = int(date_string2[6:10])
            obj1.Hour = int(time_string2[0:2])
            obj1.Min = int(time_string2[3:5])
            obj1.DaylightSaving = self.ui.checkBox_DaylightSaving.isChecked()
        except:
            print ("Date and time properties not changed from dialog")
        try:
            obj1 = FreeCAD.ActiveDocument.SunProperties
            # Sun light representation
            obj1.SunLightRepresentation = self.ui.checkBox_Sun_light_representation.isChecked()
            obj1.Radius  = self.ui.lineEdit_Radius.text()
            obj1.Distance  = self.ui.lineEdit_Distance.text()
            obj1.RayRepresentation = self.ui.checkBox_Ray_representation.isChecked()
            string_color = self.ui.colorButtonTop.styleSheet()
            string_rgb = re.findall(r'\d+', string_color)
            rgb_color = (int(string_rgb[0])/255, int(string_rgb[1])/255, int(string_rgb[2])/255)
            obj1.SunLightColor = rgb_color
        except:
            print ("Sun light representation properties not changed from dialog")
        try:
            obj1 = FreeCAD.ActiveDocument.SunProperties
            # Sun path diagram
            obj1.SunPathDiagram = self.ui.checkBox_Sun_path_diagram.isChecked()
            obj1.DiagPosition.x  = self.ui.lineEdit_Position_x.text()
            obj1.DiagPosition.y  = self.ui.lineEdit_Position_y.text()
            obj1.DiagPosition.z  = self.ui.lineEdit_Position_z.text()
            string_color2 = self.ui.colorButtonTop_2.styleSheet()
            string_rgb2 = re.findall(r'\d+', string_color2)
            rgb_color2 = (int(string_rgb2[0])/255, int(string_rgb2[1])/255, int(string_rgb2[2])/255)
            obj1.DiagColor = rgb_color2
            sp.send_diagram_to_site()
        except:
            print ("Sun path diagram properties not changed from dialog")
        try:
            obj1 = FreeCAD.ActiveDocument.SunProperties
            # Sun_path_animation
            obj1.SunPathAnimation = self.ui.checkBox_Sun_path_animation.isChecked()
            time_string3 = self.ui.timeEdit_1_From.text()
            obj1.InitialHour = int(time_string3[0:2])
            obj1.InitialMin = int(time_string3[3:5])
            time_string4 = self.ui.timeEdit_1_To.text()
            obj1.FinalHour  = int(time_string4[0:2])
            obj1.FinalMin = int(time_string4[3:5])
            time_string5 = self.ui.timeEdit_1_Interval.text()
            obj1.Inter_hour = int(time_string5[0:2])
            obj1.Inter_min = int(time_string5[3:5])
            obj1.Fps = float(self.ui.lineEdit_2_Fps.text())
            obj1.Recompute = self.ui.checkBox_2_Recompute.isChecked()
            obj1.Height = int(self.ui.lineEdit_height.text())
            obj1.Width = int(self.ui.lineEdit_width.text())
        except:
            print ("Sun_path_animation properties not changed from dialog")
        try:
            obj1 = FreeCAD.ActiveDocument.SunProperties
            # Show_save
            obj1.Image_from = self.ui.comboBox_Images.currentText()
            obj1.Save_to = self.ui.checkBox_Save_to.isChecked()
        except:
            print ("Show_save properties not changed from dialog")

        sp.get_sun_position()
        if obj1.Image_from == "Render 3D view" and obj1.SunPathAnimation is True:
            spa.set_render_animation()
        FreeCAD.ActiveDocument.recompute()

    def get_results(self):
        """Get results"""
        try:
            obj1 = FreeCAD.ActiveDocument.SunProperties
            self.ui.lineEdit_5_Altitude_result.setText(str(round(obj1.Altitude, 2)))
            self.ui.lineEdit_5_Azimuth_result.setText(str(round(obj1.Azimuth, 2)))
            self.ui.lineEdit_5_Day_hours_result.setText(str(obj1.DaylightHours))
            sun_rise_hour = int(obj1.Sunrise[0:2])
            sun_rise_min = int(obj1.Sunrise[3:5])
            self.ui.timeEdit_5_Sunrise_result.setTime(QTime(sun_rise_hour, sun_rise_min))
            noon_hour = int(obj1.Noon[0:2])
            noon_min = int(obj1.Noon[3:5])
            self.ui.timeEdit_5_Noon_result.setTime(QTime(noon_hour, noon_min))
            sun_set_hour = int(obj1.Sunset[0:2])
            sun_set_min = int(obj1.Sunset[3:5])
            self.ui.timeEdit_5_Sunset_result.setTime(QTime(sun_set_hour, sun_set_min))
            self.ui.lineEdit_Frames.setText(str(obj1.Frames))
        except:
            print ("Dialog Results not changed from properties")

def open_sun_configuration():
    """Open sun configuration"""
    dlg = SunConfigurationDialog()
    # Pre-fill data
    dlg.get_properties_data()
    dlg.get_results()
    if dlg.show_dialog():
        dlg.save_to_propeties()

if FreeCAD.GuiUp:
    FreeCAD.Gui.addCommand('SunConfigurationDialog', SunConfigurationDialog())
