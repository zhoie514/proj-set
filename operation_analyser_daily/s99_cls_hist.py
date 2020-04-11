# step 4
# 清除历史不需要的数据 有的csv比较大，10多兆


import os
import time
from datetime import datetime, timedelta

import CONF

ROOT_DIR = CONF.SOURCE_DIR


def clear_hist(date: str):
    date = int(date)
    for tag_date in range(date, 0, -1):
        rm_dir = f"{ROOT_DIR}/{tag_date}_zd_query_result"
        if os.path.isdir(rm_dir):
            files_struct = os.walk(rm_dir).__next__()  # -> ("f_dir",[],[f1,f2])
            for file in files_struct[2]:
                file_path = files_struct[0] + "/" + file
                os.remove(file_path)
            os.removedirs(rm_dir)
        else:
            break


if __name__ == '__main__':
    # 转换一下日期,为昨天
    r = time.strftime("%Y%m%d", time.localtime())
    # - 1的话会将日期为昨天的一起删掉
    date = (datetime.now() + timedelta(days=CONF.DATE_OFFSET) - timedelta(days=3)).strftime("%Y%m%d")
    print(date)
    exit(8)
    clear_hist(date)
