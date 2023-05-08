import h5py
import os
import pandas as pd


class Fast5Reader:
    def __init__(self, fast5):
        self.fast_five = h5py.File(fast5, 'r')

    def show_main_dir(self):
        for name in self.fast_five:
            print("\n@ "+name)
            self.iter_dirs(name, True)

    def iter_dirs(self, dir_index, attrs_show=False):
        print(dir_index)
        if attrs_show:
            self._has_attributes(dir_index)
        if self._is_group(dir_index):
            for name in self.fast_five[dir_index]:
                sub_index = dir_index + '/' + name
                self.iter_dirs(sub_index, True)

    def _is_group(self, dir_index):
        if "InputEvents" in dir_index:
            return False
        # if self.fast_five[dir_index].
        if self.fast_five[dir_index].__class__ is h5py.Group:
            return True
        else:
            return False

    def _has_attributes(self, dir_index, show_attributes=True):
        if "InputEvents" in dir_index:
            return False
        if len(self.fast_five[dir_index].attrs) == 0:
            return False
        else:
            if show_attributes:
                print(dir_index, end=" ")
                print("has attributes: \n", end="")
                for att in self.fast_five[dir_index].attrs:
                    print("# ",end="")
                    print(att, end="\t")
                    print(self.fast_five[dir_index].attrs[att])
                print()
            return True

    def show_a_dir(self, dir_index):
        for name in self.fast_five[dir_index]:
            print(dir_index + "/" + name)

    def get_raw_signal(self):
        if self._has_signal():
            raw_file = self.get_file(self.signal_index)
        else:
            print("Can't find signal file!")
            return

        raw_signal_list = []
        for value in raw_file:
            raw_signal_list.append(value)
        return raw_signal_list

    def show_raw_signal(self):
        raw_signal_list = self.get_raw_signal()
        if raw_signal_list is None:
            return
        i = 0
        for _ in raw_signal_list:
            print(_, sep='\t', end='\t')
            i += 1
            if i % 15 == 0:
                print()
        print()

    def _has_signal(self):
        group_list = []
        data_list = []
        for sub_name in self.fast_five:
            sub_group, sub_data = self._iter_dirs(sub_name)
            group_list.extend(sub_group)
            data_list.extend(sub_data)
        for data_set in data_list:
            if 'Signal' in data_set:
                self.signal_index = data_set
                return True
        return False

    def _iter_dirs(self, dir_index):
        group_list = []
        data_list = []
        if self.fast_five[dir_index].__class__ is h5py.Group:
            group_list.append(dir_index)
            for name in self.fast_five[dir_index]:
                sub_index = dir_index + '/' + name
                add_groups, add_datas = self._iter_dirs(sub_index)
                group_list.extend(add_groups)
                data_list.extend(add_datas)
        else:
            data_list.append(dir_index)
        return group_list, data_list

    def get_event_notes(self):
        if self._has_events():
            event_file = self.get_file(self.event_index)
        else:
            print("Can't find event file!")
            return

        # print(event_file.dtype.fields.keys())
        # 'mean', 'start', 'stdv', 'length', 'model_state', 'move', 'p_model_state', 'weights'
        field_names = event_file.dtype.names
        event_frame = pd.DataFrame()
        for field_name in field_names:
            if field_name == 'model_state':
                event_frame[field_name] = [value.decode('utf-8') for value in event_file[field_name]]
            else:
                event_frame[field_name] =  event_file[field_name]
        return event_frame

    def _has_events(self):
        group_list = []
        data_list = []
        for sub_name in self.fast_five:
            sub_group, sub_data = self._iter_dirs(sub_name)
            group_list.extend(sub_group)
            data_list.extend(sub_data)
        for data_set in data_list:
            if 'Events' in data_set:
                self.event_index = data_set
                return True
        return False

    def get_file(self,dir_index):
        return self.fast_five[dir_index]

    def get_attribute_values(self, dir_index, attribute):
        print(self.fast_five[dir_index].attrs[attribute])

    def close(self):
        self.fast_five.close()


def gci(file_path):
    files_list = []
    files = os.listdir(file_path)
    for fi in files:
        fi_d = os.path.join(file_path, fi)
        if os.path.isdir(fi_d):
            add_list = gci(fi_d)
            files_list.extend(add_list)
        else:
            if '.fast5' in fi_d:
                files_list.append(fi_d)
    return files_list


if __name__ == '__main__':
    # test_path = 'D:/Users/alan/'
    # fast5 = test_path + 'GXB01133_20180802_FAH68033_GA50000_mux_scan_BNP18L0066_0802_A_74649_read_4_ch_487_strand.fast5'
    #
    # show = Fast5Reader(fast5)
    # show.show_main_dir()
    #
    # show.get_raw_signal()
    # show.get_event_notes()
    #
    # show.close()
    test_path = '/data/dengyongjie/m6aNanopore/datas/Basecalling_data/totalData/GXB01133/BNP18L0066-0802-A/GA50000/reads/0/'
    test_files = gci(test_path)

    fastq_index = 'Analyses/Basecall_1D_000/BaseCalled_template/Fastq'
    for test_file in test_files:
        if not '_read_4_ch_' in test_file:
            continue
        print(test_file)
        test_fast5 = Fast5Reader(test_file)
        # test_fast5.show_main_dir()
        test_fastq = test_fast5.get_file(fastq_index)
        for line in test_fastq:
            print(line)
        # print(test_fastq)
        print()
        test_fast5.close()
