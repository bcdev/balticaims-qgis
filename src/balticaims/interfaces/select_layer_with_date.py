from typing import List
from datetime import datetime
from math import log

from PyQt5.QtCore import QDateTime, Qt
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

from balticaims.data_cube import GisDataCube
from balticaims.utils import get_logger

class SelectLayerAndTimeDialog(QDialog):
    def __init__(self, cubes: List[GisDataCube], parent=None) -> None:
        super().__init__(parent)

        ui_path = __file__.replace(".py", ".ui")
        uic.loadUi(ui_path, self)
        self.cubes = cubes

        self.selected_cube_id = None
        self.selected_variable = None
        self.selected_start_time = None
        self.selected_end_time = None
        self._var_time_slice = None
        self.selected_n_time_steps = None

        self.logger = get_logger()
        self.logger.info(f"available cubes: {[c.dataset_id for c in cubes]}")

        self.cubeComboBox.clear()
        self.layerComboBox.clear()
        self.cubeComboBox.addItems([c.name for c in self.cubes])
        self.update_layers_based_on_cube()
        self.update_download_size()

        self.okayButton.clicked.connect(self.handle_button_click)
        self.cubeComboBox.currentTextChanged.connect(self.update_layers_based_on_cube)
        self.startDateTimeEdit.dateTimeChanged.connect(self.update_download_size)
        self.endDateTimeEdit.dateTimeChanged.connect(self.update_download_size)

    def handle_button_click(self):
        self.selected_cube_id = self.cubes[self.cubeComboBox.currentIndex()].dataset_id
        self.selected_variable = self.layerComboBox.currentData()
        self.selected_start_time = qdatetime_to_datetime(self.startDateTimeEdit.dateTime())
        self.selected_end_time = qdatetime_to_datetime(self.endDateTimeEdit.dateTime())
        self.selected_n_time_steps = len(self._var_time_slice.time)
        self.accept()

    def update_layers_based_on_cube(self):
        selected_cube = self.cubes[self.cubeComboBox.currentIndex()]
        self.layerComboBox.clear()
        if not selected_cube:
            return

        self.logger.info(f"selected cube {selected_cube.dataset_id} with variables {selected_cube._metadata.variables.keys()}")
        for d in selected_cube._metadata.variables.values():
            self.layerComboBox.addItem(f"{d['name']} ({d['title']})", d["name"])

        time_coordinate = selected_cube._metadata.dimensions["time"]["coordinates"]
        start_qdate_time = QDateTime.fromString(time_coordinate[0], Qt.ISODate)
        end_qdate_time = QDateTime.fromString(time_coordinate[-1], Qt.ISODate)
        self.startDateTimeEdit.setDateTimeRange(start_qdate_time, end_qdate_time)
        self.endDateTimeEdit.setDateTimeRange(start_qdate_time, end_qdate_time)

        self.startDateTimeEdit.setDateTime(start_qdate_time)
        self.endDateTimeEdit.setDateTime(end_qdate_time)

    def update_download_size(self):
        selected_cube = self.cubes[self.cubeComboBox.currentIndex()]
        selected_var = self.layerComboBox.currentData()
        start_date_time = qdatetime_to_datetime(self.startDateTimeEdit.dateTime())
        end_date_time = qdatetime_to_datetime(self.endDateTimeEdit.dateTime())
        var_time_slice = selected_cube.ds[selected_var].sel(time=slice(start_date_time, end_date_time))
        self._var_time_slice=var_time_slice
        self.logger.info(f"{var_time_slice.nbytes=}, {var_time_slice.shape=}, {var_time_slice.dtype=}")
        human_readable_size = human_readable_download_size(var_time_slice.nbytes)
        label_text = f"Approx. Download size: {human_readable_size}.\nMake sure the cube slice fits into RAM."
        self.downloadSizeLabel.setText(label_text)
        self.timeStepsLabel.setText(f"Number of time steps: {len(var_time_slice.time)}")


# TODO move to util
def qdatetime_to_datetime(qdatetime):
    return datetime.fromisoformat(qdatetime.toString(Qt.ISODate))

def human_readable_download_size(nbytes: int, base=1024):
    if nbytes < 0:
        return "Invalid size"
    elif nbytes == 0:
        return f"0 bytes"
    elif nbytes == 1:
        return f"1 byte"

    units = [
        ("bytes", 0),
        ("kiB", 0),
        ("MiB", 0),
        ("GiB", 2),
        ("TiB", 2),
        ("PiB", 2),
    ]
    exponent = min(int(log(nbytes, base)), len(units)- 1)
    quotient = float(nbytes / base**exponent)
    unit, precision = units[exponent]
    return f"{quotient:.{precision}f} {unit}"