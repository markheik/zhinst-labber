from collections import defaultdict

from zhinst.toolkit.driver.nodes.generator import Generator
from zhinst.toolkit.driver.devices.base import BaseInstrument
from zhinst.toolkit.driver.devices.shfqa import SHFScope
from zhinst.toolkit.driver.modules.shfqa_sweeper import SHFQASweeper
from zhinst.toolkit.driver.nodes.readout import Readout
from zhinst.labber.generator.custom_section import CustomLabel


# # Delimiter between sections in GUI.
# LABBER_DELIMITER_VALUE = ' - '

IGNORED_FUNCTIONS = {
    'NORMAL': [],
    'ADVANCED': [
        BaseInstrument.check_compatibility,
        BaseInstrument.get_streamingnodes,
        BaseInstrument.get_as_event,
        BaseInstrument.set_transaction,
        SHFQASweeper.get_result,
        SHFQASweeper.plot,
        Readout.read_integration_weights,
        Generator.read_from_waveform_memory
    ]
}

# Ignore everything by replacing '*' to channels:
# Example: '/STATS/*/PHYSICAL/VOLTAGES/*'
_IGNORED_NODES = {
    'NORMAL': defaultdict(list, **{
        'SHFQA': [
            '/QACHANNELS/*/GENERATOR/WAVEFORMS/*/LENGTH',
            '/QACHANNELS/*/GENERATOR/SEQUENCER/MEMORYUSAGE',
            '/QACHANNELS/*/GENERATOR/SEQUENCER/STATUS',
            '/QACHANNELS/*/GENERATOR/SEQUENCER/TRIGGERED',
            '/QACHANNELS/*/GENERATOR/ELF/*'
        ],
        'AWG': [],
        'COMMON': [
            '/STATS/*',
            '/STATUS/*',
            '/SYSTEM/ACTIVEINTERFACE*',
            '/SYSTEM/BOARDREVISIONS/*',
            '/SYSTEM/FPGAREVISION',
            '/SYSTEM/NICS/*',
            '/SYSTEM/PROPERTIES/*'
        ],
        'SHFQA_SWEEPER': [
            '/PLOT/*'
        ]
    }),
    'ADVANCED': defaultdict(list, **{
        'AWG': [
            '/ELF/*'
        ],
        'COMMON': [
            '/FEATURES/*'
        ],
        'SHFQA': [],
    })
}

# Example:
# _REPLACED_NODES = {
#     '/EXAMPLE/*/NODE/VALUE': {
#         'DATATYPE': 'PATH',
#         'UNIT': 'AMPLITUDE'
#     }
# }

_REPLACED_NODES = {
    'SHFQA': {}
}

# First will be executed if match is found
NODE_SECTIONS = {
    'SHFQA': {
        '/QACHANNELS/*/INPUT*': 'QA Setup',
        '/QACHANNELS/*/GENERATOR*': 'Generator',
        '/QACHANNELS/*/READOUT*': 'QA Result',
        '/QACHANNELS/*/TRIGGERS/*': 'Input - Output',
        '/SCOPES/*': 'Scopes',
        '/DIOS*': 'Input - Output',
        '/QACHANNELS/*': 'QA Setup',
        '/SCOPES/TRIGGER/*': 'Input - Output',
        '/SYSTEM/CLOCKS/*': 'Input - Output'
    }
}

# First will be executed if match is found
NODE_GROUPS = {
    'SHFQA': {
        '/QACHANNELS/0/*': 'QA Channel 0',
        '/QACHANNELS/1/*': 'QA Channel 1',
        '/QACHANNELS/2/*': 'QA Channel 2',
        '/QACHANNELS/3/*': 'QA Channel 3',
        '/QACHANNELS/4/*': 'QA Channel 4',
        '/QACHANNELS/5/*': 'QA Channel 5',
        '/QACHANNELS/6/*': 'QA Channel 6',
        '/QACHANNELS/7/*': 'QA Channel 7',
        '/SCOPES/0/*': 'Scope 0',
        '/SCOPES/1/*': 'Scope 1',
        '/SCOPES/2/*': 'Scope 2',
        '/SCOPES/3/*': 'Scope 3',
    }
}

REPLACED_FUNCTIONS = {
    Generator.load_sequencer_program: {
        'sequencer_program': {
            'datatype': 'PATH',
        }
    },
    SHFScope.read: {
        'Executefunc': {
            'datatype': 'BUTTON'
        }
    },
    SHFQASweeper.run: {
        'Executefunc': {
            'datatype': 'BUTTON'
        },
        'Result': {
            'datatype': 'VECTOR',
            'label': 'Result',
        }
    },
    SHFQASweeper.get_offset_freq_vector: {
        'Executefunc': {
            'datatype': 'BUTTON'
        }
    },
    Generator.write_to_waveform_memory: {
        'Wave0': {
            'datatype': 'PATH',
            'set_cmd': '.csv',
            'label': 'Wave0'
        },
        'Wave1': {
            'datatype': 'PATH',
            'set_cmd': '.csv',
            'label': 'Wave1'
        },
        'markers': {
            'datatype': 'PATH',
            'set_cmd': '.csv',
            'label': 'markers'
        }
    }
}

REPLACED_NODES = defaultdict(dict, **_REPLACED_NODES)
IGNORED_NODES = defaultdict(list, **_IGNORED_NODES)
