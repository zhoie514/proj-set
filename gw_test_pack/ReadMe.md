# 流程测试脚本


#### 使用流程/步骤:

1. 复制TPJF文件夹并重命名为相应的产品SOURCECODE
1. 修改KEYS里面的公钥钥文件,尽量搜集全一点
1. mytools.py 内 if main里面有一个可以简单校验 密钥是否正确的流程
    ```text
    默认是合作方的视角,如果要校验其他的key, 参考密钥改变参数
    ```
1. CONF_NET.py 里面修改相关的网络参数
    ```text
    ORDERED_REQ 这个是连续跑N个请求的,但要建立在上一个请求成功的基础上 见:@1
    ```
1. CONF_ARG.py 里面修改各个接口的入参
    ```text
    能关联上的尽量一次性关联上
    ```
1. CONST_ARGS.py 里面修改一些"特别"固定的参数
1. sub_main.py 里面大部分内容不需要修改
    ```text
   @1: 需要修改的内容为 注释中 #修改# 附近, 需要判断连续调用接口时上一个接口的返回值,
   比如 50001如果返回01,或者03,就没有必要去访问50002了,这个条件就可以中断此次顺序调用
    ```
#### .log日志说明

##### 没啥用的

1. 所属产品目录下的 log_req_info.log : 打印入参及返回值
    >  sub_main.py 里面的 req_logger 控制
1. 所属产品目录下的 log_schedu.log : 打印入参及返回值 及 可能的一些详细的信息,如密文等
    > sub_main.py 里面的 sub_logging 控制


##### 有啥用的

1. log_CONST_PARAMS.log
    > sub_main.py 里面的const_logger 控制
   ```text
   里面可以存放一些该次请求使用的流水号,人物四要素等信息,
   #修改2# 可以自己筛选打印些啥出来,以及做一些判断
   ```
   
   
   
   其他
```cmd command
# test case:
main.py               # 会显示一些提示信息
main.py tpjf 1 50002  # 单独调 50002对应的接口,并通过网关,不通过网关可以把1改为0,不过就没必要用这个工具
main.py tpjf 1        # 顺序调用CONF_NET.py中ORDERED_REQ 列表中的相应接口,并通过网关
```
