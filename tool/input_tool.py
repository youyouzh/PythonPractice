import time

import keyboard
import uiautomation as auto


SEND_KEY_MAP = {
    'space': auto.Keys.VK_SPACE,
    'left': auto.Keys.VK_LEFT,
    'right': auto.Keys.VK_RIGHT
}


def register_key_repeat_for_window(window_name: str, key_names: list):
    """
    注册全局按键事件监听，将接收到的按键重复到目标窗口
    用于解决两个屏幕，一个屏幕使用手柄玩游戏，另外一个屏幕播放视频的同时可以通过键盘控制播放和快捷，避免频繁切屏
    游戏屏幕处于激活状态，播放视频的Chrome窗口可以不激活，窗口被遮挡也没有问题
    :param window_name: 目标窗口名称
    :param key_names: 监听的按键名称列表
    :return:
    """
    target_window_control = None
    for app_control in auto.GetRootControl().GetChildren():
        # 匹配chrome窗口
        if window_name in app_control.Name :
            target_window_control = app_control
            print('find main target window success: {}'.format(target_window_control.Name))
    if not target_window_control:
        print('not find target window')
        return

    # 记录按键队列，移除掉手动触发的按键
    manual_keys = []

    def on_key_event(event):
        print('input event name: {}, type: {}'.format(event.name, event.event_type))
        if event.name in key_names:
            if event.name in manual_keys:
                manual_keys.pop()
                return
            print('attach key name: {}, type: {}'.format(event.name, event.event_type))
            # 获取当前指定的窗口
            manual_keys.append(event.name)
            target_window_control.SendKey(SEND_KEY_MAP.get(event.name))

    # 注册全局按键事件监听
    keyboard.on_press(on_key_event)


def chrome_video_control():
    window_name = 'Google Chrome'
    key_names = ['space', 'left', 'right']
    register_key_repeat_for_window(window_name, key_names)


def print_current_cursor_position():
    """
    打印当前鼠标位置
    :return:
    """
    import ctypes.wintypes
    point = ctypes.wintypes.POINT(0, 0)
    ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
    print(f"当前鼠标位置：X={point.x}, Y={point.y}")


def main_loop():
    # 主循环
    while True:
        # point = ctypes.wintypes.POINT(0, 0)
        # ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        # print(f"当前鼠标位置：X={point.x}, Y={point.y}")
        time.sleep(1)


if __name__ == '__main__':
    chrome_video_control()
    main_loop()
