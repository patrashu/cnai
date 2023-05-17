
from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QFrame
)

from ..common_widgets import Label

class Toolbar(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setMaximumWidth(1980)
        # self.setMaximumHeight(50)
        self.setFixedHeight(50)
        self.setContentsMargins(0, 0, 0, 0)
        self.setObjectName("Toolbar")
        self.setStyleSheet("""
            QFrame#Toolbar {
                background-color: #323233; padding: 0px; margin: 0px;
            }
        """)

        self.label_title = Label("CN.AI Monitering System", fontsize=15, orientation=Qt.AlignCenter)

        layout_main = QHBoxLayout()
        layout_main.addWidget(self.label_title)
        self.setLayout(layout_main)