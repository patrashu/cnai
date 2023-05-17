
import os
from PySide6.QtCore import QPointF, QSize, Qt, Slot
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, 
    QPushButton, QProgressBar
)
from PySide6.QtCharts import (
    QBarCategoryAxis, QBarSeries, QBarSet, QPieSeries,
    QChart, QChartView, QValueAxis, QLineSeries
)
from .visualizethread import VisThread
from ..common_widgets import Frame, PushButton
from ..signals import vis_signals


class Visualization(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.setContentsMargins(0, 0, 0, 0)
        
        self.root_path = '/'.join(os.path.abspath('assets/').split('\\')[:-1])
        self.setStyleSheet("background-color: #1e1e1e;") 
        self.dashboard_layout = QVBoxLayout()
        self.dashboard_layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)

        self.frame_layout = QHBoxLayout()
        self.frame_cam = Frame("Cam1")
        self.frame_cam.setFixedSize(QSize(720, 540))
        self.frame_layout.addWidget(self.frame_cam)
        self.dashboard_layout.addLayout(self.frame_layout)

        self.middle_layout = QHBoxLayout()
        self.btn_start = PushButton("Start")
        self.btn_start.setFixedSize(250, 40)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedSize(1000, 40)
        self.total_frame = None

        self.middle_layout.addWidget(self.btn_start)
        self.middle_layout.addWidget(self.progress_bar)
        self.dashboard_layout.addLayout(self.middle_layout)

        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.setAlignment(Qt.AlignLeft)

        # Visitor Graph
        self.series_floating = QLineSeries()
        self.series_visitor = QLineSeries()
        self.chart_visitor = QChart()
        self.chart_visitor.addSeries(self.series_floating)
        self.chart_visitor.addSeries(self.series_visitor)
        self.chart_visitor.createDefaultAxes()
        self.chart_visitor.setTitle("Visitor and Floating Population")
        self.chart_visitor.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view_visitor = QChartView(self.chart_visitor)        
        self.chart_view_visitor.setFixedSize(QSize(420, 420))
        self.chart_view_visitor.setRenderHint(QPainter.Antialiasing)
        self.bottom_layout.addWidget(self.chart_view_visitor)
        
        # Age Graph
        self.bar_age = QBarSet("Person")
        self.series_age = QBarSeries()
        self.series_age.append(self.bar_age)
        
        self.chart_age = QChart()
        self.chart_age.addSeries(self.series_age)
        self.chart_age.setTitle("Age Bar Chart")
        self.chart_age.setAnimationOptions(QChart.SeriesAnimations)

        self.categories_age = ['0', '10', '20', '30', '40', '50', '60', '70', '80']
        self.chart_age_axis_x = QBarCategoryAxis()
        self.chart_age_axis_x.append(self.categories_age)
        self.chart_age.addAxis(self.chart_age_axis_x, Qt.AlignBottom)
        self.series_age.attachAxis(self.chart_age_axis_x)

        self.chart_age_axis_y = QValueAxis()
        self.chart_age.addAxis(self.chart_age_axis_y, Qt.AlignLeft)
        self.series_age.attachAxis(self.chart_age_axis_y)

        self.chart_age.legend().setVisible(True)
        self.chart_age.legend().setAlignment(Qt.AlignBottom)

        self.chart_view_age = QChartView(self.chart_age)
        self.chart_view_age.setFixedSize(QSize(420, 420))
        self.chart_view_age.setRenderHint(QPainter.Antialiasing)
        self.bottom_layout.addWidget(self.chart_view_age)

        # Gender Graph
        self.sum_gender = []
        self.series_gender = QPieSeries()
        # self.chart_gender_slice = self.series_gender.slices()[0]
        # self.chart_gender_slice.setExploded()
        # self.chart_gender_slice.setLabelVisible()

        self.chart_gender = QChart()
        self.chart_gender.addSeries(self.series_gender)
        self.chart_gender.setTitle("Gender Chart")
        self.chart_gender.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view_gender = QChartView(self.chart_gender)
        self.chart_view_gender.setFixedSize(QSize(420, 420))
        self.chart_view_gender.setRenderHint(QPainter.Antialiasing)
        self.bottom_layout.addWidget(self.chart_view_gender)
        
        self.dashboard_layout.addLayout(self.bottom_layout)
        self.setLayout(self.dashboard_layout)

        self.btn_start.clicked.connect(self.openCam)
        vis_signals.streaming_vis.connect(self.setFrame)
        vis_signals.TotalFrame.connect(self.progressStart)
        vis_signals.Complete.connect(self.setDashBoard)
        vis_signals.CurrentFrame.connect(self.progressChange)

    def openCam(self):
        self.th1 = VisThread(path=os.path.join(self.root_path, "object_tracking/assets/ch03_cut.mp4"))
        self.th1.is_run = True
        self.th1.start()

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

    @Slot(bool)
    def setDashBoard(self, value):
        pass

        ## Line Chart



        ## person bar
        # self.bar_person.append([])


        ## Sum_gender
        # self.series_gender.append(s[0], s[1])

