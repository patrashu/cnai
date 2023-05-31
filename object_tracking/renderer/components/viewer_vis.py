
import os
from PySide6.QtCore import QPointF, QSize, Qt, Slot
from PySide6.QtGui import QPainter, QPixmap, QPen
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QProgressBar, QPushButton
)
from PySide6.QtCharts import (
    QBarCategoryAxis, QBarSeries, QBarSet, QPieSeries,
    QChart, QChartView, QScatterSeries, QLineSeries, QValueAxis
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.figure import Figure

from .visualizethread import VisThread
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
        self.frame_cam.setFixedSize(QSize(720, 520))
        self.fig = Figure()
        self.fig.tight_layout()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Visitor Movement")
        self.ax.margins(0)
        
        self.minimap = FigureCanvas(self.fig)

        self.frame_layout.addWidget(self.frame_cam)
        self.frame_layout.addWidget(self.minimap)
        self.dashboard_layout.addLayout(self.frame_layout)

        self.middle_layout = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_start.setStyleSheet("""
            QPushButton:hover {
                border-color: "white";
            }
        """)
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
        self.chart_visitor = QChart()
        self.chart_visitor.setTitle("Visitor Population")
        self.chart_visitor.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view_visitor = QChartView(self.chart_visitor)        
        self.chart_view_visitor.setFixedSize(QSize(430, 430))
        self.chart_view_visitor.setRenderHint(QPainter.Antialiasing)
        self.bottom_layout.addWidget(self.chart_view_visitor)
        
        # Age Graph
        self.chart_age = QChart()
        self.chart_age.setTitle("Age Bar Chart")
        self.chart_age.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view_age = QChartView(self.chart_age)
        self.chart_view_age.setFixedSize(QSize(430, 430))
        self.chart_view_age.setRenderHint(QPainter.Antialiasing)
        self.bottom_layout.addWidget(self.chart_view_age)

        # Gender Graph
        self.chart_gender = QChart()
        self.chart_gender.setTitle("Gender Chart")
        self.chart_gender.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view_gender = QChartView(self.chart_gender)
        self.chart_view_gender.setFixedSize(QSize(430, 430))
        self.chart_view_gender.setRenderHint(QPainter.Antialiasing)
        self.bottom_layout.addWidget(self.chart_view_gender)
        
        self.dashboard_layout.addLayout(self.bottom_layout)
        self.setLayout(self.dashboard_layout)

        self.btn_start.clicked.connect(self.openCam)
        vis_signals.streaming_vis.connect(self.setFrame)
        vis_signals.TotalFrame.connect(self.progressStart)
        vis_signals.Complete.connect(self.setDashBoard)
        vis_signals.CurrentFrame.connect(self.progressChange)
        vis_signals.CenterPt.connect(self.add_circle)


    def openCam(self):
        self.th1 = VisThread(path=os.path.join(self.root_path, "object_tracking/assets/test.mp4"))
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
        # self.ax.text(
        #     value[0]/720, 1-value[1]/540+0.04
        # )
        self.minimap.draw()


    @Slot(bool)
    def setDashBoard(self, value):
        ## Line Chart
        series_visitor = QLineSeries()
        series_scatter = QScatterSeries()
        series_scatter.setMarkerSize(7.0)
        pts = [
            (1, 10), (2, 15), (3, 17), (4, 10),
            (5, 14), (6, 19), (7, 18), (8, 10)
        ]
        max_value = max([x[1] for x in pts])
        for pt in pts:
            series_visitor.append(QPointF(*pt))
            series_scatter.append(*pt)
        self.chart_visitor.addSeries(series_scatter)
        self.chart_visitor.addSeries(series_visitor)

        series_scatter.setPen(QPen(Qt.blue, 1))
        series_visitor.setPen(QPen(Qt.blue, 1))
        visitor_y_axis = QValueAxis()
        visitor_y_axis.setRange(0, max_value+5)
        self.chart_visitor.setAxisY(visitor_y_axis, series_visitor)

        self.categories_visitor = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.chart_visitor_axis_x = QBarCategoryAxis()
        self.chart_visitor_axis_x.append(self.categories_visitor)
        self.chart_visitor.setAxisX(self.chart_visitor_axis_x, series_visitor)
        self.chart_visitor.createDefaultAxes()
        self.chart_visitor.legend().hide()

        self.chart_view_visitor.update()

        ## person bar
        bar_age = QBarSet("Person")
        bar_age.append([100, 200, 400, 500, 300, 100, 200, 300, 500])
        series_age = QBarSeries()
        series_age.append(bar_age)
        self.chart_age.addSeries(series_age)
        self.chart_age.createDefaultAxes()
        self.chart_age.legend().hide()

        self.categories_age = ['0', '10', '20', '30', '40', '50', '60', '70', '80']
        self.chart_age_axis_x = QBarCategoryAxis()
        self.chart_age_axis_x.append(self.categories_age)
        self.chart_age.setAxisX(self.chart_age_axis_x)
        self.chart_view_age.update()

        ## Sum_gender
        series_gender = QPieSeries()
        series_gender.append("Man", 60)
        series_gender.append("Woman", 40)
        chart_gender_slice = series_gender.slices()[0]
        chart_gender_slice.setExploded()
        chart_gender_slice.setLabelVisible()
        chart_gender_slice.setPen(QPen(Qt.black, 1))
        chart_gender_slice.setBrush(Qt.darkRed)

        chart_gender_slice = series_gender.slices()[1]
        chart_gender_slice.setExploded()
        chart_gender_slice.setLabelVisible()
        chart_gender_slice.setPen(QPen(Qt.black, 1))
        chart_gender_slice.setBrush(Qt.darkBlue)

        self.chart_gender.addSeries(series_gender)
        self.chart_gender.createDefaultAxes()
        self.chart_view_gender.update()
