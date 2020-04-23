"""
    This file is part of gempy.

    gempy is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    gempy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with gempy.  If not, see <http://www.gnu.org/licenses/>.

    Module with classes and methods to perform implicit regional modelling based on
    the potential field method.
    Tested on Ubuntu 16

    Created on 10/11/2019

    @author: Alex Schaaf, Elisa Heim, Miguel de la Varga
"""

# This is for sphenix to find the packages
# sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from typing import Union, List

import matplotlib.pyplot as plt
# from .vista import Vista
# import gempy as _gempy
import numpy as np
import pandas as pn
from gempy.plot.vista import GemPyToVista

# Keep Alex code hidden until we merge it properly
try:
    import pyvista as pv
    from ._vista import Vista as Vista
    PYVISTA_IMPORT = True
except ImportError:
    PYVISTA_IMPORT = False

from .visualization_2d_pro import Plot2D

try:
    import mplstereonet
    mplstereonet_import = True
except ImportError:
    mplstereonet_import = False


def plot_2d(model, n_axis=None, section_names: list = None,
            cell_number: list = None, direction: list = 'y',
            show_data: Union[bool, list] = True,
            show_results: Union[bool, list] = True,
            show_lith: Union[bool, list] = True,
            show_values: Union[bool, list] = False,
            show_block: Union[bool, list] = False,
            show_scalar: Union[bool, list] = False,
            show_boundaries: Union[bool, list] = True,
            show_topography: Union[bool, list] = False,
            series_n: Union[int, List[int]] = 0,
            **kwargs):
    """"Plot 2-D sections of geomodel.

    Plot cross sections either based on custom section traces or cell number in xyz direction.
    Options to plot lithology block, scalar field or rendered surface lines.
    Input data and topography can be included.

    Args:
        show_block:
        show_values:
        model: Geomodel object with solutions.
        n_axis (int): Subplot axis for multiple sections
        section_names (list): Names of predefined custom section traces
        cell_number (list): Position of the array to plot
        direction (str): Cartesian direction to be plotted (xyz)
        show_data (bool): Show original input data. Defaults to True.
        show_results (bool): If False, override show lith, show_calar, show_values
        show_lith (bool): Show lithological block volumes. Defaults to True.
        show_scalar (bool): Show scalar field isolines. Defaults to False.
        show_boundaries (bool): Show surface boundaries as lines. Defaults to True.
        show_topography (bool): Show topography on plot. Defaults to False.
        series_n (int): number of the scalar field.
         TODO being able to pass a list of int for each axis
        **kwargs:

    Returns:
        (Plot2D) Plot2D object
    """
    if section_names is None and cell_number is None:
        cell_number = ['mid']

    section_names = [] if section_names is None else section_names
    section_names = np.atleast_1d(section_names)
    if cell_number is None:
        cell_number = []
    elif cell_number == 'mid':
        cell_number = ['mid']
    direction = [] if direction is None else direction

    if type(cell_number) != list:
        cell_number = [cell_number]

    if type(direction) != list:
        direction = [direction]

    if n_axis is None:
        n_axis = len(section_names) + len(cell_number)

    if show_results is False:
        show_lith = False
        show_values = False
        show_block = False
        show_scalar = False
        show_boundaries = False

    if type(show_data) is bool:
        show_data = [show_data] * n_axis
    if type(show_lith) is bool:
        show_lith = [show_lith] * n_axis
    if type(show_values) is bool:
        show_values = [show_values] * n_axis
    if type(show_block) is bool:
        show_block = [show_block] * n_axis
    if type(show_scalar) is bool:
        show_scalar = [show_scalar] * n_axis
    if type(show_boundaries) is bool:
        show_boundaries = [show_boundaries] * n_axis
    if type(show_topography) is bool:
        show_topography = [show_topography] * n_axis
    if type(series_n) is int:
        series_n = [series_n] * n_axis

    p = Plot2D(model, **kwargs)
    p.create_figure(**kwargs)
    # init e
    e = 0

    # Check if topography in section names
    # try:
    #     section_names.pop(np.where('topography'==np.array(section_names))[0])
    #
    # except TypeError:
    #     pass

    # is 10 and 10 because in the ax pos is the second digit
    n_columns = 10 if len(section_names) + len(cell_number) < 2 else 20

    for e, sn in enumerate(section_names):
        assert e < 10, 'Reached maximum of axes'

        ax_pos = (int(n_axis / 2) + 1) * 100 + n_columns + e + 1
        # print(ax_pos, '1')
        temp_ax = p.add_section(section_name=sn, ax_pos=ax_pos, **kwargs)
        if show_data[e] is True:
            p.plot_data(temp_ax, section_name=sn, **kwargs)
        if show_lith[e] is True and model.solutions.lith_block.shape[0] != 0:
            p.plot_lith(temp_ax, section_name=sn, **kwargs)
        elif show_values[e] is True and model.solutions.values_matrix.shape[0] != 0:
            p.plot_values(temp_ax, series_n=series_n[e], section_name=sn, **kwargs)
        elif show_block[e] is True and model.solutions.block_matrix.shape[0] != 0:
            p.plot_block(temp_ax, series_n=series_n[e], section_name=sn, **kwargs)
        if show_scalar[e] is True and model.solutions.scalar_field_matrix.shape[0] != 0:
            p.plot_scalar_field(temp_ax, series_n=series_n[e], section_name=sn, **kwargs)
        if show_boundaries[e] is True:
            p.plot_contacts(temp_ax, section_name=sn, **kwargs)
        if show_topography[e] is True:
            p.plot_topography(temp_ax, section_name=sn, **kwargs)

        # If there are section we need to shift one axis for the perpendicular
        e = e + 1

    for e2 in range(len(cell_number)):
        assert (e + e2) < 10, 'Reached maximum of axes'

        ax_pos = (int(n_axis / 2) + 1) * 100 + n_columns + e + e2 + 1
        print(ax_pos)

        temp_ax = p.add_section(cell_number=cell_number[e2],
                                direction=direction[e2], ax_pos=ax_pos)
        if show_data[e + e2] is True:
            p.plot_data(temp_ax, cell_number=cell_number[e2],
                        direction=direction[e2], **kwargs)
        if show_lith[e + e2] is True and model.solutions.lith_block.shape[0] != 0:
            p.plot_lith(temp_ax, cell_number=cell_number[e2],
                        direction=direction[e2], **kwargs)
        elif show_values[e + e2] is True and model.solutions.values_matrix.shape[0] != 0:
            p.plot_values(temp_ax, series_n=series_n[e], cell_number=cell_number[e2],
                          direction=direction[e2], **kwargs)
        elif show_block[e + e2] is True and model.solutions.block_matrix.shape[0] != 0:
            p.plot_block(temp_ax, series_n=series_n[e], cell_number=cell_number[e2],
                         direction=direction[e2], **kwargs)
        if show_scalar[e + e2] is True and model.solutions.scalar_field_matrix.shape[0] != 0:
            p.plot_scalar_field(temp_ax, series_n=series_n[e], cell_number=cell_number[e2],
                                direction=direction[e2], **kwargs)
        if show_boundaries[e + e2] is True:
            p.plot_contacts(temp_ax, cell_number=cell_number[e2],
                            direction=direction[e2], **kwargs)
        if show_topography[e + e2] is True:
            p.plot_topography(temp_ax, cell_number=cell_number[e2],
                              direction=direction[e2], **kwargs)

    return p


def plot_section_traces(model):
    """Plot section traces of section grid in 2-D topview (xy).

    Args:
        model: Geomodel object with solutions.

    Returns:
        (Plot2D) Plot2D object
    """
    pst = plot_2d(model, n_axis=1, section_names=['topography'],
                  show_data=False, show_boundaries=False, show_lith=False)
    pst.plot_section_traces(pst.axes[0], show_data=False)
    return pst


def plot_stereonet(self, litho=None, planes=True, poles=True,
                   single_plots=False,
                   show_density=False):
    if mplstereonet_import is False:
        raise ImportError(
            'mplstereonet package is not installed. No stereographic projection available.')

    from collections import OrderedDict

    if litho is None:
        litho = self.model._orientations.df['surface'].unique()

    if single_plots is False:
        fig, ax = mplstereonet.subplots(figsize=(5, 5))
        df_sub2 = pn.DataFrame()
        for i in litho:
            df_sub2 = df_sub2.append(self.model._orientations.df[
                                         self.model._orientations.df[
                                             'surface'] == i])

    for formation in litho:
        if single_plots:
            fig = plt.figure(figsize=(5, 5))
            ax = fig.add_subplot(111, projection='stereonet')
            ax.set_title(formation, y=1.1)

        # if series_only:
        # df_sub = self.model.orientations.df[self.model.orientations.df['series'] == formation]
        # else:
        df_sub = self.model._orientations.df[
            self.model._orientations.df['surface'] == formation]

        if poles:
            ax.pole(df_sub['azimuth'] - 90, df_sub['dip'], marker='o',
                    markersize=7,
                    markerfacecolor=self._color_lot[formation],
                    markeredgewidth=1.1, markeredgecolor='gray',
                    label=formation + ': ' + 'pole point')
        if planes:
            ax.plane(df_sub['azimuth'] - 90, df_sub['dip'],
                     color=self._color_lot[formation],
                     linewidth=1.5, label=formation + ': ' + 'azimuth/dip')
        if show_density:
            if single_plots:
                ax.density_contourf(df_sub['azimuth'] - 90, df_sub['dip'],
                                    measurement='poles', cmap='viridis',
                                    alpha=.5)
            else:
                ax.density_contourf(df_sub2['azimuth'] - 90, df_sub2['dip'],
                                    measurement='poles', cmap='viridis',
                                    alpha=.5)

        fig.subplots_adjust(top=0.8)
        handles, labels = ax.get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1.9, 1.1))
        ax._grid(True, color='black', alpha=0.25)


def plot_3d(model, plotter_type='background',
            show_data: bool = True,
            show_surfaces: bool = True,
            show_lith: bool = True,
            show_scalar: bool = False,
            show_boundaries: bool = True,
            show_topography: Union[bool, list] = False,
            **kwargs):

    gpv = GemPyToVista(model, plotter_type=plotter_type, **kwargs)
    if show_surfaces and len(model.solutions.vertices) != 0:
        gpv.plot_surfaces()
    if show_data:
        gpv.plot_data()
    if show_topography and model._grid.topography is not None:
        gpv.plot_topography()
    #gpv.p.show()
    return gpv
#
# if PYVISTA_IMPORT and False:
#     def plot_3d(
#             geo_model,
#             show_surfaces: bool = True,
#             show_data: bool = True,
#             show_topography: bool = False,
#             **kwargs,
#     ) -> Vista:
#         """Plot 3-D geomodel.
#
#         Args:
#             geo_model: Geomodel object with solutions.
#             render_surfaces: Render geomodel surfaces. Defaults to True.
#             render_data: Render geomodel input data. Defaults to True.
#             render_topography: Render topography. Defaults to False.
#             real_time: Toggles modyfiable input data and real-time geomodel
#                 updating. Defaults to False.
#
#         Returns:
#             (Vista) GemPy Vista object for plotting.
#         """
#         gpv = Vista(geo_model, **kwargs)
#         gpv.set_bounds()
#         if show_surfaces:
#             gpv.plot_surfaces()
#         if show_data:
#             gpv._plot_surface_points_all()
#             gpv._plot_orientations_all()
#         if show_topography and geo_model.grid.topography is not None:
#             gpv.plot_topography()
#         gpv.show()
#         return gpv
#
#
#     def plot_interactive_3d(
#             geo_model,
#             name: str,
#             render_topography: bool = False,
#             **kwargs,
#     ) -> Vista:
#         """Plot interactive 3-D geomodel with three cross sections in subplots.
#
#         Args:
#             geo_model: Geomodel object with solutions.
#             name (str): Can be either one of the following
#                     'lith' - Lithology id block.
#                     'scalar' - Scalar field block.
#                     'values' - Values matrix block.
#             render_topography: Render topography. Defaults to False.
#             **kwargs:
#
#         Returns:
#             (Vista) GemPy Vista object for plotting.
#         """
#         gpv = Vista(geo_model, plotter_type='background', shape="1|3")
#         gpv.set_bounds()
#         gpv.plot_structured_grid_interactive(name=name, render_topography=render_topography, **kwargs)
#
#         gpv.show()
#         return gpv
