import socket
import threading
import json
import pyperclip
import time
import os
from tabulate import tabulate
import constants




class ClipboardSyncServer:
    def __init__(self, host='0.0.0.0', port=constants.DEFAULT_PORT):
        self.host = host
        self.port = port
        self.ip_list = set()
        self.last_clipboard = pyperclip.paste()
        self.last_update_ip = None
        self.lock = threading.Lock()

        threading.Thread(target=self.start_server, daemon=True).start()
        threading.Thread(target=self.monitor_clipboard, daemon=True).start()

    def receive_all(self, conn):
        data = b''
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
        return data

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            print(f"📡 Server listening on {self.host}:{self.port}")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn, addr):
        with conn:
            peer_ip = addr[0]
            data = self.receive_all(conn)
            if not data:
                return
            try:
                message = json.loads(data.decode('utf-8'))
                event = message.get("event", "")
                if event == "hello":
                    # Register client without clipboard action
                    with self.lock:
                        if peer_ip not in self.ip_list:
                            self.ip_list.add(peer_ip)
                            print(f"🔗 Registered client IP: {peer_ip}")
                elif event == "update":
                    # Handle clipboard update (existing code)
                    clipboard = message.get("clipboard", "")
                    if clipboard != self.last_clipboard:
                        self.last_clipboard = clipboard
                        pyperclip.copy(clipboard)
                        self.last_update_ip = peer_ip
                        print(f"📋 Clipboard updated by {peer_ip}")
                        self.broadcast_clipboard(clipboard, exclude_device_ip=peer_ip)
            except json.JSONDecodeError:
                print("⚠️ Received invalid JSON.")

    def monitor_clipboard(self):
        while True:
            current = pyperclip.paste()
            if current != self.last_clipboard:
                self.last_clipboard = current
                self.last_update_ip = None
                self.broadcast_clipboard(current, exclude_device_ip=self.last_update_ip)
            time.sleep(0.2)

    def broadcast_clipboard(self, text, exclude_device_ip=None):
        payload = json.dumps({
            "clipboard": text
        }).encode('utf-8')

        broadcast_ips = [ip for ip in self.ip_list if ip != exclude_device_ip]

        with self.lock:
            for ip in broadcast_ips:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        s.connect((ip, self.port))
                        s.sendall(payload)
                except Exception as e:
                    print(f"❌ Could not send to {ip}: {e}")

    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_ip_table(self):
        self.clear_console()
        rows = [[ip] for ip in self.ip_list]
        print(tabulate(rows, headers=["Connected Clients"], tablefmt="github"))
        print("\n(Updates every 5 seconds)")

    def start(self):
        print("🟢 Clipboard Sync Server is running.")
        try:
            while True:
                self.print_ip_table()
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n🛑 Server shutting down.")
