import tkinter as tk
import socket
import threading
import select
from server import SocketServer

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.stocked_msg = []

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.host, self.port))
            threading.Thread(target=self.listen).start()
        except Exception as e:
            print(e)

    def send_msg(self, msg):
        try:
            self.sock.send(msg.encode())
        except:
            pass

    def listen(self):
        while True:
            r_ready_sockets, _, _ = select.select([self.sock], [], [])
            try:
                recv_msg = self.sock.recv(4096).decode()
            except:
                break
            self.stock_msg(recv_msg)

    def stock_msg(self, msg):
        self.stocked_msg.append(msg)


class GUI:
    def __init__(self, client):
        self.client = client

        self.root = tk.Tk(None)
        self.root.title("サンプルチャット")

        self.frame = tk.Frame(master=self.root, width=480, height=320)

        self.label1 = tk.Label(master=self.frame, text="サンプルチャット", font=('メイリオ', '12'), bg="#cccccc")
        self.label1.place(relx=0, rely=0, relwidth=1.0, relheight=0.1)

        self.text_w = tk.Text(master=self.frame, state=tk.DISABLED, font=('メイリオ', '10'), bg="white")
        self.text_w.place(relx=0.05, rely=0.1, relwidth=0.85, relheight=0.7)

        self.sb_y = tk.Scrollbar(master=self.frame, orient=tk.VERTICAL, command=self.text_w.yview)
        self.sb_y.place(relx=0.90, rely=0.1, relwidth=0.05, relheight=0.7)
        self.text_w.config(yscrollcommand=self.sb_y.set)

        self.entered_txt = tk.StringVar()
        self.etr = tk.Entry(master=self.frame, width=30, textvariable=self.entered_txt)
        self.etr.bind('<Return>', self.send_msg)
        self.etr.place(relx=0.05, rely=0.85, relwidth=0.65, relheight=0.1)

        self.bt = tk.Button(master=self.frame, text="発言", bg="skyblue", command=self.send_msg)
        self.bt.place(relx=0.75, rely=0.85, relwidth=0.20, relheight=0.1)

        self.bt2 = tk.Button(master=self.frame, text="削除", bg="skyblue", command=self.all_delete)
        self.bt2.place(relx=0.75, rely=0.0, relwidth=0.20, relheight=0.1)

        self.frame.pack()

    def send_msg(self, _=None):
        msg = self.entered_txt.get()
        if len(msg) > 0:
            self.client.send_msg(msg)
            self.entered_txt.set('')

    def receive_msg(self, msg):
        if self.text_w is None:
            return
        self.text_w.config(state=tk.NORMAL)
        self.text_w.insert(tk.END, msg + "\n")
        self.text_w.config(state=tk.DISABLED)
        self.text_w.see(tk.END)

    def stock_msg(self):
        while len(self.client.stocked_msg) > 0:
            self.receive_msg(self.client.stocked_msg.pop(0))
        self.text_w.after(200, self.stock_msg)

    def all_delete(self):
        self.text_w.config(state=tk.NORMAL)
        self.text_w.delete(1.0, tk.END)
        self.text_w.config(state=tk.DISABLED)


class ChatApp:
    def __init__(self, host, port):
        self.client = Client(host, port)
        self.gui = GUI(self.client)

    def start(self):
        self.client.connect()
        self.gui.stock_msg()
        self.gui.root.mainloop()


if __name__ == "__main__":
    host = '127.0.0.1'
    port = 50000
    backlog = 10
    bufsize = 4096
    server = SocketServer(host, port, backlog, bufsize)
    server.start()
    app = ChatApp(host, port)
    app.start()
   
