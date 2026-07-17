import json
import requests
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
    with open("config.json", "r", encoding='utf8') as f:
        CONFIG = json.load(f)
    HOST = f"http://{get_container_ip(CONFIG['v2raya_ip'])}:{CONFIG['webui_port']}"
    NUMBER_OF_NODE_GROUP_MEMBERS = CONFIG['number_of_node_group_members']

def get_container_ip(ip):
    '''获取容器的IP地址'''
    return ip

def login():
    global TOKEN
    url = f"{HOST}/api/login"
    payload = {"username": CONFIG['username'], "password": CONFIG['password']}
    headers = {"content-type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    TOKEN = response.json()["data"]["token"]

def get_status():
    '''获取服务状态'''
    url = f"{HOST}/api/touch"
    response = requests.get(url, headers={"Authorization": TOKEN})
    return response.json()

def get_outbounds():
    '''获取出站列表'''
    url = f"{HOST}/api/outbounds"
    response = requests.get(url, headers={"Authorization": TOKEN})
    return response.json()["data"]["outbounds"]

def updateSub(sub_id):
    '''更新订阅源'''
    url = f"{HOST}/api/subscription"
    payload = {"id": sub_id, "_type": "subscription"}
    headers = {"authorization": TOKEN, "content-type": "application/json"}
    max_retries = 10
    for retry in range(max_retries):
        try:
            response = requests.request("PUT", url, json=payload, headers=headers, timeout=30)
            if response.json().get("code") != "FAIL":
                logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 更新订阅 ID: {sub_id} 成功")
                return True
            else:
                logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 更新订阅 ID: {sub_id} 失败, 尝试 {retry+1}/{max_retries}")
        except Exception as e:
            logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 更新订阅 ID: {sub_id} 异常 (尝试 {retry+1}/{max_retries}): {e}")
        if retry < max_retries - 1:
            time.sleep(2)
    logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 更新订阅 ID: {sub_id} 失败, 已达最大重试次数")
    return False

def connect_node(node_id, sub_id, outbound):
    '''连接单个节点到指定出站'''
    url = f"{HOST}/api/connection"
    payload = {
        "id": node_id,
        "_type": "subscriptionServer",
        "sub": sub_id,
        "outbound": outbound
    }
    headers = {"Authorization": TOKEN, "content-type": "application/json"}
    max_retries = 5
    for retry in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                return True
        except Exception as e:
            logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 连接节点失败 (尝试 {retry+1}/{max_retries}): {e}")
        if retry < max_retries - 1:
            time.sleep(1)
    return False

def get_unconnected_nodes(status, sub_num):
    '''获取当前订阅下未连接的节点列表
    返回: (未连接节点信息列表, 订阅名称)
    '''
    sub_id = int(sub_num) - 1
    sub_name = ""
    sub_nodes = []
    for sub in status["data"]["touch"]["subscriptions"]:
        if sub["id"] == int(sub_num):
            sub_nodes = sub["servers"]
            sub_name = sub.get("remarks", f"ID: {sub['id']}, host: {sub['host']}")
            break

    if not sub_nodes:
        return [], sub_name

    # 获取当前已连接的节点ID (属于该订阅的)
    connected_node_ids = set()
    for connect in status["data"]["touch"].get("connectedServer", []):
        # connectedServer 中 sub 字段为 0-based 索引
        if connect.get("sub") == sub_id:
            connected_node_ids.add(connect.get("id"))

    # 找出未连接的节点
    unconnected_nodes = []
    for node in sub_nodes:
        if node["id"] not in connected_node_ids:
            unconnected_nodes.append(node)

    return unconnected_nodes, sub_name

def main(sub_num):
    '''主流程: 更新订阅 -> 检查未连接节点 -> 逐个添加连接'''
    load_config()
    login()

    start_time = int(time.time())

    # 1. 获取当前状态
    status = get_status()
    is_running = status["data"]["running"]

    # 2. 更新订阅 (不停代理)
    sub_start_time = int(time.time())
    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 开始更新订阅 ID: {sub_num} (代理保持{'运行' if is_running else '停止'}状态)")
    if not updateSub(sub_num):
        logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 更新订阅失败, 跳过后续操作")
        return
    sub_end_time = int(time.time())
    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 更新订阅耗时 {sub_end_time - sub_start_time} 秒")

    # 3. 更新后重新获取状态, 检查未连接节点
    time.sleep(2)
    status = get_status()
    unconnected_nodes, sub_name = get_unconnected_nodes(status, sub_num)

    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 订阅 [{sub_name}] 共有 {len(status['data']['touch']['subscriptions'][[s['id'] for s in status['data']['touch']['subscriptions']].index(int(sub_num))]['servers'])} 个节点, 未连接 {len(unconnected_nodes)} 个")

    if not unconnected_nodes:
        logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 所有节点均已连接, 无需操作")
        return

    # 4. 获取出站列表
    outbounds = get_outbounds()
    sub_id = int(sub_num) - 1

    # 5. 逐个添加连接
    connected_count = 0
    failed_count = 0
    for idx, node in enumerate(unconnected_nodes):
        node_name = node.get("name", f"ID: {node['id']}")
        logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> [{idx+1}/{len(unconnected_nodes)}] 开始连接节点: {node_name}")

        success = True
        for outbound in outbounds:
            if not connect_node(node["id"], sub_id, outbound):
                success = False
                logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 节点 {node_name} 连接到出站 {outbound} 失败")

        if success:
            connected_count += 1
            logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 节点 {node_name} 已连接到所有出站")
        else:
            failed_count += 1

        # 逐个添加, 每次间隔1秒
        if idx < len(unconnected_nodes) - 1:
            time.sleep(1)

    end_time = int(time.time())
    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 完成! 成功连接 {connected_count} 个, 失败 {failed_count} 个, 共耗时 {end_time - start_time} 秒")

if __name__ == "__main__":
    load_config()
    login()
    for sub_num in range(1, int(CONFIG["apply_subscription_id"]) + 1):
        try:
            main(sub_num)
        except Exception as e:
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} --> 处理订阅 ID: {sub_num} 异常: {e}")
