import tkinter as tk
from interface import MainApplication
from datetime import datetime
from tkinter import ttk

def main():
    root = tk.Tk()
    
    try:
        print("开始创建全局样式...")
        # 创建全局样式
        style = ttk.Style()
        style.configure(
            'Tooltip.TLabel',
            background='#FFFFCC',  # 淡黄色背景
            foreground='#333333',  # 深灰色文字
            font=('微软雅黑', 10),  # 稍微大一点的字体
            relief='solid',
            borderwidth=1,
            padding=(10, 5)  # 增加内边距
        )
        print("全局样式创建完成")
        
    except Exception as e:
        print(f"创建全局样式时出错: {e}")
    
    # 设置窗口透明度（可选）
    root.attributes('-alpha', 0.95)
    
    root.title("时间开销 · 体验生命")
    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def on_closing():
        root.destroy()  # 确保窗口正确关闭
        
    root.protocol("WM_DELETE_WINDOW", on_closing)  # 绑定关闭事件
    
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()
