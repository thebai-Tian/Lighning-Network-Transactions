# -*- coding: utf-8 -*-
import numpy as np
import random
from decimal import Decimal
import matplotlib.pyplot as plt


class Node:
    
    def __init__(self, name, commission=None, mode=None):
        self.name = name  
        self.capacity = Decimal('1e8')
        self.is_open = True  # 通道开启情况
        self.charged_fee = Decimal(0)  
        self.rate = Decimal('1e-8')  # 收益费率，0.000001%
        self.mode = mode  
        self.commission = commission  # 通道重启所需扣除的手续费

    # 重置节点余额
    def reset(self):
        self.capacity = Decimal('1e8')  # 科学记数法1x10^8

    # 节点发送一定数量的BTC，如果超过通道容量则交易失败
    def send(self, amount):
        if self.capacity >= amount:  # 发送交易成功
            amount = max(0, min(self.capacity, amount))
            self.capacity -= amount  # 减少通道容量
            self.is_open = True
        elif self.mode == 1:  # 发送交易失败且为关闭机制情况
            self.reset()  # 重置节点
            self.charged_fee -= self.commission  # 扣除重开通道手续费
            self.is_open = False
        else:  # 发送交易失败且为等待机制情况
            self.is_open = False

    # 获得发送方的通道是否开启的参数，若开启代表交易成功，节点接收一定数量的BTC并累计收益
    def receive(self, amount, is_open):
        if is_open:  
            self.charged_fee += (1 + amount * self.rate)  # 统计发送方支出接收方的手续费
            self.capacity += amount  
        elif self.mode == 1: 
            self.reset()  # 重置节点
            self.charged_fee -= self.commission  # 扣除重开通道手续费


if __name__ == "__main__":
    # 定义初始参数
    p = [0.50, 0.80]  # A向B交易的概率，C向D交易的概率

    n = int(50000)  # 交易次数10万次

    lam = Decimal(10000)

    profit_A = []  # 储存最终收益数据
    profit_B = []
    profit_C = []
    profit_D = []

    # 模拟n次交易过程，基于所有概率可能情况
    for i in range(len(p)):
        # 创建4个节点，A与B之间进行关闭机制下的交易，C与D之间进行等待机制下的交易，B和D为交易所
        A = Node("A", 0, 1)
        B = Node("B", 7000, 1)
        C = Node("C", 2)
        D = Node("D", 2)
        capacity_A = []  # 用于记录通道容量变化
        capacity_C = []

        j = 0
        while j < n:  
            
            direction = random.random() <= p[i]
            amount = np.random.poisson(lam)

            # 根据交易方向和金额进行交易,更新通道状态和记录通道容量
            if direction:
                A.send(amount)
                B.receive(amount, A.is_open)
                capacity_A = np.append(capacity_A, [float(A.capacity)])
                C.send(amount)
                D.receive(amount, C.is_open)
                capacity_C = np.append(capacity_C, [float(C.capacity)])
            else:
                B.send(amount)
                A.receive(amount, B.is_open)
                D.send(amount)
                C.receive(amount, D.is_open)
            j += 1
        A.charged_fee = float(A.charged_fee.quantize(Decimal('0.0001')))
        B.charged_fee = float(B.charged_fee.quantize(Decimal('0.0001')))
        C.charged_fee = float(C.charged_fee.quantize(Decimal('0.0001')))
        D.charged_fee = float(D.charged_fee.quantize(Decimal('0.0001')))

        # 统计最终收益
        profit_A.append(A.charged_fee)
        profit_B.append(B.charged_fee)
        profit_C.append(C.charged_fee)
        profit_D.append(D.charged_fee)

        # 打印最终受益，容量变化折线图
        print(f"泊松参数：{lam}")
        print(f"总交易次数：{n}")
        print(f"交易概率：{p[i]}")

        print("关闭机制下的A、B交易情况：")
        print(f"A 收益总额: {A.charged_fee}", "聪")
        print(f"B 收益总额: {B.charged_fee}", "聪")
        plt.figure()
        plt.plot(capacity_A)
        plt.xlabel('Number/times')
        plt.ylabel('Capacity/satoshi')
        plt.title(f"A->B with closing mechanism / p={p[i]}")
        plt.show()

        print("等待机制下的A、B交易情况：")
        print(f"A 收益总额: {C.charged_fee}", "聪")
        print(f"B 收益总额: {D.charged_fee}", "聪")
        plt.figure()
        plt.plot(capacity_C)
        plt.xlabel('Number/times')
        plt.ylabel('Capacity/satoshi')
        plt.title(f"A->B with waiting mechanism / p={p[i]}")
        plt.show()

    # 打印所有概率情况下的收益条形图
    print('所有概率情况下的收益:')
    plt.figure()
    # 定义条形图宽度
    width = 0.04
    # 绘制条并标注数据
    plt.bar([p for p in p], profit_A, width=width, color='r')
    for x, y in zip([p for p in p], profit_A):
        plt.text(x, y + 0.01, '%.2f' %
                 y, ha='center', va='bottom', fontsize=6.5)
    plt.bar([p + width for p in p], profit_B, width=width, color='c')
    for x, y in zip([p + width for p in p], profit_B):
        plt.text(x, y + 0.01, '%.2f' %
                 y, ha='center', va='bottom', fontsize=6.5)
    plt.bar([p + 2 * width for p in p], profit_C, width=width, color='g')
    for x, y in zip([p + 2 * width for p in p], profit_C):
        plt.text(x, y + 0.01, '%.2f' %
                 y, ha='center', va='bottom', fontsize=6.5)
    plt.bar([p + 3 * width for p in p], profit_D, width=width, color='y')
    for x, y in zip([p + 3 * width for p in p], profit_D):
        plt.text(x, y + 0.01, '%.2f' %
                 y, ha='center', va='bottom', fontsize=6.5)
    # 调整x轴标记位置
    plt.xticks([p + 0.06 for p in p], p)
    plt.xlabel('p')
    plt.ylabel('Profit/satoshi')
    plt.title('Profit with different probabilities')
    plt.legend(['profit_A(closing mechanism)', 'profit_B(closing mechanism)',
                'profit_A(waiting mechanism)', 'profit_B(waiting mechanism)'])
    plt.axhline(0, color='black', linestyle='--')
    plt.show()
