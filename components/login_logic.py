from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pickle import dump, load
from os.path import exists
import os
import time

class LoginLogic:
    def __init__(self, gui):
        self.gui = gui
        self.is_logged_in = False
        self.username = ""
        self.session = requests.Session()
        self.driver = None
        self.cookie_file = "cookies.pkl"
        self.cookies = []

    def login(self, tab=0):
        """用户登录"""
        if tab == 0:  # 账号密码登录
            self._form_login()
        elif tab == 1:  # 扫码登录
            self._qr_login()
        else:
            messagebox.showerror("错误", "不支持的登录方式")

    def _form_login(self):
        """表单登录方式"""
        account = self.gui.ui.account_entry.get()
        password = self.gui.ui.password_entry.get()
        if not account or not password:
            messagebox.showerror("错误", "账号和密码不能为空")
            return
        
        try:
            self.gui.logger.log(f"尝试登录账号: {account}")
            self.gui.ui.user_info.config(text="登录中...", foreground="#4a6fa5")
            
            # 使用Selenium获取cookie - 优化版
            options = webdriver.ChromeOptions()
            # 禁止图片、js、css加载
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.managed_default_content_settings.javascript": 1,
                'permissions.default.stylesheet': 2
            }
            mobile_emulation = {"deviceName": "Nexus 6"}
            options.add_experimental_option("prefs", prefs)
            options.add_experimental_option("mobileEmulation", mobile_emulation)
            # 去掉webdriver痕迹
            options.add_argument("--disable-blink-features=AutomationControlled")
            # 确保窗口可见
            options.add_argument("--start-maximized")  # 启动时最大化窗口
            options.add_argument("--disable-gpu")  # 禁用GPU加速
            options.add_argument("--window-size=1920,1080")  # 设置窗口大小
            
            # 使用eager页面加载策略
            capa = DesiredCapabilities.CHROME
            capa["pageLoadStrategy"] = "eager"
            
            try:
                self.driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=options,
                    desired_capabilities=capa
                )
                self.gui.logger.log("浏览器驱动初始化成功")
            except Exception as e:
                self.gui.logger.log(f"浏览器驱动初始化失败: {str(e)}")
                raise Exception(f"浏览器启动失败: {str(e)}")
            self.driver.get("https://passport.damai.cn/login")
            
            # 输入账号密码
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'fm-login-id')))
            self.driver.find_element(By.NAME, 'loginId').send_keys(account)
            self.driver.find_element(By.NAME, 'password').send_keys(password)
            self.driver.find_element(By.CLASS_NAME, 'login-btn').click()
            
            # 等待登录成功
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'login-user')))
            
            # 保存cookie
            self.cookies = self.driver.get_cookies()
            dump(self.cookies, open(self.cookie_file, "wb"))
            
            # 记录cookies到日志
            self.gui.logger.log(f"账号 {account} 登录成功，获取cookies:")
            for cookie in self.cookies:
                self.gui.logger.log(f"  {cookie['name']}: {cookie['value']}")
            
            self.is_logged_in = True
            self.username = account
            self.gui.ui.user_info.config(text=f"已登录: {account}", foreground="#2ecc71")
            self.gui.logger.log(f"账号 {account} 登录成功")
            
            # 更新UI显示cookies信息
            if hasattr(self.gui.ui, 'cookies_info'):
                cookies_text = "\n".join([f"{c['name']}: {c['value']}" for c in self.cookies[:3]])  # 显示前3个关键cookie
                self.gui.ui.cookies_info.config(text=cookies_text)
            
        except Exception as e:
            self.gui.ui.user_info.config(text="登录失败", foreground="#e74c3c")
            self.gui.logger.log(f"登录失败: {str(e)}")
            messagebox.showerror("错误", f"登录失败: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

    def _qr_login(self):
        """扫码登录"""
        try:
            self.gui.logger.log("尝试扫码登录")
            self.gui.ui.user_info.config(text="准备扫码...", foreground="#4a6fa5")
            
            if not exists(self.cookie_file):
                self._get_cookie()
            else:
                self._set_cookie()
            
            self.is_logged_in = True
            self.username = "用户"
            self.gui.ui.user_info.config(text="已登录(cookie)", foreground="#2ecc71")
            self.gui.logger.log("扫码登录成功")
            
        except Exception as e:
            self.gui.ui.user_info.config(text="扫码登录失败", foreground="#e74c3c")
            self.gui.logger.log(f"扫码登录失败: {str(e)}")
            messagebox.showerror("错误", f"扫码登录失败: {str(e)}")

    def _get_cookie(self):
        """获取扫码登录cookie"""
        # 使用Selenium获取cookie - 优化版
        options = webdriver.ChromeOptions()
        # 禁止图片、js、css加载
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.javascript": 1,
            'permissions.default.stylesheet': 2
        }
        mobile_emulation = {"deviceName": "Nexus 6"}
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        # 去掉webdriver痕迹
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # 使用eager页面加载策略
        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "eager"
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options,
            desired_capabilities=capa
        )
        self.driver.get("https://www.damai.cn")
        
        messagebox.showinfo("提示", "请扫码登录")
        self.gui.ui.user_info.config(text="等待扫码...", foreground="#4a6fa5")
        
        WebDriverWait(self.driver, 120).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'login-user')))
        
        self.cookies = self.driver.get_cookies()
        dump(self.cookies, open(self.cookie_file, "wb"))
        self.driver.quit()
        
        # 记录cookies到日志
        self.gui.logger.log("扫码登录成功，获取cookies:")
        for cookie in self.cookies:
            self.gui.logger.log(f"  {cookie['name']}: {cookie['value']}")
        
        # 更新UI显示cookies信息
        if hasattr(self.gui.ui, 'cookies_info'):
            cookies_text = "\n".join([f"{c['name']}: {c['value']}" for c in self.cookies[:3]])  # 显示前3个关键cookie
            self.gui.ui.cookies_info.config(text=cookies_text)
        
        self.gui.logger.log("Cookie保存成功")

    def _set_cookie(self):
        """设置已有cookie"""
        self.cookies = load(open(self.cookie_file, "rb"))
        self.gui.logger.log("Cookie载入成功")

    def logout(self):
        """用户登出"""
        self.is_logged_in = False
        self.username = ""
        self.session = requests.Session()
        self.cookies = []
        if exists(self.cookie_file):
            os.remove(self.cookie_file)
        if self.driver:
            self.driver.quit()
        self.gui.ui.user_info.config(text="未登录", foreground="#777777")
        self.gui.logger.log("用户已登出")

    def get_cookies(self):
        """获取当前cookie"""
        return self.cookies
