import io, copy
import keyword
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pygame
import os, sys
import json
from datetime import datetime, date
import time
import threading
import win32gui
import win32con
import keyboard
import pynput

# ---------------------- 高亮相关变量定义 ----------------------
字体='微软雅黑'
# 关键字分类
关键字 = []
函数关键字 = []
error = []
特殊关键字 = []
代码关键字 = []
# 分隔符定义（用于判断单词边界）
分隔符 = '	 !@#$%^,&*()"|.+-/?~`=[]{}:;<>' + "'"
分隔符 = [i for i in 分隔符]

# 从内置语言文件加载关键字
def load_keywords():
    try:
        with open('内置语言.txt', 'r', encoding='utf-8') as f:
            yyb = f.read().split('\n')
            for i in yyb:
                if not i.strip():  # 跳过空行
                    continue
                if i[0] == '.':
                    函数关键字.append(i[1:])
                elif i[0] == '@':
                    error.append(i[1:])
                elif len(i) > 0 and i[-1] == '~':
                    特殊关键字.append(i[:-1])
                else:
                    关键字.append(i)
        # 添加Python内置关键字作为补充
        关键字.extend(keyword.kwlist)
    except Exception as e:
        print(f"加载语言文件失败: {e}")
        # 当语言文件不存在时，使用默认Python关键字
        关键字.extend(keyword.kwlist)

# 初始化加载关键字
load_keywords()

def p(文本, x, c="#000000", **a):  # 默认颜色为黑色
    # 创建一个唯一的标签名
    tag_name = f"color_{len(文本.tag_names())}"
    # 配置颜色标签
    文本.tag_configure(tag_name, foreground=c,** a)
    # 插入文本并应用颜色标签
    文本.insert('end', x + "\n", tag_name)
    文本.see(tk.END)

# ---------------------- 高亮逻辑实现 ----------------------
def highlight_code():
    """代码高亮主函数"""
    # 清除已有的高亮标签
    for tag in text_area.tag_names():
        if tag.startswith(('comment', 'string', 'keyword', 'function', 'error', 'special', 'number')):
            text_area.tag_remove(tag, "1.0", tk.END)
    
    # 获取所有文本内容
    content = text_area.get("1.0", tk.END)
    lines = content.split('\n')
    line_count = len(lines)
    
    # 逐行处理
    for line_num in range(line_count):
        line = lines[line_num]
        line_start = f"{line_num + 1}.0"
        line_end = f"{line_num + 1}.end"
        
        # 检查是否有注释
        comment_pos = line.find('#')
        if comment_pos != -1:
            # 标记注释
            text_area.tag_add("comment", f"{line_num + 1}.{comment_pos}", line_end)
        
        # 处理字符串、数字和关键字
        i = 0
        while i < len(line):
            # 跳过注释后的内容
            if comment_pos != -1 and i >= comment_pos:
                break
                
            char = line[i]
            
            # 处理字符串 - 简化逻辑，不考虑前面字符
            if char in ['"', "'"]:
                string_start = i
                quote_char = char
                i += 1
                
                # 查找字符串结束位置
                found_end = False
                while i < len(line):
                    # 处理转义字符
                    if line[i] == '\\' and i + 1 < len(line):
                        i += 2  # 跳过转义字符和下一个字符
                        continue
                    
                    # 找到匹配的引号
                    if line[i] == quote_char:
                        # 标记字符串
                        text_area.tag_add("string", f"{line_num + 1}.{string_start}", f"{line_num + 1}.{i + 1}")
                        i += 1
                        found_end = True
                        break
                    
                    i += 1
                
                if not found_end:
                    # 字符串未闭合，标记到行尾
                    text_area.tag_add("string", f"{line_num + 1}.{string_start}", line_end)
            
            # 处理数字
            elif char in '0123456789.':
                num_start = i
                
                # 找到数字的结束
                while i < len(line) and line[i] in '0123456789.':
                    i += 1
                
                # 标记数字
                text_area.tag_add("number", f"{line_num + 1}.{num_start}", f"{line_num + 1}.{i}")
            
            # 处理关键字
            else:
                # 找到单词的开始
                while i < len(line) and line[i] in 分隔符:
                    i += 1
                word_start = i
                
                # 找到单词的结束
                while i < len(line) and line[i] not in 分隔符:
                    i += 1
                word_end = i
                
                # 提取单词
                if word_start < word_end:
                    word = line[word_start:word_end]
                    
                    # 检查单词类型并标记
                    if word in 关键字:
                        text_area.tag_add("keyword", f"{line_num + 1}.{word_start}", f"{line_num + 1}.{word_end}")
                    elif word in 函数关键字:
                        text_area.tag_add("function", f"{line_num + 1}.{word_start}", f"{line_num + 1}.{word_end}")
                    elif word in error:
                        text_area.tag_add("error", f"{line_num + 1}.{word_start}", f"{line_num + 1}.{word_end}")
                    elif word in 特殊关键字:
                        text_area.tag_add("special", f"{line_num + 1}.{word_start}", f"{line_num + 1}.{word_end}")
                    elif word not in 代码关键字:
                        代码关键字.append(word)
                else:
                    i += 1
    
    # 30毫秒后再次刷新高亮
    root.after(30, highlight_code)

# ---------------------- 核心功能函数 ----------------------
def sync_scroll(*args):
    """同步行号与编辑框滚动"""
    line_numbers.yview_moveto(args[0])

def update_line_numbers():
    """更新行号"""
    content = text_area.get('1.0', tk.END)
    lines = content.count('\n') + (1 if content.strip() else 0)
    
    line_numbers.config(state='normal')
    line_numbers.delete('1.0', tk.END)
    line_numbers.insert(tk.END, '\n'.join(map(str, range(1, lines+1))))
    line_numbers.config(state='disabled')

def save_file():
    """保存代码到data.txt"""
    try:
        content = text_area.get("1.0", tk.END).rstrip('\n')
        with open("data.txt", "w", encoding="utf-8") as f:
            f.write(content)
        status_label.config(text="已保存")
    except Exception as e:
        status_label.config(text=f"保存失败: {str(e)}")

def load_file():
    """加载代码"""
    if os.path.exists("data.txt"):
        try:
            with open("data.txt", "r", encoding="utf-8") as f:
                text_area.insert("1.0", f.read())
            status_label.config(text="已加载")
        except:
            messagebox.showerror("错误", "加载失败，使用默认内容")
            create_default_content()
    else:
        create_default_content()

def create_default_content():
    """默认代码"""
    default = '''# 代码编辑区
print("Hello, 调试器!")

# 示例函数
def test():
    for i in range(3):
        print(f"计数: {i}")
        x = 3.14159
        message = '这是一个字符串'
        test_str = 'byd'byd  # 测试字符串高亮
        another = ) '  # 测试引号前面有字符的情况

if __name__ == "__main__":
    test()
'''
    text_area.delete("1.0", tk.END)
    text_area.insert("1.0", default)
    save_file()

class OutputRedirector(io.StringIO):
    """重定向输出到结果框"""
    def write(self, string):
        def update():
            result_text.config(state='normal')
            result_text.insert(tk.END, string)
            result_text.see(tk.END)  # 自动滚动到最新内容
            result_text.config(state='disabled')
        root.after(0, update)  # 线程安全更新UI

def run_code():
    global allLVar
    allLVar = copy.deepcopy(locals())
    """运行代码"""
    # 清空历史结果
    result_text.config(state='normal')
    result_text.delete('1.0', tk.END)
    result_text.insert('end', '================Code Start================\n')
    result_text.config(state='disabled')

    # 重定向输出
    old_stdout, old_stderr = sys.stdout, sys.stderr
    redirector = OutputRedirector()
    sys.stdout = sys.stderr = redirector

    try:
        # 编译+执行代码
        code = text_area.get("1.0", tk.END)
        compiled = compile(code, '<editor>', 'exec')
        exec(compiled, globals(), allLVar)

    except SyntaxError as e:
        print(f"语法错误: {e}")
    except Exception as e:
        print(f"运行错误: {type(e).__name__}: {e}")
    finally:
        # 恢复输出流
        sys.stdout, sys.stderr = old_stdout, old_stderr
        result_text.config(state='normal')
        result_text.insert('end', '================Code Close================\n')
        result_text.config(state='disabled')

def threaded_run():
    """多线程运行"""
    threading.Thread(target=run_code, daemon=True).start()

# 主窗口初始化
root = tk.Tk()
root.title("简易代码调试器")
root.geometry("1300x700")

# 主框架
main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# ---------------------- 1. 代码编辑区（含行号） ----------------------
editor_frame = ttk.Frame(main_frame)
editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 行号组件
line_numbers = tk.Text(editor_frame, width=5, padx=3, takefocus=0,
                      border=0, background='lightgray', state='disabled',
                      font=(字体, 12))
line_numbers.pack(side=tk.LEFT, fill=tk.Y)

# 代码编辑框
text_area = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD,insertbackground='white',
                                     undo=True, font=(字体, 12),
                                     bg='#002240', fg='white')  # 深色背景，白色文字
text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 变量监听
VarText = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD,
                                     undo=True, width=20, font=(字体, 10))
VarText.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# ---------------------- 2. 侧边功能按钮区 ----------------------
sidebar = ttk.Frame(main_frame, width=120)
sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

# 运行按钮
run_button = ttk.Button(sidebar, text="运行代码", width=12, command=None)
run_button.pack(pady=(10, 5))

# 保存按钮
save_button = ttk.Button(sidebar, text="手动保存", width=12, command=None)
save_button.pack(pady=5)

# 保存状态提示
status_label = ttk.Label(sidebar, text="已保存")
status_label.pack(pady=5)

# ---------------------- 3. 运行结果区 ----------------------
result_frame = ttk.Frame(root)
result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

# 结果区标题
result_label = ttk.Label(result_frame, text="运行结果：")
result_label.pack(anchor=tk.W)

# 结果显示框
result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD,
                                       font=("Consolas", 10), state='disabled')
result_text.pack(fill=tk.BOTH, expand=True, pady=(2, 0))

def dict_keys_to_str(d: dict) -> dict:
    """将字典所有key转为字符串类型"""
    new_dict = {}
    for key, value in d.items():
        str_key = str(key)
        if isinstance(value, dict):
            new_dict[str_key] = dict_keys_to_str(value)
        else:
            new_dict[str_key] = value
    return new_dict

def update():
    global allLVar, memory_V, s
    中间 = dict_keys_to_str(allLVar)
    for tag in VarText.tag_names():
        VarText.tag_remove(tag, "0.0", "end")
    a = VarText.yview()[0]
    VarText.delete('0.0', 'end')

    c = ['white', '#00F0F0']
    t = tuple(中间.keys())
    if memory_V != allLVar:
        s = subDict(中间, memory_V)
        memory_V = dict_keys_to_str(中间)
    for i in 中间:
        if (i in s) and (s[i] > time.time()):
            p(VarText, f'{i}={allLVar[i]}', 'red', background=c[t.index(i) % 2])
        else:
            p(VarText, f'{i}={allLVar[i]}', background=c[t.index(i) % 2])
            
    VarText.yview_moveto(a)
    root.after(10, update)

def subDict(x, y):
    """计算x与y中的变化值"""
    if x == {} or y == {}:
        return {}
    c = {}
    a = dict_keys_to_str(x)
    b = dict_keys_to_str(y)
    for i in b:
        if i in a:
            if a[i] == b[i]:
                c[i] = time.time()
            else:
                c[i] = time.time() + 1
    return c

# ---------------------- 绑定事件与初始化 ----------------------
allLVar = {}
memory_V = {}
s = {}

text_area.tag_config("function", foreground="#62ff2e")  # 浅绿色函数
text_area.tag_config("keyword", foreground="#ff632e")  # 橙色关键字
text_area.tag_config("error", foreground="red")  # 红色错误
text_area.tag_config("special", foreground="#ff3cfd")  # 粉色特殊关键字
text_area.tag_config("comment", foreground="#a900ea")  # 紫色注释
text_area.tag_config("number", foreground="#23a9f2")  # 蓝色数字
text_area.tag_config("string", foreground="#02ff02")  # 绿色字符串

# 滚动同步
text_area.configure(yscrollcommand=sync_scroll)

# 文本变化触发
text_area.bind('<KeyRelease>', lambda e: (update_line_numbers(), root.after_idle(save_file)))

# 绑定按钮功能
run_button.config(command=threaded_run)
save_button.config(command=save_file)

# 初始加载
load_file()
update_line_numbers()

# 启动高亮功能
root.after(30, highlight_code)
root.after(0, update)

# 主循环
root.mainloop()
