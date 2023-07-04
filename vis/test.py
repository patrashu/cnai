import os
from glob import glob

import cv2
import numpy as np

import torch
from torch import nn, optim
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
import pytorch_lightning as pl

import timm

root_path = './korean/'

age_classes = 9
gender_classes = 2

timm_model = timm.create_model('tf_efficientnet_b1_ns', num_classes=age_classes+gender_classes)
model_path = root_path + 'cnai/best.ckpt'
TRAIN_PATH = sorted(glob(root_path + 'train/labels/*.png'))
VAL_PATH = sorted(glob(root_path + 'val/labels/*.png'))
loss = {'age': nn.MSELoss(), 'gender': nn.BCELoss()}

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
        y = [0]*11
        y[cls] = 1
        return x, y

    def __len__(self):
        return len(self.fileList)
    
transform = transforms.Compose([transforms.ToTensor(), 
                                transforms.Normalize((0.5,), (0.5,)),
                                transforms.RandomRotation(10),
                                transforms.Resize((224, 224))])

TRAIN_DATASET = AGE_GENDER(TRAIN_PATH, transform)
VALIDATION_DATASET = AGE_GENDER(VAL_PATH, transform)
val_loader = DataLoader(VALIDATION_DATASET, batch_size=64)

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
        age_acc = torch.sum(x_age == y_age).item() / (len(y_age) * 1.0)
        gender_acc = torch.sum(x_gender == y_gender).item() / (len(y_gender) * 1.0)
        self.log('val_acc', [age_acc, gender_acc], prog_bar=True)
        self.log("valid_loss", loss, on_step=True, on_epoch=True, prog_bar=True, logger=True)
        return loss


    def configure_optimizers(self):
        optimizer = optim.Adam(self.parameters(), lr=1e-3)
        return optimizer

pl_model = PLModel.load_from_checkpoint(model=timm_model, loss=loss, checkpoint_path=model_path)
run = "cuda:0" if torch.cuda.is_available() else "cpu"
pl_model.to(run)
pl_model.eval()

trainer = pl.Trainer()

trainer.fit(pl_model, val_dataloaders=val_loader)