import sys
import os
import logging
from ePaper.RaspberryPi_JetsonNano.python.lib.waveshare_epd import epd3in52
import time
from PIL import Image, ImageDraw, ImageFont
import traceback
import json
import numpy as np
import random

logging.basicConfig(level=logging.DEBUG)
font = ImageFont.truetype('lib/jetbrains-mono.ttf', 20)

# load mnist dataset
with np.load('mnist.npz') as f:
    x_train, y_train = f['x_train'], f['y_train']
    x_test, y_test = f['x_test'], f['y_test']

with open('mnist_index.json', 'r') as f:
    idx_dict = json.load(f)

gap = np.ones((28, 10)) * 255
for i in [8, 9, 18, 19]:
    for j in [4, 5, 6]:
        gap[i][j] = 0

def get_mnist_num(num):
    idxs = idx_dict[str(num)]
    idx = random.choice(idxs)
    return 255 - x_train[idx]


# === 0. init
logging.info('epd3in52 240x360')

epd = epd3in52.EPD()
logging.info('init and Clear')
epd.init()
epd.display_NUM(epd.WHITE)
epd.lut_GC()
epd.refresh()

# === 1. show date & time
logging.info('show date & time')

def YMD(draw, x1=40, y1=2, x2=240, y2=22):
    draw.rectangle((x1, y1, x2, y2), fill=255)
    draw.text((x1, y1), time.strftime('%Y-%m-%d  %a'), font=font, fill=0)

def HMS(draw, x1=250, y1=2, x2=320, y2=22):
    draw.rectangle((x1, y1, x2, y2), fill=255)
    draw.text((x1, y1), time.strftime('%H:%M'), font=font, fill=0)
    
def MNIST(img, draw, mnist_img, x1=40, y1=25, x2=320, y2=125):
    draw.rectangle((x1, y1, x2, y2), fill=255)
    mnist_img = Image.fromarray(mnist_img)
    mnist_img = mnist_img.resize((280, 100))
    img.paste(mnist_img, (x1, y1))

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

    if -1 in last_time or (mnt==0 and sec<5):
        logging.info('partial update')
        epd.init()
        epd.display_NUM(epd.WHITE)
        epd.lut_GC()
        epd.refresh()
        YMD(time_draw)

    for i in range(4):
        if last_time[i] != now_time[i]:
            last_imgs[i] = get_mnist_num(now_time[i])
            last_time[i] = now_time[i]
            mnist_image = np.hstack((last_imgs[0], last_imgs[1], gap,
                                     last_imgs[2], last_imgs[3]))
            HMS(time_draw)
            MNIST(time_image, time_draw, mnist_image)
            epd.display(epd.getbuffer(time_image.rotate(180)))
            # epd.lut_GC()
            epd.refresh()
            time.sleep(1)

    time.sleep(3)

# Clear
logging.info('Clear...')
epd.Clear()

# Sleep
logging.info('Goto Sleep...')
epd.sleep()
