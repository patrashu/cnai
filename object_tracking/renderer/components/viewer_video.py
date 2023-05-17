import os
from PySide6.QtCore import Qt, QEvent, QMimeData, Slot
from PySide6.QtGui import QDrag, QImage, QPixmap
from PySide6.QtWidgets import (
    QPushButton, QFrame, QGridLayout, QHBoxLayout
)

from ..common_widgets import Frame
from ..signals import all_signals
from .mainthread import StreamingThread


SAMPLE_COUNT = 10000
RESOLUTION = 4


class StreamingVideo(QFrame):
    def __init__(self) -> None:
        super().__init__()

        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: #1e1e1e;") 
        
        self.root_path = '/'.join(os.path.abspath('assets/').split('\\')[:-1])
        self.device = None
        self.config = None
        self.color_control = None
        self.base_path = None

        self.grid_layout = QGridLayout()
        self.frame_cam1 = Frame("Cam1")
        self.frame_cam2 = Frame("Cam2")
        self.frame_cam3 = Frame("Cam3")
        self.frame_map = Frame("minimap")
        
        self.layout_btn = QHBoxLayout()
        self.btn_open = QPushButton("Run")
        self.btn_stop = QPushButton("Stop")
        self.btn_open.setFixedSize(200, 40)
        self.btn_stop.setFixedSize(200, 40)

        self.btn_open.clicked.connect(self.openCam)
        self.btn_stop.clicked.connect(self.closeCam)
        self.btn_stop.setEnabled(False)

        self.layout_btn.setAlignment(Qt.AlignCenter)
        self.btn_open.setStyleSheet("""
            QPushButton:hover {
                border-color: "white";
            }
        """)
        self.btn_stop.setStyleSheet("""
            QPushButton:hover {
                border-color: "white";
            }
        """)

        self.layout_btn.addWidget(self.btn_open)
        self.layout_btn.addWidget(self.btn_stop)
        self.grid_layout.addWidget(self.frame_cam1, 0, 0)
        self.grid_layout.addWidget(self.frame_cam2, 0, 1)
        self.grid_layout.addWidget(self.frame_cam3, 1, 0)
        self.grid_layout.addWidget(self.frame_map, 1, 1)
        self.grid_layout.addLayout(self.layout_btn, 2, 0, 1, 2)

        all_signals.streaming_video1.connect(self.setFirstCam)
        all_signals.streaming_video2.connect(self.setSecondCam)
        all_signals.streaming_video3.connect(self.setThirdCam)

        self.setLayout(self.grid_layout)

    def openCam(self):
        self.btn_open.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.th1 = StreamingThread(path=os.path.join(self.root_path, "object_tracking/assets/ch02_cut.mp4"), signal='cam1')
        self.th1.is_run = True
        self.th1.start()
        self.th2 = StreamingThread(path=os.path.join(self.root_path, "object_tracking/assets/ch03_cut.mp4"), signal='cam2')
        self.th2.is_run = True
        self.th2.start()
        self.th3 = StreamingThread(path=os.path.join(self.root_path, "object_tracking/assets/ch04_cut.mp4"), signal='cam3')
        self.th3.is_run = True
        self.th3.start()
    
    def closeCam(self):
        self.btn_open.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.th1.is_run = False
        self.th1.quit()
        self.th2.is_run = False
        self.th2.quit()
        self.th3.is_run = False
        self.th3.quit()

    @Slot(QImage)
    def setFirstCam(self, value):
        self.frame_cam1.frame.setPixmap(QPixmap.fromImage(value))

    @Slot(QImage)
    def setSecondCam(self, value):
        self.frame_cam2.frame.setPixmap(QPixmap.fromImage(value))

    @Slot(QImage)
    def setThirdCam(self, value):
        self.frame_cam3.frame.setPixmap(QPixmap.fromImage(value))