# v2rayA_Tools

[v2rayA/v2rayA](https://github.com/v2rayA/v2rayA/) 的第三方工具，仅适用于 Docker 部署的 v2rayA ，能够自动对节点测试HTTP时延，择优（或随机）绑定到出站；停用代理并将出站上的节点解除绑定；自动更新某个订阅；自动更新全部订阅。

### config.json

```json
{
    "v2raya_container_name": "v2rayA",
    "webui_port": 2017,
    "forced_reset_proxy": true,
    "username": "v2rayA_webui_username",
    "password": "v2rayA_webui_passwore",
    "apply_subscription_id": 1,
    "number_of_node_group_members": 110,
    "random_selected_node": true,
    "node_name_blacklist":[],
    "node_protocol_blacklist":[],
    "v2raya_config": "/home/v2raya/config.json"
}
```

| 键名                         | 值的属性 | 说明                                                         |
| ---------------------------- | -------- | ------------------------------------------------------------ |
| v2raya_container_name        | str      | v2rayA 的容器名                                              |
| webui_port                   | int      | v2rayA 的 webui 端口，默认是2017                             |
| forced_reset_proxy           | bool     | 为`true`时强制重设代理<br>为`false`时会先测试http入站端口，有端口异常才会重设代理 |
| username                     | str      | 用户名                                                       |
| password                     | str      | 密码                                                         |
| apply_subscription_id        | int      | 应用的订阅的id数，每次只会测试订阅数的节点                     |
| number_of_node_group_members | int      | 若有大量节点，则分多次测试，每次测试的节点数量上限。<br>例如共有650个节点，`number_of_node_group_members`值为100，则共分1次测试，前6次测试100个节点，第7次测试剩余的50个节点 |
| random_selected_node         | bool     | 假设共有10个出站<br>为`true`时会从测试后可用的节点里随机选出10个绑定出站<br>为`false`时会将可用的节点排序，选择延迟最低的10个节点绑定出站 |
| node_name_blacklist          | list     | 这是一个列表，当节点名中的某个字符包含在其中，则该节点不会参与测试 |
| node_protocol_blacklist      | list     | 这是一个列表，当节点所用的协议包含在其中，则该节点不会参与测试 |
| v2raya_config                | str      | v2raya的配置文件在宿主机里的路径，该配置文件在容器里，须要映射到宿主机上。见[v2RayA文档](https://v2raya.org/docs/prologue/installation/docker/#%E8%BF%90%E8%A1%8C-v2raya)“传统后端的示例”里`-v /etc/v2raya:/etc/v2raya \`即为配置文件所在目录。举例，你可以改成`-v /home/v2raya:/etc/v2raya \`,那么`v2raya_config`则为`/home/v2raya/config.json` |

### main.py

自动对节点测试HTTP时延，择优 / 随机绑定到出站。

### shutdownProxy.py

停用代理并将出站上的节点解除绑定。

### updateSub_one_sub.py

更新id为`apply_subscription_id`的订阅，当代理开启时，会暂时关闭代理，整个过程大约三秒（PS：若不暂时关闭代理，更新订阅大约需要两分钟，期间WebUI是无法工作的）

### updateSub.py

更新全部订阅，当代理开启时，会暂时关闭代理，整个过程大约三秒。
