from collections import defaultdict
import configparser
import typing as t
from pathlib import Path
import json
    
from zhinst.toolkit import Session
from zhinst.labber.generator.generator import (
    to_config,
    general_settings_module,
    general_settings_device,
    general_settings_dataserver
)
from zhinst.labber.generator.custom import CustomLabel
# Create .py file for device
# settings file
# directory


IGNORED_FUNCTIONS = {
    'MFLI': [
        'check_compatibility',
        'get_streamingnodes',
        'set_transaction'
    ]
}
IGNORED_FUNCTIONS = defaultdict(list, **IGNORED_FUNCTIONS)

IGNORED_NODES = {
    'AWG': [
        '/elf/'
    ]
}
IGNORED_NODES = defaultdict(list, **IGNORED_NODES)


def cli_generator(filepath: str, device: str, server_host: str, server_port: int = None, hf2: bool = None):
    session = Session(server_host=server_host, server_port=server_port, hf2=hf2)
    dev = session.connect_device(device)

    root_path = Path(filepath)
    root_path.mkdir(exist_ok=True)

    # Dataserver
    config = configparser.ConfigParser()
    general_settings_dataserver(config)
    config = to_config(session, config, IGNORED_FUNCTIONS['DataServer'])
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
    config = to_config(dev, config, IGNORED_FUNCTIONS[dev.device_type])
    dev_dir = root_path / f'Zurich_Instruments_{dev.device_type.upper()}_Module'
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
    with open(f'{dev_dir}/settings.json', 'w') as json_file:
        json.dump(settings, json_file)

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
        config = to_config(mod, config, IGNORED_FUNCTIONS[module.upper()], IGNORED_NODES[module.upper()])

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
        with open(f'{mod_dir}/settings.json', 'w') as json_file:
            json.dump(settings, json_file)

        _py_file = f'Zurich_Instruments_{module.upper()}_Module.py'


cli_generator('configs', 'dev12019', 'localhost')
