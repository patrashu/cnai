import cv2
import json
from glob import glob

from PySide6.QtCore import QThread, Qt
from PySide6.QtGui import QImage

from ultralytics import YOLO

from ..signals import all_signals, vis_signals


class CamThread(QThread): 
    def __init__(self, parent=None) -> None:
        QThread.__init__(self, parent)
        self.is_run = None
        self.cnt = 1
        self.path = './object_tracking/assets/test.mp4'

    def run(self):
        txt_list = sorted(glob('./runs/detect/*/labels/*.txt'), key=lambda x: (int(x.split('/')[-1][5:-4])))
        print(txt_list[:100])
        track = []
        for idx, txt in enumerate(txt_list):
            with open(txt) as f:
                track.append([idx+1, f.readlines()])
        with open('./result/age_gender.json') as f:
            age_gender = json.load(f)
        age_gender_key = age_gender.keys()

        postprocess_track = []
        for idxxywh in track:
            frame = int(idxxywh[0])
            for xywh in idxxywh[1]:
                print(xywh)
                print(frame)
                _, xc, yc, w, h, id = xywh.split()
                xc, yc, w, h = float(xc), float(yc), float(w), float(h)
                x1 = int((xc - w / 2) * 640)
                y1 = int((yc - h / 2) * 544)
                x2 = int((xc + w / 2) * 640)
                y2 = int((yc + h / 2) * 544)
                id = int(id)
                postprocess_track.append([frame, x1, y1, x2, y2, id])
        postprocess_agegen = []
        for idx, k in enumerate(age_gender_key):
            for xyxy in age_gender[k]:
                _, x1, y1, x2, y2, agegen = xyxy
                x1 = int(x1)
                y1 = int(y1)
                x2 = int(x2)
                y2 = int(y2)
                postprocess_agegen.append([idx+1, x1, y1, x2, y2, agegen])

        result = []
        for track in postprocess_track:
            for agegen in postprocess_agegen:
                if agegen[0] == track[0]:
                    if abs(agegen[1] - track[1]) < 50 and \
                    abs(agegen[2] - track[2]) < 50 and \
                    abs(agegen[3] - track[3]) < 50 and \
                    abs(agegen[4] - track[4]) < 50: 
                        result.append([track[0], track[1], track[2], track[3], track[4], track[5], agegen[5]])
        cap = cv2.VideoCapture(self.path)
        while self.is_run and cap.isOpened():
            s, frame = cap.read()

            if s:
                if self.cnt % 30 == 0:
                    frame = cv2.resize(frame, (640, 544))
                    for res in result:
                        if res[0] == self.cnt // 30:
                            _, x1, y1, x2, y2, id, agegen = res
                            p1, p2 = (x1, y1), (x2, y2)
                            cv2.rectangle(frame, p1, p2, (0, 0, 255), 1, lineType=cv2.LINE_AA)
                            id_cls = f"id: {str(id)}"
                            agegen_cls = f"cls: {str(agegen)}"
                            cv2.rectangle(frame, (x1, y1), (x1+93, y1-9), (0, 0, 255), -1, cv2.LINE_AA)
                            cv2.rectangle(frame, (x1, y1), (x1+32, y1-18), (0, 0, 255), -1, cv2.LINE_AA)
                            cv2.putText(frame, id_cls, (x1, y1-9), 0, 1/3, (255, 255, 255), 1, lineType=cv2.LINE_AA)
                            cv2.putText(frame, agegen_cls, (x1, y1), 0, 1/3, (255, 255, 255), 1, lineType=cv2.LINE_AA)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    h, w, ch = frame.shape
                    frame = QImage(frame, w, h, ch * w, QImage.Format_RGB888)
                    frame = frame.scaled(1080, 720, Qt.KeepAspectRatio)

                    all_signals.streaming_cam.emit(frame)
                self.cnt += 1
            else:
                json_save = {}
                self.is_run = False
                for res in result:
                    frame, x1, y1, x2, y2, id, cls = res
                    age, gender = cls[0:5], cls[5:]
                    json_save[str(id)] = [age, gender]
                output_path = "./result/result_person.json"
                with open(output_path, 'w') as f:
                    json.dump(json_save, f)
                vis_signals.Complete.emit(True)
                break
        cap.release()