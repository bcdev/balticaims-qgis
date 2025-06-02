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
        self.variable_names = [k for k in self.ds.variables.keys() if k not in self.SKIP_KEYS]
        self.logger.info(f"Opened dataset with variables {self.variable_names}")
        self.layers = {}
        self._metadata = connection.get_metadata(dataset_id)

    def open_layer(self, layer_id: str):
        self.logger.info(f"Opening layer '{layer_id}'")
        if layer_id in self.layers:
            self.logger.info(f"Layer '{layer_id}' is already open, skipping")

        layer_ds = self.ds[layer_id].transpose("time", "lat", "lon").to_dataset(dim="time")
        time_stamps = list(layer_ds.data_vars)
        layer_ds = layer_ds.rename({t: f"{layer_id}_{t}" for t in time_stamps})
        layer = DataCubeLayer(layer_ds, name=layer_id)
        # TODO clean up
        raster_layer = layer
        self.layers[layer_id] = layer
        self.logger.info(f"Opened layer '{layer_id}'")
        layer.set_time_range_per_band(self.ds.time.to_pandas().iloc[:max_time_steps])

        # TODO add proper handling of dataset metadata
        self.logger.info(f"ids: {[d.get('id') for d in self._metadata.get("variables", {})]}")
        variable_metadata = next((d for d in self._metadata.get("variables", {}) if d.get("name") == layer_id), {})
        self.logger.info(f"variable metadata: {variable_metadata}")
        color_ramp_min = variable_metadata.get("colorBarMin", None)
        color_ramp_max = variable_metadata.get("colorBarMax", None)
        # TODO remove
        layer.set_single_band_pseudo_color_table(color_ramp_min=color_ramp_min, color_ramp_max=color_ramp_max)

        # TODO move to main Plugin
        if raster_layer.isValid():
            QgsProject.instance().addMapLayer(raster_layer)
        else:
            self.logger.warning(f"layer '{layer_id}' not valid")
            self.logger.warning(f"    cause: '{raster_layer.error().message()}'")
