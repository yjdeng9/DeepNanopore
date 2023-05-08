import os
from matplotlib import pyplot as plt
import numpy as np


class BatchCSV:
    def __init__(self, positive_path, negative_path, out_path):
        self.positive_path = positive_path
        self.negative_path = negative_path
        self.out_path = out_path

        self.pos_mean_list = []
        self.neg_mean_list = []

        model_state_set = set([])
        positive_files = os.listdir(positive_path)
        for csv_file in positive_files:
            if not '.csv' in csv_file:
                continue
            csv_name = os.path.basename(csv_file).replace('.csv', '')
            model_state = csv_name.split('_')[-1]
            model_state_set.add(model_state)

        for model_state in model_state_set:
            self._couple_gen(model_state, 'event_mean_motif')
            self._couple_gen(model_state, 'raw_signal_motif')

        self.write_mean(self.pos_mean_list, 'positive_mean.txt')
        self.write_mean(self.neg_mean_list, 'negative_mean.txt')
        # self.draw_hist('dataVis.jpg')

    def _couple_gen(self, model_state, index_type):
        title = index_type + '_' + model_state + '.csv'
        pos_file = os.path.join(self.positive_path, title)
        neg_file = os.path.join(self.negative_path, title)
        if not os.path.exists(neg_file):
            return

        def get_mean_stdv(csv_file, data_type, sep=','):

            raw_data = []
            with open(csv_file, 'r') as test_read:
                for read_line in test_read:
                    line_list = read_line.strip().split(sep)
                    eval_list = list(map(float, line_list))
                    raw_data.append(eval_list)
            for row_list in raw_data:
                row_mean = np.mean(row_list)
                row_std = np.std(row_list)

                if data_type is 'pos':
                    self.pos_mean_list.append(row_mean)
                if data_type is 'neg':
                    self.neg_mean_list.append(row_mean)

        get_mean_stdv(pos_file, 'pos')
        get_mean_stdv(neg_file, 'neg')

    def write_mean(self, data_list, file_name):
        with open(os.path.join(self.out_path, file_name), 'w') as lw:
            for data in data_list:
                lw.write(str(data))
                lw.write('\t')


class DataVisual:
    def __init__(self, input_path, out_path):
        pos_path = os.path.join(input_path, 'positive_mean.txt')
        neg_path = os.path.join(input_path, 'negative_mean.txt')
        self.out_path = out_path

        self.pos_mean_list = self.open_file(pos_path)
        self.neg_mean_list = self.open_file(neg_path)
        self.draw_hist('dataVis.jpg')

    def open_file(self, file_path):
        open_list = []
        with open(file_path,'r') as oread:
            for line in oread:
                datas = line.strip().split('\t')
                for data in datas:
                    open_list.append(float(data))
        return open_list

    def draw_hist(self, img_title):

        plt.hist(self.neg_mean_list, bins=500, range=(0, 1000), normed=True, color='tan')
        plt.hist(self.pos_mean_list, bins=1000, range=(0, 1000), normed=True, color='tomato')

        plt.show()
        # plt.savefig(os.path.join(self.out_path, img_title))


if __name__ == '__main__':
    # Linux Coding

    # test_neg = '/data/dengyongjie/m6aNanopore/datas/Processing_data/testMotif/negative/motif_csv/front_base/'
    # test_pos = test_neg.replace('negative', 'positive')
    #
    # test_out_path = '/data/dengyongjie/m6aNanopore/scripts/LinuxModelScript/AlbacoreData/'
    #
    # test_train = BatchCSV(test_pos, test_neg, test_out_path)

    # Windows Coding

    win_path = 'E:\\2018_11\\m6A_Nanopore\\LinuxCopy\\LinuxModelScript\\AlbacoreData\\'
    data_vis = DataVisual(win_path, win_path)
