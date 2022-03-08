import configparser
import typing as t
from pathlib import Path
import json

from zhinst.toolkit import Session
from zhinst.labber.generator.generator import (
    to_config
)
from zhinst.labber.generator.general_settings import (
    general_settings_module,
    general_settings_device,
    general_settings_dataserver
)
from zhinst.labber.generator.code_generator import generate_labber_device_driver_code
from zhinst.labber.generator.replaces_nodes import IGNORED_FUNCTIONS, IGNORED_NODES


def cli_generator(filepath: str, device: str, server_host: str, server_port: int = None, hf2: bool = None):
    session = Session(server_host=server_host, server_port=server_port, hf2=hf2)
    dev = session.connect_device(device)

    root_path = Path(filepath)
    root_path.mkdir(exist_ok=True)

    # Dataserver
    config = configparser.ConfigParser()
    general_settings_dataserver(config)
    config = to_config(session, config, IGNORED_FUNCTIONS)
    ds_dir = root_path / f'Zurich_Instruments_DataServer'
    ds_dir.mkdir(exist_ok=True)
    with open(f'{ds_dir}/Zurich_Instruments_DataServer.ini', "w", encoding='utf-8') as config_file:
        config.write(config_file)
    settings = {
        "data_server": {
            "host": server_host,
            "port": server_port,
            "hf2": hf2,
            "shared_session": True
        },
        "instrument": {
            "base_type": "DataServer",
        }
    }
    with open(f'{ds_dir}/settings.json', 'w') as json_file:
        json.dump(settings, json_file)

    # Device
    config = configparser.ConfigParser()
    general_settings_device(device=dev, config=config)
    config = to_config(dev, config, IGNORED_FUNCTIONS, IGNORED_NODES[dev._device_type.upper()])
    dev_dir = root_path / f'Zurich_Instruments_{dev.device_type.upper()}'
    dev_dir.mkdir(exist_ok=True)
    with open(f'{dev_dir}/Zurich_Instruments_{dev.device_type.upper()}.ini', "w", encoding='utf-8') as config_file:
        config.write(config_file)
    settings = {
        "data_server": {
            "host": server_host,
            "port": server_port,
            "hf2": hf2,
            "shared_session": True
        },
        "instrument": {
            "base_type": "device",
            "type": dev.device_type.upper()
        }
    }
    dev_settings_path = dev_dir / 'settings.json'
    with open(dev_settings_path, 'w') as json_file:
        json.dump(settings, json_file)

    gen_code = generate_labber_device_driver_code(dev.device_type.upper(), dev_settings_path)
    with open(dev_dir / f'Zurich_Instruments_{dev.device_type.upper()}.py', 'w') as f:
        f.write(gen_code)

    # Module
    # ModuleHandler not iterable
    modules: t.List[str] = [
        'daq', 'awg', 'scope', 'sweeper', 'qa', 'shfqa_sweeper', 'precompensation_advisor',
        'pid_advisor', 'mds', 'impedance']

    for module in modules:
        mod_dir = root_path / f'Zurich_Instruments_{module.upper()}_Module'
        mod_dir.mkdir(exist_ok=True)

        config = configparser.ConfigParser()
        general_settings_module(config, module)
        mod = getattr(session.modules, module)
        config = to_config(mod, config, IGNORED_FUNCTIONS, IGNORED_NODES[module.upper()])

        with open(f'{mod_dir}/Zurich_Instruments_{module.upper()}_Module.ini', "w", encoding='utf-8') as config_file:
            config.write(config_file)

        settings = {
            "data_server": {
                "host": server_host,
                "port": server_port,
                "hf2": hf2,
                "shared_session": True
            },
            "instrument": {
                "base_type": "module",
                "type": module.upper()
            }
        }
        mod_settings_path = mod_dir/ 'settings.json'
        with open(mod_settings_path, 'w') as json_file:
            json.dump(settings, json_file)

        gen_code = generate_labber_device_driver_code(f'{module.upper()}Module', mod_settings_path)
        with open(mod_dir / f'Zurich_Instruments_{module.upper()}_Module.py', 'w') as f:
            f.write(gen_code)
