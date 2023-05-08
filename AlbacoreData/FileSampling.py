import os
import random


class FilesSampling:
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

    def get_small_sample(self, sampling_rate, output_path):
        print('raw sample has %d files' % len(self.fast5_paths))

        sample_num = 0
        for fast5 in self.fast5_paths:
            p = random.random()
            if p > sampling_rate:
                continue
            sample_num += 1
            out_file = fast5.replace(self.input_path, output_path)
            out_path = os.path.dirname(out_file)

            if not os.path.exists(out_path):
                os.makedirs(out_path)
            os.system('cp %s %s' % (fast5, out_path))
            # print(fast5)
            # print(out_path)
            # print()
            if sample_num >= 2000:
                break

        print('raw sample has %d files' % sample_num)


if __name__ == '__main__':
    input_path = '/data/dengyongjie/m6aNanopore/datas/Basecalling_data/totalData/'
    output_path = '/data/dengyongjie/m6aNanopore/datas/Basecalling_data/smallSampleData/'
    sampling = FilesSampling(input_path)
    sampling.get_small_sample(0.0015, output_path)
