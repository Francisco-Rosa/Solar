# SPDX-License-Identifier: LGPL-2.1-or-later
# SPDX-FileNotice: Part of the Solar addon.

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

"""This module implements the ladybug components."""

import math
import FreeCAD
import FreeCADGui as Gui
import Draft
from PySide.QtCore import QT_TRANSLATE_NOOP
from ladybug.color import ColorRange, Colorset
from ladybug.legend import Legend, LegendParameters
from ladybug_geometry.geometry3d import Point3D
from ladybug_radiance.visualize.skydome import SkyDome
from ladybug_radiance.skymatrix import SkyMatrix
from ladybug.epw import EPW
from ladybug.datacollection import HourlyContinuousCollection
from ladybug.datatype.base import DataTypeBase
from ladybug.header import Header
from ladybug.datatype.energy import Energy

#=================================================
# 1. Sky matrix
#=================================================

def get_sky_matrix_values(epw_path = "",
                          period = None,
                          high_density = False,
                          timestep = 1,
                          ground_reflectance=0.2
                          ):

    """Get solar radiation (kWh/m2)
    from ladybug sky matrix Tregenza or Reinhart
    model.
    SkyMatrix(wea,
              north,
              high_density,
              ground_reflectance=0.2)"""

    hoys = [h for h in period.hoys] # timestep = 1
    epw = EPW(epw_path)
    metadata_dic = epw.metadata
    if timestep == 1:
        sky_matrix = SkyMatrix.from_epw(epw_path, hoys)
        sky_matrix.high_density = high_density
    if timestep > 1:
        dnr_values = [epw.direct_normal_radiation[int(hoy % 8760)] for hoy in hoys] # timestep = 1
        dhr_values = [epw.diffuse_horizontal_radiation[int(hoy % 8760)] for hoy in hoys] # timestep = 1
        #get header
        data_type = Energy(name = "Energy")
        unit = "kWh"
        analysis_period = period
        header = get_header(data_type,
                       unit,
                       analysis_period,
                       metadata_dic
                       )
        #get continuous irradiance values
        location = epw.location
        #update timestep > 1
        direct_normal_irradiance = get_continuous_values(header = header,
                                                        values = dnr_values,
                                                        timestep = timestep
                                                        )
        diffuse_horizontal_irradiance = get_continuous_values(header = header,
                                                        values = dhr_values,
                                                        timestep =  timestep
                                                        )
        sky_matrix = SkyMatrix.from_components(location,
                                  direct_normal_irradiance,
                                  diffuse_horizontal_irradiance,
                                  #hoys = None,
                                  #north=0,
                                  high_density = high_density,
                                  ground_reflectance=0.2
                                  )
    metadata = sky_matrix.metadata #tuple
    #(If True, Radiance must be installed)
    #get sky matrix values
    direct_values = list(sky_matrix.direct_values)
    diffuse_values = list(sky_matrix.diffuse_values)
    total_values = [a + b for a, b in zip(
                                direct_values,
                                diffuse_values)]
    FreeCAD.ActiveDocument.recompute()
    return [sky_matrix, #[0]
            total_values, #[1]
            direct_values, #[2]
            diffuse_values, #[3]
            metadata #[4]
            ]

#=================================================
# 2. Sky dome
#=================================================

def get_sky_dome_values(sky_matrix = None,
                         legend_parameters = None,
                         plot_irradiance = False,
                         center_point = Point3D(x=0,y=0,z=0),
                         radius = 100,
                         projection = None):

    """Get solar radiation (kWh/m2) or irradiance (W/m²)
    from ladybug sky matrix Tregenza or Reinhart
    model."""

    sky_dome_obj = None
    sky_dome_obj = SkyDome(sky_matrix = sky_matrix,
                           plot_irradiance = plot_irradiance)
                           # (If True, Radiance must be installed)
    # Get and convert lb values
    #values
    total_values = []
    total_values = list(sky_dome_obj.total_values)
    direct_values = []
    direct_values = list(sky_dome_obj.direct_values)
    diffuse_values = []
    diffuse_values = list(sky_dome_obj.diffuse_values)
    #sky dome vectors
    vector_values = []
    vectors = sky_dome_obj.patch_vectors
    for i in range(len(vectors)):
        vector = (vectors[i][0], vectors[i][1], vectors[i][2])
        vector_values.append(vector)
    #convert metadata_lb to metadata_str
    metadata_lb = []
    metadata_lb = sky_dome_obj.metadata
    metadata_str = []
    for i in range(len(metadata_lb)):
        data = metadata_lb[i]
        str_data = str(data)
        metadata_str.append(str_data)
    FreeCAD.ActiveDocument.recompute()
    return [sky_dome_obj, #[0]
            total_values, #[1]
            direct_values, #[2]
            diffuse_values, #[3]
            vector_values, #[4]
            metadata_str  #[5]
            ]

#=================================================
# 3. Inter matrix and sky inter matrix
#=================================================

#SunAnalysis.py

#=================================================
# 4. Color range and others
#=================================================

def get_face_colors(sun_analysis_results = None,
                    domain = None,
                    leg_colors = None
                    ):

    """Get sun analysis colors for each centroid
    using ladybug color range.
    ColorRange(colors=None,
               domain=None,
               continuos_colors=True)"""

    color_range = []
    color_range = ColorRange()
    color_range.colors = leg_colors
    #color_range.domain = [min(domain), max(domain)]
    color_range.domain = [0, max(domain)]
    face_colors = []
    for value in sun_analysis_results:
        color = color_range.color(value)
        color_rgb = (color[0], color[1], color[2])
        face_colors.append(color_rgb)

    FreeCAD.ActiveDocument.recompute()
    return face_colors #color for each face

def get_analysis_clone(compound = None,
                       obj_label = "",
                       analysis_group = None
                       ):

    """Create a clone object for each sun analysis object."""

    doc = FreeCAD.ActiveDocument
    # clone
    analysis_clone = Draft.make_clone(doc.getObject(compound.Name))
    doc.getObject(analysis_clone.Name).Label = obj_label
    Gui.ActiveDocument.getObject(analysis_clone.Name).LineWidth = 1
    Gui.ActiveDocument.getObject(analysis_clone.Name).PointSize = 1
    # group
    doc.getObject(analysis_group.Name).addObject(analysis_clone)
    FreeCAD.ActiveDocument.recompute()
    return analysis_clone

def apply_color_faces(obj = None,
                      face_colors = None,
                      transparency = 0):

    """Apply colors for each face
    using ladybug color range."""

    obj.ViewObject.ShapeAppearance = (
                 FreeCAD.Material(SpecularColor=(0.33,0.33,0.33))
                 )
    obj.ViewObject.LineWidth = 1
    obj.ViewObject.PointSize = 1
    obj.ViewObject.DiffuseColor = face_colors
    obj.ViewObject.Transparency = transparency
    return obj
    FreeCAD.ActiveDocument.recompute()

#=================================================
# 5. Compass
#=================================================

def get_compass(center = None,
                radius = None,
                north = None,
                variation_angle = None,
                dome_group1 = None,
                dome_group2 = None,
                dome_group3 = None
                ):

    """Create compass"""

    doc = FreeCAD.ActiveDocument
    # Create generic compass and values
    angles_compas = []
    angles_compas_leg = []
    compass_list = []
    max_angle = 360
    n_angles = int(max_angle / variation_angle)
    # create compass angles and legend text lists
    for i in range(n_angles):
        angle = variation_angle * i
        angles_compas.append(angle) # angles, clockwise
        angle_leg = str(angle) # string angles, clockwise
        if angle_leg == "0":
            angle_leg = QT_TRANSLATE_NOOP("LBComponents", "N")
        elif angle_leg == "90":
            angle_leg = QT_TRANSLATE_NOOP("LBComponents", "E")
        elif angle_leg == "180":
            angle_leg = QT_TRANSLATE_NOOP("LBComponents", "S")
        elif angle_leg == "270":
            angle_leg = QT_TRANSLATE_NOOP("LBComponents", "W")
        angles_compas_leg.append(angle_leg)
    # create compass circles
    pl=FreeCAD.Placement()
    pl.Base = FreeCAD.Vector(center)
    pl1=FreeCAD.Placement()
    pl2=FreeCAD.Placement()
    pl3=FreeCAD.Placement()
    pl.Rotation.setYawPitchRoll(0,0,0)
    radius_compas = radius
    circle1 = Draft.make_circle(radius=radius_compas,
                                placement=pl,
                                face=False,
                                support=None)
    circle2 = Draft.make_circle(radius=radius_compas*1.02,
                                placement=pl,
                                face=False,
                                support=None)
    circle3 = Draft.make_circle(radius=radius_compas*1.05,
                                placement=pl,
                                face=False,
                                support=None)
    compass_list = [circle1, circle2, circle3]
    # Create groups
    dome_leg1_group = doc.addObject('App::DocumentObjectGroup',
                                    'Compass_legend_total')
    dome_leg1_group.Label = QT_TRANSLATE_NOOP("LBComponents",
                                              "Compass_legend_total")
    dome_leg2_group = doc.addObject('App::DocumentObjectGroup',
                                    'Compass_legend_direct')
    dome_leg2_group.Label = QT_TRANSLATE_NOOP("LBComponents",
                                              "Compass_legend_direct")
    dome_leg3_group = doc.addObject('App::DocumentObjectGroup',
                                    'Compass_legend_diffuse')
    dome_leg3_group.Label = QT_TRANSLATE_NOOP("LBComponents",
                                              "Compass_legend_diffuse")
    # Create lines and texts
    for i in range(n_angles):
        # lines
        angle = (90 - float(north)) - angles_compas[i] # north y-axis, clockwise
        x1 = radius_compas * math.cos(math.radians(angle))
        y1 = radius_compas * math.sin(math.radians(angle))
        x2 = radius_compas * math.cos(math.radians(angle)) * 1.05
        y2 = radius_compas * math.sin(math.radians(angle)) * 1.05
        points = [FreeCAD.Vector(x1 + center[0],
                                 y1 + center[1],
                                 center[2]),
                  FreeCAD.Vector(x2 + center[0],
                                 y2 + center[1],
                                 center[2])]
        line = Draft.make_wire(points, placement=pl,
                               closed=False, face=False,
                               support=None)
        compass_list.append(line)
        # compass text total values
        x3 = radius_compas * math.cos(math.radians(angle)) * 1.15
        y3 = radius_compas * math.sin(math.radians(angle)) * 1.15
        title_leg_compas = angles_compas_leg[i]
        pl1.Base = FreeCAD.Vector(x3 - radius/20 + center[0],
                                  y3 - radius/50 + center[1],
                                  center[2])
        text_compas_leg1 = Draft.make_text([title_leg_compas],
                                            placement=pl1,
                                            screen=None,
                                            height=radius/15,
                                            line_spacing=None
                                           )
        text_compas_leg1.Label = str(title_leg_compas) + "_"
        # compass text direct values
        pl2.Base = FreeCAD.Vector(x3 - radius/20 + radius*3 + center[0],
                                  y3-radius/50 + center[1],
                                  center[2])
        text_compas_leg2 = Draft.make_text([title_leg_compas],
                                            placement=pl2,
                                            screen=None,
                                            height=radius/15,
                                            line_spacing=None
                                           )
        text_compas_leg2.Label = str(title_leg_compas) + "_"
        # compass text diffuse values
        pl3.Base = FreeCAD.Vector(x3 - radius/20 + radius*6 + center[0],
                                  y3-radius/50 + center[1],
                                  center[2])
        text_compas_leg3 = Draft.make_text([title_leg_compas],
                                            placement=pl3,
                                            screen=None,
                                            height=radius/15,
                                            line_spacing=None
                                            )
        text_compas_leg3.Label = str(title_leg_compas) + "_"
        # text groups
        doc.getObject(dome_leg1_group.Name).addObject(text_compas_leg1)
        doc.getObject(dome_leg2_group.Name).addObject(text_compas_leg2)
        doc.getObject(dome_leg3_group.Name).addObject(text_compas_leg3)
    # Configure compass and values
    # Get total, direct and diffuse groups
    dome_total_group = dome_group1
    dome_direct_group = dome_group2
    dome_diffuse_group = dome_group3
    # Compass total values - compound
    compass_total = doc.addObject("Part::Compound",
                                  "Compass_circles_total")
    compass_total.Label = QT_TRANSLATE_NOOP("LBComponents",
                                            "Compass_circles_total")
    doc.getObject(compass_total.Name).Links = compass_list
    doc.getObject(dome_total_group.Name).addObject(compass_total)
    # Compass direct values - clones
    compass_direct = Draft.make_clone(doc.getObject(compass_total.Name))
    doc.getObject(compass_direct.Name).Placement.Base = (radius*3, 0,0)
    doc.getObject(compass_direct.Name).Label = QT_TRANSLATE_NOOP(
                                               "LBComponents",
                                               "Compass_circles_direct")
    doc.getObject(dome_direct_group.Name).addObject(compass_direct)
    # Compass diffuse values - clone
    compass_diffuse = Draft.make_clone(doc.getObject(compass_total.Name))
    doc.getObject(compass_diffuse.Name).Placement.Base = (radius*6, 0,0)
    doc.getObject(compass_diffuse.Name).Label = QT_TRANSLATE_NOOP(
                                                "LBComponents",
                                                "Compass_circles_diffuse")
    doc.getObject(dome_diffuse_group.Name).addObject(compass_diffuse)
    # Save and return data
    compass_data = []
    compass_data.append(dome_leg1_group) # [0]
    compass_data.append(dome_leg2_group) # [1]
    compass_data.append(dome_leg3_group) # [2]
    FreeCAD.ActiveDocument.recompute()
    return compass_data

def modify_compass(center = None,
                   radius = None,
                   north = None,
                   variation_angle = None,
                   sky_domes_group = None
                   ):

    """Modify compass"""

    # Configure compass circles
    angles_compas = []
    max_angle = 360
    n_angles = int(max_angle / variation_angle)
    # Create compass angles and legend text lists
    for i in range(n_angles):
        angle = variation_angle * i
        angles_compas.append(angle)
    # Get necessary object lists
    circ_lines_list = []
    circ_lines_list = sky_domes_group.Group[0].Group[1].Links
    text_list1 = []
    text_list1 = sky_domes_group.Group[0].Group[2].Group[1].Group
    text_list2 = []
    text_list2 = sky_domes_group.Group[1].Group[2].Group[1].Group
    text_list3 = []
    text_list3 = sky_domes_group.Group[2].Group[2].Group[1].Group
    compass_original = sky_domes_group.Group[0].Group[1]
    compass_clone1 = sky_domes_group.Group[1].Group[1]
    compass_clone2 = sky_domes_group.Group[2].Group[1]
    pl = FreeCAD.Placement() # original
    pl.Base = FreeCAD.Vector(center)
    pl.Rotation.setYawPitchRoll(north,0,0)
    circle1 = circ_lines_list[0]
    circle1.Placement = pl
    circle1.Radius = radius
    circle2 = circ_lines_list[1]
    circle2.Placement = pl
    circle2.Radius = radius*1.02
    circle3 = circ_lines_list[2]
    circle3.Placement = pl
    circle3.Radius = radius*1.05
    # Configure lines and texts positions
    for i in range(len(circ_lines_list) - 3):
        angle = (90 - float(north)) - angles_compas[i] # north y-axis, clockwise
        # modify lines
        x1 = radius * math.cos(math.radians(angle))
        y1 = radius * math.sin(math.radians(angle))
        x2 = radius * math.cos(math.radians(angle)) * 1.05
        y2 = radius * math.sin(math.radians(angle)) * 1.05
        line = circ_lines_list[i + 3]
        line.Placement = pl
        line.Start = FreeCAD.Vector(x1 + center[0],
                                    y1 + center[1],
                                    center[2])
        line.End = FreeCAD.Vector(x2 + center[0],
                                  y2 + center[1],
                                  center[2])
        # modify texts
        x3 = radius * math.cos(math.radians(angle)) * 1.15
        y3 = radius * math.sin(math.radians(angle)) * 1.15
        x_text1 = center[0] + (x3 - radius/20)
        y_text1 = center[1] + (y3 - radius/50)
        z_text1 = center[2]
        text1 = text_list1[i]
        text1.Placement.Base = FreeCAD.Vector(x_text1,
                                              y_text1,
                                              z_text1
                                              )
        text1.ViewObject.FontSize = radius/15
        text2 = text_list2[i]
        text2.Placement.Base = FreeCAD.Vector(x_text1 + radius*3,
                                              y_text1,
                                              z_text1
                                              )
        text2.ViewObject.FontSize = radius/15
        text3 = text_list3[i]
        text3.Placement.Base = FreeCAD.Vector(x_text1 + radius*6,
                                              y_text1,
                                              z_text1
                                              )
        text3.ViewObject.FontSize = radius/15
    FreeCAD.ActiveDocument.recompute()
    # Update distance between original and clone1
    base_ori = compass_original.Placement.Base # original
    x_ori = base_ori[0]
    y_ori = base_ori[1]
    z_ori = base_ori[2]
    x1_fin = x_ori + radius*3
    pl1 = FreeCAD.Placement()
    pl1.Base = FreeCAD.Vector(x1_fin, y_ori, z_ori)
    compass_clone1.Placement = pl1
    # Update distance between original and clone2
    x2_fin = x_ori + radius*6
    pl2 = FreeCAD.Placement()
    pl2.Base = FreeCAD.Vector(x2_fin, y_ori, z_ori)
    compass_clone2.Placement = pl2

    FreeCAD.ActiveDocument.recompute()

#=================================================
# 6. Legend bar
#=================================================

def get_modify_legend_bar(bar_obj = None,
                          text_leg_group = None,
                          title = "",
                          values = None,
                          position = (0, 0, 0),
                          seg_heith = 1000,
                          seg_width = 1000,
                          seg_count = 11,
                          color_leg_set = 0,
                          min = 0.0
                          ):

    """Get or modify legend using ladybug color range
    and legend parameters.
    LegendParameters(min=None,
                     max=None,
                     segment_count=None,
                     colors=None,
                     title=None,
                     base_plane=None)
    Legend(values, legend_paramenters=None)
    leg_mesh = legend.segment_mesh #lb Mesh3D
    leg_vert = leg_mesh.vertices #lb Point3D
    leg_faces = leg_mesh.faces #tuples of tuples
    """

    doc = FreeCAD.ActiveDocument
    #color_scheme
    color_scheme = Colorset()
    #leg_par
    leg_par = LegendParameters
    legend = Legend(values,
                    leg_par(min = min, segment_count = seg_count,
                    colors = color_scheme[color_leg_set]))
    leg_par.segment_height = seg_heith
    leg_par.segment_width = seg_width

    # get bar
    if bar_obj is None:
        #first rect
        pl=FreeCAD.Placement()
        pl.Base = FreeCAD.Vector(position)
        rect = Draft.make_rectangle(length = seg_width,
                                    height = seg_heith,
                                    placement = pl,
                                    face = True,
                                    support = None)
        #array
        bar_new = Draft.make_ortho_array(rect,
                                    v_y = FreeCAD.Vector(0.0, seg_heith, 0.0),
                                    n_x = 1,
                                    n_y = seg_count,
                                    n_z = 1,
                                    use_link = False
                                    )
        bar_new.Label = QT_TRANSLATE_NOOP("LBComponents",
                                          "Legend_bar")
    else:
        bar_obj.Base.Length = seg_width
        bar_obj.Base.Height = seg_heith
        bar_obj.Base.Placement.Base = FreeCAD.Vector(position)
        bar_obj.IntervalY.y = seg_heith
        bar_obj.NumberY = seg_count

    # apply the corresponding colors
    color_rgb_leg = legend.segment_colors
    bar_colors = []
    for c in range(len(color_rgb_leg)):
        color = color_rgb_leg[c]
        color_rgb = (color[0], color[1], color[2])
        bar_colors.append(color_rgb)
    if bar_obj is None:
        apply_color_faces(obj = bar_new,
                          face_colors = bar_colors,
                          transparency = 0)
    else:
        apply_color_faces(obj = bar_obj,
                          face_colors = bar_colors,
                          transparency = 0)
    #delete texts if seg count is different
    leg_text_deleted = False
    if bar_obj is not None and len(text_leg_group.Group) != (seg_count + 1):
        for text in text_leg_group.Group:
            FreeCAD.ActiveDocument.removeObject(text.Name)
            leg_text_deleted = True
    # get texts
    leg_text = legend.segment_text
    text_location = legend.segment_text_location # normal, origin
    leg_bar_group = None
    if bar_obj is None:
        # create legend bar groups
        leg_bar_group = doc.addObject("App::DocumentObjectGroup",
                                        "SA_Legend_bar")
        leg_bar_group.Label = QT_TRANSLATE_NOOP("LBComponents",
                                                 "Legend_bar_")
        doc.getObject(leg_bar_group.Name).addObject(bar_new)
        # create legend text group
        leg_text_group = doc.addObject("App::DocumentObjectGroup",
                                        "Legend_text")
        leg_text_group.Label = QT_TRANSLATE_NOOP("LBComponents",
                                                 "Legend_text_")
    else:
        pass
    #get title positions
    x1 = text_location[0].o.x + position[0]
    y1 = text_location[-1].o.y + LegendParameters.segment_height + position[1]
    z1 = text_location[-1].o.z + position[2]
    pos1 = (x1, y1, z1)
    pl_bar1 = FreeCAD.Placement()
    pl_bar1.Base = pos1
    #get leg title
    text1 = title
    if bar_obj is None or leg_text_deleted == True:
        text_title = Draft.make_text(text1,
                                    placement = pl_bar1,
                                    screen = None,
                                    height = seg_heith/3,
                                    line_spacing = None
                                    )
        text_title.Label = text1 + "_"
        if leg_text_deleted == False:
            doc.getObject(leg_text_group.Name).addObject(text_title)
        else:
            doc.getObject(text_leg_group.Name).addObject(text_title)
    else:
        text_title = text_leg_group.Group[0]
        text_title.Text = text1
        text_title.Placement.Base = pos1
        text_title.ViewObject.FontSize = seg_heith/3
    #get positions and texts
    for n in range(len(text_location)):
        x2 = text_location[n].o.x + position[0]
        y2 = text_location[n].o.y + position[1]
        z2 = text_location[n].o.z + position[2]
        pos2 = (x2, y2, z2)
        text2 = leg_text[n]
        pl_bar2 = FreeCAD.Placement()
        pl_bar2.Base = pos2
        if bar_obj is None or leg_text_deleted == True:
            text_value = Draft.make_text(text2,
                                        placement = pl_bar2,
                                        screen = None,
                                        height = seg_heith/3,
                                        line_spacing=None
                                        )
            if leg_text_deleted == False:
                doc.getObject(leg_text_group.Name).addObject(text_value)
            else:
                doc.getObject(text_leg_group.Name).addObject(text_value)
        else:
            text_value = text_leg_group.Group[n + 1]
            text_value.Text = text2
            text_value.Placement.Base = pos2
            text_value.ViewObject.FontSize = seg_heith/3
        text_value.Label = text2 + "_"
    if bar_obj is None:
        doc.getObject(leg_bar_group.Name).addObject(leg_text_group)

    FreeCAD.ActiveDocument.recompute()
    return [leg_bar_group, #[0]
            color_rgb_leg #[1]
            ]

#=================================================
# 7. Main legend
#=================================================

def get_main_legend_texts(units = None,
                          metadata = None
                          ):

    """Get main legend values"""

    period_leg = f"{metadata[2]} - {metadata[3]}"
    city_leg = f"{metadata[6]}"
    country_leg = f"{metadata[5]}"
    time_zone_leg = f"{metadata[7]}"
    source_leg = f"{metadata[4]}"
    # Total title
    title_leg1 = QT_TRANSLATE_NOOP(
                 "LBComponents", "Total" + " " + "{}").format(units)
    text_total = [title_leg1, period_leg, city_leg,
                  country_leg, time_zone_leg, source_leg]
    # Direct title
    title_leg2 = QT_TRANSLATE_NOOP(
                 "LBComponents", "Direct" + " " + "{}").format(units)
    text_direct = [title_leg2, period_leg, city_leg,
                   country_leg, time_zone_leg, source_leg]
    # Diffuse title
    title_leg3 = QT_TRANSLATE_NOOP(
                 "LBComponents", "Diffuse" + " " + "{}").format(units)
    text_diffuse = [title_leg3, period_leg, city_leg,
                    country_leg, time_zone_leg, source_leg]
    FreeCAD.ActiveDocument.recompute()
    return [text_total, #[0]
            text_direct, #[1]
            text_diffuse #[2]
            ]

def get_main_legends(pos1 = (0.0, 0.0, 0.0),
                     pos2 = (0.0, 0.0, 0.0),
                     pos3 = (0.0, 0.0, 0.0),
                     units = None,
                     metadata = None,
                     text_high = 100,
                     ):

    """Create main legend"""

    doc = FreeCAD.ActiveDocument
    #get texts
    leg_titles = get_main_legend_texts(units, metadata)
    text_total = leg_titles[0]
    text_direct = leg_titles[1]
    text_diffuse = leg_titles[2]

    # main legend positions
    pl1_leg = FreeCAD.Placement()
    pl1_leg.Base = FreeCAD.Vector(pos1)
    pl2_leg = FreeCAD.Placement()
    pl2_leg.Base = FreeCAD.Vector(pos2)
    pl3_leg = FreeCAD.Placement()
    pl3_leg.Base = FreeCAD.Vector(pos3)
    # main legend texts
    text_leg1 = Draft.make_text(text_total,
                                placement=pl1_leg,
                                screen=None,
                                height=text_high,
                                line_spacing=1.2
                                )
    text_leg1.Label = QT_TRANSLATE_NOOP("LBComponents",
                                        "Legend_total")
    text_leg2 = Draft.make_text(text_direct,
                                placement=pl2_leg,
                                screen=None,
                                height=text_high,
                                line_spacing=1.2
                                )
    text_leg2.Label = QT_TRANSLATE_NOOP("LBComponents",
                                        "Legend_direct")
    text_leg3 = Draft.make_text(text_diffuse, placement=pl3_leg,
                                screen=None, height=text_high,
                                line_spacing=1.2
                                )
    text_leg3.Label = QT_TRANSLATE_NOOP("LBComponents",
                                        "Legend_diffuse")
    #create groups and put main legends into correspondent ones
    leg_total_group = doc.addObject('App::DocumentObjectGroup',
                                    'Main_Legend_Total')
    leg_total_group.Label = QT_TRANSLATE_NOOP("LBComponents",
                                              "Main_Legend_Total")
    doc.getObject(leg_total_group.Name).addObject(text_leg1)
    leg_direct_group = doc.addObject('App::DocumentObjectGroup',
                                     'Main_Legend_Direct')
    leg_direct_group.Label = QT_TRANSLATE_NOOP("LBComponents",
                                               "Main_Legend_Direct")
    doc.getObject(leg_direct_group.Name).addObject(text_leg2)
    leg_diffuse_group = doc.addObject('App::DocumentObjectGroup',
                                      'Main_Legend_Diffuse')
    leg_diffuse_group.Label = QT_TRANSLATE_NOOP("LBComponents",
                                                "Main_Legend_Diffuse")
    doc.getObject(leg_diffuse_group.Name).addObject(text_leg3)
    FreeCAD.ActiveDocument.recompute()
    return [leg_total_group, #[0]
            leg_direct_group, #[1]
            leg_diffuse_group #[2]
            ]

def modify_main_legends(sky_domes_group = None,
                        position = None,
                        radius_dome = None,
                        modify_position = False,
                        modify_values = False,
                        units = None,
                        metadata = None,
                        ):

    """ Modify main legend position and text size"""

    legend1 = None
    legend2 = None
    legend3 = None
    legend1 = sky_domes_group.Group[0].Group[2].Group[0]
    legend2 = sky_domes_group.Group[1].Group[2].Group[0]
    legend3 = sky_domes_group.Group[2].Group[2].Group[0]
    if modify_position is True:
        legend1.Placement.Base = FreeCAD.Vector(position[0] - radius_dome,
                                                position[1] - radius_dome*1.4,
                                                position[2]
                                                )
        legend1.ViewObject.FontSize = radius_dome/10
        legend2.Placement.Base = FreeCAD.Vector(position[0] + radius_dome*2,
                                                position[1] - radius_dome*1.4,
                                                position[2]
                                                )
        legend2.ViewObject.FontSize = radius_dome/10
        legend3.Placement.Base = FreeCAD.Vector(position[0] + radius_dome*5,
                                                position[1] - radius_dome*1.4,
                                                position[2]
                                                )
        legend3.ViewObject.FontSize = radius_dome/10
    if modify_values is True:
        leg_titles = get_main_legend_texts(units, metadata)
        legend1.Text = leg_titles[0]
        legend2.Text = leg_titles[1]
        legend3.Text = leg_titles[2]

    FreeCAD.ActiveDocument.recompute()


#=================================================
# 8. Header
#=================================================

def get_header(data_type=None,
               unit=None,
               analysis_period=None,
               metadata=None #EPW.metadata (dict)
               ):

    """Get LB header from data, unit, period and metada."""

    header = Header(data_type,
                    unit,
                    analysis_period,
                    metadata
                    )
    return header

#=================================================
# 9. HourlyContinuousCollection
#=================================================

def get_continuous_values(header = None,
                         values = None,
                         timestep = None
                         ):

    """Get LB Hourly Discontinuous Collection
    from header, values, datetimes and timesteps"""

    hcc = HourlyContinuousCollection(header,
                                     values,
                                     )
    values_rate = hcc.to_time_rate_of_change() # kWh to W

    values_rate2 = values_rate.to_unit("kW") # W to kW
    #hcc.interpolate_to_timestep(timestep, cumulative=None)
    values_continuos = values_rate2.interpolate_to_timestep(timestep)
    return values_continuos
