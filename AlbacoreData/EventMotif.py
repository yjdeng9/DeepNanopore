import os


class MotifBatch:
    def __init__(self, motif_df_list, raw_signal):
        self.motif_list = []

        self._load_motif_list(motif_df_list, raw_signal)

    def _load_motif_list(self, motif_df_list, raw_signal):
        for i in range(len(motif_df_list)):
            sub_frame = motif_df_list[i]
            model_state = sub_frame.ix[0, 'model_state']

            mean_list = sub_frame['mean'].values.tolist()
            stdv_list = sub_frame['stdv'].values.tolist()

            start_index = sub_frame.ix[0, 'start']
            end_index = sub_frame.ix[sub_frame.shape[0] - 1, 'start'] + sub_frame.ix[
                sub_frame.shape[0] - 1, 'length']
            sub_raw_signal = raw_signal[start_index:end_index]

            motif = Motif(model_state,start_index, end_index-start_index, i)
            motif.set_mean(mean_list)
            motif.set_stdv(stdv_list)
            motif.set_raw_signal(sub_raw_signal)

            self.motif_list.append(motif)

    def write_motifs(self, out_file):
        out_path = os.path.dirname(out_file)
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        with open(out_file, 'w') as out_motif:
            for sub_motif in self.motif_list:
                def write_list(add_list):
                    add_line = '\t'.join(str(value) for value in add_list)
                    out_motif.write(add_line)
                    out_motif.write('\n')

                out_motif.write('>%s;%d;%d;%d\n' % (
                    sub_motif.model_state, sub_motif.signal_index, sub_motif.signal_length, sub_motif.read_index))
                write_list(sub_motif.mean)
                write_list(sub_motif.stdv)
                write_list(sub_motif.raw_signal)

    def write_csvs(self, out_path, base_type='front'):
        if base_type is 'centre':
            base_position = 2
        else:
            base_position = 0

        # 设置输出文件的子目录
        sub_path = os.path.join(out_path, '%s_base' % base_type)
        if not os.path.exists(sub_path):
            os.makedirs(sub_path)

        def add_list_to_file(add_list, file_name):
            out_file = os.path.join(sub_path, file_name)
            add_line = ','.join(str(value) for value in add_list)
            with open(out_file, 'a') as out_tmp:
                out_tmp.write(add_line)
                out_tmp.write('\n')

        for sub_motif in self.motif_list:
            if sub_motif.model_state[base_position] != 'A':
                continue
            add_list_to_file(sub_motif.mean, 'event_mean_motif_%s.csv' % sub_motif.model_state)

            if sub_motif.raw_signal is not None:
                add_list_to_file(sub_motif.raw_signal, 'raw_signal_motif_%s.csv' % sub_motif.model_state)


class MotifFileReader:
    def __init__(self, motif_file):
        motif_list = []
        with open(motif_file, 'r') as mr:
            i = 0
            for line in mr:
                line = line.strip()
                if i % 4 == 0:
                    if not line.startswith('>'):
                        print("this is a wrong motif file!")
                        break
                    mnotes = line.replace('>','').split(';')
                    tmp_motif = Motif(mnotes[0], int(mnotes[1]), int(mnotes[2]), int(mnotes[3]))
                elif i % 4 == 1:
                    motif_mean = line.split('\t')
                    tmp_motif.set_mean(list(map(float, motif_mean)))
                elif i % 4 == 2:
                    motif_stdv = line.split('\t')
                    tmp_motif.set_stdv(list(map(float, motif_stdv)))
                elif i % 4 == 3:
                    motif_raw_signal = line.split('\t')
                    tmp_motif.set_raw_signal(list(map(float, motif_raw_signal)))
                    motif_list.append(tmp_motif)
                i += 1
        self.motif_list = motif_list

    def get_motif_list(self):
        return self.motif_list


class Motif:
    def __init__(self, model_state, signal_index, signal_length, read_index):
        self.model_state = model_state
        self.signal_index = signal_index
        self.signal_length = signal_length
        self.read_index = read_index

        self.mean = None
        self.stdv = None
        self.raw_signal = None

    def set_mean(self, mean_list):
        self.mean = mean_list

    def set_stdv(self, stdv_list):
        self.stdv = stdv_list

    def set_raw_signal(self, raw_signal_list):
        self.raw_signal = raw_signal_list

    def show(self):
        print(self.model_state,end='\t')
        print(self.signal_index, end='\t')
        print(self.signal_length, end='\t')
        print(self.read_index)

        print(self.mean)
        print(self.stdv)
        print(self.raw_signal)