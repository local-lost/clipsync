# textual_app.py
from textual.app import App, ComposeResult
from textual.widgets import Static, DataTable, Log
from textual.containers import Horizontal
from textual.reactive import reactive
from textual import events
from server import ClipSyncServer
import threading

class ClipSyncUI(App):
    CSS_PATH = None
    connected_ips = reactive([])

    def compose(self) -> ComposeResult:
        with Horizontal():
            self.table = DataTable(zebra_stripes=True)
            self.table.add_columns("Connected Clients")
            yield self.table

            self.log_box = Log(highlight=True)
            yield self.log_box

    def on_mount(self):
        self.server = ClipSyncServer()

        # Hook UI callbacks
        self.server.on_log = self.add_log
        self.server.on_update_ips = self.safe_update_ip_table

        # Start background task
        threading.Thread(target=self.server.start, daemon=True).start()

        # Periodically update IP table (fallback)
        self.set_interval(5, self.update_ip_table)

    def add_log(self, message: str):
        self.call_from_thread(lambda: self.log_box.write(message  + "\n"))

    def safe_update_ip_table(self):
        self.call_from_thread(self.update_ip_table)

    def update_ip_table(self):
        self.table.clear()
        for ip in sorted(self.server.ip_list):
            self.table.add_row(ip)
