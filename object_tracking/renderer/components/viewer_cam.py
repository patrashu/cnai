import json
from collections import Counter

from PySide6.QtCore import Slot, QSize, QPointF
from PySide6.QtGui import Qt, QPixmap
from PySide6.QtWidgets import (
    QPushButton, QFrame, QLabel, QFrame, QVBoxLayout, QHBoxLayout
)
from PySide6.QtGui import QPainter, QPixmap, QPen
from PySide6.QtCharts import (
    QBarCategoryAxis, QBarSeries, QBarSet, QPieSeries,
    QChart, QChartView, QScatterSeries, QLineSeries, QValueAxis
)

from ..signals import all_signals, vis_signals
from .camthread import CamThread


SAMPLE_COUNT = 10000
RESOLUTION = 4


class StreamingCam(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: #1e1e1e;") 
        
        self.device = None
        self.config = None
        self.color_control = None
        self.base_path = None

        self.main_layout = QVBoxLayout()
        self.frame = QLabel("Streaming Cam1")
        self.frame.setStyleSheet("""
            border-color: white;        
        """)
        self.frame.setAlignment(Qt.AlignCenter)
        self.frame.setFixedHeight(600)
        
        self.layout_btn = QHBoxLayout()
        self.layout_btn.setAlignment(Qt.AlignCenter)
        self.btn_open = QPushButton("Run")
        self.btn_stop = QPushButton("Stop")
        self.btn_open.setFixedSize(200, 40)
        self.btn_stop.setFixedSize(200, 40)
        
        ## Visualize Layout
        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.setAlignment(Qt.AlignLeft)

        # Visitor Graph
        self.chart_visitor = QChart()
        self.chart_visitor.setTitle("Visitor Population")
        self.chart_visitor.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view_visitor = QChartView(self.chart_visitor)        
        self.chart_view_visitor.setFixedSize(QSize(430, 350))
        self.chart_view_visitor.setRenderHint(QPainter.Antialiasing)
        self.bottom_layout.addWidget(self.chart_view_visitor)
        
        # Age Graph
        self.chart_age = QChart()
        self.chart_age.setTitle("Age Bar Chart")
        self.chart_age.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view_age = QChartView(self.chart_age)
        self.chart_view_age.setFixedSize(QSize(430, 350))
        self.chart_view_age.setRenderHint(QPainter.Antialiasing)
        self.bottom_layout.addWidget(self.chart_view_age)
        
        # Gender Graph
        self.chart_gender = QChart()
        self.chart_gender.setTitle("Gender Chart")
        self.chart_gender.setAnimationOptions(QChart.SeriesAnimations)

        self.chart_view_gender = QChartView(self.chart_gender)
        self.chart_view_gender.setFixedSize(QSize(430, 350))
        self.chart_view_gender.setRenderHint(QPainter.Antialiasing)
        self.bottom_layout.addWidget(self.chart_view_gender)

        self.btn_open.clicked.connect(self.openCam)
        self.btn_stop.clicked.connect(self.closeCam)
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

        self.main_layout.addWidget(self.frame)
        self.main_layout.addLayout(self.layout_btn)
        self.main_layout.addLayout(self.bottom_layout)
        all_signals.streaming_cam.connect(self.setFirstCam)
        vis_signals.Complete.connect(self.setDashBoard)
        self.setLayout(self.main_layout)

    def openCam(self):
        self.th1 = CamThread()
        self.th1.is_run = True
        self.th1.start()

    def closeCam(self):
        self.th1.is_run = False
        self.th1.quit()

    @Slot()
    def setFirstCam(self, value):
        self.frame.setPixmap(QPixmap.fromImage(value))


    @Slot(bool)
    def setDashBoard(self, value):
        with open("./result/result_person.json", "r") as f:
            datas = json.load(f)
        with open("./result/visitor.json", "r") as f:
            se_datas = json.load(f)

        ids = []
        ages = []
        genders = []
        for id, v in datas.items():
            ids.append(id)
            ages.append(v[0])
            genders.append(v[1])
        pts = []
        for idx, v in se_datas.items():
            pts.append((int(idx), int(v)))
        
        ages = [int(f'{age[0]}') for age in ages]
        total_ages = [0 for _ in range(9)]
        for num in ages:
            total_ages[num] += 1

        genders = Counter(genders)

        ## Line Chart
        series_visitor = QLineSeries()
        series_scatter = QScatterSeries()
        series_scatter.setMarkerSize(0.1)
        # pts = [
        #     (1, 10), (2, 15), (3, 17), (4, 10),
        #     (5, 14), (6, 19), (7, 18), (8, 10)
        # ]
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
        bar_age.append(total_ages)
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
        series_gender.append("male", genders["male"])
        series_gender.append("female", genders["female"])
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