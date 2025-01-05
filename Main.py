import socket
import threading

SERVER = '192.168.0.45'  # 替换为服务器IP地址
PORT = 12345  # 替换为服务器端口

# 初始化客户端
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((SERVER, PORT))
    print("Connected to the server successfully.")
except ConnectionRefusedError:
    print(f"Unable to connect to server at {SERVER}:{PORT}. Check if the server is running.")
    exit()


def receive_messages():
    """ 用于实时接收服务器消息 """
    while True:
        try:
            message = client_socket.recv(1024).decode()  # 接收服务器消息
            if message:
                print(f"[New Message]: {message}")
        except Exception as e:
            print(f"Error receiving message: {e}")
            break


# 创建一个线程来接收消息
receive_thread = threading.Thread(target=receive_messages, daemon=True)
receive_thread.start()

print("Welcome to the Chat Program!")
print("====================================")
print("|           Chat Box              |")
print("====================================")
print("Type your message below. Enter '/help' for help. Enter '/exit' to exit the chat.")

# 主线程处理用户输入
while True:
    try:
        user_input = input(">>> ")
        if user_input.lower() == "/help":
            print("Available commands:")
            print("==============================================================")
            print("|Command       |Description                                  |")
            print("|--------------|---------------------------------------------|")
            print("|/help         |Display this help page.                      |")
            print("|/exit         |Exit the chat program.                       |")
            print("|/register     |register a new account for you (JUST YOU!)   |")
            print("|/adduser      |add a new user (only admin).                 |")
            print("==============================================================")
        elif user_input.lower() == "/exit":
            print("Leaving the chat. Goodbye!")
            client_socket.send(user_input.encode())  # 通知服务器退出
            break
        else:
            client_socket.send(user_input.encode())  # 发送用户输入到服务器
    except Exception as e:
        print(f"Connection error: {e}")
        break

client_socket.close()
print("Disconnected from the server.")
