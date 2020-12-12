import sys
import os

import logging
import json
import numpy as np
import random
import time
import traceback

from PIL import Image, ImageDraw, ImageFont

from lib import epd2in9


logging.basicConfig(level=logging.DEBUG)
font = ImageFont.truetype('lib/Font.ttc', 18)

# load mnist dataset
with np.load('mnist.npz') as f:
    x_train, y_train = f['x_train'], f['y_train']
    x_test, y_test = f['x_test'], f['y_test']

with open('mnist_index.json', 'r') as f:
    idx_dict = json.load(f)

gap = np.ones((28, 10)) * 255
for i in [8, 9, 18, 19]:
    for j in [4,5,6,]:
        gap[i][j] = 0

def get_mnist_num(num):
    idxs = idx_dict[str(num)]
    idx = random.choice(idxs)
    return 255 - x_train[idx]


# === 0. init 
logging.info('epd2in9 Demo')

epd = epd2in9.EPD()
logging.info('init and Clear')
epd.init(epd.lut_full_update)
epd.Clear(0xFF)

# === 1. show date & time
logging.info('show date & time')

def YMD(draw, x1=10, y1=5, x2=160, y2=30):
    draw.rectangle((x1, y1, x2, y2), fill=255)
    draw.text((x1, y1), time.strftime('%Y-%m-%d  %a'), font = font, fill=0)

def HMS(draw, x1=180, y1=5, x2=280, y2=30):
    draw.rectangle((x1, y1, x2, y2), fill = 255)
    draw.text((x1, y1), time.strftime('%H:%M'), font = font, fill=0)
    
def MNIST(img, draw, mnist_img, x1=8, y1=30, x2=280, y2=120):
    draw.rectangle((x1, y1, x2, y2), fill = 255)
    mnist_img = Image.fromarray(mnist_img)
    mnist_img = mnist_img.resize((38*2*3, 28*3))
    img.paste(mnist_img, (x1, y1))

# partial update

time_image = Image.new('1', (epd.height, epd.width), 255)
time_draw = ImageDraw.Draw(time_image)

last_time = [-1, -1, -1, -1]
last_imgs = np.ones((4, 28, 28)) * 255

while (True):
    now = time.localtime(time.time())
    sec, mnt, hour = now.tm_sec, now.tm_min, now.tm_hour
    m1, m2 = mnt//10, mnt%10
    h1, h2 = hour//10, hour%10
    now_time = [h1, h2, m1, m2]
    print(f'{hour}:{mnt}:{sec}', last_time, now_time)

    if -1 in last_time or (mnt == 0 and sec < 5) :
        logging.info('partial update')
        epd.init(epd.lut_full_update)
        epd.Clear(0xFF)
        time.sleep(1)

        logging.info('partial update')
        epd.init(epd.lut_partial_update)
        epd.Clear(0xFF)
        YMD(time_draw)
        time.sleep(1)

    for i in range(4):
        if last_time[i] != now_time[i]:
            last_imgs[i] = get_mnist_num(now_time[i])
            last_time[i] = now_time[i]
            mnist_image = np.hstack((last_imgs[0], last_imgs[1], gap,
                                     last_imgs[2], last_imgs[3]))
            HMS(time_draw)  
            MNIST(time_image, time_draw, mnist_image)
            
            epd.display(epd.getbuffer(time_image))
            time.sleep(1)
    
    time.sleep(3)

# Clear        
logging.info('Clear...')
epd.init(epd.lut_full_update)
epd.Clear(0xFF)

# Sleep
logging.info('Goto Sleep...')
epd.sleep()
epd.Dev_exit()
