import pandas as pd
import numpy as np
import copy


class DataPadding:
    def __init__(self, raw_data, max_len):
        self.raw_lists = raw_data
        self.max_len = max_len

        # self.raw_data.apply(lambda se: pad_from_numpy(se), axis=1)

    # def pad_tail_zero(self, padding_size=None):
    #     if padding_size is None:
    #         padding_size = self.max_len
    #     padding_data = copy.deepcopy(self.raw_data.iloc[:, :padding_size])
    #     padding_data = padding_data.replace(np.nan, 0)
    #     return padding_data
    #
    # def cut_nan(self):
    #     raw_lists = []
    #     tail_zero_data = self.pad_tail_zero()
    #     for indexs in tail_zero_data.index:
    #         row_series = tail_zero_data.loc[indexs]
    #         row_list = list(row_series)
    #         while 0 in row_list:
    #             row_list.remove(0)
    #         raw_lists.append(row_list)
    #     return raw_lists

    def pad_with_mean_stdv(self, padding_size=None):
        if padding_size is None:
            padding_size = self.max_len

        padding_lists = []

        for row_list in self.raw_lists:
            row_mean = np.mean(row_list)
            row_std = np.std(row_list)
            padding_list = np.random.normal(loc=row_mean, scale=row_std, size=padding_size)
            padding_lists.append(list(padding_list))

        padding_data = np.array(padding_lists)

        return padding_data


    # def pad_side_zero(self, padding_size=None, mode='constant'):
    #     if padding_size is None:
    #         padding_size = self.max_len
    #
    #     padding_lists = []
    #     raw_lists = self.cut_nan()
    #
    #     for row_list in raw_lists:
    #         if len(row_list) >= padding_size:
    #             start = int(np.floor((len(row_list)-padding_size)/2))
    #             padding_list = copy.deepcopy(row_list[start:start+padding_size])
    #         else:
    #             start = int(np.floor((padding_size - len(row_list)) / 2))
    #             if (padding_size - len(row_list)) % 2 == 0:
    #                 padding_list = np.pad(row_list, start, mode)
    #             else:
    #                 padding_list = np.pad(row_list, (start,start+1), mode)
    #
    #         padding_lists.append(list(padding_list))
    #     padding_data = pd.DataFrame(padding_lists)
    #
    #     return padding_data



