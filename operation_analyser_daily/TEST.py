import codecs
import json
def test1():
    file = "csv/20200330_zd_query_result/online_50002_20200330.csv"
    l=[]
    with open(file, "r", ) as f:
        contents = f.readlines()
        print(len(contents))
        for content in contents:
            # if content.startswith(codecs.BOM_UTF8):
                # content = content.decode("utf8").encode("utf8")
                row_obj = json.loads(content)
                # print(123)
                if row_obj["_source"]["extra"]["source_code"] == "TPJF":
                    string = json.dumps(row_obj)
                    if row_obj["_source"]["extra"]["pbc_data"] =="":
                        continue
                    l.append(row_obj["_source"]["extra"]["pbc_data"] )
                    with open("text.txt", "a+", encoding="utf8") as f:
                        f.write(string)
                        f.write("\n")
    print(set(l))

def test2():
    from datetime import datetime,timedelta
    x = datetime.now()
    print(x.strftime("%Y%m%d"))
    y = x  - timedelta(days=1)
    print(y)
    ...


test2()