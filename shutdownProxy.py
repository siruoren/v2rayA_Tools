import json
import requests
import subprocess

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

def connect_cancel(connect):
    '''取消节点的连接'''
    url = f"{HOST}/api/connection"
    requests.delete(url, json=connect, headers={"Authorization": TOKEN, "content-type": "application/json"})

def main():
    load_config()
    login()
    status = get_status()
    # 如果代理开启, 则停用代理
    if status["data"]["running"]:print(f"停用代理: {disable_Proxy()}")
    else:print("当前代理停用状态")
    connectedServer = status["data"]["touch"]["connectedServer"] # 获取连接的服务器
    if connectedServer: # 如果有连接的节点
        for connect in connectedServer:connect_cancel(connect)  # 则都取消

if __name__ == "__main__":
    main()