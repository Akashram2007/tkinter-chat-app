import socket
import threading

HOST = "127.0.0.1"
PORT = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = {}   

def broadcast(msg, sender=None):
    for client in list(clients.keys()):
        if client != sender:
            try:
                client.send((msg+"\n").encode())
            except:
                client.close()
                clients.pop(client, None)


def broadcast_all(msg):
    for client in list(clients.keys()):
        try:
            client.send((msg+"\n").encode("utf-8"))
        except:
            client.close()
            clients.pop(client, None)


def send_user_list():
    """Send active users to all clients"""
    if not clients:
        return
    users = ", ".join(clients.values())
    broadcast_all(f"[USERS] {users}")


def handle_client(conn):
    try:
        nickname = conn.recv(1024).decode("utf-8")
    except:
        conn.close()
        return

    clients[conn] = nickname

    users = ", ".join(clients.values())
    conn.send(f"[USERS] {users}\n".encode("utf-8"))

    broadcast_all(f"[SYSTEM] {nickname} joined the chat")

    send_user_list()
    print(f"{nickname} joined")

    try:
        while True:
            msg = conn.recv(1024)
            if not msg:
                break
            broadcast(msg.decode("utf-8"), sender=conn)
    except:
        pass

    broadcast_all(f"[SYSTEM] {nickname} left the chat")
    print(f"{nickname} left")

    conn.close()
    clients.pop(conn, None)
    send_user_list()


print("Server started... Waiting for clients...")

while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn,), daemon=True).start()
