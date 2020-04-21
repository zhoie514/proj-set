""""""


#  根据日期及cmd_id 生成包含文件名的有序元组
def gen_filapaths(date: str, cmd_ids: tuple) -> tuple:
    filepaths = []
    for cmd_id in cmd_ids:
        filepaths.append(f"./csv/source_data/{date}_zd_query_result/online_{cmd_id}_{date}.csv")
    return tuple(filepaths)


# 根据日期及产品生成结果路径
def gen_res_file_path(date: str, source_codes: tuple) -> tuple:
    filepaths = []
    for source_code in source_codes:
        filepaths.append(f"./csv/results_output/{date}_qry_res/{source_code}-{date}-qry-res.csv")
    return tuple(filepaths)
