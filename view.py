from PyQt5.QtWidgets import (QWidget, QLineEdit, QFormLayout, QHBoxLayout,
                             QVBoxLayout, QPushButton, QTreeWidget,
                             QHeaderView, QMainWindow, QLabel)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zip_code_edit = QLineEdit()
        self.zip_code_list = QTreeWidget()
        self.submit_button = QPushButton("Submit")
        self.close_button = QPushButton("Close")
        self.status_bar = self.statusBar()
        self.setWindowTitle('Frost Dates')
        self.setUpWidgets()

    def setUpWidgets(self):
        """Set up the widgets in the main window."""
        central_widget = QWidget()
        form_layout = QFormLayout()
        form_layout.addRow("ZIP Code:", self.zip_code_edit)
        self.zip_code_list.setColumnCount(2)
        header = self.zip_code_list.header()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.zip_code_list.setHeaderHidden(True)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.submit_button)
        buttons_layout.addWidget(self.close_button)
        main_layout = QVBoxLayout()
        instructions = QLabel()
        instructions.setText(
            "Enter 5-digit zip code in the text box and click submit "
            "to fetch latitude and longitude data."
        )
        instructions.setWordWrap(True)
        main_layout.addWidget(instructions)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.zip_code_list)
        main_layout.addLayout(buttons_layout)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.zip_code_edit.setStatusTip("Enter 6-digit US ZIP code.")
        self.zip_code_list.setStatusTip("Location data returned for ZIP codes.")
        self.submit_button.setStatusTip("Get location data from GeoNames.")
        self.close_button.setStatusTip("Close the program.")
        self.submit_button.setDefault(True)
