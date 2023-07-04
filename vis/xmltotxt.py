from glob import glob
import os
import xmltodict
from shutil import copyfile

Groups = ['10', '20', 
          '30', '40', '50', 
          '60', '70', '80', '90']
lbl = ['01-10male', '01-10female', '11-20male', '11-20female', '21-30male', '21-30female', 
       '31-40male', '31-40female', '41-50male', '41-50female', '51-60male', '51-60female', 
       '61-70male', '61-70female', '71-80male', '71-80female', '81-90male', '81-90female', 
    ]

xml_list = sorted(glob('all/*/*/*/*.xml'))

for xml in xml_list:
    file_name = xml
    txt_name = file_name.split('/')[4]
    txt_name = txt_name.replace('xml', 'txt')
    txt_name = 'root/taek/cnai/label/' + txt_name

    with open(xml, 'r') as f:
        data = f.read()
    parse_data = xmltodict.parse(data)
    image_name = txt_name.replace('label', 'img')
    gender_xml = parse_data['xml']['OBJECT']['gender']
    age_xml = parse_data['xml']['OBJECT']['age']
    if age_xml is None:
        print(xml)
    for gro in Groups:
        if gro >= age_xml:
            label = '{0}-{1}{2}'.format(int(gro)-9, gro, gender_xml)
            break
    for idx, i in enumerate(lbl):
        if i == label:
            cls = idx
    with open(txt_name, 'w') as f:
        f.writelines(f'{cls}')
    # copyfile(txt_name, image_name)
    # with open(text_name, "w") as f:
    #     f.writelines(f'{cls} 0.5 0.5 1.0 1.0')