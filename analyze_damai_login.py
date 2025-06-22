import requests
from bs4 import BeautifulSoup
import re

def analyze_login_page():
    # 获取登录页面
    login_url = "https://passport.damai.cn/login"
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print("正在获取登录页面...")
        response = session.get(login_url, headers=headers)
        response.raise_for_status()
        
        print("\n=== 页面分析结果 ===")
        
        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. 查找所有表单
        forms = soup.find_all('form')
        print(f"\n找到 {len(forms)} 个表单:")
        for i, form in enumerate(forms, 1):
            print(f"\n表单 {i}:")
            print(f"ID: {form.get('id', '无')}")
            print(f"Class: {form.get('class', '无')}")
            print(f"Action: {form.get('action', '无')}")
            print(f"Method: {form.get('method', '无')}")
            
            # 查找表单中的输入字段
            inputs = form.find_all('input')
            print(f"\n包含 {len(inputs)} 个输入字段:")
            for inp in inputs:
                print(f"  name={inp.get('name', '无')}, type={inp.get('type', '无')}, id={inp.get('id', '无')}")
        
        # 2. 查找登录相关元素
        print("\n=== 登录相关元素 ===")
        
        # 查找用户名输入框
        username_fields = soup.find_all('input', {'name': re.compile(r'user|name|login|account', re.I)})
        print(f"\n找到 {len(username_fields)} 个用户名输入字段:")
        for field in username_fields:
            print(f"  name={field.get('name')}, id={field.get('id')}, type={field.get('type')}")
        
        # 查找密码输入框
        password_fields = soup.find_all('input', {'type': 'password'})
        print(f"\n找到 {len(password_fields)} 个密码输入字段:")
        for field in password_fields:
            print(f"  name={field.get('name')}, id={field.get('id')}")
        
        # 查找登录按钮
        login_buttons = soup.find_all('button', string=re.compile(r'登录|登陆|sign in', re.I))
        login_buttons += soup.find_all('input', {'type': 'submit', 'value': re.compile(r'登录|登陆|sign in', re.I)})
        print(f"\n找到 {len(login_buttons)} 个登录按钮:")
        for btn in login_buttons:
            print(f"  text={btn.get_text(strip=True)}, id={btn.get('id')}, name={btn.get('name')}")
        
        # 3. 查找可能的验证码元素
        print("\n=== 验证码相关元素 ===")
        captcha_imgs = soup.find_all('img', {'src': re.compile(r'captcha|verify|code', re.I)})
        print(f"找到 {len(captcha_imgs)} 个验证码图片:")
        for img in captcha_imgs:
            print(f"  src={img.get('src')}, id={img.get('id')}")
        
        # 4. 查找隐藏字段
        hidden_fields = soup.find_all('input', {'type': 'hidden'})
        print(f"\n找到 {len(hidden_fields)} 个隐藏字段:")
        for field in hidden_fields:
            print(f"  name={field.get('name')}, value={field.get('value')}")
            
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    analyze_login_page()
