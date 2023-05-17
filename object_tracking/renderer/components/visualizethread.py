import cv2
from ultralytics import YOLO

from PySide6.QtCore import QThread, Qt
from PySide6.QtGui import QImage
from ..signals import vis_signals

class VisThread(QThread): 
    def __init__(self, path=None, parent=None) -> None:
        QThread.__init__(self, parent)
        self.is_run = None
        self.model = YOLO('yolov8n.pt')
        self.path = path
        self.cnt = 0

    def run(self):
        self.cap = cv2.VideoCapture(self.path)
        length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))       
        vis_signals.TotalFrame.emit(length)
        
        while self.is_run and self.cap.isOpened():
            s, frame = self.cap.read()

            if s:
                res = self.model(frame)
                res = res[0].plot()
                res = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
                
                h, w, ch = res.shape
                res = QImage(res, w, h, ch * w, QImage.Format_RGB888)
                res = res.scaled(720, 540, Qt.KeepAspectRatio)

                vis_signals.streaming_vis.emit(res)
                self.cnt += 1
                vis_signals.CurrentFrame.emit(self.cnt)
            else:
                self.is_run = False        
                break
        
        self.cap.release()
        vis_signals.Complete.emit(True)