# %%
import numpy as np
import json


img_rows, img_cols = 28, 28

# the data, split between train and test sets
path = 'mnist.npz'
with np.load(path) as f:
    x_train, y_train = f['x_train'], f['y_train']
    x_test, y_test = f['x_test'], f['y_test']

print('x_train.shape: {}, y_train.shape: {}'.format(x_train.shape, y_train.shape))
print('x_test.shape: {}, y_test.shape: {}'.format(x_test.shape, y_test.shape))

print(x_train[0], y_train[0])
print(x_test[0], y_test[0])

# %%

idx_dict = {}

for i in range(10):
    idx_dict[i] = []

for idx in range(60000):
    num = y_train[idx]
    idx_dict[num].append(idx)

    # if idx == 60: break

# print(idx_dict)
idx_json = json.dumps(idx_dict)
# print(idx_json)

with open('mnist_index.json', 'w') as f:
    json.dump(idx_dict, f)

# with open('mnist_index.json', 'r') as f:
#     data = json.load(f)
# print(data)
