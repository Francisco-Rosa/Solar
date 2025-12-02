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

"""This module implements the sky domes configuration dialog"""

import os
import FreeCAD
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets
from PySide.QtCore import QDate
from PySide.QtCore import QT_TRANSLATE_NOOP
import SkyDomes as sd

SD = None

class SkyDomesConfigurationDialog(QtWidgets.QDialog):

    """A sky domes configuration dialog"""

    def __init__(self, parent = None):

        super().__init__(parent)

        # Load the UI
        ui_file = os.path.join(os.path.dirname(__file__), "SkyDomes.ui")
        self.ui = Gui.PySideUic.loadUi(ui_file)

        # Run tests on FC Pynthon console
        # user_mod_path = os.path.join(FreeCAD.getUserAppDataDir(), "Mod")
        # SkyDomesUi = FreeCADGui.PySideUic.loadUi(user_mod_path + '/Solar/SkyDomes.ui')
        # SkyDomesUi.show()

        # Correctly embed the loaded UI as a child widget
        self.setWindowTitle(QT_TRANSLATE_NOOP("SkyDomesDialog", "Sky domes configuration"))
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
        # pushButton create sky domes
        self.ui.horizontalSlider_transparency.valueChanged.connect(self.value_changed)
        # pushButton_Apply
        self.ui.pushButton_Apply.clicked.connect(self.on_button_apply_clicked)
        # buttonBox_Cancel_OK
        self.ui.buttonBox_Cancel_OK.clicked.connect(self.accept)
        self.ui.buttonBox_Cancel_OK.rejected.connect(self.reject)
        # translation
        #groupBox_epw_location
        self.ui.groupBox_epw_location.setTitle(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Epw/ Location"))
        self.ui.groupBox_epw_location.setToolTip(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Location data get from epw file."))
        #groupBox_epw_file
        self.ui.groupBox_epw_file.setTitle(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "epw file"))
        #label_Get_epw_file
        self.ui.label_Get_epw_file.setText(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Get epw file:"))
        self.ui.label_Get_epw_file.setToolTip(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Click the link to get the epw file"))
        #label_epw_map_link
        self.ui.label_epw_map_link.setToolTip(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Click to download the epw file"))
        #label_epw_path
        self.ui.label_epw_path.setText(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "epw file path:"))
        self.ui.label_epw_path.setToolTip(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "After downloading the epw file, \n"
                        "indicate its path on your machine"))
        #lineEdit_epw_path
        self.ui.lineEdit_epw_path.setToolTip(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "The epw file path on your machine"))
        #toolButton_epw_path
        self.ui.toolButton_epw_path.setToolTip(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Indicate the path of the epw file"))
        #groupBox_location
        self.ui.groupBox_location.setTitle(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Location"))
        #label_City
        self.ui.label_City.setText(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "City:"))
        #label_Country
        self.ui.label_Country.setText(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Country:"))
        #label_Latitude
        self.ui.label_Latitude.setText(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Latitude:"))
        #label_Longitude
        self.ui.label_Longitude.setText(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Longitude:"))
        #label_Elevation
        self.ui.label_Elevation.setText(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Elevation:"))
        #label_Time_zone
        self.ui.label_Time_zone.setText(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Time zone:"))
        #label_North_angle
        self.ui.label_North_angle.setText(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "North angle:"))
        #lineEdit_North_angle
        self.ui.lineEdit_North_angle.setToolTip(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Indicate the true north.\n"
                        "Clockwise with zero in \n"
                        "the direction of the y-axis"))
        #groupBox_sky_domes_configuration
        self.ui.groupBox_sky_domes_configuration.setTitle(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Sky domes configurations"))
        #label_radius
        self.ui.label_radius.setText(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Radius:"))
        #lineEdit_Radius
        self.ui.lineEdit_Radius.setToolTip(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Set the radius of the sky dome (mm)."))
        #lineEdit_Position_x
        self.ui.lineEdit_Position_x.setToolTip(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Adjust the x position of the center of the \n"
                        "dome according to the project (mm)."))
        #lineEdit_Position_y
        self.ui.lineEdit_Position_y.setToolTip(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Adjust the y position of the center of the \n"
                        "dome according to the project (mm)."))
        #lineEdit_Position_z
        self.ui.lineEdit_Position_z.setToolTip(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Adjust the z position of the center of the \n"
                        "dome according to the project (mm)."))
        #groupBox_analysis_period
        self.ui.groupBox_analysis_period.setTitle(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Analysis period"))
        self.ui.groupBox_analysis_period.setToolTip(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "An analysis period between two dates of the "
                        "year and between certain hours."))
        #label_Date_from
        self.ui.label_Date_from.setText(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Date from:"))
        #dateEdit_date_from
        self.ui.dateEdit_date_from.setToolTip(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Indicate the start date of the analysis period."))
        #label_date_to
        self.ui.label_date_to.setText(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "to:"))
        #dateEdit_date_to
        self.ui.dateEdit_date_to.setToolTip(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Indicate the end date of the analysis period."))
        #label_Time_from
        self.ui.label_Time_from.setText(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Time from:"))
        #spinBox_time_from
        self.ui.spinBox_time_from.setToolTip(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Indicate the start time of the analysis period."))
        #label_to
        self.ui.label_to.setText(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "to:"))
        #spinBox_time_to
        self.ui.spinBox_time_to.setToolTip(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Indicate the end time of the analysis period."))
        #label_Timestep
        self.ui.label_Timestep.setText(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Timestep"))
        #comboBox_timestep
        self.ui.comboBox_timestep.setToolTip(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Specify how many times per hour \n"
                       "the calculation will be performed. \n"
                       "Note that larger numbers will \n"
                       "increase the computation time."))
        #checkBox_leap_year
        self.ui.checkBox_leap_year.setText(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "leap year"))
        self.ui.checkBox_leap_year.setToolTip(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Indicate whether the Analysis\n"
                       "Period represents a leap year."))
        #groupBox_sky_domes
        self.ui.groupBox_sky_domes.setTitle(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Sky domes"))
        #label_model
        self.ui.label_model.setText(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Model:"))
        #comboBox_model
        self.ui.comboBox_model.setItemText(0,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Tregenza"))
        self.ui.comboBox_model.setItemText(1,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Reinhart"))
        self.ui.comboBox_model.setToolTip(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Choose between the low-resolution model (Tregenza)\n"
                       "or high-resolution (Reinhart) one.\n"
                       "Keep in mind that the Reinhart model can take \n"
                       "considerable time to calculate its values."))
        #label_Units
        self.ui.label_Units.setText(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Units:"))
        #comboBox_units
        self.ui.comboBox_units.setItemText(0,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Radiation (kWh/m²)"))
        self.ui.comboBox_units.setItemText(1,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Irradiance (W/m²)"))
        self.ui.comboBox_units.setToolTip(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Indicate whether the sky dome should be plotted with \n"
                       "units of total Radiation (kWh/m²) or \n"
                       "average Irradiance (W/m²)."))
        #checkBox_direct_diffuse
        self.ui.checkBox_direct_diffuse.setText(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Direct and diffuse"))
        self.ui.checkBox_direct_diffuse.setToolTip(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Enable it to visualize the direct and diffuse domes values."))
        #checkBox_center_vectors
        self.ui.checkBox_center_vectors.setText(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Center vectors"))
        self.ui.checkBox_center_vectors.setToolTip(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Enable it to visualize the center vector of each dome patch."))
        #label_5Transparency
        self.ui.label_5Transparency.setText(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Transparency"))
        #horizontalSlider_transparency
        self.ui.horizontalSlider_transparency.setToolTip(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Adjust the transparency of the sky domes."))
        #groupBox_Legend
        self.ui.groupBox_Legend.setTitle(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Legend"))
        #label_color_count
        self.ui.label_color_count.setText(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Color count"))
        self.ui.label_color_count.setToolTip(
                        QT_TRANSLATE_NOOP("SkyDomesDialog",
                        "Indicate the legend number of colors \n"
                        "(default: 11)."))
        #label_color_set
        self.ui.label_color_set.setText(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Color_set:"))
        #comboBox_color_set
        self.ui.comboBox_color_set.setItemText(0,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "00 - Original Ladybug"))
        self.ui.comboBox_color_set.setItemText(1,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "01 - Nuanced Ladybug"))
        self.ui.comboBox_color_set.setItemText(2,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "02 - Multi-colored Ladybug"))
        self.ui.comboBox_color_set.setItemText(3,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "03 - Ecotect"))
        self.ui.comboBox_color_set.setItemText(4,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "04 - View Study"))
        self.ui.comboBox_color_set.setItemText(5,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "05 - Shadow Study"))
        self.ui.comboBox_color_set.setItemText(6,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "06 - Glare Study"))
        self.ui.comboBox_color_set.setItemText(7,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "07 - Annual Comfort"))
        self.ui.comboBox_color_set.setItemText(8,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "08 - Thermal Comfort"))
        self.ui.comboBox_color_set.setItemText(9,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "09 - Peak Load Balance"))
        self.ui.comboBox_color_set.setItemText(10,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "10 - Heat Sensation"))
        self.ui.comboBox_color_set.setItemText(11,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "11 - Cold Sensation"))
        self.ui.comboBox_color_set.setItemText(12,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "12 - Benefit/Harm"))
        self.ui.comboBox_color_set.setItemText(13,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "13 - Harm"))
        self.ui.comboBox_color_set.setItemText(14,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "14 - Benefit"))
        self.ui.comboBox_color_set.setItemText(15,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "15 - Shade Benefit/Harm"))
        self.ui.comboBox_color_set.setItemText(16,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "16 - Shade Harm"))
        self.ui.comboBox_color_set.setItemText(17,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "17 - Shade Benefit"))
        self.ui.comboBox_color_set.setItemText(18,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "18 - Energy Balance"))
        self.ui.comboBox_color_set.setItemText(19,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "19 - Energy Balance w/ Storage"))
        self.ui.comboBox_color_set.setItemText(20,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "20 - THERM"))
        self.ui.comboBox_color_set.setItemText(21,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "21 - Cloud Cover"))
        self.ui.comboBox_color_set.setItemText(22,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "22 - Black to White"))
        self.ui.comboBox_color_set.setItemText(23,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "23 - Blue, Green, Red"))
        self.ui.comboBox_color_set.setItemText(24,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "24 - Multicolored 2"))
        self.ui.comboBox_color_set.setItemText(25,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "25 - Multicolored 3"))
        self.ui.comboBox_color_set.setItemText(26,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "26 - OpenStudio Palette"))
        self.ui.comboBox_color_set.setItemText(27,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "27 - Cividis (colorblind friendly)"))
        self.ui.comboBox_color_set.setItemText(28,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "28 - Viridis (colorblind friendly)"))
        self.ui.comboBox_color_set.setItemText(29,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "29 - Parula (colorblind friendly)"))
        self.ui.comboBox_color_set.setItemText(30,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "30 - Energy Balance by Face Type"))
        self.ui.comboBox_color_set.setItemText(31,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "31 - Peak Cooling by Face Type"))
        self.ui.comboBox_color_set.setItemText(32,
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "32 - Peak Hating by Face Type"))
        self.ui.comboBox_color_set.setToolTip(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Choose the legend color set."))
        #pushButton_Apply
        self.ui.pushButton_Apply.setText(
                       QT_TRANSLATE_NOOP("SkyDomesDialog",
                       "Apply"))

    def QT_TRANSLATE_NOOP(self, text):
        return text

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
            parent,  # parent window
            QT_TRANSLATE_NOOP("SkyDomesDialog", "Select epw file"),
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
                self, QT_TRANSLATE_NOOP("SkyDomesDialog", "Warning"),
                QT_TRANSLATE_NOOP("SkyDomesDialog",
                                  "Indicate a epw file before "
                                  "close the dialog sky domes!")
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

    def value_changed(self):
        value = str(self.ui.horizontalSlider_transparency.value())
        self.ui.label_transp_value.setText(value)

    # Connection dialog x sky domes properties
    def get_properties_data(self):

        """Get data from sky domes properties and send then to dialog"""

        from SkyDomes import SD, SD_NEW
        if SD is not None:
            # epw file
            if SD_NEW is True:
                try:
                    obj1 = FreeCAD.ActiveDocument.SunProperties
                    # epw file
                    if obj1.epw_path != "":
                        self.ui.lineEdit_epw_path.setText(obj1.epw_path)
                        print("epw path get from sun properties")
                    else:
                        self.ui.lineEdit_epw_path.setText(SD.epw_path)
                        print("epw path get from SD")
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
                print("epw path get from SD")
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
            FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP(
                'SkyDomesDialog', 'Get properties: There is no SkyDomes group!') + '\n')

    def save_to_propeties(self):

        """Save data from dialog to sky domes properties"""

        from SkyDomes import SD, SD_NEW
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
            date_string1 = self.ui.dateEdit_date_from.text()
            SD.start_day = int(date_string1[0:2])
            SD.start_month = int(date_string1[3:5])
            SD.start_year = int(date_string1[6:10])
            date_string2 = self.ui.dateEdit_date_to.text()
            SD.end_day = int(date_string2[0:2])
            SD.end_month = int(date_string2[3:5])
            SD.end_year = int(date_string2[6:10])
            SD.start_hour = self.ui.spinBox_time_from.value()
            SD.end_hour = self.ui.spinBox_time_to.value()
            # Sky domes
            SD.timestep = self.ui.comboBox_timestep.currentText()
            SD.leap_year = self.ui.checkBox_leap_year.isChecked()
            SD.model = self.ui.comboBox_model.currentText()
            SD.units = self.ui.comboBox_units.currentText()
            SD.direct_diffuse_domes = self.ui.checkBox_direct_diffuse.isChecked()
            SD.center_vectors = self.ui.checkBox_center_vectors.isChecked()
            if SD_NEW is False:
                SD.Group[1].Visibility = SD.direct_diffuse_domes
                SD.Group[2].Visibility = SD.direct_diffuse_domes
            SD.transparency = self.ui.horizontalSlider_transparency.value()
            # Legend
            SD.leg_title = self.ui.comboBox_units.currentText()
            SD.color_count = self.ui.spinBox_color_count.value()
            SD.color_set = self.ui.comboBox_color_set.currentText()
        else:
            FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP(
                'SkyDomesDialog', 'Save properties: There is no SkyDomes group!') + '\n')
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
        transparency2 = self.ui.horizontalSlider_transparency.value()
        #values
        epw_path2 = self.ui.lineEdit_epw_path.text()
        date_string1 = self.ui.dateEdit_date_from.text()
        start_day2 = int(date_string1[0:2])
        start_month2 = int(date_string1[3:5])
        start_year2 = int(date_string1[6:10])
        date_string2 = self.ui.dateEdit_date_to.text()
        end_day2 = int(date_string2[0:2])
        end_month2 = int(date_string2[3:5])
        end_year2 = int(date_string2[6:10])
        start_hour2 = int(self.ui.spinBox_time_from.text())
        end_hour2 = int(self.ui.spinBox_time_to.text())
        timestep2 = self.ui.comboBox_timestep.currentText()
        leap_year2 = self.ui.checkBox_leap_year.isChecked()
        units2 = self.ui.comboBox_units.currentText()
        color_count2 = self.ui.spinBox_color_count.value()
        color_set2 = self.ui.comboBox_color_set.currentText()

        dif_forms = False
        dif_values = False
        from SkyDomes import SD
        if SD is not None:
            north1 = float(SD.north)
            radius1 = float(SD.radius)
            x1 = float(SD.position.x)
            y1 = float(SD.position.y)
            z1 = float(SD.position.z)
            direct_diffuse1 = SD.direct_diffuse_domes
            center_vectors1 = SD.center_vectors
            transparency1 = SD.transparency
            if any(condition for condition in [north1 != north2,
                                               radius1 != radius2,
                                               x1 != x2,
                                               y1 != y2,
                                               z1 != z2,
                                               direct_diffuse1 != direct_diffuse2,
                                               transparency1 != transparency2,
                                               center_vectors1 != center_vectors2]
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
            units1 = SD.units
            color_count1 = SD.color_count
            color_set1 = SD.color_set
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
            print("send data to sky domes!")
            print(f"dif_forms: {dif_forms}, dif_values: {dif_values}")
            if dif_forms is True or dif_values is True:
                sd.modify_sky_domes(forms = dif_forms, values = dif_values)
                print("updated sky domes data!")
        else:
            print ("Compare sky domes data: Can not get data from sky domes!")

    def on_button_apply_clicked(self):

        """Apply button actions"""

        from SkyDomes import SD_NEW
        if SD_NEW is True:
            self.save_to_propeties()
        else:
            self.compare_sky_domes_data()

def open_sky_domes_configuration():

    """Open sky domes configuration"""

    dlg = SkyDomesConfigurationDialog()
    dlg.get_properties_data()
    if dlg.show_dialog():
        from SkyDomes import SD_NEW
        if SD_NEW is True:
            dlg.save_to_propeties()
            sd.create_sky_domes()
        else:
            dlg.compare_sky_domes_data()
    from SkyDomes import SD, SD_NEW
    if SD_NEW is True:
        FreeCAD.ActiveDocument.removeObject(SD.Name)
