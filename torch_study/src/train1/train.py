import torch
import torchvision
from torch import nn
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

from model import *

train_data = torchvision.datasets.CIFAR10("../../dataset2", train=True, transform=torchvision.transforms.ToTensor(),
                                          download=True)
test_data = torchvision.datasets.CIFAR10("../../dataset2", train=False, transform=torchvision.transforms.ToTensor(),
                                         download=True)

# 数据集长度
train_data_size = len(train_data)
test_data_size = len(test_data)

print(train_data_size)
print(test_data_size)

# 加载数据集
train_dataloader = DataLoader(train_data, batch_size=64)
test_dataloader = DataLoader(test_data, batch_size=64)

# 创建网络模型
tudui = Tudui()
# 损失函数
loss_fn = nn.CrossEntropyLoss()
# 优化器
optimizer = torch.optim.SGD(tudui.parameters(), lr=0.01)
# 训练次数
total_train_step = 0
# 测试次数
total_test_step = 0
# 训练轮数
epoch = 10

# 添加tensorboard
writer = SummaryWriter("../../logs")

for i in range(epoch):
    print("——————————第{}轮训练开始——————————".format(i + 1))
    # 训练步骤开始
    for data in train_dataloader:
        imgs, target = data
        output = tudui(imgs)
        loss = loss_fn(output, target)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_train_step = total_train_step + 1

        if total_train_step % 100 == 0:
            print("训练次数：{}，Loss:{}".format(total_train_step, loss.item()))
            writer.add_scalar("train_loss", loss.item(), total_train_step)

    # 测试步骤开始
    total_test_loss = 0
    total_accuracy = 0
    with torch.no_grad():
        for data in test_dataloader:
            imgs, target = data
            output = tudui(imgs)
            loss = loss_fn(output, target)
            total_test_loss = total_test_loss + loss.item()
            accuracy = (output.argmax(1) == target).sum()
            total_accuracy = total_accuracy + accuracy
    print("整体测试集上的loss:{}".format(total_test_loss))
    print("整体测试集上的正确率:{}".format(total_accuracy / test_data_size))
    writer.add_scalar("test_loss", total_test_loss, total_test_step)
    writer.add_scalar("test_accuracy", total_accuracy, total_test_step)
    total_test_step = total_test_step + 1
    # 保存模型
    torch.save(tudui, "../../model/model_{}.pth".format(i))
    print("模型已保存")

writer.close()
