# -*- coding: utf-8 -*-

import socket
import select
import sys

class SocketServer:
    def __init__(self, host, port, backlog=10, bufsize=4096):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.bufsize = bufsize
        self.server_sock = None
        self.sock_list = []
        self.client_sock_table = {}

    def start(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket created")

        try:
            self.server_sock.bind((self.host, self.port))
            print("Socket bound")
            self.server_sock.listen(self.backlog)
            print("Socket listening")
            self.sock_list = [self.server_sock]
            self.client_sock_table = {}

            while True:
                r_ready_sockets, _, _ = select.select(self.sock_list, [], [])
                for sock in r_ready_sockets:
                    if sock == self.server_sock:
                        self.accept_connection()
                    else:
                        self.handle_client_message(sock)

        except Exception as e:
            print("Exception!")
            print(e)
        finally:
            self.server_sock.close()

    def send_to(self, sock, msg):
        try:
            sock.send(msg.encode())
            return True
        except:
            sock.close()
            return False

    def broadcast(self, msg):
        for sock in self.sock_list:
            if not self.send_to(sock, msg):
                self.sock_list.remove(sock)

    def accept_connection(self):
        conn, address = self.server_sock.accept()
        self.sock_list.append(conn)
        self.client_sock_table[address[1]] = conn
        self.sock_list.remove(self.server_sock)
        self.broadcast("ポート" + str(address[1]) + "番のユーザーが接続しました")
        self.sock_list.append(self.server_sock)
        print(str(address) + " is connected")

    def handle_client_message(self, sock):
        try:
            b_msg = sock.recv(self.bufsize)
            msg = b_msg.decode('utf-8')
            if len(msg) == 0:
                sock.close()
                self.sock_list.remove(sock)
            else:
                sender_port = None
                for key, val in self.client_sock_table.items():
                    if val == sock:
                        sender_port = key
                        break
                if sender_port is not None:
                    self.sock_list.remove(self.server_sock)
                    self.broadcast(str(sender_port) + ":" + msg)
                    self.sock_list.append(self.server_sock)
        except:
            sock.close()
            self.sock_list.remove(sock)
            self.sock_list.remove(self.server_sock)
            self.broadcast("someone disconnected")
            self.sock_list.append(self.server_sock)


# 使用例
if __name__ == '__main__':
    host = '127.0.0.1'
    port = 50000
    backlog = 10
    bufsize = 4096

    server = SocketServer(host, port, backlog, bufsize)
    server.start()