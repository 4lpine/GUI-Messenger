import socket
import threading

host = "YOUR SERVER'S IP ADDRESS"
port = 38923

s = socket.socket()
s.bind((host, port))
s.listen(5)
buffer=1024

connections = []
names = []
chat_log = []


def accept_connections():
    while True:
        conn, address = s.accept()
        connections.append(conn)
        name = conn.recv(buffer).decode()
        names.append(name)

        print(f"{name} has joined the server!")

        for connection in connections:
            connection.send(str.encode("[NAME_LIST]" + "ㅤ".join(names)))

        conn.send(str.encode(f"[CHAT_LOG]{len(chat_log)}"))

        if conn.recv(1024).decode() == "received":
            for message in chat_log:
                conn.sendall(str.encode(message))
                conn.recv(1024)

        thread = threading.Thread(target=relay, args=(conn, connections.index(conn)))
        thread.start()


def relay(conn, index):
    num = 0
    while True:
        try:data = conn.recv(buffer)
        except ConnectionResetError:
            
            connections.remove(conn)
            print(names[index - num] + " has left the server!")
            names.remove(names[index - num])
            num += 1

            for connection in connections:
                connection.send(str.encode("[NAME_LIST]" + "ㅤ".join(names)))
                
            break

        for connection in connections:
            if connection != conn:
                connection.send(data)

        chat_log.append(data.decode())

accept_connections()
