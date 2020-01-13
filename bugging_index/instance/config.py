# jieba 分词时 排除项   一项一行
DEL_WORDS = r"/server_2/searchclient/static/jiebawords/del_word.txt"

# 结巴分词 指定词汇
ADD_WORDS = r"/server_2/searchclient/static/jiebawords/add_word.txt"

# 是否开启重建索引
REBUILD =True

# 是否允许备份
BACKUP =False
BACKUP_DIR = r"/server_2/searchclient/static/csv"

# 是否允许从CSV导入
IMPORT_CSV =False

# 允许还原db
INIT =False

# 允许删除记录
DEL_RECORD =False
