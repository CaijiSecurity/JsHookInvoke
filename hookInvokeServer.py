import os
import json
import socket
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from multiprocessing import Process

Config = {
    "HTTP_INVOKE_SERVER_HOST": "127.0.0.1",
    "HTTP_INVOKE_SERVER_PORT": 8992,
    "HTTP_INVOKE_SERVER_PATH": "/invokeServer",
    "HTTP_INVOKE_AGENT_JS_PATH": "/hookAgent.js",
    "HOOK_REQUEST_KEY": "justd01t",
    "SCRIPT_PARENT_DIR": os.path.split(os.path.realpath(__file__))[0]
}

Replace_Rule_Tmpl = '''
请将以下自动替换规则配置到burpsuite：
Type: Response body

<head>
    ↓
  替换成
    ↓
<head><script type="text/javascript" src="http://{host}:{port}{agent_js_path}"></script>

'''

class CaijiSecHTTPServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, config_dict, bind_and_activate: bool = ...) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.config_dict = config_dict

    def finish_request(self, request, client_address) -> None:
        # return super().finish_request(request, client_address)
        self.RequestHandlerClass(request, client_address, self)


class HookInvokeServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        Config = self.server.config_dict

        # 测试demo部分 开始 #
        if self.path == "/test.html":
            with open(os.path.join(Config["SCRIPT_PARENT_DIR"], "testwww/test.html"), "r") as f:
                res_data = f.read()
            self._caiji_easy_response(res_data, "text/html;charset=UTF-8")
        elif self.path == "/test.js":
            with open(os.path.join(Config["SCRIPT_PARENT_DIR"], "testwww/test.js"), "r") as f:
                res_data = f.read()
            self._caiji_easy_response(res_data, "application/javascript;charset=UTF-8")
        # 测试demo部分 结束 #

        elif self.path == Config["HTTP_INVOKE_AGENT_JS_PATH"]:
            with open(os.path.join(Config["SCRIPT_PARENT_DIR"], "hookAgent.js"), "r") as f:
                res_data = f.read()
            res_data = res_data.replace("{{hook_invoke_server_url}}", "http://{0}:{1}{2}".format(
                Config["HTTP_INVOKE_SERVER_HOST"],
                Config["HTTP_INVOKE_SERVER_PORT"],
                Config["HTTP_INVOKE_SERVER_PATH"]
            ))
            self._caiji_easy_response(res_data, "application/javascript;charset=UTF-8")
        elif self.path == Config["HTTP_INVOKE_SERVER_PATH"]:
            res_data = "testHelloGet你好"
            self._caiji_easy_response(res_data, "text/plain;charset=UTF-8")
        else:
            self._caiji_easy_response("开发中...", "text/html;charset=UTF-8")


    def do_POST(self):
        Config = self.server.config_dict
        if self.path == Config["HTTP_INVOKE_SERVER_PATH"]:
            req_datas = self.rfile.read(int(self.headers['content-length']))
            req = req_datas.decode('utf-8')
            print("[HookInvokeServerReq]接收到的内容")
            print(req)
            print("[HookInvokeServerReq]" + "-"*50)
            res_data = "OK"
            self._caiji_easy_response(res_data, "text/plain;charset=UTF-8")
        else:
            print("[HookServer]非预期的请求路径，丢弃！")
            return


    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
        self.end_headers()
    

    def _caiji_easy_response(self, res_data, content_type):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
        self.end_headers()

        print("[HookInvokeServerResp]返回的内容")
        print(res_data)
        print("[HookInvokeServerResp]" + "-"*50)
        
        self.wfile.write(res_data.encode("utf-8"))


def start_hook_invoke_server(config_dict):
    hook_host = (config_dict["HTTP_INVOKE_SERVER_HOST"], config_dict["HTTP_INVOKE_SERVER_PORT"])
    hook_server = CaijiSecHTTPServer(hook_host, HookInvokeServerHandler, config_dict)
    print("Starting Hook Invoke Server, listen at: http://%s:%s" % hook_host)
    hook_server.serve_forever()


def get_ipv4_addr():
    ipv4_addrs = []
    for addrinfo in socket.getaddrinfo(socket.gethostname(), None):
        if addrinfo[0] == socket.AddressFamily.AF_INET and addrinfo[1] == socket.SocketKind.SOCK_STREAM:
            ipv4_addrs.append(addrinfo[4][0])
    return ipv4_addrs


def main():
    # print(get_ipv4_addr())
    ipv4_addr_list = get_ipv4_addr()
    if len(ipv4_addr_list) > 0:
        if len(ipv4_addr_list) > 1:
            print("检测到本地有以下 {0} 个ipv4地址，请选择要监听的地址：".format(
                len(ipv4_addr_list)
            ))
            for idx in range(len(ipv4_addr_list)):
                print("[{0}] {1}".format(
                    idx + 1,
                    ipv4_addr_list[idx]
                ))
            try:
                chose_ipv4_addr = ipv4_addr_list[int(input("请输入编号[1]：")) - 1]
            except:
                chose_ipv4_addr = ipv4_addr_list[0]
        else:
            chose_ipv4_addr = ipv4_addr_list[0]
        print("将会监听地址：{0}".format(
            chose_ipv4_addr
        ))
        Config["HTTP_INVOKE_SERVER_HOST"] = chose_ipv4_addr
    print(Replace_Rule_Tmpl.format(
        host = Config["HTTP_INVOKE_SERVER_HOST"],
        port = Config["HTTP_INVOKE_SERVER_PORT"],
        agent_js_path = Config["HTTP_INVOKE_AGENT_JS_PATH"]
    ))

    hook_invoke_server_process = Process(target=start_hook_invoke_server, args=(Config,))
    hook_invoke_server_process.start()
    
    hook_invoke_server_process.join()

if __name__ == '__main__':
    main()
