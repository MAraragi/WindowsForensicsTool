import time
import threading
from GPT import *
import tkinter as tk
from eventsLog import *
# from fileBasic import *
from regeditReader import *
from datetime import datetime
from tkinter import messagebox
from folderMonitor import FolderMonitor
from browserSQLiteReader import BrowserHistoryReader


class UI:
    def __init__(self, root_path):
        self.root = tk.Tk()
        self.root.title("UI")
        self.begin_time = str(datetime.now()).split('.')[0]
        self.root_path = root_path

        """
        # Frame 用于容纳文件类型选择框
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        
        # Checkbutton 用于选择文件类型
        self.file_types_var = {}
        for file_type in ['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'pdf']:
            var = tk.BooleanVar()
            self.file_types_var[file_type] = var
            checkbox = tk.Checkbutton(frame, text=file_type, variable=var)
            checkbox.pack(side=tk.LEFT, padx=5) #"""

        # 初始化按钮
        init_button = tk.Button(self.root, text="初始化", command=self.initialize)
        init_button.pack(pady=10)

        # 日志按钮
        select_time_button = tk.Button(self.root, text="日志", command=self.open_log_window)
        select_time_button.pack(pady=10)

        # 注册表按钮
        select_regedit_button = tk.Button(self.root, text="注册表", command=self.open_regedit_window)
        select_regedit_button.pack(pady=10)

        # 提示信息
        self.info_label = tk.Label(self.root, text="")
        self.info_label.pack(pady=10)

        # 文本框用于显示结果
        self.result_text = tk.Text(self.root, height=20, width=100)
        self.result_text.pack(pady=10)

        # 检查变化按钮
        check_changes_button = tk.Button(self.root, text="监控文件变化", command=self.monitorFolder)
        check_changes_button.pack(pady=10)

        check_changes_button = tk.Button(self.root, text="分析用户行为", command=self.make_query)
        check_changes_button.pack(pady=10)

        # 记录当前内容按钮
        record_output_button = tk.Button(self.root, text="记录当前输出", command=self.record_output_content)
        record_output_button.pack(pady=10)

        # FileBasic 实例
        # self.file_basic_instance = None
        # 各类实例
        self.folder_monitor_instance = None
        self.event_logs_instance = None
        self.regedit_instance = None
        self.gpt = None
        self.title_and_urls = []

        # BrowserSQLiteReader 实例
        # 包括Chrome和Edge
        self.chrome_history_reader = BrowserHistoryReader(browser_name="Chrome")
        self.edge_history_reader = BrowserHistoryReader(browser_name="Edge")

        # 文件总变化
        self.add_files = []
        self.rename_files = []
        self.modify_files = []
        self.delete_files = []
        self.access_files = []
        self.move_files = []

        # 用来标识是否开启文件监控的变量
        self.keep_monitoring = False

        # 用来开启线程实现实时监控的变量
        self.thread = None

    def initialize(self):
        """
        selected_file_types = [file_type for file_type, var in self.file_types_var.items() if var.get()]

        if not selected_file_types:
            messagebox.showwarning("未选择文件类型", "请至少选择一个文件类型")
            return

        # self.root_path = 'C:\\Users\\Administrator\\Desktop\\undergraduate'  # 替换为实际的路径
        self.file_basic_instance = FileBasic(self.root_path, selected_file_types) #"""
        self.folder_monitor_instance = FolderMonitor(self.root_path)
        self.event_logs_instance = eventsLogs()
        self.regedit_instance = regeditReader()
        self.gpt = GPT()
        self.info_label.config(text=f"文件已读取，根路径为: {self.root_path}")

    def monitorFolder(self):
        if self.folder_monitor_instance is None:
            messagebox.showwarning("未初始化", "请先初始化")
            return
        if not self.keep_monitoring:
            # 每次开始监控文件夹前先清空上次监控记录
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.config(state=tk.DISABLED)
            self.add_files = []
            self.rename_files = []
            self.modify_files = []
            self.delete_files = []
            self.access_files = []
            self.move_files = []
            self.title_and_urls = []
            # 使用线程实现实时监控
            self.keep_monitoring = True
            self.thread = threading.Thread(target=self.check_changes)
            self.thread.start()
        else:
            self.keep_monitoring = False

    def check_changes(self):
        while self.keep_monitoring:
            results = self.folder_monitor_instance.getUpdates()
            if not results:
                return
            add_files, rename_files, modify_files, delete_files, access_files, move_files = results
            tz = timezone(timedelta(hours=8))
            current_time = datetime.now(tz)
            time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            # 在文本框内显示结果
            self.result_text.config(state=tk.NORMAL)
            for add in add_files:
                self.result_text.insert(tk.END, f"add {add[2]}: {add[1]}\nadd time = {add[3]}\n\n")
                self.add_files.append(add[1])
            for acc in access_files:
                self.result_text.insert(tk.END, f"access {acc[2]}: {acc[1]}\naccess time = {acc[5]}\n\n")
                self.access_files.append(acc[1])
            for delete in delete_files:
                self.result_text.insert(tk.END, f"delete {delete[2]}: {delete[1]}\ndelete time = {time_str}\n\n")
                self.delete_files.append(delete[1])
            for mo in modify_files:
                self.result_text.insert(tk.END, f"modify {mo[2]}: {mo[1]}\nmodify time = {mo[4]}\n\n")
                self.modify_files.append(mo[1])
            for ren in rename_files:
                self.result_text.insert(tk.END, f"rename {ren[0][2]}:\n{ren[0][1]}\n-->{ren[1][1]}\n"
                                                f"rename time = {time_str}\n\n")
                self.rename_files.append(ren[0][1] + "-->" + ren[1][1])
            for mo in move_files:
                self.result_text.insert(tk.END, f"move {mo[0][2]}:\n{mo[0][1]}\n-->{mo[1][1]}\n"
                                                f"move time = {time_str}\n\n")
                self.move_files.append(mo[0][1] + "-->" + mo[1][1])
            self.result_text.config(state=tk.DISABLED)
            time.sleep(5)

    def open_log_window(self):
        # 创建时间范围选择窗口
        time_range_window = tk.Toplevel(self.root)
        time_range_window.title("日志")

        # 添加文本框用于显示日志
        self.log_text = tk.Text(time_range_window, height=20, width=100)
        self.log_text.grid(row=2, column=0, columnspan=2, pady=10)
        self.result_text.config(state=tk.DISABLED)

        # 添加两个 Entry 用于输入起始时间和结束时间
        start_label = tk.Label(time_range_window, text="起始时间:")
        start_label.grid(row=0, column=0, padx=5, pady=5)
        start_entry = tk.Entry(time_range_window)
        start_entry.grid(row=0, column=1, padx=5, pady=5)

        end_label = tk.Label(time_range_window, text="结束时间:")
        end_label.grid(row=1, column=0, padx=5, pady=5)
        end_entry = tk.Entry(time_range_window)
        end_entry.grid(row=1, column=1, padx=5, pady=5)

        # 添加浅色提示文本
        start_entry.insert(0, "XXXX-XX-XX XX:XX:XX")
        start_entry.config(fg="grey")
        end_entry.insert(0, "XXXX-XX-XX XX:XX:XX")
        end_entry.config(fg="grey")

        # 添加事件处理，用于清除提示文本
        start_entry.bind("<FocusIn>", lambda event: self.on_entry_focus_in(start_entry, "XXXX-XX-XX XX:XX:XX"))
        start_entry.bind("<FocusOut>", lambda event: self.on_entry_focus_out(start_entry, "XXXX-XX-XX XX:XX:XX"))
        end_entry.bind("<FocusIn>", lambda event: self.on_entry_focus_in(end_entry, "XXXX-XX-XX XX:XX:XX"))
        end_entry.bind("<FocusOut>", lambda event: self.on_entry_focus_out(end_entry, "XXXX-XX-XX XX:XX:XX"))

        filter_button = tk.Button(time_range_window, text="筛选", command=lambda: self.filter_logs(start_entry.get(),
                                                                                                   end_entry.get()))
        filter_button.grid(row=3, column=0, columnspan=2, pady=10)

    def on_entry_focus_in(self, entry, default_text):
        if entry.get() == default_text:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def on_entry_focus_out(self, entry, default_text):
        if not entry.get():
            entry.insert(0, default_text)
            entry.config(fg="grey")

    def filter_logs(self, start, end):

        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END) 
        # 获取所有事件日志
        all_logs = []
        all_logs.extend(self.event_logs_instance.word_logs)
        all_logs.extend(self.event_logs_instance.powerpoint_logs)
        all_logs.extend(self.event_logs_instance.excel_logs)

        # 筛选并显示符合时间范围的日志
        filtered_logs = [log for log in all_logs if start <= log[0] <= end]
        for log in filtered_logs:
            self.log_text.insert(tk.END, f"{log}\n")
        self.log_text.config(state=tk.DISABLED)

    def open_regedit_window(self):
        # 创建注册表筛选窗口
        regedit_filter_window = tk.Toplevel(self.root)
        regedit_filter_window.title("注册表")

        # 添加文本框用于显示注册表内容
        self.regedit_text = tk.Text(regedit_filter_window, height=20, width=100)
        self.regedit_text.grid(row=2, column=0, columnspan=2, pady=10)
        self.regedit_text.config(state=tk.DISABLED)

        # 添加两个 Entry 用于输入起始时间和结束时间
        start_label = tk.Label(regedit_filter_window, text="起始时间:")
        start_label.grid(row=0, column=0, padx=5, pady=5)
        start_entry = tk.Entry(regedit_filter_window)
        start_entry.grid(row=0, column=1, padx=5, pady=5)

        end_label = tk.Label(regedit_filter_window, text="结束时间:")
        end_label.grid(row=1, column=0, padx=5, pady=5)
        end_entry = tk.Entry(regedit_filter_window)
        end_entry.grid(row=1, column=1, padx=5, pady=5)

        # 添加浅色提示文本
        start_entry.insert(0, "XXXX-XX-XX XX:XX:XX")
        start_entry.config(fg="grey")
        end_entry.insert(0, "XXXX-XX-XX XX:XX:XX")
        end_entry.config(fg="grey")

        # 添加事件处理，用于清除提示文本
        start_entry.bind("<FocusIn>", lambda event: self.on_entry_focus_in(start_entry, "XXXX-XX-XX XX:XX:XX"))
        start_entry.bind("<FocusOut>", lambda event: self.on_entry_focus_out(start_entry, "XXXX-XX-XX XX:XX:XX"))
        end_entry.bind("<FocusIn>", lambda event: self.on_entry_focus_in(end_entry, "XXXX-XX-XX XX:XX:XX"))
        end_entry.bind("<FocusOut>", lambda event: self.on_entry_focus_out(end_entry, "XXXX-XX-XX XX:XX:XX"))

        # 添加按钮，点击后获取用户输入的时间范围并执行筛选和显示注册表内容的操作
        filter_button = tk.Button(regedit_filter_window, text="筛选", command=lambda: self.filter_regedit(start_entry.get(), end_entry.get()))
        filter_button.grid(row=3, column=0, columnspan=2, pady=10)

    def filter_regedit(self, start, end):
        self.regedit_text.config(state=tk.NORMAL)
        self.regedit_text.delete(1.0, tk.END)

        # 获取注册表内容
        mru_set = self.regedit_instance.mru_set

        # 筛选并显示符合时间范围的注册表内容
        filtered_entries = [entry for entry in mru_set if start <= entry[0] <= end]
        for entry in filtered_entries:
            self.regedit_text.insert(tk.END, f"{entry}\n")
        self.regedit_text.config(state=tk.DISABLED)

    def make_query(self):
        start = self.begin_time
        end = str(datetime.now()).split('.')[0]
        mru_set = self.regedit_instance.mru_set

        all_logs = []
        all_logs.extend(self.event_logs_instance.word_logs)
        all_logs.extend(self.event_logs_instance.powerpoint_logs)
        all_logs.extend(self.event_logs_instance.excel_logs)

        filtered_regs = [entry[3] for entry in mru_set if start <= entry[0] <= end]
        filtered_logs = [log[3] for log in all_logs if start <= log[0] <= end]
        updated_records = [*self.chrome_history_reader.getUpdates(), *self.edge_history_reader.getUpdates()]
        self.title_and_urls = [(x["title"], x["url"]) for x in updated_records]

        all_text = f"注册表内容如下（可说明用户打开的文件）:{filtered_regs}， \
                     日志内容如下（可说明用户访问文件时产生的告警）:{filtered_logs}，\
                     操作期间增加文件如下: {self.add_files}，\
                     删除文件如下: {self.delete_files}，\
                     修改文件如下：{self.modify_files}，\
                     重命名文件如下：{self.rename_files}，\
                     移动文件如下：{self.move_files}，\
                     访问文件如下：{self.access_files}\
                     用户访问的网页的标题及url如下：{self.title_and_urls},\
                     请分析当前用户的身份、行为，并做出你的评价与判断，越详细越好。\
                     "
        self.gpt.set_prompt(all_text)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, self.gpt.get_answer() + "\n\n")
        self.result_text.config(state=tk.DISABLED)

    def record_output_content(self):
        tz = timezone(timedelta(hours=8))
        current_time = datetime.now(tz)
        time_str = current_time.strftime('%Y_%m%d_%H%M%S')
        self.result_text.config(state=tk.NORMAL)
        text_content = self.result_text.get("1.0", "end-1c")
        self.result_text.config(state=tk.DISABLED)
        with open(f"record_{time_str}.txt", 'w', encoding="utf8") as record_file:
            record_file.write(text_content)
            record_file.write("浏览器访问记录如下：\n")
            for title_and_url in self.title_and_urls:
                record_file.write(f"{title_and_url}\n")

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    ui = UI("C:\\Users\\admin\\Desktop\\forensics_test")
    ui.run()
