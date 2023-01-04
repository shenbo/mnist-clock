## 用 raspberry pico w 和墨水屏做一个 mnist-clock

## 1. 墨水屏
- 型号：Pico-ePaper-2.9
- https://www.waveshare.net/wiki/Pico-ePaper-2.9
- 工作电压：3.3V/5V
- 通信接口：SPI
- 分辨率：296 x 128
- 显示颜色：黑、白
- 局部刷新：0.3s
- 全局刷新 ：2s


## 2. pico w 基本配置
### 2.1 刷固件
- https://micropython.org/download/rp2-pico-w/

- 下载类似`rp2-pico-w-20221107-unstable-v1.19.1-616-g5987130af.uf2`
- 首次将 pico w 连接电脑之后，会以U盘形式弹出来，把固件拖进去。
- 已经刷过固件的，按着板子上的 BOOTTSEL 按钮连接电脑。 

重新上电，固件就自动刷好了。

### 2.2 开发环境 thonny
- 安装 thonny, `scoop install thonny` 
- Thonny IED： 打开 '运行' - '配置解释器'， 配置一下
- 运行一下板载的 LED 测试程序：
 
``` python
from machine import Pin 
import time

led = Pin('LED', Pin.OUT)
while(True):
    led.on()
    time.sleep(1)
    led.off()
    time.sleep(1)
```
可以看到板载的 LED 在闪烁。

## 3. 处理 mnist 数据集，保存成二进制文件

* 由于pico可用的内存有限， thonny中显示仅有 800kb 左右可用？

* 每个数字的mnist字符为 28x28 = 784 像素， 原始数据集是 0-255 黑白色阶的。
* 这里我们节省存储空间，将每个像素压缩成以黑、白图像保存，这样每个像素仅占1个bit
* 那么784个bit需要 784 / 8 = 98 个字节，约 0.1kb
* 也就是每个数字的 mnist 字符的存储空间为 ~ 0.1kb

* 选择`x_train`数据集， 选出中 0-9 每个数字的前 500 个
* 分别转换成一个 `*.bin` 文件保存，文件名：`font_lib_{0-9}.bin` 
* 那么每个`*.bin` 文件为 48kb，全部 mnist font lib 总共占用 480kb

``` python
#%%
import json
import numpy as np


# 1.load mnist dataset
with np.load('../mnist.npz') as f:
    x_train, y_train = f['x_train'], f['y_train']
    x_test, y_test = f['x_test'], f['y_test']

with open('../mnist_index.json', 'r') as f:
    idx_dict = json.load(f)

#%%
# 2. 将 mnist 打印成字符画
def draw_mnist_num(image):
    bool_array = np.array(image > 128, dtype=int)
    print(bool_array)

    char_array = np.where(image > 128, '@', '-')
    for row in char_array:
        print(''.join(i for i in row))

draw_mnist_num(x_train[0])

#%%
# 3. 将mnist转成2进制字符
def convert_2_hex_str(image):
    # print(image.shape)
    image_bw = image > 128
    image_bit = np.packbits(image_bw)
    # print(image_bit)
    char_2 = image_bit.tobytes()
    # print(char_2)
    return char_2

mm_2 = convert_2_hex_str(x_train[0])
print(len(mm_2), mm_2)

# %% 
# 4. 转成字符数组
def gen_mnist_font_lib_str(m=1):
    font_lib = []

    for num in range(10):
        font = b''
        for idx in idx_dict[str(num)][:m]:
            img = x_train[idx]
            xxx = convert_2_hex_str(img)
            font += xxx

        font_lib.append(font)

    return font_lib


mnist_font_lib = gen_mnist_font_lib_str(500)
print(len(mnist_font_lib))


# 5. 保存
for n, font in enumerate(mnist_font_lib):
    f = open(f'font_lib_{n}.bin', 'wb')
    f.write(font)
    f.close()

```

## 4. 先测试下用 pico w 显示 mnist 字符

- 将生成的 `*.bin` 文件通过 Thonny 全部上传至 pico w。

- 测试一下能否正常读取并显示。

### 4.1 读取 mnist 字符
``` python
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
```

### 4.2 绘制字符 28x28 像素
``` python
# 字符串长度为784，按照 28x28 逐个绘制像素 
def MNIST(draw, mf, i):    
    c0 = [2, 72, 154, 224]
    r0 = [20, 20, 20, 20]

    mf_x28 = [[mf_str[i*28+j] for j in range(28)] for i in range(28)]
    for r in range(28):
        for c in range(28):
            color = 0x00 if mf[r*28+c]=='1' else 0xff
            draw.pixel(c + c0[i], r + r0[i], color)

```

### 4.3 绘制字符，缩放为 nR x nC 像素
``` python
# 字符串长度为784，按照 nR x nC 逐个绘制像素 
def MNIST(draw, mf, i):    
    c0 = [2, 72, 154, 224]
    r0 = [20, 20, 20, 20]
    nR = 100
    nC = 70

    # resize: 28x28 -> nRxnC
    # mf_x28 = [[mf_str[i*28+j] for j in range(28)] for i in range(28)]
    # mf_rsz = [[int(mf_x28[int(28*r/nR)][int(28*c/nC)]) for c in range(nC)] for r in range(nR)]
    for r in range(nR):
        for c in range(nC):
            color = mf[ int(28*r/nR) * 28 + int(28*c/nC) ]
            color = 0x00 if color == '1' else 0xff
            draw.pixel(c + c0[i], r + r0[i], color)
```

详见 `Pico_epd29_mnist_clock_test.py`


## 5. 在墨水屏显示时间

详见 `Pico_main.py`

