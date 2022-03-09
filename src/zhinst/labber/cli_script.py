import click
from zhinst.labber.generator.generator import generate_labber_files


@click.group()
def main():
    """Fancy zhinst-labber cli script"""
    pass

@main.command()
@click.argument(
    "filepath",
    required=True,
    type=click.Path(exists=True),
)
@click.argument(
    "device",
    required=True,
    type=str,
)
@click.argument(
    "server_host",
    required=True,
    type=str,
)
@click.option(
    "--server_port",
    required=False,
    type=int,
)
@click.option(
    "--hf2",
    required=False,
    type=bool,
)
def makeconfig(filepath, device, server_host, server_port, hf2):
    """Generate drivers.
    
    FILEPATH Filepath where the files are saved.

    DEVICE: Device ID (e.g: dev1234)

    SERVER_HOST: Server host (e.g: localhost)
    """
    generate_labber_files(
        filepath=filepath,
        device=device,
        server_host=server_host,
        server_port=server_port,
        hf2=hf2
    )
