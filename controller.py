from view import MainWindow


class MainController:
    def __init__(self):
        self.main_window = MainWindow()
        self.set_up_signals_and_slots()

    def show(self):
        self.main_window.show()

    def set_up_signals_and_slots(self):
        """Set up the signals and slots for the program."""
        self.main_window.close_button.clicked.connect(self.main_window.close)
