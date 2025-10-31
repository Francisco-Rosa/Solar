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
from PySide import QtUiTools, QtCore, QtWidgets
from PySide.QtCore import QDate, QTime
from PySide.QtCore import QT_TRANSLATE_NOOP
import SunProperties as sp
import SunPathAnimation as spa

SD = None

class SunConfigurationDialog(QtWidgets.QDialog):
    """A sun configuration dialog"""

    def __init__(self, parent = None):
        super().__init__(parent)

        # Load the UI
        loader = QtUiTools.QUiLoader()
        ui_file = os.path.join(os.path.dirname(__file__), "SunSetup.ui")
        ui_file_obj = QtCore.QFile(ui_file)
        ui_file_obj.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(ui_file_obj, parent)
        ui_file_obj.close()

        # user_mod_path = os.path.join(FreeCAD.getUserAppDataDir(), "Mod")
        # SunSetupUi = FreeCADGui.PySideUic.loadUi(
                                  #user_mod_path + '/Solar/SunSetup.ui')
        # SunSetupUi.show()
        # self.ui = SunSetupUi

        self.setWindowTitle(QT_TRANSLATE_NOOP("SunDialog", "Sun configuration"))
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.ui)
        self.resize(self.ui.size())

        # Connect signals/slots
        # toolButton_1_epw_path
        self.ui.toolButton_1_epw_path.clicked.connect(self.open_epw_file_dialog)
        # Make label_1_epw_map_link clickable:
        self.ui.label_1_epw_map_link.setText(
            '<a href="https://www.ladybug.tools/epwmap/"'
            '>https://www.ladybug.tools/epwmap/</a>'
        )
        self.ui.label_1_epw_map_link.setOpenExternalLinks(True)
        self.ui.label_1_epw_map_link.setTextInteractionFlags(
                                     QtCore.Qt.TextBrowserInteraction)
        # Make label_4_Equinoxes_link clickable:
        self.ui.label_4_Equinoxes_link.setText(
            '<a href="https://en.wikipedia.org/wiki/Equinox"'
            '>https://en.wikipedia.org/wiki/Equinox</a>'
        )
        self.ui.label_4_Equinoxes_link.setOpenExternalLinks(True)
        self.ui.label_4_Equinoxes_link.setTextInteractionFlags(
                                       QtCore.Qt.TextBrowserInteraction)
        # Make label_4_Solstices_link clickable:
        self.ui.label_4_Solstices_link.setText(
            '<a href="https://en.wikipedia.org/wiki/Solstice"'
            '>https://en.wikipedia.org/wiki/Solstice</a>'
        )
        self.ui.label_4_Solstices_link.setOpenExternalLinks(True)
        self.ui.label_4_Solstices_link.setTextInteractionFlags(
                                       QtCore.Qt.TextBrowserInteraction)
        # colorButtonTop
        self.ui.colorButtonTop.clicked.connect(self.choose_color)
        # colorButtonTop_2
        self.ui.colorButtonTop_2.clicked.connect(self.choose_color2)
        # comboBox_Images
        self.ui.comboBox_Images.activated.connect(self.image_from_toggled)
        # pushButton_Apply
        self.ui.pushButton_Apply.clicked.connect(self.save_to_propeties)
        self.ui.pushButton_Apply.clicked.connect(self.get_results)
        # buttonBox_Cancel_OK
        self.ui.buttonBox_Cancel_OK.clicked.connect(self.accept)
        self.ui.buttonBox_Cancel_OK.rejected.connect(self.reject)
        # strings/translation
        self.ui.groupBox_sun_additional_config.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Adjust the other aspects of the solar study here"))
        self.ui.groupBox_sun_additional_config.setTitle(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Sun additional configurations"))
        self.ui.groupBox_show_save_image.setTitle(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Show and/or save image:"))
        self.ui.label_images_from.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Image from:"))
        self.ui.label_image_w_h.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Set the image resolution\n"
                    "Use for render images"))
        self.ui.label_image_w_h.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Images, w:"))
        self.ui.comboBox_Images.setItemText(0,
                    QT_TRANSLATE_NOOP("SunDialog",
                    "None/Reset"))
        self.ui.comboBox_Images.setItemText(1,
                    QT_TRANSLATE_NOOP("SunDialog",
                    "BW 3D view"))
        self.ui.comboBox_Images.setItemText(2,
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Color 3D view"))
        self.ui.comboBox_Images.setItemText(3,
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Render 3D view"))
        self.ui.comboBox_Images.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Select the scene type.\n"
                    "Use None/Reset to clear the settings.\n"
                    "Color 3D preview only works in FreeCAD-Link.\n"
                    "For Render 3D preview, install Render WB."))
        self.ui.lineEdit_width.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Set the image width in pixels\n"
                    "Use for render images"))
        self.ui.label_h.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "h:"))
        self.ui.lineEdit_height.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Set the image height in pixels\n"
                    "Use for render images"))
        self.ui.checkBox_Save_to.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Enable it to save the images created"))
        self.ui.checkBox_Save_to.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Save"))
        self.ui.checkBox_sun_light_config.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Enable it to view and adjust representations \n"
                    "of the sun and its path."))
        self.ui.checkBox_sun_light_config.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Sun light and diagram configurations"))
        self.ui.checkBox_Sun_path_animation.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Enable the sun path animation"))
        self.ui.checkBox_Sun_path_animation.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Sun path animation"))
        self.ui.checkBox_Sun_path_diagram.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "It is necessary to have an Arch Site object\n"
                    "to enable the sun path diagram.\n"
                    "For Color 3D view shadows, leave it disabled."))
        self.ui.checkBox_Sun_path_diagram.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Sun path diagram (Arch Site)"))
        self.ui.label_radius.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Radius:"))
        self.ui.label_Distance.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Distance:"))
        self.ui.label_Position.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Adjust the center position according to the project"))
        self.ui.label_Position.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Center"))
        self.ui.label_Color_2.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Color:"))
        self.ui.colorButtonTop_2.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Choose the color of the sun path diagram"))
        self.ui.checkBox_Sun_light_representation.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Enable the sun light representation"))
        self.ui.checkBox_Sun_light_representation.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Sun light"))
        self.ui.label_Ray_representation.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Ray representation:"))
        self.ui.checkBox_Ray_representation.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Visible"))
        self.ui.label_Color.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Color:"))
        self.ui.colorButtonTop.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Choose the color of the sunlight representation"))
        self.ui.label_1_From_2.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Time from:"))
        self.ui.label_1_Interval.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Interval:"))
        self.ui.label_2_Fps.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Fps:"))
        self.ui.timeEdit_1_From.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Adjust the time for the beginning of the sun path"))
        self.ui.label_1_To_2.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "to:"))
        self.ui.timeEdit_1_To.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Adjust the time for the end of the sun path"))
        self.ui.checkBox_sunrise_sunset.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Enable it to get the sunrise and sunset values, "
                    "then hit Apply."))
        self.ui.checkBox_sunrise_sunset.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Sunrise-Sunset"))
        self.ui.timeEdit_1_Interval.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Adjust the interval between each step of the solar path.\n"
                    "Must not be zero."))
        self.ui.checkBox_2_Recompute.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Enable it if you need to animate objects as well"))
        self.ui.checkBox_2_Recompute.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Recompute"))
        self.ui.lineEdit_2_Fps.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Enter the frames per second of the solar path animation"))
        self.ui.label_Frames.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Frames:"))
        self.ui.lineEdit_Frames.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Show the resulting total frames"))
        self.ui.groupBox_sun_position.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Set all data for sun position"))
        self.ui.groupBox_sun_position.setTitle(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Sun position"))
        self.ui.groupBox_results.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "These are the results of the adjustments made"))
        self.ui.groupBox_results.setTitle(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Results:"))
        self.ui.label_5_Sunrise.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Sunrise:"))
        self.ui.label_5_Noon.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Noon:"))
        self.ui.label_5_Sunset.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Sunset:"))
        self.ui.label_5_Altitude.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Altitude:"))
        self.ui.label_5_Azimuth.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Azimuth:"))
        self.ui.label_5_Day_hours.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Day hours:"))
        self.ui.label_4_Date_and_time.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Indicate the date and time \n"
                    "of the sun's position"))
        self.ui.label_4_Date_and_time.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Date and time:"))
        self.ui.radioButton_2_Location.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Activate this button to adjust \n"
                    "the sun position for a specific location"))
        self.ui.radioButton_2_Location.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Location:"))
        self.ui.label_2_City.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "City:"))
        self.ui.label_2_Country.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Country:"))
        self.ui.label_2_Latitude.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Latitude:"))
        self.ui.label_2_Longitude.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Longitude:"))
        self.ui.label_2_Elevation.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Elevation:"))
        self.ui.label_2_Time_zone.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Time zone:"))
        self.ui.label_3_North_angle.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Indicate the north angle"))
        self.ui.label_3_North_angle.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "North angle:"))
        self.ui.label_4_Equinoxes_Solstices.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Consult the equinoxes and solstices \n"
                    "in the next links"))
        self.ui.label_4_Equinoxes_Solstices.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Equin./Solst.:"))
        self.ui.checkBox_DaylightSaving.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Enable it for daylight saving periods"))
        self.ui.checkBox_DaylightSaving.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "DaylightSaving"))
        self.ui.radioButton_1_epw_file.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Enable this button to automatically \n"
                    "adjust the sun position for a location"))
        self.ui.radioButton_1_epw_file.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "epw file:"))
        self.ui.label_1_Get_epw_file.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Click the link to get the epw file"))
        self.ui.label_1_Get_epw_file.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Get epw file:"))
        self.ui.label_1_epw_map_link.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Click to download the epw file"))
        self.ui.label_1_epw_path.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "After downloading the epw file, \n"
                    "indicate its path on your machine"))
        self.ui.label_1_epw_path.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "epw file path:"))
        self.ui.lineEdit_1_epw_path.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "The epw file path on your machine"))
        self.ui.toolButton_1_epw_path.setToolTip(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Indicate the path of the epw file"))
        self.ui.pushButton_Apply.setText(
                    QT_TRANSLATE_NOOP("SunDialog",
                    "Apply"))

    def QT_TRANSLATE_NOOP(self, text):
        return text

    def GetResources(self):
        __dir__ = os.path.dirname(__file__)
        return {'Pixmap': __dir__ + '/icons/SunDialogIcon.svg',
                'MenuText': QT_TRANSLATE_NOOP(self, 'SunDialog'),
                'ToolTip': QT_TRANSLATE_NOOP(self,
                           'Create and manage the SunDialog. '
                           'After the sun configuration created, '
                           'configure its properties'
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
            sp.activated_sun_properties()
        open_sun_configuration()

    # Slots -------------
    def show_dialog(self):

        """Show dialog"""

        result = self.exec_()
        return result == QtWidgets.QDialog.Accepted

    def open_epw_file_dialog(self):

        """Open epw file dialog"""

        parent = None
        try:
            parent = Gui.getMainWindow()
        except Exception:
            parent = None
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
                                 parent,
                                 QT_TRANSLATE_NOOP("SunDialog",
                                 "Select epw file"),
                                 "",
                                 QT_TRANSLATE_NOOP("SunDialog",
                                 "EPW Files (*.epw);;All Files (*)")
                                 )
        if fname:
            self.ui.lineEdit_1_epw_path.setText(fname)
            self.autofill_from_epw()

    def autofill_from_epw(self):

        """Get the EPW file path from the UI"""

        from ladybug.epw import EPW
        epw_path = self.ui.findChild(QtWidgets.QLineEdit,
                                     "lineEdit_1_epw_path").text()
        if not epw_path or not os.path.isfile(epw_path):
            QtWidgets.QMessageBox.warning(
                                self, QT_TRANSLATE_NOOP(
                                        "SunDialog",
                                        "Warning"),
                                QT_TRANSLATE_NOOP(
                                        "SunDialog",
                                        "If you want to use EPW, "
                                        "provide a valid file path.")
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
            QtWidgets.QMessageBox.warning(self,
                                          QT_TRANSLATE_NOOP(
                                                "SunDialog",
                                                "File Error"),
                                          QT_TRANSLATE_NOOP(
                                                "SunDialog",
                                                f"Could not read EPW file:\n{e}"))
            return

    def choose_color(self):

        """Open color dialog, returns QColor"""

        color = QtWidgets.QColorDialog.getColor(
                                       parent=self,
                                       title="Select Color")
        color_rgba = color.getRgb()
        color_rgb = (color_rgba[0], color_rgba[1], color_rgba[2])
        if color.isValid():
            self.ui.colorButtonTop.setStyleSheet(
                                       f"background-color: rgb{color_rgb};")

    def choose_color2(self):

        """Open color dialog, returns QColor"""

        color = QtWidgets.QColorDialog.getColor(
                                       parent=self,
                                       title="Select Color")
        color_rgba = color.getRgb()
        color_rgb = (color_rgba[0], color_rgba[1], color_rgba[2])
        if color.isValid():
            self.ui.colorButtonTop_2.setStyleSheet(
                                       f"background-color: rgb{color_rgb};")

    def image_from_toggled(self):
        try:
            obj = FreeCAD.ActiveDocument.SunProperties
            if obj.Image_from == "Render 3D view":
                try:
                    FreeCAD.ActiveDocument.Project
                    self.ui.lineEdit_width.setEnabled(True)
                    self.ui.lineEdit_height.setEnabled(True)
                except:
                    pass
                try:
                    FreeCAD.ActiveDocument.Project
                    FreeCAD.ActiveDocument.Clapperboard
                except Exception:
                    self.ui.checkBox_Sun_path_animation.setChecked(False)
                    self.ui.checkBox_Sun_path_animation.setEnabled(False)
        except:
            pass
        if self.ui.comboBox_Images.currentText() == "Render 3D view":
            try:
                FreeCAD.ActiveDocument.Project
                self.ui.lineEdit_width.setEnabled(True)
                self.ui.lineEdit_height.setEnabled(True)
                self.ui.label_image_w_h.setEnabled(True)
                self.ui.label_h.setEnabled(True)
                self.ui.checkBox_Save_to.setEnabled(True)

            except:
                self.ui.lineEdit_width.setEnabled(False)
                self.ui.lineEdit_height.setEnabled(False)
                self.ui.label_image_w_h.setEnabled(False)
                self.ui.label_h.setEnabled(False)
                self.ui.checkBox_Save_to.setEnabled(False)
            try:
                FreeCAD.ActiveDocument.Project
                FreeCAD.ActiveDocument.Clapperboard
                self.ui.checkBox_Sun_path_animation.setEnabled(True)
            except Exception:
                self.ui.checkBox_Sun_path_animation.setChecked(False)
                self.ui.checkBox_Sun_path_animation.setEnabled(False)
        else:
            self.ui.lineEdit_width.setEnabled(False)
            self.ui.lineEdit_height.setEnabled(False)
            self.ui.label_image_w_h.setEnabled(False)
            self.ui.label_h.setEnabled(False)
            self.ui.checkBox_Save_to.setEnabled(True)
            self.ui.checkBox_Sun_path_animation.setEnabled(True)

    # Connection dialog x properties
    def get_properties_data(self):

        """Show the dialog with initial data"""

        try:
            obj = FreeCAD.ActiveDocument.SunProperties
            from SkyDomes import SD # import epw_path and north from Skydomes
            if SD is not None:
                self.ui.lineEdit_1_epw_path.setText(SD.epw_path)
                self.autofill_from_epw()
                print("epw path get from SkyDomes")
                self.ui.lineEdit_3_North_angle.setText((str(float(SD.north))))
            else:
                # Location
                self.ui.lineEdit_1_epw_path.setText(obj.epw_path)
                self.ui.lineEdit_2_City.setText(obj.City)
                self.ui.lineEdit_2_Country.setText(obj.Country)
                self.ui.lineEdit_2_Latitude.setText(str(obj.Latitude))
                self.ui.lineEdit_2_Longitude.setText(str(obj.Longitude))
                self.ui.lineEdit_2_Elevation.setText(str(obj.Elevation))
                self.ui.lineEdit_2_Time_zone.setText(str(obj.TimeZone))
                self.ui.lineEdit_3_North_angle.setText((str(float(obj.North))))
                print("epw path get from SunProperties")
        except:
            print ("Get properties: Dialog epw file or Location not changed")
        try:
            obj = FreeCAD.ActiveDocument.SunProperties
            # Date and time
            self.ui.dateEdit_4_Date.setDate(QDate(obj.Year, obj.Month, obj.Day))
            self.ui.timeEdit_4_time.setTime(QTime(obj.Hour, obj.Min))
            self.ui.checkBox_DaylightSaving.setChecked(obj.DaylightSaving)
        except:
            print ("Get properties: Date and time not changed")
        try:
            obj = FreeCAD.ActiveDocument.SunProperties
            # Sun light representation
            self.ui.checkBox_sun_light_config.setChecked(
                                            obj.SunLightDiagramConfig)
            self.ui.checkBox_Sun_light_representation.setChecked(
                                            obj.SunLightRepresentation)
            self.ui.checkBox_Ray_representation.setChecked(
                                            obj.RayRepresentation)
            self.ui.lineEdit_Radius.setText(str(int(obj.Radius)))
            color = obj.SunLightColor  # (R, G, B) floats in [0,1]
            self.ui.colorButtonTop.setStyleSheet(
                f"background-color: rgb({int(color[0]*255)}, "
                f"{int(color[1]*255)}, {int(color[2]*255)});")
            from SkyDomes import SD #import radius and distance from Skydomes
            if SD is not None:
                self.ui.lineEdit_Distance.setText(str(int(SD.radius)))
            else:
                self.ui.lineEdit_Distance.setText(str(int(obj.Distance)))

        except:
            print ("Get properties: Sun light representation not changed")
        try:
            obj = FreeCAD.ActiveDocument.SunProperties
            # Sun path diagram
            sp.get_diagram_from_site()
            self.ui.checkBox_Sun_path_diagram.setChecked(
                                              obj.SunPathDiagram)
            try:
                FreeCAD.ActiveDocument.Site
                self.ui.checkBox_Sun_path_diagram.setEnabled(True)
            except Exception:
                self.ui.checkBox_Sun_path_diagram.setChecked(False)
                self.ui.checkBox_Sun_path_diagram.setEnabled(False)
            from SkyDomes import SD #import position form Skydomes
            if SD is not None:
                self.ui.lineEdit_Position_x.setText(str(
                                        SD.position.x))
                self.ui.lineEdit_Position_y.setText(str(
                                        SD.position.y))
                self.ui.lineEdit_Position_z.setText(str(
                                        SD.position.z))
            else:
                self.ui.lineEdit_Position_x.setText(str(
                                        obj.DiagPosition.x))
                self.ui.lineEdit_Position_y.setText(str(
                                        obj.DiagPosition.y))
                self.ui.lineEdit_Position_z.setText(str(
                                        obj.DiagPosition.z))
            color1 = obj.DiagColor   # (R, G, B) floats in [0,1]
            self.ui.colorButtonTop_2.setStyleSheet(
                f"background-color: rgb({int(color1[0]*255)}, "
                f"{int(color1[1]*255)}, {int(color1[2]*255)});")
        except:
            print ("Get properties: Sun path diagram not changed")
        try:
            obj = FreeCAD.ActiveDocument.SunProperties
            # Sun_path_animation
            self.ui.checkBox_Sun_path_animation.setChecked(
                                    obj.SunPathAnimation)
            self.ui.timeEdit_1_From.setTime(QTime(
                                    obj.start_hour,
                                    obj.start_min))
            self.ui.timeEdit_1_To.setTime(QTime(
                                    obj.end_hour,
                                    obj.end_min))
            self.ui.checkBox_sunrise_sunset.setChecked(
                                    obj.sunrise_sunset)
            self.ui.timeEdit_1_Interval.setTime(QTime(
                                    obj.inter_hour,
                                    obj.inter_min))
            self.ui.lineEdit_2_Fps.setText(str(
                                    obj.Fps))
            self.ui.checkBox_2_Recompute.setChecked(
                                    obj.Recompute)
            self.ui.lineEdit_height.setText(str(
                                    obj.Height))
            self.ui.lineEdit_width.setText(str(
                                    obj.Width))
        except:
            print ("Get properties: Sun_path_animation not changed")
        try:
            obj = FreeCAD.ActiveDocument.SunProperties
            # Show_save
            self.ui.checkBox_Save_to.setChecked(
                                    obj.Save_to)
            idx1 = self.ui.comboBox_Images.findText(
                                    obj.Image_from)
            if idx1 >= 0:
                self.ui.comboBox_Images.setCurrentIndex(idx1)
        except Exception:
            print ("Dialog Show_save not changed from properties")
        self.image_from_toggled()

    def save_to_propeties(self):

        """Save data to properties"""

        try:
            obj = FreeCAD.ActiveDocument.SunProperties
            # epw file
            epw_path = self.ui.lineEdit_1_epw_path.text()
            obj.epw_path = epw_path
        except:
            print ("Save properties: epw path not changed from dialog")
        try:
            obj = FreeCAD.ActiveDocument.SunProperties
            # Location
            obj.City = self.ui.lineEdit_2_City.text()
            obj.Country = self.ui.lineEdit_2_Country.text()
            obj.Latitude  = float(self.ui.lineEdit_2_Latitude.text())
            obj.Longitude  = float(self.ui.lineEdit_2_Longitude.text())
            obj.Elevation  = float(self.ui.lineEdit_2_Elevation.text())
            obj.TimeZone  = int(self.ui.lineEdit_2_Time_zone.text())
        except:
            print ("Save properties: Location properties not changed from dialog")
        try:
            # North angle
            obj.North = float(self.ui.lineEdit_3_North_angle.text())
        except:
            print ("Save properties: "
                   "North angle properties not changed from dialog")
        try:
            obj = FreeCAD.ActiveDocument.SunProperties
            # Date and time
            date_string2 = self.ui.dateEdit_4_Date.text()
            time_string2 = self.ui.timeEdit_4_time.text()
            obj.Day = int(date_string2[0:2])
            obj.Month = int(date_string2[3:5])
            obj.Year = int(date_string2[6:10])
            obj.Hour = int(time_string2[0:2])
            obj.Min = int(time_string2[3:5])
            obj.DaylightSaving = self.ui.checkBox_DaylightSaving.isChecked()
        except:
            print ("Save properties: "
                   "Date and time properties not changed from dialog")
        try:
            obj = FreeCAD.ActiveDocument.SunProperties
            # Sun light representation
            obj.SunLightDiagramConfig = self.ui.checkBox_sun_light_config.isChecked()
            obj.SunLightRepresentation = self.ui.checkBox_Sun_light_representation.isChecked()
            obj.Radius = self.ui.lineEdit_Radius.text()
            obj.Distance = self.ui.lineEdit_Distance.text()
            obj.RayRepresentation = self.ui.checkBox_Ray_representation.isChecked()
            string_color = self.ui.colorButtonTop.styleSheet()
            string_rgb = re.findall(r'\d+', string_color)
            rgb_color = (int(string_rgb[0])/255,
                         int(string_rgb[1])/255,
                         int(string_rgb[2])/255)
            obj.SunLightColor = rgb_color
        except:
            print ("Save properties: "
                   "Sun light representation properties not changed from dialog")
        try:
            obj = FreeCAD.ActiveDocument.SunProperties
            # Sun path diagram
            obj.SunPathDiagram = self.ui.checkBox_Sun_path_diagram.isChecked()
            obj.DiagPosition.x = self.ui.lineEdit_Position_x.text()
            obj.DiagPosition.y = self.ui.lineEdit_Position_y.text()
            obj.DiagPosition.z = self.ui.lineEdit_Position_z.text()
            string_color2 = self.ui.colorButtonTop_2.styleSheet()
            string_rgb2 = re.findall(r'\d+', string_color2)
            rgb_color2 = (int(string_rgb2[0])/255,
                          int(string_rgb2[1])/255,
                          int(string_rgb2[2])/255)
            obj.DiagColor = rgb_color2
        except:
            print ("Save properties: "
                   "Sun path diagram properties not changed from dialog")
        try:
            obj = FreeCAD.ActiveDocument.SunProperties
            # Sun_path_animation
            obj.SunPathAnimation = self.ui.checkBox_Sun_path_animation.isChecked()
            time_string3 = self.ui.timeEdit_1_From.text()
            obj.start_hour = int(time_string3[0:2])
            obj.start_min = int(time_string3[3:5])
            time_string4 = self.ui.timeEdit_1_To.text()
            obj.end_hour  = int(time_string4[0:2])
            obj.end_min = int(time_string4[3:5])
            obj.sunrise_sunset = self.ui.checkBox_sunrise_sunset.isChecked()
            time_string5 = self.ui.timeEdit_1_Interval.text()
            obj.inter_hour = int(time_string5[0:2])
            obj.inter_min = int(time_string5[3:5])
            obj.Fps = float(self.ui.lineEdit_2_Fps.text())
            obj.Recompute = self.ui.checkBox_2_Recompute.isChecked()
            obj.Height = int(self.ui.lineEdit_height.text())
            obj.Width = int(self.ui.lineEdit_width.text())
        except:
            print ("Save properties: "
                   "Sun_path_animation properties not changed from dialog")
        try:
            obj = FreeCAD.ActiveDocument.SunProperties
            # Show_save
            obj.Image_from = self.ui.comboBox_Images.currentText()
            obj.Save_to = self.ui.checkBox_Save_to.isChecked()
        except:
            print ("Save properties: Show_save properties not changed from dialog")

        sp.get_sun_position()
        sp.send_diagram_to_site()
        if obj.Image_from == "Render 3D view" and obj.SunPathAnimation is True:
            spa.set_render_animation()
        FreeCAD.ActiveDocument.recompute()

    def get_results(self):

        """Get results"""

        try:
            obj = FreeCAD.ActiveDocument.SunProperties
            self.ui.label_altitude_result.setText(str(
                                        round(obj.Altitude, 2)))
            self.ui.label_azimute_result.setText(str(
                                        round(obj.Azimuth, 2)))
            self.ui.label_day_hours_result.setText(
                                        obj.DaylightHours)
            self.ui.label_sunrise_result.setText(
                                        obj.Sunrise)
            self.ui.label_noon_result.setText(
                                        obj.Noon)
            self.ui.label_sunset_result.setText(
                                        obj.Sunset)
            # Update animation date
            if obj.sunrise_sunset is True:
                sunrise_hour = int(obj.Sunrise[0:2])
                sunrise_min = int(obj.Sunrise[3:5])
                self.ui.timeEdit_1_From.setTime(QTime(
                                        sunrise_hour, sunrise_min))
                sunset_hour = int(obj.Sunset[0:2])
                sunset_min = int(obj.Sunset[3:5])
                self.ui.timeEdit_1_To.setTime(
                                        QTime(sunset_hour, sunset_min))
            self.ui.lineEdit_Frames.setText(str(obj.Frames))
        except:
            print ("Dialog Results not changed from properties")

def open_sun_configuration():

    """Open sun configuration"""

    dlg = SunConfigurationDialog()
    dlg.get_properties_data()
    dlg.get_results()
    if dlg.show_dialog():
        dlg.save_to_propeties()

if FreeCAD.GuiUp:
    FreeCAD.Gui.addCommand('SunConfigurationDialog',
                           SunConfigurationDialog())
