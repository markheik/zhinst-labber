import configparser
from copy import deepcopy
import typing as t
from pathlib import Path
import json
import fnmatch

from zhinst.toolkit import Session
from .node_section import NodeSection
from .function_section import functions_to_config
from zhinst.toolkit.nodetree import Node
from zhinst.labber.generator.helpers import delete_device_from_node_path
from zhinst.labber.code_generator.drivers import generate_labber_device_driver_code
from zhinst.labber.generator.conf import IGNORED_FUNCTIONS, IGNORED_NODES
from zhinst.labber.generator.custom_section import CustomLabel
from .conf import NODE_SECTIONS


def nodes_to_dict(node: Node) -> t.Dict:
    return {k[0]: k[1] for k in node}

def node_in_ignored(node: str, ignored: t.List[str]) -> bool:
    path = delete_device_from_node_path(node)
    for node in ignored:
        r = fnmatch.filter([path], f'{node}*')
        if r:
            return True
    return False

def labber_delim_to_nodelike(s: str) -> str:
    s = s.replace(' - ', '/')
    return '/' + s

def dict_to_config(config, data):
    for title, items in data.items():
        config.add_section(title.title())
        for name, value in items.items():
            if name.lower() in ['label', 'group', 'section']:
                config.set(title.title(), name.title(), value.title())
            else:
                config.set(title.title(), name, value)
    return config


class LabberConfig:
    def __init__(self, root, session):
        self.root = root
        self.session = session
        self.settings = {}
        self.base_dir = 'Zurich_Instruments_'
        self.name = 'DEVICE'
        self.conf_dir = self.base_dir + self.name
        self.settings_path = 'settings.json'
        self.ignored_nodes = []
        self.ignored_funcs = []

    def generated_code(self):
        return generate_labber_device_driver_code(self.name, self.settings_path)

    def _sort(self, config: dict) -> dict:
        sorted_keys = sorted(config.keys())
        sorted_conf = {}
        for k in sorted_keys:
            sorted_conf[k] = config[k]
        return sorted_conf

    def custom_sections(self):
        return {}

    def general_settings(self):
        return {}

    def config(self, type_='NORMAL'):
        general = self.general_settings()
        nodes = self.generate_nodes(type_)
        funcs = self.generate_functions(type_)
        nodes.update(funcs)
        nodes.update(self.custom_sections())
        general.update(self._sort(nodes))
        return general

    def generate_nodes(self, type_: str):
        ignored = []
        for key in IGNORED_NODES[type_].keys():
            if key in self.name:
                ignored = IGNORED_NODES['ADVANCED'][key] + IGNORED_NODES['ADVANCED']['COMMON']
                if type_ == 'NORMAL':
                    ignored = IGNORED_NODES['NORMAL'][key] + IGNORED_NODES['NORMAL']['COMMON'] + ignored
                break
        config_dict = {}
        nodes = {}
        for _, info in self.root:
            if node_in_ignored(info['Node'], ignored):
                continue
            sec = NodeSection(info)
            nodes[sec.filtered_node_path] = sec.as_dict()

        for v in nodes.values():
            config_dict.update(v)
        return config_dict

    def _node_sections(self, name) -> dict:
        for k, v in NODE_SECTIONS.items():
            if k in name:
                return v
        return {}

    def generate_functions(self, type_):
        ignored_funcs = IGNORED_FUNCTIONS[type_]
        config_dict = {}
        fs = functions_to_config(
            class_=self.root.__class__, 
            nodes=nodes_to_dict(self.root), 
            ignores=ignored_funcs
        )
        for k, _ in deepcopy(fs).items():
            # Overwrite sections
            k_as_node = labber_delim_to_nodelike(k)
            for node, section in self._node_sections(self.name).items():
                r = fnmatch.filter([k_as_node.upper()], f'{node}*')
                if r:
                    fs[k]['section'] = section
                    break
        config_dict.update(fs)
        return config_dict

class DeviceConfig(LabberConfig):
    def __init__(self, device, session):
        super().__init__(device, session)
        self.device = device
        self.name = self.device.device_type.upper()
        self.conf_dir = self.base_dir + self.name
        self.ignored_nodes = []
        self.ignored_funcs = []

    def custom_sections(self):
        sections = {}
        if 'SHFQA' in self.name:
            for res in range(4):
                s = CustomLabel(f'SCOPES - 0 - READ - RESULT {res}', 'SCOPES', 'SCOPES - 0 - READ')
                s['label'] = f'RESULT {res}'
                s['datatype'] = 'VECTOR_COMPLEX'
                s['show_in_measurement_dlg'] = 'True'
                sections.update(s.to_config())
            s = CustomLabel(f'SCOPES - 0 - CONFIGURE - TRIGGER_INPUT', 'SCOPES', 'SCOPES - 0 - CONFIGURE')
            s['datatype'] = 'COMBO'
            for _, enum in enumerate(self.device.scopes[0].available_trigger_inputs, 1):
                s.add_enum(str(enum), str(enum))
            sections.update(s.to_config())

            s = CustomLabel(f'SCOPES - 0 - CONFIGURE - INPUT_SELECT', 'SCOPES', 'SCOPES - 0 - CONFIGURE')
            for _, enum in enumerate(self.device.scopes[0].available_inputs, 1):
                s.add_enum(enum, enum)
            sections.update(s.to_config())
        return sections

    def settings(self):
        return {
            "data_server": {
                "host": self.session.server_host,
                "port": self.session.server_port,
                "hf2": self.session.is_hf2_server,
                "shared_session": True
            },
            "instrument": {
                "base_type": "device",
                "type": self.name
            }
        }

    def general_settings(self) -> dict:
        return {
            'General settings': {
                'name': f'Zurich Instruments {self.name}',
                'version': '0.1',
                "driver_path": f'Zurich_Instruments_{self.name}',
                "interface": 'Other',
                "startup": f'Do nothing'
            }
        }


class DataServerConfig(LabberConfig):
    def __init__(self, root, session):
        super().__init__(root, session)
        self.name = 'DataServer'
        self.conf_dir = self.base_dir + self.name
        self.ignored_nodes = []
        self.ignored_funcs = []

    def settings(self):
        return {
            "data_server": {
                "host": self.session.server_host,
                "port": self.session.server_port,
                "hf2": self.session.is_hf2_server,
                "shared_session": True
            },
            "instrument": {
                "base_type": "DataServer",
            }
        }

    def general_settings(self) -> dict:
        return {
            'General settings': {
                'name': f'Zurich Instruments {self.name}',
                'version': '0.1',
                "driver_path": f'Zurich_Instruments_{self.name}',
                "interface": 'Other',
                "startup": f'Do nothing'
            }
        }

class ModuleConfig(LabberConfig):
    def __init__(self, name, session):
        self.module = getattr(session.modules, name)
        super().__init__(self.module, session)
        self.name = name.upper()
        self.conf_dir = self.base_dir + self.name
        self.ignored_nodes = []
        self.ignored_funcs = []

    def settings(self):
        return {
            "data_server": {
                "host": self.session.server_host,
                "port": self.session.server_port,
                "hf2": self.session.is_hf2_server,
                "shared_session": True
            },
            "instrument": {
                "base_type": "module",
                "type": self.name
            }
        }

    def general_settings(self) -> dict:
        return {
            'General settings': {
                'name': f'Zurich Instruments {self.name}Module',
                'version': '0.1',
                "driver_path": f'Zurich_Instruments_{self.name}Module',
                "interface": 'Other',
                "startup": f'Do nothing'
            }
        }


def generate_labber_files(filepath: str, device: str, server_host: str, server_port: int = None, hf2: bool = None):
    session = Session(server_host=server_host, server_port=server_port, hf2=hf2)
    dev = session.connect_device(device)

    root_path = Path(filepath)
    root_path.mkdir(exist_ok=True)

    # Dataserver
    obj =   DataServerConfig(dev, session)
    r = obj.config()
    dev_dir = root_path / obj.conf_dir
    dev_dir.mkdir(exist_ok=True)

    config = configparser.ConfigParser()
    dict_to_config(config, r)
    with open(f'{dev_dir}/Zurich_Instruments_{obj.name}.ini', "w", encoding='utf-8') as config_file:
        config.write(config_file)
    with open(dev_dir / obj.settings_path, 'w') as json_file:
        json.dump(obj.settings, json_file)
    with open(dev_dir / f'Zurich_Instruments_{obj.name}.py', 'w') as f:
        f.write(obj.generated_code())

    # Device
    obj = DeviceConfig(dev, session)
    r = obj.config()
    dev_dir = root_path / obj.conf_dir
    dev_dir.mkdir(exist_ok=True)

    config = configparser.ConfigParser()
    dict_to_config(config, r)
    with open(f'{dev_dir}/Zurich_Instruments_{obj.name}.ini', "w", encoding='utf-8') as config_file:
        config.write(config_file)
    with open(dev_dir / obj.settings_path, 'w') as json_file:
        json.dump(obj.settings, json_file)
    with open(dev_dir / f'Zurich_Instruments_{obj.name}.py', 'w') as f:
        f.write(obj.generated_code())
        

    # Modules
    modules: t.List[str] = [
        'daq', 'scope', 'sweeper', 'qa', 'shfqa_sweeper', 'precompensation_advisor',
        'pid_advisor', 'mds', 'impedance']
    for module in modules:
        obj = ModuleConfig(module, session)
        r = obj.config()
        dev_dir = root_path / obj.conf_dir
        dev_dir.mkdir(exist_ok=True)
        config = configparser.ConfigParser()
        dict_to_config(config, r)
        with open(f'{dev_dir}/Zurich_Instruments_{obj.name}.ini', "w", encoding='utf-8') as config_file:
            config.write(config_file)
        with open(dev_dir / obj.settings_path, 'w') as json_file:
            json.dump(obj.settings, json_file)
        with open(dev_dir / f'Zurich_Instruments_{obj.name}.py', 'w') as f:
            f.write(obj.generated_code())

