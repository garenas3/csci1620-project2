from typing import Callable, Any

from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import (QWidget, QLineEdit, QHBoxLayout, QVBoxLayout,
                             QPushButton, QTreeWidget, QHeaderView,
                             QMainWindow, QLabel, QSizePolicy, QStackedLayout)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zip_code_edit = QLineEdit()
        self.zip_code_list = QTreeWidget()
        self.search_button = QPushButton("Search")
        self.next_button = QPushButton("Next")
        self.close_button = QPushButton("Close")
        self.status_bar = self.statusBar()
        self.on_close: Callable[..., Any] | None = None
        self.setWindowTitle('Frost Dates')
        self.setUpWidgets()

    def setUpWidgets(self):
        """Set up the widgets in the main window."""
        central_widget = QWidget()
        buttons_layout = QHBoxLayout()
        self.next_button.setEnabled(False)
        buttons_layout.addWidget(self.next_button)
        buttons_layout.addWidget(self.close_button)
        stacked_layout = QStackedLayout()
        stacked_layout.addWidget(self.setUpZipCodeSearchWidget())
        stacked_layout.addWidget(self.setUpSelectStationWidget())
        self.next_button.clicked.connect(lambda: stacked_layout.setCurrentIndex(1))
        self.next_button.clicked.connect(lambda: self.next_button.setEnabled(False))
        main_layout = QVBoxLayout()
        main_layout.addLayout(stacked_layout)
        main_layout.addLayout(buttons_layout)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def setUpZipCodeSearchWidget(self) -> QWidget:
        """Set up the ZIP code search widget."""
        zip_code_search_widget = QWidget()
        zip_search_layout = QHBoxLayout()
        zip_search_layout.addWidget(QLabel("ZIP Code:"))
        self.zip_code_edit.setPlaceholderText("e.g. 00501")
        self.zip_code_edit.setClearButtonEnabled(True)
        zip_search_layout.addWidget(self.zip_code_edit)
        size_policy = self.search_button.sizePolicy()
        size_policy.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        self.search_button.setSizePolicy(size_policy)
        zip_search_layout.addWidget(self.search_button)
        self.zip_code_list.setColumnCount(2)
        header = self.zip_code_list.header()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.zip_code_list.setHeaderHidden(True)
        main_layout = QVBoxLayout()
        main_layout.addLayout(zip_search_layout)
        main_layout.addWidget(self.zip_code_list)
        zip_code_search_widget.setLayout(main_layout)
        self.zip_code_edit.setStatusTip("Enter 5-digit US ZIP code.")
        self.zip_code_list.setStatusTip("Location data returned for ZIP codes.")
        self.search_button.setStatusTip("Get location data from GeoNames.")
        self.next_button.setStatusTip("Go to the next screen.")
        self.close_button.setStatusTip("Close the program.")
        self.search_button.setDefault(True)
        return zip_code_search_widget

    def setUpSelectStationWidget(self) -> QWidget:
        """Set up the select station widget."""
        select_station_widget = QWidget()
        return select_station_widget

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.on_close:
            self.on_close()
        event.accept()
