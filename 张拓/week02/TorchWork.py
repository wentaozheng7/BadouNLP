# coding:utf8
import ast

import torch
import torch.nn as nn
import numpy as np
import random
import json
import matplotlib.pyplot as plt

"""

基于pytorch框架编写模型训练
实现一个自行构造的找规律(机器学习)任务

"""


class TorchModel(nn.Module):
    def __init__(self, input_size):
        super(TorchModel, self).__init__()
        self.linear = nn.Linear(input_size, 5)  # 线性层   输出是哪类的 最大的数在那位就是哪类的
        self.activation = torch.sigmoid  # sigmoid归一化函数  激活函数
        self.loss = nn.CrossEntropyLoss()  #交叉熵

    # 当输入真实标签，返回loss值；无真实标签，返回预测值
    def forward(self, x, y=None):
        x = self.linear(x)  # (batch_size, input_size) -> (batch_size, 1)
        y_pred = self.activation(x)  # (batch_size, 1) -> (batch_size, 1)
        if y is not None:
            return self.loss(y_pred, y)  # 预测值和真实值计算损失
        else:
            return y_pred  # 输出预测结果


# 生成一个样本, 样本的生成方法，代表了我们要学习的规律
# 随机生成一个5维向量，那个数最大，输出的标签就是哪维的
def build_sample():
    x = np.random.random(5)
    a = list(x)
    b = a.index(max(x))
    # return x, b+1
    if b == 0:
        return x, [1, 0, 0, 0, 0]
    elif b == 1:
        return x, [0, 1, 0, 0, 0]
    elif b == 2:
        return x, [0, 0, 1, 0, 0]
    elif b == 3:
        return x, [0, 0, 0, 1, 0]
    elif b == 4:
        return x, [0, 0, 0, 0, 1]


# 随机生成一批样本
# 正负样本均匀生成
def build_dataset(total_sample_num):
    X = []
    Y = []
    for i in range(total_sample_num):
        x, y = build_sample()
        X.append(x)
        Y.append(y)
    return torch.FloatTensor(X), torch.FloatTensor(Y)


# 测试代码
# 用来测试每轮模型的准确率
def evaluate(model):
    model.eval()
    test_sample_num = 100
    x, y = build_dataset(test_sample_num)
    # print("本次预测集中共有%d个正样本，%d个负样本" % (sum(y), test_sample_num - sum(y)))
    oneKind, twoKind, thireKind, fourKind, fiveKind, wrong, correct = 0, 0, 0, 0, 0, 0, 0
    with torch.no_grad():
        y_pred = model(x)  # 模型预测 model.forward(x)
        for y_p, y_t in zip(y_pred, y):  # 与真实标签进行对比
            if float(y_p[0]) >= 0.5 and int(y_t[0]) == 1:
                oneKind += 1
                correct += 1
            elif float(y_p[1]) >= 0.5 and int(y_t[1]) == 1:
                twoKind += 1  # 正样本判断正确
                correct += 1
            elif float(y_p[2]) >= 0.5 and int(y_t[2]) == 1:
                thireKind += 1  # 正样本判断正确
                correct += 1
            elif float(y_p[3]) >= 0.5 and int(y_t[3]) == 1:
                fourKind += 1  # 正样本判断正确
                correct += 1
            elif float(y_p[4]) >= 0.5 and int(y_t[4]) == 1:
                fiveKind += 1  # 正样本判断正确
                correct += 1
            else:
                wrong += 1
    print("正确预测个数：%d, 正确率：%f" % (correct, correct / (correct + wrong)))
    return correct / (correct + wrong)


def main():
    # 配置参数
    epoch_num = 20  # 训练轮数
    batch_size = 20  # 每次训练样本个数
    train_sample = 5000  # 每轮训练总共训练的样本总数
    input_size = 5  # 输入向量维度
    learning_rate = 0.001  # 学习率
    # 建立模型
    model = TorchModel(input_size)
    # 选择优化器
    optim = torch.optim.Adam(model.parameters(), lr=learning_rate)
    log = []
    # 创建训练集，正常任务是读取训练集
    train_x, train_y = build_dataset(train_sample)
    # 训练过程
    for epoch in range(epoch_num):
        model.train()  #设置到训练模式
        watch_loss = []  #存储每轮loss用的，如果不想查看loss可以去掉
        for batch_index in range(train_sample // batch_size):
            x = train_x[batch_index * batch_size: (batch_index + 1) * batch_size]  #根据batch_index每轮取出20个样本，就是第一轮循环0-20.第二轮20-40这样依次取出训练数据
            y = train_y[batch_index * batch_size: (batch_index + 1) * batch_size]
            loss = model(x, y)  # 计算loss  等价于model.forward(x,y)
            loss.backward()  # 计算梯度
            optim.step()  # 更新权重
            optim.zero_grad()  # 梯度归零
            watch_loss.append(loss.item())
        print("=========\n第%d轮平均loss:%f" % (epoch + 1, np.mean(watch_loss)))
        acc = evaluate(model)  # 测试本轮模型结果
        log.append([acc, float(np.mean(watch_loss))])
    # 保存模型
    torch.save(model.state_dict(), "modelw.pt")
    # 画图
    print(log)
    plt.plot(range(len(log)), [l[0] for l in log], label="acc")  # 画acc曲线
    plt.plot(range(len(log)), [l[1] for l in log], label="loss")  # 画loss曲线
    plt.legend()
    plt.show()
    return


# 使用训练好的模型做预测
def predict(model_path, input_vec):
    input_size = 5
    model = TorchModel(input_size)
    model.load_state_dict(torch.load(model_path))  # 加载训练好的权重
    print(model.state_dict())
    model.eval()  # 测试模式
    with torch.no_grad():  # 不计算梯度
        result = model.forward(torch.FloatTensor(input_vec))  # 模型预测
    for vec, res in zip(input_vec, result):
        a = list(vec)
        b = a.index(max(a))+1
        print("输入：%s, 预测类别：%d" % (vec, b))  # 打印结果


if __name__ == "__main__":
    main()
    test_vec = [[0.97889086, 0.15229675, 0.31082123, 0.03504317, 0.88920843],
                [0.74963533, 0.5524256, 0.95758807, 0.95520434, 0.84890681],
                [0.00797868, 0.67482528, 0.13625847, 0.34675372, 0.19871392],
                [0.09349776, 0.59416669, 0.92579291, 0.41567412, 0.1358894]]
    predict("modelw.pt", test_vec)
