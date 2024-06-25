import http.server
import socketserver
import webbrowser
import os
import sys
from threading import Thread
import urllib.parse
import requests
import argparse

class ProxySPAHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 解析请求的路径
        url_parts = urllib.parse.urlparse(self.path)
        request_file_path = url_parts.path.strip("/")

        # 检查是否是媒体文件请求
        if request_file_path.startswith('media/'):
            # 构建代理 URL
            proxy_url = f'http://766677.xyz/{request_file_path}'
            
            try:
                # 发送代理请求
                response = requests.get(proxy_url)
                
                # 设置响应头
                self.send_response(response.status_code)
                for header, value in response.headers.items():
                    self.send_header(header, value)
                self.end_headers()
                
                # 发送响应内容
                self.wfile.write(response.content)
            except requests.RequestException as e:
                self.send_error(500, f"代理错误: {str(e)}")
            return

        # 如果请求的不是文件，返回 index.html
        if not os.path.exists(request_file_path) or os.path.isdir(request_file_path):
            self.path = '/index.html'
        
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def start_server(port, directory):
    os.chdir(directory)
    Handler = ProxySPAHandler
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Web服务器已启动，地址：http://localhost:{port}")
        print(f"服务目录: {directory}")
        httpd.serve_forever()

def open_browser(port):
    webbrowser.open(f"http://localhost:{port}")

def main():
    parser = argparse.ArgumentParser(description="带代理功能的SPA服务器")
    parser.add_argument("--port", type=int, default=5173, help="服务端口 (默认: 5173)")
    parser.add_argument("--dir", type=str, default=".", help="要服务的目录 (默认: 当前目录)")
    args = parser.parse_args()

    # 确保目录存在
    if not os.path.exists(args.dir):
        print(f"错误: 目录 '{args.dir}' 不存在。")
        sys.exit(1)

    # 在新线程中启动服务器
    server_thread = Thread(target=start_server, args=(args.port, args.dir))
    server_thread.daemon = True
    server_thread.start()

    # 稍微延迟以确保服务器已启动
    import time
    time.sleep(1)

    # 打开浏览器
    open_browser(args.port)

    # 保持主线程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n服务器已停止。")

if __name__ == "__main__":
    main()