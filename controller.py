from view import MainWindow


class MainController:
    def __init__(self):
        self.main_window = MainWindow()
        self.set_up_signals_and_slots()

    def show(self):
        """Show the main window to the user."""
        self.main_window.show()

    def set_up_signals_and_slots(self):
        """Set up the signals and slots for the program."""
        self.main_window.close_button.clicked.connect(self.main_window.close)


def submit_zip_code(zip_code: str) -> None:
    """Submit the zip code for processing."""
    print(zip_code)
