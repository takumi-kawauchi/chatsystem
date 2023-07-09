import tkinter as tk
import socket
import threading
from tkinter import messagebox


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
        except Exception as e:
            print("Exception:", e)

    def listen(self):
        while True:
            try:
                recv_msg = self.sock.recv(4096).decode()
                if recv_msg == "未登録":
                    if gui.ask_for_registration():
                        self.send_msg("yes")
                    else:
                        self.send_msg("no")
                if recv_msg == "パスワード":
                    psw = gui.ask_for_pass()
                    self.send_msg(psw)
            except:
                break
            self.stock_msg(recv_msg)
            if "未登録" in self.stocked_msg:
                self.stocked_msg.remove("未登録")
            if "パスワード" in self.stocked_msg:
                self.stocked_msg.remove("パスワード")
            
    def stock_msg(self, msg):
        self.stocked_msg.append(msg)


class GUI:
    def __init__(self, client):
        self.client = client

        self.root = tk.Tk(None)
        self.root.title("掲示板")

        self.frame = tk.Frame(master=self.root, width=480, height=320)

        self.label1 = tk.Label(master=self.frame, text="システムの利用には登録,認証が必要です", font=('メイリオ', '12'), bg="#cccccc")
        self.label1.place(relx=0, rely=0, relwidth=1.0, relheight=0.1)

        self.label2 = tk.Label(master=self.frame, text="下部に文字列を入力して開始してください", font=('メイリオ', '12'), bg="#cccccc")
        self.label2.place(relx=0, rely=0.1, relwidth=1.0, relheight=0.1)

        self.text_w = tk.Text(master=self.frame, state=tk.DISABLED, font=('メイリオ', '10'), bg="white")
        self.text_w.place(relx=0.05, rely=0.2, relwidth=0.75, relheight=0.6)

        self.sb_y = tk.Scrollbar(master=self.frame, orient=tk.VERTICAL, command=self.text_w.yview)
        self.sb_y.place(relx=0.90, rely=0.2, relwidth=0.05, relheight=0.6)
        self.text_w.config(yscrollcommand=self.sb_y.set)

        self.entered_txt = tk.StringVar()
        self.etr = tk.Entry(master=self.frame, width=30, textvariable=self.entered_txt)
        self.etr.bind('<Return>', self.send_msg)
        self.etr.place(relx=0.05, rely=0.85, relwidth=0.75, relheight=0.1)

        self.bt = tk.Button(master=self.frame, text="投稿", bg="skyblue", command=self.send_msg)
        self.bt.place(relx=0.85, rely=0.85, relwidth=0.10, relheight=0.1)

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
    
    def start(self, gui):
        gui.stock_msg()
        gui.root.mainloop()
    
    def ask_for_registration(self):
        result = messagebox.askyesno("仮登録", "登録しますか？")
        return result
    
    def ask_for_pass(self):
        self.dialog = tk.Toplevel(self.root) 
        self.dialog.title("パスワード入力")
        self.dialog.geometry("500x90")
        def close_dialog():
            self.dialog.destroy()

        password = tk.StringVar()
        entry = tk.Entry(self.dialog, textvariable=password)
        entry.pack()

        button = tk.Button(self.dialog, text="OK", command=close_dialog)
        button.pack()

        self.dialog.wait_window(self.dialog)

        return password.get()


if __name__ == "__main__":
    host = '127.0.0.1'
    port = 50000
    client = Client(host, port)
    client.connect()
    gui = GUI(client)
    gui.start(gui)
   
