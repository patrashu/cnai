import os, time
from datetime import datetime
from glob import glob

import cv2
import numpy as np
import torch
import torchvision.transforms as transforms

import timm


root_path = './korean/'
TRAIN_PATH = sorted(glob(root_path + 'train/labels/*.png'))
VAL_PATH = sorted(glob(root_path + '/val/labels/*.png'))

model = timm.create_model('tf_efficientnet_b1_ns', pretrained=True, num_classes=16)
run = "cuda:0" if torch.cuda.is_available() else "cpu"
model.to(run)


class AGE_GENDER(torch.utils.data.Dataset):
    def __init__(self, fileList, transform=None):
        self.fileList = fileList
        self.transform = transform
    
    def __getitem__(self, i):
        imgName = self.fileList[i]
        IMG = cv2.imread(imgName)
        if IMG is None:
            os.remove(imgName)
            pass
        img = cv2.cvtColor(IMG, cv2.COLOR_BGR2RGB).astype(np.float32)
        img /= 255.0
        txt = imgName.replace('.png', '.txt')
        with open(txt, 'r') as f:
            data = f.readlines()
        data = data[0].split(' ')
        cls, x1, y1, x2, y2 = data
        cls= int(cls)
        if self.transform: 
            img = self.transform(img)
        x = img
        y = cls
        return x, y

    def __len__(self):
        return len(self.fileList)
    
transform = transforms.Compose([transforms.ToTensor(), 
                                transforms.Normalize((0.5,), (0.5,)),
                                transforms.RandomRotation(10),
                                transforms.Resize((224, 224))])

TRAIN_DATASET = AGE_GENDER(TRAIN_PATH, transform)
VALIDATION_DATASET = AGE_GENDER(VAL_PATH, transform)

def train(MyModel, DATA, Optimizer, Epochs, onDevice, batchSize):
    MyModel.to(onDevice)
    runID = time.time()
    TRAIN_DATA, VALIDATION_DATA = DATA['TRAIN'], DATA['VALIDATION']
    lossHistory, bestLoss = {'TRAIN': [], 'VALIDATION': []}, -1
    validationLoss = -1
    criterion = torch.nn.CrossEntropyLoss()

    trainLoader = torch.utils.data.DataLoader(dataset=TRAIN_DATA, 
                                              batch_size=batchSize,
                                              shuffle=True,
                                              num_workers=16, 
                                              pin_memory=True)
    
    validationLoader = torch.utils.data.DataLoader(dataset=VALIDATION_DATA,
                                                  batch_size=batchSize,
                                                  shuffle=True,
                                                  num_workers=16, 
                                                  pin_memory=True)
    
    schedulerLR = torch.optim.lr_scheduler.ReduceLROnPlateau(Optimizer, 'min', patience=2, verbose=True)
    totalSteps = len(trainLoader)
    MyModel.train()
    validationLoss = 0
    for i, (x, y) in enumerate(validationLoader):
        x = x.to(onDevice)
        y = y.to(onDevice)

        y_ = MyModel(x)
        Optimizer.zero_grad()
        
        loss = criterion(y_, y)
        loss.backward()

        Optimizer.step()

        lossHistory['VALIDATION'].append(loss.item())
        validationLoss += loss.item()
    validationLoss = validationLoss / (i+1)
    schedulerLR.step(validationLoss)

    if validationLoss < bestLoss or bestLoss == -1:
        modelPath = root_path + 'models/' + f'Best [{runID}].pt'
        torch.save(MyModel.state_dict(), modelPath)
        bestLoss = validationLoss

    dateTime = (str(datetime.now())).split('.')[0].replace(' ', '_')
    modelName = dateTime + f"_Epoch={Epochs+1}"
    modelPath = root_path + 'models/' + modelName + '.pt'
    torch.save(MyModel.state_dict(), modelPath)
    # return lossHistory

Optimizer = torch.optim.Adam(model.parameters(), amsgrad=True, lr=0.001, weight_decay=1e-6)

Epochs = 30
BatchSize = 128

DATA = {'TRAIN': TRAIN_DATASET, 'VALIDATION': VALIDATION_DATASET}
lossHistory = train(model, DATA, Optimizer, Epochs, run, BatchSize)