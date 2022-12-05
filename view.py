from typing import Callable, Any

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import (QWidget, QLineEdit, QFormLayout, QHBoxLayout,
                             QVBoxLayout, QPushButton, QTreeWidget,
                             QHeaderView, QMainWindow, QLabel, QSizePolicy)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zip_code_edit = QLineEdit()
        self.zip_code_list = QTreeWidget()
        self.search_button = QPushButton("Search")
        self.close_button = QPushButton("Close")
        self.status_bar = self.statusBar()
        self.on_close: Callable[..., Any] | None = None
        self.setWindowTitle('Frost Dates')
        self.setUpWidgets()

    def setUpWidgets(self):
        """Set up the widgets in the main window."""
        central_widget = QWidget()
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
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.close_button)
        main_layout = QVBoxLayout()
        main_layout.addLayout(zip_search_layout)
        main_layout.addWidget(self.zip_code_list)
        main_layout.addLayout(buttons_layout)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.zip_code_edit.setStatusTip("Enter 5-digit US ZIP code.")
        self.zip_code_list.setStatusTip("Location data returned for ZIP codes.")
        self.search_button.setStatusTip("Get location data from GeoNames.")
        self.close_button.setStatusTip("Close the program.")
        self.search_button.setDefault(True)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.on_close:
            self.on_close()
        event.accept()
