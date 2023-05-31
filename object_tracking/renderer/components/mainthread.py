import cv2
from abc import *
from ultralytics import YOLO

from PySide6.QtCore import QThread, Qt
from PySide6.QtGui import QImage
from ..signals import all_signals


class StreamingThread(QThread):
    def __init__(self, parent=None, path=None, signal=None) -> None:
        QThread.__init__(self, parent)
        self.is_run = None
        self.model = YOLO('yolov8n.pt')
        self.model.to('cuda')
        self.video_path = path
        self.signal = signal

    def run(self):
        cap = cv2.VideoCapture(self.video_path)

        while self.is_run and cap.isOpened():
            s, frame = cap.read()
            if s:
                frame = cv2.resize(frame, (640, 480))
                res = self.model(frame)
                res = res[0].plot()
                res = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
                
                h, w, ch = res.shape
                res = QImage(res, w, h, ch * w, QImage.Format_RGB888)
                res = res.scaled(640, 480, Qt.KeepAspectRatio)

                if self.signal == 'cam1':
                    all_signals.streaming_video1.emit(res)
                elif self.signal == 'cam2':
                    all_signals.streaming_video2.emit(res)
                elif self.signal == 'cam3':
                    all_signals.streaming_video3.emit(res)
            else:
                break