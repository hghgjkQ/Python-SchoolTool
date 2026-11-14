import pygame
import sys
import ctypes  # 调用Windows API的核心库
from pygame.locals import *

# -------------------------- 关键：调用Windows原生提示框API --------------------------
# 加载user32.dll，调用MessageBoxW（W表示支持中文宽字符）
# 参数说明：
#   hwnd: 父窗口句柄（0表示无父窗口，置顶显示）
#   text: 提示框内容
#   caption: 提示框标题
#   type: 提示框类型（0=仅确定按钮，1=确定+取消，48=警告，64=信息）
MessageBox = ctypes.windll.user32.MessageBoxW
# 定义提示框类型常量（方便调用）
MB_INFO = 64        # 信息提示框（带i图标）
MB_WARNING = 48     # 警告提示框（带!图标）
MB_OK = 0           # 仅确定按钮

# 初始化pygame
pygame.init()

# 指定Windows自带中文字体（确保中文显示）
font_path = "C:/Windows/Fonts/msyh.ttc"  # 微软雅黑
font = pygame.font.Font(font_path, 32)

# 设置窗口
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("中文文本输入框（原生Windows提示框）")

# 输入框参数
input_box = pygame.Rect(100, 100, 200, 32)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive
active = False
text = ''
running = True

# 主循环
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        
        # 激活/取消输入框
        elif event.type == MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = not active
            else:
                active = False
            color = color_active if active else color_inactive
        
        # 键盘事件处理
        elif event.type == KEYDOWN:
            if active:
                if event.key == K_RETURN:
                    print(f"输入的文本：{text}")
                    # -------------------------- 替换为Windows原生提示框 --------------------------
                    if text.strip():
                        # 信息提示框：标题+内容（支持中文）
                        MessageBox(0, f"你输入的内容是：\n{text}", "输入内容", MB_OK | MB_INFO)
                    else:
                        # 警告提示框
                        MessageBox(0, "输入框不能为空！", "提示", MB_OK | MB_WARNING)
                    text = ''
                # 退格删除（支持中文）
                elif event.key == K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode
        
        # 启用中文输入
        pygame.key.start_text_input()
        if event.type == TEXTINPUT:
            text += event.text

    # 绘制界面
    screen.fill((255, 255, 255))
    txt_surface = font.render(text, True, color)
    input_box.w = max(200, txt_surface.get_width() + 10)
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    pygame.draw.rect(screen, color, input_box, 2)
    pygame.display.flip()
