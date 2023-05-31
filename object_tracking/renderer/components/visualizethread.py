import cv2
import time
import timm
import torch
from torchvision import transforms
from ultralytics import YOLO
from PySide6.QtCore import QThread, Qt
from PySide6.QtGui import QImage

from ..signals import vis_signals

age_lbl = ['01-10', '11-20', '21-30',
       '31-40', '41-50', '51-60',
       '61-70', '71-80', '81-90',
    ]
gen_lbl = ['male', 'female']
device = "cuda" if torch.cuda.is_available() else "cpu"
effi = timm.create_model('tf_efficientnet_b0_ns', num_classes=11)
effi.load_state_dict(torch.load('epoch_5.pt'))
effi.to(device)
effi.eval()


class VisThread(QThread): 
    def __init__(self, path=None, parent=None) -> None:
        QThread.__init__(self, parent)
        self.is_run = None
        self.model = YOLO('yolov8n.pt')
        self.path = path
        self.cnt = 0
        self.transform = transforms.Compose([transforms.ToTensor()])

    def run(self):
        self.cap = cv2.VideoCapture(self.path)
        length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))       
        vis_signals.TotalFrame.emit(length)
        
        while self.is_run and self.cap.isOpened():
            s, frame = self.cap.read()

            if s:
                frame = cv2.resize(frame, (720, 540))
                res = self.model.track(frame)
                res_frame = res[0].plot()

                for x1, y1, x2, y2 in res.boxes.xyxy:
                    # x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    # cut = frame[y1:y2, x1:x2]
                    # cut = cv2.resize(cut, (50, 50))
                    # cut = self.transform(cut).unsqueeze(0)
                    # cut = cut.to(device)
                    # a = effi(cut)
                    # print(a)
                    # age_cls = age_lbl[int(torch.argmax(a[0][:9]))]
                    # gender_cls = gen_lbl[int(torch.argmax(a[0][9:]))]
                    # cls = str(age_cls) + str(gender_cls)
                    # cv2.putText(
                    #     res_frame, str(cls), (x1, y1), 0, 1/3,
                    #     (255, 128, 0), 1/3,lineType=cv2.LINE_AA
                    # )
                    vis_signals.CenterPt.emit(((x1+x2)//2), (y1+y2//2))

                res_frame = cv2.cvtColor(res_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = res_frame.shape
                res_frame = QImage(res_frame, w, h, ch * w, QImage.Format_RGB888)
                res_frame = res_frame.scaled(720, 540, Qt.KeepAspectRatio)

                vis_signals.streaming_vis.emit(res_frame)
                self.cnt += 1
                vis_signals.CurrentFrame.emit(self.cnt)
                time.sleep(0.01)
            else:
                self.is_run = False        
                break
        
        self.cap.release()
        vis_signals.Complete.emit(True)