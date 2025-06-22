import threading
import time
import json
import os
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TicketLogic:
    def __init__(self, ui_components):
        self.ui = ui_components
        self.is_running = False
        self.thread = None
        self.driver = None
        self.status = 0  # 0:未开始 1:准备中 2:运行中 3:成功 4:失败
        
    def start_ticket_task(self):
        """开始抢票任务"""
        if not self.ui.login_logic.is_logged_in:
            messagebox.showerror("错误", "请先登录后再开始抢票")
            return
            
        # 准备任务参数
        task_params = {
            'uri': self.ui.ui.uri_entry.get(),
            'use_proxy': self.ui.ui.proxy_check_var.get(),
            'proxy_ip': self.ui.ui.proxy_ip_entry.get() if self.ui.ui.proxy_check_var.get() else None,
            'proxy_port': self.ui.ui.proxy_port_entry.get() if self.ui.ui.proxy_check_var.get() else None,
            'username': self.ui.login_logic.username
        }
        
        # 更新UI状态
        self.ui.ui.start_btn.config(state='disabled')
        self.ui.ui.stop_btn.config(state='normal') 
        self.ui.ui.restart_btn.config(state='disabled')
        
        # 启动抢票线程
        self.is_running = True
        self.thread = threading.Thread(target=self._run_ticket_task, args=(task_params,))
        self.thread.start()
        self.ui.logger.log("抢票任务已开始")

    def _run_ticket_task(self, params):
        """实际执行抢票任务的线程方法"""
        try:
            # 初始化浏览器
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # 性能优化设置
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.managed_default_content_settings.javascript": 1
            }
            options.add_experimental_option("prefs", prefs)
            
            try:
                # 自动管理ChromeDriver版本并增加重试逻辑
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # chromedriver_path = "./chromedriver.exe"
                        # service = Service(executable_path=chromedriver_path)
                        # self.driver = webdriver.Chrome(service=service, options=options)
                        self.driver = webdriver.Chrome(
                            service=Service(ChromeDriverManager().install()),
                            options=options)
                        
                        # 检查浏览器是否正常启动
                        if not self.driver:
                            raise Exception("浏览器启动失败")
                        break
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise
                        self.ui.logger.log(f"浏览器初始化失败(尝试 {attempt+1}/{max_retries}): {str(e)}")
                        time.sleep(2)  # 等待2秒后重试
                
                # 先访问目标页面
                self.driver.get(params['uri'])
                
            except Exception as e:
                self.ui.logger.log(f"浏览器初始化失败: {str(e)}")
                if hasattr(self, 'driver') and self.driver:
                    self.driver.quit()
                raise Exception(f"浏览器初始化失败: {str(e)}")
            
            # 确保在正确域名下添加cookie
            try:
                for cookie in self.ui.login_logic.cookies:
                    self.driver.add_cookie({
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': '.damai.cn'
                    })
                # 刷新页面使cookie生效
                self.driver.refresh()
            except Exception as e:
                self.ui.logger.log(f"添加cookie失败: {str(e)}")
            
            # 更健壮的页面加载等待
            max_retries = 3
            loaded = False
            for attempt in range(max_retries):
                try:
                    # 检查浏览器是否仍然可用
                    if not self.driver or not hasattr(self.driver, 'current_url'):
                        raise Exception("浏览器不可用")
                    
                    # 使用更通用的页面加载检测
                    WebDriverWait(self.driver, 15).until(
                        lambda d: d.execute_script('return document.readyState') == 'complete')
                    
                    # 检查页面标题或URL是否包含大麦网标识
                    if "damai" in self.driver.current_url.lower() or "大麦" in self.driver.title:
                        loaded = True
                        break
                    else:
                        self.ui.logger.log(f"页面加载尝试 {attempt+1}/{max_retries}: 页面验证失败")
                except Exception as e:
                    self.ui.logger.log(f"页面加载尝试 {attempt+1}/{max_retries} 失败: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        self.driver.refresh()
                    else:
                        raise Exception(f"页面加载失败: {str(e)}")
            
            if not loaded:
                raise Exception("页面加载失败: 无法找到app元素")
            
            # 抢票主循环 - 高频刷新模式
            refresh_interval = 0.1  # 100ms = 10次/秒
            while self.is_running:
                try:
                    # 查找class为"buy-link"的元素
                    buy_links = self.driver.find_elements(By.CSS_SELECTOR, ".buy-link")
                    
                    # 优先点击可见的元素
                    visible_links = [link for link in buy_links if link.is_displayed()]
                    if visible_links:
                        try:
                            # 详细记录元素信息
                            self.ui.logger.log(f"找到{len(visible_links)}个可见buy-link元素")
                            for i, link in enumerate(visible_links[:3]):  # 最多记录前3个
                                self.ui.logger.log(f"元素#{i+1} - 文本: {link.text}")
                                self.ui.logger.log(f"元素#{i+1} - 位置: {link.location}")
                                self.ui.logger.log(f"元素#{i+1} - 尺寸: {link.size}")
                            
                            # 智能点击策略
                            target_link = visible_links[0]
                            for i in range(3):  # 减少点击次数但增加点击精度
                                try:
                                    # 使用JavaScript点击避免元素遮挡
                                    self.driver.execute_script("arguments[0].click();", target_link)
                                    self.ui.logger.log(f"第{i+1}次点击buy-link元素(JS方式)")
                                    
                                    # 检查是否跳转
                                    time.sleep(0.3)
                                    if "confirm" in self.driver.current_url:
                                        break
                                except Exception as e:
                                    self.ui.logger.log(f"点击失败: {str(e)}")
                                    # 回退到普通点击
                                    target_link.click()
                                    self.ui.logger.log(f"第{i+1}次点击buy-link元素(普通方式)")
                            
                            # 详细记录点击结果
                            self.ui.logger.log("点击操作完成")
                            self.ui.logger.log(f"当前URL: {self.driver.current_url}")
                            self.ui.logger.log(f"页面标题: {self.driver.title}")
                            self.ui.logger.log(f"页面状态码: {self.driver.execute_script('return document.readyState')}")
                            
                            # 检查是否进入选座页面
                            if "选座" in self.driver.title or "seat" in self.driver.current_url.lower():
                                self.ui.logger.log("已进入选座页面，开始选择座位")
                                
                                # 等待座位加载完成
                                try:
                                    WebDriverWait(self.driver, 10).until(
                                        EC.presence_of_element_located((By.CSS_SELECTOR, ".seat-item")))
                                    
                                    # 选择第一个可用座位
                                    available_seats = self.driver.find_elements(
                                        By.CSS_SELECTOR, ".seat-item.available")
                                    if available_seats:
                                        self.ui.logger.log(f"找到{len(available_seats)}个可用座位")
                                        available_seats[0].click()
                                        self.ui.logger.log("已选择第一个可用座位")
                                        
                                        # 点击立即购买按钮
                                        buy_btn = WebDriverWait(self.driver, 10).until(
                                            EC.element_to_be_clickable((By.CSS_SELECTOR, ".buy-btn")))
                                        buy_btn.click()
                                        self.ui.logger.log("已点击立即购买按钮")
                                        
                                        # 检查是否跳转到确认页面
                                        WebDriverWait(self.driver, 10).until(
                                            lambda d: "确认订单" in d.title)
                                        self.ui.logger.log("已跳转到订单确认页面")
                                        break
                                    else:
                                        self.ui.logger.log("没有可用座位，刷新重试")
                                        self.driver.refresh()
                                except Exception as e:
                                    self.ui.logger.log(f"选座过程中出错: {str(e)}")
                                    self.driver.refresh()
                            elif "确认订单" in self.driver.title:
                                self.ui.logger.log("已跳转到订单确认页面")
                                break
                        except Exception as e:
                            self.ui.logger.log(f"点击选座按钮失败: {str(e)}")
                            self.ui.logger.log(f"当前页面HTML: {self.driver.page_source[:500]}...")
                    else:
                        # 没有找到可点击元素时才刷新
                        self.ui.logger.log(f"未找到可点击元素，执行页面刷新，等待{refresh_interval}秒")
                        self.driver.refresh()
                        time.sleep(refresh_interval)
                        self.ui.logger.log(f"刷新完成，当前URL: {self.driver.current_url}")
                    
                    # 检查是否成功
                    if "确认订单" in self.driver.title:
                        self.status = 3  # 成功
                        self.ui.logger.log("抢票成功！请完成支付")
                        break
                        
                except Exception as e:
                    error_msg = str(e)
                    self.ui.logger.log(f"抢票过程中出错: {error_msg}")
                    
                    # 处理浏览器崩溃情况
                    if "Stacktrace:" in error_msg or "GetHandleVerifier" in error_msg:
                        self.ui.logger.log("检测到浏览器崩溃，尝试恢复...")
                        try:
                            if self.driver:
                                self.driver.quit()
                            # 重新初始化浏览器
                            driver_path = "./"
                            self.driver = webdriver.Chrome(
                                service=Service(ChromeDriverManager(path=driver_path).install()),
                                options=options)
                            self.driver.get(params['uri'])
                            # 重新添加cookie
                            for cookie in self.ui.login_logic.cookies:
                                self.driver.add_cookie({
                                    'name': cookie['name'],
                                    'value': cookie['value'],
                                    'domain': '.damai.cn'
                                })
                            self.driver.refresh()
                        except Exception as e:
                            self.ui.logger.log(f"浏览器恢复失败: {str(e)}")
                            raise
                    else:
                        self.driver.refresh()
                        time.sleep(1)
                    
        except Exception as e:
            error_msg = str(e)
            if "cannot join current thread" not in error_msg:  # 过滤已知无害错误
                self.ui.logger.log(f"抢票任务出错: {error_msg}")
            self.status = 4  # 失败
        finally:
            try:
                if self.driver:
                    self.driver.quit()
            except Exception as e:
                self.ui.logger.log(f"关闭浏览器时出错: {str(e)}")
            try:
                self.stop_ticket_task()
            except Exception as e:
                self.ui.logger.log(f"停止任务时出错: {str(e)}")

    def stop_ticket_task(self):
        """停止抢票任务"""
        self.is_running = False
        if self.thread and self.thread.is_alive() and threading.current_thread() != self.thread:
            self.thread.join(timeout=1)
            
        # 更新UI状态
        self.ui.ui.start_btn.config(state='normal')
        self.ui.ui.stop_btn.config(state='disabled')
        self.ui.ui.restart_btn.config(state='normal')
        self.ui.logger.log("抢票任务已停止")

    def retry_ticket_task(self):
        """重试抢票任务"""
        self.stop_ticket_task()
        time.sleep(1)  # 短暂延迟
        self.start_ticket_task()
        self.ui.logger.log("正在重试抢票任务...")
