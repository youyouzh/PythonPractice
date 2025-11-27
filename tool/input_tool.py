import time

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


def video_control_keyboard_listener(source_window_name: str, video_window_name: str):
    """
    通过键盘事件监听对视频窗口进行控制控制
    用于解决两个屏幕，一个屏幕使用手柄玩游戏，另外一个屏幕播放视频的同时可以通过键盘控制播放和快捷，避免频繁切屏
    游戏屏幕处于激活状态，播放视频的Chrome窗口可以不激活，窗口被遮挡也没有问题
    :param source_window_name: 原始窗口名称
    :param video_window_name: 视频播放窗口名称
    :return:
    """
    source_window_control = None
    video_window_control = None
    for app_control in auto.GetRootControl().GetChildren():
        if source_window_name == app_control.Name:
            source_window_control = app_control
            print('find source window success: {}'.format(app_control.Name))
        if video_window_name in app_control.Name:
            video_window_control = app_control
            print('find main target window success: {}'.format(video_window_control.Name))
    if not source_window_control or not video_window_control :
        print('not find target window')
        return

    # 记录手动发送按键时间，需要进行去重
    manual_send_keys = []
    # 为了避免按键循环触发，key，value的按键最好不一致
    video_key_map = {
        'space': [auto.Keys.VK_MEDIA_PLAY_PAUSE, auto.Keys.VK_MEDIA_STOP],
        'left': auto.Keys.VK_NUMPAD4,
        'right': auto.Keys.VK_NUMPAD6,
    }

    def keyboard_event_listener(event):
        print('input event event: {}'.format(event))
        event_name = event.name if hasattr(event, 'name') else str(event)

        # 修正逻辑：只处理关心的按键
        if event_name not in video_key_map.keys():
            return  # 不关心的按键直接返回

        # 对于空格键，要判断上一次发送的是播放还是暂停，这次相反
        if event_name == 'space':
            last_send_key = manual_send_keys[-1] if manual_send_keys else None
            if last_send_key == auto.Keys.VK_MEDIA_PLAY_PAUSE:
                send_key = auto.Keys.VK_MEDIA_STOP
            else:
                send_key = auto.Keys.VK_MEDIA_PLAY_PAUSE
        else:
            # 从映射表获取对应按键
            send_key = video_key_map.get(event_name)
        print(f'attach key event: {event}, send key: {send_key}')
        # 更新最后发送按键记录
        manual_send_keys.append(send_key)
        video_window_control.SendKey(send_key, waitTime=0.1)
        # 需要回到原窗口
        time.sleep(0.1)
        source_window_control.SetActive()

    register_keyboard_listener(keyboard_event_listener)


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
    video_control_keyboard_listener('原神', 'Google Chrome')
    main_loop()
