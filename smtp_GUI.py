import tkinter as tk
from tkinter import simpledialog,filedialog,ttk

import base64
import os
import random
import string

import socket

def sendList_emails(client, list):
    if list:
        for item in list:
            client.sendall(f'RCPT TO:<{item}>\r\n'.encode("utf8"))
            client.recv(1024)


def email_list(str_info):
    mails = str_info.split(',')

    mails = [email.strip() for email in mails]

    mails = [email for email in mails if email]

    valid = []
    invalid = []

    for email in mails:
        if "@" in email and "." in email:
            valid.append(email)
        else:
            invalid.append(email)

    if invalid:
        print("Invalid email address: ")
        for email in invalid:
            print(email)

    return valid


def check_list_file_size(list_file_path, size):
    max_size_in_bytes = size * 1024 * 1024
    list_file_size = 0
    for file_path in list_file_path:
        list_file_size += os.path.getsize(file_path)
    if list_file_size > max_size_in_bytes:
        return False
    return True


def get_type_content_file(path):
    name, extension = os.path.splitext(os.path.basename(path))

    if extension == ".pdf":
        return "application/pdf"
    elif extension == ".txt":
        return "text/plain"
    elif extension == ".docx":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif extension == ".jpg":
        return "image/jpeg"
    elif extension == ".zip":
        return "application/zip"
    else:
        return "application/octet-stream"


def send_file(client, path, boundary):
    attachment_filename = os.path.basename(path)

    client.send(f'--{boundary}\r\n'.encode())
    client.send(
        f'Content-Type:{get_type_content_file(path)}; charset={"UTF-8"};name ="{attachment_filename}"\r\n'.encode())
    client.send(
        f'Content-Disposition: attachment; filename="{attachment_filename}"\r\n'.encode())

    # Attach the file
    with open(path, 'rb') as file:
        attachment_data = base64.b64encode(file.read()).decode()
        client.send(f'Content-Transfer-Encoding: base64\r\n\r\n'.encode())
        for data in range(0, len(attachment_data), 72):
            line = attachment_data[data:data+72]
            client.send(f'{line}\r\n'.encode())


def generate_boundary():              # Generate a random boundary value
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))


class EmailClient:
    def __init__(self, master):
        self.master = master
        self.c = None  
        self.boundary = None
        self.master.title("Email Client")
        for i in range(6):
            self.master.columnconfigure(i, weight=1, minsize=50)
            self.master.rowconfigure(i, weight=1)

        self.create_tool()

    def create_tool(self):
        self.master.geometry("300x150")
        self.master.resizable(True, True)
        
        toolbar = ttk.Frame(self.master, padding=(5, 5, 5, 5), relief="ridge")
        toolbar.pack(side="top", anchor="center")

        new_email_button = ttk.Button(toolbar, text="New Email", command=self.create_send)
        new_email_button.grid(row=0, column=0, padx=5, pady=5)

        inbox_button = ttk.Button(toolbar, text="Inbox", command=self.master.destroy)     #Waiting.....
        inbox_button.grid(row=1, column=0, padx=5, pady=5)

        exit_button = ttk.Button(toolbar, text="Exit", command=self.master.destroy)
        exit_button.grid(row=2, column=0, padx=5, pady=5)
        
    def create_menu(self):
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Menu", menu=file_menu)
        file_menu.add_command(label="New Email", command=self.create_send)
        file_menu.add_separator()
        file_menu.add_command(label="Inbox", command=self.master.destroy)   #Waiting.....
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.destroy)
        
    def update_attachFile_button(self,*args):
        if self.attach_var.get() == 1:
            if not hasattr(self, 'attach_button'):
                # Create the Attach File button if it doesn't exist
                self.attach_button = tk.Button(self.master, text="Attach File", command=self.attach_file)
                self.attach_button.grid(row=7, column=1, sticky="W")
        else:
            # Remove the Attach File button if it exists
            if hasattr(self, 'attach_button'):
                self.attach_button.destroy()
                del self.attach_button

    def clear_widgets(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    def attach_file(self):
        file_amount = simpledialog.askinteger("File Attachment", "Số lượng file muốn gửi:", initialvalue=1)
        self.path_list = []
        for i in range(1, file_amount + 1):
            #path = input(f"Nhập đường dẫn file thứ {i}: ")
            path = filedialog.askopenfilename(title=f"Chọn đường dẫn file thứ {i}:")
            if path:
                self.path_list.append(path)
                
        return self.path_list
    
    def get_path_list(self):
        return self.path_list

    def send_email(self):
        to_email = self.to_entry.get()
        cc_email = self.cc_entry.get()
        bcc_email = self.bcc_entry.get()
        subject = self.subject_entry.get()
        content = self.content_entry.get("1.0", tk.END)
        
        to_receivers = email_list(to_email)
        cc_receivers = email_list(cc_email)
        bcc_receivers = email_list(bcc_email)

        mail_server = "127.0.0.1"
        mail_port = 2225

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.c:
            try:
                self.c.connect((mail_server, mail_port))
                self.c.sendall(b'EHLO \r\n')
                self.c.recv(1024)

                # Send MAIL FROM
                mail_from = "MAIL FROM: <tin75vn@gmail.com>\r\n"
                self.c.send(mail_from.encode())
                self.c.recv(1024)

                # Send MAIL TO
                if  to_receivers:
                    sendList_emails(self.c, to_receivers)
                if  cc_receivers:
                    sendList_emails(self.c, cc_receivers)
                if  bcc_receivers:
                    sendList_emails(self.c, bcc_receivers)

                # Begin sending data
                self.c.send(b'DATA\r\n')
                self.c.recv(1024)

                # Generate a random boundary
                self.boundary = generate_boundary()

                # Send email structure

                self.c.send(f'Subject: {subject}\r\n'.encode())
                self.c.send(f'From: {"tin75vn@gmail.com"}\r\n'.encode())
                self.c.send(f'To: {", ".join( to_receivers)}\r\n'.encode())
                if  cc_receivers:
                    self.c.send(f'Cc: {", ".join( cc_receivers)}\r\n'.encode())
                self.c.send(
                    f'Content-Type: multipart/mixed; charset={"UTF-8"}; boundary={self.boundary}\r\n'.encode())
                self.c.send('\r\n'.encode())  # End header

                # Send body email
                self.c.send(f'--{self.boundary}\r\n'.encode())
                self.c.send(f'Content-Type: text/plain\r\n\r\n{content}\r\n'.encode())

                # Send file attachments
                if self.attach_var.get() == 1:
                    path_list = self.get_path_list()
                    if check_list_file_size(path_list, 3):
                        for path_file in path_list:
                            send_file(self.c, path_file, self.boundary)

                # End mail
                self.c.send(f'\r\n--{self.boundary}--\r\n'.encode())
                end = f'.\r\n'
                self.c.send(end.encode())
                self.c.recv(1024)

                # Close connect
                quit = "QUIT\r\n"
                self.c.send(quit.encode())
                self.c.recv(1024)

                print("\nĐã gửi email thành công\n\n")
                
            except Exception as error:
                print("Error: ", error)
                
            finally:
                self.c.close()
        
    def create_send(self):
        self.clear_widgets()
        self.master.geometry("600x500")
        self.master.resizable(True, True)
        
        self.create_menu()
        
        labels = [
            "To:",
            "CC:",
            "BCC:",
            "Subject:"
        ]
        for idx, text in enumerate(labels):
            self.to_label = tk.Label(self.master, text=text)
            self.to_label.grid(row=idx, column=0, sticky="E")
            self.to_entry = tk.Entry(self.master, width=100)
            self.to_entry.grid(row=idx, column=1, columnspan=2, sticky="W")
        # self.to_label = tk.Label(self.master, text="To:")
        # self.to_label.grid(row=0, column=0, sticky="E")
        # self.to_entry = tk.Entry(self.master, width=100)
        # self.to_entry.grid(row=0, column=1, columnspan=2, sticky="W")

        # self.cc_label = tk.Label(self.master, text="CC:")
        # self.cc_label.grid(row=1, column=0, sticky="E")
        # self.cc_entry = tk.Entry(self.master, width=100)
        # self.cc_entry.grid(row=1, column=1, columnspan=2, sticky="W")

        # self.bcc_label = tk.Label(self.master, text="BCC:")
        # self.bcc_label.grid(row=2, column=0, sticky="E")
        # self.bcc_entry = tk.Entry(self.master, width=100)
        # self.bcc_entry.grid(row=2, column=1, columnspan=2, sticky="W")

        # self.subject_label = tk.Label(self.master, text="Subject:")
        # self.subject_label.grid(row=3, column=0, sticky="E")
        # self.subject_entry = tk.Entry(self.master, width=100)
        # self.subject_entry.grid(row=3, column=1, columnspan=2, sticky="W")

        self.content_label = tk.Label(self.master, text="Content:")
        self.content_label.grid(row=4, column=0, sticky="E")
        self.content_entry = tk.Text(self.master, height=10, width=100)
        self.content_entry.grid(row=4, column=1, columnspan=2, sticky="W")
        
        self.content_label = tk.Label(self.master, text="Có gửi kèm file (1. có, 2. không):")
        self.content_label.grid(row=5, column=1, sticky="W")

        self.attach_var = tk.IntVar()
        self.attach_var.set(2)  # Default choice is "2. không"
        self.attach_button_yes = tk.Radiobutton(self.master, text="1. có", variable=self.attach_var, value=1)
        self.attach_button_yes.grid(row=6, column=1, sticky="W")
        self.attach_button_no = tk.Radiobutton(self.master, text="2. không", variable=self.attach_var, value=2)
        self.attach_button_no.grid(row=6, column=2, sticky="W")
        
        # Using the trace_add method to set up a callback function (self.update_attachFile_button) that will be called when the value of the self.attach_var variable changes
        self.attach_var.trace_add("write", self.update_attachFile_button)
        # Initial creation of the Attach File button if self.attach_var.set(1)
        self.update_attachFile_button()
        
        self.send_button = tk.Button(self.master, text="Send Email", command=self.send_email)
        self.send_button.grid(row=7, column=2, sticky="W")

    


window = tk.Tk()
email_client_gui = EmailClient(window)
window.mainloop()
