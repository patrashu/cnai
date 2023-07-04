import os

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QFrame, QPushButton
)

import qtawesome as qta

from ..signals import all_signals

class SidebarMenus(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedWidth(60)
        self.setStyleSheet("background-color: #333333;")

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        self.streaming_video = self._make_icons(
            qta.icon("mdi.file-multiple-outline"),
            "Streaming with stored video",
        )
        self.streaming_cam = self._make_icons(
            qta.icon("mdi6.file-find-outline"),
            "Streaming with cam",
        )
        self.visualization = self._make_icons( 
            qta.icon("ph.gear"), 
            "Visualization",
        )

        main_layout.addWidget(self.streaming_video)
        main_layout.addWidget(self.streaming_cam)
        main_layout.addWidget(self.visualization)
        self.setLayout(main_layout)

        self.streaming_video.clicked.connect(self.clicked_recorder)
        self.streaming_cam.clicked.connect(self.clicked_explorer)
        self.visualization.clicked.connect(self.clicked_solution)


    def _make_icons(
            self, 
            icon: qta,
            tooltip: str,
        ) -> QPushButton:

        _btn = QPushButton(icon, "")
        _btn.setFixedSize(45, 55)
        _btn.setIconSize(QSize(45, 45))
        _btn.setToolTip(f'<b>{tooltip}<b>')
        _btn.setStyleSheet("""
            QPushButton:hover {
                border-color: white;
            }
            QToolTip {
                font:"Arial"; font-size: 15px; color: #ffffff; border: 1px solid #ffffff; 
            }
        """)

        return _btn
    
    def clicked_recorder(self):
        all_signals.stacked_sidebar_status.emit("video")

    def clicked_explorer(self):
        all_signals.stacked_sidebar_status.emit("camera")

    def clicked_solution(self):
        all_signals.stacked_sidebar_status.emit("visualization")