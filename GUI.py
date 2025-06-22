import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import threading
import time
import random
import json
import os
from components.ui_logic import UILogic
from components.ticket_logic import TicketLogic
from components.config_logic import ConfigLogic
from components.login_logic import LoginLogic
from components.logger import Logger

class TicketHelperGUI:
    def __init__(self):
        self.window = tk.Tk()
        
        # 初始化登录状态
        self.is_logged_in = False
        self.username = ""
        
        # 创建UI
        self.ui = UILogic(self.window)
        self.ui.create_menus()
        self.ui.create_widgets(self.window)
        
        # 初始化组件
        self.ticket = TicketLogic(self)
        self.config = ConfigLogic(self)
        self.login_logic = LoginLogic(self)
        self.logger = Logger(self)
        
        # 初始化登录状态
        self.is_logged_in = False
        self.username = ""
        
        # 绑定事件
        self.bind_events()
        
    def bind_events(self):
        """绑定UI事件到对应的方法"""
        # 登录页面事件
        self.ui.login_btn.config(command=lambda: self.login(1))
        
        # 抢票页面事件
        self.ui.uri_entry.bind("<FocusOut>", lambda e: self.config.validate_url(self.ui.uri_entry.get()))
        self.ui.start_btn.config(command=self.start_ticket_task)
        self.ui.stop_btn.config(command=self.stop_ticket_task)
        self.ui.restart_btn.config(command=self.retry_ticket_task)
        
        # 配置页面事件
        self.ui.proxy_check.config(command=lambda: self.config.toggle_proxy_fields())
        self.ui.save_btn.config(command=self.save_config)
        self.ui.log_file_btn.config(command=self.select_log_file)
        
        # 绑定菜单命令
        for item in self.ui.file_menu.winfo_children():
            if item.cget("label") == "保存配置":
                item.config(command=lambda: self.config.save_config())
            elif item.cget("label") == "加载配置":
                item.config(command=lambda: self.config.load_config())
                
        # 绑定按钮命令
        self.ui.start_btn.config(command=self.start_ticket_task)
        self.ui.stop_btn.config(command=self.stop_ticket_task)
        self.ui.restart_btn.config(command=self.retry_ticket_task)
        self.ui.log_file_btn.config(command=self.select_log_file)
        self.ui.save_btn.config(command=self.save_config)

    def create_widgets(self, main_frame):
        """UI组件创建已移动到UILogic类中"""
        pass

    def save_config(self):
        """保存当前配置到文件"""
        self.config.save_config()

    def load_config(self):
        """从文件加载配置"""
        self.config.load_config()

    def validate_url(self, event=None):
        """验证URL输入是否有效"""
        return self.config.validate_url()

    def validate_time(self, event=None):
        """验证时间输入是否有效"""
        return self.config.validate_time()

    def toggle_proxy_fields(self):
        """切换代理输入框的启用状态"""
        self.config.toggle_proxy_fields()

    def login(self, tab=0):
        """用户登录"""
        self.login_logic.login(tab)
        if self.login_logic.is_logged_in:
            self.ui.user_info.config(text=f"已登录: {self.login_logic.username}")
            self.ui.login_time.config(text=f"登录时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 显示完整cookie信息
            if hasattr(self.login_logic, 'cookies') and self.login_logic.cookies:
                cookie_text = "Cookies:\n"
                for cookie in self.login_logic.cookies:
                    cookie_text += f"{cookie['name']}: {cookie['value']}\n"
                    cookie_text += f"Domain: {cookie.get('domain', 'N/A')} | "
                    cookie_text += f"Path: {cookie.get('path', 'N/A')} | "
                    cookie_text += f"Expires: {cookie.get('expiry', 'N/A')}\n"
                    cookie_text += f"Secure: {cookie.get('secure', False)} | "
                    cookie_text += f"HttpOnly: {cookie.get('httpOnly', False)}\n"
                    cookie_text += "----------------\n"
                
                # 更新cookies_info标签
                self.ui.cookies_info.config(text=cookie_text)


    def get_sms_code(self):
        """获取短信验证码"""
        self.login_logic.get_sms_code()

    def do_login(self, notebook):
        """执行登录操作"""
        self.login_logic.do_login(notebook)
        self.is_logged_in = self.login_logic.is_logged_in
        self.username = self.login_logic.username

    def start_ticket_task(self):
        """开始抢票任务"""
        if not self.ui.uri_entry.get().strip():
            messagebox.showerror("错误", "请输入场次URI")
            return
            
        if not self.login_logic.is_logged_in:
            messagebox.showerror("错误", "请先登录后再开始抢票")
            return
            
        self.ticket.start_ticket_task()

    def stop_ticket_task(self):
        """停止抢票任务"""
        self.ticket.stop_ticket_task()

    def retry_ticket_task(self):
        """重试抢票任务"""
        self.ticket.retry_ticket_task()

    def clear_log(self):
        """清空日志内容"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log("日志已清空")

    def select_log_file(self):
        """选择日志文件路径"""
        file_path = filedialog.askdirectory()
        if file_path:
            self.ui.log_file_entry.delete(0, tk.END)
            self.ui.log_file_entry.insert(0, file_path)
            self.log(f"日志路径已设置为: {file_path}")

    def save_log(self):
        """保存日志到文件"""
        log_content = self.log_text.get(1.0, tk.END)
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
        log_content = self.log_text.get(1.0, tk.END)
        self.window.clipboard_clear()
        self.window.clipboard_append(log_content)
        self.log("日志内容已复制到剪贴板")

    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo(
            "关于抢票助手", 
            "抢票助手 Pro\n版本: 1.0.0\n作者: Semon\n"
            "功能: 自动抢票工具，支持多平台抢票"
        )
        
        # 绑定帮助菜单的关于命令
        for item in self.ui.help_menu.winfo_children():
            if item.cget("label") == "关于":
                item.config(command=self.show_about)

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = TicketHelperGUI()
    app.run()
