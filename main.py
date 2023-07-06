from server import SocketServer
from client import ChatApp
import threading
import time

def run_server():
    host = '127.0.0.1'
    port = 50000
    server = SocketServer(host, port)
    server.start()

if __name__ == "__main__":
    # サーバーの起動
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # クライアントの起動
    host = '127.0.0.1'
    port = 50000

    app = ChatApp(host, port)
    app.start()
    


    