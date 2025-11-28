import time
import re
import uiautomation as auto


def register_keyboard_listener(keyboard_listener_func: callable, with_pynput=True):
    try:
        if with_pynput:
            from pynput import keyboard
            listener = keyboard.Listener(on_press=keyboard_listener_func)
            listener.start()
        else:
            import keyboard
            keyboard.on_press(keyboard_listener_func)
            # keyboard.hook(on_key_event, suppress=False)  # 添加 suppress 参数
    except ImportError as e:
        print('not find module: {}'.format(e))


def find_window(window_name: str) -> auto.WindowControl | None:
    """
    通过名称查找窗口，支持正则表达式匹配
    如果window_name是有效的正则表达式，则使用正则匹配；否则使用普通字符串匹配
    :param window_name: 窗口名称或正则表达式
    :return: 找到的窗口控件或None
    """
    # 尝试将window_name作为正则表达式编译
    pattern = None
    try:
        pattern = re.compile(window_name)
    except re.error:
        # 如果不是有效正则表达式，则pattern保持为None
        pass
    for app_control in auto.GetRootControl().GetChildren():
        if not isinstance(app_control, auto.WindowControl):
            continue
        if pattern and pattern.search(app_control.Name):
            # 使用正则表达式匹配
            print('find window success: {} (matched by regex: {})'.format(app_control.Name, window_name))
            return app_control
        elif window_name in app_control.Name:
            # 使用普通字符串匹配
            print('find window success: {} (matched by name: {})'.format(app_control.Name, window_name))
            return app_control
    return None


def send_key_to_window_with_keyboard_event(
    window_control: auto.WindowControl, key_code: int, restore_window_control: auto.Control = None
):
    """
    通过键盘事件发送按键给窗口
    :param window_control: 窗口控件
    :param key_code: 按键码
    :param restore_window_control: 恢复窗口控件
    :return: None
    """
    window_control.SetFocus()
    auto.SendKey(key_code, waitTime=0.1)
    if not restore_window_control:
        return
    # 需要回到原窗口
    if hasattr(restore_window_control, 'SetActive'):
        restore_window_control.SetActive()
    else:
        restore_window_control.SetFocus()


def send_key_to_window_with_message(
    window_control: auto.WindowControl, key_code: int, restore_window_control: auto.Control = None
):
    """
    通过消息发送按键给窗口
    :param window_control: 窗口控件
    :param key_code: 按键码
    :param restore_window_control: 恢复窗口控件
    :return: None
    """
    window_control.SetFocus()
    result1 = auto.SendMessage(window_control.NativeWindowHandle, 0x100, key_code, 0)  # WM_KEYDOWN
    result2 = auto.SendMessage(window_control.NativeWindowHandle, 0x101, key_code, 0)  # WM_KEYUP
    print(f"Sent key {key_code} - WM_KEYDOWN result: {result1}, WM_KEYUP result: {result2}")
    # 需要回到原窗口
    if restore_window_control:
        restore_window_control.SetFocus()


def video_control_keyboard_listener(
    video_window_name: str, restore_window_name: str = None,
    with_pynput=True, with_message_send_key=True,
):
    """
    通过键盘事件监听对视频窗口进行控制控制
    用于解决两个屏幕，一个屏幕使用手柄玩游戏，另外一个屏幕播放视频的同时可以通过键盘控制播放和快捷，避免频繁切屏
    游戏屏幕处于激活状态，播放视频的Chrome窗口可以不激活，窗口被遮挡也没有问题
    :param video_window_name: 视频窗口名称
    :param restore_window_name: 恢复窗口名称，如果不设置，则默认回复到当前窗口
    :param with_pynput: 是否使用pynput作为键盘钩子
    :param with_message_send_key: 使用send_message来发送按键
    """
    video_window_control = find_window(video_window_name)
    restore_window_control = find_window(restore_window_name) if restore_window_name else auto.GetForegroundControl()
    if not video_window_control:
        print('not find video window.')
        return

    # 记录手动发送按键时间，需要进行去重
    manual_send_keys = []
    # 为了避免按键循环触发，key，value的按键最好不一致
    video_key_map = {
        'space': auto.Keys.VK_SPACE,
        'left': auto.Keys.VK_NUMPAD4,
        'right': auto.Keys.VK_NUMPAD6,
        'up': auto.Keys.VK_MEDIA_PREV_TRACK,    # 切换上一P
        'down': auto.Keys.VK_MEDIA_NEXT_TRACK,  # 切换下一P
    }

    def keyboard_event_listener(event):
        print('input event event: {}'.format(event))
        event_name = event.name if hasattr(event, 'name') else str(event)
        # 只处理关心的按键
        if event_name not in video_key_map.keys():
            return
        # 如果不是发送消息的方式，需要过滤掉手动触发的按键事件
        if not with_message_send_key and video_key_map.get(event_name) in manual_send_keys:
            manual_send_keys.remove(video_key_map.get(event_name))
            return

        # 从映射表获取对应按键
        send_key = video_key_map.get(event_name)
        print(f'attach key event: {event}, send key: {send_key}')
        # 限制manual_send_keys大小，避免内存泄漏
        if len(manual_send_keys) > 10:  # 只保留最近10次记录
            manual_send_keys.pop(0)
        # 更新最后发送按键记录
        manual_send_keys.append(send_key)
        if with_message_send_key:
            send_key_to_window_with_message(video_window_control, send_key, restore_window_control)
        else:
            send_key_to_window_with_keyboard_event(video_window_control, send_key, restore_window_control)

    register_keyboard_listener(keyboard_event_listener, with_pynput)


def print_current_cursor_position():
    """
    打印当前鼠标位置
    :return:
    """
    import ctypes.wintypes
    point = ctypes.wintypes.POINT(0, 0)
    ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
    print(f"当前鼠标位置：X={point.x}, Y={point.y}")


def register_keyboard_video_control_when_play_game():
    """
    用于一边玩游戏的同时，一边可以用键盘控制攻略视频播放
    注意要用管理员权限启动该脚本，否则无法捕获游戏时的键盘输入
    """
    video_control_keyboard_listener('Google Chrome', '原神')


def main_loop():
    # 主循环
    while True:
        # print_current_cursor_position()
        time.sleep(1)


if __name__ == '__main__':
    register_keyboard_video_control_when_play_game()
    # video_control_keyboard_listener('Google Chrome')
    main_loop()
