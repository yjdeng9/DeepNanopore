import os
import sys
import h5py


def get_notes(fast5):
    fast_five = h5py.File(fast5, 'r')
    seq_kit = fast_five["UniqueGlobalKey/context_tags"].attrs["sequencing_kit"].decode('utf-8').upper()
    flow_cell = fast_five["UniqueGlobalKey/context_tags"].attrs["flowcell_type"].decode('utf-8').upper()
    fast_five.close()
    return flow_cell, seq_kit


def crate_script(fast5, flow_cell, seq_kit, out_path):
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    basecallor = '/home/dengyj/anaconda3/envs/py36/bin/read_fast5_basecaller.py'
    command = 'python %s -f %s -k %s -i %s -t %d -s %s -o fast5 --disable_filtering' %\
              (basecallor, flow_cell, seq_kit, fast5, 40, out_path)
    os.system(command)
    #print(command)
    check_the_result(fast5, out_path, '.fast5')


def check_the_result(input_path, out_path, index):
    input_num = len(gci(input_path, index))
    output_num = len(gci(out_path, index))
    if input_num == output_num:
        print("Success in dir\"%s\",num = %d" % (out_path, output_num))
    else:
        print("Worry in dir\"%s\",input = %d,output = %d" % (out_path, input_num, output_num))
    return 0


def list_dir(file_path, index_type):
    index_files = gci(file_path, index_type)
    index_dir = {}
    for file in index_files:
        father_path = os.path.dirname(file)
        if father_path in index_dir:
            continue
        flow_cell, seq_kit = get_notes(file)
        index_dir[father_path] = [flow_cell, seq_kit]
    return index_dir


def gci(file_path, index_type):
    files_list = []
    files = os.listdir(file_path)
    for sub_file in files:
        sub_path = os.path.join(file_path, sub_file)
        if os.path.isdir(sub_path):
            add_list = gci(sub_path, index_type)
            files_list.extend(add_list)
        else:
            if index_type in sub_path:
                files_list.append(sub_path)
    return files_list


def main():
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    if not os.path.exists(input_path):
        print('Error: fast5 file path is\'t existing! ')
        return
    print("get data from \"%s\"" % input_path)
    print()

    fast5_dirs = list_dir(input_path, ".fast5")
    for fast5_dir in fast5_dirs:
        out_index = fast5_dir.replace(input_path, "")
        out_path = os.path.join(output_path, out_index)
        flow_cell = fast5_dirs[fast5_dir][0]
        seq_kit = fast5_dirs[fast5_dir][1]
        crate_script(fast5_dir, flow_cell, seq_kit, out_path)


if __name__ == '__main__':
    main()
