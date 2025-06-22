import tkinter as tk
from tkinter import ttk

class UILogic:
    def __init__(self, window):
        self.window = window
        self.style = ttk.Style()
        self.setup_window()
        self.setup_styles()
        
    def setup_window(self):
        self.window.title("抢票助手 Pro")
        self.window.geometry("1200x900")
        self.window.config(bg="#f5f7fa")
        self.window.resizable(True, True)
        self.window.minsize(1000, 800)
        
    def setup_styles(self):
        self.style.theme_use('clam')
        self.style.configure("TButton", font=("微软雅黑", 12), padding=8, 
                           background="#4a6fa5", foreground="white", 
                           borderwidth=1, relief="flat", width=15)
        self.style.map("TButton", 
                      background=[('active', '#3a5a80'), ('disabled', '#cccccc')])
        self.style.configure("TLabel", font=("微软雅黑", 11), foreground="#2c3e50", 
                           background="#f5f7fa", padding=5)
        self.style.configure("TCheckbutton", font=("微软雅黑", 11), foreground="#2c3e50", 
                           background="#f5f7fa", padding=5)
        self.style.configure("TEntry", font=("微软雅黑", 11), padding=5, 
                           fieldbackground="#ffffff")
        self.style.configure("TLabelframe", font=("微软雅黑", 12, "bold"), 
                           foreground="#2c3e50", background="#ffffff", 
                           borderwidth=2, relief="groove")
        self.style.configure("TLabelframe.Label", font=("微软雅黑", 12, "bold"), 
                           foreground="#4a6fa5")
        self.style.configure("Horizontal.TProgressbar", thickness=20, 
                           background="#4a6fa5", troughcolor="#e0e6ed")
    
    def create_menus(self):
        """创建菜单栏"""
        self.menu_bar = tk.Menu(self.window)
        
        # 文件菜单
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="保存配置")
        self.file_menu.add_command(label="加载配置")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="退出")
        self.menu_bar.add_cascade(label="文件", menu=self.file_menu)
        
        # 帮助菜单
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="关于")
        self.menu_bar.add_cascade(label="帮助", menu=self.help_menu)
        
        self.window.config(menu=self.menu_bar)
    
    def create_widgets(self, main_frame):
        # 创建顶部标题区域
        header_frame = tk.Frame(main_frame, bg="#f5f7fa")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 创建左侧导航菜单
        nav_frame = tk.Frame(main_frame, bg="#e0e6ed", width=150)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # 导航按钮
        self.login_nav_btn = ttk.Button(nav_frame, text="账号登录", 
                                      command=lambda: self.show_page("login"))
        self.login_nav_btn.pack(fill=tk.X, pady=5, padx=5)
        
        self.ticket_nav_btn = ttk.Button(nav_frame, text="抢票设置", 
                                       command=lambda: self.show_page("ticket"))
        self.ticket_nav_btn.pack(fill=tk.X, pady=5, padx=5)
        
        self.config_nav_btn = ttk.Button(nav_frame, text="系统配置", 
                                       command=lambda: self.show_page("config"))
        self.config_nav_btn.pack(fill=tk.X, pady=5, padx=5)
        
        # 创建内容区域
        self.content_frame = tk.Frame(main_frame, bg="#f5f7fa")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建三个页面
        self.create_login_page()
        self.create_ticket_page()
        self.create_config_page()
        
        # 默认显示登录页
        self.show_page("login")
        
    def show_page(self, page_name):
        """显示指定页面"""
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()
            
        if page_name == "login":
            self.login_frame.pack(fill=tk.BOTH, expand=True)
        elif page_name == "ticket":
            self.ticket_frame.pack(fill=tk.BOTH, expand=True)
        elif page_name == "config":
            self.config_frame.pack(fill=tk.BOTH, expand=True)
            
    def create_login_page(self):
        """创建登录页面"""
        self.login_frame = tk.Frame(self.content_frame, bg="#f5f7fa")
        
        # 登录区域
        login_frame = ttk.LabelFrame(self.login_frame, text="登录")
        login_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10, ipadx=5, ipady=5)
        
        # 登录说明
        login_label = ttk.Label(login_frame, 
                              text="点击下方按钮登录\n登录成功后自动保存登录状态",
                              justify=tk.CENTER)
        login_label.pack(pady=20)
        
        # 登录按钮
        self.login_btn = ttk.Button(login_frame, text="登录", width=15)
        self.login_btn.pack(pady=10)
        
        # 登录信息展示区域
        self.info_frame = ttk.LabelFrame(login_frame, text="登录信息")
        self.info_frame.pack(fill=tk.X, pady=10)
        
        self.user_info = ttk.Label(self.info_frame, text="未登录", 
                                 font=("微软雅黑", 11, "bold"),
                                 foreground="#4a6fa5")
        self.user_info.pack(pady=5)
        
        # Cookies信息展示
        self.cookies_info = tk.Label(self.info_frame, text="Cookies: 未获取",
                                   font=("Courier New", 8), foreground="#333333",
                                   background="#f0f0f0", relief="groove",
                                   borderwidth=1, padx=5, pady=2,
                                   wraplength=500, justify=tk.LEFT, anchor='nw')
        self.cookies_info.pack(pady=5, fill=tk.X, padx=10)
        
        self.login_time = ttk.Label(self.info_frame, text="", 
                                  font=("微软雅黑", 10),
                                  foreground="#777777")
        self.login_time.pack()
        
    def create_ticket_page(self):
        """创建抢票页面"""
        self.ticket_frame = tk.Frame(self.content_frame, bg="#f5f7fa")
        
        # 票务信息
        ticket_info_frame = ttk.LabelFrame(self.ticket_frame, text="票务信息")
        ticket_info_frame.pack(fill=tk.X, pady=10, padx=10, ipadx=5, ipady=5)
        
        # 场次URI输入
        uri_frame = tk.Frame(ticket_info_frame, bg="#ffffff")
        uri_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(uri_frame, text="场次URI:").pack(side=tk.LEFT, padx=5)
        self.uri_entry = ttk.Entry(uri_frame)
        self.uri_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        
        # 控制按钮
        control_frame = tk.Frame(self.ticket_frame, bg="#f5f7fa")
        control_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="开始抢票")
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = ttk.Button(control_frame, text="停止", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        self.restart_btn = ttk.Button(control_frame, text="重试", state=tk.DISABLED)
        self.restart_btn.pack(side=tk.LEFT, padx=10)
        
    def create_config_page(self):
        """创建配置页面"""
        self.config_frame = tk.Frame(self.content_frame, bg="#f5f7fa")
        
        # 代理设置
        proxy_frame = ttk.LabelFrame(self.config_frame, text="代理设置")
        proxy_frame.pack(fill=tk.X, pady=10, padx=10, ipadx=5, ipady=5)
        
        # 代理启用复选框
        proxy_enable_frame = tk.Frame(proxy_frame, bg="#ffffff")
        proxy_enable_frame.pack(fill=tk.X, pady=5)
        
        self.proxy_check_var = tk.BooleanVar()
        self.proxy_check = ttk.Checkbutton(proxy_enable_frame, text="启用代理",
                                         variable=self.proxy_check_var)
        self.proxy_check.pack(side=tk.LEFT, padx=10)
        
        # 代理IP输入
        proxy_ip_frame = tk.Frame(proxy_frame, bg="#ffffff")
        proxy_ip_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(proxy_ip_frame, text="代理IP:").pack(side=tk.LEFT, padx=5)
        self.proxy_ip_entry = ttk.Entry(proxy_ip_frame)
        self.proxy_ip_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 代理端口输入
        proxy_port_frame = tk.Frame(proxy_frame, bg="#ffffff")
        proxy_port_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(proxy_port_frame, text="端口:").pack(side=tk.LEFT, padx=5)
        self.proxy_port_entry = ttk.Entry(proxy_port_frame, width=10)
        self.proxy_port_entry.pack(side=tk.LEFT, padx=5)
        
        # 日志设置
        log_frame = ttk.LabelFrame(self.config_frame, text="日志设置")
        log_frame.pack(fill=tk.X, pady=10, padx=10, ipadx=5, ipady=5)
        
        # 日志级别
        log_level_frame = tk.Frame(log_frame, bg="#ffffff")
        log_level_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(log_level_frame, text="日志级别:").pack(side=tk.LEFT, padx=5)
        self.log_level_var = tk.StringVar(value="INFO")
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.log_level_menu = ttk.OptionMenu(log_level_frame, self.log_level_var, 
                                           *log_levels)
        self.log_level_menu.pack(side=tk.LEFT, padx=5)
        
        # 日志文件
        log_file_frame = tk.Frame(log_frame, bg="#ffffff")
        log_file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(log_file_frame, text="日志路径:").pack(side=tk.LEFT, padx=5)
        self.log_file_entry = ttk.Entry(log_file_frame)
        self.log_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.log_file_btn = ttk.Button(log_file_frame, text="浏览", width=5)
        self.log_file_btn.pack(side=tk.LEFT, padx=5)
        
        # 保存按钮
        save_frame = tk.Frame(self.config_frame, bg="#f5f7fa")
        save_frame.pack(fill=tk.X, pady=10)
        
        self.save_btn = ttk.Button(save_frame, text="保存配置", width=15)
        self.save_btn.pack(pady=5)
        
        # 日志文本框
        log_frame = tk.Frame(self.window, bg="#f5f7fa")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
