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
