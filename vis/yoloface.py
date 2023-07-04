import cv2

import torch
from torch import nn
from torchvision import models
import torchvision.transforms as transforms

from ultralytics import YOLO
import timm

age_lbl = ['01-10', '11-20', '21-30', 
       '31-40', '41-50', '51-60', 
       '61-70', '71-80', '81-90', 
    ]
gen_lbl = ['male', 'female']

runOn = "cuda:1" if torch.cuda.is_available() else "cpu"

model = YOLO('yolov8x.pt')
effi = timm.create_model('tf_efficientnet_b1_ns', num_classes=11)
effi.load_state_dict(torch.load('best.ckpt'))

effi.to(runOn)
effi.eval()

video_path = 'ch03_cut.mp4'
newPath = 'cv05.mp4'
output = cv2.VideoWriter(newPath, cv2.VideoWriter_fourcc(*'DIVX'), 20, (1920, 1080))
cap = cv2.VideoCapture(video_path)
cmt = 0
temp = []
transform = transforms.Compose([transforms.ToTensor()])
while cap.isOpened():
    success, frame = cap.read()
    if success:
        results = model(frame, classes=0)
        for result in results:
            result = result.cpu().numpy()
            for x1, y1, x2, y2 in result.boxes.xyxy:
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cut = frame[y1:y2, x1:x2]
                cut = cv2.resize(cut, (50, 50))
                cut = transform(cut).unsqueeze(0)
                cut = cut.to(runOn)
                a = effi(cut)
                print(a)

                age_cls = age_lbl[int(torch.argmax(a[0][:9]))]
                gender_cls = gen_lbl[int(torch.argmax(a[0][9:]))]
                cls = str(age_cls) + str(gender_cls)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 0, cv2.LINE_AA)
                cv2.putText(
                    frame, str(cls), (x1+10, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (225, 255, 255), thickness=1, lineType=cv2.LINE_AA)
                print(cls)
        output.write(frame)
    else:
        break
output.release()
cap.release()
cv2.destroyAllWindows()
