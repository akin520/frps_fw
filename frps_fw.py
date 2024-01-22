#!/usr/bin/env python
#coding:utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Flask, request,jsonify
import json
import redis
import time

app = Flask(__name__)

user_list=['fh21','akin','admin']  #用户白名单列表
token = "admin.."  #添加白名单的时候需要
DENYNUM = 10

def writelog(msg):
    f = open("/tmp/frps_post.log","a+")
    f.write(str(msg)+"\n")
    f.close()

def getsetip(ip):
    client = redis.Redis(host='127.0.0.1', port=6379, db=0)
    r = client.incr(ip)
    client.expire(ip, 60*2)
    return r

def hashop(ip,key,op="hget"):
    client = redis.Redis(host='127.0.0.1', port=6379, db=0)
    if op == "hexists":
        r = client.hexists(key,ip)
    elif op == "hset":
        r = client.hset(key,ip, time.time())
    elif op == "hget":
        r = client.hget(key,ip)
    elif op == "hdel":
        r = client.hdel(key,ip)
    elif op == "hgetall":
        r = client.hgetall(key)
    elif op == "hkeys":
        r = client.hkeys(key)
    else:
        r = None
    return r

@app.route('/handler', methods=["POST", "GET"])
def handler():
    if request.method == "GET":
        print('GET访问')
        data = [{'提示': "非法访问"}]
        return json.dumps(data, ensure_ascii=False), 403
    try:
        # 不拒绝连接，保持不变；即不对内容进行任何操作
        response_data = {"reject": False, "unchange": True}
        print('POST访问')
        data = request.json
        #print(data)
        writelog(json.dumps(data))
        
        if data['op'] == "NewUserConn":
            ip = data['content']['remote_addr'].split(":")[0]
            num = getsetip(ip)
            exists = hashop(ip,"frps_deny_hash",op="hexists")
            allow = hashop(ip,"frps_allow_hash",op="hkeys")
            print(num,exists,allow)
            if ip not in allow and (num > DENYNUM or exists):    #2分钟大于10次请求拒绝
                # 拒绝连接，非法用户
                hashop(ip, "frps_deny_hash", op="hset")
                response_data = {"reject": True, "reject_reason": "deny user"}
        elif data['op'] == "Login":
            user = data['content']['user']
            if user not in user_list:
                response_data = {"reject": True, "reject_reason": "invalid user"}
        print(response_data)
        return json.dumps(response_data, ensure_ascii=False), 200
    except Exception as e:
        print(repr(e))
        return 404

@app.route("/fw/", methods=["GET"])
def fw():
    if request.method == "GET":
        token_str = request.args.get("token")
        ip_str = request.args.get("ip", None)
        op_str = request.args.get("op", None)
        print(token_str)
        if token_str == token and ip_str and op_str:
            r = hashop(ip_str, "frps_deny_hash", op=op_str)
            return json.dumps({"msg":r}, ensure_ascii=False), 200
        else:
            return json.dumps({"msg":"op or ip error"}, ensure_ascii=False), 200
    else:
        return json.dumps({"msg":403}, ensure_ascii=False), 403

if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=8082)
