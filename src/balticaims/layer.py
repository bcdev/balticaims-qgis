import itertools
from typing import List

from qgis.core import Qgis, QgsDateTimeRange, QgsRasterLayer, QgsColorRampShader, QgsRasterLayerTemporalProperties, QgsRasterShader, QgsSingleBandPseudoColorRenderer
from qgis.PyQt.QtCore import QDateTime, Qt

from osgeo import gdal, osr

import pandas as pd
import xarray as xr
import numpy as np

from balticaims.utils import get_logger

class DataCubeLayer(QgsRasterLayer):
    """
    A single variable of a data cube represented by a :class:`balticaims.data_cube.GisDataCube`.
    Each time step is represented as a band in a `DatacubeLayer`.

    Adds functionality to :class:`qgis.core.QgsRasterLayer` that are specific it being
    part of a data cube (i.e. time awareness).
    """

    def __init__(self, ds: xr.Dataset, name: str):
        self.ds = ds
        self.logger = get_logger()
        self.var_name = name
        self.vsi_path = self.read_data(ds)
        super().__init__(self.vsi_path, self.var_name, "gdal")


    # TODO name
    def read_data(self, ds):
        self.logger.info(f"Read data: variables are {self.ds.variables.keys()}")
        n_time_steps = len(ds.variables) - len(ds.coords)
        vsi_path = f"/vsimem/{self.name}.tif"
        # TODO use actual data type and do not force to f32 
        driver = gdal.GetDriverByName("GTiff")
        first_time_step = next(iter(ds.variables.keys()))
        height, width = self.ds[first_time_step].shape
        self.logger.info(f"{n_time_steps=}, {height=}, {width=}")
        mem_ds = driver.Create(f"/vsimem/{self.name}.tif", width, height, n_time_steps, gdal.GDT_Float32)

        xres = (self.ds.lon[1] - self.ds.lon[0]).item()
        yres = (self.ds.lat[1] - self.ds.lat[0]).item()

        origin_x = self.ds.lon[0].item() - (xres / 2)
        origin_y = self.ds.lat[0].item() - (yres / 2)

        # TODO Set to ACTUAL epsg
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        mem_ds.SetProjection(srs.ExportToWkt())
        self.logger.info(f"setting projection to {srs.ExportToWkt()}")

        geo_transform = [origin_x, xres, 0, origin_y, 0, yres]
        mem_ds.SetGeoTransform(geo_transform)
        self.logger.info(f"setting geo transform to {geo_transform}")

        band_names = list(self.ds.variables.keys())
        for band_idx in range(1, n_time_steps+1):
            band_name = band_names[band_idx - 1]
            array = self.ds[band_name].values.astype(np.float32)
            self.logger.info(f"{band_idx=}, {band_name=}, {array.shape=}")
            band_dsc = mem_ds.GetRasterBand(band_idx)
            band_dsc.WriteArray(array)
            band_dsc.SetDescription(band_name)
        del mem_ds

        return vsi_path

    def set_single_band_pseudo_color_table(self):
        shader_fn = QgsColorRampShader()
        shader_fn.setColorRampType(Qgis.ShaderInterpolationMethod.Linear)
        shader = QgsRasterShader()
        shader.setRasterShaderFunction(shader_fn)

        # TODO see which band should be set
        self.setRenderer(QgsSingleBandPseudoColorRenderer(self.dataProvider(), 1, shader))
        self.triggerRepaint()

    def set_time_range_per_band(self, time_index: pd.Series) -> bool:
        """
        Set the for each band (representing a single time
        step of a data cube) to range from the an entry in the
        ``time_index`` to the next.
        Assumes that ``time_index`` is sorted in ascending order and that
        ``time_index`` has the same number of entries that the layer
        has time steps (bands).
        """
        dp = self.dataProvider()
        if dp is None:
            self.logger.warning(f"No data provider found for layer {self.id()}")
            return False
        temporal_properties = self.temporalProperties()
        if temporal_properties is None:
            self.logger.warning(f"No temporal properties found for layer {self.id()}")
            return False

        # TODO this skips the last image, also time ranges overlap
        band_count = dp.bandCount()
        ranges: List[QgsDateTimeRange] = []
        if band_count != len(time_index):
            self.logger.warning(f"Band count does not match time index shape for band '{self.id()}'")
            return False
        for (start_idx, end_idx) in itertools.pairwise(range(band_count)):
            start_time = QDateTime.fromString(time_index.iloc[start_idx].isoformat(), Qt.ISODate)
            end_time = QDateTime.fromString(time_index.iloc[end_idx].isoformat(), Qt.ISODate)
            ranges.append(QgsDateTimeRange(start_time, end_time))

        temporal_properties.setMode(QgsRasterLayerTemporalProperties.TemporalMode.FixedRangePerBand)
        temporal_properties.setFixedRangePerBand({i+1: r for i,r in enumerate(ranges)})
        temporal_properties.setIsActive(True)
        self.triggerRepaint()

        return True