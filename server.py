# -*- coding: utf-8 -*-

import socket
import select
from datetime import datetime
import csv


class Server:
    def __init__(self, host, port, backlog=10, bufsize=4096):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.bufsize = bufsize
        self.server_sock = None
        self.sock_list = []
        self.client_sock_table = {}
        self.sender_ip = None
        self.flag = -1
        self.pass_data = self.dict_from_csv("password.csv")
        

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
            count = 0
            while True:
                self.pass_data = self.dict_from_csv("password.csv")
                r_ready_sockets, _, _ = select.select(self.sock_list, [], [])
                for sock in r_ready_sockets:
                    if sock == self.server_sock:
                        self.accept_connection()
                    else:
                        if self.check_account(sock):
                            if self.flag == 3:
                                self.handle_client_message(sock, 1)
                            else:
                                # 登録してなかった時のメッセージを受け取る
                                b_msg = sock.recv(self.bufsize)
                                msg = b_msg.decode('utf-8')
                                self.broadcast("アカウント認証を行ってください")
                                self.send_to(sock, "パスワード")
                                if self.handle_client_message(sock, 3):
                                    self.broadcast("承認完了です。会話に参加できます")
                                else:
                                    self.broadcast("承認失敗です。再度試して下さい")
                        else:
                            # 登録してなかった時のメッセージを受け取る
                            b_msg = sock.recv(self.bufsize)
                            msg = b_msg.decode('utf-8')
                            # クライアントに登録するか確認
                            self.send_to(sock, "未登録")
                            if self.handle_client_message(sock, 2):
                                # 登録完了
                                # パスワードの設定
                                self.broadcast("パスワードを登録してください")
                                self.send_to(sock, "パスワード")
                                if self.handle_client_message(sock, 4):
                                    # パスワードオッケー
                                    self.broadcast("パスワード登録完了です。会話に参加できます")
                                else:
                                    self.broadcast("パスワード登録失敗")
                                    self.broadcast("仮登録からやり直して下さい")
                            else:
                                # 登録失敗
                                pass
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
        if self.server_sock in self.sock_list:
            self.sock_list.remove(self.server_sock)
        for sock in self.sock_list:
            if not self.send_to(sock, msg):
                self.sock_list.remove(sock)
        if self.server_sock not in self.sock_list:
            self.sock_list.append(self.server_sock)

    def accept_connection(self):
        conn, address = self.server_sock.accept()
        self.sock_list.append(conn)
        self.client_sock_table[address] = conn
        self.broadcast("IPアドレス" + str(address[0]) + "のユーザーが接続しました")
        print(str(address) + " is connected")


    def handle_client_message(self, sock, case):
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
                        sender_port = key[1]
                        sender_ip = key[0]
                        break
                if sender_port is not None:
                    if case == 1:
                        self.broadcast(str(sender_ip) + ":" + msg)
                        self.broadcast(f"送信時刻：{datetime.now()}")
                    if case == 2:
                        if msg == "yes":
                            self.broadcast("仮登録完了")
                            self.flag = 2
                        elif msg == "no":
                            self.broadcast("仮登録失敗")
                            self.flag = -1
                    if case == 3:
                        server_pass = self.pass_data[sender_ip]
                        if msg != "" and msg == server_pass:
                            self.flag = 3
                    if case == 4:
                        if msg != "":
                            with open('password.csv', 'a', newline='') as csvfile:
                                writer = csv.writer(csvfile)
                                writer.writerow([str(sender_ip), str(msg)])
                                self.flag = 3
                        else:
                            self.flag = -1
            if self.flag > 0:
                return True
            else:
                return False
        except:
            self.close_sock(sock)
    

    def check_account(self, sock):
        try:
            for key, val in self.client_sock_table.items():
                if val == sock:
                    self.sender_ip = key[0]
                    break
            if self.sender_ip is not None:
                if self.sender_ip in list(self.pass_data.keys()): 
                    return True
                else:
                    self.broadcast("新規登録手続きを行います")
                    return False
            else:
                return False
        except Exception as e:
            print("Exception!")
            print(e)
            self.close_sock(sock)
            return False
     

    def close_sock(self, sock):
        sock.close()
        self.sock_list.remove(sock)
        self.sock_list.remove(self.server_sock)
        self.broadcast("someone disconnected")
        self.sock_list.append(self.server_sock)


    def dict_from_csv(self, file_path):
        data = {}
        with open(file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                data[row[0]] = row[1]
        return data


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 50000
    server = Server(host, port)
    server.start()