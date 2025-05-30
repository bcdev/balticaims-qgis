from dataclasses import dataclass
from typing import Callable 

from qgis.PyQt.QtWidgets import QAction, QMessageBox

from balticaims.data_cube import GisDataCube
from balticaims.xcube_connection import XcubeConnection
from balticaims.utils import get_logger

from balticaims.interfaces.select_dataset import SelectDatasetDialog
from balticaims.interfaces.select_layer import SelectLayerDialog


DEFAULT_MENU="&BalticAIMS"


class XcubePlugin:
    def __init__(self, iface):
        self.logger = get_logger()
        self.iface = iface
        self.actions = {}
        self.connection = None
        self.cubes = {}

    def initGui(self):
        """
        Load the gui (called internally by QGIS)
        """
        self.init_action(
            identifier="setup",
            action_name="Add Datacube",
            #action_name="Setup (Debug)",
            action_fn=self.action_debug,
            object_name="Setup (Debug, on)",
            whats_this="""
                Run complete plugin setup for debugging
            """,
            shortcut="Ctrl+T",
        )

        # self.init_action(
        #     identifier="query dataset",
        #     action_name="Query (Debug)",
        #     action_fn=self.action_query_dialog,
        #     object_name="Query the currently selected data",
        #     whats_this="""
        #         Looks up the currently selected dataset from the dialog
        #     """,
        #     shortcut="Ctrl+U",
        # )

        self.init_action(
            identifier="Load layer",
            action_name="Load layer",
            #action_name="Load layer (Debug)",
            action_fn=self.action_load_layer,
            object_name="Load a layer from a datacube",
            whats_this="""
                Loads the data for a single data cube variable and displays as a raster layer
            """,
            shortcut="Ctrl+U",
        )



    def init_action(
        self,
        identifier: str,
        action_fn: Callable,
        action_name: str = "",
        object_name: str = "",
        whats_this: str = "",
        menu: str = DEFAULT_MENU,
        shortcut: str | None = None,
    ):
        """
        Initialize an action to appear in the plugin > ``menu`` menu.
        """
        action = QAction(action_name, self.iface.mainWindow())
        self.actions[identifier] = action
        action.setObjectName(object_name)
        action.setWhatsThis(whats_this)
        action.triggered.connect(action_fn)
        if shortcut:
            action.setShortcut(shortcut)

        self.iface.addToolBarIcon(action)
        if menu != DEFAULT_MENU:
            raise NotImplementedError("Custom menus are not yet handled in unload")
        self.iface.addPluginToMenu(menu, action)

    def unload(self):
        for action in self.actions.values():
            self.iface.removePluginMenu(DEFAULT_MENU, action)
            self.iface.removeToolBarIcon(action)
        #self.iface.mapCanvas().renderComplete.disconnect(self.renderTest)
    def renderTest(self, painter):
        pass

    def on_zoom_changed(self):
        """
        Handles the loading of the correct pyramid level for the current area.
        """
        # TODO might need to be called also on other events, e.g. panning
        pass

        #################################################################
        # Actions
        #################################################################

    def action_debug(self):
        """
        Run complete setup in one action for debugging
        """
        self.action_connect_to_xcube()
        self.action_load_data_cube()

    def action_connect_to_xcube(self):
        """
        Open a connection to xcube server.
        """
        self.connection = XcubeConnection()
        self.connection.open_store()
        self.logger.info("Xcube: Opened connection to xcube server")

    def action_load_data_cube(self):
        """
        Select a data cube from an existing server connection.
        """
        options = None
        if not self.connection:
            self.logger.info(f"Trying to load data cube without connection, skipping.")
            QMessageBox.information(self, "No connection to xcube", "Cannot load a data cube without an active xcube connection. Please establish a connection first.")
            return

        options = list(self.connection.list_datasets())

        dialog = SelectDatasetDialog(dataset_ids=options)
        if not dialog.exec_():
            self.logger.info("dataset selection not accepted, skipping")
            return
        dataset_id = dialog.selected_dataset
        self.logger.info(f"Dataset selected: {dataset_id}")

        cube = GisDataCube(dataset_id, self.connection)
        self.cubes[dataset_id] = cube

    def action_load_layer(self):
        dialog = SelectLayerDialog(self.cubes)
        if not dialog.exec_():
            self.logger.info("Layer selection not accepted, skipping")
            return
        cube_id = dialog.selected_cube
        variable = dialog.selected_variable
        # TODO for test
        #self.cubes[dataset_id].open_layer(cube.variable_names[0])
        self.cubes[cube_id].open_layer(variable)

    def action_query_dialog(self):
        """
        TODO remove, this is just for debugging purposes
        """
        if not self.dialog:
            self.logger.warning("No dialog present")
            return
        ds_name = self.dialog.datasetComboBox.currentText()
        self.logger.info(f"DS name: '{ds_name}'")

        #################################################################
        # Others
        #################################################################
