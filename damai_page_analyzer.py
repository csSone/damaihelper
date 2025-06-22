from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import os

def _get_damai_cookies(driver):
    """获取damai.com的cookie"""
    try:
        # 访问登录页面并直接开始等待
        driver.get("https://passport.damai.cn/login")
        print("请手动完成登录操作，等待30秒...")
        time.sleep(30)  # 固定等待30秒
        
        # 获取所有cookie
        cookies = driver.get_cookies()
        if not cookies:
            print("警告: 未获取到任何cookie")
            return None
            
        # 保存cookie
        with open("damai_cookies.json", "w") as f:
            json.dump(cookies, f)
            
        # 关闭当前页面
        driver.close()
            
        return cookies
    except Exception as e:
        print(f"获取cookie失败: {e}")
        return None

def analyze_damai_page(url):
    # Set up Chrome options to disable images
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--blink-settings=imagesEnabled=false")
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheet": 2
    }
    options.add_experimental_option("prefs", prefs)
    
    # Initialize WebDriver with robust fallback options
    service = None
    driver = None
    chromedriver_path = "C:/Users/Semon/.wdm/drivers/chromedriver/win64/137.0.7151.119/chromedriver-win32/chromedriver.exe"
    
    # 1. Try local chromedriver.exe first (with full path verification)
    if os.path.exists(chromedriver_path) and chromedriver_path.endswith('.exe'):
        try:
            service = Service(executable_path=chromedriver_path)
            driver = webdriver.Chrome(service=service, options=options)
            # Quick test to verify driver works
            driver.get("about:blank")
            driver.back()
        except Exception as e:
            print(f"Local chromedriver is invalid: {e}")
            os.remove(chromedriver_path)  # Remove invalid driver
            service = None
    
    # 2. Try ChromeDriverManager if local driver not available
    if service is None:
        try:
            manager = ChromeDriverManager()
            # Force correct executable path
            driver_path = manager.install()
            if not driver_path.endswith('.exe'):
                driver_path += '.exe'
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print("Failed to initialize ChromeDriver:")
            print(f"Error: {e}")
            raise
        
        # Save cookies for future use
        cookies = driver.get_cookies()
        with open("damai_cookies.json", "w") as f:
            json.dump(cookies, f)
    
    try:
        # 先获取cookie
        cookies = _get_damai_cookies(driver)
        if not cookies:
            print("警告: 未能获取有效cookie，继续分析但可能受限")
        
        # Navigate to the page (新页面)
        driver.get(url)
        
        # 添加cookie到当前会话
        if cookies:
            driver.delete_all_cookies()  # 先清除现有cookie
            for cookie in cookies:
                driver.add_cookie(cookie)
            driver.refresh()  # 刷新使cookie生效
        time.sleep(3)  # Wait for page to load
        
        # Find only buttons and text elements
        all_elements = driver.find_elements(By.XPATH, "//button|//input[@type='button' or @type='submit']|//*[text()]")
        
        # Prepare analysis data
        analysis = {
            "page_title": driver.title,
            "page_url": driver.current_url,
            "elements": [],
            "potential_buy_buttons": [],
            "all_buttons": []
        }
        
        # Analyze each element
        for element in all_elements:
            try:
                element_data = {
                    "tag": element.tag_name,
                    "text": element.text.strip() if element.text else "",
                    "id": element.get_attribute("id"),
                    "class": element.get_attribute("class"),
                    "xpath": get_xpath(element),
                    "visible": element.is_displayed(),
                    "enabled": element.is_enabled()
                }
                
                analysis["elements"].append(element_data)
                
                # Check if element is a button
                if (element.tag_name.lower() == "button" or 
                    (element.tag_name.lower() == "input" and 
                     element.get_attribute("type") in ["button", "submit"])):
                    analysis["all_buttons"].append(element_data)
                    
                # Check if element might be a buy button
                if (("buy" in (element.get_attribute("class") or "").lower() or 
                     "submit" in (element.get_attribute("class") or "").lower() or
                     "btn" in (element.get_attribute("class") or "").lower()) and
                    element.is_displayed()):
                    analysis["potential_buy_buttons"].append(element_data)
                    
            except Exception as e:
                continue
        
        # Save analysis to file
        with open("damai_page_analysis.json", "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
            
        print("Analysis saved to damai_page_analysis.json")
        
        # Print potential buy buttons
        print("\nPotential buy buttons found:")
        for btn in analysis["potential_buy_buttons"]:
            print(f"- {btn['text']} (XPath: {btn['xpath']})")
            
        # Print all buttons
        print("\nAll buttons found:")
        for btn in analysis["all_buttons"]:
            print(f"- {btn['text']} (Tag: {btn['tag']}, XPath: {btn['xpath']})")
            
        return analysis
        
    finally:
        if driver is not None:
            driver.quit()

def get_xpath(element):
    """Generate XPath for an element"""
    components = []
    child = element
    while child.tag_name != 'html':
        parent = child.find_element(By.XPATH, '..')
        siblings = parent.find_elements(By.XPATH, f'*[name()="{child.tag_name}"]')
        if len(siblings) == 1:
            components.insert(0, child.tag_name)
        else:
            index = siblings.index(child) + 1
            components.insert(0, f"{child.tag_name}[{index}]")
        child = parent
    return '/' + '/'.join(components)

if __name__ == "__main__":
    url = "https://m.damai.cn/shows/seat.html?itemId=934567114275&userPromotion=false&toDxOrder=true&quickBuy=0&privilegeActId=&channel=damai_app&performId=234412094&skuId=5826090165269&projectId=228354020&signKey=cEl2bXVYXw9iRVl%2BTk11eXdff2hxW10KakdVelo3GBcTIgoSBzI6bBIgOB9aCz09ER8uMDUEHVE2B1d%2FSEpke3haem9nDgZUPBpWeUlUZXlyWX9qcVhfHjAbASMXQ2N4bFl%2BbHFdWgFgRksvFhQ5JntbeXJyXFsIYkBVfEheNScsBSFldF1FC2JGXnxMSGRxZgkgMi4DUg1jWF59S0hleHhddngiAgVXPU9YfFVLZ3pzWntudFVPWzwYAiJCTWY%3D&rtc=1"
    analyze_damai_page(url)
