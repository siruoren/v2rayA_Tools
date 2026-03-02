import json
import requests
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

CONFIG = {}
HOST = ""
TOKEN = ""

def load_config():
    global CONFIG, HOST
    with open("config.json", "r", encoding='utf8') as f:
        CONFIG = json.load(f)
    HOST = f"http://{CONFIG['v2raya_ip']}:{CONFIG['webui_port']}"

def login():
    global TOKEN
    url = f"{HOST}/api/login"
    payload = {"username": CONFIG['username'],"password": CONFIG['password']}
    headers = {"content-type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    TOKEN = response.json()["data"]["token"]

def get_status():
    '''获取服务状态'''
    url = f"{HOST}/api/touch"
    response = requests.get(url, headers={"Authorization": TOKEN})
    return response.json()

def disable_Proxy():
    """禁用代理"""
    max_retries = 20
    for retry in range(max_retries):
        try:
            response = requests.delete(f"{HOST}/api/v2ray", headers={"Authorization": TOKEN}, timeout=30)
            response.raise_for_status()
            result = response.json()
            code = result.get("code", "UNKNOWN")
            if code == "SUCCESS":
                return code
            else:
                logging.warning(f"禁用代理尝试 {retry+1}/{max_retries} 失败: {code}")
        except Exception as e:
            logging.warning(f"禁用代理尝试 {retry+1}/{max_retries} 异常: {e}")
        if retry < max_retries - 1:
            time.sleep(1)  # 等待1秒后重试
    logging.error(f"禁用代理失败，已尝试 {max_retries} 次")
    return "ERROR"

def enable_Proxy():
    """启用代理"""
    max_retries = 20
    for retry in range(max_retries):
        try:
            response = requests.post(f"{HOST}/api/v2ray", headers={"Authorization": TOKEN}, timeout=30)
            response.raise_for_status()
            result = response.json()
            code = result.get("code", "UNKNOWN")
            if code == "SUCCESS":
                return code
            else:
                logging.warning(f"启用代理尝试 {retry+1}/{max_retries} 失败: {code}")
        except Exception as e:
            logging.warning(f"启用代理尝试 {retry+1}/{max_retries} 异常: {e}")
        if retry < max_retries - 1:
            time.sleep(1)  # 等待1秒后重试
    logging.error(f"启用代理失败，已尝试 {max_retries} 次")
    return "ERROR"

def main():
    """主函数"""
    start_time = time.time()
    logging.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 开始重启代理服务...")
    
    # 加载配置
    logging.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 加载配置文件...")
    try:
        load_config()
        logging.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 配置加载成功")
    except Exception as e:
        logging.error(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 加载配置失败: {e}")
        return
    
    # 登录
    logging.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 登录 v2rayA...")
    try:
        login()
        logging.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 登录成功")
    except Exception as e:
        logging.error(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 登录失败: {e}")
        return
    
    # 等待2秒
    logging.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 等待2秒...")
    time.sleep(2)
    
    # 禁用代理
    logging.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 禁用代理...")
    disable_result = disable_Proxy()
    logging.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 禁用代理结果: {disable_result}")
    
    # 等待1秒
    logging.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 等待1秒...")
    time.sleep(1)
    
    # 启用代理
    logging.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 启用代理...")
    enable_result = enable_Proxy()
    logging.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 启用代理结果: {enable_result}")
    
    # 完成
    end_time = time.time()
    logging.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 代理重启完成！")
    logging.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 总耗时: {end_time - start_time:.2f} 秒")
    
    # 检查代理状态
    try:
        status = get_status()
        running_status = status.get("data", {}).get("running", False)
        logging.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 代理当前状态: {'运行中' if running_status else '已停止'}")
    except Exception as e:
        logging.warning(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] 检查代理状态失败: {e}")

if __name__ == "__main__":
    main()
