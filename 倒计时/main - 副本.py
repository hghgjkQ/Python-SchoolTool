import tkinter as tk
import time
from playsound import playsound


root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", 0.85)
root.config(bg="#f0f0f0")

# 固定窗口尺寸
ORIGIN_W = 500
ORIGIN_H = 350
SCREEN_W = root.winfo_screenwidth()
SCREEN_H = root.winfo_screenheight()

root.geometry(f"{ORIGIN_W}x{ORIGIN_H}+{SCREEN_W}+{SCREEN_H}")
root.resizable(False, False)

# 全局变量
diff_text = tk.StringVar(value="距离目标时间：00时10分")
h1 = h2 = m1 = m2 = None
h2_label = None
target_hour = target_min = 0
countdown_timer = None
progress = 0
win_x = win_y = 0

# 窗口拖动
start_x = start_y = 0
def on_press(event):
    global start_x, start_y
    start_x = event.x
    start_y = event.y

def on_drag(event):
    global win_x, win_y
    win_x = root.winfo_x() + event.x - start_x
    win_y = root.winfo_y() + event.y - start_y
    root.geometry(f"+{win_x}+{win_y}")

root.bind("<Button-1>", on_press)
root.bind("<B1-Motion>", on_drag)

# 三次方缓动函数
def ease_in_out_cubic(x):
    return 4 * x**3 if x < 0.5 else 1 - ((-2*x + 2)**3) / 2

# ==================== 主界面 ====================
def create_main_ui():
    global h1, h2, m1, m2, h2_label, target_hour, target_min, countdown_timer, win_x, win_y
    # 取消所有定时器
    if countdown_timer:
        root.after_cancel(countdown_timer)
        countdown_timer = None
    
    for w in root.winfo_children():
        w.destroy()
    root.config(bg="#f0f0f0")
    root.attributes("-alpha", 0.85)
    win_x = (SCREEN_W - ORIGIN_W) // 2
    win_y = (SCREEN_H - ORIGIN_H) // 2
    root.geometry(f"{ORIGIN_W}x{ORIGIN_H}+{win_x}+{win_y}")

    top_frame = tk.Frame(root, bg="#f0f0f0")
    top_frame.pack(side=tk.TOP, fill=tk.X)
    btn_exit = tk.Button(top_frame, text="退出", width=10, command=root.destroy)
    btn_exit.pack(side=tk.RIGHT, padx=5, pady=1)

    top_label = tk.Label(root, textvariable=diff_text, font=("微软雅黑", 13), bg="#f0f0f0")
    top_label.pack(side=tk.TOP, pady=6)

    localtime = time.localtime()
    hour_str = f"{localtime.tm_hour:02d}"
    h1 = tk.StringVar(value=hour_str[0])
    h2 = tk.StringVar(value=hour_str[1])

    current_min = localtime.tm_min
    target_min_val = 0 if current_min >= 50 else current_min + 10
    min_str = f"{target_min_val:02d}"
    m1 = tk.StringVar(value=min_str[0])
    m2 = tk.StringVar(value=min_str[1])

    def update_color():
        if not h2_label: return
        n1 = int(h1.get())
        n2 = int(h2.get())
        h2_label.config(fg="red" if n1 == 2 and n2 > 3 else "black")

    def update_diff_display():
        global target_hour, target_min
        hh = int(h1.get())*10 + int(h2.get())
        mm = int(m1.get())*10 + int(m2.get())
        target_hour, target_min = hh, mm
        now = time.localtime()
        hd = hh - now.tm_hour
        md = mm - now.tm_min
        if md < 0:
            hd -= 1
            md += 60
        if hd < 0:
            hd += 24
        diff_text.set(f"距离目标时间：{hd:02d}时{md:02d}分")

    def create_unit(parent, var, max_v):
        global h2_label
        f = tk.Frame(parent, bg="#f0f0f0")
        def add():
            v = int(var.get())+1
            var.set(str(v if v<=max_v else 0))
            update_color()
            update_diff_display()
        def sub():
            v = int(var.get())-1
            var.set(str(max_v if v<0 else v))
            update_color()
            update_diff_display()
        tk.Button(f, text="+", font=("微软雅黑",16), width=4, command=add).pack(side=tk.TOP)
        lbl = tk.Label(f, textvariable=var, font=("微软雅黑",42), bg="#f0f0f0")
        lbl.pack(side=tk.TOP, pady=2)
        tk.Button(f, text="-", font=("微软雅黑",16), width=4, command=sub).pack(side=tk.TOP)
        if var == h2:
            h2_label = lbl
        return f

    center_frame = tk.Frame(root, bg="#f0f0f0")
    center_frame.pack(expand=True, fill=tk.BOTH, pady=8)
    create_unit(center_frame, h1, 2).pack(side=tk.LEFT, padx=(8,1))
    create_unit(center_frame, h2,9).pack(side=tk.LEFT, padx=1)
    tk.Label(center_frame, text="：", font=("微软雅黑",42), bg="#f0f0f0").pack(side=tk.LEFT, expand=True)
    create_unit(center_frame, m2,9).pack(side=tk.RIGHT, padx=(1,8))
    create_unit(center_frame, m1,5).pack(side=tk.RIGHT, padx=1)

    start_btn = tk.Button(root, text="开始倒计时", font=("微软雅黑",14), width=22,
                          command=lambda: animate_switch(create_countdown_ui))
    start_btn.pack(side=tk.BOTTOM, pady=10)

    update_color()
    update_diff_display()

# ==================== 倒计时界面 ====================
def create_countdown_ui(is_finished=False):
    global countdown_timer
    # 彻底取消倒计时定时器
    if countdown_timer:
        root.after_cancel(countdown_timer)
        countdown_timer = None
        
    for w in root.winfo_children():
        w.destroy()
    root.config(bg="#f0f0f0")
    root.attributes("-alpha", 0.85)
    # 固定窗口大小，不再动画
    root.geometry(f"{ORIGIN_W}x{ORIGIN_H}+{win_x}+{win_y}")

    if is_finished:
        playsound("a.mp3", block=False)
        playsound("a.mp3", block=False)
        playsound("a.mp3", block=False)
        time_label = tk.Label(root, text="倒计时结束", font=("微软雅黑", 40, "bold"), bg="#f0f0f0", fg="red")
        current_t = time.strftime("%H:%M:%S", time.localtime())
        tip_label = tk.Label(root, text="", font=("微软雅黑", 15), bg="#f0f0f0", fg="gray")
    else:
        time_label = tk.Label(root, font=("微软雅黑", 40, "bold"), bg="#f0f0f0")
        tip_label = tk.Label(root, text=f"目标时间：{target_hour:02d}:{target_min:02d}", font=("微软雅黑", 15), bg="#f0f0f0", fg="gray")
    
    time_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
    tip_label.place(relx=0.5, rely=0.55, anchor=tk.CENTER)

    tk.Button(root, text="退出", font=("微软雅黑",12),
             command=lambda: animate_switch(create_main_ui)).place(relx=0.05, rely=0.92, anchor=tk.SW)
    tk.Button(root, text="全屏", font=("微软雅黑",12),
             command=start_fullscreen_animate).place(relx=0.95, rely=0.92, anchor=tk.SE)

    def update_small_countdown():
        global countdown_timer
        now = time.localtime()
        now_sec = now.tm_hour*3600 + now.tm_min*60 + now.tm_sec
        target_sec = target_hour*3600 + target_min*60
        diff_sec = target_sec - now_sec

        # 结束直接显示，不执行任何缩放动画
        if diff_sec <= 0:
            create_countdown_ui(is_finished=True)
            return
        if diff_sec <= 10:
            playsound("b.mp3", block=False)

        h = diff_sec//3600
        m = (diff_sec%3600)//60
        s = diff_sec%60
        time_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        countdown_timer = root.after(1000, update_small_countdown)

    if not is_finished:
        update_small_countdown()

# ==================== 全屏倒计时界面 ====================
def create_fullscreen_ui():
    global countdown_timer
    if countdown_timer:
        root.after_cancel(countdown_timer)
        countdown_timer = None
        
    for w in root.winfo_children():
        w.destroy()
    root.config(bg="black")
    root.attributes("-alpha", 1)
    root.geometry(f"{SCREEN_W}x{SCREEN_H}+0+0")

    time_label = tk.Label(root, font=("微软雅黑",200,"bold"), fg="white", bg="black")
    target_tip = tk.Label(root, text=f"目标时间：{target_hour:02d}:{target_min:02d}", 
                         font=("微软雅黑", 25), fg="gray", bg="black")
    exit_btn = tk.Button(root, text="退出全屏", font=("微软雅黑",15), 
                        command=exit_fullscreen_animate, bg="#333", fg="white")
    
    time_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
    target_tip.place(relx=0.5, rely=0.55, anchor=tk.CENTER)
    exit_btn.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

    def update_big_countdown():
        global countdown_timer
        now = time.localtime()
        now_sec = now.tm_hour*3600 + now.tm_min*60 + now.tm_sec
        target_sec = target_hour*3600 + target_min*60
        diff_sec = target_sec - now_sec

        # 结束直接显示，不自动缩小
        if diff_sec <= 0:
            create_countdown_ui(is_finished=True)
            return
        if diff_sec <= 10:
            playsound("b.mp3", block=False)
            
        h = diff_sec//3600
        m = (diff_sec%3600)//60
        s = diff_sec%60
        time_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        root.geometry(f"+0+0")
        countdown_timer = root.after(1000, update_big_countdown)

    update_big_countdown()

# ==================== 退出全屏动画 ====================
def exit_fullscreen_animate():
    global countdown_timer, progress
    if countdown_timer:
        root.after_cancel(countdown_timer)
        countdown_timer = None
    progress = 0.0
    exit_animate()

def exit_animate():
    global progress
    speed = 0.01
    smooth = ease_in_out_cubic(progress)

    center_x = win_x + ORIGIN_W//2
    center_y = win_y + ORIGIN_H//2
    w = int(SCREEN_W - (SCREEN_W - ORIGIN_W) * smooth)
    h = int(SCREEN_H - (SCREEN_H - ORIGIN_H) * smooth)
    x = int(center_x - w//2)
    y = int(center_y - h//2)

    root.attributes("-alpha", 1.0 - 0.15 * smooth)
    bg = int(240 * smooth)
    root.config(bg=f"#{bg:02x}{bg:02x}{bg:02x}")

    root.geometry(f"{w}x{h}+{x}+{y}")
    progress += speed

    if progress >= 1.0:
        create_countdown_ui()
        return

    root.after_idle(exit_animate)

# ==================== 进入全屏动画 ====================
def start_fullscreen_animate():
    global progress
    progress = 0.0
    fullscreen_animate()

def fullscreen_animate():
    global progress
    speed = 0.01
    smooth = ease_in_out_cubic(progress)

    center_x = win_x + ORIGIN_W//2
    center_y = win_y + ORIGIN_H//2
    w = int(ORIGIN_W + (SCREEN_W - ORIGIN_W) * smooth)
    h = int(ORIGIN_H + (SCREEN_H - ORIGIN_H) * smooth)
    x = int(center_x - w//2)
    y = int(center_y - h//2)

    root.attributes("-alpha", 0.85 + 0.15 * smooth)
    bg = int(240 - 240 * smooth)
    root.config(bg=f"#{bg:02x}{bg:02x}{bg:02x}")

    root.geometry(f"{w}x{h}+{x}+{y}")
    progress += speed

    if progress >=1.0:
        create_fullscreen_ui()
        return

    root.after_idle(fullscreen_animate)

# ==================== 界面切换动画 ====================
anim_stage = 0
target_ui = None

def animate_switch(callback):
    global anim_stage, target_ui, progress
    anim_stage = 0
    progress = 0.0
    target_ui = callback
    animate()

def animate():
    global anim_stage, progress
    speed = 0.01
    cx = win_x + ORIGIN_W//2
    cy = win_y + ORIGIN_H//2
    smooth = ease_in_out_cubic(progress)

    if anim_stage ==0:
        w = int(1 + (ORIGIN_W - 1)*(1-smooth))
        h = int(1 + (ORIGIN_H - 1)*(1-smooth))
        x = int(cx - w//2)
        y = int(cy - h//2)
        progress += speed
        if progress >=1.0:
            anim_stage =1
            progress=0.0
            target_ui()
    else:
        w = int(1 + (ORIGIN_W - 1)*smooth)
        h = int(1 + (ORIGIN_H - 1)*smooth)
        x = int(cx - w//2)
        y = int(cy - h//2)
        progress += speed
        if progress >=1.0:
            root.geometry(f"{ORIGIN_W}x{ORIGIN_H}+{win_x}+{win_y}")
            return

    root.geometry(f"{w}x{h}+{x}+{y}")
    root.after_idle(animate)

# 启动
create_main_ui()
root.mainloop()
