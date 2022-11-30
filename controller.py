import re

from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import Qt

from view import MainWindow
import geonames_api
import programdata


class MainController:
    def __init__(self) -> None:
        self.geonames_username = geonames_api.load_username()
        self.main_window = MainWindow()
        self.program_data = programdata.load()
        self.main_window.on_close = lambda: programdata.save(self.program_data)
        self.set_up_signals_and_slots()

    def show(self) -> None:
        """Show the main window to the user."""
        self.main_window.show()

    def set_up_signals_and_slots(self) -> None:
        """Set up the signals and slots for the program."""
        self.main_window.close_button.clicked.connect(self.main_window.close)
        self.main_window.submit_button.clicked.connect(self.submit_zip_code)
        self.main_window.zip_code_edit.returnPressed.connect(
            self.submit_zip_code
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
            coords = self.program_data[zipcode]
        except KeyError:
            coords = geonames_api.get_zipcode_location(
                username=self.geonames_username,
                zipcode=zipcode
            )
            self.program_data[zipcode] = {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"]
            }
        zip_item = QTreeWidgetItem(None, [zipcode])
        QTreeWidgetItem(zip_item, ["latitude:", str(coords["latitude"])])
        QTreeWidgetItem(zip_item, ["longitude:", str(coords["longitude"])])
        self.main_window.zip_code_list.addTopLevelItem(zip_item)
