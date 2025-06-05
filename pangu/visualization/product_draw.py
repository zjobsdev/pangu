# -*- coding: utf-8 -*-
# @Author: wqshen
# @Email: wqshen91@gmail.com
# @Date: 2023/7/5 10:10
# @Last Modified by: wqshen


import os
import cmaps
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import PathPatch, Path
from matplotlib.font_manager import FontProperties
from mpl_toolkits.axes_grid1 import ImageGrid
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

cmaps_BlAqGrYeOrReVi200 = cmaps.BlAqGrYeOrReVi200


class ProductPlot:
    _extent = (95, 145, 10, 50)

    @property
    def extent(self):
        return self._extent

    @extent.setter
    def extent(self, ext):
        self._extent = ext

    def basemap(self, nrows=1, ncols=1, figsize=(12, 10), tick_step=2):
        import cartopy.crs as ccrs
        from cartopy.io.shapereader import Reader
        from cartopy.feature import ShapelyFeature

        def customize_axes(ax):
            ax.set_extent(self.extent)
            ax.add_feature(shape_feature_province, zorder=100)

            gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                              linewidth=1, color='gray', alpha=1, linestyle=':')
            gl.top_labels = False
            gl.right_labels = False
            gl.xlines = True
            # gl.xlocator = mticker.FixedLocator(range(95, 146, 2))
            # gl.ylocator = mticker.FixedLocator(range(10, 51, 2))
            gl.xlocator = mticker.FixedLocator(np.arange(90, 150, tick_step))
            gl.ylocator = mticker.FixedLocator(np.arange(0, 60, tick_step))
            gl.xformatter = mticker.FuncFormatter(lambda v, pos: f'{v:g}')
            gl.yformatter = mticker.FuncFormatter(lambda v, pos: f'{v:g}')
            arial = FontProperties(fname=f'{os.path.dirname(__file__)}/fonts/arial.ttf', size=8)
            gl.xlabel_style = {'font': arial, 'size': 14, 'color': 'k'}
            gl.ylabel_style = {'font': arial, 'size': 14, 'color': 'k', 'weight': 'normal'}

        figsize = (figsize[-1] * (ncols / nrows), figsize[-1])
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize,
                                 subplot_kw={'projection': ccrs.PlateCarree()})

        fname = os.path.abspath(f'{os.path.dirname(__file__)}/Country/中华人民共和国.shp')
        geoms = list(Reader(fname).geometries())
        shape_feature_province = ShapelyFeature(geoms,
                                                ccrs.PlateCarree(),
                                                facecolor='none', edgecolor='0.5',
                                                linewidth=1.5)
        if isinstance(axes, np.ndarray):
            for ax in axes.flat:
                customize_axes(ax)
        else:
            customize_axes(axes)

        return fig, axes, geoms

    def seazone_zj(self, ax):
        lines = (
            (119.22, 35),
            (126.32, 35),
            (126.59, 34.37),
            (126.1, 33.22),
            (121.90, 31.7),
            (129.53, 33.22),
            (130.17, 31.23),
            (129.5, 28.0),
            (126, 25.26),
            (121.57, 25.26),
            (119.85, 25.45),
            (121.33, 28),
            (122.09, 29.6),
            (117.3, 23.43),
            (120.82, 22),
            (120.82, 20.76),
            (124, 20.76)
        )

        points = {'黄   海   南   部': (122, 33.8),
                  '东   海   北   部': (123.75, 31.8),
                  '东   海   中   部': (124, 28.8),
                  '东   海   南   部': (123, 26.8),
                  '台 湾 海 峡': (118.25, 24.25),
                  '台 湾 以 东 洋 面': (122, 23.8)}

        ax.plot(*zip(*lines[:5]), color='blue', linestyle='--')
        ax.plot(*zip(*[lines[3], lines[5]]), color='blue', linestyle='--')
        ax.plot(*zip(*[lines[11], lines[7]]), color='blue', linestyle='--')
        ax.plot(*zip(*[lines[12], lines[6]]), color='blue', linestyle='--')
        ax.plot(*zip(*[lines[16], lines[8]]), color='blue', linestyle='--')
        ax.plot(*zip(*lines[5:11]), color='blue', linestyle='--')
        ax.plot(*zip(*lines[13:17]), color='blue', linestyle='--')

        font = FontProperties(fname=f'{os.path.dirname(__file__)}/fonts/msyh.ttf', size=14)
        for k, v in points.items():
            ax.text(*v, k, ha='left', va='center', fontproperties=font, color='blue')

        return ax

    def clip_artist_by_path_patch(self, artist, path):
        """Clip a returned object of matplotlib contour or contourf or imshow or pcolormesh method

        Parameters
        ----------
        artist: matplotlib artist (return by plt.contour, contourf, pcolormesh, imshow, text and so on)
        path: PathPatch
        """
        if isinstance(artist, matplotlib.contour.QuadContourSet):
            [c.set_clip_path(path) for c in artist.collections]
        else:
            artist.set_clip_path(path)
        if hasattr(artist, "labelTexts"):  # From Liu Xianyao (Jiangxi Province Meteo)
            # TODO: Failed
            for txt in artist.labelTexts:
                if not path.contains_point(txt.get_position()):
                    txt.remove()

    def path_patch(self, transform, geoms):
        """Convert list of geometries to matplotlib pathpatch which can be use to clip contour

        Parameters
        ----------
        transform (cartopy.crs): projection of geometry

        Returns
        --------
        (PathPatch), of compound of self._geoms
        """
        from cartopy.mpl import patch

        return PathPatch(
            Path.make_compound_path(*patch.geos_to_path(geoms)),
            transform=transform)

    def clip_artist(self, artist, geoms, ax=None):
        """Clip artist by self._geoms

        Parameters
        ----------
        artist :
            matplotlib artist (return by plt.contour, contourf, pcolormesh, imshow, text and so on)
        ax : Axes, optional
            axes that artist belonging to

        Returns
        -------
        Clipped Artist
        """
        if hasattr(artist, 'ax'):
            patch = self.path_patch(artist.ax.transData, geoms)
        elif hasattr(artist, 'axes'):
            patch = self.path_patch(artist.axes.transData, geoms)
        elif ax is not None:
            patch = self.path_patch(ax.transData, geoms)
        else:
            raise NotImplementedError("You must set argument `ax` explicitly.")
        return self.clip_artist_by_path_patch(artist, patch)

    @staticmethod
    def plot_temperature(dar: xr.DataArray, ax, step=(1, 1), title: str = None, title_right: str = None):
        import cartopy.crs as ccrs

        if ax is None:
            ax = plt.gca()

        cs = ax.contour(
            dar.lon, dar.lat, dar.squeeze().astype('f4'),
            levels=np.arange(5, 45+0.01, 0.5),
            transform=ccrs.PlateCarree(), linewidths=0.1, colors='0.6')
        csf = ax.contourf(
            dar.lon, dar.lat, dar.squeeze().astype('f4'),
            cmap=cmaps_BlAqGrYeOrReVi200, levels=np.arange(5, 45+0.01, 0.5),
            transform=ccrs.PlateCarree(), extend='both')

        cbbox = inset_axes(ax, '5%', '33%', loc='lower right',
                           bbox_transform=ax.transAxes,
                           borderpad=0,
                           bbox_to_anchor=(0, 0.005, 1, 1), )
        [cbbox.spines[k].set_visible(False) for k in cbbox.spines]
        cbbox.tick_params(axis='both', left='off', top='off', right='off', bottom='off',
                          labelleft='off', labeltop='off', labelright='off', labelbottom='off')
        cbbox.minorticks_off()
        cbbox.set_xticks([])
        cbbox.set_yticks([])
        cbbox.set_facecolor([1, 1, 1, 0.95])

        cbaxes = inset_axes(cbbox, width="35%", height="90%", loc='lower left',
                            bbox_transform=cbbox.transAxes,
                            borderpad=0,
                            bbox_to_anchor=(0.05, 0.05, 1, 1),
                            )
        plt.colorbar(csf, cax=cbaxes, orientation='vertical', ticks=np.arange(5, 46, 5),
                     extend='both', extendfrac='auto', extendrect=True, drawedges=False)
        cbaxes.figure.set_facecolor('#ffffff')
        cbaxes.minorticks_off()
        cbaxes.tick_params(direction='in', length=2, labelsize=8 + 2)

        ix, iy = step

        tmax_clip = dar.squeeze()[1:-1:ix, 1:-1:iy]
        font = FontProperties(fname=f'{os.path.dirname(__file__)}/fonts/msyhbd.ttf', size=8)
        if title is not None:
            ax.set_title(title, fontproperties=font, fontsize=12, y=1.01, loc='left')
        if title_right is not None:
            ax.set_title(title_right, fontproperties=font, fontsize=12, y=1.01, loc='right')
        font = FontProperties(fname=f'{os.path.dirname(__file__)}/fonts/arial.ttf', size=12)
        for (i, j), d in np.ndenumerate(tmax_clip):
            d = tmax_clip[i, j].astype('f4')
            if np.isnan(d.values):
                continue
            art = ax.text(float(d.lon), float(d.lat), f'{d.values:.0f}',
                          transform=ccrs.PlateCarree(), fontsize=11,
                          ha='center', va='center',
                          fontproperties=font, zorder=1000)

    @staticmethod
    def float_formatter(x, pos):
        """Remove zero tail float formatter for ticklabels"""
        vtxt = f"{x:.1f}"
        if '.' in vtxt:
            return vtxt.rstrip('0').rstrip('.')
        return vtxt

    @staticmethod
    def plot_rainfall(dar: xr.DataArray, ax, title: str = "", title_right: str = "", acch=24):
        import cartopy.crs as ccrs

        if ax is None:
            ax = plt.gca()

        colors = ('#ffffff', '#a5f28d', '#3dbd3c', '#62b8ff', '#0002fe', '#fd00fd', '#830041')
        if acch == 24:
            levels = (0.1, 10, 25, 50, 100, 250)
        elif acch == 12:
            levels = (1, 5, 15, 30, 70, 140)
        elif acch == 6:
            levels = (1, 4, 13, 25, 60, 120)
        elif acch == 1:
            levels = (1, 3, 10, 20, 50, 70)
        else:
            raise Exception("acch must be 1, 6, 12, 24")

        csf = ax.contourf(
            dar.lon, dar.lat, dar.squeeze().astype('f4'),
            levels=levels, colors=colors,
            transform=ccrs.PlateCarree(), extend='both')

        cbbox = inset_axes(ax, '10%', '33%', loc='lower left',
                           bbox_transform=ax.transAxes,
                           borderpad=0,
                           bbox_to_anchor=(0.9, 0.005, 1, 1), )
        [cbbox.spines[k].set_visible(False) for k in cbbox.spines]
        cbbox.tick_params(axis='both', left='off', top='off', right='off', bottom='off',
                          labelleft='off', labeltop='off', labelright='off', labelbottom='off')
        cbbox.minorticks_off()
        cbbox.set_xticks([])
        cbbox.set_yticks([])
        cbbox.set_facecolor([1, 1, 1, 0.95])

        cbaxes = inset_axes(cbbox, width="2.5%", height="30%", loc='lower left',
                            bbox_transform=ax.transAxes,
                            borderpad=0,
                            bbox_to_anchor=(0.91, 0.015, 1, 1),
                            )

        plt.colorbar(csf, cax=cbaxes, orientation='vertical',
                     extend='both', extendfrac='auto', extendrect=True,
                     format=mticker.FuncFormatter(ProductPlot.float_formatter))

        cbaxes.figure.set_facecolor('#ffffff')
        cbaxes.minorticks_off()
        cbaxes.tick_params(direction='in', length=13, labelsize=12)

        tmax_clip = dar.squeeze().sel(lon=slice(118.1, 122.8), lat=slice(27.1, 31.2))[::3, ::3]
        font = FontProperties(fname=f'{os.path.dirname(__file__)}/fonts/msyh.ttf', size=8)
        ax.set_title(title, fontproperties=font, fontsize=14, y=1.01, loc='left')
        if title_right is not None:
            ax.set_title(title_right, fontproperties=font, fontsize=14, y=1.01, loc='right')
        for (i, j), d in np.ndenumerate(tmax_clip):
            d = tmax_clip[i, j].astype('f4')
            if np.isnan(d.values) or d < 0.1:
                continue
            art = ax.text(float(d.lon), float(d.lat), f'{d.values:.0f}',
                          transform=ccrs.PlateCarree(), fontsize=10,
                          fontproperties=FontProperties('Arial'),
                          zorder=1000)
