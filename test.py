# !/usr/bin/python3
# -*-coding:utf-8-*-
# Author: blair liu
# CreatDate: 2021/4/1 20:17
# Description: 

import numpy as np

# a = np.array([])
#

# a = np.append(a, np.array([100, 200]))
# a = np.append(a, np.array([100, 200]))
# a = np.concatenate((a, np.array([[100, 200]])), axis=0)
# a = np.concatenate((a, np.array([[100, 200]])), axis=0)
# print(a)

# per2 = np.zeros((10, 3))
# per2[1] = [1, 1, 1]
# print(per2)

# a = np.random.randint(0, high=65536, size=100)
# print(a)
#
# b = np.histogram(a, bins=65536, range=(-0.5, 65535.5))
# print(b)

def count_per2_per98_from_cdf(c):
    for index2, i in enumerate(c):
        if i >= 0.02:
            break
    per2 = index2
    for index98, i in enumerate(c[::-1]):
        if i <= 0.98:
            break
    per98 = len(c) - index98 - 1
    return per2, per98


a = np.random.randint(0, high=255, size=10000)
print(a)

a = a.reshape((100, 100))

b, _ = np.histogram(a, bins=256, range=(-0.5, 255.5))
print(b)
print(b.shape)
c = b.cumsum() / b.sum()
per2, per98 = count_per2_per98_from_cdf(c)
print(per2, per98)

print(b.dtype)
d = np.ones(256, dtype=np.int64)
print(d.dtype)
d += b
print(d)


