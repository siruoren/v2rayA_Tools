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

def del_sub(sub_url_head):
    load_config()
    login()
    del_list = []
    # 获取服务状态
    status = get_status()
    sub_info = status["data"]["touch"]["subscriptions"]
    for sub in sub_info:
        if sub_url_head in sub["address"] :
            item = {}
            item["id"] = sub["id"]
            item["address"]= sub["address"]
            del_list.append(item)
    if len(del_list) > 7:
        for del_id in del_list[0:5]:
            max_retries = 20
            for retry in range(max_retries):
                try:
                    # 删除订阅
                    url = f"{HOST}/api/touch"
                    payload = {"touches": [{"id": del_id["id"], "_type": "subscription"}]}
                    headers = {"authorization": TOKEN,"content-type": "application/json"}
                    response = requests.request("DELETE", url, json=payload, headers=headers, timeout=30)
                    if response.json()["code"] != 'FAIL':
                        logging.info(f"删除订阅id: {del_id['id']} {del_id['address']} 成功，尝试次数: {retry+1}")
                        break   
                    else:
                        logging.warning(f"删除订阅id: {del_id['id']} {del_id['address']} 失败，尝试次数: {retry+1}")
                        Exception(response.json()["code"])
                except Exception as e:
                    logging.warning(f"删除订阅id: {del_id['id']} {del_id['address']} 失败 (尝试 {retry+1}/{max_retries}): {e}")
                    if retry < max_retries - 1:
                        time.sleep(2)  # 等待2秒后重试
                    else:
                        logging.error(f"删除订阅id: {del_id['id']} {del_id['address']} 失败，已达到最大重试次数 {max_retries}")

if __name__ == "__main__":
    
    m_url=f"https://clashgithub.com/wp-content/uploads"
    del_sub(m_url)
    time.sleep(1)