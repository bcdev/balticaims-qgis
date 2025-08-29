# main working code of the plugin
import qgis.PyQt.Qt
from qgis.PyQt.QtGui import QKeySequence, QColor
from qgis.PyQt.QtCore import QDateTime
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsRasterLayer, QgsProject, QgsRasterShader, QgsColorRampShader, QgsSingleBandGrayRenderer, QgsContrastEnhancement, QgsDateTimeRange, QgsRasterLayerTemporalProperties
from qgis.core import Qgis, QgsSingleBandPseudoColorRenderer
from qgis.gui import QgsSingleBandPseudoColorRendererWidget
#from qgis.PyQt.QtCore import pyqtRemoveInputHook
import os
import time
from pathlib import Path
import numpy as np
import xarray as xr
from xcube.core.store import new_data_store, get_data_store_params_schema

class XcubePlugin:
    def __init__(self, iface):
        self.iface = iface
        self.layers = []
        self.current_time_step = 1
        self.max_time_step = 5

    def initGui(self):
        self.action = QAction("Load Xcube dataset", self.iface.mainWindow())
        self.action.setObjectName("testAction")
        self.action.setWhatsThis("Configuration for Xcube plugin")
        self.action.setStatusTip("This is a status tip")
        self.action.triggered.connect(self.run_baltic)

        self.action.setShortcut(QKeySequence("Ctrl+R"))

        self.action2 = QAction("Next time step", self.iface.mainWindow())
        self.action2.setObjectName("nextTimeStep")
        self.action2.setWhatsThis("Selects the next time step of the raster layer")
        self.action2.triggered.connect(self.run2)

        self.action2.setShortcut(QKeySequence("Alt+N"))

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&Test plugins", self.action)
        self.iface.addToolBarIcon(self.action2)
        self.iface.addPluginToMenu("&Test plugins", self.action2)

        self.iface.mapCanvas().renderComplete.connect(self.renderTest)

    def unload(self):
        self.iface.removePluginMenu("&Test plugins", self.action)
        self.iface.removeToolBarIcon(self.action)
        self.iface.removeToolBarIcon(self.action2)
        self.iface.mapCanvas().renderComplete.disconnect(self.renderTest)

    def run_baltic(self):
        store = new_data_store(
            "s3",
            root="datasets",  # can also use "pyramids" here
            storage_options={
                "anon": True,
                "client_kwargs": {
                    "endpoint_url": "https://xcube.balticaims.eu/api/s3"
                }
            }
        )
        print("Datasets: ", store.list_data_ids())
        ds = store.open_data(data_id="MV_HROC_L4D_1M.zarr")
        var = "CHL_mean"
        print("Variable: ", var)

        print("time shape:", ds["time"].shape)
        da = ds[var].isel(time=0)

        # Reshape: Move the 'time' dimension into multiple bands
        ds_reshaped = ds[var].transpose("time", "lat", "lon").to_dataset(dim="time")
        print(ds_reshaped)
        # Rename the new variables (bands) for clarity
        ds_reshaped = ds_reshaped.rename({t: f"{var}_{str(t)}" for t in ds_reshaped.variables})
        timestamp = time.perf_counter_ns()
        tmp_dir = Path("/tmp/qgisxarray/")
        tmp_dir.mkdir(exist_ok=True)
        tmp_file = tmp_dir / f"{var}_{timestamp}.tif"
        if not da.rio.crs:
            # TODO check what the actual CRS is
            da.rio.write_crs("EPSG:4326", inplace=True)
        if not ds_reshaped.rio.crs:
            ds_reshaped.rio.write_crs("EPSG:4326", inplace=True)
        print("CRS:", da.rio.crs)
        #da.rio.to_raster(tmp_file)
        ds_reshaped.rio.to_raster(tmp_file)
        print("Successfully created raster")

        tif_layer = QgsRasterLayer(str(tmp_file), var, "gdal")
        if tif_layer.isValid():
            print("Adding tif layer")
            QgsProject.instance().addMapLayer(tif_layer)
            #self.set_raster_symbology(tif_layer)
            self.set_color_table(tif_layer, da)
            self.set_time_per_band(tif_layer, ds)
            self.layers.append(tif_layer)
            print("done")
        else:
            print("Could not add tif layer")

    def run(self):
        print("Xcube: run called!")
        try:
            s = get_data_store_params_schema("s3")
            for (k, v) in s.to_dict().items():
                print(f"{k}\t\t{v}")

            dataset_path = os.getenv("QGISXCUBE_DATASET_PATH")
            print("Path:", dataset_path)
            print("Path exits: ", Path(dataset_path).exists())
            store = new_data_store("file", root=dataset_path, read_only=True, includes="*")
            #store = new_data_store("s3", root="")
            data_ids = store.list_data_ids()
            print(f"{data_ids=}")
            selected_data_id = next(filter(lambda i: i.endswith(".zarr"), data_ids))

            ds = store.open_data(selected_data_id)
            print(ds.variables)
            print("time shape:", ds["time"].shape)
            var = "conc_chl"
            da = ds[var].isel(time=0)

            # Reshape: Move the 'time' dimension into multiple bands
            ds_reshaped = ds[var].transpose("time", "lat", "lon").to_dataset(dim="time")
            print(ds_reshaped)
            # Rename the new variables (bands) for clarity
            ds_reshaped = ds_reshaped.rename({t: f"{var}_{t}" for i, t in enumerate(ds.time.values)})

            # TODO make real temporary directory

            timestamp = time.perf_counter_ns()
            tmp_dir = Path("/tmp/qgisxarray/")
            tmp_dir.mkdir(exist_ok=True)
            tmp_file = tmp_dir / f"{var}_{timestamp}.tif"
            if not da.rio.crs:
                # TODO check what the actual CRS is
                da.rio.write_crs("EPSG:4326", inplace=True)
            if not ds_reshaped.rio.crs:
                ds_reshaped.rio.write_crs("EPSG:4326", inplace=True)
            print("CRS:", da.rio.crs)
            #da.rio.to_raster(tmp_file)
            ds_reshaped.rio.to_raster(tmp_file)
            print("Successfully created raster")


        except Exception as e:
            print("failed xcube initialization: ", e)
            raise e
            return
        #layer = QgsRasterLayer("qgis-xcube-prototype/data/T28PDC_20220713T112119_WVP_20m.jp2", "Xcube raster layer")

        layer_path = Path(dataset_path) / selected_data_id
        print("trying to open layer", layer_path)
        layer = QgsRasterLayer(str(layer_path))
        from osgeo import gdal
        print("Gdal version", gdal.__version__)
        if layer and layer.isValid():
            QgsProject.instance().addMapLayer(layer)
            print("Added layer")
        else:
            print("Failed to load raster layer")

        tif_layer = QgsRasterLayer(str(tmp_file), var, "gdal")
        if tif_layer.isValid():
            print("Adding tif layer")
            QgsProject.instance().addMapLayer(tif_layer)
            #self.set_raster_symbology(tif_layer)
            self.set_color_table(tif_layer, da)
            self.set_time_per_band(tif_layer, ds)
            self.layers.append(tif_layer)
            print("done")
        else:
            print("Could not add tif layer")

        self.set_color_table(layer, ds[var])

    def run2(self):
        print("Run2 called!")
        for layer in self.layers:
            self.set_raster_symbology(layer)

    def set_raster_symbology(self, raster_layer: QgsRasterLayer):
        print("Setting symbology for layer", raster_layer.name(), "\n")
        self._advance_time_step()
        previous_renderer = raster_layer.renderer()
        keep_renderer = isinstance(previous_renderer, QgsSingleBandGrayRenderer)
        if keep_renderer:
            print("Using existing renderer")
            renderer = previous_renderer
        else:
            renderer = QgsSingleBandGrayRenderer(raster_layer.dataProvider(), self.current_time_step)

        print("Got renderer")
        renderer.setGradient(QgsSingleBandGrayRenderer.Gradient.BlackToWhite)
        print("Set gradient")
        contrast_enhancement = QgsContrastEnhancement()
        contrast_enhancement.setContrastEnhancementAlgorithm(QgsContrastEnhancement.StretchToMinimumMaximum)
        raster_layer_array = raster_layer.as_numpy()
        min_val = np.nanmin(raster_layer_array)
        max_val = np.nanmax(raster_layer_array)
        max_val = min(20, max_val)
        print("min: ", min_val)
        print("max: ", max_val)
        contrast_enhancement.setMinimumValue(min_val) # TODO could be nan if there are only nans
        contrast_enhancement.setMaximumValue(max_val)
        print("Set contrast enhancement algorithm of enhancement")
        renderer.setContrastEnhancement(contrast_enhancement)
        print("Set contrast enhancement")
        if not keep_renderer:
            raster_layer.setRenderer(renderer)
        else:
            renderer.setInputBand(self.current_time_step)
        print("Set renderer")
        raster_layer.triggerRepaint()
        print("Triggered repaint")

    def set_time_per_band(self, layer: QgsRasterLayer, ds):
        time_index = ds.time.to_pandas()
        num_bands = layer.dataProvider().bandCount()
        num_time_steps = len(time_index)
        if num_bands != num_time_steps:
            print("WARNING: number of time steps and number of bands do not match")
        end = min(num_bands, num_time_steps) - 1
        assert end > 0, "End not greater than 0"
        ranges: dict[int, QgsDateTimeRange] = dict()
        for i in range(end):
            ts = time_index.iloc[i]
            tsp1 = time_index.iloc[i+1]
            start_datetime = QDateTime.fromString(ts.isoformat(), qgis.PyQt.QtCore.Qt.ISODate)
            end_datetime = QDateTime.fromString(tsp1.isoformat(), qgis.PyQt.QtCore.Qt.ISODate)
            time_range = QgsDateTimeRange(start_datetime, end_datetime)
            ranges[i+1] = time_range

        # set last time range to one day
        start_datetime = QDateTime.fromString(time_index.iloc[-1].isoformat(), qgis.PyQt.QtCore.Qt.ISODate)
        end_datetime = start_datetime.addDays(1)
        time_range = QgsDateTimeRange(start_datetime, end_datetime)
        ranges[len(time_index)] = time_range

        temporal_properties: QgsRasterLayerTemporalProperties = layer.temporalProperties()
        temporal_properties.setMode(QgsRasterLayerTemporalProperties.TemporalMode.FixedRangePerBand)
        temporal_properties.setFixedRangePerBand(ranges)
        temporal_properties.setIsActive(True)

        layer.triggerRepaint()

    def set_color_table(self, layer: QgsRasterLayer, da: xr.DataArray):
        print("Setting color table")
        red = da.attrs.get("color_table_red_values")
        green = da.attrs.get("color_table_green_values")
        blue = da.attrs.get("color_table_blue_values")
        samples = da.attrs.get("color_table_sample_values")
        #samples = [i/(len(samples)-1) * 40 for i in range(len(samples))]
        print("samples ", samples)

        if any([x is None for x in [red, green, blue, samples]]):
            print(da.attrs)
            print("Could not find color attributes. Sticking to gray")
            self.set_raster_symbology(layer)
            return


        shader_fn = QgsColorRampShader()
        shader_fn.setColorRampType(Qgis.ShaderInterpolationMethod.Linear)
        colors = [QColor(r, g, b) for (r, g, b) in zip(red, green, blue)]
        colors = list(reversed(colors))
        colors = [QgsColorRampShader.ColorRampItem(s, color) for (s, color) in zip(samples, colors)]
        print(colors)
        shader_fn.setColorRampItemList(colors)
        shader = QgsRasterShader()
        #shader.setMinimumValue(min(samples))
        #shader.setMaximumValue(max(samples))
        print(f"setting min to {min(samples)}")
        print(f"setting max to {max(samples)}")
        shader.setRasterShaderFunction(shader_fn)

        renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), layer.type(), shader)
        renderer.setClassificationMin(min(samples))
        renderer.setClassificationMax(max(samples))
        renderer.setInputBand(self.current_time_step)

        layer.setRenderer(renderer)
        print("Set color renderer")
        layer.triggerRepaint()

    def _advance_time_step(self):
        self.current_time_step = (self.current_time_step % self.max_time_step) + 1
        print("set current time step:", self.current_time_step)


    def renderTest(self, painter):
        print("Xcube: renderTest called")
