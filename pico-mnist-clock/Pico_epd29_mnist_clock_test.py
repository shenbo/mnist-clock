import random
import time
import Pico_ePaper29 as epd29

import gc
gc.collect()
print("mem: ", gc.mem_free())

# === 1. load mnist font lib
# 读取字符，返回一个由 '0' 或 '1' 组成的字符串，字符串长度为784。
def get_mnist_font(num):
    SIZE = 98
    NUM = 500    
    
    f = open('font_lib_{}.bin'.format(num), 'rb')
    f.seek(random.randrange(0, NUM) * SIZE)
    mf_bin = f.read(SIZE)
    f.close() 
    
    # string: 784 * '0' or '1'
    mf_str = ''.join(['{:08b}'.format(mf_bin[i]) for i in range(SIZE)])
    # mf_x28 = [[mf_str[i*28+j] for j in range(28)] for i in range(28)]
 
    return mf_str

# === 2. epaper29: 296x128;     0xff:white;  0x00:black;   
epd = epd29.EPD_2in9_Landscape()
       
def MNIST(draw, mf, i):    
    c0 = [2, 72, 154, 224]
    r0 = [20, 20, 20, 20]
    nR = 100
    nC = 70

    # mf_x28 = [[mf_str[i*28+j] for j in range(28)] for i in range(28)]
    # for r in range(28):
    #     for c in range(28):
    #         color = 0x00 if mf[r*28+c]=='1' else 0xff
    #         draw.pixel(c + c0[i], r + r0[i], color)
    
    # resize: 28x28 -> nRxnC
    # mf_rsz = [[int(mf_x28[int(28*r/nR)][int(28*c/nC)]) for c in range(nC)] for r in range(nR)]
    for r in range(nR):
        for c in range(nC):
            color = mf[ int(28*r/nR) * 28 + int(28*c/nC) ]
            color = 0x00 if color == '1' else 0xff
            draw.pixel(c + c0[i], r + r0[i], color)

    gc.collect()
    print(i, "mem: ", gc.mem_free())
    
# --------------------------------------------
print('full update')
epd.Clear(0xff)        
epd.delay_ms(100)
epd.fill(0xff)
epd.delay_ms(100)
epd.display(epd.buffer)
epd.display_Partial(epd.buffer)

last_time = [-1, -1, -1, -1]
now_time = [1, 2, 3, 4]        
for i in range(4):
    if last_time[i] != now_time[i]:
        mnist = get_mnist_font(now_time[i])
        MNIST(epd, mnist, i)

        print('partial update', now_time)
        epd.display_Partial(epd.buffer)
        epd.delay_ms(1000)

gc.collect()
print("mem: ", gc.mem_free())

