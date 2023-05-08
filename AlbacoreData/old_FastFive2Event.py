from argparse import ArgumentParser

import h5py
import os


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


class Fast5List:
    def __init__(self, input_path, output_path, num_limit):
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        fast5_paths = sorted(list(gci(input_path, ".fast5")))
        count = 0
        for fast5 in fast5_paths:
            path_inf = fast5.replace(input_path, '').split(os.path.sep)
            out_path = os.path.join(output_path, os.path.sep.join(path_inf[0:2]))
            EventWriter(fast5, out_path)

            count += 1
            if num_limit is not None and count >= num_limit:
                break
            if (count % 1000) == 0:
                print('get %d reads!' % count)
        print('whole %d reads!' % count)


class EventWriter:
    def __init__(self, fast5, out_path):
        file_name = os.path.basename(fast5).strip().replace('.fast5', '')
        self.fast_five = h5py.File(fast5, 'r')
        default_index = 'Analyses/Basecall_1D_000/BaseCalled_template/Events'
        self.event_index = default_index
        if self._has_events():
            if not os.path.exists(out_path):
                os.makedirs(out_path)
            self.event_dataset = self.fast_five[self.event_index]
            self._write_event(os.path.join(out_path, file_name + '.txt'))
        else:
            grader_father_path = os.path.abspath(out_path + (str(os.path.sep + "..")*2))
            worry_file = os.path.join(grader_father_path, "no_event_list.txt")
            with open(worry_file, 'a') as add_worry:
                add_worry.write(out_path)
                add_worry.write('\t')
                add_worry.write(file_name)
                add_worry.write('\n')
        self.fast_five.close()

    def _write_event(self, out_file):
        field_names = self.event_dataset.dtype.names
        with open(out_file, 'w') as out:
            out.write('\t'.join(str(field_name) for field_name in field_names))
            out.write('\n')
            for i in range(self.event_dataset.size):
                out.write('\t'.join(self._get_event_value(i, field_name) for field_name in field_names))
                out.write('\n')

    def _get_event_value(self, num, filed_name):
        value = self.event_dataset[filed_name][num]
        if filed_name == 'model_state':
            value = value.decode('utf-8')
        return str(value)

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


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-i', '--input_path', required=True)
    parser.add_argument('-o', '--output_path', default='outPut')
    parser.add_argument('-m', '--max_read_num', type=int, default=None)
    args = parser.parse_args()
    print('input_path:', end=' ')
    print(os.path.abspath(args.input_path))
    print('output_path:', end=' ')
    print(os.path.abspath(args.output_path))
    Fast5List(args.input_path, args.output_path, args.max_read_num)