import socket
import threading
import time

SERVER = '192.168.0.45'  # 替换为主机的局域网IP地址
PORT = 12345  # 替换为主机监听的端口号

# 初始化客户端
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((SERVER, PORT))
    print("Connected to the server successfully.")
except ConnectionRefusedError:
    print(f"Unable to connect to server at {SERVER}:{PORT}. Check if the server is running.")
    exit()


def receive_messages():
    """
    用于实时接收服务器消息
    """
    while True:
        try:
            message = client_socket.recv(1024).decode()  # 接收服务器消息
            if message.strip():  # 如果消息非空
                print(f"\r{message}\n>>> ", end="")  # 消息换行并补回输入提示符
        except Exception as e:
            print(f"Error receiving message: {e}")
            break


def print_chat_box():
    """
    打印聊天界面布局
    """
    print(f"\r\n####################################")
    print("#             Chat Box             #")
    print("####################################")
    print("Welcome! You can now chat with others.")
    print("Type your message below. Enter '/help' for help. Enter '/exit' to exit the chat.")


def login_process():
    """
    用户登录流程
    """
    print("====================================")
    print("|           Login Screen           |")
    print("====================================")

    while True:
        try:
            server_signal = client_socket.recv(1024).decode().strip()
            if server_signal == "USERNAME":
                username = input("Enter your username: ")
                client_socket.send(username.encode())  # 将用户名发送给服务器
            elif server_signal == "PASSWORD":
                password = input("Enter your password: ")
                client_socket.send(password.encode())  # 将密码发送给服务器
            elif server_signal == "SUCCESS":
                print("Login successful!")
                print(f"Welcome to the chat, {username}!")
                return username  # 返回用户名
            elif server_signal == "FAIL":
                print("Invalid username or password. Please try again.")
                client_socket.close()
                exit()
        except Exception as e:
            print(f"Error during login: {e}")
            client_socket.close()
            exit()


# 执行登录流程
current_user = login_process()

# 欢迎和聊天框生成
print_chat_box()

# 创建线程进行消息接收
receive_thread = threading.Thread(target=receive_messages, daemon=True)
receive_thread.start()

# 主线程处理用户输入
while True:
    try:
        user_input = input(">>> ")  # 恢复提示符 `>>>`
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
            client_socket.send(user_input.encode())  # 发送用户消息
    except Exception as e:
        print(f"Connection error: {e}")
        break

client_socket.close()
print("Disconnected from the server.")
