# frps_fw

## 通过frp的plugin实现的封IP，防止并发测用户行为，具体可以查看

https://github.com/fatedier/frp/blob/dev/doc/server_plugin.md

## server端配置如下：

```toml
[[httpPlugins]]
name = "login-manager"
addr = "127.0.0.1:8082"
path = "/handler"
ops = ["Login"]

[[httpPlugins]]
name = "newuserconn-manager"
addr = "127.0.0.1:8082"
path = "/handler"
ops = ["NewUserConn"]
```

## 客户端配置如下：

```toml
user = "akin"  #对应列表中的白名单
serverAddr = "frpc.akin.com"
serverPort = 7018
auth.token = "asdfasdfasdfasdf"

[[proxies]]
name = "test-tcp"
type = "tcp"
localIP = "127.0.0.1"
localPort = 22
remotePort = 6060
```

## 用户需要配置：

```python
...
user_list=['fh21','akin','admin']  
token = "admin.."      #token,添加IP白名单时需要
DENYNUM = 10   #
...

#更详细请查看官网文档说明
```

## 安装

```shell
pip install -r requirements.txt
python frps_fw.py 
 * Running on http://0.0.0.0:8082/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 336-837-330 
```