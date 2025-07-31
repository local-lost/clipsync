import pyperclip
import socket
import json
import time
import threading
import constants
import os

DEFAULT_PORT = 65432
class ClipSyncClient:
    """Client for clipsync server."""

    def __init__(self, server_ip, port=constants.DEFAULT_PORT):
        self.server_ip = server_ip
        self.port = port
        self.last_clipboard = pyperclip.paste()

    def is_ip_reachable(self, ip, port):
        try:
            print(f"🔍 Checking if Server at {ip}:{port} is reachable.")
            with socket.create_connection((ip, port), timeout=10):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            print(f"❌ Server at {ip}:{port} is not reachable.")
            return False

    def send_hello(self):
        payload = json.dumps({
            "event": "hello"
        }).encode('utf-8')
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((self.server_ip, self.port))
                s.sendall(payload)
        except Exception as e:
            print(f"❌ Failed to connect to the server: {e}.\n Please ensure the server IP is correct, the server is running and the server is reachable.\n 🛑 Client shutting down.")
            os._exit(1)


    def receive_all(self, conn):
        data = b''
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
        return data

    def monitor_clipboard(self):
        while True:
            current = pyperclip.paste()
            if current != self.last_clipboard:
                self.last_clipboard = current
                self.send_clipboard(current)
            time.sleep(0.2)

    def send_clipboard(self, text):
        payload = json.dumps({
            "event": "update",
            "clipboard": text
        }).encode('utf-8')

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((self.server_ip, self.port))
                s.sendall(payload)
        except Exception as e:
            print(f"❌ Failed to send clipboard to server: {e}")

    def send_bye(self):
        payload = json.dumps({
            "event": "bye"
        }).encode('utf-8')
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((self.server_ip, self.port))
                s.sendall(payload)
        except Exception as e:
            print(f"❌ Failed to send bye message to server: {e}")

    def listen_for_updates(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', self.port))
            s.listen()
            print(f"📥 Client listening for updates on port {self.port}")
            while True:
                conn, addr = s.accept()
                with conn:
                    data = self.receive_all(conn)
                    if data:
                        try:
                            message = json.loads(data.decode('utf-8'))
                            clipboard = message.get("clipboard", "")
                            if clipboard != self.last_clipboard:
                                self.last_clipboard = clipboard
                                pyperclip.copy(clipboard)
                                print(f"📋 Clipboard updated from server.")
                        except json.JSONDecodeError:
                            print("⚠️ Received invalid JSON on client.")

    def start(self):
        is_reachable = self.is_ip_reachable(self.server_ip, self.port)
        if is_reachable:
            print(f"✅ Server at {self.server_ip}:{self.port} is reachable.")
        else:
            print(f"❌ Server at {self.server_ip}:{self.port} is not reachable.\n 🛑 Client shutting down.")
            os._exit(1)

        self.send_hello()
        threading.Thread(target=self.monitor_clipboard, daemon=True).start()
        threading.Thread(target=self.listen_for_updates, daemon=True).start()
        print("🟢 clipsync Client is running.")
        try:
            while True:
                time.sleep(10)
        except KeyboardInterrupt:
            self.send_bye()
            print("\n🛑 Client shutting down.")