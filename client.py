import tkinter as tk
from tkinter import scrolledtext, messagebox
import socket
import threading

HOST = "127.0.0.1"
PORT = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

incoming_messages = []
msg_lock = threading.Lock()
nickname = ""

root = tk.Tk()
font_tuple = ("Helvetica", 12, "bold italic")
root.geometry("650x600")
root.title("Chat App")
root.config(bg="#1E1E1E")

title = tk.Label(root, text="GROUP CHAT",
    font=("sans-serif", 20, "bold"), bg="red", fg="white")
title.pack(fill="x", pady=5)

main = tk.Frame(root)
main.pack(fill="both", expand=True, padx=10, pady=10)

popup = tk.Frame(main, bg="#3A3A3A")
popup.pack(fill="both", expand=True)

note = tk.Label(popup, text="Enter Your Name to Join the Chat", font=("Helvetica", 15, "bold" ), bg="#2D2D2D", fg="white")
note.pack(pady=50)

nameframe = tk.Frame(popup, bg="#2D2D2D", pady=50)
nameframe.pack()

nickname_label = tk.Label(nameframe, text="Your Nickname", font=("Helvetica", 15, "bold" ), bg="#2D2D2D", fg="white")
nickname_label.pack()

entry = tk.Entry(nameframe, font=("Segoe UI", 12, "bold"), bg="#777373", fg="white", justify="center")
entry.pack(pady=10,padx=10)


def join():
    global nickname
    name = entry.get().strip()
    if not name:
        messagebox.showerror("Error", "Enter username")
        return

    nickname = name
    client.send(nickname.encode("utf-8"))

    popup.destroy()
    chat_ui()


tk.Button(nameframe, text="Join", command=join,font=("Helvetica", 15, "bold"), bg="red").pack(pady=20)

def chat_ui():

    chat_layout = tk.Frame(main, bg="#1E1E1E")
    chat_layout.pack(fill="both", expand=True)

    sidebar = tk.Frame(chat_layout, width=180, bg="#181818")
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(sidebar, text="ONLINE",
        bg="#181818", fg="#8AFF6C",
        font=("Segoe UI", 11, "bold")).pack(pady=6)

    users_list = tk.Listbox(
        sidebar, bg="#202020", fg="white",justify="center",
        font=("Segoe UI", 11, "bold"),
        border=0, highlightthickness=0,
        selectbackground="#2B2B2B"
    )
    users_list.pack(fill="both", expand=True, padx=6, pady=6)

    chat_area = tk.Frame(chat_layout, bg="#2A2A2A")
    chat_area.pack(side="right", fill="both", expand=True)

    chat_display = scrolledtext.ScrolledText(
        chat_area, wrap="word",
        state="disabled", font=font_tuple
    )
    chat_display.pack(fill="both", expand=True, padx=5, pady=5)
    
    chat_display.config(bg="#1f1f1f", fg="#e8e8e8")
    chat_display.tag_configure("system",
        background="#444444", foreground="#FF2B05", justify="center")
    
    chat_display.tag_configure("you",
        background="#FFFFFF", foreground="black", justify="right")
    
    chat_display.tag_configure("other",
        background="#6B6B6B", foreground="white", justify="left")


    input_bar = tk.Frame(chat_area)
    input_bar.pack(fill="x")

    text_input = tk.Entry(input_bar, font=("sans-serif", 14),bg="#b6b6b6", fg="black")
    text_input.pack(side="left", fill="x", expand=True, padx=20, pady=5)


    def send_msg(event=None):
        msg = text_input.get().strip()
        if not msg:
            return

        client.send(f"{nickname}: {msg}".encode())

        chat_display.config(state="normal")
        chat_display.insert("end", msg + "\n", "you")
        chat_display.config(state="disabled")
        chat_display.see("end")

        text_input.delete(0, "end")


    send_chat = tk.Button(input_bar, text="Send", command=send_msg, bg="red", fg="white", width=7)
    send_chat.pack(fill="x", side="right", padx=10, pady=5)

    text_input.bind("<Return>", send_msg)

    def receive():
        buffer = ""
        while True:
            try:
                msg = client.recv(1024).decode()
                if not msg:
                    break

                buffer += msg
                
                while "\n" in buffer:
                    msg, buffer = buffer.split("\n", 1)
                    if msg.strip():
                      with msg_lock:
                        incoming_messages.append(msg.strip())
            except:
                break

    def update_user_list(users_str):
        users_list.delete(0, "end")

        usernames = [u.strip() for u in users_str.split(",") if u.strip()]

        for u in usernames:
            if u == nickname:
                users_list.insert("end", f"{u} (you)")
            else:
                users_list.insert("end", u)

    def update_chat():
        with msg_lock:
            while incoming_messages:
                msg = incoming_messages.pop(0)
                print("MSG :",msg)

                if msg.startswith("[USERS]"):
                    users = msg.replace("[USERS]", "").strip()
                    update_user_list(users)
                    continue

                chat_display.config(state="normal")

                if msg.startswith("[SYSTEM]"):
                    alert = msg.replace("[SYSTEM]", "").strip()
                    chat_display.insert("end", alert + "\n", "system")

                elif msg.startswith(f"{nickname}: "):
                    clean = msg.split(": ", 1)[1]
                    chat_display.insert("end", clean + "\n", "you")

                else:
                    chat_display.insert("end", msg + "\n", "other")

                chat_display.config(state="disabled")
                chat_display.see("end")

        root.after(100, update_chat)


    threading.Thread(target=receive, daemon=True).start()
    update_chat()


root.mainloop()
