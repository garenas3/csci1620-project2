import re

from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import Qt

from view import MainWindow
import geonames_api
import zip_data


class MainController:
    def __init__(self) -> None:
        self.geonames_controller = geonames_api.GetZIPCodeAsyncController(
            geonames_api.load_username()
        )
        self.main_window = MainWindow()
        self.program_data = zip_data.load()
        self.main_window.on_close = lambda: zip_data.save(self.program_data)
        self.set_up_signals_and_slots()

    def show(self) -> None:
        """Show the main window to the user."""
        self.main_window.show()

    def set_up_signals_and_slots(self) -> None:
        """Set up the signals and slots for the program."""
        self.main_window.close_button.clicked.connect(self.main_window.close)
        self.main_window.search_button.clicked.connect(self.submit_zip_code)
        self.main_window.zip_code_edit.returnPressed.connect(
            self.submit_zip_code
        )
        self.geonames_controller.result_ready.connect(
            lambda: self.main_window.status_bar.showMessage("Request successful.")
        )
        self.geonames_controller.error_raised.connect(
            lambda: self.main_window.status_bar.showMessage("Error occurred while making request.")
        )
        self.geonames_controller.error_raised.connect(
            lambda message: QMessageBox.warning(self.main_window, "Error", message)
        )
        self.geonames_controller.result_ready.connect(lambda result: self.set_program_data(result))
        self.geonames_controller.result_ready.connect(lambda result: self.add_zip_code_item(**result))
        self.main_window.zip_code_list.itemSelectionChanged.connect(
            lambda: self.main_window.next_button.setEnabled(
                bool(self.main_window.zip_code_list.selectedItems())
            )
        )

    def submit_zip_code(self) -> None:
        """Submit the ZIP code displayed in the ZIP code line edit."""
        zipcode = self.main_window.zip_code_edit.text()
        zipcode = zipcode.strip()
        match = re.match(r"\d{5}", zipcode)
        if not match:
            QMessageBox.warning(
                self.main_window,
                "ZIP code is required",
                "A 5-digit ZIP code is required."
            )
            return
        if self.main_window.zip_code_list.findItems(zipcode, Qt.MatchFlag.MatchExactly):
            self.main_window.status_bar.showMessage(f"Duplicate request for {zipcode}.")
            return
        try:
            zipcode_result = self.program_data[zipcode]
            self.add_zip_code_item(**zipcode_result)
            self.main_window.status_bar.showMessage(
                "Data loaded from cache."
            )
            return
        except KeyError:
            self.main_window.status_bar.showMessage("Requesting ZIP code data ...")
            self.geonames_controller.sendRequest(zipcode)

    def set_program_data(self, result):
        """Set the program data for the zipcode entry."""
        zipcode = result['zipcode']
        self.program_data[zipcode] = result

    def add_zip_code_item(self, *, zipcode, latitude, longitude, city):
        """Add a ZIP code item to the list."""
        zip_item = QTreeWidgetItem(None, [str(zipcode)])
        QTreeWidgetItem(zip_item, ["Latitude:", str(latitude)])
        QTreeWidgetItem(zip_item, ["Longitude:", str(longitude)])
        QTreeWidgetItem(zip_item, ["City:", city])
        self.main_window.zip_code_list.addTopLevelItem(zip_item)
        zip_item.setExpanded(True)
