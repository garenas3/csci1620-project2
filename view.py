from typing import Callable, Any

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent, QFont
from PyQt5.QtWidgets import (QWidget, QLineEdit, QHBoxLayout, QVBoxLayout,
                             QPushButton, QTreeWidget, QHeaderView,
                             QMainWindow, QLabel, QSizePolicy, QStackedLayout, QSlider, QSpinBox)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zip_code_search_widget = ZipCodeSearchPage()
        self.select_weather_station_widget = SelectWeatherStationPage()
        self.stacked_layout = QStackedLayout()
        self.status_bar = self.statusBar()
        self.on_close: Callable[..., Any] | None = None
        self.setWindowTitle('Frost Dates')
        self.setUpWidgets()

    def setUpWidgets(self):
        """Set up the widgets in the main window."""
        central_widget = QWidget()
        self.stacked_layout.addWidget(self.zip_code_search_widget)
        self.stacked_layout.addWidget(self.select_weather_station_widget)
        central_widget.setLayout(self.stacked_layout)
        self.setCentralWidget(central_widget)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.on_close:
            self.on_close()
        event.accept()


class ZipCodeSearchPage(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zip_code_edit = QLineEdit()
        self.zip_code_list = QTreeWidget()
        self.search_button = QPushButton("Search")
        self.next_button = QPushButton("Next")
        self.close_button = QPushButton("Close")
        self.setWindowTitle('ZIP Code Search')
        self.setUpWidget()

    def setUpWidget(self):
        """Set up the ZIP code search widget."""
        search_heading = QLabel("Select a Location")
        search_heading_font = QFont()
        search_heading_font.setPointSize(16)
        search_heading.setFont(search_heading_font)
        zip_search_layout = QHBoxLayout()
        zip_search_layout.addWidget(QLabel("ZIP Code:"))
        self.zip_code_edit.setPlaceholderText("e.g. 00501")
        self.zip_code_edit.setClearButtonEnabled(True)
        zip_search_layout.addWidget(self.zip_code_edit)
        size_policy = self.search_button.sizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        self.search_button.setSizePolicy(size_policy)
        self.zip_code_list.setColumnCount(2)
        header = self.zip_code_list.header()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.zip_code_list.setHeaderHidden(True)
        main_layout = QVBoxLayout()
        main_layout.addWidget(search_heading)
        main_layout.addSpacing(10)
        main_layout.addLayout(zip_search_layout)
        main_layout.addWidget(self.search_button, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.zip_code_list)
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        self.next_button.setEnabled(False)
        buttons_layout.addWidget(self.next_button)
        buttons_layout.addWidget(self.close_button)
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)
        self.zip_code_edit.setStatusTip("Enter 5-digit US ZIP code.")
        self.zip_code_list.setStatusTip("Location data returned for ZIP codes.")
        self.search_button.setStatusTip("Get location data from GeoNames.")
        self.next_button.setStatusTip("Go to the next screen.")
        self.close_button.setStatusTip("Close the program.")


class SelectWeatherStationPage(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_radius = SearchRadiusWidget()
        self.search_button = QPushButton("Search")
        self.station_list = QTreeWidget()
        self.next_button = QPushButton("Next")
        self.go_back_button = QPushButton("Go Back")
        self.close_button = QPushButton("Close")
        self.setWindowTitle('Select Weather Station')
        self.setUpWidget()

    def setUpWidget(self):
        """Set up the select weather station widget."""
        select_heading = QLabel("Select a Weather Station")
        select_heading_font = QFont()
        select_heading_font.setPointSize(16)
        select_heading.setFont(select_heading_font)
        self.station_list.setColumnCount(2)
        header = self.station_list.header()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.station_list.setHeaderHidden(True)
        main_layout = QVBoxLayout()
        main_layout.addWidget(select_heading)
        main_layout.addSpacing(10)
        self.search_radius.setMinimum(5)
        self.search_radius.setMaximum(20)
        main_layout.addWidget(self.search_radius)
        main_layout.addWidget(self.search_button, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.station_list)
        buttons_layout = QHBoxLayout()
        self.next_button.setEnabled(False)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.go_back_button)
        buttons_layout.addWidget(self.next_button)
        buttons_layout.addWidget(self.close_button)
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)
        self.station_list.setStatusTip("Select a weather station.")
        self.go_back_button.setStatusTip("Go to the previous screen.")
        self.next_button.setStatusTip("Go to the next screen.")
        self.close_button.setStatusTip("Close the program.")


class SearchRadiusWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.spin_box = QSpinBox()
        self.setUpWidgets()

    def setUpWidgets(self):
        """Set up widgets for the search radius widget."""
        main_layout = QHBoxLayout()
        main_layout.addWidget(QLabel("Search Radius:"))
        main_layout.addWidget(self.slider)
        main_layout.addWidget(self.spin_box)
        self.spin_box.setSuffix(" miles")
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
        self.slider.setStatusTip("Set the search radius.")
        self.slider.valueChanged.connect(self.spin_box.setValue)
        self.spin_box.valueChanged.connect(self.slider.setValue)

    def setMinimum(self, value):
        self.slider.setMinimum(value)
        self.spin_box.setMinimum(value)

    def setMaximum(self, value):
        self.slider.setMaximum(value)
        self.spin_box.setMaximum(value)
