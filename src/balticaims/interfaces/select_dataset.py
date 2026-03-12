from typing import List

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from balticaims.utils import get_logger

class SelectDataCubeDialog(QDialog):
    def __init__(self, parent=None, data_cubes: List | None = None) -> None:
        super().__init__(parent)

        ui_path = __file__.replace(".py", ".ui")
        uic.loadUi(ui_path, self)

        self.selected_data_cube = None
        self.data_cubes = data_cubes

        self.logger = get_logger()
        if data_cubes:
            self.logger.info(f"data cube ids: {[d['id'] for d in data_cubes]}")
        else:
            self.logger.warning("No data cubes found")
        if not data_cubes:
            self.dataCubeComboBox.addItem("No data cubes available, make sure the xcube connection is open")
            self.dataCubeComboBox.setEnabled(False)
            return

        self.dataCubeComboBox.clear()
        self.dataCubeComboBox.addItems([d["title"] for d in data_cubes])
        self.okayButton.clicked.connect(self.handle_button_click)

    def handle_button_click(self):
        if self.data_cubes:
            self.selected_data_cube = self.data_cubes[self.dataCubeComboBox.currentIndex()]["id"]
            self.accept()
        else:
            self.logger.warning("Pressed data cube selection button with no data cubes available")
            self.accept()
