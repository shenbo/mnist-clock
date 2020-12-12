# %%
import numpy as np
import json
import random
import cv2
import time


path = 'mnist.npz'
with np.load(path) as f:
    x_train, y_train = f['x_train'], f['y_train']
    x_test, y_test = f['x_test'], f['y_test']

with open('mnist_index.json', 'r') as f:
    idx_dict = json.load(f)

for i in range(10):
    print(i, len(idx_dict[str(i)]))


def get_mnist_num(num):
    idxs = idx_dict[str(num)]
    idx = random.choice(idxs)
    return x_train[idx]


gap = np.zeros((28, 10))
for i in [8, 9, 18, 19]:
    for j in [4,5,6,]:
        gap[i][j] = 255

last_time = [-1, -1, -1, -1, -1, -1]
last_imgs = np.zeros((6, 28, 28))

while True:
    now = time.localtime(time.time())
    sec, mnt, hour = now.tm_sec, now.tm_min, now.tm_hour
    s1, s2 = sec//10, sec%10
    m1, m2 = mnt//10, mnt%10
    h1, h2 = hour//10, hour%10
    now_time = [h1, h2, m1, m2, s1, s2]
    print(last_time, now_time)

    for i in range(6):
        if last_time[i] != now_time[i]:
            last_imgs[i] = get_mnist_num(now_time[i])
            last_time[i] = now_time[i]

    img = np.hstack((last_imgs[0], last_imgs[1], gap,
                     last_imgs[2], last_imgs[3], gap,
                     last_imgs[4], last_imgs[5]))

    cv2.imshow('num', img)
    # cv2.imwrite('mnist-clock.png', img)
    cv2.waitKey(100)
