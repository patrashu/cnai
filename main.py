import qdarktheme
from object_tracking.main_window import MainWindow
from PySide6.QtWidgets import QApplication
 

if __name__ == "__main__":
    app = QApplication()
    qdarktheme.setup_theme()
    main_window = MainWindow()
    main_window.show()
    app.exec()