import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
import os
from datetime import datetime

# Configuración del servidor
HOST = '0.0.0.0'
PORT = 12345
clients = []  # Lista de clientes conectados
SAVE_DIR = "base64_logs"

# Crear la carpeta de logs si no existe
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def broadcast(sender_socket, data):
    """ Envía el mensaje a todos los clientes excepto el que lo envió """
    for client in clients:
        if client != sender_socket:
            try:
                client.sendall(data)
            except:
                clients.remove(client)  # Remover clientes desconectados

def handle_client(conn, addr):
    """ Maneja la comunicación con un cliente """
    clients.append(conn)
    chat_display.insert(tk.END, f"Cliente {addr} conectado\n")

    while True:
        try:
            data = conn.recv(1024 * 128)  # Un buffer más grande (recv(1024 * 128)) permite recibir imágenes completas de hasta 128 KB en un solo mensaje, reduciendo el riesgo de fragmentación.
            if not data:
                break

            try:
                message = data.decode('utf-8')

                if message.startswith("IMG::"):
                    base64_data = message[5:]

                    # Guardar la cadena Base64 en un archivo
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{SAVE_DIR}/image_{addr[1]}_{timestamp}.txt"

                    with open(filename, "w") as file:
                        file.write(base64_data)

                    chat_display.insert(tk.END, f"Cliente {addr}: [Imagen recibida]\n")
                    chat_display.insert(tk.END, f"[Base64 guardado]: {filename}\n")

                else:
                    chat_display.insert(tk.END, f"Cliente {addr}: {message}\n")

            except UnicodeDecodeError:
                chat_display.insert(tk.END, f"Cliente {addr}: [Imagen recibida]\n")

            # Enviar el mensaje a los demás clientes
            broadcast(conn, data)

        except:
            break

    chat_display.insert(tk.END, f"Cliente {addr} desconectado\n")
    clients.remove(conn)
    conn.close()

def start_server():
    """ Inicia el servidor """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    chat_display.insert(tk.END, "Servidor esperando conexiones...\n")

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

# Crear ventana del servidor
root = tk.Tk()
root.title("Servidor - Chat Base64")

chat_display = scrolledtext.ScrolledText(root, width=50, height=20)
chat_display.pack(pady=10)

start_button = tk.Button(root, text="Iniciar Servidor", command=lambda: threading.Thread(target=start_server, daemon=True).start())
start_button.pack()

root.mainloop()
