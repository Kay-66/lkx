import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta
from components import DateComponent
from data_manager import DataManager
import json
import os

class MainApplication(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.data_manager = DataManager()
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()
        self.load_saved_components()  # 加载保存的组件
        
        # 绑定窗口关闭事件
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        try:
            # 顶部标题
            self.title_frame = ttk.Frame(self)
            self.title_frame.pack(fill=tk.X, pady=10)
            
            self.title_label = ttk.Label(
                self.title_frame,
                text="时间开销 · 体验生命",
                font=('微软雅黑', 16, 'bold')
            )
            self.title_label.pack()
            
            # 创建滚动区域
            self.canvas = tk.Canvas(self, bg='white')
            self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
            self.scrollable_frame = ttk.Frame(self.canvas)
            
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            )
            
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            
            self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 添加按钮
            self.add_button = ttk.Button(
                self,
                text="+",
                width=3,
                command=self.add_component
            )
            self.add_button.place(relx=0.95, rely=0.95, anchor="se")
            
            # 修改提示标签的样式
            self.tooltip = tk.Label(
                self,
                text="一切终将归零，除了生死，都是小事！",
                bg='#FFFFCC',
                fg='#333333',
                font=('微软雅黑', 10),
                relief='solid',
                borderwidth=1,
                padx=10,
                pady=5
            )
            self.tooltip.lift()  # 确保提示框显示在最上层
            
            # 绑定鼠标事件
            self.add_button.bind('<Enter>', self.show_tooltip)
            self.add_button.bind('<Leave>', self.hide_tooltip)
            
            # 添加批量操作框架
            self.batch_frame = ttk.Frame(self)
            self.batch_frame.pack(fill=tk.X, padx=20, pady=5)
            
            # 批量删除按钮
            self.batch_delete_button = ttk.Button(
                self.batch_frame,
                text="批量删除",
                command=self.start_batch_delete,
                width=10
            )
            self.batch_delete_button.pack(side=tk.RIGHT)
            
            # 确认删除按钮（初始隐藏）
            self.confirm_delete_button = ttk.Button(
                self.batch_frame,
                text="确认删除",
                command=self.confirm_batch_delete,
                width=10
            )
            
            # 取消按钮（初始隐藏）
            self.cancel_delete_button = ttk.Button(
                self.batch_frame,
                text="取消",
                command=self.cancel_batch_delete,
                width=10
            )
            
            # 全选复选框（初始隐藏）
            self.select_all_var = tk.BooleanVar()
            self.select_all_checkbox = ttk.Checkbutton(
                self.batch_frame,
                text="全选",
                variable=self.select_all_var,
                command=self.toggle_all_selections
            )
            
            # 用于存储组件和其复选框状态的字典
            self.component_selections = {}
            self.is_batch_deleting = False
            
        except Exception as e:
            print(f"创建界面时出错: {e}")
        
    def show_tooltip(self, event):
        """显示提示文本"""
        button_x = self.add_button.winfo_x()
        button_y = self.add_button.winfo_y()
        tooltip_x = button_x - self.tooltip.winfo_reqwidth() + 30
        tooltip_y = button_y - 40  # 显示在按钮上方
        self.tooltip.place(x=tooltip_x, y=tooltip_y)
    
    def hide_tooltip(self, event):
        """隐藏提示文本"""
        self.tooltip.place_forget()
    
    def add_component(self):
        """添加新组件"""
        current_datetime = datetime.now()
        date_str = current_datetime.strftime("%Y年%m月%d日 %H:%M:%S")
        component_id = current_datetime.strftime("%Y%m%d%H%M%S")
        
        self.create_component(component_id, date_str, current_datetime)
        self.save_components()  # 保存组件信息
        
    def create_component(self, component_id, date_str, date):
        """创建组件"""
        try:
            # 检查组件ID是否已存在
            if component_id in self.component_selections:
                return None
            
            # 创建组件框架
            component_frame = ttk.Frame(self.scrollable_frame)
            component_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # 创建内容框架
            content_frame = ttk.Frame(component_frame)
            content_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # 添加复选框（初始隐藏）
            select_var = tk.BooleanVar()
            checkbox = ttk.Checkbutton(
                component_frame,
                variable=select_var,
                command=self.update_select_all_state
            )
            
            # 创建日期组件，直接传递 data_manager
            component = DateComponent(
                content_frame,
                date=date,
                command=lambda d: self.open_detail_view(d, component_id),
                datetime_str=date_str,
                component_id=component_id,
                on_delete=self.delete_component,
                data_manager=self.data_manager  # 添加这一行
            )
            component.pack(fill=tk.X, expand=True)
            
            # 保存组件和复选框状态的引用
            self.component_selections[component_id] = {
                'component': component,
                'frame': component_frame,
                'checkbox': select_var,
                'checkbox_widget': checkbox
            }
            
            return component
            
        except Exception as e:
            print(f"创建组件时出错: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    def open_detail_view(self, date, component_id):
        """打开详细视图并隐藏主窗口"""
        self.master.withdraw()
        detail_window = DetailView(self, date, component_id)
        detail_window.protocol("WM_DELETE_WINDOW", lambda: self.on_detail_close(detail_window))

    def on_detail_close(self, detail_window):
        """处理详细视图关闭事件"""
        detail_window.destroy()
        self.master.deiconify()  # 重显示主窗口

    def delete_component(self, component):
        """删除组件"""
        try:
            # 添加确认对话框
            result = messagebox.askquestion(
                "确认删除",
                "确定要删除这个组件吗？\n删除后将无法恢复。",
                icon='warning'
            )
            
            if result != 'yes':
                return
            
            # 删除数据文件
            file_path = os.path.join(
                self.data_manager.data_dir,
                f"{component.component_id}.json"
            )
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # 删除备注文件
            note_file = os.path.join(
                self.data_manager.data_dir,
                f"{component.component_id}_note.txt"
            )
            if os.path.exists(note_file):
                os.remove(note_file)
            
            # 从选择字典中移除
            if component.component_id in self.component_selections:
                self.component_selections.pop(component.component_id)
            
            # 销毁组件
            component.destroy()
            
        except Exception as e:
            print(f"删除组件时出错: {e}")
            messagebox.showerror("错误", f"删除组件时出错：{str(e)}")

    def save_components(self):
        """保存所有组件信息"""
        try:
            components_data = []
            children = self.scrollable_frame.winfo_children()
            
            for frame in children:
                if isinstance(frame, ttk.Frame):  # 检查是否是组件框架
                    # 在框架中查找 DateComponent
                    for child in frame.winfo_children():
                        if isinstance(child, ttk.Frame):  # 内容框架
                            for subchild in child.winfo_children():
                                if isinstance(subchild, DateComponent):
                                    component = subchild
                                    components_data.append({
                                        'component_id': component.component_id,
                                        'date_str': component.datetime_str,
                                        'date': component.date.strftime("%Y-%m-%d %H:%M:%S")
                                    })
                                    break
            
            self.data_manager.save_components(components_data)
            
        except Exception as e:
            print(f"保存组件时出错: {e}")
        
    def load_saved_components(self):
        """��载保存的组件"""
        try:
            # 空现有组件和选择状态
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            self.component_selections.clear()
            
            # 加载组件数据
            components_data = self.data_manager.load_components()
            for comp_data in components_data:
                date = datetime.strptime(comp_data['date'], "%Y-%m-%d %H:%M:%S")
                self.create_component(
                    comp_data['component_id'],
                    comp_data['date_str'],
                    date
                )
                
        except Exception as e:
            print(f"加载组件时出错: {e}")
        
    def on_closing(self):
        """窗口关闭时的处理"""
        self.save_components()  # 保存组件信息
        self.master.destroy()

    def toggle_all_selections(self):
        """切换全选状态"""
        is_selected = self.select_all_var.get()
        for data in self.component_selections.values():
            data['checkbox'].set(is_selected)
            
    def update_select_all_state(self):
        """更新全选复选框状态"""
        all_selected = all(
            data['checkbox'].get() 
            for data in self.component_selections.values()
        )
        self.select_all_var.set(all_selected)
        
    def confirm_batch_delete(self):
        """确认批量删除"""
        selected_components = [
            comp_id for comp_id, data in self.component_selections.items()
            if data['checkbox'].get()
        ]
        
        if not selected_components:
            messagebox.showinfo("提示", "请先选择要删除的组件")
            return
            
        result = messagebox.askquestion(
            "确认删除",
            f"确定要删除选中的 {len(selected_components)} 个组件吗？\n此操作不可撤销。",
            icon='warning'
        )
        
        if result == 'yes':
            self.batch_delete_components(selected_components)
            
    def batch_delete_components(self, component_ids):
        """执行批量删除"""
        try:
            for comp_id in component_ids:
                if comp_id in self.component_selections:
                    # 删除数据文件
                    file_path = os.path.join(
                        self.data_manager.data_dir,
                        f"{comp_id}.json"
                    )
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    
                    # 从界面除组件
                    self.component_selections[comp_id]['frame'].destroy()
                    # 从选择字典中移除
                    del self.component_selections[comp_id]
            
            # 保存更新后的组件信息
            self.save_components()
            messagebox.showinfo("成功", "已删除选中的组件")
            
        except Exception as e:
            messagebox.showerror("错误", f"批量删除组件时出错：{str(e)}")

    def start_batch_delete(self):
        """开始批量删除模式"""
        try:
            self.is_batch_deleting = True
            
            # 隐藏批量删除钮，显示确认和取消按钮
            self.batch_delete_button.pack_forget()
            self.confirm_delete_button.pack(side=tk.RIGHT, padx=5)
            self.cancel_delete_button.pack(side=tk.RIGHT, padx=5)
            self.select_all_checkbox.pack(side=tk.RIGHT, padx=10)
            
            # 显示所有复选框
            for comp_id, data in self.component_selections.items():
                checkbox = data['checkbox_widget']
                if checkbox.winfo_exists():
                    checkbox.pack(side=tk.LEFT, padx=5)
                    checkbox.lift()
                
        except Exception as e:
            print(f"动量���除模式时出错: {e}")

    def cancel_batch_delete(self):
        """取消批量删除模式"""
        self.is_batch_deleting = False
        
        # 恢复按钮显示状态
        self.confirm_delete_button.pack_forget()
        self.cancel_delete_button.pack_forget()
        self.select_all_checkbox.pack_forget()
        self.batch_delete_button.pack(side=tk.RIGHT)
        
        # 隐藏所有复选框并重置选择状态
        for data in self.component_selections.values():
            data['checkbox_widget'].pack_forget()
            data['checkbox'].set(False)
        self.select_all_var.set(False)

    def update_component_statistics(self, component_id):
        """更新指定组件的统计信息"""
        for widget in self.scrollable_frame.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ttk.Frame):  # 内容框架
                    for subchild in child.winfo_children():
                        if isinstance(subchild, DateComponent):
                            if subchild.component_id == component_id:
                                subchild.update_statistics()
                                return

class DetailView(tk.Toplevel):
    def __init__(self, master, date, component_id):
        super().__init__(master)
        self.master = master
        self.date = date
        self.component_id = component_id
        self.data_manager = master.data_manager
        self.records = []
        self.setup_window()
        self.create_widgets()
        self.load_records()

    def setup_window(self):
        """设置窗口属性"""
        self.title("详细记录")
        window_width = 800
        window_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建样式
        self.style = ttk.Style()
        self.style.configure('DetailView.TFrame', background='white')
        self.style.configure('Header.TLabel', font=('微软雅黑', 14, 'bold'))
        
    def create_widgets(self):
        """创建界面控件"""
        # 顶部架
        self.top_frame = ttk.Frame(self, style='DetailView.TFrame')
        self.top_frame.pack(fill=tk.X, pady=10)
        
        # 返回按钮
        self.back_button = ttk.Button(
            self.top_frame,
            text="←",
            width=3,
            command=self.destroy
        )
        self.back_button.pack(side=tk.LEFT, padx=10)
        
        # 日期显示
        self.date_label = ttk.Label(
            self.top_frame,
            text=self.date.strftime("%Y年%m月%d日"),
            style='Header.TLabel'
        )
        self.date_label.pack(side=tk.LEFT, padx=20)
        
        # 创建主内容区域
        self.create_main_content()
        
        # 添加按钮
        self.add_button = ttk.Button(
            self,
            text="+",
            width=3,
            command=self.show_add_dialog
        )
        self.add_button.place(relx=0.95, rely=0.95, anchor="se")
        
        # 创建提示标签
        self.tooltip = tk.Label(
            self,
            text="一切终将归零，除了生死，都是小事！",
            bg='#FFFFCC',
            fg='#333333',
            font=('微软雅黑', 10),
            relief='solid',
            borderwidth=1,
            padx=10,
            pady=5
        )
        self.tooltip.lift()  # 确保提示框显示在最上层
        
        # 绑定鼠标事件
        self.add_button.bind('<Enter>', self.show_tooltip)
        self.add_button.bind('<Leave>', self.hide_tooltip)
        
    def create_main_content(self):
        """创建主内容区域"""
        self.content_frame = ttk.Frame(self, style='DetailView.TFrame')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 添加备注框架
        note_frame = ttk.Frame(self.content_frame)
        note_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        ttk.Label(
            note_frame,
            text="对自己说点什么：",
            font=('微软雅黑', 9)
        ).pack(side=tk.LEFT)
        
        self.note_entry = ttk.Entry(note_frame)
        self.note_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.note_entry.bind('<Return>', self.save_note)  # 按回车保存
        self.note_entry.bind('<FocusOut>', self.save_note)  # 失去焦点时保存
        
        # 加载已有备注
        self.load_note()
        
        # 创建滚动区域
        self.canvas = tk.Canvas(self.content_frame, bg='white')
        self.scrollbar = ttk.Scrollbar(
            self.content_frame,
            orient=tk.VERTICAL,
            command=self.canvas.yview
        )
        
        self.scrollable_frame = ttk.Frame(self.canvas, style='DetailView.TFrame')
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def show_add_dialog(self):
        """显示添加记录对话框"""
        dialog = AddRecordDialog(self)
        dialog.wait_window()
        # 对话框关闭后，更新主界面的组件统计
        main_app = self.master
        if isinstance(main_app, MainApplication):
            for frame in main_app.scrollable_frame.winfo_children():
                if isinstance(frame, ttk.Frame):
                    for child in frame.winfo_children():
                        if isinstance(child, ttk.Frame):
                            for subchild in child.winfo_children():
                                if isinstance(subchild, DateComponent):
                                    if subchild.component_id == self.component_id:
                                        subchild.update_statistics()
                                        break

    def destroy(self):
        """写destroy方法"""
        self.master.master.deiconify()  # 显示主窗
        super().destroy()
        
    def get_file_path(self):
        """获当前组件的数据件路径"""
        return os.path.join(
            self.data_manager.data_dir,
            f"{self.component_id}.json"
        )

    def load_records(self):
        """加载记录"""
        try:
            file_path = self.get_file_path()
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
                # 确保记录按时间戳排序
                self.records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            else:
                self.records = []
            self.display_records()
        except Exception as e:
            print(f"Error loading records: {e}")
            messagebox.showerror("错误", f"加载记录时出错：{str(e)}")
            self.records = []
            self.display_records()

    def display_records(self):
        """显示所有记录"""
        # 清空现有显示
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # 显示每条记录
        for record in self.records:
            self.create_record_widget(record)
        
    def create_record_widget(self, record):
        """创建单条记录的显示组件"""
        try:
            # 创建录架
            record_frame = ttk.Frame(self.scrollable_frame, style='Record.TFrame')
            record_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # 主内容框架
            main_frame = ttk.Frame(record_frame)
            main_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # 创建两列布局
            left_frame = ttk.Frame(main_frame)
            left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
            
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(side=tk.RIGHT, anchor='ne')
            
            # 编辑和删除按钮
            edit_button = ttk.Button(
                button_frame,
                text="编辑",
                width=6,
                command=lambda: self.edit_record(record, record_frame)
            )
            edit_button.pack(side=tk.TOP, pady=2)
            
            delete_button = ttk.Button(
                button_frame,
                text="删除",
                width=6,
                command=lambda: self.confirm_delete(record, record_frame)
            )
            delete_button.pack(side=tk.TOP, pady=2)
            
            # 内容部分（在左框架中）
            # 第一行：标题行
            title_frame = ttk.Frame(left_frame)
            title_frame.pack(fill=tk.X, pady=(0, 5))
            
            # 颜色标
            color_frame = ttk.Frame(title_frame, width=20, height=20)
            color_frame.pack(side=tk.LEFT, padx=(0, 10))
            color_value = record.get('颜色标记', 'gray')
            color_canvas = tk.Canvas(color_frame, width=20, height=20, bg=color_value)
            color_canvas.pack()
            
            # 活动名称
            ttk.Label(
                title_frame,
                text=record.get('活动', '未命名活动'),
                style='RecordTitle.TLabel'
            ).pack(side=tk.LEFT)
            
            # 第二行：时间信息
            time_frame = ttk.Frame(left_frame)
            time_frame.pack(fill=tk.X, pady=2)
            
            actual_time = record.get('实际时间', '0')
            estimated_time = record.get('预估时间', '0')
            time_info = f"时间段: {record.get('时间段', '未设置')} | 实际时间: {actual_time}分钟 | 预估时间: {estimated_time}分钟"
            ttk.Label(
                time_frame,
                text=time_info,
                style='RecordContent.TLabel'
            ).pack(anchor=tk.W)
            
            # 第三行：体验感和类别
            info_frame = ttk.Frame(left_frame)
            info_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(
                info_frame,
                text=f"体验感: {record.get('体验感', '0')} | 类别: {record.get('类别', '未分类')}",
                style='RecordContent.TLabel'
            ).pack(anchor=tk.W)
            
            # 第四行：优化建议（添加动换行）
            suggestion = record.get('优化建议', '').strip()
            if suggestion:
                suggestion_frame = ttk.Frame(left_frame)
                suggestion_frame.pack(fill=tk.X, pady=2)
                ttk.Label(
                    suggestion_frame,
                    text=f"优化建议: {suggestion}",
                    style='RecordContent.TLabel',
                    wraplength=600  # 自动换行，但保留较大宽度
                ).pack(anchor=tk.W, fill=tk.X)
            
            # 时间戳
            if 'timestamp' in record:
                timestamp_frame = ttk.Frame(left_frame)
                timestamp_frame.pack(fill=tk.X, pady=(5, 0))
                ttk.Label(
                    timestamp_frame,
                    text=f"记录时间: {record['timestamp']}",
                    style='RecordContent.TLabel',
                    foreground='gray'
                ).pack(side=tk.RIGHT)
                
        except Exception as e:
            print(f"Error displaying record: {e}")
        
    def confirm_delete(self, record, record_frame):
        """确认删除对话框"""
        result = messagebox.askquestion(
            "确认删除",
            "确定要删除这条记录吗？\n此操作不可撤。",
            icon='warning'
        )
        
        if result == 'yes':
            self.delete_record(record, record_frame)

    def delete_record(self, record, record_frame):
        """删除记录"""
        try:
            # 从数据文件中删除记录
            self.records = [r for r in self.records if r.get('timestamp') != record.get('timestamp')]
            
            # 保存新后的记录
            file_path = self.get_file_path()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
            
            # 从界面移除记录组件
            record_frame.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"删除记录时出错：{str(e)}")

    def edit_record(self, record, record_frame):
        """编辑记录"""
        dialog = EditRecordDialog(self, record)
        dialog.wait_window()
        
        # 如果记录被更新，刷新显示
        if hasattr(dialog, 'updated') and dialog.updated:
            self.load_records()
        
    def save_record(self):
        """保存记录"""
        try:
            data = {}
            for label, widget in self.entries.items():
                if isinstance(widget, tk.Text):
                    data[label] = widget.get("1.0", tk.END).strip()
                elif isinstance(widget, tk.StringVar):
                    data[label] = widget.get()
                else:
                    data[label] = widget.get()
            
            # 添加时间戳
            data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 加载现有记录
            file_path = self.get_file_path()
            records = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            
            # 添加新记录
            records.append(data)
            
            # 保存记录
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            
            # 更新主界面组件的统计信息
            for widget in self.master.scrollable_frame.winfo_children():
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):  # 内容框架
                        for subchild in child.winfo_children():
                            if isinstance(subchild, DateComponent):
                                if subchild.component_id == self.component_id:
                                    subchild.update_statistics()
                                    break
            
            # 立即刷新当前视图的记录显示
            self.load_records()
            
            # 清空输入框
            self.clear_inputs()
            
        except Exception as e:
            print(f"保存记录时出错: {e}")
            import traceback
            traceback.print_exc()

    def clear_inputs(self):
        """清空所有输入框"""
        for widget in self.entries.values():
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            elif isinstance(widget, tk.StringVar):
                widget.set("")
            else:
                widget.delete(0, tk.END)

    def show_tooltip(self, event):
        """显示提示文本"""
        button_x = self.add_button.winfo_x()
        button_y = self.add_button.winfo_y()
        tooltip_x = button_x - self.tooltip.winfo_reqwidth() + 30
        tooltip_y = button_y - 40  # 显示在按钮上方
        self.tooltip.place(x=tooltip_x, y=tooltip_y)
    
    def hide_tooltip(self, event):
        """隐藏提示文本"""
        self.tooltip.place_forget()

    def save_note(self, event=None):
        """保存备注"""
        new_note = self.note_entry.get().strip()
        note_file = os.path.join(
            self.data_manager.data_dir,
            f"{self.component_id}_note.txt"
        )
        with open(note_file, 'w', encoding='utf-8') as f:
            f.write(new_note)
            
        # 更新主界面显示的备注
        main_app = self.master
        if isinstance(main_app, MainApplication):
            for frame in main_app.scrollable_frame.winfo_children():
                if isinstance(frame, ttk.Frame):
                    for child in frame.winfo_children():
                        if isinstance(child, ttk.Frame):
                            for subchild in child.winfo_children():
                                if isinstance(subchild, DateComponent):
                                    if subchild.component_id == self.component_id:
                                        subchild.update_note(new_note)
                                        break

    def load_note(self):
        """加载备注"""
        try:
            note_file = os.path.join(
                self.data_manager.data_dir,
                f"{self.component_id}_note.txt"
            )
            if os.path.exists(note_file):
                with open(note_file, 'r', encoding='utf-8') as f:
                    note = f.read().strip()
                    self.note_entry.delete(0, tk.END)
                    self.note_entry.insert(0, note)
        except Exception as e:
            print(f"加载备注时出错: {e}")

class AddRecordDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("添加记录")
        self.setup_dialog()
        self.create_form()
        
    def setup_dialog(self):
        """���置对话框属性"""
        self.geometry("400x600")
        self.resizable(False, False)
        self.transient(self.master)
        self.grab_set()
        
    def create_form(self):
        """建表单"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 定义表单项（确保键名一）
        self.fields = [
            ("活动", "entry"),
            ("体验感", "entry"),
            ("时间段", "combobox"),
            ("实际时间", "entry"),
            ("预估时间", "entry"),
            ("优化建议", "text"),
            ("颜色标记", "radio"),
            ("类别", "combobox")
        ]
        
        # 创建表单控件
        self.entries = {}
        for i, (label, field_type) in enumerate(self.fields):
            # 标签显示
            display_label = label
            if label == "体验感":
                display_label = "体验感 (0-10)"
            elif label == "实际时间":
                display_label = "实际时间（分钟）"
            elif label == "预估时间":
                display_label = "预估时间（分钟）"
                
            ttk.Label(main_frame, text=display_label).grid(row=i, column=0, sticky=tk.W, pady=5)
            
            if field_type == "entry":
                self.entries[label] = ttk.Entry(main_frame, width=30)
                self.entries[label].grid(row=i, column=1, sticky=tk.W, pady=5)
                
            elif field_type == "combobox":
                if label == "时间段":
                    times = [f"{i:02d}:00-{i+1:02d}:00" for i in range(24)]
                    self.entries[label] = ttk.Combobox(main_frame, values=times, width=27)
                elif label == "类别":
                    categories = ["学习", "健康", "投资", "娱乐", "出勤", "生活"]
                    self.entries[label] = ttk.Combobox(main_frame, values=categories, width=27)
                self.entries[label].grid(row=i, column=1, sticky=tk.W, pady=5)
                
            elif field_type == "text":
                self.entries[label] = tk.Text(main_frame, width=30, height=4)
                self.entries[label].grid(row=i, column=1, sticky=tk.W, pady=5)
                
            elif field_type == "radio":
                frame = ttk.Frame(main_frame)
                frame.grid(row=i, column=1, sticky=tk.W, pady=5)
                self.color_var = tk.StringVar(value="green")
                colors = [("绿色", "green"), ("黄色", "yellow"), ("红色", "red")]
                for j, (text, value) in enumerate(colors):
                    ttk.Radiobutton(
                        frame,
                        text=text,
                        value=value,
                        variable=self.color_var
                    ).pack(side=tk.LEFT, padx=5)
                self.entries[label] = self.color_var
        
        # 添加按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(self.fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="确定", command=self.save_record).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.destroy).pack(side=tk.LEFT, padx=10)
        
    def save_record(self):
        """保存记录"""
        try:
            # 1. 收集数据
            data = {}
            for label, widget in self.entries.items():
                if isinstance(widget, tk.Text):
                    data[label] = widget.get("1.0", tk.END).strip()
                elif isinstance(widget, tk.StringVar):
                    data[label] = widget.get()
                else:
                    data[label] = widget.get()
            
            # 2. 保存记录
            data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_path = self.master.get_file_path()
            
            records = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    records = json.load(f)
            
            records.append(data)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            
            # 3. 刷新当前视图
            self.master.load_records()
            
            # 4. 关闭对话框
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存记录时出错：{str(e)}")

    def clear_inputs(self):
        """清空所有输入框"""
        for widget in self.entries.values():
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            elif isinstance(widget, tk.StringVar):
                widget.set("")
            else:
                widget.delete(0, tk.END)

class EditRecordDialog(tk.Toplevel):
    def __init__(self, master, record):
        super().__init__(master)
        self.master = master
        self.record = record
        self.title("编辑记录")
        self.setup_dialog()
        self.create_form()
        self.load_record_data()
        
    def setup_dialog(self):
        """设置对话框属性"""
        self.geometry("400x600")
        self.resizable(False, False)
        self.transient(self.master)
        self.grab_set()
        
    def create_form(self):
        """创建表单"""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 定义表单项
        self.fields = [
            ("活动", "entry"),
            ("体验感", "entry"),
            ("时间段", "combobox"),
            ("实际时间", "entry"),
            ("预估时间", "entry"),
            ("优化建议", "text"),
            ("颜色标记", "radio"),
            ("类别", "combobox")
        ]
        
        # 创建表单控件
        self.entries = {}
        for i, (label, field_type) in enumerate(self.fields):
            # 标签显示
            display_label = label
            if label == "体验感":
                display_label = "体验感 (0-10)"
            elif label == "实际时间":
                display_label = "实际时间（分钟）"
            elif label == "预估时间":
                display_label = "预估时间（分钟）"
                
            ttk.Label(main_frame, text=display_label).grid(row=i, column=0, sticky=tk.W, pady=5)
            
            if field_type == "entry":
                self.entries[label] = ttk.Entry(main_frame, width=30)
                self.entries[label].grid(row=i, column=1, sticky=tk.W, pady=5)
                
            elif field_type == "combobox":
                if label == "时间段":
                    times = [f"{i:02d}:00-{i+1:02d}:00" for i in range(24)]
                    self.entries[label] = ttk.Combobox(main_frame, values=times, width=27)
                elif label == "类别":
                    categories = ["学习", "健康", "投资", "娱乐", "出���", "生活"]
                    self.entries[label] = ttk.Combobox(main_frame, values=categories, width=27)
                self.entries[label].grid(row=i, column=1, sticky=tk.W, pady=5)
                
            elif field_type == "text":
                self.entries[label] = tk.Text(main_frame, width=30, height=4)
                self.entries[label].grid(row=i, column=1, sticky=tk.W, pady=5)
                
            elif field_type == "radio":
                frame = ttk.Frame(main_frame)
                frame.grid(row=i, column=1, sticky=tk.W, pady=5)
                self.color_var = tk.StringVar(value=self.record.get('颜色标记', 'green'))
                colors = [("绿色", "green"), ("黄色", "yellow"), ("红色", "red")]
                for j, (text, value) in enumerate(colors):
                    ttk.Radiobutton(
                        frame,
                        text=text,
                        value=value,
                        variable=self.color_var
                    ).pack(side=tk.LEFT, padx=5)
                self.entries[label] = self.color_var
        
        # 添加按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(self.fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="保存", command=self.save_record).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.destroy).pack(side=tk.LEFT, padx=10)
        
    def load_record_data(self):
        """加载记录数据到表单"""
        for label, widget in self.entries.items():
            value = self.record.get(label, '')
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
                widget.insert("1.0", value)
            elif isinstance(widget, tk.StringVar):
                widget.set(value)
            else:
                widget.delete(0, tk.END)
                widget.insert(0, value)
                
    def save_record(self):
        """保存修改后的记录"""
        try:
            # 先确认是否要保存修改
            result = messagebox.askquestion(
                "确认修改",
                "确定要保存修改吗？",
                icon='question'
            )
            
            if result != 'yes':
                return
            
            # 获取所有输入的值
            data = {}
            for label, widget in self.entries.items():
                if isinstance(widget, tk.Text):
                    data[label] = widget.get("1.0", tk.END).strip()
                elif isinstance(widget, tk.StringVar):
                    data[label] = widget.get()
                else:
                    data[label] = widget.get()
            
            # 保存原有时间戳
            data['timestamp'] = self.record.get('timestamp', '')
            
            # 更新记录
            file_path = self.master.get_file_path()
            
            # 从文件中读取所有记录
            with open(file_path, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            # 更新对应的记录
            for i, r in enumerate(records):
                if r.get('timestamp') == data['timestamp']:
                    records[i] = data
                    break
            
            # 保存更新后的记录
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            
            # 更新主界面的统计信息
            for widget in self.master.master.scrollable_frame.winfo_children():
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):  # 内容框架
                        for subchild in child.winfo_children():
                            if isinstance(subchild, DateComponent):
                                if subchild.component_id == self.master.component_id:
                                    subchild.update_statistics()
                                    break
            
            self.updated = True
            # 刷新主界面显示
            self.master.load_records()
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存记录时出错：{str(e)}")
            print(f"Error saving record: {e}")

class DateComponent(ttk.Frame):
    def __init__(self, master, date, command, datetime_str, component_id, on_delete, data_manager):
        super().__init__(master)
        self.date = date
        self.datetime_str = datetime_str
        self.component_id = component_id
        self.command = command
        self.on_delete = on_delete
        self.data_manager = data_manager
        self.note = ""  # 添加备注属性
        
        self.create_widgets()
        self.load_note()  # 加载备注
        self.update_statistics()

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.X, expand=True)
        
        # 顶部框架（包含日期按钮、备注和删除按钮）
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=2)
        
        # 日期按钮
        self.date_button = ttk.Button(
            top_frame,
            text=self.datetime_str,
            command=lambda: self.command(self.date)
        )
        self.date_button.pack(side=tk.LEFT)
        
        # 备注标签
        self.note_label = ttk.Label(
            top_frame,
            text="",
            font=('微软雅黑', 9),
            foreground='#666666'
        )
        self.note_label.pack(side=tk.LEFT, padx=10)
        
        # 删除按钮
        delete_button = ttk.Button(
            top_frame,
            text="×",
            width=3,
            command=lambda: self.on_delete(self)
        )
        delete_button.pack(side=tk.RIGHT)
        
        # 加载备注
        self.load_note()
        
        # 统计信息框架
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=2)
        
        # 统计信息左侧框架
        left_stats = ttk.Frame(stats_frame)
        left_stats.pack(side=tk.LEFT, fill=tk.X)
        
        # 体验感平均值
        self.exp_avg_label = ttk.Label(
            left_stats,
            text="平均体验感: --",
            font=('微软雅黑', 9)
        )
        self.exp_avg_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
        
        # 统计信息右侧框架
        right_stats = ttk.Frame(stats_frame)
        right_stats.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 各类别时长统计
        categories = ["学习", "健康", "投资", "娱乐", "出勤", "生活"]
        self.time_labels = {}
        
        # 创建两行布局
        row1_frame = ttk.Frame(right_stats)
        row1_frame.pack(fill=tk.X)
        row2_frame = ttk.Frame(right_stats)
        row2_frame.pack(fill=tk.X)
        
        # 将类别分成两行显示
        for i, category in enumerate(categories):
            parent_frame = row1_frame if i < 3 else row2_frame
            self.time_labels[category] = ttk.Label(
                parent_frame,
                text=f"{category}: --",
                font=('微软雅黑', 9)
            )
            self.time_labels[category].pack(side=tk.LEFT, padx=5)

    def update_note(self, note):
        """更新备注显示"""
        self.note_label.configure(text=note)

    def load_note(self):
        """加载备注"""
        try:
            note_file = os.path.join(
                self.data_manager.data_dir,
                f"{self.component_id}_note.txt"
            )
            if os.path.exists(note_file):
                with open(note_file, 'r', encoding='utf-8') as f:
                    note = f.read().strip()
                    self.note_label.configure(text=note)
        except Exception as e:
            print(f"加载备注时出错: {e}")

    def update_statistics(self):
        """更新统计信息"""
        try:
            print(f"\n=== 开始更新组件统计信息 ===")
            print(f"组件ID: {self.component_id}")
            
            # 1. 读取数据
            file_path = os.path.join(
                self.data_manager.data_dir,
                f"{self.component_id}.json"
            )
            print(f"1. 数据文件路径: {file_path}")
            print(f"   文件是否存在: {os.path.exists(file_path)}")
            
            if not os.path.exists(file_path):
                print("   文件不存在，退出更新")
                return
                
            with open(file_path, 'r', encoding='utf-8') as f:
                records = json.load(f)
            print(f"2. 读取到 {len(records)} 条记录")
            
            # 2. 更新标签
            print("3. 开始更新显示")
            print("   3.1 更新体验感")
            exp_values = []
            for r in records:
                exp_str = r.get('体验感', '').strip()
                if exp_str:
                    try:
                        exp_values.append(float(exp_str))
                    except ValueError:
                        continue
            
            if exp_values:
                avg_exp = sum(exp_values) / len(exp_values)
                print(f"   平均体验感: {avg_exp:.2f}")
                self.exp_avg_label.configure(text=f"平均体验感: {avg_exp:.2f}")
                self.exp_avg_label.pack(side=tk.TOP, anchor=tk.W, padx=5)
            
            print("   3.2 更新时长统计")
            for category in ["学习", "健康", "投资", "娱乐", "出勤", "生活"]:
                total_time = sum(
                    int(r.get('实际时间', 0))
                    for r in records
                    if r.get('类别') == category and r.get('实际时间', '').strip()
                )
                
                if total_time > 0:
                    print(f"   {category}: {total_time}分钟")
                    time_text = (
                        f"{total_time // 60}小时{total_time % 60}分钟"
                        if total_time >= 60
                        else f"{total_time}分钟"
                    )
                    self.time_labels[category].configure(text=f"{category}: {time_text}")
                    self.time_labels[category].pack(side=tk.LEFT, padx=5)
            
            print("=== 统计信息更新完成 ===\n")
            
        except Exception as e:
            print(f"更新统计信息时出错: {e}")
            import traceback
            traceback.print_exc()
