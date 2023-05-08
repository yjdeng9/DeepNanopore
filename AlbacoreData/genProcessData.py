import copy
import os
from argparse import ArgumentParser

import pandas as pd

from EventMotif import MotifBatch
from FastFiveReader import Fast5Reader


class BatchMotif:
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
        print(log_file)

        total_num = len(self.fast5_paths)
        continue_list = []
        count = 0

        with open(log_file, 'w') as log_writer:
            log_writer.write('input_path: %s\n' % self.input_path)
            log_writer.write('output_path: %s\n' % out_path)
            log_writer.write('Total num : %d files\n' % total_num)

        for fast5 in self.fast5_paths:
            gen_motif = FastFive2Motif(fast5)
            if gen_motif.motif_batch is None:
                continue_list.append(fast5)
                continue

            path_inf = fast5.replace(self.input_path, '').split(os.path.sep)
            sub_out_path = os.path.join(out_path, os.path.sep.join(path_inf[0:2]))
            file_name = os.path.basename(fast5).strip().replace('.fast5', '.fasta')
            gen_motif.write_motif_file(os.path.join(sub_out_path, file_name))
            gen_motif.write_csv_file(os.path.join(out_path, 'motif_csv/'))

            count += 1
            if count % 1000 == 0:
                with open(log_file, 'a') as log_add:
                    log_add.write('>=========get %d/%d motifs\n' % (count, total_num))

        with open(log_file, 'a') as log_add_end:
            log_add_end.write('Finish! get %d motifs \n\n' % count)
            for inexistent_file in continue_list:
                log_add_end.write('[Don\'t exist event file] %s\n' % inexistent_file)


class FastFive2Motif:
    def __init__(self, input_file, is_fast5_file=True):
        self.sub_path = ''
        self.fast5_signal = None
        # self.signal_start_list = []
        self.motif_batch = None

        if is_fast5_file:
            self._load_fast5(input_file)
            self._gen_motif_data()
        else:
            self._load_event(input_file)

    def _gen_motif_data(self):
        if self.event_frame is None or self.fast5_signal is None:
            return

        motif_list = self._map_same_motif()
        self.motif_batch = MotifBatch(motif_list, self.fast5_signal)

    def write_motif_file(self, out_file):
        self.motif_batch.write_motifs(out_file)

    def write_csv_file(self, out_path):
        self.motif_batch.write_csvs(out_path, 'front')
        self.motif_batch.write_csvs(out_path, 'centre')

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


if __name__ == '__main__':
    # test_fast5 = 'D:/Users/alan/GXB01133_20180802_FAH68033_GA50000_mux_scan_BNP18L0066_0802_A_74649_read_4_ch_487_strand.fast5'
    # test_out_file = 'D:/Users/alan/result/test.fasta'
    # test_out_path = 'D:/Users/alan/result'
    # test_py = FastFive2Motif(test_fast5)
    # test_py.write_motif_file(test_out_file)
    # test_py.write_csv_file(test_out_path)

    parser = ArgumentParser()
    parser.add_argument('-i', '--input_path', required=True)
    parser.add_argument('-o', '--output_path', default='outPut')
    args = parser.parse_args()
    new_motif = BatchMotif(args.input_path)
    new_motif.fast5_to_motif(args.output_path)


