"""流程相关"""
import csv
import time

from selenium import webdriver

from parse_utils import *


class JsonDecodeError(Exception):
    pass


class ElementNotFoundError(Exception):
    pass


class Browser():
    """创建一个浏览器,可选是否显示界面"""

    def __init__(self, custom_config: str, headless: bool = False,
                 default_config: str = 'default_config.json'):
        """
        :param custom_config: custom_config为一个json路径
        :param headless:
        :param default_config:default_config为一个json路径
        """
        self.g = {"res": []}  # 存储一些 临时加入的对象的
        self.default_config = self.config = json2dict(default_config)
        self.options = webdriver.ChromeOptions()
        if self.default_config.get("error", None):
            raise JsonDecodeError("default_config.json 文件不规范")

        if headless:
            self.options.add_argument('--headless')
        self.browser = webdriver.Chrome(options=self.options)
        if custom_config:
            custom_config_dic = json2dict(custom_config)
            if custom_config_dic.get("error", None):
                raise JsonDecodeError("custom_config.json 文件不规范")
            if custom_config_dic:
                self.default_config.update(custom_config_dic)
        for k, v in self.default_config.items():
            setattr(self, k, v)

    # 打开页面
    def get_page(self) -> None:
        """打开一个页面"""
        self.browser.get(self.url)
        return

    # 向搜索框中输入内容
    def send_content(self, content: str, delay: int = 3, limit: int = 10) -> None:
        """向指定xpath node中写入content
        content 为转换为 content + extend_search
        delay: 为未找到节点的重试时间 默认3秒后重新去获取页面中加载的节点
        limit: 为重试次数限制 默认重试10次后报错"""
        count = 1
        while True:
            try:
                node = self.browser.find_element_by_xpath(self.search_input)
                break
            except Exception:
                print(f"未找到输入框,{delay}秒后重试第{count}次...")
                count += 1
                time.sleep(delay)
                if count > limit:
                    raise ElementNotFoundError(f"重试{count}次后,依然未根据 xpath 找到搜索框, 请确认xpath是否正确,网络是否有故障")
        node.clear()
        self.g["search_content"] = content + self.extend_search
        node.send_keys(self.g.get("search_content"))
        return

    # 点击搜索按钮
    def click_searck_key(self, wait: float = 1.0) -> None:
        """通过xpath找到搜索按钮并点击
        :wait 点击搜索后的 延迟等待时间"""
        try:
            self.browser.find_element_by_xpath(self.search_button).click()
        except Exception:
            raise ElementNotFoundError('未根据 xpath 找到搜索按钮')
        time.sleep(wait)
        return

    # 顺序点击一些其他的按钮
    def common_click(self, delay: float = 0.2) -> None:
        """ 循环点击设置的控件,间隔 0.2 秒 """
        i = 0
        for item in self.common_button:
            i += 1
            try:
                self.browser.find_element_by_xpath(item)
                time.sleep(delay)
            except Exception:
                # raise ElementNotFoundError(f"第 {i} 个 xpath 未找到元素")
                print(f"第 {i} 个 'common_button的' xpath 未找到元素")

    # 获得页面中的表格中的数据 与 scratch_field 中的集合取交集
    def get_thead_infos(self) -> List[List[str]]:
        res = self.g.get('res')
        try:
            # 1. 首先获取表头
            head = self.browser.find_element_by_xpath(self.t_head)
            tmp = [item.strip() for item in head.text.split()]
            # 2. 对网页中显示的内容与我们想要的内容进行对比,其实当然可以统一,但要考虑到 我想看n条信息,但我只想保留 k(k<=n)条信息的情况
            # 2.1 index is [int,int2,...] 这个index 后面也会用到
            index = parse_index(tmp, self.scratch_field)
            self.g['index'] = index
            # 仅取出config中 要求的字段,如不存在会报错
            clean_tmp = [t for t in tmp for i in index if tmp.index(t) == i]
            res.append(clean_tmp)
        except Exception:
            print(f'页面中没有表格,可能搜索的结果为空:{self.g.get("search_content")}')
        return res

    def get_tbody_infos(self) -> List[List[str]]:
        """"""
        res = self.g.get('res')
        try:
            # 3. 取出tbody中的记录
            # 3.1 找出tbody中的tr节点
            tr_list = self.browser.find_elements_by_xpath(self.t_body)
            if len(tr_list) == 0:
                print(f'页面中没有表格,可能搜索的结果为空:{self.g.get("search_content")}')
                return res
            # 3.2 再从 tr节点的遍历 所有的td节点并获取内容
            for tr in tr_list:
                tmp = [item.strip() for item in tr.text.split("\n")]
                clean_tmp = [t for t in tmp for i in self.g.get("index", []) if tmp.index(t) == i]
                res.append(clean_tmp)
        except Exception:
            print(f'其他错误,对应搜索内容:{self.g.get("search_content")}')
        return res

    # 保存所有数据为 csv
    def save_csv(self) -> None:
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        with open(f'csv/output-{timestamp}.csv', newline="", encoding="utf-8", mode="a+") as f:
            writer = csv.writer(f)
            writer.writerows(self.g.get("res", [["无内容"]]))
            f.flush()
            return

    # 自动根据 input csv来获取所有数据 一个内置的方法,当然也可以在外部自己调用并组合
    def auto_run(self, wait: float = 0.5, delay: int = 3, limit: int = 10) -> bool:
        """
        自动获取数据的脚本
        :param wait: 点击搜索按钮后的等待时间
        :param delay: 加载页面时,获取输入框的延迟
        :param limit: 获取 输入框失败后的重试次数
        :return:
        """
        try:
            self.get_page()
            key_serial_nos = input2list(self.input_csv)
            count = 0
            for serial_no in key_serial_nos:
                self.send_content(content=serial_no, delay=delay, limit=limit)
                if not self.have_head():
                    self.get_thead_infos()
                count += 1
                self.click_searck_key(wait=wait)
                self.get_tbody_infos()
            return True
        except Exception:
            return False
        finally:
            # 可能获取了部分后失败,故将已经获取的数据进行保存
            self.save_csv()
            self.quit()
            print("Done...")

    # 退出浏览器
    def quit(self):
        self.browser.quit()

    # 判断是否有内容
    def have_head(self) -> bool:
        """
        返回是否拿到表头了
        :return: True :有   False:没有
        """
        return len(self.g.get('res')) != 0
