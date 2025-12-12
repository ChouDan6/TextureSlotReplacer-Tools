import tkinter as tk
from tkinter import ttk, messagebox

# --- 颜色配置 ---
BG_COLOR = "#F0F2F5"        # 整体背景
CARD_BG = "#FFFFFF"         # 卡片背景
HEADER_BG = "#2E3440"       # 表头深色
HEADER_FG = "#ECEFF4"       # 表头文字
ACCENT_COLOR = "#5E81AC"    # 左侧装饰条蓝
INPUT_BORDER = "#E5E9F0"    # 输入框边框

# 按钮颜色
BTN_PASTE_BG = "#D8DEE9"    # 粘贴按钮-常态
BTN_PASTE_HOVER = "#E5E9F0" # 粘贴按钮-悬停
BTN_COPY_BG = "#A3BE8C"     # 复制按钮-常态 (绿)
BTN_COPY_FG = "#2E3440"     # 复制按钮-文字
BTN_COPY_HOVER = "#B1C69D"  # 复制按钮-悬停
BTN_CLEAR_BG = "#BF616A"    # 清空按钮-常态 (红)
BTN_CLEAR_HOVER = "#C8757E" # 清空按钮-悬停

TEXT_FONT = ("Consolas", 10)
UI_FONT = ("Microsoft YaHei", 9)

class ModernButton(tk.Label):
    """自定义扁平化按钮，模拟Web风格"""
    def __init__(self, parent, text, command=None, bg="#DDDDDD", fg="#333333", hover_bg="#EEEEEE", width=None, height=None, **kwargs):
        super().__init__(parent, text=text, bg=bg, fg=fg, cursor="hand2", **kwargs)
        self.bg_normal = bg
        self.bg_hover = hover_bg
        self.command = command
        
        if width: self.configure(width=width)
        # Label的高度单位是字符行数，这里为了微调通常结合pack/grid的pady
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def on_enter(self, e):
        self.configure(bg=self.bg_hover)

    def on_leave(self, e):
        self.configure(bg=self.bg_normal)

    def on_click(self, e):
        if self.command:
            self.command()

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_COLOR)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

class ExcelLikeConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Migoto GI 纹理转换器")
        self.root.geometry("1100x750")
        self.root.configure(bg=BG_COLOR)

        # --- Header ---
        header_frame = tk.Frame(root, bg=HEADER_BG, height=55)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="输入 (Input)", bg=HEADER_BG, fg=HEADER_FG, font=("Microsoft YaHei", 11, "bold")).place(relx=0.05, rely=0.5, anchor="w")
        tk.Label(header_frame, text="结果 (Output)", bg=HEADER_BG, fg=HEADER_FG, font=("Microsoft YaHei", 11, "bold")).place(relx=0.5, rely=0.5, anchor="w")
        
        # 顶部清空按钮
        self.btn_clear_all = ModernButton(header_frame, text="清空所有", bg=BTN_CLEAR_BG, fg="white", hover_bg=BTN_CLEAR_HOVER, 
                                          font=("Microsoft YaHei", 9), command=self.clear_all)
        self.btn_clear_all.pack(side=tk.RIGHT, padx=20, pady=12, ipadx=10, ipady=3) # ipad用于增加按钮内边距

        # --- 滚动区域 ---
        self.scroll_container = ScrollableFrame(root)
        self.scroll_container.pack(fill="both", expand=True)
        self.inner_frame = self.scroll_container.scrollable_frame

        self.rows = []
        
        tk.Frame(self.inner_frame, height=10, bg=BG_COLOR).pack(fill=tk.X)
        self.add_row()

    def add_row(self, event=None):
        row_idx = len(self.rows) + 1 
        
        # 卡片
        card_frame = tk.Frame(self.inner_frame, bg=CARD_BG, bd=0)
        card_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # 装饰条
        tk.Frame(card_frame, bg=ACCENT_COLOR, width=4).pack(side=tk.LEFT, fill=tk.Y)

        # 序号
        tk.Label(card_frame, text=f"{row_idx:02d}", bg=CARD_BG, fg="#999", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=(12, 8), anchor="n", pady=15)

        # 内容区
        content_frame = tk.Frame(card_frame, bg=CARD_BG)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.columnconfigure(2, weight=0)

        # 1. 输入容器
        input_container = tk.Frame(content_frame, bg=INPUT_BORDER, bd=1)
        input_container.grid(row=0, column=0, sticky="nsew", padx=10)
        
        # 粘贴按钮 (自定义样式)
        btn_paste = ModernButton(input_container, text="粘贴", bg=BTN_PASTE_BG, fg="#4C566A", hover_bg=BTN_PASTE_HOVER, 
                                 width=6, font=("Microsoft YaHei", 8))
        btn_paste.pack(side=tk.RIGHT, fill=tk.Y, padx=0, pady=0)
        
        txt_input = tk.Text(input_container, height=5, width=30, font=TEXT_FONT, bg="white", relief="flat", wrap=tk.WORD, undo=True)
        txt_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)

        # 2. 输出容器
        output_container = tk.Frame(content_frame, bg=INPUT_BORDER, bd=1)
        output_container.grid(row=0, column=1, sticky="nsew", padx=10)

        txt_output = tk.Text(output_container, height=5, width=30, font=TEXT_FONT, bg="#FAFAFA", fg="#333", relief="flat", wrap=tk.WORD)
        txt_output.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # 3. 复制按钮 (自定义样式)
        # 使用Frame来包装一下，方便控制大小和对齐
        btn_frame = tk.Frame(content_frame, bg=CARD_BG)
        btn_frame.grid(row=0, column=2, sticky="n", padx=5, pady=0)
        
        btn_copy = ModernButton(btn_frame, text="复制", bg=BTN_COPY_BG, fg=BTN_COPY_FG, hover_bg=BTN_COPY_HOVER,
                                font=("Microsoft YaHei", 9), width=8)
        btn_copy.pack(ipady=5) # 增加垂直内边距让按钮高一点

        # 数据
        row_data = {
            'frame': card_frame,
            'input': txt_input,
            'output': txt_output
        }
        self.rows.append(row_data)

        # 事件
        btn_paste.command = lambda: self.clear_and_paste(row_data)
        btn_copy.command = lambda: self.copy_text(txt_output, btn_copy)
        
        txt_input.bind("<<Modified>>", lambda e, r=row_data: self.on_text_change(e, r))
        txt_input.bind("<KeyRelease>", lambda e, r=row_data: self.check_add_new_row(e, r))

    def clear_and_paste(self, row_data):
        try:
            content = self.root.clipboard_get()
            row_data['input'].delete("1.0", tk.END)
            row_data['input'].insert("1.0", content)
            self.perform_convert(row_data)
            self.check_add_new_row(None, row_data)
        except: pass

    def check_add_new_row(self, event, row_data):
        self.perform_convert(row_data)
        if row_data == self.rows[-1]:
            content = row_data['input'].get("1.0", tk.END).strip()
            if content: self.add_row()

    def on_text_change(self, event, row_data):
        row_data['input'].edit_modified(False)
        self.perform_convert(row_data)

    def perform_convert(self, row_data):
        input_text = row_data['input'].get("1.0", tk.END).strip()
        result = self.convert_logic(input_text)
        out_widget = row_data['output']
        if out_widget.get("1.0", tk.END).strip() != result.strip():
            out_widget.delete("1.0", tk.END)
            out_widget.insert("1.0", result)

    def copy_text(self, text_widget, btn_widget):
        content = text_widget.get("1.0", tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            orig_text = btn_widget.cget("text")
            orig_bg = btn_widget.cget("bg")
            
            btn_widget.configure(text="已复制", bg="#8FBCBB") # 成功色
            self.root.after(1000, lambda: btn_widget.configure(text=orig_text, bg=orig_bg))
        else:
            messagebox.showinfo("提示", "内容为空")

    def clear_all(self):
        for row in self.rows: row['frame'].destroy()
        self.rows = []
        self.add_row()

    # --- 逻辑 ---
    def parse_ini_block(self, text):
        data = {}
        for line in text.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                data[key.strip().lower()] = value.strip()
        return data

    def extract_value(self, val_str):
        return val_str[4:].strip() if val_str.lower().startswith('ref ') else val_str

    def convert_logic(self, block_text):
        if not block_text: return ""
        data = self.parse_ini_block(block_text)
        run = data.get('run', '').lower()
        
        if 'orfix\\orfix' in run or 'orfix\\nnfix' in run:
            t0, t1, t2 = data.get('ps-t0', ''), data.get('ps-t1', ''), data.get('ps-t2', '')
            res = []
            if 'orfix\\orfix' in run:
                if t1: res.append(f"Resource\\TSR\\Diffuse = ref {t1}")
                if t2: res.append(f"Resource\\TSR\\Lightmap = ref {t2}")
                if t0: res.append(f"Resource\\TSR\\Normalmap = ref {t0}")
            elif 'orfix\\nnfix' in run:
                if t0: res.append(f"Resource\\TSR\\Diffuse = ref {t0}")
                if t1: res.append(f"Resource\\TSR\\Lightmap = ref {t1}")
            res.append("Run = CommandList\\TSR\\SetTextures")
            return "\n".join(res)

        elif 'tsr\\settextures' in run:
            d = self.extract_value(data.get('resource\\tsr\\diffuse', ''))
            l = self.extract_value(data.get('resource\\tsr\\lightmap', ''))
            n = self.extract_value(data.get('resource\\tsr\\normalmap', ''))
            res = []
            if n:
                res.extend([f"ps-t0 = {n}", f"ps-t1 = {d}", f"ps-t2 = {l}", "run = Commandlist\\Global\\ORFix\\ORFix"])
            else:
                res.extend([f"ps-t0 = {d}", f"ps-t1 = {l}", "run = Commandlist\\Global\\ORFix\\NNFix"])
            return "\n".join(res)
        return ""

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelLikeConverter(root)
    root.mainloop()