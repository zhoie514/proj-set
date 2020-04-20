# step 1:
#
# 解压至项目的CSV下面的同名目录中（需要新建）
import poplib
import zipfile
from datetime import timedelta, datetime

import CONF


def un_zip(src_file, dest_dir, password=None):
    ''' 解压单个文件到目标文件夹。'''
    if password:
        password = password.encode()
    zf = zipfile.ZipFile(src_file)
    try:
        zf.extractall(path=dest_dir, pwd=password)
    except RuntimeError as e:
        print(e)
    zf.close()


if __name__ == '__main__':
    # 转换一下日期,为昨天
    date = (datetime.now() + timedelta(days=CONF.DATE_OFFSET)).strftime("%Y%m%d")
    ZIP_DIR = f"{CONF.ZIP_DIR}/{date}_zd_query_result.zip"
    ZIP_DIR_NORMAL = f"{CONF.ZIP_DIR}/{date}.zip"
    TARGET_DIR = f"{CONF.SOURCE_DIR}/{date}_zd_query_result/"
    TARGET_DIR_NORMAL = f"{CONF.SOURCE_DIR}/{date}/"
    un_zip(ZIP_DIR, TARGET_DIR)
    un_zip(ZIP_DIR_NORMAL, TARGET_DIR_NORMAL)
