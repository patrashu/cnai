import os
from glob import glob
import xmltodict

from PIL import Image


Groups = ['10', '20', 
          '30', '40', '50', 
          '60', '70', '80', '90']
lbl = ['01-10male', '01-10female', '11-20male', '11-20female', '21-30male', '21-30female', 
       '31-40male', '31-40female', '41-50male', '41-50female', '51-60male', '51-60female', 
       '61-70male', '61-70female', '71-80male', '71-80female', '81-90male', '81-90female', 
    ]

txt_list = sorted(glob('./all/*/*/*/*.txt'))
for txt in txt_list:
    txt_name = txt.split('/')[2]
    txt_out = txt.replace('label', 'labels')
    yolo_txt = 'runs/detect/predict/labels/' + txt_name
    if not os.path.isfile(yolo_txt):
        print('not file', yolo_txt)
        continue
    with open(yolo_txt, 'r') as f:
        yolo_data = f.readlines()
    if yolo_data is None and yolo_data == []:
        print('none', yolo_txt)
        continue
    with open(txt, 'r') as f:
        txt_data = f.read()
    temp = []
    for yolo in yolo_data:
        cls, cx, cy, w, h = yolo.split(' ')
        temp.append([txt_data, cx, cy, w, h])
    with open(txt_out, 'w') as f:
        for tmp in temp:
            cls, cx, cy, w, h = tmp
            f.writelines(f'{cls} {cx} {cy} {w} {h}')