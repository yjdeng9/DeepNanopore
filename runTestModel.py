import argparse
import os

import numpy as np
from keras.preprocessing.sequence import pad_sequences

from KerasModel.SimpleLSTM import NewLSTM
from KerasModel.meData import MeData


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help='display an integer')
    parser.add_argument('-o', '--out_path', default='./', help='display an integer')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    # 38190 positive data + 372294 negative data
    path = args.path
    me_data = MeData(path)
    (x_train, y_train), (x_test, y_test) = me_data.divide_data(0.8)
    # 需要调节格式
    # shapes：(328388, 6846)，(82096, 6846)
    # max_len = max(len(line) for line in x_train)
    max_len = 9800
    x_train = pad_sequences(x_train, dtype=np.float32, maxlen=max_len, padding='post')
    x_test = pad_sequences(x_test, dtype=np.float32, maxlen=max_len, padding='post')

    # CNN Model
    save_path = os.path.join(args.out_path, 'tmp_cnn_model.h5')
    cnn_model = NewLSTM(x_train, y_train, x_test, y_test, 'CNN')
    cnn_model.fit_model(20, 5)
    cnn_model.save_model(save_path)

    score = cnn_model.evaluate_score()
    print('Test score:', score[0])
    print('Test accuracy:', score[1])
    print(score)

    # log_file = os.path.join(args.out_path, 'log_file.txt')
    # with open(log_file, 'w') as out_file:
    #     out_file.write(cnn_model.evaluate_score())




