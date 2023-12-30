import tkinter as tk
from UI import *

class PathInput:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("输入路径参数")

        self.label = tk.Label(self.root, text="请输入根路径:")
        self.label.pack(pady=10)

        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack(pady=10)

        self.confirm_button = tk.Button(self.root, text="确定", command=self.confirm_path)
        self.confirm_button.pack(pady=10)

        self.path_value = None

    def confirm_path(self):
        self.path_value = self.entry.get()
        self.root.destroy()

    def get_path(self):
        return self.path_value

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    path_input = PathInput()
    path_input.run()
    root_path = path_input.get_path()

    ui = UI(root_path)
    ui.run()
