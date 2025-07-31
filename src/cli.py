import time
import click
from client import ClipSyncClient
from ui import ClipSyncUI
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

    ClipSyncUI().run()  # Run the Textual UI for monitoring

@cli.command()
@click.argument('server_ip')
@click.option('--port', default=constants.DEFAULT_PORT, help='Server port')
def client(server_ip, port):
    """Start the clipboard sync client."""
    cli = ClipSyncClient(server_ip=server_ip, port=port)
    cli.start()
    click.echo(f'📡 Running client, connected to {server_ip}:{port}')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo('🛑 Client shutting down.')