import json
import os
import time
from tkinter import messagebox, filedialog

class ConfigLogic:
    def __init__(self, ui_components):
        self.ui = ui_components

    def save_config(self):
        """保存当前配置到文件"""
        config = {
            'url': self.ui.uri_entry.get(),
            'time': self.ui.time_entry.get(),
            'proxy_ip': self.ui.proxy_ip_entry.get(),
            'proxy_port': self.ui.proxy_port_entry.get(),
            'proxy_enabled': self.ui.proxy_check_var.get(),
            'auto_buy': self.ui.auto_buy_check_var.get()
        }
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            self.ui.log(f"配置已保存到: {file_path}")

    def load_config(self):
        """从文件加载配置"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.ui.uri_entry.delete(0, tk.END)
            self.ui.uri_entry.insert(0, config.get('url', ''))
            self.ui.time_entry.delete(0, tk.END)
            self.ui.time_entry.insert(0, config.get('time', ''))
            self.ui.proxy_ip_entry.delete(0, tk.END)
            self.ui.proxy_ip_entry.insert(0, config.get('proxy_ip', ''))
            self.ui.proxy_port_entry.delete(0, tk.END)
            self.ui.proxy_port_entry.insert(0, config.get('proxy_port', ''))
            self.ui.proxy_check_var.set(config.get('proxy_enabled', False))
            self.ui.auto_buy_check_var.set(config.get('auto_buy', False))
            self.ui.log(f"配置已从 {file_path} 加载")

    def validate_url(self, url=None):
        """验证URI输入是否有效"""
        if url is None:
            url = self.ui.uri_entry.get().strip()
        if not url:
            messagebox.showerror("错误", "URI不能为空")
            return False
        if not (url.startswith('http://') or url.startswith('https://')):
            messagebox.showerror("错误", "URI必须以http://或https://开头")
            return False
        return True

    def validate_time(self, event=None):
        """验证时间输入是否有效"""
        time_str = self.ui.time_entry.get().strip()
        if not time_str:
            messagebox.showerror("错误", "时间不能为空")
            return False
        try:
            time.strptime(time_str, "%H:%M:%S")
            return True
        except ValueError:
            messagebox.showerror("错误", "时间格式不正确，请使用HH:MM:SS格式")
            return False

    def toggle_proxy_fields(self):
        """切换代理输入框的启用状态"""
        if self.ui.proxy_check_var.get():
            self.ui.proxy_ip_entry.config(state=tk.NORMAL)
            self.ui.proxy_port_entry.config(state=tk.NORMAL)
        else:
            self.ui.proxy_ip_entry.config(state=tk.DISABLED)
            self.ui.proxy_port_entry.config(state=tk.DISABLED)
