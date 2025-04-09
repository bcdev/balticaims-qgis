from typing import Mapping

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from balticaims.data_cube import GisDataCube
from balticaims.utils import get_logger

class SelectLayerDialog(QDialog):
    def __init__(self, cubes: Mapping[str, GisDataCube], parent=None) -> None:
        super().__init__(parent)

        ui_path = __file__.replace(".py", ".ui")
        uic.loadUi(ui_path, self)
        self.cubes = cubes

        self.selected_cube = None
        self.selected_variable = None

        self.logger = get_logger()
        self.logger.info(f"available cubes: {list(cubes.keys())}")

        self.cubeComboBox.clear()
        self.layerComboBox.clear()
        self.cubeComboBox.addItems(self.cubes.keys())
        selected_cube = self.cubeComboBox.currentText()
        if selected_cube:
            self.layerComboBox.addItems(self.cubes[selected_cube].variable_names)

        self.okayButton.clicked.connect(self.handle_button_click)
        self.cubeComboBox.currentTextChanged.connect(self.update_layers_based_on_cube)

    def handle_button_click(self):
        self.selected_cube = self.cubeComboBox.currentText()
        self.selected_variable = self.layerComboBox.currentText()
        self.accept()

    def update_layers_based_on_cube(self):
        selected_cube = self.cubeComboBox.currentText()
        self.layerComboBox.clear()
        self.logger.info(f"Variable names of cube '{selected_cube}'\n{self.cubes[selected_cube].variable_names}")
        self.layerComboBox.addItems(self.cubes[selected_cube].variable_names)
