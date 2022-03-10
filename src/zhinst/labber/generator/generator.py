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
from zhinst.labber.generator.helpers import delete_device_from_node_path, labber_delim_to_nodelike
from zhinst.labber.code_generator.drivers import generate_labber_device_driver_code
from .conf import NODE_GROUPS, NODE_SECTIONS, REPLACED_FUNCTIONS, IGNORED_FUNCTIONS, IGNORED_NODES, REPLACED_NODES


def node_in_ignored(node: str, ignored: t.List[str]) -> bool:
    path = delete_device_from_node_path(node)
    for node in ignored:
        r = fnmatch.filter([path], f"{node}*")
        if r:
            return True
    return False


def dict_to_config(config: configparser.ConfigParser, data: dict) -> None:
    for title, items in data.items():
        if not title == 'General settings':
            title = title.title()
        config.add_section(title)
        for name, value in items.items():
            if name.lower() in ["label", "group", "section"]:
                config.set(title, name.title(), value.title())
            else:
                config.set(title, name, value)


def replace_node_ch_n(node: str) -> str:
    replaced = []
    for c in node.upper().split('/'):
        if c.isnumeric():
            replaced.append('*')
        else:
            replaced.append(c)
    return '/'.join(replaced)

class LabberConfig:
    def __init__(self, root: Node, session: Session, mode="NORMAL"):
        self.root = root
        self.session = session
        self._mode = mode
        self._base_dir = "Zurich_Instruments_"
        self._name = "SYSTEM"
        self._settings_path = "settings.json"

    @property
    def settings_path(self):
        return self._settings_path

    @property
    def name(self):
        return self._base_dir  + self._name

    def generated_code(self) -> str:
        return generate_labber_device_driver_code(self._name, self.settings_path)

    def _sort(self, config: dict) -> dict:
        sorted_keys = sorted(config.keys())
        sorted_conf = {}
        for k in sorted_keys:
            sorted_conf[k] = config[k]
        return sorted_conf

    def custom_sections(self) -> dict:
        return {}

    @property
    def settings(self) -> dict:
        return {}

    def general_settings(self) -> dict:
        return {}

    def config(self) -> t.Dict[str, dict]:
        general = self.general_settings()
        nodes = self.generate_nodes()
        funcs = self.generate_functions()
        nodes.update(funcs)
        nodes.update(self.custom_sections())
        general.update(self._sort(nodes))
        return general

    def _ignored_nodes(self) -> list:
        for key in IGNORED_NODES[self._mode].keys():
            if key in self._name:
                adv = IGNORED_NODES["ADVANCED"][key]
                adv_common = IGNORED_NODES["ADVANCED"]["COMMON"]
                ignored = adv + adv_common
                if self._mode == "NORMAL":
                    normal = IGNORED_NODES["NORMAL"][key]
                    norm_common = IGNORED_NODES["NORMAL"]["COMMON"]
                    ignored = normal + norm_common + ignored
                return ignored
        return []

    def generate_nodes(self) -> t.Dict[str, dict]:
        nodes = {}
        for _, info in self.root:
            if node_in_ignored(info["Node"], self._ignored_nodes()):
                continue
            sec = NodeSection(info)
            sec_dict = sec.as_dict()[sec.label]
            for k, v in REPLACED_NODES.items():
                if k in self._name:
                    for kk, vv in v.items():
                        r = fnmatch.filter([sec.filtered_node_path.upper()], f'{kk}*')
                        if r:
                            sec_dict.update(vv)
                            break
            for k, v in NODE_SECTIONS.items():
                if k in self._name:
                    for kk, vv in v.items():
                        r = fnmatch.filter([sec.filtered_node_path.upper()], f'{kk}*')
                        if r:
                            sec_dict['section'] = vv
                            break
            # Overwrite groups
            for k, v in NODE_GROUPS.items():
                if k in self._name:
                    for kk, vv in v.items():
                        r = fnmatch.filter([sec.filtered_node_path.upper()], f'{kk}*')
                        if r:
                            sec_dict['group'] = vv
                            break
            nodes[sec.filtered_node_path] = {sec.label: sec_dict}

        config_dict = {}
        for v in nodes.values():
            config_dict.update(v)
        return config_dict

    def _node_sections(self, name) -> dict:
        for k, v in NODE_SECTIONS.items():
            if k in name:
                return v
        return {}

    def generate_functions(self) -> t.Dict[str, dict]:
        ignored_funcs = IGNORED_FUNCTIONS[self._mode] + IGNORED_FUNCTIONS[self._mode]
        config_dict = {}
        fs = functions_to_config(
            class_=self.root.__class__,
            nodes={k[0]: k[1] for k in self.root},
            ignores=ignored_funcs,
        )
        for k, _ in deepcopy(fs).items():
            # Overwrite sections
            k_as_node = labber_delim_to_nodelike(k)
            for node, section in self._node_sections(self._name).items():
                r = fnmatch.filter([k_as_node.upper()], f"{node}*")
                if r:
                    fs[k]["section"] = section
                    break
        config_dict.update(fs)
        return config_dict


class DeviceConfig(LabberConfig):
    def __init__(self, device: Node, session: Session, mode: str):
        super().__init__(device, session, mode)
        self.device = device
        self._name = self.device.device_type.upper()
        if "SHFQA" in self._name:
            from zhinst.toolkit.driver.nodes.shfqa_scope import SHFScope
            for ch in range(len(self.device.scopes[0].channels)):
                REPLACED_FUNCTIONS[SHFScope.read].update(
                    {
                        f'Result {ch}': {
                            f'label': f"RESULT {ch}",
                            'datatype': "VECTOR_COMPLEX",
                            "show_in_measurement_dlg": "True"
                        }
                    }
                )

    def custom_sections(self) -> t.Dict[str, dict]:
        sections = {}
        return sections

    @property
    def settings(self) -> dict:
        return {
            "data_server": {
                "host": self.session.server_host,
                "port": self.session.server_port,
                "hf2": self.session.is_hf2_server,
                "shared_session": True,
            },
            "instrument": {"base_type": "device", "type": self._name},
        }

    def general_settings(self) -> dict:
        return {
            "General settings": {
                "name": f"Zurich Instruments {self._name}",
                "version": "0.1",
                "driver_path": f"Zurich_Instruments_{self._name}",
                "interface": "Other",
                "startup": f"Do nothing",
            }
        }


class DataServerConfig(LabberConfig):
    def __init__(self, session: Session, mode: str):
        super().__init__(session, session, mode)
        self._name = "DataServer"

    @property
    def settings(self) -> dict:
        return {
            "data_server": {
                "host": self.session.server_host,
                "port": self.session.server_port,
                "hf2": self.session.is_hf2_server,
                "shared_session": True,
            },
            "instrument": {
                "base_type": "DataServer",
            },
        }

    def general_settings(self) -> dict:
        return {
            "General settings": {
                "name": f"Zurich Instruments {self._name}",
                "version": "0.1",
                "driver_path": f"Zurich_Instruments_{self._name}",
                "interface": "Other",
                "startup": f"Do nothing",
            }
        }


class ModuleConfig(LabberConfig):
    def __init__(self, name: str, session: Session, mode: str):
        self.module = getattr(session.modules, name)
        super().__init__(self.module, session, mode)
        self._name = name.upper() + '_Module'

    @property
    def settings(self) -> dict:
        return {
            "data_server": {
                "host": self.session.server_host,
                "port": self.session.server_port,
                "hf2": self.session.is_hf2_server,
                "shared_session": True,
            },
            "instrument": {"base_type": "module", "type": self._name},
        }

    def general_settings(self) -> dict:
        return {
            "General settings": {
                "name": f"Zurich Instruments {self._name}_Module",
                "version": "0.1",
                "driver_path": f"Zurich_Instruments_{self._name}_Module",
                "interface": "Other",
                "startup": f"Do nothing",
            }
        }


def generate_labber_files(
    filepath: str,
    mode: str,
    device: str,
    server_host: str,
    upgrade: bool = False,
    server_port: t.Optional[int] = None,
    hf2: t.Optional[bool] = None,
):
    session = Session(server_host=server_host, server_port=server_port, hf2=hf2)
    dev = session.connect_device(device)

    root_path = Path(filepath)
    root_path.mkdir(exist_ok=True)

    def write_to_json(path: Path, data, upgrade):
        if upgrade:
            with open(path, "w") as json_file:
                json.dump(data, json_file)
        else:
            if not path.exists():
                with open(path, "w") as json_file:
                    json.dump(data, json_file)

    def write_to_file(path: Path, data, upgrade):
        if upgrade:
            with open(path, "w") as f:
                f.write(data)
        else:
            if not path.exists():
                with open(path, "w") as f:
                    f.write(data)

    def write_to_config(path: Path, config, upgrade):
        if upgrade:
            with open(path, "w", encoding="utf-8") as config_file:
                config.write(config_file)
        else:
            if not path.exists():
                with open(path, "w", encoding="utf-8") as config_file:
                    config.write(config_file)

    # Dataserver
    obj = DataServerConfig(session, mode)
    dev_dir = root_path / obj.name
    dev_dir.mkdir(exist_ok=True)

    config = configparser.ConfigParser()
    dict_to_config(config, obj.config())
    path = dev_dir / f'{obj.name}.ini'
    write_to_config(path, config, upgrade)
    s_path = dev_dir / obj.settings_path
    write_to_json(s_path, obj.settings, upgrade)
    c_path = dev_dir / f'{obj.name}.py'
    write_to_file(c_path, obj.generated_code(), upgrade)

    # Device
    obj = DeviceConfig(dev, session, mode)
    dev_dir = root_path / obj.name
    dev_dir.mkdir(exist_ok=True)

    config = configparser.ConfigParser()
    dict_to_config(config, obj.config())
    path = dev_dir / f'{obj.name}.ini'
    write_to_config(path, config, upgrade)
    s_path = dev_dir / obj.settings_path
    write_to_json(s_path, obj.settings, upgrade)
    c_path = dev_dir / f'{obj.name}.py'
    write_to_file(c_path, obj.generated_code(), upgrade)

    # Modules
    modules: t.List[str] = [
        "daq",
        "scope",
        "sweeper",
        "qa",
        "shfqa_sweeper",
        "precompensation_advisor",
        "pid_advisor",
        "mds",
        "impedance",
    ]
    for module in modules:
        obj = ModuleConfig(module, session, mode)
        dev_dir = root_path / obj.name
        dev_dir.mkdir(exist_ok=True)
        config = configparser.ConfigParser()
        dict_to_config(config, obj.config())
        path = dev_dir / f'{obj.name}.ini'
        write_to_config(path, config, upgrade)
        s_path = dev_dir / obj.settings_path
        write_to_json(s_path, obj.settings, upgrade)
        c_path = dev_dir / f'{obj.name}.py'
        write_to_file(c_path, obj.generated_code(), upgrade)
