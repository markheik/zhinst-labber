import configparser
import re
import typing as t
from copy import deepcopy

from .node_section import NodeSection
from .function_section import functions_to_config
from .helpers import tooltip
from zhinst.toolkit.nodetree import Node


def nodes_to_dict(node: Node) -> t.Dict:
    return {k[0]: k[1] for k in node}

def node_in_ignored(node: str, ignored: t.List[str]) -> bool:
    if ignored:
        for ignored_node in ignored:
            if ignored_node in node.lower():
                return True
        return False
    return False

def to_config(
    root_node: Node, 
    config: configparser.ConfigParser, 
    ignored_funcs: t.List[str] = [],
    ignored_nodes: t.List[str] = []
    ) -> configparser.ConfigParser:
    for node, info in root_node:
        if node_in_ignored(info['Node'], ignored_nodes):
            continue
        sec = NodeSection(info)
        sec.to_config(config)
    secs = functions_to_config(class_=root_node.__class__, nodes=nodes_to_dict(root_node), ignores=ignored_funcs)
    for sec in secs:
        for k, v in sec.items():
            config.add_section(k)
            for kk, vv in v.items():
                config.set(k, kk, vv)
    config_2 = []
    # filetype to section when PATH set_cmd, get_cmd
    # functions no return --> checkbox
    # functions return --> get from device

    # Find better solutions for this
    # Replace, extend, ignore


    for k, v in config.items():
        ...
        # if ('LOAD_SEQUENCER_PROGRAM - SEQUENCER_PROGRAM') in k:
        #     v['DATATYPE'] = 'PATH'
        # elif ('WRITE_TO_WAVEFORM_MEMORY - WAVEFORMS') in k:
        #     v['DATATYPE'] = 'PATH'
        # elif ('WRITE_TO_WAVEFORM_MEMORY - INDEXES') in k:
        #     v['DATATYPE'] = 'STRING'
        #     v['TOOLTIP'] = tooltip('Indexes separated by comma.')

        # Find better solutions for this
        # r = re.match(r'(?i)qachannels - \d - generator - waveforms - \d - wave', k)
        # if r:
        #     b = deepcopy(v)
        #     b['label'] = str(k) + ' - ' + 'SET'
        #     b['datatype'] = 'PATH'
        #     b['permission'] = 'WRITE'
        #     config_2.append((b['label'], b))

        # r = re.match(r'(?i)qachannels - \d - readout - integration - weights - \d - wave', k)
        # if r:
        #     b = deepcopy(v)
        #     b['label'] = str(k) + ' - ' + 'SET'
        #     b['datatype'] = 'PATH'
        #     b['permission'] = 'WRITE'
        #     config_2.append((b['label'], b))

        # r = re.match(r'(?i)qachannels - \d - spectroscopy - envelope - wave', k)
        # if r:
        #     b = deepcopy(v)
        #     b['label'] = str(k) + ' - ' + 'SET'
        #     b['datatype'] = 'PATH'
        #     b['permission'] = 'WRITE'
        #     config_2.append((b['label'], b))
    
    for item in config_2:
        config[item[0]] = item[1]
    return config
