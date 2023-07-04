import os
import json
import shutil
from glob import glob

import cv2

from PySide6.QtCore import QThread, Qt, Slot
from PySide6.QtGui import QImage

import torch
from torch import nn
import torch.optim as optim
from torchvision import transforms
import pytorch_lightning as pl

import timm
from ultralytics import YOLO

from ..signals import vis_signals


age_lbl = ['01-10', '11-20', '21-30',
       '31-40', '41-50', '51-60',
       '61-70', '71-80', '81-90',
        ]
gen_lbl = ['male', 'female']
age_classes = 9
gender_classes = 2

device = "cuda" if torch.cuda.is_available() else "cpu"
timm_model = timm.create_model('tf_efficientnet_b1_ns', num_classes=age_classes+gender_classes)


class PLModel(pl.LightningModule):
    def __init__(self, model, loss):
        super().__init__()
        self.model = model
        self.loss_age = loss['age']
        self.loss_gender = loss['gender']

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        images, targets = batch

        images = self.model(images)
        sigmoid = nn.Sigmoid()
        images = sigmoid(images)
        x_age = images[:,:age_classes]
        y_age = targets[:,:age_classes]
        x_gender = images[:,age_classes:]
        y_gender = targets[:,age_classes:]

        age_loss = self.loss_age(x_age, y_age)
        gender_loss = self.loss_gender(x_gender, y_gender)
        loss = age_loss + gender_loss

        self.log("train_loss", loss, on_step=True, on_epoch=True, prog_bar=True, logger=True)
        return loss
    
    def validation_step(self, batch, batch_idx):
        images, targets = batch
        images = self.model(images)
        sigmoid = nn.Sigmoid()
        images = sigmoid(images)

        x_age = images[:,:age_classes]
        y_age = targets[:,:age_classes]
        x_gender = images[:,age_classes:]
        y_gender = targets[:,age_classes:]

        age_loss = self.loss_age(x_age, y_age)
        gender_loss = self.loss_gender(x_gender, y_gender)
        loss = age_loss + gender_loss

        self.log("valid_loss", loss, on_step=True, on_epoch=True, prog_bar=True, logger=True)
        return loss


    def configure_optimizers(self):
        optimizer = optim.Adam(self.parameters(), lr=1e-3)
        return optimizer


class BackEnd(QThread):
    def __init__(self, path=None, parent=None) -> None:
        QThread.__init__(self, parent)
        self.is_run = None
        model = YOLO('./checkpoints/yolov8x.pt')
        self.model = model
        self.path = path

    def run(self):
        self.model.track(source=self.path, save_txt=True, vid_stride=30, classes=0)


class VisThread(QThread): 
    def __init__(self, path=None, model=None, parent=None) -> None:
        QThread.__init__(self, parent)
        self.is_run = None
        self.model = model
        self.path = path
        self.cnt = 1
        self.visitor = 0
        self.transform = transforms.Compose([transforms.ToTensor(), transforms.Resize((240, 240))])

        self.ids = []
        self.dicts = {}
        self.dictes ={}
        vis_signals.ObjectId.connect(self.set_id)
        model_path = './checkpoints/best.ckpt'
        loss = {'age': nn.MSELoss(), 'gender': nn.BCELoss()}
        self.pl_model = PLModel.load_from_checkpoint(model=timm_model, loss=loss, checkpoint_path=model_path)
        self.pl_model.to(device)
        self.pl_model.eval()

    def run(self):
        if os.path.exists('runs'):
            shutil.rmtree('runs')
        self.cap = cv2.VideoCapture(self.path)
        length = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        vis_signals.TotalFrame.emit(length)
        while self.is_run and self.cap.isOpened():
            s, frame = self.cap.read()
            if s:
                if self.cnt % 30 == 0:
                    frame = cv2.resize(frame, (640, 544))
                    ress = self.model(frame)
                    res_frame = ress[0].plot()
                    temp = []

                    for res in ress:
                        res = res.cpu().numpy()
                        for i, (x1, y1, x2, y2) in enumerate(res.boxes.xyxy):
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                            cut = frame[y1:y2, x1:x2]
                            cut = self.transform(cut).unsqueeze(0)
                            cut = cut.to(device)
                            result = self.pl_model(cut)
                            age_cls = age_lbl[int(torch.argmax(result[0][:9]))]
                            gender_cls = gen_lbl[int(torch.argmax(result[0][9:]))]
                            cls = str(age_cls) + str(gender_cls)
                            cv2.rectangle(res_frame, (x1, y1), (x1+70, y1-9), (0, 0, 255), -1, cv2.LINE_AA)
                            cv2.putText(
                                res_frame, str(cls), (x1, y1), 0, 1/3,
                                (255, 255, 255), 1, lineType=cv2.LINE_AA
                            )
                            vis_signals.CenterPt.emit([(x1+x2)//2, (y1+y2)//2])
                            temp.append([i, x1, y1, x2, y2, cls])
                            self.visitor += 1
                    self.dicts[self.cnt // 30] = self.visitor
                    self.dictes[self.cnt] = temp
                    self.ids = []
                    res_frame = cv2.cvtColor(res_frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = res_frame.shape
                    res_frame = QImage(res_frame, w, h, ch * w, QImage.Format_RGB888)
                    res_frame = res_frame.scaled(960, 720, Qt.KeepAspectRatio)

                    vis_signals.streaming_vis.emit(res_frame)
                    vis_signals.CurrentFrame.emit(self.cnt)
                self.cnt += 1
                self.visitor = 0

            else:
                vis_signals.streaming_vis.emit(res_frame)
                vis_signals.CurrentFrame.emit(length)
                self.is_run = False
                output_path = "./result/age_gender.json"
                with open(output_path, 'w') as f:
                    json.dump(self.dictes, f)
                output_path = "./result/visitor.json"
                with open(output_path, 'w') as f:
                    json.dump(self.dicts, f)
                break
        self.cap.release()

    @Slot(str)
    def set_id(self, value):
        self.ids.append(value)