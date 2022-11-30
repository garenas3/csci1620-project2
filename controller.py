import re
import csv

from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import Qt

from view import MainWindow
import geonames_api


class MainController:
    def __init__(self) -> None:
        self.geonames_username = geonames_api.load_username()
        self.main_window = MainWindow()
        self.program_data = load_program_data()
        self.main_window.on_close = lambda: save_program_data(self.program_data)
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


def load_program_data(filename: str = "programdata.csv") -> dict[str, str]:
    """Load the program cache from a file."""
    try:
        with open(filename, 'r', newline='') as fh:
            result = {}
            fh.readline()  # read header
            reader = csv.reader(fh)
            for row in reader:
                zipcode = row[0]
                latitude = row[1]
                longitude = row[2]
                result[zipcode] = {"latitude": latitude,
                                   "longitude": longitude}
            return result
    except FileNotFoundError:
        return {}


def save_program_data(data: dict[str, str],
                      filename: str = "programdata.csv") -> None:
    """Save the program cache to a file."""
    if not data:
        return
    try:
        with open(filename, 'w', newline='') as fh:
            writer = csv.writer(fh)
            writer.writerow(["zipcode", "latitude", "longitude"])
            for zipcode, coords in data.items():
                writer.writerow(
                    [zipcode, coords["latitude"], coords["longitude"]]
                )
    except KeyError:
        raise RuntimeError("Unexpected program data format")
