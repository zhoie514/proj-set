import jieba
from instance import config

from searchclient.init_server_db import cut
res= cut([["","我们以及url老师"]])
print(res)


with open(config.DEL_WORDS, 'r', encoding="utf8") as f:
    del_words = f.readlines()
    for item in del_words:
        jieba.del_word(item.strip())
res = jieba.cut_for_search("我们以及url老师")
print(list(res))