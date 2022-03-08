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

# First will be executed if match is found
NODE_SECTIONS = {
    '/QACHANNELS/*/INPUT*': 'QA Setup',
    '/QACHANNELS/*/GENERATOR*': 'Generator',
    '/QACHANNELS/*/READOUT*': 'QA Result',
    '/SCOPES/*': 'Scopes',
    '/QACHANNELS/*': 'QA Setup',
}

# First will be executed if match is found
NODE_GROUPS = {
    '/QACHANNELS/0/*': 'QA Channel 0',
    '/QACHANNELS/1/*': 'QA Channel 1',
    '/QACHANNELS/2/*': 'QA Channel 2',
    '/QACHANNELS/3/*': 'QA Channel 3',
    '/QACHANNELS/4/*': 'QA Channel 4',
    '/QACHANNELS/5/*': 'QA Channel 5',
    '/QACHANNELS/6/*': 'QA Channel 6',
    '/QACHANNELS/7/*': 'QA Channel 7',
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
