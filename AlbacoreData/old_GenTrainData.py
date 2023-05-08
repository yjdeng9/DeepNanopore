#!/usr/bin/python
# -*- coding: UTF-8 -*-


from argparse import ArgumentParser
import copy
import h5py
import math
import os


def get_read_motif_mean(fast5):
    # 从fast5文件中获取event信息
    fast_five = h5py.File(fast5, 'r')
    event_motif = fast_five['Analyses/Basecall_1D_000/BaseCalled_template/Events']['model_state']
    event_mean = fast_five['Analyses/Basecall_1D_000/BaseCalled_template/Events']['mean']
    if len(event_motif) != len(event_mean):
        return False

    # 对每一motif进行检查，若不为A motif，则跳过
    n = math.ceil(len(event_motif[0].decode('utf-8')) / 2) - 1
    motif_list = []
    mean_list = []
    for i in range(len(event_motif)):
        a_motif = event_motif[i].decode('utf-8')
        a_mean = event_mean[i]
        if a_motif[n] != 'A':
            continue
        motif_list, mean_list = add_motif_value(motif_list, mean_list, a_motif, a_mean)
    print(mean_list)
    if len(motif_list) != 0:
        last_values = copy.deepcopy(mean_list[-1])
        mean_list[-1] = sum(last_values) / len(last_values)
    else:
        print('Worrying: there is a no-A motif file, FILENAME: %s' % fast5)
    fast_five.close()
    # 结果返回每一个motif对应的mean值
    return motif_list, mean_list


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


def iter_dirs(fast_five, dir_index):
    group_list = []
    data_list = []
    if fast_five[dir_index].__class__ is h5py.Group:
        group_list.append(dir_index)
        for name in fast_five[dir_index]:
            sub_index = dir_index + '/' + name
            add_groups, add_datas = iter_dirs(fast_five, sub_index)
            group_list.extend(add_groups)
            data_list.extend(add_datas)
    else:
        data_list.append(dir_index)
    return group_list, data_list


def has_events(fast5):
    fast_five = h5py.File(fast5, 'r')
    group_list = []
    data_list = []
    for sub_name in fast_five:
        sub_group, sub_data = iter_dirs(fast_five, sub_name)
        group_list.extend(sub_group)
        data_list.extend(sub_data)
    fast_five.close()
    for data_set in data_list:
        if 'Events' in data_set:
            return True
    print(fast5)
    return False


def loop_reads(file_path, out_path, num_limit, label):

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    if label == 'positive':
        binary_label = 1
        out_path = os.path.join(out_path,'positive_data.txt')
    else:
        binary_label = 0
        out_path = os.path.join(out_path,'negative_data.txt')

    fast5_paths = sorted(list(gci(file_path, ".fast5")))
    out_file = open(out_path, 'w')
    count = 0
    for fast5 in fast5_paths:
        if not has_events(fast5):
            continue
        _, read_mean = get_read_motif_mean(fast5)
        for mean in read_mean:
            print(mean, end=' ', file=out_file)
        print(binary_label, file=out_file)

        count += 1
        if num_limit is not None and count >= num_limit:
            break

    out_file.close()
    print('get %d %s datas!' % (count, label))


# 将新的motif和mean值添加进原本的list中，如果前后两个motif相同，则合并取均值
def add_motif_value(motif_list, value_list, motif, value):
    if len(motif_list) == 0:
        return [motif], [[value]]
    last_motif = motif_list[-1]
    if motif == last_motif:
        value_list[-1].append(value)
    else:
        last_values = copy.deepcopy(value_list[-1])
        value_list[-1] = sum(last_values)/len(last_values)
        motif_list.append(motif)
        value_list.append([value])
    return motif_list, value_list


def main():
    # 读取参数
    parser = ArgumentParser()
    parser.add_argument('-i','--input_path', required=True)
    parser.add_argument('-p','--pos_fold')
    parser.add_argument('-n', '--neg_fold')
    parser.add_argument('-o', '--out_path', default='outPut')
    parser.add_argument('-m', '--max_read_num', type=int, default=None)
    args = parser.parse_args()

    # 对阳性数据和阴性数据分别处理，存储
    pos_file = os.path.join(args.input_path, args.pos_fold)
    neg_file = os.path.join(args.input_path, args.neg_fold)
    loop_reads(pos_file, args.out_path, args.max_read_num, 'positive')
    loop_reads(neg_file, args.out_path, args.max_read_num, 'negative')

    # 测试motif提取功能
    # fast5 = 'E:\\2018_08\\meDNA\\workspace\\0\\GXB01133_20180601_FAH60408_GA10000_sequencing_run_BNP18L0040_0601_92550_read_324_ch_337_strand.fast5'
    # motif_list, mean_list = get_read_motif_mean(fast5)
    # print(motif_list)
    # print(mean_list)


if __name__ == '__main__':
    main()
