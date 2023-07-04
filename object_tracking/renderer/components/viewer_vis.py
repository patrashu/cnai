import os
from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QProgressBar, QPushButton
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.patches as patches
from matplotlib.figure import Figure

from ultralytics import YOLO

from .visualizethread import VisThread, BackEnd
from ..common_widgets import Frame
from ..signals import vis_signals

os.environ['KMP_DUPLICATE_LIB_OK']='True'


class Visualization(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.setContentsMargins(0, 0, 0, 0)
        self.is_minimap = True
        
        self.root_path = '/'.join(os.path.abspath('assets/').split('\\')[:-1])
        self.setStyleSheet("background-color: #1e1e1e;") 
        self.dashboard_layout = QVBoxLayout()
        self.dashboard_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)

        self.frame_layout = QHBoxLayout()
        self.frame_cam = Frame("Cam1")
        self.frame_cam.setFixedSize(QSize(880, 880))
        self.fig = Figure()
        self.fig.tight_layout()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Visitor Movement")
        self.ax.margins(0)
        
        self.minimap_frame = QFrame()
        self.minimap_frame.setFixedSize(400, 400)
        self.minimap_layout = QHBoxLayout(self.minimap_frame)
        self.minimap = FigureCanvas(self.fig)
        self.minimap_layout.addWidget(self.minimap)

        self.frame_layout.addWidget(self.frame_cam)
        self.frame_layout.addWidget(self.minimap_frame)
        self.dashboard_layout.addLayout(self.frame_layout)

        self.middle_layout = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_start.setStyleSheet("""
            QPushButton:hover {
                border-color: "white";
            }
        """)
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.setStyleSheet("""
            QPushButton:hover {
                border-color: "white";
            }
        """)
        self.btn_start.setFixedSize(250, 50)
        self.btn_pause.setFixedSize(250, 50)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedSize(780, 50)
        self.total_frame = None

        self.middle_layout.addWidget(self.btn_start)
        self.middle_layout.addWidget(self.btn_pause)
        self.middle_layout.addWidget(self.progress_bar)
        self.dashboard_layout.addLayout(self.middle_layout)

        self.setLayout(self.dashboard_layout)

        self.btn_start.clicked.connect(self.openCam)
        self.btn_pause.clicked.connect(self.toggleCam)
        vis_signals.streaming_vis.connect(self.setFrame)
        vis_signals.TotalFrame.connect(self.progressStart)
        vis_signals.CurrentFrame.connect(self.progressChange)
        vis_signals.CenterPt.connect(self.add_circle)


    def openCam(self):
        model = YOLO('./checkpoints/yolov8x.pt')
        self.th0 = BackEnd(path=os.path.join(self.root_path, "./object_tracking/assets/test.mp4"))
        self.th0.is_run = True
        self.th1 = VisThread(path=os.path.join(self.root_path, "./object_tracking/assets/test.mp4"), model=model)
        self.th1.is_run = True
        self.th0.start()
        self.th1.start()

    def toggleCam(self):
        if self.th0 and self.th0.is_run:
            self.th0.is_run = False
            self.th1.is_run = False
            self.btn_pause.setText("Resume")
        else:
            self.th0.is_run = False
            self.th1.is_run = False
            self.btn_pause.setText("Pause")


    @Slot(int)
    def setFrame(self, value):
        self.frame_cam.frame.setPixmap(QPixmap.fromImage(value))

    @Slot(int)
    def progressStart(self, value):
        self.total_frame = value
    
    @Slot(int)
    def progressChange(self, value):
        tmp = (value / self.total_frame) * 100
        self.progress_bar.setValue(tmp)
        self.progress_bar.setFormat("%.02f %%" % tmp)
        self.ax.cla()
        self.is_minimap = True

    @Slot(list)
    def add_circle(self, value):
        if self.is_minimap:
            self.ax.set_title("Visitor Movement")
            self.ax.axis("off")
            self.ax.add_patch(
                patches.Rectangle(
                    (0, 0), 1, 1, facecolor='red', alpha=0.2
                )
            )
            self.is_minimap = False

        self.ax.add_patch(
            patches.Circle(
                (value[0]/720, 1-value[1]/540), radius=0.01
            )
        )
        self.minimap.draw()