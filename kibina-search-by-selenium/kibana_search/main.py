import time

from selenium import webdriver

browser = webdriver.Chrome()


def send_search_key(item_xpath, content):
    """通过xpath找到输入框并向其中写入content"""
    node = browser.find_element_by_xpath(item_xpath)
    node.clear()
    node.send_keys(content)


def click_searck_key(click_xpath):
    """通过xpath找到搜索按钮并点击"""
    node = browser.find_element_by_xpath(click_xpath)
    node.click()
    time.sleep(5)


if __name__ == '__main__':
    # # 搜索的url
    # url = "http://log.xwfintech.com:20008/app/kibana#/discover?_g=(refreshInterval:(display:Off,pause:!f,value:0),time:(from:'2019-12-19T16:00:00.000Z',mode:absolute,to:'2019-12-20T02:59:59.999Z'))&_a=(columns:!(message,beat.hostname,cmd_id,doc.trx,doc.bussiness_serial_no),filters:!(),index:'524e0370-c17c-11e8-85be-954a266357fc',interval:auto,query:(language:lucene,query:'%22SRCBCR201912200000000000000222%22%20AND%20%2250001%22'),sort:!('@timestamp',desc))"
    # # 搜索框的xpath
    # item_xpath = '//*[@id="kibana-body"]/div[1]/div/div/div[4]/discover-app/kbn-top-nav/div/div[3]/div/query-bar/form/kbn-typeahead/div/ng-transclude/div/div/input'
    # # 点击搜索按钮的xpath
    # click_xpath = '//*[@id="kibana-body"]/div[1]/div/div/div[4]/discover-app/kbn-top-nav/div/div[3]/div/query-bar/form/kbn-typeahead/div/ng-transclude/div/button'
    # # 加载首页
    # browser.get(url=url)
    # time.sleep(15)
    #
    # send_search_key(item_xpath, "50003")
    # click_searck_key(click_xpath)
    import json
    json.loads()
