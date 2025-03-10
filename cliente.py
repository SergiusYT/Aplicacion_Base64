import socket
import base64
import tkinter as tk
from tkinter import filedialog, scrolledtext
from PIL import Image, ImageTk
import io
import threading

HOST = '127.0.0.1'
PORT = 12345

# Lista global para almacenar imágenes y evitar que se borren de la memoria
images_list = []

def receive_messages():
    """ Hilo que recibe mensajes del servidor """
    while True:
        try:
            data = client_socket.recv(1024 * 128)  # Aumentamos el buffer para imágenes grandes
            if not data:
                break

            try:
                message = data.decode('utf-8')
                if message.startswith("IMG::"):
                    base64_data = message[5:]
                    
                    # Mostrar parte de la cadena Base64 recibida
                    chat_display.insert(tk.END, f"[Base64 recibido]: {base64_data[:100]}...\n")

                    decoded_image = base64.b64decode(base64_data)

                    # Convertir bytes a imagen y mostrar en el chat
                    image = Image.open(io.BytesIO(decoded_image))
                    image.thumbnail((100, 100))
                    img = ImageTk.PhotoImage(image)

                    chat_display.insert(tk.END, "Otro Cliente: [Imagen recibida]\n")
                    chat_display.image_create(tk.END, image=img)
                    chat_display.insert(tk.END, "\n")

                    images_list.append(img)
                else:
                    chat_display.insert(tk.END, f"Otro Cliente: {message}\n")
            except UnicodeDecodeError:
                pass  

        except:
            break

def send_text():
    """ Envía un mensaje de texto """
    message = entry_text.get()
    if message:
        client_socket.sendall(message.encode('utf-8'))
        chat_display.insert(tk.END, f"Tú: {message}\n")
        entry_text.delete(0, tk.END)

def send_image():
    """ Selecciona y envía una imagen codificada en Base64 """
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

        # Mostrar fragmento de Base64 antes de enviarlo
        chat_display.insert(tk.END, f"[Base64 enviado]: {encoded_string[:100]}...\n")

        # Agregar prefijo y enviar
        full_message = f"IMG::{encoded_string}"
        client_socket.sendall(full_message.encode('utf-8'))
        chat_display.insert(tk.END, "Tú: [Imagen enviada]\n")

        # Mostrar la imagen en la interfaz
        image = Image.open(file_path)
        image.thumbnail((100, 100))
        img = ImageTk.PhotoImage(image)
        chat_display.image_create(tk.END, image=img)
        chat_display.insert(tk.END, "\n")

        images_list.append(img)

# Conectar al servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Crear la ventana del cliente
root = tk.Tk()
root.title("Cliente - Chat Base64")

chat_display = scrolledtext.ScrolledText(root, width=50, height=20)
chat_display.pack(pady=10)

entry_text = tk.Entry(root, width=40)
entry_text.pack(side=tk.LEFT, padx=5)

send_button = tk.Button(root, text="Enviar", command=send_text)
send_button.pack(side=tk.LEFT, padx=5)

image_button = tk.Button(root, text="Enviar Imagen", command=send_image)
image_button.pack(side=tk.LEFT, padx=5)

# Iniciar hilo para recibir mensajes
threading.Thread(target=receive_messages, daemon=True).start()

root.mainloop()
client_socket.close()
