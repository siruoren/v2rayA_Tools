import json
import requests
import subprocess
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

NUMBER_OF_NODE_GROUP_MEMBERS = 50
'''节点延迟测试时，节点数量过多时就需要分组请求，每一组的节点数量上限'''
CONFIG = {}
HOST = ""
TOKEN = ""
def load_config():
    global CONFIG, HOST, NUMBER_OF_NODE_GROUP_MEMBERS
    with open("config.json", "r", encoding='utf8') as f:CONFIG = json.load(f)
    HOST = f"http://{get_container_ip(CONFIG['v2raya_ip'])}:{CONFIG['webui_port']}"
    NUMBER_OF_NODE_GROUP_MEMBERS = CONFIG['number_of_node_group_members']

def get_container_ip(ip):
    '''获取容器的IP地址'''
    return ip

def login():
    global TOKEN
    url = f"{HOST}/api/login"
    payload = {"username": CONFIG['username'],"password": CONFIG['password']}
    headers = {"content-type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    TOKEN = response.json()["data"]["token"]

def get_status():
    url = f"{HOST}/api/touch"
    response = requests.get(url, headers={"Authorization": TOKEN})
    return response.json()

def disable_Proxy():
    return requests.delete(f"{HOST}/api/v2ray", headers={"Authorization": TOKEN}).json()["code"]

def enable_Proxy():
    return requests.post(f"{HOST}/api/v2ray", headers={"Authorization": TOKEN}).json()["code"]

def updateSub(id):
    url = f"{HOST}/api/subscription"
    payload = {"id": id,"_type": "subscription"}
    headers = {"authorization": TOKEN,"content-type": "application/json"}
    response = requests.request("PUT", url, json=payload, headers=headers)

def main():
    load_config()
    login()
    # 获取服务状态
    status = get_status()
    start_time = int(time.time())
    sub_info = status["data"]["touch"]["subscriptions"]
    if status["data"]["running"]:
        logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 停用代理: {disable_Proxy()}")
    for sub in sub_info:
        sub_start_time = int(time.time())
        updateSub(sub["id"])
        sub_end_time = int(time.time())
        logging.info(f'''{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 更新订阅 {sub.get("remarks", f"ID: {sub['id']}")} 耗时 {sub_end_time - sub_start_time} 秒''')
    end_time = int(time.time())
    if status["data"]["running"]:
        logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 启用代理: {enable_Proxy()}")
    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 更新了{len(sub_info)}个订阅, 共耗时 {end_time - start_time} 秒")

if __name__ == "__main__":

    main()
