import re
import time

from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject

from view import MainWindow
import geonames_api
import programdata


class MainController:
    def __init__(self) -> None:
        self.geonames_username = geonames_api.load_username()
        self.main_window = MainWindow()
        self.program_data = programdata.load()
        self.main_window.on_close = lambda: programdata.save(self.program_data)
        self.worker_thread = QThread()
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
            zipcode_result = self.program_data[zipcode]
            self.add_zip_code_item(**zipcode_result)
            self.main_window.status_bar.showMessage(
                "Data loaded from cache."
            )
            return
        except KeyError:
            self.send_zip_code_request(zipcode)

    def send_zip_code_request(self, zipcode: str):
        """Send the ZIP code request via API and update window."""
        self.main_window.status_bar.showMessage(
            f"Request to fetch location data ..."
        )
        time_start = time.perf_counter()
        self.main_window.repaint()
        zipcode_result = geonames_api.get_zipcode_location(
            username=self.geonames_username,
            zipcode=zipcode
        )
        time_end = time.perf_counter()
        self.main_window.status_bar.showMessage(
            f"Request completed in {time_end - time_start:.3f} s."
        )
        self.program_data[zipcode] = zipcode_result
        self.add_zip_code_item(**zipcode_result)

    def add_zip_code_item(self, *, zipcode, latitude, longitude, city):
        """Add a ZIP code item to the list."""
        zip_item = QTreeWidgetItem(None, [str(zipcode)])
        QTreeWidgetItem(zip_item, ["Latitude:", str(latitude)])
        QTreeWidgetItem(zip_item, ["Longitude:", str(longitude)])
        QTreeWidgetItem(zip_item, ["City:", city])
        self.main_window.zip_code_list.addTopLevelItem(zip_item)


class FetchZipCodeWorker(QObject):
    """Fetch the ZIP code info asynchronously."""
    result_ready = pyqtSignal(dict)
    request_cancelled = pyqtSignal()
    request_error = pyqtSignal(RuntimeError)

    def __init__(self, geonames_username: str, zipcode: str):
        super().__init__()
        self.geonames_username = geonames_username
        self.zipcode = zipcode

    def cancel(self):
        """Cancel the running operation."""
        self.terminate()
        self.wait()
        self.request_cancelled.emit()

    def run(self):
        try:
            result = geonames_api.get_zipcode_location(
                username=self.geonames_username,
                zipcode=self.zipcode
            )
            self.result_ready.emit(result)
        except RuntimeError as error:
            self.request_error.emit(error)
