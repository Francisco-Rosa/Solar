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

"""This module implements the ladybug components."""

import os
import math
import FreeCAD
import FreeCADGui as Gui
import Draft
from ladybug.color import ColorRange, Colorset
from ladybug.legend import Legend, LegendParameters
from ladybug_geometry.geometry3d import Point3D
from ladybug_radiance.visualize.skydome import SkyDome
from ladybug_radiance.skymatrix import SkyMatrix
from ladybug.epw import EPW
from ladybug.sunpath import Sunpath
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.pointvector import Vector3D
from ladybug.datacollection import HourlyContinuousCollection
from ladybug.header import Header
from ladybug.datatype.energy import Energy

translate = FreeCAD.Qt.translate

LanguagePath = os.path.dirname(__file__) + '/translations'
Gui.addLanguagePath(LanguagePath)
#=================================================
# 0. Globals
#=================================================

RESUL_00 = translate("LBComponents", "Direct Sunlight (Sun hours)")
RESUL_01 = translate("LBComponents", "Radiation (kWh/m²)")
RESUL_02 = translate("LBComponents", "Irradiance (W/m²)")

IMAGE_00 = translate("LBComponents", "None/Reset")
IMAGE_01 = translate("LBComponents", "BW 3D view")
IMAGE_02 = translate("LBComponents", "Color 3D view")
IMAGE_03 = translate("LBComponents", "Render 3D view")

COLORS_00 = translate("LBComponents", "Original Ladybug")
COLORS_01 = translate("LBComponents", "Nuanced Ladybug")
COLORS_02 = translate("LBComponents", "Multi-colored Ladybug")
COLORS_03 = translate("LBComponents", "Ecotect")
COLORS_04 = translate("LBComponents", "View Study")
COLORS_05 = translate("LBComponents", "Shadow Study")
COLORS_06 = translate("LBComponents", "Glare Study")
COLORS_07 = translate("LBComponents", "Annual Comfort")
COLORS_08 = translate("LBComponents", "Thermal Comfort")
COLORS_09 = translate("LBComponents", "Peak Load Balance")
COLORS_10 = translate("LBComponents", "Heat Sensation")
COLORS_11 = translate("LBComponents", "Cold Sensation")
COLORS_12 = translate("LBComponents", "Benefit/Harm")
COLORS_13 = translate("LBComponents", "Harm")
COLORS_14 = translate("LBComponents", "Benefit")
COLORS_15 = translate("LBComponents", "Shade Benefit/Harm")
COLORS_16 = translate("LBComponents", "Shade Harm")
COLORS_17 = translate("LBComponents", "Shade Benefit")
COLORS_18 = translate("LBComponents", "Energy Balance")
COLORS_19 = translate("LBComponents", "Energy Balance w/ Storage")
COLORS_20 = translate("LBComponents", "THERM")
COLORS_21 = translate("LBComponents", "Cloud Cover")
COLORS_22 = translate("LBComponents", "Black to White")
COLORS_23 = translate("LBComponents", "Blue, Green, Red")
COLORS_24 = translate("LBComponents", "Multicolored 2")
COLORS_25 = translate("LBComponents", "Multicolored 3")
COLORS_26 = translate("LBComponents", "OpenStudio Palette")
COLORS_27 = translate("LBComponents", "Cividis (colorblind friendly)")
COLORS_28 = translate("LBComponents", "Viridis (colorblind friendly)")
COLORS_29 = translate("LBComponents", "Parula (colorblind friendly)")
COLORS_30 = translate("LBComponents", "Energy Balance by Face Type")
COLORS_31 = translate("LBComponents", "Peak Cooling by Face Type")
COLORS_32 = translate("LBComponents", "Peak Hating by Face Type")

#=================================================
# 1. Geometries
#=================================================

def convert_face3D(face = None):

    """Get ladybug Face3D from triangular face in FreeCAD."""

    vertices = []
    for v in range(len(face.Vertexes)):
        verticex = face.Vertexes[v].X
        verticey = face.Vertexes[v].Y
        verticez = face.Vertexes[v].Z
        point = Point3D(verticex, verticey, verticez)
        vertices.append(point)
    face3D = Face3D(vertices)
    FreeCAD.ActiveDocument.recompute()
    return face3D

def get_face_centroids(face, point3D = False):

    """Get simple centroids or ladybug Point3D of
       a list of FreeCAD triangular faces."""

    centroids = []
    centroids_lb = []
    center = face.CenterOfMass
    if point3D is True:
        point1 = Point3D(center.x, center.y, center.z)
        centroids_lb.append(point1)
    else:
        point2 = (center.x, center.y, center.z)
        centroids.append(point2)
    FreeCAD.ActiveDocument.recompute()
    if point3D is True:
        return centroids_lb
    else:
        return centroids

def get_face_normals(face, vector3D = False):

    """Get the normal vector for each main face tri."""

    face_normals = []
    face_normals_lb = []
    normal = face.normalAt(0.5, 0.5) # center of the triangule
    if vector3D is True:
        normal_lb = Vector3D(normal.x, normal.y, normal.z)
        face_normals_lb.append(normal_lb)
        FreeCAD.ActiveDocument.recompute()
        return face_normals_lb
    else:
        normal = (normal.x, normal.y, normal.z)
        face_normals.append(normal)
        FreeCAD.ActiveDocument.recompute()
        return face_normals

def get_lb_centroids_normals(faces_tris = None):

    """Get ladybug centroids and normals."""

    centroids_lb = []
    face_normals_lb = []
    for f in range(len(faces_tris)):
        face = faces_tris[f]
        centroids = get_face_centroids(face, point3D = True)
        face_normals = get_face_normals(face, vector3D = True)
        centroids_lb.extend(centroids)
        face_normals_lb.extend(face_normals)
    FreeCAD.ActiveDocument.recompute()
    return [centroids_lb,  # [0]
            face_normals_lb] # [1]

#=================================================
# 2. Sun path and direct sunlight study
#=================================================

def get_sun_lb_vectors(latitude = None,
                      longitude = None,
                      timezone = None,
                      north_angle = 0,
                      #day_light_saving = None, #period
                      period = None):

    """Get a list of location ladybug sun Vector3D (lb_vectors) for a period in FreeCAD."""

    sp = Sunpath(latitude,
                 longitude,
                 timezone,
                 north_angle,
                 #day_light_saving
                 )
    dts = period.datetimes
    sun_vecs = []
    for dt in dts:
        sun = sp.calculate_sun_from_date_time(dt)
        if -sun.sun_vector.z > 0:
            sun_vec = Vector3D(-sun.sun_vector.x,
                               -sun.sun_vector.y,
                               -sun.sun_vector.z
                               )
            sun_vecs.append(sun_vec)
    FreeCAD.ActiveDocument.recompute()
    return sun_vecs

def convert_lb_vectors(lb_vectors = None):

    """convert ladybug vectors to FreeCAD vectors"""

    vectors = []
    for i in range(len(lb_vectors)):
        vector = (lb_vectors[i][0],
                  lb_vectors[i][1],
                  lb_vectors[i][2]
                  )
        vectors.append(vector)
    return vectors

def calculate_sun_hours(inter_matrix_bools = None,
                        timesteps = 1
                        ):
    sun_hours_results = []
    for point_data in inter_matrix_bools:
        visible_timesteps = sum(point_data)
        # Convert time steps to hours
        sun_hours = visible_timesteps / int(timesteps)
        sun_hours_results.append(float(sun_hours))
    return sun_hours_results

#=================================================
# 3. Sky matrix
#=================================================

def get_sky_matrix_values(epw_path = "",
                          period = None,
                          high_density = False,
                          timestep = 1,
                          ground_reflectance = 0.2
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
        sky_matrix.ground_reflectance = ground_reflectance
    if timestep > 1:
        dnr_values = [epw.direct_normal_radiation[int(hoy % 8760)] for hoy in hoys] # timestep = 1
        dhr_values = [epw.diffuse_horizontal_radiation[int(hoy % 8760)] for hoy in hoys] # timestep = 1
        #get header
        data_type = Energy(name = "Energy")
        unit = "kWh"
        analysis_period=period
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
                                  #north = 0,
                                  high_density = high_density,
                                  ground_reflectance = ground_reflectance
                                  )
    metadata = sky_matrix.metadata #tuple
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
# 4. Sky dome
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
    try:
        sky_dome_obj = SkyDome(sky_matrix = sky_matrix,
                               plot_irradiance = plot_irradiance)
                               # (If True, Radiance must be installed)
    except Exception:
        FreeCAD.Console.PrintMessage(translate("LBComponents",
            "To get irradiance values, it is necessary \n"
            "to install Radiance in your machine.\n"))
        return
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
def get_sky_matrix_dome_values(epw_path = "",
                        period = None,
                        high_density = False,
                        plot_irradiance = False,
                        timestep = 1,
                        center_vectors = False,
                        ground_reflectance = 0.2
                        ):

    """Obtains the necessary data (epw file, analysis period, model,
    total, directs and diffuse values and returns the sky domes values
    (total, direct, diffuse and vectors values), and legend parameters."""

    #total_values, direct_values, diffuse_values
    sky_matrix_values = get_sky_matrix_values(epw_path,
                              period,
                              high_density,
                              timestep = timestep,
                              ground_reflectance = ground_reflectance
                              )
    # Irradiance
    if plot_irradiance is True:
        try:
            sky_dome_obj = get_sky_dome_values(
                                sky_matrix = sky_matrix_values[0],
                                plot_irradiance = True,
                                )
            total_values = sky_dome_obj[1]
            direct_values = sky_dome_obj[2]
            diffuse_values = sky_dome_obj[3]
        except Exception:
            FreeCAD.Console.PrintMessage(
                "get sky matrix dome values: " + translate("LBComponents",
                "To get irradiance values, Radiance software must be \n"
                "installed in your machine.\n"))
            return
    else:
        total_values = sky_matrix_values[1]
        direct_values = sky_matrix_values[2]
        diffuse_values = sky_matrix_values[3]
        sky_dome_obj = get_sky_dome_values(
                        sky_matrix = sky_matrix_values[0])
    #vector values
    vector_values = []
    vectors = sky_dome_obj[0].patch_vectors
    for i in range(len(vectors)):
        vector = (vectors[i][0],
                  vectors[i][1],
                  vectors[i][2])
        vector_values.append(vector)
    metadata = []
    metadata = sky_matrix_values[4]
    metadata_str = []
    for i in range(len(metadata)):
        data = metadata[i]
        str_data = str(data)
        metadata_str.append(str_data)
    FreeCAD.ActiveDocument.recompute()
    return [total_values,# [0]
            direct_values,# [1]
            diffuse_values,# [2]
            vector_values,# [3]
            metadata_str,# [4]
            ]

#=================================================
# 5. Color range and others
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
    #usage: color_range.domain = [min(domain), max(domain)]
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
    put_obj_group(obj = analysis_clone,
                  group = analysis_group,
                  )
    FreeCAD.ActiveDocument.recompute()
    return analysis_clone

def apply_color_faces(obj = None,
                      face_colors = None,
                      transparency = 0):

    """Apply color to each face
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
# 6. Compass
#=================================================

def get_compass_group(center = None,
                radius = None,
                north = None,
                variation_angle = None,
                total_group = None,
                direct_group = None,
                diffuse_group = None,
                deltx = None
                ):

    """Create compass and manage their groups"""

    doc = FreeCAD.ActiveDocument
    ## Create compass and values
    angles_compas = []
    #angles_compas_leg = []
    compass_list = []
    total_text_list = []
    direct_text_list = []
    diffuse_text_list = []
    max_angle = 360
    n_angles = int(max_angle / variation_angle)
    # compass circles
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
    #displacement
    if deltx == None:
        deltx2 = radius*3
        deltx3 = radius*6
    else:
        deltx2 = deltx
        deltx3 = 2*deltx
    delty = - radius/50
    # compass lines and texts
    for i in range(n_angles):
        angles_compas = variation_angle * i
        # compass lines
        angle = (90 - float(north)) - angles_compas # north y-axis, clockwise
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
        # compass texts
        angle_leg = str(angles_compas)
        scale = 1.0
        font = "Arial"
        if angles_compas == 0.0:
            angle_leg = translate("LBComponents", "N")
            scale = 2.0
            font = "ArialBlack"
            point_n = points[0]
        elif angles_compas == 90.0:
            angle_leg = translate("LBComponents", "E")
            scale = 2.0
            font = "ArialBlack"
            point_e = points[0]
        elif angles_compas == 180.0:
            angle_leg = translate("LBComponents", "S")
            scale = 2.0
            font = "ArialBlack"
        elif angles_compas == 270.0:
            angle_leg = translate("LBComponents", "W")
            scale = 2.0
            font = "ArialBlack"
            point_w = points[0]
        # total compass text positions
        x3 = radius_compas * math.cos(math.radians(angle)) * 1.15
        y3 = radius_compas * math.sin(math.radians(angle)) * 1.15
        pl1.Base = FreeCAD.Vector(x3 - radius/20 + center[0],
                                  y3 + delty + center[1],
                                  center[2])
        # total compass text
        text_compas_leg1 = Draft.make_text([angle_leg],
                                            placement=pl1,
                                            screen=None,
                                            height=radius/15,
                                            line_spacing=None
                                           )
        text_compas_leg1.Label = str(angle_leg) + "_"
        text_compas_leg1.ViewObject.FontName = font
        text_compas_leg1.ViewObject.ScaleMultiplier = scale
        total_text_list.append(text_compas_leg1)
        # direct compass text positions
        pl2.Base = FreeCAD.Vector(x3 - radius/20 + deltx2 + center[0],
                                  y3 + delty + center[1],
                                  center[2])
        if direct_group != None or diffuse_group != None:
            # direct compass text
            text_compas_leg2 = Draft.make_text([angle_leg],
                                                placement=pl2,
                                                screen=None,
                                                height=radius/15,
                                                line_spacing=None
                                               )
            text_compas_leg2.Label = str(angle_leg) + "_"
            text_compas_leg2.ViewObject.FontName = font
            text_compas_leg2.ViewObject.ScaleMultiplier = scale
            direct_text_list.append(text_compas_leg2)
            # diffuse compass text positions
            pl3.Base = FreeCAD.Vector(x3 - radius/20 + deltx3 + center[0],
                                      y3 + delty + center[1],
                                      center[2])
            # diffuse compass text
            text_compas_leg3 = Draft.make_text([angle_leg],
                                                placement=pl3,
                                                screen=None,
                                                height=radius/15,
                                                line_spacing=None
                                                )
            text_compas_leg3.Label = str(angle_leg) + "_"
            text_compas_leg3.ViewObject.FontName = font
            text_compas_leg3.ViewObject.ScaleMultiplier = scale
            diffuse_text_list.append(text_compas_leg3)
    # create a north triangle
    if deltx is not None:
        points = [point_n, point_e, point_w]
        triangle = Draft.make_wire(points,
                                    placement=pl,
                                    closed=True,
                                    face=True,
                                    support=None)
        compass_list.append(triangle)
    direct_compass_group = None
    diffuse_compass_group = None
    direct_compass = None
    diffuse_compass = None
    # Total compass - compound
    total_compass = doc.addObject("Part::Compound",
                                  "Total_compass_circles")
    total_compass.Label = translate("LBComponents",
                                            "Total compass circles")
    doc.getObject(total_compass.Name).Links = compass_list
    doc.getObject(total_group.Name).addObject(total_compass)
    if direct_group != None or diffuse_group != None:
        # Compass direct - clone
        direct_compass = Draft.make_clone(doc.getObject(total_compass.Name))
        doc.getObject(direct_compass.Name).Placement.Base = (deltx2, 0,0)
        doc.getObject(direct_compass.Name).Label = translate(
                                                   "LBComponents",
                                                   "Direct compass circles")
        doc.getObject(direct_group.Name).addObject(direct_compass)
        # Compass diffuse - clone
        diffuse_compass = Draft.make_clone(doc.getObject(total_compass.Name))
        doc.getObject(diffuse_compass.Name).Placement.Base = (deltx3, 0,0)
        doc.getObject(diffuse_compass.Name).Label = translate(
                                                    "LBComponents",
                                                    "Diffuse compass circles")
        doc.getObject(diffuse_group.Name).addObject(diffuse_compass)
    ## managing groups
    # Create compass groups
    total_compass_group = create_group(group_name = "Total_Compass_Group",
                           group_label = translate("LBComponents",
                                                    "Total Compass Group")
                            )
    # Create compass legend groups
    total_compass_leg_group = create_group(group_name = "Total_Compass_Legend_Group",
                           group_label = translate("LBComponents",
                                                    "Total Compass Legend Group")
                            )
    if direct_group != None or diffuse_group != None:
        direct_compass_group = create_group(group_name = "Direct_Compass_Group",
                               group_label = translate("LBComponents",
                                                        "Direct Compass Group")
                                )
        diffuse_compass_group = create_group(group_name = "Diffuse_Compass_Group",
                               group_label = translate("LBComponents",
                                                        "Diffuse Compass Group")
                                )
        # Create compass legend groups
        direct_compass_leg_group = create_group(group_name = "Direct_Compass_Legend_Group",
                               group_label = translate("LBComponents",
                                                        "Direct Compass Legend Group")
                                )
        diffuse_compass_leg_group = create_group(group_name = "Diffuse_Compass_Legend_Group",
                               group_label = translate("LBComponents",
                                                        "Diffuse Compass Legend Group")
                                )
    #Compasses to their groups
    put_obj_group(obj = total_compass,
                  group = total_compass_group,
                  )
    # Text groups to their groups
    put_group1_in_group2(group1 = total_compass_leg_group,
                        group2 = total_compass_group,
                        )
    # Texts to legend groups
    for i in range(n_angles):
        doc.getObject(total_compass_leg_group.Name).addObject(total_text_list[i])
        if direct_group != None or diffuse_group != None:
            doc.getObject(direct_compass_leg_group.Name).addObject(direct_text_list[i])
            doc.getObject(diffuse_compass_leg_group.Name).addObject(diffuse_text_list[i])
            # Compasses to their groups
            put_obj_group(obj = direct_compass,
                          group = direct_compass_group,
                          )
            put_obj_group(obj = diffuse_compass,
                          group = diffuse_compass_group,
                          )
            # Text groups to their groups
            put_group1_in_group2(group1 = direct_compass_leg_group,
                                group2 = direct_compass_group,
                                )
            put_group1_in_group2(group1 = diffuse_compass_leg_group,
                                group2 = diffuse_compass_group,
                                )
    FreeCAD.ActiveDocument.recompute()
    return [total_compass_group, #[0]
            direct_compass_group, #[1]
            diffuse_compass_group, #[2]
            total_compass, #[3]
            direct_compass, #[4]
            diffuse_compass #[5]
           ]

def modify_compass(center = None,
                   radius = None,
                   north = None,
                   variation_angle = None,
                   sky_domes_group = None,
                   sun_analysis_group = None,
                   deltx = None
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
    text_list1 = []
    text_list2 = []
    text_list3 = []

    if sky_domes_group is not None:
        circ_lines_list = sky_domes_group.Group[0].Group[1].Group[0].Links
        text_list1 = sky_domes_group.Group[0].Group[1].Group[1].Group
        text_list2 = sky_domes_group.Group[1].Group[1].Group[1].Group
        text_list3 = sky_domes_group.Group[2].Group[1].Group[1].Group
        compass_original = sky_domes_group.Group[0].Group[1].Group[0]
        compass_clone1 = sky_domes_group.Group[1].Group[1].Group[0]
        compass_clone2 = sky_domes_group.Group[2].Group[1].Group[0]
        deltx2 = radius*3
        deltx3 = radius*6
    elif sun_analysis_group is not None and deltx is not None:
        circ_lines_list1 = sun_analysis_group.Group[1].Group[1].Group[1].Group[0].Links
        compass_triangle = circ_lines_list1[-1]
        compass_triangle.Points
        circ_lines_list = circ_lines_list1[0:-1]
        text_list1 = sun_analysis_group.Group[1].Group[1].Group[1].Group[1].Group
        compass_original = sun_analysis_group.Group[1].Group[1].Group[1].Group[0]
        deltx2 = deltx
        deltx3 = 2*deltx
        try:
            text_list2 = sun_analysis_group.Group[2].Group[1].Group[1].Group[1].Group
            text_list3 = sun_analysis_group.Group[3].Group[1].Group[1].Group[1].Group
            compass_clone1 = sun_analysis_group.Group[2].Group[1].Group[1].Group[0]
            compass_clone2 = sun_analysis_group.Group[3].Group[1].Group[1].Group[0]
        except:
            pass
    else:
        FreeCAD.Console.PrintMessage(
            "Modify compass: Could not get existing compass! \n")
        return
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
        try:
            text2 = text_list2[i]
            text2.Placement.Base = FreeCAD.Vector(x_text1 + deltx2,
                                                  y_text1,
                                                  z_text1
                                                  )
            text2.ViewObject.FontSize = radius/15
            text3 = text_list3[i]
            text3.Placement.Base = FreeCAD.Vector(x_text1 + deltx3,
                                                  y_text1,
                                                  z_text1
                                                  )
            text3.ViewObject.FontSize = radius/15
        except:
            pass
        # save triangle points
        if angles_compas[i] == 0.0:
            point_n = line.Start
        elif angles_compas[i] == 90.0:
            point_e = line.Start
        elif angles_compas[i] == 270.0:
            point_w = line.Start
    try:
        points = [point_e, point_w, point_n]
        # update a north triangle
        if sun_analysis_group is not None and deltx is not None:
            compass_triangle.Placement.Base = FreeCAD.Vector(0.0, 0.0, 0.0)
            compass_triangle.Points = points
    except:
        pass
    FreeCAD.ActiveDocument.recompute()
    try:
        # Update distance between original and clone1
        base_ori = compass_original.Placement.Base # original
        x_ori = base_ori[0]
        y_ori = base_ori[1]
        z_ori = base_ori[2]
        x1_fin = x_ori + deltx2
        pl1 = FreeCAD.Placement()
        pl1.Base = FreeCAD.Vector(x1_fin, y_ori, z_ori)
        compass_clone1.Placement = pl1
        # Update distance between original and clone2
        x2_fin = x_ori + deltx3
        pl2 = FreeCAD.Placement()
        pl2.Base = FreeCAD.Vector(x2_fin, y_ori, z_ori)
        compass_clone2.Placement = pl2
    except:
        pass
    FreeCAD.ActiveDocument.recompute()

#=================================================
# 7. Legend bar
#=================================================

def get_modify_legend_bar(bar_obj = None,
                          text_leg_group = None,
                          title = "",
                          values = None,
                          position = (0, 0, 0),
                          seg_height = 1000,
                          seg_width = 1000,
                          seg_count = 11,
                          color_leg_set = 0,
                          min = 0.0
                          ):

    """Get or modify legend using ladybug color range
    and legend parameters. Usage:
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
                    leg_par(min = min,
                    segment_count = seg_count,
                    colors = color_scheme[color_leg_set])
                    )
    leg_par.segment_height = seg_height
    leg_par.segment_width = seg_width

    # get bar
    bar = None
    leg_bar_group = None
    if bar_obj is None:
        #create a bar
        #first rect
        pl=FreeCAD.Placement()
        pl.Base = FreeCAD.Vector(position)
        rect = Draft.make_rectangle(length = seg_width,
                                    height = seg_height,
                                    placement = pl,
                                    face = True,
                                    support = None)
        #array
        bar_new = Draft.make_ortho_array(rect,
                                    v_y = FreeCAD.Vector(0.0, seg_height, 0.0),
                                    n_x = 1,
                                    n_y = seg_count,
                                    n_z = 1,
                                    use_link = False
                                    )
        bar_new.Label = translate("LBComponents",
                                          "Legend bar")
        bar = bar_new
        # create legend bar groups
        leg_bar_group = create_group(group_name = "Legend_Bar_Group",
                         group_label = translate("LBComponents",
                                                     "Legend Bar Group"),
                         )
        put_obj_group(obj = bar_new,
                      group = leg_bar_group,
                      )
        # create legend text group
        leg_text_group = create_group(group_name = "Legend_bar_text",
                         group_label = translate("LBComponents",
                         "Legend bar text"),
                         )
    else:
        #update bar
        bar_obj.Base.Length = seg_width
        bar_obj.Base.Height = seg_height
        bar_obj.Base.Placement.Base = FreeCAD.Vector(position)
        bar_obj.IntervalY.y = seg_height
        bar_obj.NumberY = seg_count
        bar = bar_obj
    # apply the corresponding colors
    color_rgb_leg = legend.segment_colors
    bar_colors = []
    for c in range(len(color_rgb_leg)):
        color = color_rgb_leg[c]
        color_rgb = (color[0], color[1], color[2])
        bar_colors.append(color_rgb)
    apply_color_faces(obj = bar,
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
    #print(F"lenleg_text: {len(leg_text)}")
    #print(F"lentext_location: {len(text_location)}")

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
        #create texts
        text_title = Draft.make_text(text1,
                                    placement = pl_bar1,
                                    screen = None,
                                    height = seg_width/3,
                                    line_spacing = None
                                    )
        text_title.Label = text1 + "_"
        if leg_text_deleted == False:
            doc.getObject(leg_text_group.Name).addObject(text_title)
        else:
            doc.getObject(text_leg_group.Name).addObject(text_title)
    else:
        #update texts
        text_title = text_leg_group.Group[0]
        text_title.Text = text1
        text_title.Placement.Base = pos1
        text_title.ViewObject.FontSize = seg_width/3
    #get positions and texts
    for n in range(len(leg_text)):
        x2 = text_location[n].o.x + position[0]
        y2 = text_location[n].o.y + position[1]
        z2 = text_location[n].o.z + position[2]
        pos2 = (x2, y2, z2)
        text2 = leg_text[n]
        pl_bar2 = FreeCAD.Placement()
        pl_bar2.Base = pos2
        if bar_obj is None or leg_text_deleted == True:
            #create text
            text_value = Draft.make_text(text2,
                                        placement = pl_bar2,
                                        screen = None,
                                        height = seg_width/3,
                                        line_spacing=None
                                        )
            if leg_text_deleted == False:
                doc.getObject(leg_text_group.Name).addObject(text_value)
            else:
                doc.getObject(text_leg_group.Name).addObject(text_value)
        else:
            #update text
            text_value = text_leg_group.Group[n + 1]
            text_value.Text = text2
            text_value.Placement.Base = pos2
            text_value.ViewObject.FontSize = seg_width/3
        text_value.Label = text2 + "_"
    if bar_obj is None:
        doc.getObject(leg_bar_group.Name).addObject(leg_text_group)
    FreeCAD.ActiveDocument.recompute()
    return [leg_bar_group, #[0]
            color_rgb_leg #[1]
            ]

#=================================================
# 8. Main legend
#=================================================

def get_metadata(epw_path = "", period = None):

    """Get metadata from epw and period"""

    metadata = ["None", "None"]
    start_day_name = str(period.st_day)
    start_month_name = period.MONTHNAMES[period.st_month]
    start_hour_name = get_time_format(float_time = period.st_hour)
    end_day_name = str(period.end_day)
    end_month_name = period.MONTHNAMES[period.end_month]
    end_hour_name = get_time_format(float_time = period.end_hour)
    period_str1 = f"{start_day_name} {start_month_name} {start_hour_name}"
    metadata.append(period_str1)
    period_str2 = f"{end_day_name} {end_month_name} {end_hour_name}"
    metadata.append(period_str2)
    epw = EPW(epw_path)
    epw_metadata = epw.metadata
    source_name = epw_metadata["source"]
    source_str = translate("LBComponents",
                           "Source: {}").format(source_name)
    metadata.append(source_str)
    country_name = epw_metadata["country"]
    country_str = translate("LBComponents",
                            "Country: {}").format(country_name)
    metadata.append(country_str)
    city_name = epw_metadata["city"]
    city_str = translate("LBComponents",
                         "City: {}").format(city_name)
    metadata.append(city_str)
    time_zone_name = epw_metadata["time-zone"]
    time_zone_str = translate("LBComponents",
                              "Time-zone: {}").format(time_zone_name)
    metadata.append(time_zone_str)
    return metadata

def get_time_format(float_time = 0.0):
    hours = int(float_time)
    minutes = round((float_time - hours) * 60)
    time_format = f'{int(hours):0>2}:{int(minutes):0>2}'
    return time_format

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
    title_leg1 = translate(
                 "LBComponents", "Total" + " " + "{}").format(units)
    text_total = [title_leg1, period_leg, city_leg,
                  country_leg, time_zone_leg, source_leg]
    # Direct title
    title_leg2 = translate(
                 "LBComponents", "Direct" + " " + "{}").format(units)
    text_direct = [title_leg2, period_leg, city_leg,
                   country_leg, time_zone_leg, source_leg]
    # Diffuse title
    title_leg3 = translate(
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

    #get texts
    leg_titles = get_main_legend_texts(units, metadata)
    if pos1 is not None:
        text_total = leg_titles[0]
        # main legend total positions
        pl1_leg = FreeCAD.Placement()
        pl1_leg.Base = FreeCAD.Vector(pos1)
        # main legend total texts
        text_leg1 = Draft.make_text(text_total,
                                    placement=pl1_leg,
                                    screen=None,
                                    height=text_high,
                                    line_spacing=1.2
                                    )
        text_leg1.Label = translate("LBComponents",
                                    "Total legend")
        #create groups and put main legends into correspondent ones
        leg_total_group = create_group(group_name = "Total_Legend_Group",
                                       group_label = translate("LBComponents",
                                                     "Total Legend Group"),
                                       )
        put_obj_group(obj = text_leg1,
                      group = leg_total_group,
                       )
    else:
        leg_total_group = None
    if pos2 is not None and pos3 is not None:
        #get texts
        text_direct = leg_titles[1]
        text_diffuse = leg_titles[2]
        # main legend direct and diffuse positions
        pl2_leg = FreeCAD.Placement()
        pl2_leg.Base = FreeCAD.Vector(pos2)
        pl3_leg = FreeCAD.Placement()
        pl3_leg.Base = FreeCAD.Vector(pos3)
        # main legend texts
        text_leg2 = Draft.make_text(text_direct,
                                    placement=pl2_leg,
                                    screen=None,
                                    height=text_high,
                                    line_spacing=1.2
                                    )
        text_leg2.Label = translate("LBComponents",
                                    "Direct legend")
        text_leg3 = Draft.make_text(text_diffuse, placement=pl3_leg,
                                    screen=None, height=text_high,
                                    line_spacing=1.2
                                    )
        text_leg3.Label = translate("LBComponents",
                                    "Diffuse legend")
        #create groups and put main legends into correspondent ones
        leg_direct_group = create_group(group_name = "Direct_Legend_Group",
                                       group_label = translate("LBComponents",
                                                     "Direct Legend Group"),
                                       )
        put_obj_group(obj = text_leg2,
                      group = leg_direct_group,
                       )
        leg_diffuse_group = create_group(group_name = "Diffuse Legend Group",
                                       group_label = translate("LBComponents",
                                                     "Diffuse Legend Group"),
                                       )
        put_obj_group(obj = text_leg3,
                      group = leg_diffuse_group,
                       )
    else:
        leg_direct_group = None
        leg_diffuse_group = None
    FreeCAD.ActiveDocument.recompute()
    return [leg_total_group, #[0]
            leg_direct_group, #[1]
            leg_diffuse_group #[2]
            ]

def modify_main_legends(main_leg1 = None,
                         main_leg2 = None,
                         main_leg3 = None,
                         pos1 = None,
                         pos2 = None,
                         pos3 = None,
                         unit = None,
                         metadata = None,
                         modify_position = False,
                         modify_values = False,
                         font_size = None
                         ):

    """ Modify main legend position and text size
    - Sun analysis"""
    if modify_position is True:
        main_leg1.Placement.Base = FreeCAD.Vector(pos1)
        main_leg1.ViewObject.FontSize = font_size
    if modify_values is True:
        leg_titles = get_main_legend_texts(unit, metadata)
        main_leg1.Text = leg_titles[0]
    if main_leg2 is not None and main_leg3 is not None:
        if modify_position is True:
            main_leg2.Placement.Base = FreeCAD.Vector(pos2)
            main_leg2.ViewObject.FontSize = font_size
            main_leg3.Placement.Base = FreeCAD.Vector(pos3)
            main_leg3.ViewObject.FontSize = font_size
        if modify_values is True:
            main_leg2.Text = leg_titles[1]
            main_leg3.Text = leg_titles[2]
    FreeCAD.ActiveDocument.recompute()

#=================================================
# 9. Header
#=================================================

def get_header(data_type=None,
               unit=None,
               analysis_period=None,
               metadata=None #EPW.metadata (dict)
               ):

    """Get LB header from data, unit, period and metada
    data_type = Energy(name = "Energy")
    unit = "kWh"
    data_type = Energy(name = "Irradiation")
    unit = "Wh/m²"
    """

    header = Header(data_type,
                    unit,
                    analysis_period,
                    metadata
                    )
    return header

#=================================================
# 10. HourlyContinuousCollection
#=================================================

def get_continuous_values(header = None,
                         values = None,
                         timestep = None
                         ):

    """Get LB Hourly Continuous Collection
    from header, values, datetimes and timesteps"""

    #usage: HourlyContinuousCollection(header, values)
    hcc = HourlyContinuousCollection(header,
                                     values,
                                     )
    #hcc.to_time_rate_of_change()
    values_rate = hcc.to_time_rate_of_change() # kWh to W
    values_rate2 = values_rate.to_unit("kW") # W to kW
    #hcc.interpolate_to_timestep(timestep, cumulative=None)
    values_continuos = values_rate2.interpolate_to_timestep(timestep)
    return values_continuos

#=================================================
# 11. Groups
#=================================================

def create_group(group_name = "",
                 group_label = "",
                 ):
    doc = FreeCAD.ActiveDocument
    if group_name == "":
        group = doc.addObject('App::DocumentObjectGroup',
                            "Group")
    else:
        group = doc.addObject('App::DocumentObjectGroup',
                            group_name)
    group.Label = group_label
    FreeCAD.ActiveDocument.recompute()
    return group

def put_obj_group(obj = None,
                  group = None,
                  ):
    doc = FreeCAD.ActiveDocument
    doc.getObject(group.Name).addObject(obj)
    FreeCAD.ActiveDocument.recompute()

def put_group1_in_group2(group1 = None,
                    group2 = None,
                    ):
    doc = FreeCAD.ActiveDocument
    doc.getObject(group2.Name).addObject(group1)
    FreeCAD.ActiveDocument.recompute()
