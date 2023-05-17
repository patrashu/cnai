import cv2
from ultralytics import YOLO

from PySide6.QtCore import QThread, Qt
from PySide6.QtGui import QImage
from ..signals import all_signals

class CamThread(QThread): 
    def __init__(self, parent=None) -> None:
        QThread.__init__(self, parent)
        self.is_run = None
        self.model = YOLO('yolov8n.pt')

    def run(self):
        cap = cv2.VideoCapture(0)
        while self.is_run and cap.isOpened():
            s, frame = cap.read()

            if s:
                res = self.model(frame)
                res = res[0].plot()
                res = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
                
                h, w, ch = res.shape
                res = QImage(res, w, h, ch * w, QImage.Format_RGB888)
                res = res.scaled(1080, 720, Qt.KeepAspectRatio)

                all_signals.streaming_cam.emit(res)