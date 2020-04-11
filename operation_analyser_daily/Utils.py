""""""


#  根据日期及cmd_id 生成包含文件名的有序元组
def gen_filapaths(date: str, cmd_ids: tuple) -> tuple:
    filepaths = []
    for cmd_id in cmd_ids:
        filepaths.append(f"./csv/source_data/{date}_zd_query_result/online_{cmd_id}_{date}.csv")
    return tuple(filepaths)
