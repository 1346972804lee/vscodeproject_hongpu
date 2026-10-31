import socket
import struct
import threading


HOST = "192.168.2.7"
PORT = 9999
HEADER_SIZE = 4
switch = True

def recv_exactly(conn ,n):
    #recv_exactly函数目的是精确的取得conn信道上的n个字节
    #因为直接conn.recv(n)可能只能收到0~n个字节
    buf = b""  #用来记录结果
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        # recv函数，如果收到了b""，就会返回None，而发送消息的那边发送b""，代表要中断连接
        # 所以，收到了None代表客户端中断连接
        if not chunk:
            return None
        buf += chunk
    return buf

def send_message(conn, text):
    #send_message函数的目的是在conn信道上发送消息text
    text_b = text.encode("utf-8")
    header = len(text_b)
    header_b = struct.pack("!I", header)
    conn.sendall(header_b)
    conn.sendall(text_b)

def recv_loop(conn):
    global switch
    while True:
        header_b = recv_exactly(conn, HEADER_SIZE)
        if not header_b:
            switch = False
            return
        header = struct.unpack("!I", header_b)[0]
        text_b = recv_exactly(conn, header)
        if not text_b:
            switch = False
            return
        text = text_b.decode("utf-8")
        print(f"\n服务端说:{text}")

def main():
    # 1. 创造一个套接字对象conn，连接服务端(HOST, PORT)
    # 2. 发消息给服务端（服务端先运行，所以此时服务端已经在监听了，我们可以发消息给服务端了）
    # 2.1 服务端推出while循环的判断条件全部在收消息的环节，所以我们要在客户端发消息的时候（对应服务端收消息的时候）创造一个if来终止聊天
    # 3. 开始接收服务端的消息
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((HOST, PORT))  #connect函数只接受元组，应该是(HOST, PORT)
    client_sub = threading.Thread(target=recv_loop, args=(conn,), daemon=True)
    client_sub.start()
    print("已连接到服务端")

    while True:
        if not switch:
            break
        # 2. 发消息给服务端
        text = input("客户端，请输入你要发的消息：")
        
        # 2.1 服务端推出while循环的判断条件全部在收消息的环节，所以我们要在客户端发消息的时候（对应服务端收消息的时候）创造一个if来终止聊天
        if text == "bbb":
            break
        try:
            send_message(conn, text)
        except (BrokenPipeError, ConnectionResetError):
            print("服务端已断开")
            break


    conn.close()  #这个时候会给服务端发 b"" ， 服务端的recv_exactly()函数就会返回None，服务端的while函数就会break掉了
    print("客户端断开连接了")





