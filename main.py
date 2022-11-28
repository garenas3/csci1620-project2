import sys

from PyQt5.QtWidgets import QApplication

from controller import MainController


def main():
    app = QApplication(sys.argv)
    controller = MainController()
    controller.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
