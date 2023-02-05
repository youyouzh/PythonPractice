"""
支付宝粉丝群消息爬取
TODO ： 时间信息关联，消息去重，滚动爬取优化，稳定性异常处理，更多case兼容，多账号批量操作
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

    # 检查和进入消息中心页面
    def check_switch_message_center(self):
        current = self.d.app_current()
        alipay_package = 'com.eg.android.AlipayGphone'
        message_activity = 'com.eg.android.AlipayGphone.AlipayLogin'
        chat_room_activity = 'com.alipay.mobile.chatapp.ui.GroupChatMsgActivity_'

        # 检查打开阿里云APP
        if current['package'] != alipay_package:
            log('the package is not active, open it.')
            self.d.app_start(alipay_package)
            self.d.app_wait(alipay_package)

        # 从聊天室返回到消息中心
        if current['activity'] == chat_room_activity:
            log('current chat room. back to message center.')
            self.d.xpath('//*[@resource-id="com.alipay.mobile.antui:id/back_button"]').click()
            self.d.wait_activity(message_activity, 10)
            return

        # 检查和打开消息中心的activity，这个activity是阿里首页，不一定是消息中心
        if current['activity'] != message_activity:
            log('the package is not active, open it. activity: {}'.format(message_activity))
            self.d.app_start(alipay_package, message_activity)
            self.d.wait_activity(message_activity, 10)

        # 点击底部【消息】菜单按钮，进入消息中心
        bottom_message_node = self.d.xpath('//*[@text="消息"]') \
            .xpath('//*[@resource-id="com.alipay.mobile.socialwidget:id/social_tab_text"]')
        if bottom_message_node:
            log('click bottom message button')
            bottom_message_node.click(timeout=10)
        return

    # 消息群组列表
    def crawl_groups(self):
        main_layout = self.d(resourceId='com.alipay.mobile.socialwidget:id/recent_list')

        # 使用resourceId定位，用className定位不准确，每一个消息分组卡片
        group_layouts = main_layout.child(resourceId='com.alipay.mobile.socialwidget:id/first_line')
        groups = []
        for group_layout in group_layouts:
            # 消息分组卡片中的组名
            group_name_node = group_layout.child(resourceId='com.alipay.mobile.socialwidget:id/item_name',
                                                 className='android.widget.TextView')
            # 消息分组卡片中的最近更新时间
            recent_time_node = group_layout.child(resourceId='com.alipay.mobile.socialwidget:id/item_date',
                                                  className='android.widget.TextView')
            if group_name_node and recent_time_node:
                group = {
                    'name': group_name_node.get_text(),
                    'timeStr': recent_time_node.get_text(),  # 可能是时间，刚刚，直播中，昨天，日期等
                    'node': group_name_node
                }
                log('group: {}, time: {}'.format(group['name'], group['timeStr']))
                groups.append(group)
        return groups

    # '//*[@resource-id="com.alipay.mobile.socialwidget:id/recent_list"]/android.widget.RelativeLayout'
    def crawler_by_xpath(self):
        cj_group_nodes = self.d.xpath('//*[contains(@text, "创金新粉群")]').all()
        log('group count: {}'.format(len(cj_group_nodes)))

        # 群组名称和最近消息时间的相对xpath
        relative_cj_group_xpath = '/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.TextView'
        relative_cj_time_xpath = '/android.widget.FrameLayout[1]/android.widget.TextView'

        # 基准列表项xpath
        base_list_xpath = '//*[@resource-id="com.alipay.mobile.socialwidget:id/recent_list"]'
        base_list_split_token = 'ListView'
        for cj_group_node in cj_group_nodes:
            # 完整绝对xpath，用来截取遍历
            cj_group_xpath = cj_group_node.get_xpath()

            # 截断到基准列表到尾部的中间部分
            start_index = cj_group_xpath.index(base_list_split_token) + len(base_list_split_token)
            end_index = len(relative_cj_group_xpath)
            mid_xpath = cj_group_xpath[start_index:-end_index]

            # 查看最近更新时间
            time_xpath = base_list_xpath + mid_xpath + relative_cj_time_xpath
            cj_time_node = self.d.xpath(time_xpath).get()

            log('group: {}, time: {}'.format(cj_group_node.text, cj_time_node.text))

            cj_group_node.click()
            time.sleep(3)

    # 群内消息爬取子任务
    def crawl_group_sub_messages(self):
        chat_nodes = self.d(resourceId='com.alipay.mobile.chatapp:id/chat_msg_layout',
                            className='android.widget.RelativeLayout')
        log('chat nodes size: {}'.format(len(chat_nodes)))

        chat_messages = []
        for chat_node in chat_nodes:
            # 头像节点
            avatar_node = chat_node.child(resourceId='com.alipay.mobile.chatapp:id/chat_msg_avatar_layout')
            name_node = chat_node.child(resourceId='com.alipay.mobile.chatapp:id/chat_msg_name')
            # 昵称节点
            name_text_node = chat_node.child(resourceId='com.alipay.mobile.chatapp:id/chat_msg_name_text')

            try:
                # 消息内容节点，需要细分图片、小程序、文本等
                content_node = chat_node.child(resourceId='com.alipay.mobile.chatapp:id/chat_msg_bubble_biz')
                # 只处理文本内容节点
                content_text_node = chat_node.child(resourceId='com.alipay.mobile.chatapp:id/chat_msg_text')
            except UiObjectNotFoundError:
                log('not found UiObject.')
                continue
            chat_message = {
                'name': name_text_node.get_text(),
                'text': content_text_node.get_text() if content_node else '',
                'time': '',
                'key': ''
            }
            chat_messages.append(chat_message)

            # 用于消息过滤，比如群主和管理员发送的消息过滤掉
            if '--' not in chat_message['name']:
                print('user: {}, message: {}'.format(chat_message['name'], chat_message['text']))

        return chat_messages

    # 爬取消中心的群组列表
    def crawl_group_messages(self, group):
        # 只处理创金粉丝群列表
        if '创金' not in group['name']:
            log('The group is not target. name: {}'.format(group['name']))
            return []

        # 切换到指定群组的聊天室中
        self.check_switch_message_center()
        group['node'].click()
        message_room_activity = 'com.alipay.mobile.chatapp.ui.GroupChatMsgActivity_'
        self.d.wait_activity(message_room_activity, timeout=10)
        chat_messages = []

        # 滑动爬取群消息，需要更好的方式
        add_count = 5
        while add_count > 0:
            add_chat_messages = self.crawl_group_sub_messages()
            log('add message count: {}'.format(len(add_chat_messages)))
            chat_messages.extend(add_chat_messages)
            self.d.swipe_ext('down')
            time.sleep(1)
            add_count -= 1
        return chat_messages


# 支付宝消息爬取主任务调度
def crawl_main():
    # monitor = DeviceMonitor('127.0.0.1:21503')  # 虚拟机
    # monitor = DeviceMonitor('98895a394241474541')
    monitor = DeviceMonitor('10.203.223.87:5555')  # adb connect 10.203.223.87:5555
    monitor.check_switch_message_center()
    groups = monitor.crawl_groups()
    for group in groups:
        log('begin crawl group: {}'.format(group['name']))
        monitor.crawl_group_messages(group)


if __name__ == '__main__':
    crawl_main()
