import re

from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox

from view import MainWindow
import geonames_api


class MainController:
    def __init__(self) -> None:
        self.geonames_username = geonames_api.load_username()
        self.main_window = MainWindow()
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
        zip_code = self.main_window.zip_code_edit.text()
        zip_code = zip_code.strip()
        match = re.match(r"\d{5}", zip_code)
        if not match:
            QMessageBox.warning(
                self.main_window,
                "ZIP code is required",
                "A 5-digit ZIP code is required."
            )
            return
        coords = geonames_api.get_zipcode_location(
            username=self.geonames_username,
            zipcode=zip_code
        )
        zip_item = QTreeWidgetItem(None, [zip_code])
        QTreeWidgetItem(zip_item, ["latitude:", str(coords["latitude"])])
        QTreeWidgetItem(zip_item, ["longitude:", str(coords["longitude"])])
        self.main_window.zip_code_list.addTopLevelItem(zip_item)
