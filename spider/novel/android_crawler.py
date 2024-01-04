"""
起点app小说爬取
"""
import time

import uiautomator2
from uiautomator2 import UiObjectNotFoundError


# 临时log函数
def log(message):
    print(message)


class DeviceMonitor:

    def __init__(self, path=None):
        # 连接移动设备
        self.d = uiautomator2.connect(path)
        if self.d is None:
            log('connect fail. path: {}'.format(path))
        log('connect success: {}'.format(self.d.device_info))

    def open_qidian_app(self):
        current = self.d.app_current()
        qidian_package = 'com.qidian.QDReader'

        # 检查打开阿里云APP
        if current['package'] != qidian_package:
            log('the package is not active, open it.')
            self.d.app_start(qidian_package)
            self.d.app_wait(qidian_package)

    def get_page_text(self):
        log('begin get page text')
        page_count = 1
        for page_index in range(page_count):
            self.d.screenshot().save(r'result/page-' + str(page_index) + '.png')
            self.d.click(0.964, 0.703)
            time.sleep(0.5)


# 支付宝消息爬取主任务调度
def crawl_main():
    # monitor = DeviceMonitor('127.0.0.1:21503')  # 虚拟机
    monitor = DeviceMonitor('98895a394241474541')
    # monitor = DeviceMonitor('10.203.223.87:5555')  # adb connect 10.203.223.87:5555
    monitor.open_qidian_app()
    monitor.get_page_text()


if __name__ == '__main__':
    crawl_main()
