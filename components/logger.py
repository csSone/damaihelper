from tkinter import messagebox, filedialog
import tkinter as tk

class Logger:
    def __init__(self, gui):
        self.gui = gui

    def log(self, message):
        """添加日志消息"""
        self.gui.ui.log_text.config(state=tk.NORMAL)
        self.gui.ui.log_text.insert(tk.END, f"{message}\n")
        self.gui.ui.log_text.see(tk.END)
        self.gui.ui.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        """清空日志内容"""
        self.gui.ui.log_text.config(state=tk.NORMAL)
        self.gui.ui.log_text.delete(1.0, tk.END)
        self.gui.ui.log_text.config(state=tk.DISABLED)
        self.log("日志已清空")

    def save_log(self):
        """保存日志到文件"""
        log_content = self.gui.ui.log_text.get(1.0, tk.END)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
            self.log(f"日志已保存到: {file_path}")

    def copy_log(self):
        """复制日志内容到剪贴板"""
        log_content = self.gui.ui.log_text.get(1.0, tk.END)
        self.gui.window.clipboard_clear()
        self.gui.window.clipboard_append(log_content)
        self.log("日志内容已复制到剪贴板")
