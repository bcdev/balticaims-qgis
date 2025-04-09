from typing import List

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from balticaims.utils import get_logger

class SelectDatasetDialog(QDialog):
    def __init__(self, parent=None, dataset_ids: List | None = None) -> None:
        super().__init__(parent)

        ui_path = __file__.replace(".py", ".ui")
        uic.loadUi(ui_path, self)

        self.selected_dataset = None


        self.logger = get_logger()
        self.logger.info(f"dataset ids: {dataset_ids}")
        if not dataset_ids:
            self.datasetComboBox.addItem("No datasets available, make sure the xcube connection is open")
            self.datasetComboBox.setEnabled(False)
            return

        self.datasetComboBox.clear()
        self.datasetComboBox.addItems(dataset_ids)
        self.okayButton.clicked.connect(self.handle_button_click)

    def handle_button_click(self):
        self.selected_dataset = self.datasetComboBox.currentText()
        self.accept()
