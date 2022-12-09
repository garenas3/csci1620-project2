import re
from typing import Any

from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt

from view import MainWindow
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
        self.current_station_id: str = ''
        self.main_window = MainWindow()
        self.zip_code_search_page = self.main_window.zip_code_search_widget
        self.select_weather_station_page = self.main_window.select_weather_station_widget
        self.frost_dates_page = self.main_window.frost_dates_widget
        self.zip_data = zip_data.load()
        self.main_window.on_close = lambda: zip_data.save(self.zip_data)
        self.set_up_signals_and_slots()

    def show(self) -> None:
        """Show the main window to the user."""
        self.main_window.show()
        self.main_window.setFixedSize(self.main_window.size())

    def set_up_signals_and_slots(self) -> None:
        """Set up the signals and slots for the program."""
        self.zip_code_search_page.close_button.clicked.connect(self.main_window.close)
        self.zip_code_search_page.search_button.clicked.connect(
            lambda: self.zip_code_search_page.search_button.setEnabled(False)
        )
        self.zip_code_search_page.search_button.clicked.connect(self.submit_zip_code)
        self.zip_code_search_page.zip_code_edit.returnPressed.connect(
            lambda: self.zip_code_search_page.search_button.setEnabled(False)
        )
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
        self.geonames_controller.finished.connect(
            lambda: self.zip_code_search_page.search_button.setEnabled(True)
        )
        self.geonames_controller.result_ready.connect(lambda result: self.set_zip_data(result))
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
            lambda: self.select_weather_station_page.search_button.setEnabled(False)
        )
        self.select_weather_station_page.search_button.clicked.connect(
            self.select_weather_station_page.station_list.clear
        )
        self.select_weather_station_page.search_button.clicked.connect(
            self.search_weather_stations
        )
        self.ncdc_controller.result_ready.connect(
            lambda result: self.add_weather_stations(result)
        )
        self.ncdc_controller.finished.connect(
            lambda: self.select_weather_station_page.search_button.setEnabled(True)
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
        self.select_weather_station_page.station_list.itemSelectionChanged.connect(
            self.set_current_station_id
        )
        self.select_weather_station_page.next_button.clicked.connect(
            lambda: self.main_window.stacked_layout.setCurrentIndex(2)
        )
        self.frost_dates_page.restart_button.clicked.connect(
            lambda: self.zip_code_search_page.zip_code_edit.clear()
        )
        self.frost_dates_page.restart_button.clicked.connect(
            lambda: self.zip_code_search_page.zip_code_list.clear()
        )
        self.frost_dates_page.restart_button.clicked.connect(
            lambda: self.main_window.stacked_layout.setCurrentIndex(0)
        )
        self.frost_dates_page.close_button.clicked.connect(
            self.main_window.close
        )
        self.select_weather_station_page.next_button.clicked.connect(
            lambda: self.select_weather_station_page.next_button.setEnabled(False)
        )
        self.select_weather_station_page.next_button.clicked.connect(
            self.add_frost_dates
        )

    def submit_zip_code(self) -> None:
        """Submit the ZIP code displayed in the ZIP code line edit."""
        zipcode = self.zip_code_search_page.zip_code_edit.text()
        zipcode = zipcode.strip()
        match = re.match(r"\d{5, 5}", zipcode)
        if not match:
            QMessageBox.warning(
                self.main_window,
                "ZIP code is required",
                "A 5-digit ZIP code is required."
            )
            self.zip_code_search_page.search_button.setEnabled(True)
            return
        if self.zip_code_search_page.zip_code_list.findItems(
                zipcode, Qt.MatchFlag.MatchExactly
                ):
            self.main_window.status_bar.showMessage(f"Duplicate request for {zipcode}.")
            self.zip_code_search_page.search_button.setEnabled(True)
            return
        try:
            zipcode_result = self.zip_data[zipcode]
            self.add_zip_code_item(**zipcode_result)
            self.main_window.status_bar.showMessage(
                "Data loaded from cache."
            )
            self.zip_code_search_page.search_button.setEnabled(True)
            return
        except KeyError:
            self.main_window.status_bar.showMessage("Requesting ZIP code data ...")
            self.geonames_controller.sendRequest(zipcode)

    def set_zip_data(self, zip_entry: dict[str, Any]) -> None:
        """Set the program data for the ZIP entry."""
        zipcode = zip_entry['zipcode']
        self.zip_data[zipcode] = zip_entry

    def add_zip_code_item(self, *, zipcode: str, latitude: Any, longitude: Any,
                          city: str) -> None:
        """Add a ZIP code item to the list."""
        zip_item = QTreeWidgetItem(None, [zipcode])
        QTreeWidgetItem(zip_item, ["Latitude:", str(latitude)])
        QTreeWidgetItem(zip_item, ["Longitude:", str(longitude)])
        QTreeWidgetItem(zip_item, ["City:", city])
        self.zip_code_search_page.zip_code_list.addTopLevelItem(zip_item)
        zip_item.setFirstColumnSpanned(True)
        zip_item.setExpanded(True)

    def set_current_location(self) -> None:
        """Set the current location to the selected ZIP code."""
        selected = self.zip_code_search_page.zip_code_list.selectedItems()[0]
        if isinstance(selected.parent(), QTreeWidgetItem):
            selected = selected.parent()
        zip_code = selected.text(0)
        self.current_location = LocationCoordinates(
            latitude=self.zip_data[zip_code]["latitude"],
            longitude=self.zip_data[zip_code]["longitude"]
        )

    def search_weather_stations(self) -> None:
        """Search for weather stations near the current location."""
        radius = self.select_weather_station_page.search_radius.value()
        self.ncdc_controller.sendRequest(self.current_location, radius, 'miles')

    def add_weather_stations(self, stations: list[ncdc_api.StationInfo]) -> None:
        """Add a list of weather stations.

        Args:
            stations: A list of stations to add to the list.
        """
        self.select_weather_station_page.station_list.clear()
        self.select_weather_station_page.next_button.setEnabled(False)
        stations.sort(key=lambda s: self.current_location.distance_from(s.location, 'miles'))
        for station in stations:
            item = QTreeWidgetItem(None, [station.name])
            QTreeWidgetItem(item, ["ID:", station.id])
            QTreeWidgetItem(item, ["Latitude:", str(station.location.latitude)])
            QTreeWidgetItem(item, ["Longitude:", str(station.location.longitude)])
            distance = self.current_location.distance_from(station.location, 'miles')
            QTreeWidgetItem(item, ["Distance:", f"{distance:.1f} miles"])
            self.select_weather_station_page.station_list.addTopLevelItem(item)
            item.setFirstColumnSpanned(True)

    def set_current_station_id(self) -> None:
        """Set the current station ID to the selected station."""
        items = self.select_weather_station_page.station_list.selectedItems()
        if not items:
            self.current_station_id = ''
            return
        selected = items[0]
        if isinstance(selected.parent(), QTreeWidgetItem):
            selected = selected.parent()
        station_id = selected.child(0).text(1)
        self.current_station_id = station_id

    def add_frost_dates(self) -> None:
        """Add frost dates to the frost dates page."""
        frost_dates = ncdc_api.get_frost_dates(self.ncdc_controller.token, self.current_station_id, 'first')
        frost_date_keys = ncdc_api.FrostDateDataTypesIterable('first')
        for key in frost_date_keys:
            row = (frost_date_keys.temperature - 16) // 4
            column = frost_date_keys.percent_probability // 10
            item = QTableWidgetItem(frost_dates[key])
            self.frost_dates_page.fall_frost_dates_table.setItem(row, column, item)

        frost_dates = ncdc_api.get_frost_dates(self.ncdc_controller.token, self.current_station_id, 'last')
        frost_date_keys = ncdc_api.FrostDateDataTypesIterable('last')
        for key in frost_date_keys:
            row = (frost_date_keys.temperature - 16) // 4
            column = frost_date_keys.percent_probability // 10
            item = QTableWidgetItem(frost_dates[key])
            self.frost_dates_page.spring_frost_dates_table.setItem(row, column, item)
