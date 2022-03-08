from collections import defaultdict

from zhinst.toolkit.driver.nodes.generator import Generator
from zhinst.toolkit.driver.devices.base import BaseInstrument


IGNORED_FUNCTIONS = [
    BaseInstrument.check_compatibility,
    BaseInstrument.get_streamingnodes,
    BaseInstrument.get_as_event,
    BaseInstrument.set_transaction
]

# Ignore everything by replacing 'N' to channels:
# Example: '/STATS/N/PHYSICAL/VOLTAGES/N'
_IGNORED_NODES = {
    'AWG': [
        '/ELF/'
    ],
    'SHFQA4': []
}

# Example:
# _REPLACED_NODES = {
#     '/EXAMPLE/N/NODE/VALUE': {
#         'DATATYPE': 'PATH',
#         'UNIT': 'AMPLITUDE'
#     }
# }
_REPLACED_NODES = {
    '': {}
}


REPLACED_FUNCTIONS = {
    Generator.load_sequencer_program: {
        'sequencer_program': {
            'datatype': 'PATH'
        }
    }
}

REPLACED_NODES = defaultdict(dict, **_REPLACED_NODES)
IGNORED_NODES = defaultdict(list, **_IGNORED_NODES)
