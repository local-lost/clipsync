import time
import click
from server import ClipboardSyncServer
from client import ClipboardSyncClient
import constants

@click.group()
def cli():
    """Clipboard Sync CLI for managing clipboard synchronization."""
    pass

@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind')
@click.option('--port', default=constants.DEFAULT_PORT, help='Port to use')
def server(host, port):
    """Start the clipboard sync server."""
    srv = ClipboardSyncServer(host=host, port=port)
    srv.start()  # blocking method that starts server + periodic display

@cli.command()
@click.argument('server_ip')
@click.option('--port', default=constants.DEFAULT_PORT, help='Server port')
def client(server_ip, port):
    """Start the clipboard sync client."""
    cli = ClipboardSyncClient(server_ip=server_ip, port=port)
    cli.start()
    click.echo(f'📡 Running client, connected to {server_ip}:{port}')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo('🛑 Client shutting down.')