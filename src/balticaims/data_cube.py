from datetime import datetime
from typing import Tuple

from qgis.core import QgsProject
import xarray as xr

from balticaims.layer import DataCubeLayer
from balticaims.utils import get_logger
from balticaims.xcube_connection import XcubeConnection


class GisDataCube:
    """
    """
    SKIP_KEYS = {"time", "lat_bnds", "lon_bnds", "lat", "lon"}

    def __init__(self, dataset_id, connection: XcubeConnection) -> None:
        self._connection = connection
        self.dataset_id = dataset_id
        self.ds: xr.Dataset = connection.get_ds(dataset_id)
        self.logger = get_logger()
        self.layers = {}
        self._metadata = DataCubeMetadata(connection.get_metadata(dataset_id))
        self.name = self._metadata.name
        self.variable_names = [v["name"] for v in self._metadata.variables.values()]
        self.logger.info(f"Opened dataset with variables {self.variable_names}")

    def open_layer(self, layer_id: str, time_range:Tuple[datetime, datetime]|None=None):
        self.logger.info(f"Opening layer '{layer_id}'")

        # TODO makes it impossible to change the time selection
        if layer_id in self.layers:
            self.logger.info(f"Layer '{layer_id}' is already open, skipping")

        time_subset = self.time_subset(time_range[0], time_range[1], layer_id)
        layer_ds = time_subset.transpose("time", "lat", "lon").to_dataset(dim="time")
        time_stamps = list(layer_ds.data_vars)
        layer_ds = layer_ds.rename({t: f"{t}: ({layer_id})" for t in time_stamps})
        display_name = f"{self._metadata.variables[layer_id]['name']} ({self._metadata.name})"
        layer = DataCubeLayer(layer_ds, name=layer_id, display_name=display_name)
        self.layers[layer_id] = layer
        self.logger.info(f"Opened layer '{layer_id}'")
        layer.set_time_range_per_band(time_subset.time.to_pandas())

        self.logger.info(f"ids: {[self._metadata.variables.keys()]}")
        variable_metadata = self._metadata.variables.get(layer_id)
        color_ramp_min = variable_metadata.get("colorBarMin", None)
        color_ramp_max = variable_metadata.get("colorBarMax", None)
        layer.set_single_band_pseudo_color_table(color_ramp_min=color_ramp_min, color_ramp_max=color_ramp_max)

        # TODO move to main Plugin
        if layer.isValid():
            QgsProject.instance().addMapLayer(layer)
        else:
            self.logger.warning(f"layer '{layer_id}' not valid")
            self.logger.warning(f"    cause: '{layer.error().message()}'")

    def time_subset(self, start_time: datetime, end_time: datetime, layer_id: str) -> xr.DataArray:
        return self.ds[layer_id].sel(time=slice(start_time, end_time))


class DataCubeMetadata:
    def __init__(self, raw: dict) -> None:
        self.raw = raw
        self.id = raw["id"]
        self.name = raw["title"]

        self.variables = {
            var["name"]: raw["variables"][i] for i, var in enumerate(raw["variables"])
        }
        self.dimensions = {
            dim["name"]: dim for i, dim in enumerate(raw["dimensions"])
        }

    def __getattr__(self, item):
        if item in self.variables:
            return self.variables[item]

        raise AttributeError(f"{item} not in {self.variables}")