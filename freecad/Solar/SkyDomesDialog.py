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

"""This module implements the Sky Domes configuration dialog"""

import os
import FreeCAD
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets
from PySide.QtCore import QDate
import freecad.Solar.SkyDomes as SkyDomes

translate = FreeCAD.Qt.translate

LanguagePath = os.path.dirname(__file__) + '/translations'
Gui.addLanguagePath(LanguagePath)

SD = None

class SkyDomesConfigurationDialog(QtWidgets.QDialog):

    """A Sky Domes configuration dialog"""

    def __init__(self, parent = None):

        super().__init__(parent)

        # Load the UI
        ui_file = os.path.join(os.path.dirname(__file__), "SkyDomes.ui")
        self.ui = Gui.PySideUic.loadUi(ui_file)

        # Run tests on FC Pynthon console
        """
        user_mod_path = os.path.join(FreeCAD.getUserAppDataDir(), "Mod")
        SkyDomesUi = FreeCADGui.PySideUic.loadUi(
                        user_mod_path + '/Solar/freecad/Solar/SkyDomes.ui')
        SkyDomesUi.show()
        """

        # Correctly embed the loaded UI as a child widget
        self.setWindowTitle(translate("SkyDomesDialog", "Sky Domes configuration"))
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.ui)
        self.resize(self.ui.size())

        # Connect signals/slots
        # toolButton_epw_path
        self.ui.toolButton_epw_path.clicked.connect(self.open_epw_file_dialog)
        # Make label_epw_map_link clickable:
        self.ui.label_epw_map_link.setText(
            '<a href="https://www.ladybug.tools/epwmap/"'
            '>https://www.ladybug.tools/epwmap/</a>'
        )
        self.ui.label_epw_map_link.setOpenExternalLinks(True)
        self.ui.label_epw_map_link.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        # time to and from
        self.ui.spinBox_time_from.valueChanged.connect(self.time_toggled)
        self.ui.spinBox_time_to.valueChanged.connect(self.time_toggled)
        # checkBox_center_vectors
        self.ui.checkBox_center_vectors.toggled.connect(self.bool_changed)
        # horizontalSlider_transparency
        self.ui.horizontalSlider_transparency.valueChanged.connect(self.value_changed)
        # pushButton_Apply
        self.ui.pushButton_Apply.clicked.connect(self.on_button_apply_clicked)
        # buttonBox_Cancel_OK
        self.ui.buttonBox_Cancel_OK.clicked.connect(self.accept)
        self.ui.buttonBox_Cancel_OK.rejected.connect(self.reject)
        # translation
        #groupBox_epw_location
        self.ui.groupBox_epw_location.setTitle(
                        translate("SkyDomesDialog",
                        "Epw/ Location"))
        self.ui.groupBox_epw_location.setToolTip(
                        translate("SkyDomesDialog",
                        "Location data get from epw file."))
        #groupBox_epw_file
        self.ui.groupBox_epw_file.setTitle(
                        translate("SkyDomesDialog",
                        "epw file"))
        #label_Get_epw_file
        self.ui.label_Get_epw_file.setText(
                        translate("SkyDomesDialog",
                        "Get epw file:"))
        self.ui.label_Get_epw_file.setToolTip(
                        translate("SkyDomesDialog",
                        "Click the link to get the epw file"))
        #label_epw_map_link
        self.ui.label_epw_map_link.setToolTip(
                        translate("SkyDomesDialog",
                        "Click to download the epw file"))
        #label_epw_path
        self.ui.label_epw_path.setText(
                        translate("SkyDomesDialog",
                        "epw file path:"))
        self.ui.label_epw_path.setToolTip(
                        translate("SkyDomesDialog",
                        "After downloading the epw file, \n"
                        "indicate the path on your machine"))
        #lineEdit_epw_path
        self.ui.lineEdit_epw_path.setToolTip(
                        translate("SkyDomesDialog",
                        "The epw file path on your machine"))
        #toolButton_epw_path
        self.ui.toolButton_epw_path.setToolTip(
                        translate("SkyDomesDialog",
                        "Indicate the epw file path"))
        #groupBox_location
        self.ui.groupBox_location.setTitle(
                        translate("SkyDomesDialog",
                        "Location"))
        #label_City
        self.ui.label_City.setText(
                        translate("SkyDomesDialog",
                        "City:"))
        #label_Country
        self.ui.label_Country.setText(
                        translate("SkyDomesDialog",
                        "Country:"))
        #label_Latitude
        self.ui.label_Latitude.setText(
                        translate("SkyDomesDialog",
                        "Latitude:"))
        #label_Longitude
        self.ui.label_Longitude.setText(
                        translate("SkyDomesDialog",
                        "Longitude:"))
        #label_Elevation
        self.ui.label_Elevation.setText(
                        translate("SkyDomesDialog",
                        "Elevation:"))
        #label_Time_zone
        self.ui.label_Time_zone.setText(
                        translate("SkyDomesDialog",
                        "Time zone:"))
        #label_North_angle
        self.ui.label_North_angle.setText(
                        translate("SkyDomesDialog",
                        "North angle:"))
        #lineEdit_North_angle
        self.ui.lineEdit_North_angle.setToolTip(
                        translate("SkyDomesDialog",
                        "Indicate the true north.\n"
                        "Values ​​in a clockwise direction, \n"
                        "with zero in the direction of the y-axis"))
        #groupBox_sky_domes_configuration
        self.ui.groupBox_sky_domes_configuration.setTitle(
                        translate("SkyDomesDialog",
                        "Sky Domes configurations"))
        #label_radius
        self.ui.label_radius.setText(
                        translate("SkyDomesDialog",
                        "Radius:"))
        #lineEdit_Radius
        self.ui.lineEdit_Radius.setToolTip(
                        translate("SkyDomesDialog",
                        "Set the radius of the sky dome (mm)."))
        #label_Position
        self.ui.label_Position.setText(
                        translate("SkyDomesDialog",
                        "Position:"))
        self.ui.label_Position.setToolTip(
                        translate("SkyDomesDialog",
                        "Adjust the center of the dome according to the project."))
        #lineEdit_Position_x
        self.ui.lineEdit_Position_x.setToolTip(
                        translate("SkyDomesDialog",
                        "Adjust the x coordinate of the center of the \n"
                        "dome according to the project (mm)."))
        #lineEdit_Position_y
        self.ui.lineEdit_Position_y.setToolTip(
                        translate("SkyDomesDialog",
                        "Adjust the y coordinate of the center of the \n"
                        "dome according to the project (mm)."))
        #lineEdit_Position_z
        self.ui.lineEdit_Position_z.setToolTip(
                        translate("SkyDomesDialog",
                        "Adjust the z coordinate of the center of the \n"
                        "dome according to the project (mm)."))
        #groupBox_analysis_period
        self.ui.groupBox_analysis_period.setTitle(
                        translate("SkyDomesDialog",
                        "Analysis period"))
        self.ui.groupBox_analysis_period.setToolTip(
                        translate("SkyDomesDialog",
                        "Analysis period between two dates and \n"
                        "hours of the year."))
        #label_Date_from
        self.ui.label_Date_from.setText(
                        translate("SkyDomesDialog",
                        "Date from:"))
        #dateEdit_date_from
        self.ui.dateEdit_date_from.setToolTip(
                        translate("SkyDomesDialog",
                        "Indicate the start date of the analysis period."))
        #label_date_to
        self.ui.label_date_to.setText(
                        translate("SkyDomesDialog",
                        "to:"))
        #dateEdit_date_to
        self.ui.dateEdit_date_to.setToolTip(
                        translate("SkyDomesDialog",
                        "Indicate the end date of the analysis period."))
        #label_Time_from
        self.ui.label_Time_from.setText(
                        translate("SkyDomesDialog",
                        "Time from:"))
        #spinBox_time_from
        self.ui.spinBox_time_from.setToolTip(
                       translate("SkyDomesDialog",
                       "Indicate the start time of the analysis period."))
        #label_to
        self.ui.label_to.setText(
                       translate("SkyDomesDialog",
                       "to:"))
        #spinBox_time_to
        self.ui.spinBox_time_to.setToolTip(
                       translate("SkyDomesDialog",
                       "Indicate the end time of the analysis period."))
        #label_Timestep
        self.ui.label_Timestep.setText(
                        translate("SkyDomesDialog",
                        "Timestep"))
        #comboBox_timestep
        self.ui.comboBox_timestep.setToolTip(
                       translate("SkyDomesDialog",
                       "Specify the number of times per hour \n"
                       "the linear interpolation of sub-hourly \n"
                       "values ​​will be performed.\n"
                       "It works only with time intervals \n"
                       "from 0 to 23 hours.\n"
                       "Note that larger numbers \n"
                       "will increase the computation time.\n"
                       ))
        #checkBox_leap_year
        self.ui.checkBox_leap_year.setText(
                       translate("SkyDomesDialog",
                       "leap year"))
        self.ui.checkBox_leap_year.setToolTip(
                       translate("SkyDomesDialog",
                       "Indicate whether the Analysis\n"
                       "Period represents a leap year."))
        #groupBox_sky_domes
        self.ui.groupBox_sky_domes.setTitle(
                       translate("SkyDomesDialog",
                       "Sky Domes"))
        #label_model
        self.ui.label_model.setText(
                       translate("SkyDomesDialog",
                       "Model:"))
        #comboBox_model
        self.ui.comboBox_model.setItemText(0,
                       translate("SkyDomesDialog",
                       "Tregenza"))
        self.ui.comboBox_model.setItemText(1,
                       translate("SkyDomesDialog",
                       "Reinhart"))
        self.ui.comboBox_model.setToolTip(
                       translate("SkyDomesDialog",
                       "Choose between the low-resolution model (Tregenza)\n"
                       "or high-resolution (Reinhart) one.\n"
                       "Remember that the Reinhart model can take a \n"
                       "considerable amount of time to calculate."))
        #label_Units
        self.ui.label_Units.setText(
                       translate("SkyDomesDialog",
                       "Units:"))
        #comboBox_units
        from freecad.Solar.LBComponents import RESUL_01, RESUL_02
        self.ui.comboBox_units.setItemText(0, f"00 - {RESUL_01}")
        self.ui.comboBox_units.setItemText(1, f"01 - {RESUL_02}")
        self.ui.comboBox_units.setToolTip(
                       translate("SkyDomesDialog",
                       "Indicate whether the sky dome should be plotted with \n"
                       "units of total Radiation (kWh/m²) or \n"
                       "average Irradiance (W/m²)."))
        #checkBox_direct_diffuse
        self.ui.checkBox_direct_diffuse.setText(
                       translate("SkyDomesDialog",
                       "Direct and diffuse"))
        self.ui.checkBox_direct_diffuse.setToolTip(
                       translate("SkyDomesDialog",
                       "Enable it to visualize the direct and diffuse domes."))
        #checkBox_center_vectors
        self.ui.checkBox_center_vectors.setText(
                       translate("SkyDomesDialog",
                       "Center vectors"))
        self.ui.checkBox_center_vectors.setToolTip(
                       translate("SkyDomesDialog",
                       "Enable it to visualize the center vectors of each dome patch."))
        #label_5Transparency
        self.ui.label_5Transparency.setText(
                       translate("SkyDomesDialog",
                       "Transparency"))
        #horizontalSlider_transparency
        self.ui.horizontalSlider_transparency.setToolTip(
                       translate("SkyDomesDialog",
                       "Adjust the transparency of the Sky Domes."))
        #groupBox_Legend
        self.ui.groupBox_Legend.setTitle(
                        translate("SkyDomesDialog",
                        "Legend Bar"))
        #label_color_count
        self.ui.label_color_count.setText(
                        translate("SkyDomesDialog",
                        "Num. of colors:"))
        self.ui.label_color_count.setToolTip(
                        translate("SkyDomesDialog",
                        "Indicate the number of colors of the legend bar \n"
                        "(default: 11)."))
        #label_color_set
        self.ui.label_color_set.setText(
                       translate("SkyDomesDialog",
                       "Color palette:"))
        #comboBox_color_set
        from freecad.Solar.LBComponents import COLORS_00, COLORS_01, COLORS_02, COLORS_03
        from freecad.Solar.LBComponents import COLORS_04, COLORS_05, COLORS_06, COLORS_07
        from freecad.Solar.LBComponents import COLORS_08, COLORS_09, COLORS_10, COLORS_11
        from freecad.Solar.LBComponents import COLORS_12, COLORS_13, COLORS_14, COLORS_15
        from freecad.Solar.LBComponents import COLORS_16, COLORS_17, COLORS_18, COLORS_19
        from freecad.Solar.LBComponents import COLORS_20, COLORS_21, COLORS_22, COLORS_23
        from freecad.Solar.LBComponents import COLORS_24, COLORS_25, COLORS_26, COLORS_27
        from freecad.Solar.LBComponents import COLORS_28, COLORS_29, COLORS_30, COLORS_31
        from freecad.Solar.LBComponents import COLORS_32
        self.ui.comboBox_color_set.setItemText(0, f"00 - {COLORS_00}")
        self.ui.comboBox_color_set.setItemText(1, f"01 - {COLORS_01}")
        self.ui.comboBox_color_set.setItemText(2, f"02 - {COLORS_02}")
        self.ui.comboBox_color_set.setItemText(3, f"03 - {COLORS_03}")
        self.ui.comboBox_color_set.setItemText(4, f"04 - {COLORS_04}")
        self.ui.comboBox_color_set.setItemText(5, f"05 - {COLORS_05}")
        self.ui.comboBox_color_set.setItemText(6, f"06 - {COLORS_06}")
        self.ui.comboBox_color_set.setItemText(7, f"07 - {COLORS_07}")
        self.ui.comboBox_color_set.setItemText(8, f"08 - {COLORS_08}")
        self.ui.comboBox_color_set.setItemText(9, f"09 - {COLORS_09}")
        self.ui.comboBox_color_set.setItemText(10, f"10 - {COLORS_10}")
        self.ui.comboBox_color_set.setItemText(11, f"11 - {COLORS_11}")
        self.ui.comboBox_color_set.setItemText(12, f"12 - {COLORS_12}")
        self.ui.comboBox_color_set.setItemText(13, f"13 - {COLORS_13}")
        self.ui.comboBox_color_set.setItemText(14, f"14 - {COLORS_14}")
        self.ui.comboBox_color_set.setItemText(15, f"15 - {COLORS_15}")
        self.ui.comboBox_color_set.setItemText(16, f"16 - {COLORS_16}")
        self.ui.comboBox_color_set.setItemText(17, f"17 - {COLORS_17}")
        self.ui.comboBox_color_set.setItemText(18, f"18 - {COLORS_18}")
        self.ui.comboBox_color_set.setItemText(19, f"19 - {COLORS_19}")
        self.ui.comboBox_color_set.setItemText(20, f"20 - {COLORS_20}")
        self.ui.comboBox_color_set.setItemText(21, f"21 - {COLORS_21}")
        self.ui.comboBox_color_set.setItemText(22, f"22 - {COLORS_22}")
        self.ui.comboBox_color_set.setItemText(23, f"23 - {COLORS_23}")
        self.ui.comboBox_color_set.setItemText(24, f"24 - {COLORS_24}")
        self.ui.comboBox_color_set.setItemText(25, f"25 - {COLORS_25}")
        self.ui.comboBox_color_set.setItemText(26, f"26 - {COLORS_26}")
        self.ui.comboBox_color_set.setItemText(27, f"27 - {COLORS_27}")
        self.ui.comboBox_color_set.setItemText(28, f"28 - {COLORS_28}")
        self.ui.comboBox_color_set.setItemText(29, f"29 - {COLORS_29}")
        self.ui.comboBox_color_set.setItemText(30, f"30 - {COLORS_30}")
        self.ui.comboBox_color_set.setItemText(31, f"31 - {COLORS_31}")
        self.ui.comboBox_color_set.setItemText(32, f"32 - {COLORS_32}")
        self.ui.comboBox_color_set.setToolTip(
                       translate("SkyDomesDialog",
                       "Choose the legend bar color palette."))
        #pushButton_Apply
        self.ui.pushButton_Apply.setText(
                       translate("SkyDomesDialog",
                       "Apply"))

    # Slots
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
            parent,  # parent window
            translate("SkyDomesDialog", "Select epw file"),
            "",
            "EPW Files (*.epw);;All Files (*)"
        )
        if fname:
            self.ui.lineEdit_epw_path.setText(fname)
            self.autofill_from_epw()

    def autofill_from_epw(self):

        """Get the EPW file path and save it"""

        from ladybug.epw import EPW
        epw_path = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit_epw_path").text()
        if not epw_path or not os.path.isfile(epw_path):
            QtWidgets.QMessageBox.warning(
                self, translate("SkyDomesDialog", "Warning"),
                translate("SkyDomesDialog",
                                  "Indicate a epw file before "
                                  "close the dialog Sky Domes!")
            )
            return
        try:
            epw = EPW(epw_path)
            # Set the dialog fields with EPW info
            self.ui.label_city_value.setText(epw.location.city)
            self.ui.label_country_value.setText(epw.location.country)
            self.ui.label_latitude_value.setText(str(epw.location.latitude))
            self.ui.label_longitude_value.setText(str(epw.location.longitude))
            self.ui.label_elevation_value.setText(str(epw.location.elevation))
            self.ui.label_time_zone_value.setText(str(epw.location.time_zone))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "File Error", f"Could not read EPW file:\n{e}")
            return

    def time_toggled(self):
        if self.ui.spinBox_time_from.value() == 0 and self.ui.spinBox_time_to.value() == 23:
            self.ui.comboBox_timestep.setEnabled(True)
        else:
            self.ui.comboBox_timestep.setCurrentIndex(0)
            self.ui.comboBox_timestep.setEnabled(False)

    def bool_changed(self):
        from .SkyDomes import SD
        if SD is not None:
            try:
                SD.Group[0].Group[3]
                if self.ui.checkBox_center_vectors.isChecked() is True:
                    SD.Group[0].Group[3].Visibility = True
                else:
                    SD.Group[0].Group[3].Visibility = False
            except Exception:
                print("No center vectors was found!")

    def value_changed(self):
        value = str(self.ui.horizontalSlider_transparency.value())
        self.ui.label_transp_value.setText(value)
        from .SkyDomes import SD
        if SD is not None:
            try:
                SD.Group[0].Group[0].ViewObject.Transparency = int(value)
                SD.Group[1].Group[0].ViewObject.Transparency = int(value)
                SD.Group[2].Group[0].ViewObject.Transparency = int(value)
                SD.transparency = int(value)
                FreeCAD.ActiveDocument.recompute()
            except Exception:
                print("There are no clones to modify transparency!")
        else:
            print("Try modify transparency, but SD is None!")

    # Connection dialog x sky domes properties
    def get_properties_data(self):

        """Get data from Sky Domes properties and send them to dialog"""

        from .SkyDomes import SD, SD_NEW
        if SD is not None:
            # epw file
            if SD_NEW is True:
                try:
                    obj1 = FreeCAD.ActiveDocument.SunProperties
                    # epw file
                    if obj1.epw_path != "":
                        self.ui.lineEdit_epw_path.setText(obj1.epw_path)
                        FreeCAD.Console.PrintMessage(translate("SkyDomesDialog",
                            "epw path get from Sun Path" + '\n'))
                    else:
                        self.ui.lineEdit_epw_path.setText(SD.epw_path)
                    # North
                    self.ui.lineEdit_North_angle.setText((str(float(obj1.North))))
                    # radius and position
                    self.ui.lineEdit_Radius.setText(str(int(obj1.Distance)))
                    self.ui.lineEdit_Position_x.setText(str(obj1.DiagPosition.x))
                    self.ui.lineEdit_Position_y.setText(str(obj1.DiagPosition.y))
                    self.ui.lineEdit_Position_z.setText(str(obj1.DiagPosition.z))
                except:
                    pass
                # Create sky domes model
                self.ui.label_model.setEnabled(True)
                self.ui.comboBox_model.setEnabled(True)
            else:
                # epw file
                self.ui.lineEdit_epw_path.setText(SD.epw_path)
                #print("epw path get from SD")
                # North
                self.ui.lineEdit_North_angle.setText((str(float(SD.north))))
                # radius and position
                self.ui.lineEdit_Radius.setText(str(int(SD.radius)))
                self.ui.lineEdit_Position_x.setText(str(SD.position.x))
                self.ui.lineEdit_Position_y.setText(str(SD.position.y))
                self.ui.lineEdit_Position_z.setText(str(SD.position.z))
                # Create sky domes model
                self.ui.label_model.setEnabled(False)
                self.ui.comboBox_model.setEnabled(False)
            self.autofill_from_epw()
            # Analysis period
            self.ui.dateEdit_date_from.setDate(QDate(SD.start_year, SD.start_month, SD.start_day))
            self.ui.dateEdit_date_to.setDate(QDate(SD.end_year, SD.end_month, SD.end_day))
            self.ui.spinBox_time_from.setValue(SD.start_hour)
            self.ui.spinBox_time_to.setValue(SD.end_hour)
            idx = self.ui.comboBox_timestep.findText(SD.timestep)
            if idx >= 0:
                self.ui.comboBox_timestep.setCurrentIndex(idx)
            self.ui.checkBox_leap_year.setChecked(SD.leap_year)
            # Sky domes
            idx3 = self.ui.comboBox_model.findText(SD.model)
            if idx3 >= 0:
                self.ui.comboBox_model.setCurrentIndex(idx3)
            idx4 = self.ui.comboBox_units.findText(SD.units)
            if idx4 >= 0:
                self.ui.comboBox_units.setCurrentIndex(idx4)
            self.ui.checkBox_direct_diffuse.setChecked(SD.direct_diffuse_domes)
            self.ui.checkBox_center_vectors.setChecked(SD.center_vectors)
            # Transparency
            self.ui.label_transp_value.setText(str(SD.transparency))
            self.ui.horizontalSlider_transparency.setValue(SD.transparency)
            # Legend
            self.ui.spinBox_color_count.setValue(SD.color_count)
            idx3 = self.ui.comboBox_color_set.findText(SD.color_set)
            if idx3 >= 0:
                self.ui.comboBox_color_set.setCurrentIndex(idx3)
        else:
            FreeCAD.Console.PrintMessage('get properties: ' + translate(
                'SkyDomesDialog', 'There is no Sky Domes group!') + '\n')

    def save_to_propeties(self):

        """Save data from dialog to Sky Domes properties"""

        from .SkyDomes import SD, SD_NEW
        if SD is not None:

            # epw file
            epw_path = self.ui.lineEdit_epw_path.text()
            SD.epw_path = epw_path
            # Location
            SD.city = self.ui.label_city_value.text()
            # North angle
            SD.north  = float(self.ui.lineEdit_North_angle.text())
            # radius and position
            SD.radius = self.ui.lineEdit_Radius.text()
            SD.position.x  = self.ui.lineEdit_Position_x.text()
            SD.position.y  = self.ui.lineEdit_Position_y.text()
            SD.position.z  = self.ui.lineEdit_Position_z.text()

            # Analysis period

            date_string1 = self.ui.dateEdit_date_from.date()

            SD.start_month = date_string1.month()
            SD.start_year = date_string1.year()
            SD.start_day = date_string1.day()

            date_string2 = self.ui.dateEdit_date_to.date()

            SD.end_month = date_string2.month()
            SD.end_year = date_string2.year()
            SD.end_day = date_string2.day()

            SD.start_hour = self.ui.spinBox_time_from.value()
            SD.end_hour = self.ui.spinBox_time_to.value()
            # Sky domes
            SD.timestep = self.ui.comboBox_timestep.currentText()
            SD.leap_year = self.ui.checkBox_leap_year.isChecked()
            SD.model = self.ui.comboBox_model.currentText()
            #SD.units = self.ui.comboBox_units.currentText()
            prefix1 = int(self.ui.comboBox_units.currentText()[0:2])
            units_list = SD.getEnumerationsOfProperty("units")
            SD.units = units_list[prefix1]
            SD.direct_diffuse_domes = self.ui.checkBox_direct_diffuse.isChecked()
            SD.center_vectors = self.ui.checkBox_center_vectors.isChecked()
            if SD_NEW is False:
                SD.Group[1].Visibility = SD.direct_diffuse_domes
                SD.Group[2].Visibility = SD.direct_diffuse_domes
            SD.transparency = self.ui.horizontalSlider_transparency.value()
            # Legend
            SD.leg_title = self.ui.comboBox_units.currentText()[5:]
            SD.color_count = self.ui.spinBox_color_count.value()
            #SD.color_set = self.ui.comboBox_color_set.currentText()
            prefix2 = int(self.ui.comboBox_color_set.currentText()[0:2])
            color_set_list = SD.getEnumerationsOfProperty("color_set")
            SD.color_set = color_set_list[prefix2]
        else:
            FreeCAD.Console.PrintMessage('save to properties: ' + translate(
                'SkyDomesDialog', 'There is no Sky Domes group!') + '\n')
        FreeCAD.ActiveDocument.recompute()

    def compare_sky_domes_data(self):

        """Compares and activates the update of sky dome data."""

        #forms
        north2 = float(self.ui.lineEdit_North_angle.text())
        radius2 = float(self.ui.lineEdit_Radius.text())
        x2 = float(self.ui.lineEdit_Position_x.text())
        y2 = float(self.ui.lineEdit_Position_y.text())
        z2 = float(self.ui.lineEdit_Position_z.text())
        direct_diffuse2 = self.ui.checkBox_direct_diffuse.isChecked()
        center_vectors2 = self.ui.checkBox_center_vectors.isChecked()
        #values
        epw_path2 = self.ui.lineEdit_epw_path.text()

        date_string1 = self.ui.dateEdit_date_from.date()

        start_month2 = date_string1.month()
        start_year2 = date_string1.year()
        start_day2 = date_string1.day()

        date_string2 = self.ui.dateEdit_date_to.date()

        end_month2 = date_string2.month()
        end_year2 = date_string2.year()
        end_day2 = date_string2.day()

        start_hour2 = int(self.ui.spinBox_time_from.text())
        end_hour2 = int(self.ui.spinBox_time_to.text())
        timestep2 = self.ui.comboBox_timestep.currentText()
        leap_year2 = self.ui.checkBox_leap_year.isChecked()
        units2 = self.ui.comboBox_units.currentText()[0:2]
        color_count2 = self.ui.spinBox_color_count.value()
        color_set2 = self.ui.comboBox_color_set.currentText()[0:2]

        dif_forms = False
        dif_values = False
        from .SkyDomes import SD
        if SD is not None:
            north1 = float(SD.north)
            radius1 = float(SD.radius)
            x1 = float(SD.position.x)
            y1 = float(SD.position.y)
            z1 = float(SD.position.z)
            direct_diffuse1 = SD.direct_diffuse_domes
            try:
                SD.Group[0].Group[3]
                center_vectors1 = center_vectors2
            except Exception:
                center_vectors1 = SD.center_vectors
            if any(condition for condition in [north1 != north2,
                                               radius1 != radius2,
                                               x1 != x2,
                                               y1 != y2,
                                               z1 != z2,
                                               direct_diffuse1 != direct_diffuse2,
                                               center_vectors1 != center_vectors2
                                               ]
                ):
                dif_forms = True
            epw_path1 = SD.epw_path
            start_year1 = SD.start_year
            end_year1 = SD.end_year
            start_month1 = SD.start_month
            end_month1 = SD.end_month
            start_day1 = SD.start_day
            end_day1 = SD.end_day
            start_hour1 = SD.start_hour
            end_hour1 = SD.end_hour
            timestep1 = SD.timestep
            leap_year1 = SD.leap_year
            units1 = SD.units[0:2]
            color_count1 = SD.color_count
            color_set1 = SD.color_set[0:2]
            if any(condition for condition in [epw_path1 != epw_path2,
                                               start_year1 != start_year2,
                                               end_year1 != end_year2,
                                               start_month1 != start_month2,
                                               end_month1 != end_month2,
                                               start_day1 != start_day2,
                                               end_day1 != end_day2,
                                               start_hour1 != start_hour2,
                                               end_hour1 != end_hour2,
                                               timestep1 != timestep2,
                                               leap_year1 != leap_year2,
                                               units1 != units2,
                                               color_count1 != color_count2,
                                               color_set1 != color_set2
                                               ]
                ):
                dif_values = True
            self.save_to_propeties()
            print("send data to Sky Domes!")
            print(f"dif_forms: {dif_forms}, dif_values: {dif_values}")
            if dif_forms is True or dif_values is True:
                SkyDomes.modify_sky_domes(forms = dif_forms, values = dif_values)
                FreeCAD.Console.PrintMessage(translate("SkyDomesDialog",
                                                       "Sky Domes was updated!\n"))
        else:
            print("Compare sky domes data: Can not get data from Sky Domes!")

    def on_button_apply_clicked(self):

        """Apply button actions"""

        from .SkyDomes import SD_NEW
        if SD_NEW is True:
            self.save_to_propeties()
        else:
            self.compare_sky_domes_data()

def open_sky_domes_configuration():

    """Open Sky Domes configuration"""

    dlg = SkyDomesConfigurationDialog()
    dlg.get_properties_data()
    if dlg.show_dialog():
        from .SkyDomes import SD_NEW
        if SD_NEW is True:
            dlg.save_to_propeties()
            SkyDomes.create_sky_domes()
        else:
            dlg.compare_sky_domes_data()
    from .SkyDomes import SD, SD_NEW
    if SD_NEW is True:
        FreeCAD.ActiveDocument.removeObject(SD.Name)
