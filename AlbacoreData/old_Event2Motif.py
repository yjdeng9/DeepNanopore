# 5-mer m6a_or_not  mean[] stedv[]
import copy
import os

import h5py
import numpy as np
import pandas as pd
from AlbacoreData.FastFiveReader import Fast5Reader


class BatchFile:
    def __init__(self, input_path):
        def gci(file_path, index_type):
            files_list = []
            files = os.listdir(file_path)
            for fi in files:
                fi_d = os.path.join(file_path, fi)
                if os.path.isdir(fi_d):
                    add_list = gci(fi_d, index_type)
                    files_list.extend(add_list)
                else:
                    if index_type in fi_d:
                        files_list.append(fi_d)
            return files_list

        self.input_path = input_path
        self.fast5_paths = sorted(list(gci(input_path, ".fast5")))

    def fast5_to_motif(self, out_path):
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        log_file = os.path.join(out_path, "log_file.txt")
        log_add = open(log_file, 'a')

        for fast5 in self.fast5_paths:
            re = ReadEvent(fast5, True)
            if re.event_frame is None:
                log_add.write("[Don't exist event file] %s\n" % fast5)
                continue

            path_inf = fast5.replace(self.input_path, '').split(os.path.sep)
            sub_out_path = os.path.join(out_path, os.path.sep.join(path_inf[0:2]))
            file_name = os.path.basename(fast5).strip().replace('.fast5', '.fasta')

            re.gen_motif_data(os.path.join(sub_out_path, file_name))


class ReadEvent:
    def __init__(self, input_file, is_fast5_file=False):
        self.sub_path = ''
        self.fast5_signal = None
        self.signal_start_list = []

        if is_fast5_file:
            self._load_fast5(input_file)
        else:
            self._load_event(input_file)

    def gen_motif_data(self, out_file):
        if self.event_frame is None or self.fast5_signal is None:
            return

        motif_list = self._map_same_motif()

        with open(out_file, 'w') as out_motif:
            def write_list(add_list):
                add_line = '\t'.join(str(value) for value in add_list)
                out_motif.write(add_line)
                out_motif.write('\n')

            for i in range(len(motif_list)):
                sub_frame = motif_list[i]
                motif = sub_frame.ix[0, 'model_state']

                mean_list = sub_frame['mean'].values.tolist()
                stdv_list = sub_frame['stdv'].values.tolist()

                start_index = sub_frame.ix[0, 'start']
                end_index = sub_frame.ix[sub_frame.shape[0] - 1, 'start'] + sub_frame.ix[
                    sub_frame.shape[0] - 1, 'length']
                sub_raw_signal = self.fast5_signal[start_index:end_index]

                out_motif.write('>%s;%d-%d\n' % (motif, start_index, end_index))
                write_list(mean_list)
                write_list(stdv_list)
                write_list(sub_raw_signal)

    def gen_train_data(self, base_type, out_path):
        if self.event_frame is None:
            return

        motif_list = self._map_same_motif()

        # 设置输出文件的子目录
        if base_type is 'centre':
            base_position = 2
        else:
            base_position = 0
        self.sub_path = os.path.join(out_path, '%s_base' % base_type)
        if not os.path.exists(self.sub_path):
            os.makedirs(self.sub_path)

        for i in range(len(motif_list)):
            sub_frame = motif_list[i]
            motif = sub_frame.ix[0, 'model_state']
            base = motif[base_position]
            if base != 'A':
                continue

            mean_list = sub_frame['mean'].values.tolist()
            stdv_list = sub_frame['stdv'].values.tolist()

            self._add_list_to_file(mean_list, 'event_mean_motif_%s.txt' % motif)

            self._add_list_to_file(['>mean;stdv'], 'event_mean_stdv_motif_%s.txt' % motif)
            self._add_list_to_file(mean_list, 'event_mean_stdv_motif_%s.txt' % motif)
            self._add_list_to_file(stdv_list, 'event_mean_stdv_motif_%s.txt' % motif)

            if self.fast5_signal is not None:
                start_index = sub_frame.ix[0, 'start']
                end_index = sub_frame.ix[sub_frame.shape[0]-1, 'start']+sub_frame.ix[sub_frame.shape[0]-1, 'length']

                sub_raw_signal = self.fast5_signal[start_index:end_index]
                self._add_list_to_file(sub_raw_signal, 'raw_signal_motif_%s.txt' % motif)

    def _load_fast5(self, fast5_file):
        fast5_read = Fast5Reader(fast5_file)
        self.event_frame = fast5_read.get_event_notes()
        self.fast5_signal = fast5_read.get_raw_signal()
        fast5_read.close()

    def _load_event(self, event_file):
        event_read = pd.read_csv(event_file, sep='\t')
        self.event_frame = event_read

    def _map_same_motif(self):
        motif_list = []
        # 以model_state为索引，切片
        last_motif = 'NNNNN'
        start_index = 0
        for i in range(self.event_frame.shape[0]):
            current_motif = self.event_frame['model_state'][i]
            if current_motif != last_motif and i != 0:
                last_frame = pd.DataFrame(self.event_frame[start_index:i])
                last_frame.index = range(i-start_index)
                motif_list.append(last_frame)
                start_index = i
            last_motif = copy.deepcopy(current_motif)
        return motif_list

    def _add_list_to_file(self, add_list, file_name):
        out_file = os.path.join(self.sub_path, file_name)
        add_line = '\t'.join(str(value) for value in add_list)
        with open(out_file, 'a') as out_tmp:
            out_tmp.write(add_line)
            out_tmp.write('\n')


if __name__ == '__main__':
    test_file = 'D:/Users/alan/GXB01133_20180802_FAH68033_GA50000_mux_scan_BNP18L0066_0802_A_74649_read_4_ch_487_strand.txt'
    test_fast5 = 'D:/Users/alan/GXB01133_20180802_FAH68033_GA50000_mux_scan_BNP18L0066_0802_A_74649_read_4_ch_487_strand.fast5'
    # re = ReadEvent(test_file)
    # # re.gen_train_data('centre', 'D:/Users/alan/result')
    # re.gen_train_data('front', 'D:/Users/alan/result/event')

    re = ReadEvent(test_fast5, True)
    # re.gen_train_data('centre', 'D:/Users/alan/result')
    re.gen_train_data('front', 'D:/Users/alan/result/fast5')
    re.gen_motif_data('D:/Users/alan/result/test.fasta')

    batch_input_path = ""
    batch_out_path = ""




