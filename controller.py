import re
from typing import Any

from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import Qt

from view import MainWindow, ZipCodeSearchPage
import geonames_api
import ncdc_api
import zip_data
from location_coordinates import LocationCoordinates


class MainController:
    def __init__(self) -> None:
        self.geonames_controller = geonames_api.GetZIPCodeAsyncController(
            geonames_api.load_username()
        )
        self.ncdc_controller = ncdc_api.GetNearbyStationsAsyncController(
            ncdc_api.load_token()
        )
        self.current_location = LocationCoordinates(latitude="41.318581", longitude="-96.346288")
        self.main_window = MainWindow()
        self.zip_code_search_page = self.main_window.zip_code_search_widget
        self.select_weather_station_page = self.main_window.select_weather_station_widget
        self.zip_data = zip_data.load()
        self.main_window.on_close = lambda: zip_data.save(self.zip_data)
        self.set_up_signals_and_slots()

    def show(self) -> None:
        """Show the main window to the user."""
        self.main_window.show()

    def set_up_signals_and_slots(self) -> None:
        """Set up the signals and slots for the program."""
        self.zip_code_search_page.close_button.clicked.connect(self.main_window.close)
        self.zip_code_search_page.search_button.clicked.connect(self.submit_zip_code)
        self.zip_code_search_page.zip_code_edit.returnPressed.connect(
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
        self.zip_code_search_page.zip_code_list.itemSelectionChanged.connect(
            lambda: self.zip_code_search_page.next_button.setEnabled(
                bool(self.zip_code_search_page.zip_code_list.selectedItems())
            )
        )
        self.zip_code_search_page.next_button.clicked.connect(
            lambda: self.main_window.stacked_layout.setCurrentIndex(1)
        )
        self.select_weather_station_page.go_back_button.clicked.connect(
            lambda: self.main_window.stacked_layout.setCurrentIndex(0)
        )
        self.select_weather_station_page.close_button.clicked.connect(
            self.main_window.close
        )
        self.select_weather_station_page.search_button.clicked.connect(
            self.search_weather_stations
        )
        self.ncdc_controller.result_ready.connect(
            lambda result: self.add_weather_stations(result)
        )
        self.select_weather_station_page.station_list.itemSelectionChanged.connect(
            lambda: self.select_weather_station_page.next_button.setEnabled(
                bool(self.select_weather_station_page.station_list.selectedItems())
            )
        )
        self.zip_code_search_page.next_button.clicked.connect(
            self.set_current_location
        )
        self.zip_code_search_page.next_button.clicked.connect(
            self.select_weather_station_page.station_list.clear
        )

    def submit_zip_code(self) -> None:
        """Submit the ZIP code displayed in the ZIP code line edit."""
        zipcode = self.zip_code_search_page.zip_code_edit.text()
        zipcode = zipcode.strip()
        match = re.match(r"\d{5}", zipcode)
        if not match:
            QMessageBox.warning(
                self.main_window,
                "ZIP code is required",
                "A 5-digit ZIP code is required."
            )
            return
        if self.zip_code_search_page.zip_code_list.findItems(zipcode, Qt.MatchFlag.MatchExactly):
            self.main_window.status_bar.showMessage(f"Duplicate request for {zipcode}.")
            return
        try:
            zipcode_result = self.zip_data[zipcode]
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
        self.zip_data[zipcode] = result

    def add_zip_code_item(self, *, zipcode, latitude, longitude, city):
        """Add a ZIP code item to the list."""
        zip_item = QTreeWidgetItem(None, [str(zipcode)])
        QTreeWidgetItem(zip_item, ["Latitude:", str(latitude)])
        QTreeWidgetItem(zip_item, ["Longitude:", str(longitude)])
        QTreeWidgetItem(zip_item, ["City:", city])
        self.zip_code_search_page.zip_code_list.addTopLevelItem(zip_item)
        zip_item.setFirstColumnSpanned(True)
        zip_item.setExpanded(True)

    def set_current_location(self):
        """Set the current location to the selected ZIP code."""
        selected = self.zip_code_search_page.zip_code_list.selectedItems()[0]
        if isinstance(selected.parent(), QTreeWidgetItem):
            selected = selected.parent()
        zip_code = selected.text(0)
        self.current_location = LocationCoordinates(
            latitude=self.zip_data[zip_code]["latitude"],
            longitude=self.zip_data[zip_code]["longitude"]
        )

    def search_weather_stations(self):
        radius = self.select_weather_station_page.search_radius.value()
        self.ncdc_controller.sendRequest(self.current_location, radius, 'miles')

    def add_weather_stations(self, stations: list[ncdc_api.StationInfo]):
        """Add a list of weather stations."""
        self.select_weather_station_page.station_list.clear()
        self.select_weather_station_page.next_button.setEnabled(False)
        stations.sort(key=lambda s: self.current_location.distance_from(s.location, 'miles'))
        for station in stations:
            item = QTreeWidgetItem(None, [station.name])
            item.setToolTip(0, station.name)
            QTreeWidgetItem(item, ["Latitude:", str(station.location.latitude)])
            QTreeWidgetItem(item, ["Longitude:", str(station.location.longitude)])
            distance = self.current_location.distance_from(station.location, 'miles')
            QTreeWidgetItem(item, ["Distance:", f"{distance:.1f} miles"])
            self.select_weather_station_page.station_list.addTopLevelItem(item)
            item.setFirstColumnSpanned(True)
