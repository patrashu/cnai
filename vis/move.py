from shutil import copyfile
from glob import glob

txt_list = sorted(glob('train/labels/*.txt'))
for txt in txt_list:
    with open(txt, 'r') as f:
        data = f.readlines()
    print(data)
    data = data[0].split(' ')
    cls, x1, y1, x2, y2 = data
    print(cls, x1, y1, x2, y2)