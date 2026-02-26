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

"""This module implements the Sun Analysis configuration dialog"""

import os
import FreeCAD
import FreeCADGui as Gui
from PySide import QtCore, QtWidgets #, QtUiTools
from PySide.QtCore import QDate #, QTime

import freecad.Solar.SunAnalysis as SunAnalysis

translate = FreeCAD.Qt.translate

LanguagePath = os.path.dirname(__file__) + '/translations'
Gui.addLanguagePath(LanguagePath)

SA = None
NEW_GEOM = False

class SunAnalysisConfigurationDialog(QtWidgets.QDialog):

    """A Sun Analysis configuration dialog"""

    def __init__(self, parent = None):

        super().__init__(parent)

        # Load the UI
        ui_file = os.path.join(os.path.dirname(__file__), "SunAnalysis.ui")
        self.ui = Gui.PySideUic.loadUi(ui_file)

        # Run tests on FC Pynthon console
        # user_mod_path = os.path.join(FreeCAD.getUserAppDataDir(), "Mod")
        # SunAnalysisUi = FreeCADGui.PySideUic.loadUi(
                                  #user_mod_path + '/Solar/freecad/Solar/SunAnalysis.ui')
        # SunAnalysisUi.show()

        self.setWindowTitle(translate("SunAnalysisDialog", "Sun Analysis configuration"))
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.ui)
        self.resize(self.ui.size())

        # Connect signals/slots
        # toolButton_epw_path
        self.ui.toolButton_epw_path.clicked.connect(self.open_epw_file_dialog)
        # Make label_epw_map_link clickable:
        self.ui.label_epw_map_link.setText(
            '<a href="https://www.ladybug.tools/epwmap/"'
            '>www.ladybug.tools/epwmap</a>'
        )
        self.ui.label_epw_map_link.setOpenExternalLinks(True)
        self.ui.label_epw_map_link.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        # toolButton_study_objects
        self.ui.toolButton_study_objects.clicked.connect(self.open_select_study_objects)
        # toolButton_study_context
        self.ui.toolButton_study_context.clicked.connect(self.open_select_context_objects)
        #comboBox_results
        self.ui.comboBox_results.activated.connect(self.results_toggled)
        #checkBox_direct_diffuse
        self.ui.checkBox_direct_diffuse.clicked.connect(self.direct_diffuse_toggled)
        # pushButton_Apply
        self.ui.pushButton_Apply.clicked.connect(self.on_button_apply_clicked)
        # buttonBox_Cancel_OK
        self.ui.buttonBox_Cancel_OK.clicked.connect(self.accept)
        self.ui.buttonBox_Cancel_OK.rejected.connect(self.reject)
        # translation
        #groupBox_epw_location
        self.ui.groupBox_epw_location.setTitle(
                        translate("SunAnalysisDialog",
                        "Epw/ Location/ Legend"))
        self.ui.groupBox_epw_location.setToolTip(
                        translate("SunAnalysisDialog",
                        "Location data get from epw file."))
        #groupBox_epw_file
        self.ui.groupBox_epw_file.setTitle(
                        translate("SunAnalysisDialog",
                        "epw file"))
        #label_Get_epw_file
        self.ui.label_Get_epw_file.setText(
                        translate("SunAnalysisDialog",
                        "Get epw file:"))
        self.ui.label_Get_epw_file.setToolTip(
                        translate("SunAnalysisDialog",
                        "Click the link to get the epw file"))
        #label_epw_map_link
        self.ui.label_epw_map_link.setToolTip(
                        translate("SunAnalysisDialog",
                        "Click to download the epw file"))
        #label_epw_path
        self.ui.label_epw_path.setText(
                        translate("SunAnalysisDialog",
                        "epw file path:"))
        self.ui.label_epw_path.setToolTip(
                        translate("SunAnalysisDialog",
                        "After downloading the epw file, \n"
                        "indicate the path on your machine"))
        #lineEdit_epw_path
        self.ui.lineEdit_epw_path.setToolTip(
                        translate("SunAnalysisDialog",
                        "The epw file path on your machine"))
        #toolButton_epw_path
        self.ui.toolButton_epw_path.setToolTip(
                        translate("SunAnalysisDialog",
                        "Indicate the path of the epw file"))
        #groupBox_location
        self.ui.groupBox_location.setTitle(
                        translate("SunAnalysisDialog",
                        "Location"))
        #label_City
        self.ui.label_City.setText(
                        translate("SunAnalysisDialog",
                        "City:"))
        #label_Country
        self.ui.label_Country.setText(
                        translate("SunAnalysisDialog",
                        "Country:"))
        #label_Latitude
        self.ui.label_Latitude.setText(
                        translate("SunAnalysisDialog",
                        "Latitude:"))
        #label_Longitude
        self.ui.label_Longitude.setText(
                        translate("SunAnalysisDialog",
                        "Longitude:"))
        #label_Elevation
        self.ui.label_Elevation.setText(
                        translate("SunAnalysisDialog",
                        "Elevation:"))
        #label_Time_zone
        self.ui.label_Time_zone.setText(
                        translate("SunAnalysisDialog",
                        "Time zone:"))
        #label_North_angle
        self.ui.label_North_angle.setText(
                        translate("SunAnalysisDialog",
                        "North angle:"))
        #lineEdit_North_angle
        self.ui.lineEdit_North_angle.setToolTip(
                        translate("SunAnalysisDialog",
                        "Indicate the true north.\n"
                        "Values ​​in a clockwise direction, \n"
                        "with zero in the direction of the y-axis"))
        #groupBox_Geometries
        self.ui.groupBox_Geometries.setTitle(
                        translate("SunAnalysisDialog",
                        "Geometries:"))
        #label_study_objects
        self.ui.label_study_objects.setText(
                       translate("SunAnalysisDialog",
                       "Study objects:"))
        #lineEdit_study_objects
        self.ui.lineEdit_study_objects.setToolTip(
                       translate("SunAnalysisDialog",
                       "Objects to be analyzed. \n"
                       "Use only simple volumetric objects."))
        #toolButton_study_objects
        self.ui.toolButton_study_objects.setToolTip(
                       translate("SunAnalysisDialog",
                       "Select the objects to be analyzed. \n"
                       "Use only simple volumetric objects."))
        #label_study_context
        self.ui.label_study_context.setText(
                       translate("SunAnalysisDialog",
                       "Context objects:"))
        #lineEdit_study_context
        self.ui.lineEdit_study_context.setToolTip(
                       translate("SunAnalysisDialog",
                       "Context objects that affect the \n"
                       "insolation of the objects being analyzed. \n"
                       "Use only simple volumetric objects."))
        #toolButton_study_context
        self.ui.toolButton_study_context.setToolTip(
                       translate("SunAnalysisDialog",
                       "Select the context objects that affect the \n"
                       "insolation of the objects being analyzed. \n"
                       "Use only simple volumetric objects."))
        #label_max_length
        self.ui.label_max_length.setText(
                        translate("SunAnalysisDialog",
                        "Max. length:"))
        #lineEdit_max_length
        self.ui.lineEdit_max_length.setToolTip(
                        translate("SunAnalysisDialog",
                        "Specify the maximum value for the \n"
                        "triangular sub faces (mm).\n"
                        "Warning: small values ​​can result in \n"
                        "very long calculation times."))
        #label_offset_distance
        self.ui.label_offset_distance.setText(
                        translate("SunAnalysisDialog",
                        "Offset distance:"))
        #lineEdit_offset_distance
        self.ui.lineEdit_offset_distance.setToolTip(
                        translate("SunAnalysisDialog",
                        "Specify the value for the \n"
                        "offset distance (mm)."))
        #groupBox_Sun_analysis_configuration
        self.ui.groupBox_Sun_analysis_configuration.setTitle(
                        translate("SunAnalysisDialog",
                        "Sun Analysis configurations"))
        #groupBox_sun_analysis_period
        self.ui.groupBox_Sun_analysis_period.setTitle(
                        translate("SunAnalysisDialog",
                        "Sun Analysis period"))
        self.ui.groupBox_Sun_analysis_period.setToolTip(
                        translate("SunAnalysisDialog",
                        "Analysis period between two dates of the "
                        "year and between certain hours."))
        #label_Date_from
        self.ui.label_Date_from.setText(
                        translate("SunAnalysisDialog",
                        "Date from:"))
        #dateEdit_date_from
        self.ui.dateEdit_date_from.setToolTip(
                        translate("SunAnalysisDialog",
                        "Indicate the start date of the analysis period."))
        #label_date_to
        self.ui.label_date_to.setText(
                        translate("SunAnalysisDialog",
                        "to:"))
        #dateEdit_date_to
        self.ui.dateEdit_date_to.setToolTip(
                        translate("SunAnalysisDialog",
                        "Indicate the end date of the analysis period."))
        #label_Time_from
        self.ui.label_Time_from.setText(
                        translate("SunAnalysisDialog",
                        "Time from:"))
        #spinBox_time_from
        self.ui.spinBox_time_from.setToolTip(
                       translate("SunAnalysisDialog",
                       "Indicate the start time of the analysis period."))
        #label_to
        self.ui.label_to.setText(
                       translate("SunAnalysisDialog",
                       "to:"))
        #spinBox_time_to
        self.ui.spinBox_time_to.setToolTip(
                       translate("SunAnalysisDialog",
                       "Indicate the end time of the analysis period."))
        #label_Timestep
        self.ui.label_Timestep.setText(
                        translate("SunAnalysisDialog",
                        "Timestep"))
        #comboBox_timestep
        self.ui.comboBox_timestep.setToolTip(
                       translate("SunAnalysisDialog",
                       "Specify how many times per hour \n"
                       "the calculation will be performed. \n"
                       "Note that larger numbers will \n"
                       "increase the computation time."))
        #checkBox_leap_year
        self.ui.checkBox_leap_year.setText(
                       translate("SunAnalysisDialog",
                       "Leap year"))
        self.ui.checkBox_leap_year.setToolTip(
                       translate("SunAnalysisDialog",
                       "Indicate whether the analysis period \n"
                       "is in leap year."))
        #groupBox_Sun_analysis_results
        self.ui.groupBox_Sun_analysis_results.setTitle(
                       translate("SunAnalysisDialog",
                       "Sun Analysis results"))
        #checkBox_sky_matrix_high_density
        self.ui.checkBox_sky_matrix_high_density.setText(
                        translate("SunAnalysisDialog",
                        "Sky matrix high density"))
        self.ui.checkBox_sky_matrix_high_density.setToolTip(
                        translate("SunAnalysisDialog",
                        "Enable sky matrix high density (Reinhart model) \n"
                        "or not (Tregenza one)."))
        #label_Results
        self.ui.label_Results.setText(
                       translate("SunAnalysisDialog",
                       "Results:"))
        #comboBox_results
        from freecad.Solar.LBComponents import RESUL_00, RESUL_01, RESUL_02
        self.ui.comboBox_results.setItemText(0, f"00 - {RESUL_00}")
        self.ui.comboBox_results.setItemText(1, f"01 - {RESUL_01}")
        self.ui.comboBox_results.setItemText(2, f"02 - {RESUL_02}")
        self.ui.comboBox_results.setToolTip(
                       translate("SunAnalysisDialog",
                       "Indicate whether the Solar Analysis results \n"
                       "should be presented in sun hours, \n"
                       "Radiation (kWh/m²) or Irradiance (W/m²)."))
        #checkBox_direct_diffuse
        self.ui.checkBox_direct_diffuse.setText(
                       translate("SunAnalysisDialog",
                       "Direct and diffuse"))
        self.ui.checkBox_direct_diffuse.setToolTip(
                       translate("SunAnalysisDialog",
                       "Enable it to visualize the direct and diffuse values."))
        #groupBox_Legend
        self.ui.groupBox_Legend.setTitle(
                        translate("SunAnalysisDialog",
                        "Legend Bar"))
        #label_color_count
        self.ui.label_color_count.setText(
                        translate("SunAnalysisDialog",
                        "Num. of colors"))
        self.ui.label_color_count.setToolTip(
                        translate("SunAnalysisDialog",
                        "Indicate the number of colors of the legend bar \n"
                        "(default: 11)."))
        #label_color_set
        self.ui.label_color_set.setText(
                       translate("SunAnalysisDialog",
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
                       translate("SunAnalysisDialog",
                       "Choose the legend bar color palette."))
        #pushButton_Apply
        self.ui.pushButton_Apply.setText(
                       translate("SunAnalysisDialog",
                       "Apply"))

    def translate(self, text):
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
            translate("SunAnalysisDialog", "Select epw file"),
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
                self, translate("SunAnalysisDialog", "Warning"),
                translate("SunAnalysisDialog",
                "Indicate a epw file before "
                "close the dialog Sun Analysis!")
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

    def open_select_study_objects(self):
        global NEW_GEOM
        from .SunAnalysis import SA
        sel_objs1 = []
        sel_objs1 = open_objs_selection(SA.objs_group)
        #print(f"sel_objs1: {sel_objs1}")
        if sel_objs1 != []:
            self.ui.lineEdit_study_objects.setText(str(sel_objs1))
            SA.study_objs = sel_objs1
            NEW_GEOM = True

    def open_select_context_objects(self):
        global NEW_GEOM
        from .SunAnalysis import SA
        sel_objs2 = []
        sel_objs2 = open_objs_selection(SA.objs_group)
        #print(f"sel_objs2: {sel_objs2}")
        if sel_objs2 != []:
            self.ui.lineEdit_study_context.setText(str(sel_objs2))
            SA.study_context = sel_objs2
            NEW_GEOM = True

    def results_toggled(self):
        if self.ui.comboBox_results.currentText()[0:2] == "00":
            self.ui.checkBox_direct_diffuse.setChecked(False)
            self.ui.checkBox_direct_diffuse.setEnabled(False)
        else:
            self.ui.checkBox_direct_diffuse.setEnabled(True)

    def direct_diffuse_toggled(self):
        if self.ui.comboBox_results.currentText()[0:2] != "00":
            from freecad.Solar.SunAnalysis import SA
            SA.direct_diffuse_values = self.ui.checkBox_direct_diffuse.isChecked()
            SunAnalysis.direct_diffuse_visualization()

    # Connection dialog x sun analysis properties
    def get_properties_data(self):

        """Get data from Sun Analysis properties and send them to dialog"""

        from freecad.Solar.SunAnalysis import SA, SA_NEW
        if SA is not None:
            # epw file
            if SA_NEW is True:
                try:
                    obj1 = FreeCAD.ActiveDocument.SkyDomes
                    # epw file
                    if obj1.epw_path != "":
                        self.ui.lineEdit_epw_path.setText(obj1.epw_path)
                        FreeCAD.Console.PrintMessage(translate("SunAnalysisDialog",
                                                      "epw path get from Sun Path") + '\n')
                    else:
                        self.ui.lineEdit_epw_path.setText(SA.epw_path)
                        #print("epw path get from SA")
                    # North
                    self.ui.lineEdit_North_angle.setText((str(float(obj1.north))))
                    # Sun analysis period
                    self.ui.dateEdit_date_from.setDate(QDate(obj1.start_year,
                                                             obj1.start_month,
                                                             obj1.start_day)
                                                             )
                    self.ui.dateEdit_date_to.setDate(QDate(obj1.end_year,
                                                           obj1.end_month,
                                                           obj1.end_day)
                                                           )
                    self.ui.spinBox_time_from.setValue(obj1.start_hour)
                    self.ui.spinBox_time_to.setValue(obj1.end_hour)
                    idx = self.ui.comboBox_timestep.findText(obj1.timestep)
                    if idx >= 0:
                        self.ui.comboBox_timestep.setCurrentIndex(idx)
                except:
                    pass
            else:
                # epw file
                self.ui.lineEdit_epw_path.setText(SA.epw_path)
                #print("epw path get from SA")
                # North
                self.ui.lineEdit_North_angle.setText((str(float(SA.north))))
                # Sun analysis period
                self.ui.dateEdit_date_from.setDate(QDate(SA.start_year, SA.start_month, SA.start_day))
                self.ui.dateEdit_date_to.setDate(QDate(SA.end_year, SA.end_month, SA.end_day))
                self.ui.spinBox_time_from.setValue(SA.start_hour)
                self.ui.spinBox_time_to.setValue(SA.end_hour)
                idx = self.ui.comboBox_timestep.findText(SA.timestep)
                if idx >= 0:
                    self.ui.comboBox_timestep.setCurrentIndex(idx)
            self.ui.checkBox_leap_year.setChecked(SA.leap_year)
            self.autofill_from_epw() #get location data
            self.ui.spinBox_color_count.setValue(SA.color_count)
            idx3 = self.ui.comboBox_color_set.findText(SA.color_set)
            if idx3 >= 0:
                self.ui.comboBox_color_set.setCurrentIndex(idx3)
            # Geometries
            labels_objs = []
            for o in range(len(SA.study_objs)):
                label_obj = SA.study_objs[o].Label
                labels_objs.append(label_obj)
            self.ui.lineEdit_study_objects.setText(str(labels_objs))
            labels_context = []
            for c in range(len(SA.study_context)):
                label_context = SA.study_context[c].Label
                labels_context.append(label_context)
            self.ui.lineEdit_study_context.setText(str(labels_context))
            self.ui.lineEdit_max_length.setText(str(SA.max_length))
            self.ui.lineEdit_offset_distance.setText(str(SA.offset_distance))
            # Sun analysis results
            idx2 = self.ui.comboBox_results.findText(SA.results)
            if idx2 >= 0:
                self.ui.comboBox_results.setCurrentIndex(idx2)
            #checkBox_sky_matrix_high_density
            self.ui.checkBox_sky_matrix_high_density.setChecked(SA.sky_matrix_high_density)
            self.ui.checkBox_direct_diffuse.setChecked(SA.direct_diffuse_values)
            self.results_toggled()
        else:
            FreeCAD.Console.PrintMessage(translate(
                'SunAnalysisDialog', 'There is no Sun Analysis!') + '\n')

    def save_to_propeties(self):

        """Save data from dialog to Sun Analysis properties"""

        from freecad.Solar.SunAnalysis import SA
        if SA is not None:

            # epw file
            epw_path = self.ui.lineEdit_epw_path.text()
            SA.epw_path = epw_path
            # Location
            SA.city = self.ui.label_city_value.text()
            SA.country = self.ui.label_country_value.text()
            SA.elevation = float(self.ui.label_elevation_value.text())
            SA.latitude = float(self.ui.label_latitude_value.text())
            SA.longitude = float(self.ui.label_longitude_value.text())
            SA.time_zone = int(float(self.ui.label_time_zone_value.text()))
            # North angle
            SA.north  = float(self.ui.lineEdit_North_angle.text())
            SA.color_count = self.ui.spinBox_color_count.value()
            prefix1 = int(self.ui.comboBox_color_set.currentText()[0:2])
            color_set_list = SA.getEnumerationsOfProperty("color_set")
            SA.color_set = color_set_list[prefix1]
            # Geometries
            SA.max_length = float(self.ui.lineEdit_max_length.text())
            SA.offset_distance = float(self.ui.lineEdit_offset_distance.text())
            date_string1 = self.ui.dateEdit_date_from.date()
            SA.start_day = date_string1.day()
            SA.start_month = date_string1.month()
            SA.start_year = date_string1.year()
            date_string2 = self.ui.dateEdit_date_to.date()
            SA.end_day = date_string2.day()
            SA.end_month = date_string2.month()
            SA.end_year = date_string2.year()
            SA.start_hour = self.ui.spinBox_time_from.value()
            SA.end_hour = self.ui.spinBox_time_to.value()
            SA.timestep = self.ui.comboBox_timestep.currentText()
            SA.leap_year = self.ui.checkBox_leap_year.isChecked()
            # Sun analysis results
            SA.sky_matrix_high_density = self.ui.checkBox_sky_matrix_high_density.isChecked()
            prefix2 = int(self.ui.comboBox_results.currentText()[0:2])
            resul_list = SA.getEnumerationsOfProperty("results")
            SA.results = resul_list[prefix2]
            SA.direct_diffuse_values = self.ui.checkBox_direct_diffuse.isChecked()
        else:
            FreeCAD.Console.PrintMessage(translate('SunAnalysisDialog',
                             'There is no Sun Analysis!') + '\n')
        FreeCAD.ActiveDocument.recompute()

    def compare_sun_analysis_data(self):

        """Compares and activates the update of Sun Analysis data."""

        #forms
        max_length2 = float(self.ui.lineEdit_max_length.text())

        #values and colors
        epw_path2 = self.ui.lineEdit_epw_path.text()
        north2 = float(self.ui.lineEdit_North_angle.text())
        offset_distance2 = float(self.ui.lineEdit_offset_distance.text())
        date_string1 = self.ui.dateEdit_date_from.date()
        start_day2 = date_string1.day()
        start_month2 = date_string1.month()
        start_year2 = date_string1.year()
        date_string2 = self.ui.dateEdit_date_to.date()
        end_day2 = date_string2.day()
        end_month2 = date_string2.month()
        end_year2 = date_string2.year()
        start_hour2 = int(self.ui.spinBox_time_from.text())
        end_hour2 = int(self.ui.spinBox_time_to.text())
        timestep2 = self.ui.comboBox_timestep.currentText()
        leap_year2 = self.ui.checkBox_leap_year.isChecked()
        results2 = self.ui.comboBox_results.currentText()[0:2]
        sky_matrix_high_density2 = self.ui.checkBox_sky_matrix_high_density.isChecked()

        #colors
        color_count2 = self.ui.spinBox_color_count.value()
        color_set2 = self.ui.comboBox_color_set.currentText()[0:2]

        dif_forms = False
        dif_values_colors = False
        dif_colors = False
        from freecad.Solar.SunAnalysis import SA
        if SA is not None:
            #SA values
            epw_path1 = SA.epw_path
            north1 = float(SA.north)
            color_count1 = SA.color_count
            offset_distance1 = SA.offset_distance
            color_set1 = SA.color_set[0:2]
            max_length1 = SA.max_length
            start_year1 = SA.start_year
            end_year1 = SA.end_year
            start_month1 = SA.start_month
            end_month1 = SA.end_month
            start_day1 = SA.start_day
            end_day1 = SA.end_day
            start_hour1 = SA.start_hour
            end_hour1 = SA.end_hour
            timestep1 = SA.timestep
            leap_year1 = SA.leap_year
            results1 = SA.results[0:2]
            sky_matrix_high_density1 = SA.sky_matrix_high_density

            #check forms
            if max_length1 != max_length2 or NEW_GEOM is True:
                dif_forms = True
                print(f"found difference for dif_forms: {dif_forms}")
            #else:
                #print(f"dif_forms: {dif_forms}")

            #check values and colors
            if any(condition for condition in [epw_path1 != epw_path2,
                                               north1 != north2,
                                               offset_distance1 != offset_distance2,
                                               start_year1 != start_year2,
                                               end_year1 != end_year2,
                                               start_month1 != start_month2,
                                               end_month1 != end_month2,
                                               start_day1 != start_day2,
                                               end_day1 != end_day2,
                                               start_hour1 != start_hour2,
                                               end_hour1 != end_hour2,
                                               timestep1 != timestep2,
                                               #daylight_saving1 != daylight_saving2,
                                               leap_year1 != leap_year2,
                                               results1 != results2,
                                               sky_matrix_high_density1 != sky_matrix_high_density2,      
                                               ]
                ):
                dif_values_colors = True
                print(f"found difference for values_colors: {dif_values_colors}")
            #else:
                #print(f"dif_values_colors: {dif_values_colors}")

            #check colors
            if any(condition for condition in [color_count1 != color_count2,
                                               color_set1 != color_set2
                                               ]
                                               ):
                dif_colors = True
                print(f"found difference for dif_colors: {dif_colors}")
            #else:
                #print(f"dif_colors: {dif_colors}")

            #update properties
            self.save_to_propeties()
            #print("send data to Sun Analysis!")
            #print(f"dif_forms: {dif_forms}, dif_values_colors: {dif_values_colors}, dif_colors: {dif_colors}")
            if dif_forms is True or dif_values_colors is True or dif_colors is True:
                #print("try to update Sun Analysis data!")
                SunAnalysis.modify_sun_analysis(forms = dif_forms,
                                                values_colors = dif_values_colors,
                                                colors = dif_colors)
                FreeCAD.Console.PrintMessage(translate('SunAnalysisDialog',
                                                       "Sun Analysis was updated!\n"))
        else:
            print ("Compare sun analysis data: Can not get data from Sun Analysis!")

    def on_button_apply_clicked(self):

        """Apply button actions"""

        from .SunAnalysis import SA_NEW
        if SA_NEW is True:
            self.save_to_propeties()
        else:
            self.compare_sun_analysis_data()

def open_sun_analysis_configuration():

    """Open Sun Analysis configuration"""

    global NEW_GEOM
    dlg = SunAnalysisConfigurationDialog()
    dlg.get_properties_data()
    if dlg.show_dialog():
        from .SunAnalysis import SA_NEW
        if SA_NEW is True:
            dlg.save_to_propeties()
            SunAnalysis.create_sun_analysis()
            NEW_GEOM = False
        else:
            dlg.compare_sun_analysis_data()
            NEW_GEOM = False
    from .SunAnalysis import SA, SA_NEW
    if SA_NEW is True:
        FreeCAD.ActiveDocument.removeObject(SA.Name)

#-------------------------------------------------------

class GroupRestrictedSelector(QtWidgets.QDialog):
    def __init__(self, selected_group):

        """Selection of study objects and context dialog"""

        super(GroupRestrictedSelector, self).__init__(Gui.getMainWindow())
        self.setWindowTitle(translate("SunAnalysisDialog",
                                              "Selection of study or context objects"))
        self.setMinimumSize(450, 500)
        self.selected_group = selected_group
        layout = QtWidgets.QVBoxLayout(self)
        #TreeWidget configured for multiple selection
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Object in Group", "Type"])
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.populate_tree()
        layout.addWidget(self.tree)
        #Button
        self.btn_confirm = QtWidgets.QPushButton(
                           translate("SunAnalysisDialog",
                                             "Confirm")
                            )
        self.btn_confirm.clicked.connect(self.accept)
        layout.addWidget(self.btn_confirm)

    def populate_tree(self):
        doc = FreeCAD.ActiveDocument
        if not doc: return

        """Populate tree with objects from selected group"""

        #for group_name in self.selected_group:
        group_obj = doc.getObject(self.selected_group.Name)
        #Creates a category item for the Group
        group_item = QtWidgets.QTreeWidgetItem([group_obj.Label, "GROUP"])
        group_item.setFlags(group_item.flags() & ~QtCore.Qt.ItemIsSelectable)
        self.tree.addTopLevelItem(group_item)

        for obj in group_obj.Group:
            child_item = QtWidgets.QTreeWidgetItem([obj.Label, obj.TypeId.split('::')[-1]])
            child_item.setData(0, QtCore.Qt.UserRole, obj.Name)
            #Add available icon
            if hasattr(obj, "ViewObject"):
                child_item.setIcon(0, obj.ViewObject.Icon)
            group_item.addChild(child_item)
        group_item.setExpanded(True)

    def get_selected_objects(self):
        return [FreeCAD.ActiveDocument.getObject(item.data(0, QtCore.Qt.UserRole))
                for item in self.tree.selectedItems() if item.data(0, QtCore.Qt.UserRole)]

def open_objs_selection(selected_group = None):

    """Open the objects selection dialog"""

    dialog = GroupRestrictedSelector(selected_group)
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        selection = dialog.get_selected_objects()
        return selection
    else:
        return []
