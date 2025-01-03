import socket

SERVER = '127.0.0.1'
PORT = 12345

# 初始化客户端
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER, PORT))

# 打印欢迎消息和登录界面
print("Welcome to the Chat Program!")
print("====================================")
print("|           Login Screen           |")
print("====================================")

# 登录流程
while True:
    try:
        # 等待服务器发起登录请求
        server_signal = client_socket.recv(1024).decode().strip()
        if server_signal == "USERNAME":
            username = input("Enter your username: ")
            client_socket.send(username.encode())
        elif server_signal == "PASSWORD":
            password = input("Enter your password: ")
            client_socket.send(password.encode())
        elif server_signal == "SUCCESS":
            print("Login successful!")
            break  # 登录成功，进入聊天部分
        elif server_signal == "FAIL":
            print("Invalid username or password. Please try again.")
            client_socket.close()
            exit()  # 登录失败，关闭客户端
    except Exception as e:
        print(f"Error during login: {e}")
        client_socket.close()
        exit()

# 聊天界面
print(f"\r\n####################################")
print(f"#             Chat Box             #")
print(f"####################################")
print("Type your message below. Enter '/help' for help. Enter '/exit' to exit the chat.")

while True:
    try:
        # 非阻塞接收消息
        client_socket.settimeout(0.2)  # 设置超时时间，避免无限阻塞
        try:
            message = client_socket.recv(1024).decode().strip()
            if message:
                print(message)
        except socket.timeout:
            pass  # 超时后不再接收，继续消息输入

        # 处理用户输入
        user_input = input(">>> ")
        if user_input.lower() == "/help":
            print("Available commands:")
            print("==============================================================")
            print("|Command       |Description                                  |")
            print("|--------------|---------------------------------------------|")
            print("|/help         |Display this help page.                      |")
            print("|/exit         |Exit the chat program.                       |")
            print("|/register     |register a new account for you(JUST YOU!)    |")
            print("|/adduser      |add a new user.(only admin)                  |")

            print("|              |                                             |")
            print("==============================================================")
        elif user_input.lower() == "/exit":
            print("Leaving the chat. Goodbye!")
            break
        client_socket.send(user_input.encode())
    except Exception as e:
        print(f"Connection error: {e}")
        break

client_socket.close()
print("Disconnected from the server.")
