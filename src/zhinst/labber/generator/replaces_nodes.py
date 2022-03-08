from collections import defaultdict

from zhinst.toolkit.driver.nodes.generator import Generator
from zhinst.toolkit.driver.devices.base import BaseInstrument


IGNORED_FUNCTIONS = [
    BaseInstrument.check_compatibility,
    BaseInstrument.get_streamingnodes,
    BaseInstrument.get_as_event,
    BaseInstrument.set_transaction
]
#     'MFLI': [
#         'check_compatibility',
#         'get_streamingnodes',
#         'set_transaction'
#     ]
# ]

_IGNORED_NODES = {
    'AWG': [
        '/elf/'
    ]
}


_REPLACED_NODES = {
    '/EXAMPLE/N/NODE/VALUE': {
        'DATATYPE': 'PATH',
        'UNIT': 'AMPLITUDE'
    }
}


REPLACED_FUNCTIONS = {
    Generator.load_sequencer_program: {
        'sequencer_program': {
            'datatype': 'PATH'
        }
    }
}

REPLACED_NODES = defaultdict(dict, **_REPLACED_NODES)
# IGNORED_FUNCTIONS = defaultdict(list, **_IGNORED_FUNCTIONS)
IGNORED_NODES = defaultdict(list, **_IGNORED_NODES)
