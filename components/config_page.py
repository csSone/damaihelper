import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class ConfigPage:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.frame = tk.Frame(self.parent, bg="#f5f7fa")
        self.create_widgets()

    def create_widgets(self):
        """创建配置页面组件"""
        form_frame = ttk.LabelFrame(self.frame, text="系统配置")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10, ipadx=10, ipady=10)

        # 配置表单容器
        form_container = tk.Frame(form_frame, bg="#ffffff")
        form_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 配置项列表
        config_items = [
            ("date", "日期(逗号分隔):", "1,2,3"),
            ("sess", "场次(逗号分隔):", "1,2"),
            ("price", "票档(逗号分隔):", "1,2,3"),
            ("real_name", "实名信息ID:", "1"),
            ("nick_name", "昵称:", "用户"),
            ("ticket_num", "购票数量:", "2"),
            ("viewer_person", "观演人ID:", "1"),
            ("driver_path", "浏览器驱动路径:", "chromedriver.exe"),
            ("damai_url", "大麦网URL:", "https://www.damai.cn"),
            ("target_url", "目标URL:", ""),
            ("auto_buy_time", "自动抢票时间:", "00:00:00"),
            ("retry_interval", "重试间隔(秒):", "5")
        ]

        self.entries = {}
        for i, (key, label, default) in enumerate(config_items):
            row = tk.Frame(form_container, bg="#ffffff")
            row.pack(fill=tk.X, pady=5)
            
            lbl = ttk.Label(row, text=label, width=20)
            lbl.pack(side=tk.LEFT, padx=5)
            
            entry = ttk.Entry(row)
            entry.insert(0, default)
            entry.pack(fill=tk.X, expand=True, padx=5)
            self.entries[key] = entry

        # 自动抢票复选框
        auto_frame = tk.Frame(form_container, bg="#ffffff")
        auto_frame.pack(fill=tk.X, pady=5)
        
        self.auto_buy_var = tk.BooleanVar()
        auto_check = ttk.Checkbutton(auto_frame, text="启用自动抢票", 
                                   variable=self.auto_buy_var)
        auto_check.pack(side=tk.LEFT, padx=5)

        # 按钮区域
        btn_frame = tk.Frame(self.frame, bg="#f5f7fa")
        btn_frame.pack(fill=tk.X, pady=10)
        
        save_btn = ttk.Button(btn_frame, text="保存配置", command=self.save_config)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        load_btn = ttk.Button(btn_frame, text="加载配置", command=self.load_config)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        test_btn = ttk.Button(btn_frame, text="测试配置", command=self.test_config)
        test_btn.pack(side=tk.LEFT, padx=5)

    def save_config(self):
        """保存配置到文件"""
        config_data = {
            "date": self.entries["date"].get(),
            "sess": self.entries["sess"].get(),
            "price": self.entries["price"].get(),
            "real_name": self.entries["real_name"].get(),
            "nick_name": self.entries["nick_name"].get(),
            "ticket_num": self.entries["ticket_num"].get(),
            "viewer_person": self.entries["viewer_person"].get(),
            "driver_path": self.entries["driver_path"].get(),
            "damai_url": self.entries["damai_url"].get(),
            "target_url": self.entries["target_url"].get(),
            "auto_buy": self.auto_buy_var.get(),
            "auto_buy_time": self.entries["auto_buy_time"].get(),
            "retry_interval": self.entries["retry_interval"].get()
        }
        
        try:
            os.makedirs("config", exist_ok=True)
            with open("config/config.json", "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("成功", "配置保存成功")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")

    def load_config(self):
        """从文件加载配置"""
        try:
            if not os.path.exists("config/config.json"):
                messagebox.showwarning("警告", "配置文件不存在")
                return
                
            with open("config/config.json", "r", encoding="utf-8") as f:
                config_data = json.load(f)
                
            for key, entry in self.entries.items():
                if key in config_data:
                    entry.delete(0, tk.END)
                    entry.insert(0, str(config_data[key]))
                    
            if "auto_buy" in config_data:
                self.auto_buy_var.set(config_data["auto_buy"])
                
            messagebox.showinfo("成功", "配置加载成功")
        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败: {str(e)}")

    def test_config(self):
        """测试配置有效性"""
        try:
            # 检查必要字段
            required_fields = ["date", "sess", "price", "real_name", "driver_path"]
            for field in required_fields:
                if not self.entries[field].get().strip():
                    raise ValueError(f"请填写{field}字段")
                    
            messagebox.showinfo("成功", "配置测试通过")
        except Exception as e:
            messagebox.showerror("错误", f"配置测试失败: {str(e)}")
