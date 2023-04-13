from customtkinter import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64decode, b64encode
from os import urandom
import socket
from threading import Thread
from textwrap import indent

set_appearance_mode("dark")
set_default_color_theme("blue")

root = CTk()
root.geometry("1066x600")

server = "YOUR SERVER'S IP ADDRESS"
port = 38923
name_list = []
buffer = 4096
borders = "#303030"
borders_width = 5
message_color = "#202020"
message_height = 30
better_font = ("Consolas", 24)
wraplength=80
padx=2
pady=2

secret_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
s = socket.socket()

def encrypt(message):
    nonce = urandom(12)
    cipher = AES.new(secret_key.encode('utf-8'), AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(pad(message.encode('utf-8'), AES.block_size))
    ciphertext_b64 = b64encode(ciphertext).decode('utf-8')
    nonce_b64 = b64encode(nonce).decode('utf-8')
    tag_b64 = b64encode(tag).decode('utf-8')

    return '~'.join([ciphertext_b64, nonce_b64, tag_b64])

def decrypt(encrypted_message):
    deconstructed_encrypted_message = encrypted_message.split("~")
    ciphertext = b64decode(deconstructed_encrypted_message[0])
    nonce = b64decode(deconstructed_encrypted_message[1])
    tag = b64decode(deconstructed_encrypted_message[2])
    cipher = AES.new(secret_key.encode(), AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    plaintext = unpad(plaintext, AES.block_size).decode()

    return plaintext

def receive_messages(message_panel, slider_panel):
    while True:
        data = s.recv(buffer).decode()
        if data != "":
            if data.startswith("[NAME_LIST]"):
                children = slider_panel.winfo_children()
                for child in children:
                    if isinstance(child, CTkButton):
                        child.destroy()

                name_list = data.removeprefix("[NAME_LIST]").split("ㅤ")
                
                for member in name_list:
                    name = decrypt(member)
                    display_name = CTkButton(master=slider_panel, text=name, font=better_font, fg_color=message_color, height=32)
                    display_name.pack(side=TOP, fill='x', padx=padx, pady=pady)
            
            elif data.startswith("[CHAT_LOG]"):
                chat_log_length = int(data.removeprefix("[CHAT_LOG]"))
                s.send(str.encode("received"))
                if chat_log_length > 0:
                    for i in range(int(chat_log_length)):
                        message = decrypt(s.recv(1024).decode()).split(" : ")
                        message_header = message[0].lstrip()
                        lines = [message[1].lstrip()[i:i+wraplength] for i in range(0, len(message[1].lstrip()), wraplength)]
                        display_messages = CTkButton(master=message_panel, text=message_header + " : {}\n{}".format(lines[0], indent('\n'.join(lines[1:]), ' ' * (len(message_header) + 2))), font=better_font, anchor="w", fg_color=message_color, height=message_height, text_color="silver")
                        display_messages.pack(side=TOP, fill='x', padx=padx, pady=pady)
                        s.send(str.encode("received"))
            else:
                message = decrypt(data).split(" : ")
                message_header = message[0].lstrip()
                lines = [message[1].lstrip()[i:i+wraplength] for i in range(0, len(message[1].lstrip()), wraplength)]
                display_messages = CTkButton(master=message_panel, text=message_header + " : {}\n{}".format(lines[0], indent('\n'.join(lines[1:]), ' ' * (len(message_header) + 2))), font=better_font, anchor="nw", fg_color=message_color, height=message_height, text_color="silver")
                display_messages.pack(side=TOP, fill='x', padx=padx, pady=pady)
                
            
def send(message, message_panel, username, entry):
    entry.delete(0, END)
    if message != "":
        s.send(str.encode(encrypt(f"{username} : {message}")))
        lines = [message[i:i+wraplength] for i in range(0, len(message), wraplength)]
        display_message = CTkButton(master=message_panel, text="You : {}\n{}".format(lines[0], indent('\n'.join(lines[1:]), ' ' * 6)), font=better_font, anchor="nw", fg_color=message_color, height=message_height)
        display_message.pack(side=TOP, fill='x', padx=padx, pady=pady)
    
def send_messages(send_message_panel, message_panel, username):
    entry = CTkEntry(master=send_message_panel, height=50, width=1500, placeholder_text="Send", corner_radius=20, font=better_font)
    entry.place(relx=0.5, rely=0.5, anchor=CENTER)
    entry.bind('<Return>', lambda event: send(entry.get(), message_panel, username, entry))

def main_gui(username):
    root = CTk()
    root.geometry("1600x900")
    root.columnconfigure(index=0, weight=1)
    root.columnconfigure(index=1, weight=10)
    root.rowconfigure(index=0, weight=5)
    root.rowconfigure(index=1, weight=1)

    message_panel = CTkScrollableFrame(master=root, border_color=borders, border_width=borders_width)
    message_panel.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    slider_panel = CTkScrollableFrame(master=root, border_color=borders, border_width=borders_width, label_text="Online Users : ", label_font=('Consolas', 26), label_anchor="nw", label_fg_color="#2B2B2B")
    slider_panel.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    send_message_panel = CTkFrame(master=root, height=10, border_color=borders, border_width=borders_width)
    send_message_panel.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=20, pady=20)
    
    s.connect((server, port))
    s.send(str.encode(encrypt(username)))

    Thread(target=receive_messages, args=(message_panel, slider_panel)).start()
    Thread(target=send_messages, args=(send_message_panel, message_panel, username)).start()

    root.mainloop()

def initiate_main_gui(username):
    if username != "":
        root.destroy()
        main_gui(username)    

def startup():
    frame = CTkFrame(master=root, border_color=borders, border_width=borders_width)
    frame.pack(padx=100, pady=100, fill=BOTH, expand=True)
    
    entry = CTkEntry(master=frame, height=50, width=300, placeholder_text="Name", corner_radius=20, font=better_font)
    entry.place(relx=0.5, rely=0.5, anchor=CENTER)
    entry.bind('<Return>', lambda event: initiate_main_gui(entry.get()))
    
    button = CTkButton(master=frame, text="Enter :)", height=50, width=300, corner_radius=20, font=better_font, command = lambda : initiate_main_gui(entry.get()))
    button.place(relx=0.5, rely=0.65, anchor=CENTER)

startup()
root.mainloop()
