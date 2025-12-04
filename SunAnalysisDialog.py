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

"""This module implements the sun analysis configuration dialog"""

import os
import FreeCAD
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets #, QtUiTools
from PySide.QtCore import QDate #, QTime
from PySide.QtCore import QT_TRANSLATE_NOOP
import SunAnalysis as sa

SA = None

class SunAnalysisConfigurationDialog(QtWidgets.QDialog):

    """A sun analysis configuration dialog"""

    def __init__(self, parent = None):

        super().__init__(parent)

        # Load the UI
        ui_file = os.path.join(os.path.dirname(__file__), "SunAnalysis.ui")
        self.ui = Gui.PySideUic.loadUi(ui_file)

        # Run tests on FC Pynthon console
        # user_mod_path = os.path.join(FreeCAD.getUserAppDataDir(), "Mod")
        # SunAnalysisUi = FreeCADGui.PySideUic.loadUi(user_mod_path + '/Solar/SunAnalysis.ui')
        # SunAnalysisUi.show()

        self.setWindowTitle(QT_TRANSLATE_NOOP("SunAnalysisDialog", "sun analysis configuration"))
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
        # toolButton_study_objects
        self.ui.toolButton_study_objects.clicked.connect(self.open_select_study_object)
        # toolButton_study_context
        #self.ui.toolButton_study_context.clicked.connect(self.open_select_study_context)
        # pushButton create sun analysis
        self.ui.horizontalSlider_transparency.valueChanged.connect(self.value_changed)
        # pushButton_Apply
        self.ui.pushButton_Apply.clicked.connect(self.on_button_apply_clicked)
        # buttonBox_Cancel_OK
        self.ui.buttonBox_Cancel_OK.clicked.connect(self.accept)
        self.ui.buttonBox_Cancel_OK.rejected.connect(self.reject)
        # translation
        #groupBox_epw_location
        self.ui.groupBox_epw_location.setTitle(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Epw/ Location"))
        self.ui.groupBox_epw_location.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Location data get from epw file."))
        #groupBox_epw_file
        self.ui.groupBox_epw_file.setTitle(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "epw file"))
        #label_Get_epw_file
        self.ui.label_Get_epw_file.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Get epw file:"))
        self.ui.label_Get_epw_file.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Click the link to get the epw file"))
        #label_epw_map_link
        self.ui.label_epw_map_link.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Click to download the epw file"))
        #label_epw_path
        self.ui.label_epw_path.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "epw file path:"))
        self.ui.label_epw_path.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "After downloading the epw file, \n"
                        "indicate its path on your machine"))
        #lineEdit_epw_path
        self.ui.lineEdit_epw_path.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "The epw file path on your machine"))
        #toolButton_epw_path
        self.ui.toolButton_epw_path.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Indicate the path of the epw file"))
        #groupBox_location
        self.ui.groupBox_location.setTitle(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Location"))
        #label_City
        self.ui.label_City.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "City:"))
        #label_Country
        self.ui.label_Country.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Country:"))
        #label_Latitude
        self.ui.label_Latitude.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Latitude:"))
        #label_Longitude
        self.ui.label_Longitude.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Longitude:"))
        #label_Elevation
        self.ui.label_Elevation.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Elevation:"))
        #label_Time_zone
        self.ui.label_Time_zone.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Time zone:"))
        #label_North_angle
        self.ui.label_North_angle.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "North angle:"))
        self.ui.label_North_angle.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Indicate the true north.\n"
                        "Clockwise with zero in \n"
                        "the direction of the y-axis"))
        #lineEdit_North_angle
        self.ui.lineEdit_North_angle.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Indicate the true north.\n"
                        "Clockwise with zero in \n"
                        "the direction of the y-axis"))
        #label_max_length
        self.ui.label_max_length.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Max. length:"))
        #lineEdit_max_length
        self.ui.lineEdit_max_length.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Specify the maximum value for the \n"
                        "triangular sub faces (mm).\n"
                        "Warning: small values ​​can result in \n"
                        "very long calculation times."))
        #groupBox_Sun_analysis_configuration
        self.ui.groupBox_Sun_analysis_configuration.setTitle(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Sun analysis configurations"))
        #groupBox_sun_analysis_period
        self.ui.groupBox_Sun_analysis_period.setTitle(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Sun analysis period"))
        self.ui.groupBox_Sun_analysis_period.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "An analysis period between two dates of the "
                        "year and between certain hours."))
        #label_Date_from
        self.ui.label_Date_from.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Date from:"))
        #dateEdit_date_from
        self.ui.dateEdit_date_from.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Indicate the start date of the analysis period."))
        #label_date_to
        self.ui.label_date_to.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "to:"))
        #dateEdit_date_to
        self.ui.dateEdit_date_to.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Indicate the end date of the analysis period."))
        #label_Time_from
        self.ui.label_Time_from.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Time from:"))
        #spinBox_time_from
        self.ui.spinBox_time_from.setToolTip(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Indicate the start time of the analysis period."))
        #label_to
        self.ui.label_to.setText(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "to:"))
        #spinBox_time_to
        self.ui.spinBox_time_to.setToolTip(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Indicate the end time of the analysis period."))
        #label_Timestep
        self.ui.label_Timestep.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Timestep"))
        #comboBox_timestep
        self.ui.comboBox_timestep.setToolTip(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Specify how many times per hour \n"
                       "the calculation will be performed. \n"
                       "Note that larger numbers will \n"
                       "increase the computation time."))
        #checkBox_daylight_saving
        self.ui.checkBox_daylight_saving.setText(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Daylight saving"))
        self.ui.checkBox_daylight_saving.setToolTip(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Indicate whether the analysis period \n"
                       "is in daylight saving time."))
        #groupBox_Sun_analysis_results
        self.ui.groupBox_Sun_analysis_results.setTitle(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Sun analysis results"))
        #label_sky_matrix
        """self.ui.label_sky_matrix.setText(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Sky matrix:"))"""
        #comboBox_sky_matrix
        """self.ui.comboBox_sky_matrix.setItemText(0,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Tregenza"))
        self.ui.comboBox_sky_matrix.setItemText(1,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Reinhart"))
        self.ui.comboBox_sky_matrix.setToolTip(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Choose between the low-resolution model (Tregenza)\n"
                       "or high-resolution (Reinhart) one.\n"
                       "Keep in mind that the Reinhart model can take \n"
                       "considerable time to calculate its values."))"""
        #checkBox_sky_matrix_high_density
        self.ui.checkBox_sky_matrix_high_density.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Sky matrix high density."))
        self.ui.checkBox_sky_matrix_high_density.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Enable sky matrix high density (for Reinhart model) \n"
                        "or not (for Tregenza one)."))
        #label_Results
        self.ui.label_Results.setText(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Results:"))
        #comboBox_results
        self.ui.comboBox_results.setItemText(0,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Sun hours"))
        self.ui.comboBox_results.setItemText(1,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Radiation (kWh/m²)"))
        self.ui.comboBox_results.setItemText(2,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Irradiation (Wh/m²)"))
        self.ui.comboBox_results.setToolTip(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Indicate whether the sun analysis results should be plotted with \n"
                       "units of hours, total Radiation (kWh/m2) or \n"
                       "Irradiation (Wh/m2)."))
        #checkBox_direct_diffuse
        self.ui.checkBox_direct_diffuse.setText(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Direct and diffuse"))
        self.ui.checkBox_direct_diffuse.setToolTip(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Enable it to visualize the direct and diffuse domes values."))
        #checkBox_sun_vectors
        self.ui.checkBox_sun_vectors.setText(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Sun vectors"))
        self.ui.checkBox_sun_vectors.setToolTip(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Enable it to visualize the vector of sun position."))
        #label_5Transparency
        """self.ui.label_Transparency.setText(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Transparency"))
        #horizontalSlider_transparency
        self.ui.horizontalSlider_transparency.setToolTip(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Adjust the transparency of the sun analysis."))"""
        #groupBox_Legend
        self.ui.groupBox_Legend.setTitle(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Legend"))
        #label_Position
        self.ui.label_leg_position.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Custom position"))
        self.ui.label_leg_position.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Adjust the legend position (bottom left corner) \n"
                        "according to the project."))
        #lineEdit_Position_x
        self.ui.lineEdit_position_x.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Adjust the x legend position (bottom left corner) \n"
                        "according to the project (mm)."))
        #lineEdit_Position_y
        self.ui.lineEdit_position_y.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Adjust the y legend position (bottom left corner) \n"
                        "according to the project (mm)."))
        #lineEdit_Position_z
        self.ui.lineEdit_position_z.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Adjust the z legend position (bottom left corner) \n"
                        "according to the project (mm)."))
        #label_leg_width
        self.ui.label_leg_width.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Width"))
        self.ui.label_leg_width.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Indicate the legend with (mm)."))
        #label_color_count
        self.ui.label_color_count.setText(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Color count"))
        self.ui.label_color_count.setToolTip(
                        QT_TRANSLATE_NOOP("SunAnalysisDialog",
                        "Indicate the legend number of colors \n"
                        "(default: 11)."))
        #label_color_set
        self.ui.label_color_set.setText(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Color_set:"))
        #comboBox_color_set
        self.ui.comboBox_color_set.setItemText(0,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "00 - Original Ladybug"))
        self.ui.comboBox_color_set.setItemText(1,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "01 - Nuanced Ladybug"))
        self.ui.comboBox_color_set.setItemText(2,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "02 - Multi-colored Ladybug"))
        self.ui.comboBox_color_set.setItemText(3,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "03 - Ecotect"))
        self.ui.comboBox_color_set.setItemText(4,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "04 - View Study"))
        self.ui.comboBox_color_set.setItemText(5,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "05 - Shadow Study"))
        self.ui.comboBox_color_set.setItemText(6,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "06 - Glare Study"))
        self.ui.comboBox_color_set.setItemText(7,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "07 - Annual Comfort"))
        self.ui.comboBox_color_set.setItemText(8,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "08 - Thermal Comfort"))
        self.ui.comboBox_color_set.setItemText(9,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "09 - Peak Load Balance"))
        self.ui.comboBox_color_set.setItemText(10,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "10 - Heat Sensation"))
        self.ui.comboBox_color_set.setItemText(11,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "11 - Cold Sensation"))
        self.ui.comboBox_color_set.setItemText(12,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "12 - Benefit/Harm"))
        self.ui.comboBox_color_set.setItemText(13,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "13 - Harm"))
        self.ui.comboBox_color_set.setItemText(14,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "14 - Benefit"))
        self.ui.comboBox_color_set.setItemText(15,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "15 - Shade Benefit/Harm"))
        self.ui.comboBox_color_set.setItemText(16,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "16 - Shade Harm"))
        self.ui.comboBox_color_set.setItemText(17,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "17 - Shade Benefit"))
        self.ui.comboBox_color_set.setItemText(18,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "18 - Energy Balance"))
        self.ui.comboBox_color_set.setItemText(19,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "19 - Energy Balance w/ Storage"))
        self.ui.comboBox_color_set.setItemText(20,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "20 - THERM"))
        self.ui.comboBox_color_set.setItemText(21,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "21 - Cloud Cover"))
        self.ui.comboBox_color_set.setItemText(22,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "22 - Black to White"))
        self.ui.comboBox_color_set.setItemText(23,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "23 - Blue, Green, Red"))
        self.ui.comboBox_color_set.setItemText(24,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "24 - Multicolored 2"))
        self.ui.comboBox_color_set.setItemText(25,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "25 - Multicolored 3"))
        self.ui.comboBox_color_set.setItemText(26,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "26 - OpenStudio Palette"))
        self.ui.comboBox_color_set.setItemText(27,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "27 - Cividis (colorblind friendly)"))
        self.ui.comboBox_color_set.setItemText(28,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "28 - Viridis (colorblind friendly)"))
        self.ui.comboBox_color_set.setItemText(29,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "29 - Parula (colorblind friendly)"))
        self.ui.comboBox_color_set.setItemText(30,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "30 - Energy Balance by Face Type"))
        self.ui.comboBox_color_set.setItemText(31,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "31 - Peak Cooling by Face Type"))
        self.ui.comboBox_color_set.setItemText(32,
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "32 - Peak Hating by Face Type"))
        self.ui.comboBox_color_set.setToolTip(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
                       "Choose the legend color set."))
        #pushButton_Apply
        self.ui.pushButton_Apply.setText(
                       QT_TRANSLATE_NOOP("SunAnalysisDialog",
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
            QT_TRANSLATE_NOOP("SunAnalysisDialog", "Select epw file"),
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
                self, QT_TRANSLATE_NOOP("SunAnalysisDialog", "Warning"),
                QT_TRANSLATE_NOOP("SunAnalysisDialog",
                "Indicate a epw file before "
                "close the dialog sun analysis!")
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

    def open_select_study_object(self):
        pass
        #SA.study_objs. =


    def value_changed(self):
        value = str(self.ui.horizontalSlider_transparency.value())
        self.ui.label_transp_value.setText(value)

    # Connection dialog x sun analysis properties
    def get_properties_data(self):

        """Get data from sun analysis properties and send them to dialog"""

        from SunAnalysis import SA, SA_NEW
        if SA is not None:
            # epw file
            if SA_NEW is True:
                try:
                    obj1 = FreeCAD.ActiveDocument.SunProperties
                    # epw file
                    if obj1.epw_path != "":
                        self.ui.lineEdit_epw_path.setText(obj1.epw_path)
                        print("epw path get from sun properties")
                    else:
                        self.ui.lineEdit_epw_path.setText(SA.epw_path)
                        print("epw path get from SA")
                    # North
                    self.ui.lineEdit_North_angle.setText((str(float(obj1.North))))
                except:
                    pass
            else:
                # epw file
                self.ui.lineEdit_epw_path.setText(SA.epw_path)
                print("epw path get from SA")
                # North
                self.ui.lineEdit_North_angle.setText((str(float(SA.north))))
            self.autofill_from_epw()
            # Max length
            self.ui.lineEdit_max_length.setText(str(SA.max_length))
            # Sun analysis period
            self.ui.dateEdit_date_from.setDate(QDate(SA.start_year, SA.start_month, SA.start_day))
            self.ui.dateEdit_date_to.setDate(QDate(SA.end_year, SA.end_month, SA.end_day))
            self.ui.spinBox_time_from.setValue(SA.start_hour)
            self.ui.spinBox_time_to.setValue(SA.end_hour)
            idx = self.ui.comboBox_timestep.findText(SA.timestep)
            if idx >= 0:
                self.ui.comboBox_timestep.setCurrentIndex(idx)
            self.ui.checkBox_daylight_saving.setChecked(SA.daylight_saving)
            # Sun analysis results
            idx2 = self.ui.comboBox_results.findText(SA.results)
            if idx2 >= 0:
                self.ui.comboBox_results.setCurrentIndex(idx2)
            # Sun sky matrix
            """idx4 = self.ui.comboBox_sky_matrix.findText(SA.sky_matrix_model)
            if idx4 >= 0:
                self.ui.comboBox_sky_matrix.setCurrentIndex(idx4)
            self.ui.checkBox_direct_diffuse.setChecked(SA.direct_diffuse_values)
            self.ui.checkBox_sun_vectors.setChecked(SA.sun_vectors)"""
            #checkBox_sky_matrix_high_density
            self.ui.checkBox_sky_matrix_high_density.setChecked(SA.sky_matrix_high_density)
            # Transparency
            """self.ui.label_transp_value.setText(str(SA.transparency))
            self.ui.horizontalSlider_transparency.setValue(SA.transparency)"""
            # Legend
            self.ui.lineEdit_position_x.setText(str(SA.leg_position.x))
            self.ui.lineEdit_position_y.setText(str(SA.leg_position.y))
            self.ui.lineEdit_position_z.setText(str(SA.leg_position.z))
            self.ui.lineEdit_leg_width.setText(str(SA.leg_width))
            self.ui.spinBox_color_count.setValue(SA.color_count)
            idx3 = self.ui.comboBox_color_set.findText(SA.color_set)
            if idx3 >= 0:
                self.ui.comboBox_color_set.setCurrentIndex(idx3)
        else:
            FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP(
                'SunAnalysisDialog', 'Get properties: There is no SunAnalysis group!') + '\n')

    def save_to_propeties(self):

        """Save data from dialog to sun analysis properties"""

        from SunAnalysis import SA, SA_NEW
        if SA is not None:

            # epw file

            epw_path = self.ui.lineEdit_epw_path.text()
            SA.epw_path = epw_path
            # Location
            SA.city = self.ui.label_city_value.text()
            # North angle
            SA.north  = float(self.ui.lineEdit_North_angle.text())
            # Max length
            SA.max_length = float(self.ui.lineEdit_max_length.text())
            # Sun analysis period
            date_string1 = self.ui.dateEdit_date_from.text()
            SA.start_day = int(date_string1[0:2])
            SA.start_month = int(date_string1[3:5])
            SA.start_year = int(date_string1[6:10])
            date_string2 = self.ui.dateEdit_date_to.text()
            SA.end_day = int(date_string2[0:2])
            SA.end_month = int(date_string2[3:5])
            SA.end_year = int(date_string2[6:10])
            SA.start_hour = self.ui.spinBox_time_from.value()
            SA.end_hour = self.ui.spinBox_time_to.value()
            SA.timestep = self.ui.comboBox_timestep.currentText()
            SA.daylight_saving = self.ui.checkBox_daylight_saving.isChecked()
            # Sun analysis results
            #SA.sky_matrix_model = self.ui.comboBox_sky_matrix.currentText()
            SA.sky_matrix_high_density = self.ui.checkBox_sky_matrix_high_density.isChecked()
            SA.results = self.ui.comboBox_results.currentText()
            SA.direct_diffuse_values = self.ui.checkBox_direct_diffuse.isChecked()
            SA.sun_vectors = self.ui.checkBox_sun_vectors.isChecked()
            #if SA_NEW is False:
                #SA.Group[1].Visibility = SA.direct_diffuse_values
                #SA.Group[2].Visibility = SA.direct_diffuse_values
            #SA.transparency = self.ui.horizontalSlider_transparency.value()
            # Legend
            SA.leg_position.x = self.ui.lineEdit_position_x.text()
            SA.leg_position.y = self.ui.lineEdit_position_y.text()
            SA.leg_position.z = self.ui.lineEdit_position_z.text()
            SA.leg_width = float(self.ui.lineEdit_leg_width.text())
            SA.color_count = self.ui.spinBox_color_count.value()
            SA.color_set = self.ui.comboBox_color_set.currentText()
        else:
            FreeCAD.Console.PrintMessage(QT_TRANSLATE_NOOP(
                'SunAnalysisDialog', 'Save properties: There is no SunAnalysis group!') + '\n')
        FreeCAD.ActiveDocument.recompute()

    def compare_sun_analysis_data(self):

        """Compares and activates the update of sun analysis data."""

        #Only values
        epw_path2 = self.ui.lineEdit_epw_path.text()
        north2 = float(self.ui.lineEdit_North_angle.text())
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
        daylight_saving2 = self.ui.checkBox_daylight_saving.isChecked()
        results2 = self.ui.comboBox_results.currentText()
        sky_matrix_high_density2 = self.ui.checkBox_sky_matrix_high_density.isChecked()
        color_set2 = self.ui.comboBox_color_set.currentText()

        #Only form
        sun_vectors2 = self.ui.checkBox_sun_vectors.isChecked()
        #Values and form
        direct_diffuse2 = self.ui.checkBox_direct_diffuse.isChecked()
        color_count2 = self.ui.spinBox_color_count.value()

        #Only legend
        x2 = float(self.ui.lineEdit_position_x.text())
        y2 = float(self.ui.lineEdit_position_y.text())
        z2 = float(self.ui.lineEdit_position_z.text())
        leg_width2 = float(self.ui.lineEdit_leg_width.text())

        dif_values = False
        dif_forms = False
        dif_leg = False
        from SunAnalysis import SA
        if SA is not None:
            #values
            epw_path1 = SA.epw_path
            north1 = float(SA.north)
            start_year1 = SA.start_year
            end_year1 = SA.end_year
            start_month1 = SA.start_month
            end_month1 = SA.end_month
            start_day1 = SA.start_day
            end_day1 = SA.end_day
            start_hour1 = SA.start_hour
            end_hour1 = SA.end_hour
            timestep1 = SA.timestep
            daylight_saving1 = SA.daylight_saving
            results1 = SA.results
            sky_matrix_high_density1 = SA.sky_matrix_high_density
            color_set1 = SA.color_set
            print(f"{epw_path1} != {epw_path2} or \n"
                  f"{north1} != {north2} or \n"
                  f"{start_year1} != {start_year2} or \n"
                  f"{end_year1} != {end_year2} or \n "
                  f"{start_month1} != {start_month2} or \n"
                  f"{end_month1} != {end_month2} or \n"
                  f"{start_day1} != {start_day2} or \n"
                  f"{end_day1} != {end_day2} or \n"
                  f"{start_hour1} != {start_hour2} or \n"
                  f"{end_hour1} ! = {end_hour2} or \n"
                  f"{timestep1} != {timestep2} or \n"
                  f"{daylight_saving1} != {daylight_saving2} or \n"
                  f"{results1} != {results2} or \n"
                  f"{sky_matrix_high_density1} != {sky_matrix_high_density2} or \n"
                  f"{color_set1} != {color_set2}"
                  )
            if any(condition for condition in [epw_path1 != epw_path2,
                                               north1 != north2,
                                               start_year1 != start_year2,
                                               end_year1 != end_year2,
                                               start_month1 != start_month2,
                                               end_month1 != end_month2,
                                               start_day1 != start_day2,
                                               end_day1 != end_day2,
                                               start_hour1 != start_hour2,
                                               end_hour1 != end_hour2,
                                               timestep1 != timestep2,
                                               daylight_saving1 != daylight_saving2,
                                               results1 != results2,
                                               sky_matrix_high_density1 != sky_matrix_high_density2,
                                               color_set1 != color_set2,
                                               color_set1 != color_set2
                                               ]
                ):
                dif_values = True
                print(f"found difference for values: {dif_values}")
            else:
                print(f"dif_values: {dif_values}")
            #only form
            sun_vectors1 = SA.sun_vectors
            print(f"{sun_vectors1} != {sun_vectors2}")
            if any(condition for condition in [sun_vectors1 != sun_vectors2]
                                               ):
                dif_forms = True
                print(f"found difference for forms: {dif_forms}")
            else:
                print(f"dif_forms: {dif_forms}")
            #Values and form
            direct_diffuse1 = SA.direct_diffuse_values
            color_count1 = SA.color_count
            print(f"{direct_diffuse1} != {direct_diffuse2} or \n"
                  f"{color_count1} != {color_count2} or \n"
                  )
            if any(condition for condition in [direct_diffuse1 != direct_diffuse2,
                                               sun_vectors1 != sun_vectors2]
                                               ):
                dif_forms = True
                dif_values = True
                dif_leg = True
                print(f"found difference for forms, values and leg: {dif_forms}, {dif_values}, {dif_leg}")
            else:
                print(f"dif_forms: {dif_forms}, {dif_values}, {dif_leg}")
            #Only legend
            x1 = float(SA.leg_position.x)
            y1 = float(SA.leg_position.y)
            z1 = float(SA.leg_position.z)
            leg_width1 = float(SA.leg_width)

            print(f"{x1} ! = {x2} or \n"
                  f"{y1} != {y2} or \n"
                  f"{z1} != {z2} or \n"
                  f"{leg_width1} != {leg_width2} or \n"
                  )
            if any(condition for condition in [x1 != x2,
                                               y1 != y2,
                                               z1 != z2,
                                               leg_width1 != leg_width2]
                                               ):
                dif_leg = True
                print(f"found difference for forms: {dif_leg}")
            else:
                print(f"dif_forms: {dif_leg}")
            self.save_to_propeties()
            print("send data to sun analysis!")
            print(f"dif_forms: {dif_forms}, dif_values: {dif_values}, dif_leg: {dif_leg}")
            if dif_forms is True or dif_values is True or dif_leg is True:
                print("try to update sun analysis data!")
                sa.modify_sun_analysis(forms = dif_forms, values = dif_values, leg = dif_leg)
                print("updated sun analysis data!")
        else:
            print ("Compare sun analysis data: Can not get data from sun analysis!")

    def on_button_apply_clicked(self):

        """Apply button actions"""

        from SunAnalysis import SA_NEW
        if SA_NEW is True:
            self.save_to_propeties()
        else:
            self.compare_sun_analysis_data()

def open_sun_analysis_configuration():

    """Open sun analysis configuration"""

    dlg = SunAnalysisConfigurationDialog()
    dlg.get_properties_data()
    if dlg.show_dialog():
        from SunAnalysis import SA_NEW
        if SA_NEW is True:
            dlg.save_to_propeties()
            #sa.create_sun_analysis()
        else:
            dlg.compare_sun_analysis_data()
            sa.create_sun_analysis()
    from SunAnalysis import SA, SA_NEW
    if SA_NEW is True:
        FreeCAD.ActiveDocument.removeObject(SA.Name)
