import pandas as pd
import numpy as np
import os

from DataPadding import DataPadding
from EventMotif import MotifFileReader


class GenRawSignal:
    def __init__(self):
        def gci(file_path, index):
            files_list = []
            files = os.listdir(file_path)
            for fi in files:
                fi_d = os.path.join(file_path, fi)
                if os.path.isdir(fi_d):
                    add_list = gci(fi_d, index)
                    files_list.extend(add_list)
                else:
                    if index in fi_d:
                        files_list.append(fi_d)
            return files_list

#     max_len = 53320



class BatchFasta:
    def __init__(self, positive_path, negative_path, out_path):
        def gci(file_path):
            files_list = []
            files = os.listdir(file_path)
            for fi in files:
                fi_d = os.path.join(file_path, fi)
                if os.path.isdir(fi_d):
                    add_list = gci(fi_d)
                    files_list.extend(add_list)
                else:
                    if '.fasta' in fi_d:
                        files_list.append(fi_d)
            return files_list

        self.positive_files = gci(positive_path)
        self.negative_files = gci(negative_path)
        self.out_path = out_path

        self.fasta2motif(self.positive_files, 'positive', 7)
        self.fasta2motif(self.negative_files, 'negative', 7)

    def fasta2motif(self, fasta_files, class_type, len_wing):
        out_file = os.path.join(self.out_path, class_type+'_train_data.txt')

        def write_train_data(data_title, out_data):
            with open(out_file, 'a') as out_add:
                out_add.write('>'+data_title+'\n')
                for out_line in out_data:
                    for out_value in out_line:
                        out_add.write(str(out_value) + '\t')
                    out_add.write('\n')

        for fasta_file in fasta_files:
            read_name = os.path.basename(fasta_file).replace('.fasta', '')
            print('get '+read_name)

            motif_reader = MotifFileReader(fasta_file)
            motif_list = motif_reader.get_motif_list()

            for i in range(len(motif_list)):
                if i<len_wing or i>=len(motif_list)-len_wing:
                    continue
                centre_base = motif_list[i].model_state[0]
                if centre_base is 'A':
                    train_array = []
                    motif_seq = ''
                    for j in range(i-len_wing, i+len_wing+1):
                        tmp_motif = motif_list[j]
                        motif_seq = motif_seq + tmp_motif.model_state[0]

                        tmp_mean = np.mean(tmp_motif.mean)
                        tmp_length = tmp_motif.signal_length

                        tmp_raw_signal = tmp_motif.raw_signal
                        tmp_raw_mean = np.mean(tmp_raw_signal)
                        tmp_raw_std = np.std(tmp_raw_signal)
                        tmp_raw_max = np.max(tmp_raw_signal)
                        tmp_raw_min = np.min(tmp_raw_signal)

                        tmp_list = [tmp_mean, tmp_length, tmp_raw_mean, tmp_raw_std, tmp_raw_max, tmp_raw_min]
                        train_array.append(tmp_list)

                    train_array = np.array(train_array)
                    # write_train_data(motif_seq, train_array)



class BatchCSV:
    def __init__(self, positive_path, negative_path, out_path):
        self.positive_path = positive_path
        self.negative_path = negative_path
        self.out_path = out_path

        model_state_set = set([])
        positive_files = os.listdir(positive_path)
        for csv_file in positive_files:
            if not '.csv' in csv_file:
                continue
            csv_name = os.path.basename(csv_file).replace('.csv', '')
            model_state = csv_name.split('_')[-1]
            model_state_set.add(model_state)

        for model_state in model_state_set:
            self._couple_gen(model_state, 'event_mean_motif', 200)
            self._couple_gen(model_state, 'raw_signal_motif', 500)

    def _couple_gen(self, model_state, index_type, index_max_len):
        title = index_type + '_' + model_state + '.csv'
        pos_file = os.path.join(self.positive_path, title)
        neg_file = os.path.join(self.negative_path, title)
        if not os.path.exists(neg_file):
            return

        out_file = os.path.join(self.out_path, index_type + '.txt')

        def get_pad_data(csv_file, sep=','):
            raw_data = []
            max_len = 0
            with open(csv_file, 'r') as test_read:
                for read_line in test_read:
                    line_list = read_line.strip().split(sep)
                    eval_list = list(map(float, line_list))
                    raw_data.append(eval_list)

                    if len(eval_list) >= max_len:
                        max_len = len(eval_list)

            data_pad = DataPadding(raw_data, max_len)
            padding_data = data_pad.pad_with_mean_stdv(index_max_len)
            return padding_data

        def write_train_data(out_data, label):
            with open(out_file, 'a') as out_add:
                for out_line in out_data:
                    for out_value in out_line:
                        out_add.write(str(out_value) + '\t')
                    out_add.write(str(label) + '\n')

        pos_pad = get_pad_data(pos_file)
        neg_pad = get_pad_data(neg_file)

        write_train_data(pos_pad, 1)
        write_train_data(neg_pad, 0)

        # return pos_pad, neg_pad


if __name__ == '__main__':
    # test_neg = '/data/dengyongjie/m6aNanopore/datas/Processing_data/testMotif/negative/motif_csv/front_base/'
    # test_pos = test_neg.replace('negative', 'positive')
    # test_out_path = '/data/dengyongjie/m6aNanopore/datas/Model_data/sample_2000/'
    # test_train = BatchCSV(test_pos, test_neg, test_out_path)

    test_neg = '/data/dengyongjie/m6aNanopore/datas/Processing_data/testMotif/negative/GA10000/reads/'
    test_pos = '/data/dengyongjie/m6aNanopore/datas/Processing_data/testMotif/positive/GA50000/reads/'
    test_out_path = '/data/dengyongjie/m6aNanopore/datas/Model_data/sample_2000/'
    test_train = BatchFasta(test_pos, test_neg, test_out_path)
