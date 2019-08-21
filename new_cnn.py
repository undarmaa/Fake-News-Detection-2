#!/usr/bin/env python
# coding: utf-8

# In[1]:


# -*- coding: utf-8 -*-
"""pura

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TTtW3wmDUC1F4ASCInrg76Vg7RGbTlJS
"""

import torch
import torch.nn as nn
import numpy as np
import pickle
import pandas
import torch.optim

from torchvision import transforms
from torch.utils.data import Dataset, DataLoader


# In[2]:




# In[3]:


def trainData(arr, y, batch = 64, istrain = True):
    class txtData(torch.utils.data.Dataset):
        def __init__(self, arr, y, istrain, transform, device='cuda'):
            self.arr = arr
            self.labels = y
            self.istrain = istrain
            self.transform = transform

        def __len__(self):
            return len(self.labels)

        def __getitem__(self, idx):
            data = self.arr[idx]
            label = self.labels[idx]


            if self.istrain:
                return data, label

    data_transform = transforms.Compose([
                transforms.ToTensor()])
    dataset = txtData(arr, y, istrain=istrain, transform=data_transform)
    dataloader = DataLoader(dataset, batch_size = batch, shuffle=False, num_workers=2)

    return dataloader


# In[ ]:





# In[4]:


class TensorDot(nn.Module):
    def __init__(self):
        super(TensorDot, self).__init__()

    def forward(self, x, y):
        batch_size = y.size(0)
        y_old = y
        x = x.to(device)
        y = y.to(device)
        y_old = y_old.to(device)

        y = y.unsqueeze(-1)
        y = y.expand(batch_size, y.size(1), x.size(1))
        y = y.contiguous().view(-1, y.size(1) * x.size(1))

        x = x.unsqueeze(-1)
        x = x.expand(batch_size, x.size(1), y_old.size(1))
        x = x.permute(0, 2, 1)
        x = x.contiguous().view(batch_size, -1)

        f = x.float()  * y.float()

        w = torch.ones((6, 1))

        f = f.view((batch_size, 1, -1))
        w = w.view((1, 1, -1))
        w = w.to(device)

        final =  torch.nn.functional.conv1d(f.float(), w.float(), stride = 6).view(-1, 1024)
        # print(final.size())
        return final


# In[5]:


class mainNet(nn.Module):
    def __init__(self):
        super(mainNet, self).__init__()

        self.lstm = nn.LSTM(input_size=768, hidden_size=768, num_layers=2, batch_first=True)
        self.fc = nn.Sequential(
                nn.Linear(115, 64),
                nn.ReLU(inplace=False)
                )
        self.tdot = TensorDot()
        self.dp1 = nn.Dropout(0.7)
        self.fcf1 = nn.Sequential(
                nn.Linear(1094, 512),
                nn.ReLU()
                )
        self.fcf2 = nn.Sequential(
                nn.Linear(512, 256),
                nn.ReLU()
                )

        self.fcf3 = nn.Sequential(
                nn.Linear(256, 128),
                nn.ReLU()
                )
        self.fcf4 = nn.Sequential(
                nn.Linear(128, 64),
                nn.ReLU()
                )
        self.fcf5 = nn.Sequential(
                nn.Linear(64, 6),
                nn.ReLU()
                )

        self.softmax = nn.Softmax(dim = 1)
        self.cnn1 = nn.Conv1d(768, 800, 2)
        self.cnn2 = nn.Conv1d(768, 800, 5)
        self.cnn3 = nn.Conv1d(768, 800, 8)

        self.mp1 = nn.MaxPool1d(24)
        self.mp2 = nn.MaxPool1d(21)
        self.mp3 = nn.MaxPool1d(18)

        self.dense_mcat = nn.Linear(2400, 1024)



    def forward(self, main, aux, cred):
        main[main != main] = 0.5
        main = main.permute(0, 2, 1)

        c1 = self.cnn1(main)
        c2 = self.cnn2(main)
        c3 = self.cnn3(main)
        m1 = self.mp1(c1).squeeze()
        m2 = self.mp2(c2).squeeze()
        m3 = self.mp3(c3).squeeze()


        mcat = torch.cat((m1, m2, m3), 1)
        dense_mcat = self.dense_mcat(mcat)
        x = dense_mcat
        x[x != x] = 0.5


        aux[aux != aux] = 0.5
        cred[cred != cred] = 0.5
        z = self.fc(aux)
        y = self.tdot(cred, x)

        x = cred
        x = x.float()
        z[z != z] = 0.5
        y[y != y] = 0.5
        x = x.to(device)
        y = y.to(device)
        z = z.to(device)

        out = torch.cat((x, y, z), 1)
        out = self.fcf1(out)
        out = self.dp1(out)

        out = self.fcf2(out)

        out = self.dp1(out)
        out = self.fcf3(out)
        out = self.dp1(out)
        out = self.fcf4(out)
        out = self.dp1(out)
        out = self.fcf5(out)
        out = self.dp1(out)
        fin_out = self.softmax(out)




        return fin_out


# In[ ]:




torch.autograd.set_detect_anomaly(True)
# In[14]:


device = torch.device("cuda")

with open("X_train.txt", "rb") as fp:
    a = pickle.load(fp)
with open("X_train_meta.txt", "rb") as fp:
    b = pickle.load(fp)
with open("X_train_cred_new.txt", "rb") as fp:
    c = pickle.load(fp)

with open("X_val.txt", "rb") as fp:
    d = pickle.load(fp)
with open("X_val_meta.txt", "rb") as fp:
    e = pickle.load(fp)
with open("X_val_cred_new.txt", "rb") as fp:
    f = pickle.load(fp)


with open("X_test.txt", "rb") as fp:
    d1 = pickle.load(fp)
with open("X_test_meta.txt", "rb") as fp:
    e1 = pickle.load(fp)
with open("X_test_cred_new.txt", "rb") as fp:
    f1 = pickle.load(fp)


# In[15]:


a = a.tolist()
d = d.tolist()
d1 = d1.tolist()

with open("Y_train.txt", "rb") as fp:
    y_train = pickle.load(fp)
with open("Y_val.txt", "rb") as fp:
    y_val = pickle.load(fp)
with open("Y_test.txt", "rb") as fp:
    y_test = pickle.load(fp)

y_train = y_train.tolist()
y_val = y_val.tolist()
y_test = y_test.tolist()

batch_size = 200
tmain = trainData(a, y_train, batch_size)
taux = trainData(b, y_train, batch_size)
tcred = trainData(c, y_train, batch_size)

vmain = trainData(d, y_val, batch_size)
vaux = trainData(e, y_val, batch_size)
vcred = trainData(f, y_val, batch_size)

test_main = trainData(d1, y_test, batch_size)
test_aux = trainData(e1, y_test, batch_size)
test_cred = trainData(f1, y_test, batch_size)

model = mainNet().to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)
loss_function = torch.nn.CrossEntropyLoss()

num_epochs = 1000
losses = []


# In[12]:


for epoch in range(num_epochs):
    print("epoch: {}/{}".format(epoch, num_epochs))
    train_loss = []
    valid_loss = []
    ep_acc = []
    model.train()

    main_iter = iter(tmain)
    aux_iter = iter(taux)
    cred_iter = iter(tcred)
    length = len(taux)
    i = 0
    while (i < length):
        accuracy = 0
        mainiter = main_iter.next()
        auxiter = aux_iter.next()

        crediter = cred_iter.next()

        main, label = mainiter
        main = main.to(device)
        label = label.to(device)
        aux, _ = auxiter
        aux = aux.to(device)
        cred, _ = crediter
        cred = cred.to(device)
        optimizer.zero_grad()

        main = torch.Tensor.float(main)
        aux = torch.Tensor.float(aux)


        output = model(main, aux, cred)


        _, idx = torch.max(output, dim=1)
        acc = (idx == label)
        accuracy += acc.sum().item() / acc.size(0)



        loss = loss_function(output, label)

        loss.backward()
        optimizer.step()
        i+=1
        ep_acc.append(accuracy)
        train_loss.append(loss.item())
    print("Training")
    print(sum(ep_acc)/len(ep_acc))
    model.eval()
    ep_acc = []

    main_iter_v = iter(vmain)
    aux_iter_v = iter(vaux)
    cred_iter_v = iter(vcred)
    length = len(vaux)
    i = 0
    while (i < length):
        accuracy = 0
        mainiter = main_iter_v.next()
        auxiter = aux_iter_v.next()

        crediter = cred_iter_v.next()

        main, label = mainiter
        main = main.to(device)
        label = label.to(device)
        aux, _ = auxiter
        aux = aux.to(device)
        cred, _ = crediter
        cred = cred.to(device)
        optimizer.zero_grad()

        main = torch.Tensor.float(main)
        aux = torch.Tensor.float(aux)
        output = model(main, aux, cred)

        _, idx = torch.max(output, dim=1)
        acc = (idx == label)
        accuracy += acc.sum().item() / acc.size(0)


        loss = loss_function(output, label)
        i+=1
        ep_acc.append(accuracy)
        train_loss.append(loss.item())
        valid_loss.append(loss.item())

    losses.append([train_loss, valid_loss])
    print("Validation")
    print(sum(ep_acc)/len(ep_acc))


# In[9]:




# In[17]:


for epoch in range(1):
    print("epoch: {}/{}".format(epoch, num_epochs))
    train_loss = []
    valid_loss = []
    ep_acc = []
    main_iter = iter(test_main)
    aux_iter = iter(test_aux)
    cred_iter = iter(test_cred)
    length = len(test_aux)
    i = 0

    model.eval()
    ep_acc = []
    while (i < length):
        accuracy = 0
        mainiter = main_iter.next()
        auxiter = aux_iter.next()

        crediter = cred_iter.next()

        main, label = mainiter
        main = main.to(device)
        label = label.to(device)
        aux, _ = auxiter
        aux = aux.to(device)
        cred, _ = crediter
        cred = cred.to(device)
        optimizer.zero_grad()

        main = torch.Tensor.float(main)
        aux = torch.Tensor.float(aux)
        output = model(main, aux, cred)

        _, idx = torch.max(output, dim=1)
        acc = (idx == label)
        accuracy += acc.sum().item() / acc.size(0)


        loss = loss_function(output, label)
        print("Test:")
        i+=1
        ep_acc.append(accuracy)
        train_loss.append(loss.item())
        print(epoch, i, loss.item(), accuracy)
        valid_loss.append(loss.item())

    losses.append([train_loss, valid_loss])
    print(sum(ep_acc)/len(ep_acc))


# In[ ]: