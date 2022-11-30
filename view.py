from PyQt5.QtWidgets import (QWidget, QLineEdit, QFormLayout, QHBoxLayout,
                             QVBoxLayout, QPushButton, QTreeWidget)


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.zip_code_edit = QLineEdit()
        self.zip_code_list = QTreeWidget()
        self.submit_button = QPushButton("Submit")
        self.close_button = QPushButton("Close")
        self.setWindowTitle('Frost Dates')
        self.setUpWidgets()

    def setUpWidgets(self):
        """Set up the widgets in the main window."""
        form_layout = QFormLayout()
        form_layout.addRow("ZIP Code:", self.zip_code_edit)
        self.zip_code_list.setColumnCount(1)
        self.zip_code_list.setHeaderHidden(True)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.submit_button)
        buttons_layout.addWidget(self.close_button)
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.zip_code_list)
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)
