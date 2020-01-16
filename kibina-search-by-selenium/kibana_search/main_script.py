from schedule_utils import *


# 运行方式1
if __name__ == '__main__':
    # 时间戳记录
    t = time.time()
    # 打开一个浏览器,如果自定义了配置json文件就使用,没有的话就使用默认的,自定义的可以覆盖默认的
    # 可以开启无头模式
    browser = Browser('custom_config.json', headless=True)
    browser.auto_run(wait=0.5, delay=1, limit=20)
    print(time.time() - t)
    exit()

# 运行方式2
if __name__ == '__main__1':
    # 时间戳记录
    t = time.time()
    browser = Browser('custom_config.json', headless=False)
    try:
        browser.get_page()
        key_serial_nos = input2list(browser.input_csv)
        count = 0
        for serial_no in key_serial_nos:
            browser.send_content(content=serial_no, delay=1, limit=20)
            if browser.have_head():
                browser.get_thead_infos()
            count += 1
            browser.click_searck_key(wait=0.5)
            browser.get_tbody_infos()
    except Exception:
        print(123)
    finally:
        # 可能获取了部分后失败,故将已经获取的数据进行保存
        browser.save_csv()
        browser.quit()
    print(time.time() - t)
