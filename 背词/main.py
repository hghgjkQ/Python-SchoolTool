import pyperclip,os
import edge_tts,random,threading
from playsound import playsound
import tkinter as tk
from tkinter import ttk
from pypinyin import lazy_pinyin

temp=os.listdir('temp')

# 相似度计算
def levenshtein_distance(s1, s2):
    s1 = s1.replace('⭐', '').lower()
    s2 = s2.replace('⭐', '').lower()
    dp = [[0]*(len(s2)+1) for _ in range(len(s1)+1)]
    for i in range(len(s1)+1):
        dp[i][0] = i
    for j in range(len(s2)+1):
        dp[0][j] = j
    for i in range(1, len(s1)+1):
        for j in range(1, len(s2)+1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+cost)
    return dp[len(s1)][len(s2)]

def get_similar_words(target_word, word_list):
    similar_words = []
    for word in word_list:
        if word == target_word:
            continue
        if levenshtein_distance(target_word, word) <= 2:
            similar_words.append(word)
    return similar_words

# 音频播放
def 播放(音频名称):
    def _play():
        文件路径 = f'{音频名称}.mp3'
        try:
            playsound(文件路径)
        except Exception as e:
            print(f"播放{音频名称}失败：{e}")
    play_thread = threading.Thread(target=_play, daemon=True)
    play_thread.start()

def edge_tts_save_to_file(input_text, output_file="say.mp3"):
    try:
        communicate = edge_tts.Communicate(input_text, "zh-CN-XiaoxiaoNeural")
        communicate.save_sync(output_file)
    except Exception as e:
        print(f"❌ 保存失败：{str(e)}")

def 朗读(x):
    path=f'{x.lower()}'
    播放(f'temp/{path}')

with open('data.txt','r',encoding='utf-8') as f:
    单词集=eval(f.read())

for i in 单词集:
    i=i.replace('⭐','')
    if not ((f'{i.lower()}.mp3' in temp) or (f'{i}.mp3' in temp)):
        print(f'{i}不存在并正在补全')
        edge_tts_save_to_file(i,f'temp/{i}.mp3')
print('准备就绪！')


def 保存词():
    global 词
    shu=sum([len(词[i]) for i in 词])-len(词)
    s=0
    for i in 词:
        s+=sum(词[i])
    try:
        top_left_label['text']=f'总次数：{shu} 总（实际）正确率：{s/(shu+len(词))*100:.2f}%（{(s)/(shu)*100:.2f}%）'
    except Exception as e:
        top_left_label['text']=e
    with open('temp.txt','w',encoding='utf-8') as f:
        f.write(str(词))

try:
    with open('temp.txt','r',encoding='utf-8') as f:
        词=eval(f.read())
except Exception as e:
    print(f'读取出现问题：{e}')
    词={}
    for i in 单词集.keys():
        词[i]=[0]
        保存词()
if len(词)!=len(单词集):
    for i in 单词集:
        if i not in 词:
            print(f'缺少单词：{i}')
            词[i]=[0]
    保存词()

# ====================== 中文转拼音 ======================
def text_to_pinyin(text):
    return ''.join(lazy_pinyin(text)).lower()

# ====================== 窗口 ======================
root = tk.Tk()
root.title("背词")
try:
    root.iconphoto(False, tk.PhotoImage(file='ico.png'))
except:
    pass
root.geometry("1200x800")
root.resizable(True, True)

button_list = []
# 保存按钮原始数据（文字、命令），用于筛选恢复
button_original_data = []

# ====================== 左侧 ======================
top_left_label = tk.Label(root, text="左上角固定文字", font=("SimHei", 10))
top_left_label.place(relx=0.02, rely=0.02, relwidth=0.2, relheight=0.05)

main_label = tk.Label(root, text="", font=("方正正黑简体", 20))
main_label.place(relx=0.02, rely=0.1, relwidth=0.3, relheight=0.1)

sub_label = tk.Label(root, text="", font=("SimHei", 15))
sub_label.place(relx=0.02, rely=0.22, relwidth=0.3, relheight=0.05)

entry_frame = tk.Frame(root)
entry_frame.place(relx=0.02, rely=0.3, relwidth=0.3, relheight=0.08)

input_entry = tk.Entry(entry_frame, width=25, highlightthickness=1, highlightbackground="gray")
input_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

small_btn = tk.Button(entry_frame, text="🎶", width=6,command=lambda : 朗读(main_label['text']))
small_btn.pack(side=tk.LEFT, padx=5)

confirm_btn = tk.Button(root, text="确认", width=20,
                        command=lambda: check_input(root, main_label, input_entry))
confirm_btn.place(relx=0.02, rely=0.4, relwidth=0.3, relheight=0.5)

# ====================== 左下角：拼音筛选框（只控制中间按钮） ======================
pinyin_frame = tk.Frame(root)
pinyin_frame.place(relx=0.02, rely=0.9, relwidth=0.3, relheight=0.08)

tk.Label(pinyin_frame, text="按钮拼音筛选：", font=("SimHei", 10)).pack(side=tk.LEFT, padx=5)

pinyin_entry = tk.Entry(pinyin_frame, width=20, highlightthickness=1, highlightbackground="gray")
pinyin_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

# ====================== 【修改：拼音框输入数字时拦截并触发按键】 ======================
def validate_pinyin(c):
    # 允许空、小写字母；输入数字则拦截并触发按键
    if c.isdigit():
        # 构造一个虚拟事件，触发数字键逻辑
        class FakeEvent:
            char = c
        press_number_key(FakeEvent())
        return False  # 不允许数字输入到框里
    return c.islower() or c == ""

# 重新注册验证命令
vcmd = root.register(validate_pinyin)
pinyin_entry.config(validate="key", validatecommand=(vcmd, "%S"))

# ====================== 中间按钮区域（修改：100个按钮，一行4个） ======================
button_frame = tk.Frame(root)
button_frame.place(relx=0.35, rely=0.02, relwidth=0.5, relheight=0.96)

# 生成100个按钮，一行4个，共25行
BUTTON_TOTAL = 100  # 总按钮数
COLUMN_COUNT = 4    # 每行4个
ROW_COUNT = BUTTON_TOTAL // COLUMN_COUNT  # 25行

# 计算每个按钮的尺寸和间距
btn_width = (1 - 0.05) / COLUMN_COUNT  # 列间距总预留0.05
btn_height = (1 - 0.05) / ROW_COUNT    # 行间距总预留0.05
x_padding = 0.01  # 按钮横向间距
y_padding = 0.00 # 按钮纵向间距

for i in range(BUTTON_TOTAL):
    # 计算行列索引
    row = i // COLUMN_COUNT
    col = i % COLUMN_COUNT
    
    # 计算按钮位置
    relx = x_padding + col * (btn_width + x_padding)
    rely = y_padding + row * (btn_height + y_padding)
    
    btn = tk.Button(button_frame, text="", height=1, font=("SimHei", 8))
    btn.place(relx=relx, rely=rely, relwidth=btn_width, relheight=btn_height)
    button_list.append(btn)

# ====================== 右侧单词列表（完全恢复原样） ======================
RIGHT_FRAME = tk.Frame(root, bd=1, relief=tk.SUNKEN)
RIGHT_FRAME.place(relx=0.85, rely=0.02, relwidth=0.13, relheight=0.96)

tk.Label(RIGHT_FRAME, text="单词正确率（从小到大）", font=("SimHei",11,"bold"), bg="#f5f5f5")\
    .pack(fill=tk.X, pady=3)

text_frame = tk.Frame(RIGHT_FRAME)
text_frame.pack(fill=tk.BOTH, expand=True)

text_widget = tk.Text(text_frame, wrap=tk.NONE, font=("Courier", 10), bg="white", relief=tk.FLAT, borderwidth=0)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=text_widget.yview)
text_widget.configure(yscrollcommand=scrollbar.set)

text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_widget.config(state=tk.DISABLED)

def get_word_accuracy(word):
    scores = 词[word].copy()
    scores.pop(0)
    acc = sum(scores)/len(scores) if scores else 0
    return round(acc, 2)

def get_color(acc):
    r = int(255 * (1 - acc))
    g = int(255 * acc)
    return f"#{r:02x}{g:02x}00"

def refresh_word_list():
    current_line = int(text_widget.index("@0,0").split(".")[0])
    sorted_items = []
    for w in 词:
        clean = w.replace('⭐','')
        acc = get_word_accuracy(w)
        sorted_items.append((clean, acc))
    sorted_items.sort(key=lambda x: x[1])

    text_widget.config(state=tk.NORMAL)
    text_widget.delete(1.0, tk.END)
    for word, acc in sorted_items:
        line = f"{word:<20} {acc*100:>5.0f}%"
        start = text_widget.index(tk.END + "-1c")
        text_widget.insert(tk.END, line + "\n")
        end = text_widget.index(tk.END + "-1c")
        color = get_color(acc)
        tag = f"c_{acc}"
        text_widget.tag_add(tag, start, end)
        text_widget.tag_config(tag, background=color, foreground="white")
    text_widget.delete(tk.END + "-1c", tk.END)
    text_widget.config(state=tk.DISABLED)
    text_widget.see(f"{current_line}.0")

# ====================== 核心：按拼音筛选中间按钮 ======================
def filter_buttons_by_pinyin(pinyin_filter):
    pinyin_filter = pinyin_filter.strip().lower()
    # 无输入：恢复所有按钮
    if not pinyin_filter:
        for i, btn in enumerate(button_list):
            if i < len(button_original_data):
                txt, cmd = button_original_data[i]
                btn.config(text=txt, command=cmd, state=tk.NORMAL)
            else:
                btn.config(text="", state=tk.DISABLED)
        return

    # 有输入：匹配按钮文字的拼音
    matched = []
    for txt, cmd in button_original_data:
        if not txt:
            continue
        pinyin = text_to_pinyin(txt)
        if pinyin_filter in pinyin:
            matched.append((txt, cmd))

    # 先清空所有按钮
    for btn in button_list:
        btn.config(text="", state=tk.DISABLED)
    # 再填充匹配到的按钮
    for i, (txt, cmd) in enumerate(matched):
        if i < len(button_list):
            button_list[i].config(text=txt, command=cmd, state=tk.NORMAL)

# 输入变化时实时筛选按钮
def on_pinyin_change(event):
    filter_buttons_by_pinyin(pinyin_entry.get())

pinyin_entry.bind('<KeyRelease>', on_pinyin_change)

# ====================== 原有按钮生成逻辑（修改：优先首字母相同的单词） ======================
def generate_options(current_word):
    correct_meaning = ','.join(单词集[current_word])
    options = [(correct_meaning, True)]
    all_words = list(单词集.keys())
    
    # 处理目标单词，提取首字母
    clean_target = current_word.replace('⭐', '').lower()
    target_first_char = clean_target[0] if clean_target else ''
    
    # 1. 优先筛选首字母相同的单词（几率特别大）
    same_first_char_words = [
        w for w in all_words 
        if w != current_word and w.replace('⭐', '').lower().startswith(target_first_char)
    ]
    
    # 2. 补充相似单词（编辑距离）
    similar_words = get_similar_words(current_word, all_words)
    similar_words = [w for w in similar_words if w not in same_first_char_words]
    
    # 3. 其他单词（补充用）
    other_words = [
        w for w in all_words 
        if w != current_word and w not in same_first_char_words and w not in similar_words
    ]
    
    # 需要99个干扰项（因为总按钮100个，1个正确项）
    needed_distractors = 99
    
    # 优先选首字母相同的单词（占80%）
    same_char_count = min(int(needed_distractors * 0.8), len(same_first_char_words))
    selected_same_char = random.sample(same_first_char_words, same_char_count) if same_first_char_words else []
    
    # 剩下的从相似单词中选（占15%）
    remaining = needed_distractors - same_char_count
    similar_count = min(int(needed_distractors * 0.15), len(similar_words), remaining)
    selected_similar = random.sample(similar_words, similar_count) if similar_words else []
    
    # 最后从其他单词中补充
    remaining -= similar_count
    selected_other = random.sample(other_words, remaining) if remaining > 0 and other_words else []
    
    # 合并所有干扰项
    selected_distractors = selected_same_char + selected_similar + selected_other
    
    # 如果数量不够，再补充（防止单词库不足）
    if len(selected_distractors) < needed_distractors:
        extra_needed = needed_distractors - len(selected_distractors)
        all_available = [w for w in all_words if w != current_word and w not in selected_distractors]
        selected_distractors += random.sample(all_available, extra_needed) if all_available else []
    
    # 添加干扰项到选项
    for word in selected_distractors:
        options.append((','.join(单词集[word]), False))
    
    # 随机打乱顺序
    random.shuffle(options)
    return options

def update_buttons(current_word):
    global button_original_data
    options = generate_options(current_word)
    button_original_data.clear()  # 清空原始数据
    for idx, btn in enumerate(button_list):
        if idx < len(options):
            meaning, is_correct = options[idx]
            cmd = lambda m=meaning, c=is_correct: button_click(m, c)
            button_original_data.append((meaning, cmd))
            btn.config(text=meaning, command=cmd, state=tk.NORMAL)
        else:
            button_original_data.append(("", None))
            btn.config(text="", state=tk.DISABLED)
    # 每次刷新题目后，重新应用筛选
    filter_buttons_by_pinyin(pinyin_entry.get())

# ====================== 原有逻辑不变 ======================
def button_click(selected_meaning, is_correct):
    global 词
    结果 = 1 if is_correct else 0
    词[main_label.原词].append(结果)
    保存词()
    pinyin_entry.delete('0','end')
    if is_correct:
        input_entry.config(highlightbackground="green", highlightcolor="green", highlightthickness=2)
        sub_label['text']=','.join(main_label.目标)+'：'+str(结果)
        播放('win')
    else:
        播放(f'error{random.randint(1,3)}')
        shake_window(root)
        input_entry.config(highlightbackground="red", highlightcolor="red", highlightthickness=2)
        sub_label['text']=main_label.原词+'\n'+','.join(main_label.目标)+'：'+str(结果)
    root.after(500, lambda: input_entry.config(highlightbackground="gray", highlightcolor="gray", highlightthickness=1))
    root.after(500, 随机单词)

def 随机单词():
    global 词
    目标词池=[]
    for i in 词:
        if sum(词[i])==0:
            目标词池=[]
            for x in 词:
                if sum(词[x])==0:
                    目标词池.append(x)
            break
        aaa=词[i].copy()
        aaa.pop(0)
        添加=100-max(min(round((sum(aaa)/len(aaa))*100),99),1)
        目标词池+=[i]*添加
    word=random.choice(目标词池)
    main_label.目标=单词集[word]
    main_label.原词=word
    if '⭐' in word:
        word=word.replace('⭐','')
        main_label['fg']='green'
    else:
        main_label['fg']='black'
    朗读(word)
    main_label['text']=word
    update_buttons(main_label.原词)
    refresh_word_list()
    
    

def 判断(x,目标):
    a=0
    for i in 目标:
        if x in i:
            a+=1
    return a/len(目标)

def check_input(window, main_text_label, entry):
    global 词
    input_content = entry.get().strip()
    if input_content == '':
        return
    结果=判断(input_content,main_text_label.目标)
    词[main_text_label.原词].append(结果)
    if 结果>0:
        entry.config(highlightbackground="green", highlightcolor="green", highlightthickness=2)
        sub_label['text']=','.join(main_text_label.目标)+'：'+str(结果)
        播放('win')
        window.after(500, lambda: entry.config(highlightbackground="gray", highlightcolor="gray", highlightthickness=1))
        window.after(500, 随机单词)
    else:
        播放(f'error{random.randint(1,3)}')
        shake_window(window)
        entry.config(highlightbackground="red", highlightcolor="red", highlightthickness=2)
        sub_label['text']=''.join(main_text_label.目标)+'：'+str(结果)
        window.after(500, lambda: entry.config(highlightbackground="gray", highlightcolor="gray", highlightthickness=1))
        window.after(500, 随机单词)
    保存词()

def shake_window(window):
    init_x = window.winfo_x()
    init_y = window.winfo_y()
    def shake(step=0):
        if step < 10:
            new_x = init_x + (3 if step%2==0 else -3)
            window.geometry(f"+{new_x}+{init_y}")
            window.after(10, shake, step+1)
        else:
            window.geometry(f"+{init_x}+{init_y}")
    shake()

# ====================== 新增：数字键绑定功能 ======================
def get_right_list_top10_words():
    """获取右侧单词列表的前10个单词"""
    sorted_items = []
    for w in 词:
        clean = w.replace('⭐','')
        acc = get_word_accuracy(w)
        sorted_items.append((clean, acc))
    sorted_items.sort(key=lambda x: x[1])
    # 提取前10个单词
    top10_words = [item[0] for item in sorted_items[:10]]
    return top10_words

def press_number_key(event):
    """处理数字键按下事件"""
    key = event.char
    # 获取前10个单词
    top10_words = get_right_list_top10_words()
    
    # 确定选中的索引（1-9对应0-8，0对应9）
    if key == '0':
        idx = 9
    elif key in '123456789':
        idx = int(key) - 1
    else:
        return  # 不是目标数字键，直接返回
    
    # 检查索引是否有效
    if idx >= len(top10_words):
        return
    
    # 获取选中的单词
    selected_word = top10_words[idx]
    # 找到中间按钮中对应该单词释义的按钮并触发点击
    for i, (meaning, cmd) in enumerate(button_original_data):
        if meaning == ','.join(单词集.get(selected_word, [])) and cmd:
            # 执行按钮的点击命令
            cmd()
            break

# 绑定数字键（1-9和0）
for num in '1234567890':
    root.bind(num, press_number_key)
    
def on_pinyin_key(event):
    """按下数字键时直接点击对应按钮（1~10），并阻止数字输入到输入框"""
    if event.char=='':
        return None
    if event.char in '1234567890':
        num = int(event.char)
        idx = 9 if num == 0 else num - 1
        if idx < len(button_list):
            btn = button_list[idx]
            if btn['state'] == tk.NORMAL:
                btn.invoke()
        return "break"  # 阻止数字输入，避免触发拼音筛选
    return None

# 绑定键盘按下事件，add=True 确保不影响原有绑定
pinyin_entry.bind('<Key>', on_pinyin_key, add=True)
# 启动
refresh_word_list()
随机单词()
root.mainloop()
