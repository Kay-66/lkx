import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox

class DateComponent(ttk.Frame):
    def __init__(self, master, date=None, command=None, datetime_str=None, component_id=None, on_delete=None, **kwargs):
        super().__init__(master, **kwargs)
        self.date = date or datetime.now()
        self.command = command
        self.datetime_str = datetime_str or self.date.strftime("%Y年%m月%d日 %H:%M:%S")
        self.component_id = component_id
        self.on_delete = on_delete
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure(
            'Component.TFrame',
            background='#F5F5F5',
            relief='solid',
            borderwidth=1
        )
        self.style.configure(
            'Date.TLabel',
            font=('微软雅黑', 11),
            background='#F5F5F5',
            foreground='#333333'
        )
        
    def create_widgets(self):
        self.configure(style='Component.TFrame', padding=(10, 5))
        
        # 创建可��击的框架
        self.clickable_frame = ttk.Frame(self, style='Component.TFrame')
        self.clickable_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左侧框架用于日期显示
        left_frame = ttk.Frame(self.clickable_frame, style='Component.TFrame')
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 显示完整的日期时间
        self.date_label = ttk.Label(
            left_frame,
            text=self.datetime_str,
            style='Date.TLabel'
        )
        self.date_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 箭头标签
        self.arrow_label = ttk.Label(
            left_frame,
            text="→",
            style='Date.TLabel'
        )
        self.arrow_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 删除按钮放在最右侧
        self.delete_button = ttk.Button(
            self.clickable_frame,
            text="×",
            width=3,
            command=self.confirm_delete
        )
        self.delete_button.pack(side=tk.RIGHT, padx=(0, 50))  # 大幅增加右侧间距
        
        # 绑定点击事件
        left_frame.bind('<Button-1>', self.on_click)
        self.date_label.bind('<Button-1>', self.on_click)
        self.arrow_label.bind('<Button-1>', self.on_click)
        
        # 绑定鼠标悬停事件
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
    def on_click(self, event):
        if self.command:
            self.command(self.date)
        
    def on_enter(self, event):
        self.style.configure(
            'Component.TFrame',
            background='#E8E8E8'
        )
        
    def on_leave(self, event):
        self.style.configure(
            'Component.TFrame',
            background='#F5F5F5'
        )
        
    def confirm_delete(self):
        """确认删除对话框"""
        if self.on_delete:
            result = messagebox.askquestion(
                "确认删除",
                "确定要删除这个时间组件吗？\n此操作将删除该组件的所有记录，且不可撤销。",
                icon='warning'
            )
            if result == 'yes':
                self.on_delete(self)
