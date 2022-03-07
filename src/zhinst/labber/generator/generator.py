from collections import defaultdict
import configparser
from logging import root
import typing as t

from .node_section import NodeSection
from .function_section import functions_to_config
from .helpers import tooltip
from zhinst.labber.generator.helpers import LABBER_DELIMITER_VALUE


# All modules separate INI file.
# DataServer separate instrument
# Test individual function
# Two entries for both waves. CSV / reading


def general_settings_device(config, device):
    section = 'General settings'
    config.add_section(section)
    config.set(section, "name", f'Zurich Instruments {device.device_type}')
    config.set(section, "version", f'0.1')
    config.set(section, "driver_path", f'Zurich_Instruments_{device.device_type}')
    config.set(section, "interface", f'Other')
    config.set(section, "startup", f'Do nothing')


def general_settings_dataserver(config):
    section = 'General settings'
    config.add_section(section)
    config.set(section, "name", f'Zurich Instruments DataServer')
    config.set(section, "version", '0.1')
    config.set(section, "driver_path", f'Zurich_Instruments_DataServer')
    config.set(section, "interface", f'Other')
    config.set(section, "startup", f'Do nothing')


def general_settings_module(config, module):
    section = 'General settings'
    config.add_section(section)
    config.set(section, "name", f'Zurich Instruments {module.upper()} Module')
    config.set(section, "version", f'0.1')
    config.set(section, "driver_path", f'Zurich_Instruments_{module.upper()}_Module')
    config.set(section, "interface", f'Other')
    config.set(section, "startup", f'Do nothing')


def nodes_to_dict(node) -> t.Dict:
    return {k[0]: k[1] for k in node}

def node_in_ignored(node, ignored):
    if ignored:
        for ignored_node in ignored:
            if ignored_node in node.lower():
                return True
        return False
    return False

def to_config(root_node, config, ignored_funcs: t.Optional[t.List[str]] = None, ignored_nodes: t.Optional[t.List[str]] = None):
    SECTIONS_ = [
        {'root': root_node, 'handler': NodeSection},
        # {'root': session.modules.sweeper, 'handler': NodeSection},
    ]

    for item in SECTIONS_:
        handler = item['handler']
        for node, leaf in item['root']:
            if node_in_ignored(leaf['Node'], ignored_nodes):
                continue
            sec = handler(leaf)
            sec.to_config(config)

    secs = functions_to_config(class_=root_node.__class__, nodes=nodes_to_dict(root_node), ignores=ignored_funcs)
    for sec in secs:
        for k, v in sec.items():
            config.add_section(k)
            for kk, vv in v.items():
                config.set(k, kk, vv)

    import re
    from zhinst.labber.generator.custom import CustomLabel
    from copy import deepcopy, copy
    

    config_2 = []
 
    for k, v in config.items():
        if ('LOAD_SEQUENCER_PROGRAM - SEQUENCER_PROGRAM') in k:
            v['DATATYPE'] = 'PATH'
        elif ('WRITE_TO_WAVEFORM_MEMORY - WAVEFORMS') in k:
            v['DATATYPE'] = 'PATH'
        elif ('WRITE_TO_WAVEFORM_MEMORY - INDEXES') in k:
            v['DATATYPE'] = 'STRING'
            v['TOOLTIP'] = tooltip('Indexes separated by comma.')

        r = re.match(r'(?i)qachannels - \d - generator - waveforms - \d - wave', k)
        if r:
            b = deepcopy(v)
            b['label'] = str(k) + ' - ' + 'SET'
            b['datatype'] = 'PATH'
            b['permission'] = 'WRITE'
            config_2.append((b['label'], b))

        r = re.match(r'(?i)qachannels - \d - readout - integration - weights - \d - wave', k)
        if r:
            b = deepcopy(v)
            b['label'] = str(k) + ' - ' + 'SET'
            b['datatype'] = 'PATH'
            b['permission'] = 'WRITE'
            config_2.append((b['label'], b))

        r = re.match(r'(?i)qachannels - \d - spectroscopy - envelope - wave', k)
        if r:
            b = deepcopy(v)
            b['label'] = str(k) + ' - ' + 'SET'
            b['datatype'] = 'PATH'
            b['permission'] = 'WRITE'
            config_2.append((b['label'], b))
    
    for item in config_2:
        config[item[0]] = item[1]
    

    return config
