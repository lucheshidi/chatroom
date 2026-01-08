import socket
import threading

# 配置服务器
SERVER = '127.0.0.1'
PORT = 90552

# 初始化登录凭证（内存管理）
LOGIN_CREDENTIALS = {
    "admin": "admin123",
    "jyx": "mercedes",
    "dachong": "ekmanska",
    "queen": "meimei"
}  # 默认管理员账号

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER, PORT))
server_socket.listen()

print(f"Server is running on {SERVER}:{PORT}")
print("Server started and waiting for connections...")

clients = []  # 在线客户端
usernames = []  # 在线用户名


# 广播消息给所有客户端
def broadcast(message):
    for client in clients:
        try:
            client.send((message + '\n').encode())
        except Exception as e:
            print(f"Failed to broadcast message: {e}")


# 动态添加用户
def add_user(username, password):
    if username in LOGIN_CREDENTIALS:
        return False  # 用户已存在无法重复添加
    LOGIN_CREDENTIALS[username] = password
    return True


# 处理客户端消息和指令
def handle_client(client, username):
    while True:
        try:
            # 接收消息
            message = client.recv(1024).decode().strip()

            if message.startswith("/adduser"):  # 管理员添加用户
                if username == "admin":  # 仅管理员可添加用户
                    try:
                        _, new_user, new_pass = message.split()
                        success = add_user(new_user, new_pass)
                        if success:
                            client.send(f"User {new_user} added successfully.\n".encode())
                        else:
                            client.send("Error: User already exists.\n".encode())
                    except ValueError:
                        client.send("Usage: /adduser <username> <password>\n".encode())
                else:
                    client.send("Permission denied: Only admin can add users.\n".encode())

            elif message.startswith("/register"):  # 普通用户注册功能
                try:
                    _, new_user, new_pass = message.split()
                    success = add_user(new_user, new_pass)
                    if success:
                        client.send(f"User {new_user} registered successfully.\n".encode())
                    else:
                        client.send("Error: User already exists.\n".encode())
                except ValueError:
                    client.send("Usage: /register <username> <password>\n".encode())

            else:  # 普通消息广播
                broadcast(f"{username}: {message}")

        # 处理连接中断的情况
        except (ConnectionResetError, BrokenPipeError):
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                usernames.pop(index)
                broadcast(f"{username} has left the chat.")
                print(f"Connection with {username} closed.")
                break
        except Exception as e:
            print(f"Unexpected error with user {username}: {e}")
            break

    client.close()


# 接收新的连接并处理登录
def receive_connections():
    while True:
        try:
            client, _ = server_socket.accept()
            print("New connection established.")

            # 登录流程
            client.send("USERNAME".encode())
            username = client.recv(1024).decode().strip()

            client.send("PASSWORD".encode())
            password = client.recv(1024).decode().strip()

            # 登录验证
            if username in LOGIN_CREDENTIALS and LOGIN_CREDENTIALS[username] == password:
                client.send("SUCCESS".encode())
                usernames.append(username)
                clients.append(client)
                broadcast(f"{username} has joined the chat!")
                print(f"{username} logged in.")

                thread = threading.Thread(target=handle_client, args=(client, username))
                thread.start()
            else:
                client.send("FAIL".encode())
                client.close()
        except ConnectionResetError:
            print("A client disconnected unexpectedly during login.")
        except Exception as e:
            print(f"Error during connection acceptance or login: {e}")


# 运行服务器
try:
    receive_connections()
except KeyboardInterrupt:
    print("Server shutting down...")
    server_socket.close()
