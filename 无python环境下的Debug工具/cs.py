import ctypes
import tkinter as tk
import os,sys
import json
from datetime import datetime, date
import time
import threading
import win32gui
import win32con
import keyboard  # 用于全局键盘检测
import pynput  # 用于全局鼠标检测

def get_window_title(hwnd):
    # 先获取标题长度
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    # 创建缓冲区
    buffer = ctypes.create_unicode_buffer(length + 1)
    # 获取标题
    ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value

def has_taskbar_windows_no_minimized():
    """
    检查是否存在非最小化的任务栏窗口
    """
    has_windows = [False]  # 使用列表来在回调函数中修改值
    
    def enum_windows_callback(hwnd, _):
        if (win32gui.IsWindowVisible(hwnd) and 
            win32gui.GetWindowText(hwnd) and
            not win32gui.GetParent(hwnd)):
            
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            if (style & win32con.WS_OVERLAPPEDWINDOW) and not (style & win32con.WS_DISABLED):
                ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                if not (ex_style & win32con.WS_EX_TOOLWINDOW):
                    if not win32gui.IsIconic(hwnd):
                        has_windows[0] = True
                        print(f"窗口标题: {get_window_title(hwnd)}")
                        return False  # 找到符合条件的窗口就停止枚举
        return True
    
    win32gui.EnumWindows(enum_windows_callback, None)
    return has_windows[0]


# 使用示例（需替换为实际窗口句柄）
if __name__ == "__main__":
    has_taskbar_windows_no_minimized()
   
