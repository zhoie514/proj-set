from schedule_utils import *

if __name__ == '__main__':
    t = time.time()
    browser = Browser('custom_config.json')
    browser.get_page()
    time.sleep(10)
    browser.send_content("")
    browser.click_searck_key()
    browser.common_click()
    time.sleep(5)
    s = browser.get_table_infos()
    browser.save_all_infos(s)
    browser.quit()
    print(time.time() - t)
