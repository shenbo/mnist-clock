import network
import random
import time
import ntptime
import Pico_ePaper29 as epd29

# === 0. wifi config ==========================
ssid = 'aaa'
pswd = 'xxx'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, pswd)

status = wlan.ifconfig()
print('wifi={}  ip={}'.format(ssid, status[0]))
print(time.localtime())

try:
    # https://www.pool.ntp.org/zone/cn
    ntptime.host = 'cn.pool.ntp.org'
    ntptime.settime()
except Exception as e:
    print('NTPTIME ERROR', e, ntptime.host)

# === 1. load mnist font lib ==================
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

def YMD(draw, ymd, wid):
    draw.fill(0xff)
    
    draw.fill_rect(5, 5, 95, 8, 0xff)
    draw.text(wid, 5, 5, 0x00)    
    draw.fill_rect(100, 5, 120, 8, 0xff)
    draw.text(ymd, 100, 5, 0x00)
        
def HMS(draw, txt):
    draw.fill_rect(240, 5, 50, 8, 0xff)
    draw.text(txt, 240, 5, 0x00)

def DOT(draw):
    draw.fill_rect(144, 60, 7, 7, 0x00)
    draw.fill_rect(144, 80, 7, 7, 0x00)

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
            
def MNIST_clear(draw):
    draw.fill_rect(0, 20, 296, 100, 0xff)
    draw.fill_rect(240, 5, 50, 8, 0xff)
    
# === 3. run ==================================
last_time = [-1, -1, -1, -1]
while (True):
    # 2.1 get time.now
    wifi_id = ssid if wlan.status()==3 else 'no wifi'
    now = time.localtime(time.time() + 8*3600)
    
    year, mon, day = now[0], now[1], now[2]
    hour, mnt, sec = now[3], now[4], now[5]
    week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekday = week[now[6]]
    now_time = [hour//10, hour%10, mnt//10, mnt%10]
    
    print(now, wifi_id, last_time, now_time)
        
    # 2.2 full update
    if -1 in last_time or (mnt%10==0 and sec<5):
        print('full update')
        epd.Clear(0xff)        
        epd.delay_ms(100)
        
        YMD(epd, '{:04d}-{:02d}-{:02d} {}'.format(year, mon, day, weekday), wifi_id)
        epd.display(epd.buffer)
        epd.delay_ms(100)
        
        MNIST_clear(epd)
        epd.display_Partial(epd.buffer)
        epd.delay_ms(100)        
        last_time = [-1, -1, -1, -1]
        
    # 2.3 partial update
    for i in range(4):
        if last_time[i] != now_time[i]:
            print('partial update', last_time, now_time)
            last_time[i] = now_time[i]
            
            mnist = get_mnist_font(now_time[i])
            HMS(epd, '{:02d}:{:02d}'.format(hour, mnt))
            MNIST(epd, mnist, i)            
            epd.display_Partial(epd.buffer)
            epd.delay_ms(100)
            
            if i == 1:
                DOT(epd)
                epd.display_Partial(epd.buffer)
                epd.delay_ms(100)
                 
    time.sleep(5)

