## 用树莓派和墨水屏做一个 mnist-clock

- 灵感 https://github.com/dheera/mnist-clock



## 墨水屏
- 型号：微雪 2.9inch e-Paper Module， 带驱动板，8PIN
- 工作电压：3.3V/5V
- 通信接口：SPI
- 分辨率：296 x 128
- 显示颜色：黑、白
- 局部刷新：0.3s
- 全局刷新 ：2s

- 接线表：

| 墨水屏 8PIN | 树莓派 40PIN 物理序号 | 备注 |
| ----------- | --------------------- | ---- |
| VCC         | 1                     | 3.3V |
| GND         | 6                     | GND  |
| DIN         | 19                    |
| CLK         | 23                    |
| CS          | 24                    |
| DC          | 22                    |
| RST         | 11                    |
| BUSY        | 18                    |


## 树莓派基本配置

- 详细步骤见帮助文档: https://www.waveshare.net/wiki/2.9inch_e-Paper_Module
- 程序源码在 github 也有: https://github.com/waveshare/e-Paper
- 下载`git clone https://github.com/waveshare/e-Paper.git --depth 1`
- 目录如下，有用的文件就几个：

``` bash
├───Arduino
├───RaspberryPi&JetsonNano
│   ├───c
│   │   └─── ...
│   └───python
│       │   readme_rpi_CN.txt
│       │   setup.py
│       │   ...
│       │
│       ├───examples
│       │       epd_2in9bc_test.py  # 测试程序
│       │       ...
│       │
│       ├───lib
│       │   └───waveshare_epd
│       │           epd2in9.py      # 主逻辑
│       │           epdconfig.py    # 配置文件
│       │           __init__.py
│       │           ...
│       │
│       └───pic                
│               2in9.bmp            # 图片
│               Font.ttc            # 字体文件，文泉驿，含中文字体
│               ...
└─── ...

```

- 运行测试程序
 
``` bash
cd e-Paper/'RaspberryPi&JetsonNano'/
cd python/examples

sudo python3 epd_2in9bc_test.py
```

## mnist 数据集

- 下载 `mnist.npz`
https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz

- 我们使用`x_train`的60000个数字，把0-9对应的序号(index)，提取出来，保存到 `mnist_index.json`


## 测试用 opencv 显示时间

![](/images/mnist-clock.png)


## 所有文件

``` bash
.
├── cv2_mnist_clock.py     # 测试用 opencv 显示时间
├── epd29_mnist_clock.py   # 在墨水屏显示时间
├── epd_2in9_test.py
├── gen_mnist_index.py     # 提取序号(index)
├── lib
│ ├── epd2in9.py
│ ├── epdconfig.py
│ ├── Font.ttc
│ └── __init__.py
├── mnist_index.json
└── mnist.npz

```
