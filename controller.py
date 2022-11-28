from view import MainWindow


class MainController:
    def __init__(self) -> None:
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
        """Submit the zip code displayed in the zip code line edit."""
        zip_code = self.main_window.zip_code_edit.text()
        self.main_window.zip_code_list.addItems([zip_code])


def submit_zip_code(zip_code: str) -> None:
    """Submit the zip code for processing."""
    print(zip_code)
