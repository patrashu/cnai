import os
import xmltodict
import cv2
from glob import glob


xml_list = sorted(glob('all/*/*/*/*.xml'))
try:
    for xml in xml_list:
        file_name = xml
        png_name = file_name.replace('.xml', '.png')
        with open(file_name, 'r') as f:
            data = f.read()
        parse_data = xmltodict.parse(data)
        if parse_data['xml'] is None:
            print(file_name)
            os.remove(file_name)
            os.remove(png_name)
            continue
        gender_xml = parse_data['xml']['OBJECT']['gender']
        age_xml = parse_data['xml']['OBJECT']['age']
        if not os.path.isfile(png_name):
            os.remove(file_name)
            os.remove(png_name)
        img = cv2.imread(png_name)
        if img.shape == (0, 0, 3):
            os.remove(file_name)
            os.remove(png_name)
        

except:
    os.remove(file_name)
    os.remove(png_name)
    print(file_name)