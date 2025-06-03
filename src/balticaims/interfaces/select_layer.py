from typing import List

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from balticaims.data_cube import GisDataCube
from balticaims.utils import get_logger

class SelectLayerDialog(QDialog):
    def __init__(self, cubes: List[GisDataCube], parent=None) -> None:
        super().__init__(parent)

        ui_path = __file__.replace(".py", ".ui")
        uic.loadUi(ui_path, self)
        self.cubes = cubes

        self.selected_cube_id = None
        self.selected_variable = None

        self.logger = get_logger()
        self.logger.info(f"available cubes: {[c.dataset_id for c in cubes]}")

        self.cubeComboBox.clear()
        self.layerComboBox.clear()
        self.cubeComboBox.addItems([c.name for c in self.cubes])
        self.update_layers_based_on_cube()

        self.okayButton.clicked.connect(self.handle_button_click)
        self.cubeComboBox.currentTextChanged.connect(self.update_layers_based_on_cube)

    def handle_button_click(self):
        self.selected_cube_id = self.cubes[self.cubeComboBox.currentIndex()].dataset_id
        self.selected_variable = self.layerComboBox.currentData()
        self.accept()

    def update_layers_based_on_cube(self):
        selected_cube = self.cubes[self.cubeComboBox.currentIndex()]
        self.layerComboBox.clear()
        if selected_cube:
            self.logger.info(f"selected cube {selected_cube.dataset_id} with variables {selected_cube._metadata.variables.keys()}")
            for d in selected_cube._metadata.variables.values():
                self.layerComboBox.addItem(f"{d['name']} ({d['title']})", d["name"])
