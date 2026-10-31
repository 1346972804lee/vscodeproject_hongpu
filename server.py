import socket
import struct
import threading

#此版本相较于chatdemo 2.0，新增1项功能：
#1. 服务端和客户端都可以随意发消息随意收消息了，不需要你一句我才能一句了
#此版本缺陷：服务端无法终止对话

HOST = "0.0.0.0"
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
        print(f"\n客户端说:{text}")
    


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 端口复用，防止 TIME_WAIT 报错
    server.bind((HOST, PORT))
    server.listen()
    print("服务端开始监听")
    conn, addr = server.accept()

    #获得了信道，接下来：
    # 1. 创建一个子线程，子线程专门用来接收消息
    # 1.1 要为子线程创建一个收消息的函数，子线程执行这个函数，我们将这个函数命名为recv_loop
    # 1.2 要不停的收消息，直到客户端发送"bbb"为止，所以在recv_loop函数里面也要while TRUE，然后加判断条件退出
    # 3. 给客户端发消息，同样的，也要while TRUE

    server_sub = threading.Thread(target=recv_loop, args=(conn, ), daemon=True)
    server_sub.start()

    while True:
        # 3. 发送消息给客户端
        if not switch:
            print("客户端已离线")
            break
        text = input("请输入你要回复给客户端的消息:")

        #服务端主动退出
        if text == "bbb":
            break

        try:
            send_message(conn, text)
        except (BrokenPipeError, ConnectionResetError):
            print("客户端已断开！")
            break

    conn.close()
    server.close()
    print("服务端关闭")


if __name__ == "__main__":
    main()
    



