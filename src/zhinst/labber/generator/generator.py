import configparser
import re
import typing as t

from .node_section import NodeSection
from .function_section import functions_to_config
from zhinst.toolkit.nodetree import Node
from zhinst.labber.generator.node_section import replace_node_ch_n
from zhinst.labber.generator.helpers import delete_device_from_node_path

def nodes_to_dict(node: Node) -> t.Dict:
    return {k[0]: k[1] for k in node}

def node_in_ignored(node: str, ignored: t.List[str]) -> bool:
    path = delete_device_from_node_path(node)
    if replace_node_ch_n(path.upper()) in ignored:
        return True
    return False


def dict_to_config(config, data):
    for title, items in data.items():
        config.add_section(title)
        for name, value in items.items():
            config.set(title, name, value)
    return config

def to_config(
    root_node: Node, 
    config: configparser.ConfigParser, 
    ignored_funcs: t.List[t.Any] = [],
    ignored_nodes: t.List[str] = []
    ) -> configparser.ConfigParser:
    dd = {}
    for node, info in root_node:
        if node_in_ignored(info['Node'], ignored_nodes):
            continue
        sec = NodeSection(info)
        dd.update(sec.as_dict())
    secs = functions_to_config(class_=root_node.__class__, nodes=nodes_to_dict(root_node), ignores=ignored_funcs)
    dd.update(secs)
    dict_to_config(config, dd)
    return config
    # filetype to section when PATH set_cmd, get_cmd


# for k, v in config.items():
#     ...

#     # Find better solutions for this
#     # r = re.match(r'(?i)qachannels - \d - generator - waveforms - \d - wave', k)
#     # if r:
#     #     b = deepcopy(v)
#     #     b['label'] = str(k) + ' - ' + 'SET'
#     #     b['datatype'] = 'PATH'
#     #     b['permission'] = 'WRITE'
#     #     config_2.append((b['label'], b))

#     # r = re.match(r'(?i)qachannels - \d - readout - integration - weights - \d - wave', k)
#     # if r:
#     #     b = deepcopy(v)
#     #     b['label'] = str(k) + ' - ' + 'SET'
#     #     b['datatype'] = 'PATH'
#     #     b['permission'] = 'WRITE'
#     #     config_2.append((b['label'], b))

#     # r = re.match(r'(?i)qachannels - \d - spectroscopy - envelope - wave', k)
#     # if r:
#     #     b = deepcopy(v)
#     #     b['label'] = str(k) + ' - ' + 'SET'
#     #     b['datatype'] = 'PATH'
#     #     b['permission'] = 'WRITE'
#     #     config_2.append((b['label'], b))

# for item in config_2:
#     config[item[0]] = item[1]
# return config
