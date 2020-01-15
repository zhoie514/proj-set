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
    def send_content(self, content: str) -> None:
        """向指定xpath node中写入content
        content 为转换为 content + extend_search"""
        try:
            node = self.browser.find_element_by_xpath(self.search_input)
        except Exception:
            raise ElementNotFoundError("未根据 xpath 找到搜索框")
        node.clear()
        node.send_keys(content + self.extend_search)
        return

    # 点击搜索按钮
    def click_searck_key(self) -> None:
        """通过xpath找到搜索按钮并点击"""
        try:
            self.browser.find_element_by_xpath(self.search_button).click()
        except Exception:
            raise ElementNotFoundError('未根据 xpath 找到搜索按钮')
        return

    # 顺序点击一些其他的按钮
    def common_click(self) -> None:
        """ 循环点击设置的控件,间隔 0.2 秒 """
        i = 0
        for item in self.common_button:
            i += 1
            try:
                self.browser.find_element_by_xpath(item)
                time.sleep(self.interval_time)
            except Exception:
                # raise ElementNotFoundError(f"第 {i} 个 xpath 未找到元素")
                print(f"第 {i} 个 'common_button的' xpath 未找到元素")

    # 获得页面中的表格中的数据 与 scratch_field 中的集合取交集
    def get_table_infos(self) -> List[List[str]]:
        res = []
        try:
            head = self.browser.find_element_by_xpath(self.t_head)
        except Exception:
            raise ElementNotFoundError('未找主内容的 表头')
        tmp = [item.strip() for item in head.text.split()]
        # 对网页中显示的内容与我们想要的内容进行对比,其实当然可以统一,但要考虑到 我想看n条信息,但我只想保留 k(k<=n)条信息的情况
        index = parse_index(tmp, self.scratch_field)
        res.append(tmp)

        return res

    # 保存所有数据为 csv
    @classmethod
    def save_all_infos(cls, csv_content: List[List[str]]) -> None:
        with open('csv/output.csv', newline="", encoding="utf-8", mode="w+") as f:
            writer = csv.writer(f)
            writer.writerows(csv_content)
            f.flush()
            return

    # 退出浏览器
    def quit(self):
        self.browser.quit()
