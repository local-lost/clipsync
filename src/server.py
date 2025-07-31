import socket
import threading
import json
import pyperclip
import time
import constants



class ClipSyncServer:
    def __init__(self, host='0.0.0.0', port=constants.DEFAULT_PORT):
        self.host = host
        self.port = port
        self.ip_list = set()
        self.last_clipboard = pyperclip.paste()
        self.last_update_ip = None
        self.lock = threading.Lock()

        self.on_log = lambda msg: None
        self.on_update_ips = lambda msg: None

        self.ss = threading.Thread(target=self.start_server, daemon=True)
        self.mc = threading.Thread(target=self.monitor_clipboard, daemon=True)

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
            self.on_log(f"📡 Server listening on {self.host}:{self.port}")
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
                            self.on_log(f"🔗 Registered client IP: {peer_ip}")
                            self.on_update_ips()
                elif event == "bye":
                    # Remove client from the list
                    with self.lock:
                        if peer_ip in self.ip_list:
                            self.ip_list.remove(peer_ip)
                            self.on_log(f"🔗 Unregistered client IP: {peer_ip}")
                            self.on_update_ips()
                elif event == "update":
                    # Handle clipboard update (existing code)
                    clipboard = message.get("clipboard", "")
                    if clipboard != self.last_clipboard:
                        self.last_clipboard = clipboard
                        pyperclip.copy(clipboard)
                        self.last_update_ip = peer_ip
                        self.on_log(f"📋 Clipboard updated by {peer_ip}")
                        self.broadcast_clipboard(clipboard, exclude_device_ip=peer_ip)
            except json.JSONDecodeError:
                self.on_log("⚠️ Received invalid JSON.")

    def monitor_clipboard(self):
        while True:
            current = pyperclip.paste()
            if current != self.last_clipboard:
                self.on_log("📋 Clipboard updated by the server.")
                self.last_clipboard = current
                self.last_update_ip = None
                self.broadcast_clipboard(current, exclude_device_ip=self.last_update_ip)
                self.on_log(f"📡 Clipboard broadcasted.")
                
            time.sleep(0.2)

    def broadcast_clipboard(self, text, exclude_device_ip=None):
        payload = json.dumps({
            "clipboard": text
        }).encode('utf-8')

        broadcast_ips = [ip for ip in self.ip_list if ip != exclude_device_ip]
        inactive_ips = []

        with self.lock:
            for ip in broadcast_ips:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        s.connect((ip, self.port))
                        s.sendall(payload)
                except Exception as e:
                    self.on_log(f"❌ Could not send to {ip}: {e}")
                    inactive_ips.append(ip)

        with self.lock:
            self.ip_list = [ip for ip in self.ip_list if ip not in inactive_ips]


    def start(self):
        self.on_log("🟢 Clipboard Sync Server is running.")
        self.ss.start()
        self.mc.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.on_log("\n🛑 Server shutting down.")
